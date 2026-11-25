"""The kid's memory between runs, so that a playthrough can go on over several sittings.

The game keeps its own state on the server; this file keeps the player's side: the
turns played, the notes, the lines already seen and the earlier sittings. One file per
game and persona, `runs/<game>-<persona>.state.json`: a run with --reset starts a new
playthrough and replaces it.

A reset starts the whole game over, for every persona, so each game also has
`runs/<game>.reset.txt`, the time of its last reset. A playthrough remembers the reset it
began with, and can't be continued once the game has been started over again.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from kid import Seen, Turn
from report import RUNS, Run, Sitting

VERSION: int = 1


@dataclass
class Saved:
    """A playthrough as the last run left it."""

    stamp: str  # the first sitting's time, in the report's file name
    reset_at: str  # when the game was started over for it ('' if unknown)
    notes: str
    howto: str
    known: set[str]
    turns: list[Turn]
    sittings: list[Sitting]


def state_path(game: str, persona: str) -> Path:
    return RUNS / f"{game}-{persona}.state.json"


def reset_path(game: str) -> Path:
    return RUNS / f"{game}.reset.txt"


def record_reset(game: str) -> str:
    """Note that the game has just been started over, and return when."""
    RUNS.mkdir(exist_ok=True)
    when: str = datetime.now().isoformat(timespec="seconds")
    reset_path(game).write_text(when, encoding="utf-8")
    return when


def last_reset(game: str) -> str:
    """When the playtester last started the game over ('' if never)."""
    path: Path = reset_path(game)
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def save_state(run: Run) -> Path:
    """Write the playthrough so far, this run's sitting included."""
    RUNS.mkdir(exist_ok=True)
    path: Path = state_path(run.game.key, run.kid.persona.key)
    data: dict[str, Any] = {
        "version": VERSION,
        "game": run.game.key,
        "persona": run.kid.persona.key,
        "stamp": run.stamp,
        "reset_at": run.reset_at,
        "notes": run.kid.notes,
        "howto": run.kid.howto,
        "known": sorted(run.kid.known),
        "sittings": [asdict(sitting) for sitting in run.sittings()],
        "turns": [asdict(turn) for turn in run.kid.turns],
    }
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    return path


def load_state(game: str, persona: str) -> Saved:
    """The saved playthrough, or FileNotFoundError if there is none."""
    path: Path = state_path(game, persona)
    if not path.exists():
        raise FileNotFoundError(
            f"Nothing to continue: no saved playthrough ({path.name} in runs/). "
            "Add --reset to start one."
        )
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != VERSION:
        raise ValueError(f"{path.name} was saved by another version of the playtester.")
    turns: list[Turn] = [Turn(**{**turn, "seen": Seen(**turn["seen"])}) for turn in data["turns"]]
    return Saved(
        stamp=str(data["stamp"]),
        reset_at=str(data.get("reset_at", "")),
        notes=str(data["notes"]),
        howto=str(data.get("howto", "")),
        known=set(data["known"]),
        turns=turns,
        sittings=[Sitting(**sitting) for sitting in data["sittings"]],
    )
