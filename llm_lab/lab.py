"""Talk to a game character played by a local Qwen3 model, or replay a case's test lines.

Interactive: you are the player. Every reply shows the intent the model read in your words.
For a narration case (a place, an object, a scenario) you play the game logic instead: each
line you type is a request to the narrator, answered on its own, without history.
A world (`world:<name>`) can be explored the same way: each line is a question to a neutral
informant who knows only the world sheet.
Replay: every conversation (or request, or probe) runs through each model, and a Markdown
transcript with intent hits and speed lands in runs/.

Usage (from the repo root):
  uv run python llm_lab/lab.py fisherman
  uv run python llm_lab/lab.py sailor --model 1.7b
  uv run python llm_lab/lab.py fisherman --replay
  uv run python llm_lab/lab.py fisherman --replay --models 0.6b
  uv run python llm_lab/lab.py okeanos --replay
  uv run python llm_lab/lab.py world:medieval --replay --models 0.6b
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from case import (
    LAB,
    NEUTRAL_SAY,
    Case,
    Request,
    Scene,
    World,
    case_names,
    character_prompt,
    intent_prompt,
    intent_question,
    load_case,
    load_world,
    narration_prompt,
    probe_prompt,
    probe_requests,
    world_names,
)
from model import MAX_NEW_TOKENS, MODELS, ChatModel, IntentGuess, Message, Reply

RUNS: Path = LAB / "runs"
# How much conversation a character remembers by default, in exchanges (player line + reply).
HISTORY_EXCHANGES: int = 10
# Reply limit when exploring a world: answers of a few sentences.
PROBE_TOKENS: int = 200
WORLD_PREFIX: str = "world:"
HELP: str = """Commands:
  /model NAME   talk to another model (0.6b, 1.7b, 4b); loads it the first time
  /cpu, /gpu    move the active model to the CPU (fp32) or the GPU (fp16)
  /tokens N     set the reply length limit (default 120 tokens; descriptions need ~300-400)
  /trim N       remember the last N exchanges (default 10; 0 = only the current line)
  /stream       toggle: show the reply as it is generated; /stream tokens marks each token
  /compare      toggle: every line goes to all loaded models, each with its own conversation
  /prompt       show the system prompt the model gets
  /reset        start the conversation over
  /list         show the loaded models and settings
  /help         show this help
  /quit         leave"""


@dataclass
class Turn:
    """The result of one player line to a character: the reply and the intent ranking.

    `intents` is sorted best first; `intents[0]` is what the game would react to.
    """

    reply: Reply
    intents: list[IntentGuess]


@dataclass
class Lab:
    """The session state shared by the interactive mode and the replay.

    It holds one case, the models loaded so far (loaded on first use and kept, so switching
    back is instant), and one conversation history per model, so in /compare mode each
    model follows its own conversation. `active` is the model the interactive mode talks
    to. `max_new_tokens` and `history_exchanges` are the /tokens and /trim settings, and
    `stream` is the /stream setting ("off", "text" or "tokens"; interactive mode only).
    For a character it runs `turn()`; for a narration or a world being explored, `ask()`.
    """

    case: Case | Scene | World
    active: str
    models: dict[str, ChatModel] = field(default_factory=dict)
    histories: dict[str, list[Message]] = field(default_factory=dict)
    compare: bool = False
    max_new_tokens: int = MAX_NEW_TOKENS
    history_exchanges: int = HISTORY_EXCHANGES
    stream: str = "off"

    def __post_init__(self) -> None:
        if isinstance(self.case, Scene):
            self.max_new_tokens = self.case.max_new_tokens
        elif isinstance(self.case, World):
            self.max_new_tokens = PROBE_TOKENS

    def prompt(self) -> str:
        if isinstance(self.case, Scene):
            return narration_prompt(self.case)
        if isinstance(self.case, World):
            return probe_prompt(self.case)
        return character_prompt(self.case)

    def requests(self) -> list[Request]:
        """The test requests of a narration, or the probes of a world."""
        if isinstance(self.case, Scene):
            return self.case.requests
        if isinstance(self.case, World):
            return probe_requests(self.case)
        return []

    def title(self) -> str:
        if isinstance(self.case, World):
            return f"Exploring {self.case.name}"
        return self.case.title

    def file_key(self) -> str:
        """The transcript name: the case key, or world-<key> for a world."""
        if isinstance(self.case, World):
            return f"world-{self.case.key}"
        return self.case.key

    def load(self, short: str) -> ChatModel:
        if short not in self.models:
            print(f"  loading {MODELS[short]} ...", flush=True)
            self.models[short] = ChatModel(short)
            print(f"  {self.models[short].describe()}")
        return self.models[short]

    def turn(
        self, short: str, say: str, seed: int = 0, on_token: Callable[[str], None] | None = None
    ) -> Turn:
        """Read the player's intent, then let the character answer.

        The history keeps the last `history_exchanges` exchanges, so the prompt stays small.
        """
        assert isinstance(self.case, Case)
        chat: ChatModel = self.load(short)
        history: list[Message] = self.histories.setdefault(short, [])
        intents: list[IntentGuess] = chat.rank_intents(
            intent_prompt(self.case),
            intent_question(say),
            intent_question(NEUTRAL_SAY),
            list(self.case.intents),
        )
        history.append({"role": "user", "content": say})
        reply: Reply = chat.reply(
            character_prompt(self.case), history, seed, self.max_new_tokens, on_token
        )
        history.append({"role": "assistant", "content": reply.text})
        self.trim(history)
        return Turn(reply, intents)

    def ask(
        self, short: str, text: str, seed: int = 0, on_token: Callable[[str], None] | None = None
    ) -> Reply:
        """Answer one request to a narrator or one probe of a world; each stands alone."""
        assert not isinstance(self.case, Case)
        chat: ChatModel = self.load(short)
        messages: list[Message] = [{"role": "user", "content": text}]
        return chat.reply(self.prompt(), messages, seed, self.max_new_tokens, on_token)

    def trim(self, history: list[Message]) -> None:
        """Drop the oldest messages beyond the limit (two messages per exchange)."""
        excess: int = len(history) - 2 * self.history_exchanges
        if excess > 0:
            del history[:excess]

    def reset(self) -> None:
        self.histories.clear()


def timing(reply: Reply) -> str:
    return f"{reply.seconds:.1f} s, {reply.tokens} tokens, {reply.tokens_per_second:.0f} tok/s"


def stats(turn: Turn) -> str:
    best: IntentGuess = turn.intents[0]
    return f"intent {best.name} {best.probability:.2f} | {timing(turn.reply)}"


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
    elif command == "/stream":
        if argument == "tokens":
            lab.stream = "tokens"
        elif argument == "off":
            lab.stream = "off"
        else:
            lab.stream = "off" if lab.stream != "off" else "text"
        print(f"  streaming {lab.stream}")
    elif command == "/compare":
        lab.compare = not lab.compare
        print(f"  compare {'on' if lab.compare else 'off'}: {list(lab.models)}")
    elif command == "/prompt":
        print(lab.prompt())
    elif command == "/reset":
        lab.reset()
        print("  conversation cleared")
    elif command == "/list":
        for loaded in lab.models.values():
            print(f"  {loaded.describe()}")
        print(
            f"  active={lab.active} compare={lab.compare} tokens={lab.max_new_tokens} "
            f"trim={lab.history_exchanges} stream={lab.stream}"
        )
    else:
        print(f"  unknown command {line!r}; /help lists them")
    return True


def interactive(lab: Lab) -> None:
    if isinstance(lab.case, Scene):
        print(f"{lab.case.title}: you are the game, asking the narrator about {lab.case.subject}.")
    elif isinstance(lab.case, World):
        print(f"{lab.title()}: ask the informant anything about this world.")
        print('Set a perspective with " | ", as in the examples: Asked by: ... | Where: ... | ...')
    if not isinstance(lab.case, Case):
        print("Examples from the file:")
        for request in lab.requests():
            print("  " + request.ask.replace("\n", " | "))
    else:
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
            label: str = f"[{short}] " if lab.compare else ""
            if isinstance(lab.case, Case):
                label += f"{lab.case.name}: "
            on_token: Callable[[str], None] | None = None
            if lab.stream != "off":
                print(label, end="", flush=True)
                on_token = print_token if lab.stream == "text" else print_marked_token
            if not isinstance(lab.case, Case):
                reply: Reply = lab.ask(short, line.replace(" | ", "\n"), on_token=on_token)
                print() if on_token else print(f"{label}{reply.text}")
                print(f"    ({timing(reply)})")
            else:
                turn: Turn = lab.turn(short, line, on_token=on_token)
                print() if on_token else print(f"{label}{turn.reply.text}")
                print(f"    ({stats(turn)})")


def print_token(piece: str) -> None:
    print(piece, end="", flush=True)


def print_marked_token(piece: str) -> None:
    """A token followed by a bar, so the token boundaries show (end of turn decodes to "")."""
    if piece:
        print(piece + "|", end="", flush=True)


# --- replay ------------------------------------------------------------------------------


@dataclass
class Score:
    """Running totals for one model during a replay, for the table at the top.

    `hits` counts lines whose best intent matched the expected one (characters only);
    `lines`, `seconds` and `tokens` give the average reply time and the speed.
    """

    hits: int = 0
    lines: int = 0
    seconds: float = 0.0
    tokens: int = 0


def replay(lab: Lab, shorts: list[str]) -> Path:
    """Run every conversation (or request) through every model; write the transcript."""
    for short in shorts:
        lab.load(short)
    if not isinstance(lab.case, Case):
        return replay_requests(lab, shorts)
    case: Case = lab.case
    scores: dict[str, Score] = {short: Score() for short in shorts}
    body: list[str] = []
    for conversation in case.conversations:
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
                    f"{turn.reply.seconds:.1f} s  \n  {case.name}: {turn.reply.text}"
                )
            body.append("")
    header: list[str] = [
        f"# {case.title} - replay {time.strftime('%Y-%m-%d %H:%M')}\n",
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
    return write_transcript(lab, header, body)


def replay_requests(lab: Lab, shorts: list[str]) -> Path:
    """Send every request of a narration, or every probe of a world, to every model."""
    scores: dict[str, Score] = {short: Score() for short in shorts}
    body: list[str] = []
    for number, request in enumerate(lab.requests(), start=1):
        print(f"request: {request.name}")
        asked: str = request.ask.replace("\n", "  \n")  # keep the lines in Markdown
        body.append(f"## {number}. {request.name}\n\n**Request:**  \n{asked}\n")
        for short in shorts:
            reply: Reply = lab.ask(short, request.ask, seed=number)
            score: Score = scores[short]
            score.lines += 1
            score.seconds += reply.seconds
            score.tokens += reply.tokens
            print(f"  {number}. [{short}] {timing(reply)}")
            body.append(f"- **{short}** - {timing(reply)}\n\n  {reply.text}\n")
    header: list[str] = [
        f"# {lab.title()} - replay {time.strftime('%Y-%m-%d %H:%M')}\n",
        f"Reply limit: {lab.max_new_tokens} tokens.\n",
        "| model | device | avg reply | avg tokens | tokens/s |",
        "| --- | --- | --- | --- | --- |",
    ]
    for short, score in scores.items():
        speed: float = score.tokens / score.seconds if score.seconds else 0.0
        header.append(
            f"| {short} | {lab.models[short].device} | {score.seconds / score.lines:.1f} s "
            f"| {score.tokens / score.lines:.0f} | {speed:.0f} |"
        )
    return write_transcript(lab, header, body)


def write_transcript(lab: Lab, header: list[str], body: list[str]) -> Path:
    """Add the system prompt to the header and save everything under runs/."""
    header += ["", "<details><summary>System prompt</summary>", "", "```text"]
    header += [lab.prompt(), "```", "", "</details>", ""]
    RUNS.mkdir(exist_ok=True)
    path: Path = RUNS / f"{lab.file_key()}-{time.strftime('%Y%m%d-%H%M%S')}.md"
    path.write_text("\n".join(header + body) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    choices: list[str] = case_names() + [WORLD_PREFIX + name for name in world_names()]
    parser.add_argument(
        "case", choices=choices, help="a case in cases/, or world:<name> to explore a world"
    )
    parser.add_argument("--model", default="0.6b", choices=list(MODELS), help="to talk to")
    parser.add_argument("--replay", action="store_true", help="run the case's test lines")
    parser.add_argument("--models", default="0.6b,1.7b", help="comma-separated models for --replay")
    args = parser.parse_args()

    subject: Case | Scene | World = (
        load_world(args.case.removeprefix(WORLD_PREFIX))
        if args.case.startswith(WORLD_PREFIX)
        else load_case(args.case)
    )
    lab: Lab = Lab(subject, active=args.model)
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
