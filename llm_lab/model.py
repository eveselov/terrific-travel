"""A local Qwen3 model, used two ways: reply in character, and rank the player's intent.

Everything runs in this process with transformers: no server, no network once the model is in
the Hugging Face cache. The model picks its own device: the GPU in fp16 when the weights fit in
its free memory, otherwise the CPU in fp32 (fp16 is slow on a CPU).
"""

from __future__ import annotations

import math
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizerBase
from transformers.generation.streamers import BaseStreamer

# Short name -> Hugging Face id. Add a line to try another size.
MODELS: dict[str, str] = {
    "0.6b": "Qwen/Qwen3-0.6B",
    "1.7b": "Qwen/Qwen3-1.7B",
    "4b": "Qwen/Qwen3-4B",
}
# Real parameter counts (with embeddings), to judge whether fp16 weights fit on the GPU.
PARAMS: dict[str, float] = {"0.6b": 0.75e9, "1.7b": 2.0e9, "4b": 4.0e9}
# Room on the GPU beyond the weights: activations, the KV cache, the CUDA context.
GPU_HEADROOM: float = 1.3

# Qwen's recommended sampling for non-thinking mode.
TEMPERATURE: float = 0.7
TOP_P: float = 0.8
TOP_K: int = 20
# Enough for a chat reply of a few sentences; descriptions need more (/tokens in lab.py).
MAX_NEW_TOKENS: int = 120

END_OF_TURN: str = "<|im_end|>"
THINK_RE: re.Pattern[str] = re.compile(r"<think>.*?</think>", re.DOTALL)

Message = dict[str, str]


class TokenStreamer(BaseStreamer):
    """Hands each newly generated token, as text, to a callback, while generation runs.

    `generate()` calls `put()` from its own loop, in the same thread: first once with the
    prompt (skipped here), then with every new token. Tokens are decoded one by one, so the
    pieces are raw: often part of a word, and a letter like "é" may arrive in two broken
    halves. The returned Reply has the properly decoded text.
    """

    def __init__(self, tokenizer: PreTrainedTokenizerBase, on_token: Callable[[str], None]) -> None:
        self.tokenizer: PreTrainedTokenizerBase = tokenizer
        self.on_token: Callable[[str], None] = on_token
        self.prompt_seen: bool = False

    def put(self, value: torch.Tensor) -> None:
        if not self.prompt_seen:
            self.prompt_seen = True
            return
        for token_id in value.flatten().tolist():
            self.on_token(str(self.tokenizer.decode([token_id], skip_special_tokens=True)))

    def end(self) -> None:
        pass


@dataclass
class Reply:
    """A generated reply: the text, how long generation took, and how many tokens it made.

    `seconds` covers generation only, not intent ranking or loading.
    """

    text: str
    seconds: float
    tokens: int

    @property
    def tokens_per_second(self) -> float:
        return self.tokens / self.seconds if self.seconds > 0 else 0.0


@dataclass
class IntentGuess:
    """One intent and the model's probability for it; a ranking's probabilities sum to 1."""

    name: str
    probability: float


def gpu_fits(short: str) -> bool:
    """Whether the model's fp16 weights fit in the GPU's free memory, with headroom."""
    if not torch.cuda.is_available():
        return False
    free_bytes: int = torch.cuda.mem_get_info()[0]
    return free_bytes > PARAMS[short] * 2 * GPU_HEADROOM


def pick_device(short: str) -> tuple[str, torch.dtype]:
    """The GPU in fp16 if the weights fit with headroom, else the CPU in fp32."""
    return ("cuda", torch.float16) if gpu_fits(short) else ("cpu", torch.float32)


class ChatModel:
    """One loaded model with its tokenizer: a tool shared by every case, not a character.

    It holds no conversation or character state; callers pass the system prompt and the
    messages on every call. `short` is the key in MODELS ("0.6b"). The device is picked
    when loading (see pick_device) and can be changed with `move()`. `baselines` caches
    the calibration scores used by `rank_intents()`.
    """

    def __init__(self, short: str) -> None:
        if short not in MODELS:
            raise ValueError(f"unknown model {short!r}; have {list(MODELS)}")
        self.short: str = short
        self.device: str
        self.dtype: torch.dtype
        self.device, self.dtype = pick_device(short)
        started: float = time.perf_counter()
        self.tokenizer: PreTrainedTokenizerBase = AutoTokenizer.from_pretrained(MODELS[short])
        # transformers' stubs for loaded models don't line up under strict mypy: keep it Any.
        self.model: Any = cast(
            Any, AutoModelForCausalLM.from_pretrained(MODELS[short], dtype=self.dtype)
        )
        self.model.to(self.device)
        self.model.eval()
        self.load_seconds: float = time.perf_counter() - started
        # Intent scores for a content-free question, per (prompt, question, intent names).
        self.baselines: dict[tuple[str, str, tuple[str, ...]], list[float]] = {}

    def move(self, device: str) -> None:
        """Move to "cuda" (fp16) or "cpu" (fp32); refuses the GPU when the model won't fit."""
        if device == self.device:
            return
        if device == "cuda" and not torch.cuda.is_available():
            raise ValueError("torch sees no usable GPU")
        if device == "cuda" and not gpu_fits(self.short):
            raise ValueError(f"{self.short} doesn't fit in the GPU's free memory")
        self.dtype = torch.float16 if device == "cuda" else torch.float32
        self.model.to(device=device, dtype=self.dtype)
        if self.device == "cuda":
            torch.cuda.empty_cache()
        self.device = device
        self.baselines.clear()  # scores shift a little with the precision

    def describe(self) -> str:
        dtype: str = str(self.dtype).removeprefix("torch.")
        return f"{self.short} on {self.device} ({dtype}), loaded in {self.load_seconds:.1f} s"

    def render(self, system: str, messages: list[Message]) -> str:
        """The conversation as the model reads it, ending where the assistant's turn starts."""
        full: list[Message] = [{"role": "system", "content": system}, *messages]
        text: str = str(
            self.tokenizer.apply_chat_template(
                full, tokenize=False, add_generation_prompt=True, enable_thinking=False
            )
        )
        return text

    @torch.no_grad()
    def reply(
        self,
        system: str,
        messages: list[Message],
        seed: int = 0,
        max_new_tokens: int = MAX_NEW_TOKENS,
        on_token: Callable[[str], None] | None = None,
    ) -> Reply:
        """Sample the next assistant turn. The fixed seed makes replays repeatable.

        `max_new_tokens` is a ceiling, not a target: the prompt sets how long replies are.
        `on_token`, if given, is called with the text of each new token as it is generated
        (see TokenStreamer); the complete reply is returned either way.
        """
        prompt: str = self.render(system, messages)
        encoded = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(
            self.device
        )
        torch.manual_seed(seed)
        started: float = time.perf_counter()
        output: torch.Tensor = self.model.generate(
            **encoded,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            pad_token_id=self.tokenizer.pad_token_id,
            streamer=TokenStreamer(self.tokenizer, on_token) if on_token else None,
        )
        seconds: float = time.perf_counter() - started
        new_tokens: torch.Tensor = output[0, encoded["input_ids"].shape[1] :]
        text: str = str(self.tokenizer.decode(new_tokens, skip_special_tokens=True))
        return Reply(THINK_RE.sub("", text).strip(), seconds, int(new_tokens.shape[0]))

    @torch.no_grad()
    def rank_intents(
        self, system: str, user: str, neutral: str, intents: list[str]
    ) -> list[IntentGuess]:
        """How likely the model is to answer with each intent name, best first.

        Free generation could answer with something not on the list. Here every name is scored
        as a complete answer (its tokens plus the end of turn). Small models favour some names
        whatever the player says, so each score is compared with the same name's score for
        `neutral`, a content-free question: what is left is how much the player's words moved it.
        The calibrated scores are turned into probabilities over the list.
        """
        key: tuple[str, str, tuple[str, ...]] = (system, neutral, tuple(intents))
        if key not in self.baselines:
            self.baselines[key] = self.score_answers(system, neutral, intents)
        raw: list[float] = self.score_answers(system, user, intents)
        scores: list[float] = [
            score - base for score, base in zip(raw, self.baselines[key], strict=True)
        ]
        top: float = max(scores)
        weights: list[float] = [math.exp(score - top) for score in scores]
        total: float = sum(weights)
        guesses: list[IntentGuess] = [
            IntentGuess(name, weight / total) for name, weight in zip(intents, weights, strict=True)
        ]
        return sorted(guesses, key=lambda guess: guess.probability, reverse=True)

    def score_answers(self, system: str, user: str, answers: list[str]) -> list[float]:
        """Log-probability of each answer as the whole assistant turn, computed in one batch."""
        prompt: str = self.render(system, [{"role": "user", "content": user}])
        prefix: list[int] = self.tokenizer(prompt, add_special_tokens=False).input_ids
        end: list[int] = self.tokenizer(END_OF_TURN, add_special_tokens=False).input_ids
        encoded: list[list[int]] = [
            self.tokenizer(answer, add_special_tokens=False).input_ids + end for answer in answers
        ]
        length: int = len(prefix) + max(len(answer) for answer in encoded)
        pad: int = int(self.tokenizer.pad_token_id)
        rows: list[list[int]] = []
        masks: list[list[int]] = []
        for answer in encoded:
            row: list[int] = prefix + answer
            rows.append(row + [pad] * (length - len(row)))
            masks.append([1] * len(row) + [0] * (length - len(row)))
        input_ids: torch.Tensor = torch.tensor(rows, device=self.device)
        attention: torch.Tensor = torch.tensor(masks, device=self.device)
        logits: torch.Tensor = self.model(input_ids=input_ids, attention_mask=attention).logits
        # The token at position p is predicted by the logits at position p - 1.
        logprobs: torch.Tensor = torch.log_softmax(logits[:, len(prefix) - 1 : -1].float(), -1)
        scores: list[float] = []
        for i, answer in enumerate(encoded):
            targets: torch.Tensor = torch.tensor(answer, device=self.device)
            picked: torch.Tensor = logprobs[i, torch.arange(len(answer)), targets]
            scores.append(float(picked.sum()))
        return scores
