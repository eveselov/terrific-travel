"""The run's report: a Markdown file in runs/ (git-ignored: it holds the game's texts).

A playthrough played over several runs is one report, one section per sitting.
"""

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from kid import Kid, Turn
from profiles import GameProfile

RUNS: Path = Path(__file__).parent / "runs"
UNHAPPY: tuple[str, ...] = ("confused", "frustrated", "bored")


@dataclass
class Sitting:
    """One run of the program: a playthrough has one or more."""

    started: str  # ISO date and time
    model: str
    first_turn: int
    last_turn: int
    outcome: str
    dollars: float
    debrief: str = ""


@dataclass
class Run:
    game: GameProfile
    kid: Kid
    model: str
    started: datetime
    outcome: str = ""
    debrief: str = ""
    dollars: float = 0.0
    earlier: list[Sitting] = field(default_factory=list)  # sittings before this one
    stamp: str = ""  # the first sitting's time, in the report's file name
    reset_at: str = ""  # when the game was started over for this playthrough

    def sittings(self) -> list[Sitting]:
        """Every sitting, this one last."""
        now: Sitting = Sitting(
            started=self.started.isoformat(timespec="minutes"),
            model=self.model,
            first_turn=self.kid.sitting_start + 1,
            last_turn=len(self.kid.turns),
            outcome=self.outcome,
            dollars=self.dollars,
            debrief=self.debrief,
        )
        return [*self.earlier, now]


def hints_used(run: Run) -> int:
    """Turns whose command starts with one of the game's hint commands."""
    words: set[str] = {word.lower() for word in run.game.hint_commands}
    firsts: list[list[str]] = [turn.typed.lower().split()[:1] for turn in run.kid.turns]
    return sum(1 for first in firsts if first and first[0] in words)


def write_report(run: Run, manual: bool = False) -> Path:
    """Write the report and return its path. Manual runs are named apart."""
    RUNS.mkdir(exist_ok=True)
    if not run.stamp:
        run.stamp = run.started.strftime("%Y%m%d-%H%M")
    kind: str = "-manual" if manual else ""
    path: Path = RUNS / f"{run.game.key}-{run.kid.persona.key}{kind}-{run.stamp}.md"
    path.write_text(render(run), encoding="utf-8")
    return path


def render(run: Run) -> str:
    kid: Kid = run.kid
    name: str = kid.persona.name
    turns: list[Turn] = kid.turns
    traits = kid.persona.traits
    sittings: list[Sitting] = run.sittings()
    out: list[str] = [f"# Playtest: {name} plays {run.game.title}", ""]
    out += [
        f"- **When:** {sittings[0].started.replace('T', ' ')}",
        f"- **Persona:** `{kid.persona.key}` ({name}, {kid.persona.age}), effort "
        f"`{traits.effort}`, attention {traits.attention_words} words, patience "
        f"{traits.patience} turns, memory {traits.memory_turns} turns ({traits.thoughts_kept} "
        f"with thoughts), notes {traits.notes_lines} + howto {traits.howto_lines} lines, "
        f"sittings of {traits.sitting_minutes[0]}–{traits.sitting_minutes[1]} minutes",
        f"- **Model:** `{run.model}`",
        f"- **Outcome:** {run.outcome}",
        f"- **Turns:** {len(turns)}, hints asked: {hints_used(run)}, typos: "
        f"{sum(1 for t in turns if t.typed != t.intended)}",
        f"- **Cost (estimate):** ${sum(s.dollars for s in sittings):.2f}",
        "",
    ]
    if len(sittings) > 1:
        out += ["## Sittings", "", "| # | Started | Turns | Model | Outcome | Cost |"]
        out.append("|---|---|---|---|---|---|")
        for number, s in enumerate(sittings, 1):
            out.append(
                f"| {number} | {s.started.replace('T', ' ')} | {s.first_turn}–{s.last_turn} "
                f"| `{s.model}` | {s.outcome} | ${s.dollars:.2f} |"
            )
        out.append("")
    talks: list[tuple[int, Sitting]] = [(n, s) for n, s in enumerate(sittings, 1) if s.debrief]
    if talks:
        out += [f"## What {name} said afterwards", ""]
        for number, sitting in talks:
            if len(sittings) > 1:
                out += [f"**After sitting {number}** (turn {sitting.last_turn}):", ""]
            out += [sitting.debrief.strip(), ""]

    feelings: Counter[str] = Counter(turn.feeling for turn in turns if turn.feeling)
    if feelings:
        out += ["## Feelings", "", " · ".join(f"{f} {n}" for f, n in feelings.most_common()), ""]
        out += ["Turn by turn: " + " ".join(feeling_mark(t.feeling) for t in turns), ""]
        out += [
            "(`.` content, `+` excited, proud or happy, `?` confused, `z` bored, `!` frustrated)",
            "",
        ]

    unhappy: list[Turn] = [t for t in turns if t.feeling in UNHAPPY]
    if unhappy:
        out += ["## Confused, bored or frustrated", ""]
        out += [f"- **{t.number}** ({t.feeling}) `{t.typed}`: {t.thought}" for t in unhappy]
        out.append("")

    noticed: list[Turn] = [t for t in turns if t.noticed.strip()]
    if noticed:
        out += [
            f"## What {name} thought was important",
            "",
            "Compare with the real clues: anything here that leads nowhere looked like a lead.",
            "",
        ]
        out += [f"- **{t.number}**: {t.noticed}" for t in noticed]
        out.append("")

    words: Counter[str] = Counter(w.lower() for t in turns for w in t.hard_words)
    if words:
        out += ["## Words not understood", ""]
        out.append(", ".join(f"{w} ({n})" if n > 1 else w for w, n in words.most_common()))
        out.append("")

    skimmed: list[Turn] = [t for t in turns if t.seen.skipped]
    if skimmed:
        out += ["## Screens too long to read", ""]
        out += [f"- **{t.number}**: {t.seen.skipped} words not read" for t in skimmed]
        out.append("")

    if kid.notes or kid.howto:
        out += [f"## What {name} kept in mind at the end", ""]
        out += ["About the game:", "", "```text", kid.notes or "(nothing)", "```", ""]
        out += ["How to play:", "", "```text", kid.howto or "(nothing)", "```", ""]

    out += ["## Transcript", ""]
    starts: dict[int, int] = {s.first_turn: n for n, s in enumerate(sittings, 1)}
    for turn in turns:
        if len(sittings) > 1 and turn.number in starts:
            out += [f"## Sitting {starts[turn.number]}", ""]
        out += [f"### {turn.number}" + (f" · {turn.feeling}" if turn.feeling else ""), ""]
        out += ["```text", turn.seen.text, "```", ""]
        if turn.thought:
            out += [f"*{turn.thought}*", ""]
        if turn.quit:
            out += ["**Stops playing.**", ""]
        elif turn.typed or turn.intended:
            typed: str = f"> `{turn.typed}`"
            if turn.typed != turn.intended:
                typed += f" (meant `{turn.intended}`)"
            out += [typed, ""]
    return "\n".join(out)


def feeling_mark(feeling: str) -> str:
    marks: dict[str, str] = {
        "excited": "+",
        "proud": "+",
        "happy": "+",
        "confused": "?",
        "bored": "z",
        "frustrated": "!",
    }
    return marks.get(feeling, ".")
