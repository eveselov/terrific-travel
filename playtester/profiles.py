"""Kid personas and game profiles, read from TOML files.

A persona (`personas/*.toml`) is who plays: a name, a short description, and the traits
the playtester enforces. A game profile (`games/*.toml`) is how to reach and reset a
game. Only the persona is shown to the player agent; the game profile stays outside.
"""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

HERE: Path = Path(__file__).parent
PERSONAS: Path = HERE / "personas"
GAMES: Path = HERE / "games"

Effort = Literal["low", "medium", "high", "xhigh", "max"]
EFFORTS: tuple[str, ...] = ("low", "medium", "high", "xhigh", "max")


@dataclass(frozen=True)
class Traits:
    """What the playtester enforces, whatever the model would rather do."""

    attention_words: int = 150  # words of one screen read before skimming past the rest
    tired_after: int = 80  # turns; after that, attention is halved
    patience: int = 6  # turns with nothing new before boredom shows
    memory_turns: int = 6  # earlier turns remembered word for word
    notes_lines: int = 6  # lines of notes kept "in the head"
    typo_rate: float = 0.05  # chance that a typed command gets a typo
    effort: Effort = "low"  # how hard the model thinks: the persona's smartness


@dataclass(frozen=True)
class Persona:
    key: str  # the file name: personas/<key>.toml
    name: str  # also the account and character name in the game
    age: int
    about: str
    experience: str
    traits: Traits = field(default_factory=Traits)


@dataclass(frozen=True)
class GameProfile:
    key: str
    title: str
    host: str
    port: int
    reset: tuple[str, ...]  # typed by the admin account before the player logs in
    end_texts: tuple[str, ...]  # the run is finished when the game shows one of these
    hint_commands: tuple[str, ...]  # counted in the report
    quiet_seconds: float  # the game has finished answering after this much silence


def _read(path: Path) -> dict[str, Any]:
    if not path.exists():
        choices: str = ", ".join(sorted(p.stem for p in path.parent.glob("*.toml")))
        raise FileNotFoundError(f"No {path.name} in {path.parent.name}/. There are: {choices}.")
    with path.open("rb") as file:
        return tomllib.load(file)


def load_persona(key: str) -> Persona:
    data: dict[str, Any] = _read(PERSONAS / f"{key}.toml")
    raw: dict[str, Any] = dict(data.get("traits", {}))
    unknown: set[str] = set(raw) - set(Traits.__dataclass_fields__)
    if unknown:
        raise ValueError(f"personas/{key}.toml: unknown traits {', '.join(sorted(unknown))}.")
    if raw.get("effort", "low") not in EFFORTS:
        raise ValueError(f"personas/{key}.toml: effort is one of {', '.join(EFFORTS)}.")
    return Persona(
        key=key,
        name=str(data["name"]),
        age=int(data["age"]),
        about=str(data["about"]).strip(),
        experience=str(data["experience"]).strip(),
        traits=Traits(**raw),
    )


def load_game(key: str) -> GameProfile:
    data: dict[str, Any] = _read(GAMES / f"{key}.toml")
    return GameProfile(
        key=key,
        title=str(data["title"]),
        host=str(data.get("host", "localhost")),
        port=int(data["port"]),
        reset=tuple(cast(list[str], data.get("reset", []))),
        end_texts=tuple(cast(list[str], data.get("end_texts", []))),
        hint_commands=tuple(cast(list[str], data.get("hint_commands", []))),
        quiet_seconds=float(data.get("quiet_seconds", 2.0)),
    )
