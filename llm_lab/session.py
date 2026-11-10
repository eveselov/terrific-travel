"""Recordings of interactive sessions: written step by step, read back for playback.

Every interactive session is recorded automatically to runs/<case>-<time>.log.toml (the
file appears with the first step). The double suffix keeps recordings apart from other TOML
files (cases, worlds, configs). A recording is plain TOML, meant to be edited by hand:
delete a dull step, fix a typo, add `comment` steps for a presentation. `lab.py --play`
shows it again step by step. TOML can be read with the standard library but not written,
so this module writes it itself; the format is simple enough for that.
"""

from __future__ import annotations

import json
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from case import LAB

RUNS: Path = LAB / "runs"
SUFFIX: str = ".log.toml"
# Step fields in the order they are written.
FIELDS: tuple[str, ...] = (
    "comment",
    "command",
    "say",
    "model",
    "reply",
    "intent",
    "probability",
    "seconds",
)


@dataclass
class Step:
    """One step of a session; exactly one of `comment`, `command` and `say` is set.

    - `comment`: a note typed as `# ...` (or added later in the file); never sent to a model.
    - `command`: a command that changes later replies (/model, /trim, /tokens, /reset, /cpu,
      /gpu), so a live playback can repeat it.
    - `say`: what was typed, with the `model` that answered, its `reply`, the best `intent`
      and its `probability` (characters only) and the generation time in `seconds`. In
      /compare mode one line gives one step per model, with the same `say`.
    """

    comment: str | None = None
    command: str | None = None
    say: str | None = None
    model: str | None = None
    reply: str | None = None
    intent: str | None = None
    probability: float | None = None
    seconds: float | None = None


@dataclass
class Recording:
    """A whole session: which case it was (`case`, as given to lab.py, e.g. "fisherman"
    or "world:medieval"), its title, when it started, and the steps in order."""

    case: str
    title: str
    started: str
    steps: list[Step] = field(default_factory=list)

    def to_toml(self) -> str:
        lines: list[str] = [
            "# A recorded lab session. Edit freely: delete steps, add [[step]] comment = ...",
            "# Play it with: uv run python llm_lab/lab.py --play <this file> [--live]",
            "",
            f"case = {toml_value(self.case)}",
            f"title = {toml_value(self.title)}",
            f"started = {toml_value(self.started)}",
        ]
        for step in self.steps:
            lines += ["", "[[step]]"]
            for name in FIELDS:
                value: str | float | None = getattr(step, name)
                if value is not None:
                    lines.append(f"{name} = {toml_value(value)}")
        return "\n".join(lines) + "\n"


def toml_value(value: str | float) -> str:
    """A TOML literal: a number as is, a string quoted.

    A JSON string is also a valid TOML basic string. Text with line breaks becomes a
    multi-line literal string instead, which stays readable when edited by hand.
    """
    if isinstance(value, float):
        return f"{value:.2f}"
    if "\n" in value and "'''" not in value:
        return "'''\n" + value + "'''"
    return json.dumps(value, ensure_ascii=False)


def recording_stem(name: str) -> str:
    """A recording's name without its suffix: "banana.log.toml" and "banana" both give "banana"."""
    return name.removesuffix(SUFFIX).removesuffix(".toml")


def load_recording(path: Path) -> Recording:
    if not path.exists():
        raise SystemExit(f"no recording {path}")
    with path.open("rb") as file:
        data: dict[str, Any] = tomllib.load(file)
    steps: list[Step] = []
    for raw in data.get("step", []):
        unknown: set[str] = set(raw) - set(FIELDS)
        if unknown:
            raise SystemExit(f"{path.name}: unknown step fields {sorted(unknown)}")
        steps.append(Step(**raw))
    return Recording(data["case"], data["title"], data.get("started", ""), steps)


class Recorder:
    """Writes the session to its file after every step, so nothing is lost on a crash.

    The file is created with the first step, so sessions where nothing was asked leave
    no file behind. `save_as()` renames it, and recording continues in the new file.
    """

    def __init__(self, case: str, title: str) -> None:
        stamp: str = time.strftime("%Y%m%d-%H%M%S")
        self.path: Path = RUNS / f"{case.replace(':', '-')}-{stamp}{SUFFIX}"
        self.recording: Recording = Recording(case, title, time.strftime("%Y-%m-%d %H:%M"))

    def add(self, step: Step) -> None:
        self.recording.steps.append(step)
        self.write()

    def write(self) -> None:
        RUNS.mkdir(exist_ok=True)
        self.path.write_text(self.recording.to_toml(), encoding="utf-8")

    def save_as(self, name: str) -> Path:
        """Move the recording to runs/<name>.log.toml; refuses to overwrite another file."""
        target: Path = RUNS / f"{recording_stem(name)}{SUFFIX}"
        if target.exists():
            raise ValueError(f"{target.name} already exists")
        if self.path.exists():
            self.path.rename(target)
        self.path = target
        if self.recording.steps:
            self.write()
        return target
