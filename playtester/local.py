"""The player agent's mind on a local model: Qwen3 (0.6B, 1.7B or 4B), in this process.

The same prompts as Claude's (brain.py) and the same limits (kid.py), so a run on a local
model compares with a Claude run. Two differences:

- No structured output: the model is asked for one JSON object and its answer is read
  leniently. An answer that still can't be read is asked for once more, and then the kid
  just looks around; the report counts those turns (`unreadable`).
- No cost: the tokens are priced as the cheapest Claude model (brain.CHEAPEST_MODEL), so the
  figure is what the run saved.

Loading follows llm_lab/model.py (copied, not imported: the repo's folders share no code):
transformers, the GPU in fp16 when the weights fit, otherwise the CPU in fp32. The first use
of a size downloads it into the Hugging Face cache (0.6B about 1.5 GB, 1.7B 4 GB, 4B 8 GB);
with HF_HUB_OFFLINE=1 only the cache is used.
"""

import json
import re
from typing import Any, cast, get_args

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizerBase

from brain import CHEAPEST_MODEL, Feeling, Move, Spend, debrief_question, system_prompt, turn_prompt
from kid import Kid, Seen

# --model name -> Hugging Face id.
MODELS: dict[str, str] = {
    "qwen3-0.6b": "Qwen/Qwen3-0.6B",
    "qwen3-1.7b": "Qwen/Qwen3-1.7B",
    "qwen3-4b": "Qwen/Qwen3-4B",
}
# Real parameter counts (with embeddings), to judge whether fp16 weights fit on the GPU.
PARAMS: dict[str, float] = {"qwen3-0.6b": 0.75e9, "qwen3-1.7b": 2.0e9, "qwen3-4b": 4.0e9}
GPU_HEADROOM: float = 1.3  # room beyond the weights: activations, the KV cache, CUDA

# Qwen's recommended sampling, without and with thinking.
SAMPLING: dict[bool, dict[str, float | int]] = {
    False: {"temperature": 0.7, "top_p": 0.8, "top_k": 20},
    True: {"temperature": 0.6, "top_p": 0.95, "top_k": 20},
}
# A move is a short JSON object; thinking first needs room. The talk afterwards is longer.
MOVE_TOKENS: dict[bool, int] = {False: 600, True: 2500}
DEBRIEF_TOKENS: int = 700

THINK: re.Pattern[str] = re.compile(r"<think>.*?(</think>|$)", re.DOTALL)
FEELINGS: tuple[str, ...] = get_args(Feeling)

ANSWER_FORMAT: str = (
    """

Answer with one JSON object and nothing else, with exactly these keys:
{"thought": "...", "command": "...", "feeling": "curious", "noticed": "", \
"hard_words": [], "notes": "...", "howto": "...", "quit": false}
"feeling" is one of: """
    + ", ".join(FEELINGS)
    + """. "notes" and "howto" are short lines \
separated by \\n. "quit" is true or false."""
)

RETRY: str = (
    "That answer couldn't be read. Answer again with only the JSON object, with the keys "
    "thought, command, feeling, noticed, hard_words, notes, howto and quit."
)


def is_local(model: str) -> bool:
    return model in MODELS


def gpu_fits(name: str) -> bool:
    """Whether the model's fp16 weights fit in the GPU's free memory, with headroom."""
    if not torch.cuda.is_available():
        return False
    free_bytes: int = torch.cuda.mem_get_info()[0]
    return free_bytes > PARAMS[name] * 2 * GPU_HEADROOM


def lines(value: Any) -> str:
    """Notes as the model wrote them, a string or a list of lines, as lines."""
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value or "")


def read_move(text: str) -> Move | None:
    """The move in a model's answer: the JSON object in it, read leniently. None if none."""
    text = THINK.sub("", text)
    start: int = text.find("{")
    end: int = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data: Any = json.loads(text[start : end + 1], strict=False)  # line breaks in strings
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    command: str = str(data.get("command") or "").strip().split("\n")[0]
    if not command:
        return None
    feeling: str = str(data.get("feeling") or "").strip().lower()
    words: Any = data.get("hard_words")
    return Move(
        thought=str(data.get("thought") or ""),
        command=command,
        feeling=cast(Feeling, feeling if feeling in FEELINGS else "curious"),
        noticed=str(data.get("noticed") or ""),
        hard_words=[str(word) for word in words] if isinstance(words, list) else [],
        notes=lines(data.get("notes")),
        howto=lines(data.get("howto")),
        quit=data.get("quit") in (True, "true", "yes"),
    )


class LocalBrain:
    """Asks a local Qwen3 for the kid's next move."""

    def __init__(self, name: str, seed: int = 0) -> None:
        if name not in MODELS:
            raise ValueError(f"Unknown local model {name!r}; there are {', '.join(MODELS)}.")
        self.name: str = name
        self.seed: int = seed
        on_gpu: bool = gpu_fits(name)
        self.device: str = "cuda" if on_gpu else "cpu"
        dtype: torch.dtype = torch.float16 if on_gpu else torch.float32
        self.tokenizer: PreTrainedTokenizerBase = AutoTokenizer.from_pretrained(MODELS[name])
        # transformers' stubs for loaded models don't line up under strict mypy: keep it Any.
        self.model_obj: Any = cast(
            Any, AutoModelForCausalLM.from_pretrained(MODELS[name], dtype=dtype)
        )
        self.model_obj.to(self.device)
        self.model_obj.eval()
        precision: str = "fp16" if on_gpu else "fp32"
        self.model: str = f"{name} (local, {self.device} {precision})"
        self.spend: Spend = Spend()
        self.cost_note: str = "as the cheapest Claude model would cost; locally: free"
        self.unreadable: int = 0  # turns whose answer couldn't be read, even asked again
        self.calls: int = 0

    @torch.no_grad()
    def generate(self, system: str, messages: list[dict[str, str]], think: bool, limit: int) -> str:
        """One answer from the model; its tokens counted at the cheapest Claude's prices."""
        full: list[dict[str, str]] = [{"role": "system", "content": system}, *messages]
        prompt: str = str(
            self.tokenizer.apply_chat_template(
                full, tokenize=False, add_generation_prompt=True, enable_thinking=think
            )
        )
        encoded: Any = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        encoded = encoded.to(self.device)
        self.calls += 1
        torch.manual_seed(self.seed + self.calls)  # a run with --seed repeats
        output: torch.Tensor = self.model_obj.generate(
            **encoded,
            max_new_tokens=limit,
            do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id,
            **SAMPLING[think],
        )
        prompt_tokens: int = int(encoded["input_ids"].shape[1])
        new_tokens: torch.Tensor = output[0, prompt_tokens:]
        self.spend.add_tokens(CHEAPEST_MODEL, fresh=prompt_tokens, output=int(new_tokens.shape[0]))
        return str(self.tokenizer.decode(new_tokens, skip_special_tokens=True))

    def decide(self, kid: Kid, seen: Seen) -> Move:
        think: bool = kid.persona.traits.effort != "low"  # smarter personas think first
        system: str = system_prompt(kid) + ANSWER_FORMAT
        messages: list[dict[str, str]] = [{"role": "user", "content": turn_prompt(kid, seen)}]
        answer: str = self.generate(system, messages, think, MOVE_TOKENS[think])
        move: Move | None = read_move(answer)
        if move is None:  # once more, with the answer and a reminder
            messages += [
                {"role": "assistant", "content": THINK.sub("", answer).strip()},
                {"role": "user", "content": RETRY},
            ]
            move = read_move(self.generate(system, messages, False, MOVE_TOKENS[False]))
        if move is None:
            self.unreadable += 1
            return Move(
                thought="(The model's answer couldn't be read, so the kid looks around.)",
                command="look",
                feeling="confused",
                noticed="",
                hard_words=[],
                notes=kid.notes,
                howto=kid.howto,
                quit=False,
            )
        return move

    def debrief(self, kid: Kid, outcome: str) -> str:
        messages: list[dict[str, str]] = [
            {"role": "user", "content": debrief_question(kid, outcome)}
        ]
        return THINK.sub("", self.generate(system_prompt(kid), messages, False, DEBRIEF_TOKENS))
