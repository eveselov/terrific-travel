"""Talk to a game character played by a local Qwen3 model, or replay a case's test lines.

Interactive: you are the player. Every reply shows the intent the model read in your words.
Replay: every conversation in the case runs through each model, and a Markdown transcript
with intent hits and speed lands in runs/.

Usage (from the repo root):
  uv run python llm_lab/lab.py fisherman
  uv run python llm_lab/lab.py sailor --model 1.7b
  uv run python llm_lab/lab.py fisherman --replay
  uv run python llm_lab/lab.py fisherman --replay --models 0.6b
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field
from pathlib import Path

from case import (
    LAB,
    NEUTRAL_SAY,
    Case,
    case_names,
    character_prompt,
    intent_prompt,
    intent_question,
    load_case,
)
from model import MAX_NEW_TOKENS, MODELS, ChatModel, IntentGuess, Message, Reply

RUNS: Path = LAB / "runs"
# How much conversation a character remembers by default, in exchanges (player line + reply).
HISTORY_EXCHANGES: int = 10
HELP: str = """Commands:
  /model NAME   talk to another model (0.6b, 1.7b, 4b); loads it the first time
  /cpu, /gpu    move the active model to the CPU (fp32) or the GPU (fp16)
  /tokens N     set the reply length limit (default 120 tokens; descriptions need ~300-400)
  /trim N       remember the last N exchanges (default 10; 0 = only the current line)
  /compare      toggle: every line goes to all loaded models, each with its own conversation
  /prompt       show the character prompt the model gets
  /reset        start the conversation over
  /list         show the loaded models and settings
  /help         show this help
  /quit         leave"""


@dataclass
class Turn:
    reply: Reply
    intents: list[IntentGuess]


@dataclass
class Lab:
    case: Case
    active: str
    models: dict[str, ChatModel] = field(default_factory=dict)
    histories: dict[str, list[Message]] = field(default_factory=dict)
    compare: bool = False
    max_new_tokens: int = MAX_NEW_TOKENS
    history_exchanges: int = HISTORY_EXCHANGES

    def load(self, short: str) -> ChatModel:
        if short not in self.models:
            print(f"  loading {MODELS[short]} ...", flush=True)
            self.models[short] = ChatModel(short)
            print(f"  {self.models[short].describe()}")
        return self.models[short]

    def turn(self, short: str, say: str, seed: int = 0) -> Turn:
        """Read the player's intent, then let the character answer.

        The history keeps the last `history_exchanges` exchanges, so the prompt stays small.
        """
        chat: ChatModel = self.load(short)
        history: list[Message] = self.histories.setdefault(short, [])
        intents: list[IntentGuess] = chat.rank_intents(
            intent_prompt(self.case),
            intent_question(say),
            intent_question(NEUTRAL_SAY),
            list(self.case.intents),
        )
        history.append({"role": "user", "content": say})
        reply: Reply = chat.reply(character_prompt(self.case), history, seed, self.max_new_tokens)
        history.append({"role": "assistant", "content": reply.text})
        self.trim(history)
        return Turn(reply, intents)

    def trim(self, history: list[Message]) -> None:
        """Drop the oldest messages beyond the limit (two messages per exchange)."""
        excess: int = len(history) - 2 * self.history_exchanges
        if excess > 0:
            del history[:excess]

    def reset(self) -> None:
        self.histories.clear()


def stats(turn: Turn) -> str:
    best: IntentGuess = turn.intents[0]
    return (
        f"intent {best.name} {best.probability:.2f} | {turn.reply.seconds:.1f} s, "
        f"{turn.reply.tokens_per_second:.0f} tok/s"
    )


# --- interactive -------------------------------------------------------------------------


def handle_command(line: str, lab: Lab) -> bool:
    """Apply a /command; returns False when the user wants to leave."""
    command, _, argument = line.partition(" ")
    argument = argument.strip()
    if command == "/quit":
        return False
    if command == "/help":
        print(HELP)
    elif command == "/model":
        if argument not in MODELS:
            print(f"  unknown model {argument!r}; have {list(MODELS)}")
        else:
            lab.load(argument)
            lab.active = argument
            print(f"  talking to {argument}")
    elif command == "/cpu" or command == "/gpu":
        chat: ChatModel = lab.models[lab.active]
        try:
            chat.move("cpu" if command == "/cpu" else "cuda")
            print(f"  {chat.describe()}")
        except ValueError as error:
            print(f"  {error}; staying on {chat.device}")
    elif command == "/tokens" and argument.isdigit() and int(argument) > 0:
        lab.max_new_tokens = int(argument)
        print(f"  reply limit {lab.max_new_tokens} tokens")
    elif command == "/trim" and argument.isdigit():
        lab.history_exchanges = int(argument)
        for history in lab.histories.values():
            lab.trim(history)
        print(f"  remembering the last {lab.history_exchanges} exchanges")
    elif command == "/compare":
        lab.compare = not lab.compare
        print(f"  compare {'on' if lab.compare else 'off'}: {list(lab.models)}")
    elif command == "/prompt":
        print(character_prompt(lab.case))
    elif command == "/reset":
        lab.reset()
        print("  conversation cleared")
    elif command == "/list":
        for loaded in lab.models.values():
            print(f"  {loaded.describe()}")
        print(
            f"  active={lab.active} compare={lab.compare} tokens={lab.max_new_tokens} "
            f"trim={lab.history_exchanges}"
        )
    else:
        print(f"  unknown command {line!r}; /help lists them")
    return True


def interactive(lab: Lab) -> None:
    print(f"{lab.case.title}: you are talking to {lab.case.name}, {lab.case.role}.")
    print(HELP)
    lab.load(lab.active)
    while True:
        try:
            line: str = input(f"{'compare' if lab.compare else lab.active}> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line.startswith("/"):
            if not handle_command(line, lab):
                break
            continue
        targets: list[str] = list(lab.models) if lab.compare else [lab.active]
        for short in targets:
            turn: Turn = lab.turn(short, line)
            label: str = f"[{short}] " if lab.compare else ""
            print(f"{label}{lab.case.name}: {turn.reply.text}")
            print(f"    ({stats(turn)})")


# --- replay ------------------------------------------------------------------------------


@dataclass
class Score:
    hits: int = 0
    lines: int = 0
    seconds: float = 0.0
    tokens: int = 0


def replay(lab: Lab, shorts: list[str]) -> Path:
    """Run every conversation through every model; write and return the transcript."""
    for short in shorts:
        lab.load(short)
    scores: dict[str, Score] = {short: Score() for short in shorts}
    body: list[str] = []
    for conversation in lab.case.conversations:
        print(f"conversation: {conversation.name}")
        body.append(f"## {conversation.name}\n")
        lab.reset()
        for number, line in enumerate(conversation.lines, start=1):
            body.append(f"**{number}. Player:** {line.say}  \n*expected intent:* `{line.intent}`\n")
            for short in shorts:
                turn: Turn = lab.turn(short, line.say, seed=number)
                best: IntentGuess = turn.intents[0]
                hit: bool = best.name == line.intent
                score: Score = scores[short]
                score.hits += hit
                score.lines += 1
                score.seconds += turn.reply.seconds
                score.tokens += turn.reply.tokens
                mark: str = "ok" if hit else "MISS"
                print(f"  {number}. [{short}] {mark} {stats(turn)}")
                body.append(
                    f"- **{short}** - intent `{best.name}` {best.probability:.2f} {mark}, "
                    f"{turn.reply.seconds:.1f} s  \n  {lab.case.name}: {turn.reply.text}"
                )
            body.append("")
    header: list[str] = [
        f"# {lab.case.title} - replay {time.strftime('%Y-%m-%d %H:%M')}\n",
        "| model | device | intents right | avg reply | tokens/s |",
        "| --- | --- | --- | --- | --- |",
    ]
    for short, score in scores.items():
        chat: ChatModel = lab.models[short]
        speed: float = score.tokens / score.seconds if score.seconds else 0.0
        average: float = score.seconds / score.lines if score.lines else 0.0
        header.append(
            f"| {short} | {chat.device} | {score.hits}/{score.lines} "
            f"| {average:.1f} s | {speed:.0f} |"
        )
    header += ["", "<details><summary>Character prompt</summary>", "", "```text"]
    header += [character_prompt(lab.case), "```", "", "</details>", ""]
    RUNS.mkdir(exist_ok=True)
    path: Path = RUNS / f"{lab.case.key}-{time.strftime('%Y%m%d-%H%M%S')}.md"
    path.write_text("\n".join(header + body) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("case", choices=case_names(), help="a case file in cases/")
    parser.add_argument("--model", default="0.6b", choices=list(MODELS), help="to talk to")
    parser.add_argument("--replay", action="store_true", help="run the case's test lines")
    parser.add_argument("--models", default="0.6b,1.7b", help="comma-separated models for --replay")
    args = parser.parse_args()

    lab: Lab = Lab(load_case(args.case), active=args.model)
    if args.replay:
        shorts: list[str] = [short.strip() for short in args.models.split(",")]
        unknown: list[str] = [short for short in shorts if short not in MODELS]
        if unknown:
            raise SystemExit(f"unknown models {unknown}; have {list(MODELS)}")
        print(f"transcript: {replay(lab, shorts)}")
    else:
        interactive(lab)


if __name__ == "__main__":
    main()
