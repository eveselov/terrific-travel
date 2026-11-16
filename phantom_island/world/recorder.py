"""
The scenario recorder: a developer plays, and the game writes what they did as a batch file
that `batchcommand` can play back (`world/scenarios/<name>.ev`, like `island.ev`).

Only the recording developer's own commands are kept (DECISIONS.md, 8: transcripts are made
deliberately by the developer), and only commands any player could type: building and admin
commands, and lines the game didn't understand, are left out. After each command the file
notes what the game recorded (new clues, notebook entries, where you are now), and leaves a
`Why:` line to fill in by hand.

A recording always starts with a new expedition, so its file always plays back the same way.
It is kept in a persistent Attribute on the character, so it survives a `reload`.
"""

import re
from datetime import date
from pathlib import Path
from typing import Any

from django.conf import settings

RECORDING: str = "recording"
NAME: re.Pattern[str] = re.compile(r"[a-z][a-z0-9_]*")
FIRST_COMMAND: str = "startover yes"
WHY: str = "Why:"


def scenario_dir() -> Path:
    """Where recorded scenarios are written: `world/scenarios/` in the game folder."""
    return Path(settings.GAME_DIR) / "world" / "scenarios"


def scenario_path(name: str) -> Path:
    return scenario_dir() / f"{name}.ev"


def valid_name(name: str) -> bool:
    return bool(NAME.fullmatch(name))


def is_recording(character: Any) -> bool:
    return bool(character.attributes.has(RECORDING))


def recording_name(character: Any) -> str | None:
    data: dict[str, Any] | None = _data(character)
    return str(data["name"]) if data is not None else None


def begin(character: Any, name: str) -> None:
    """Start recording into scenario `name` (the new expedition is the caller's to start)."""
    character.attributes.add(RECORDING, {"name": name, "steps": []})


def step(character: Any, command: str) -> None:
    """The character typed `command`: a new step of the recording, if one is running."""
    data: dict[str, Any] | None = _data(character)
    if data is None or not command.strip():
        return
    data["steps"].append([command.strip(), []])
    character.attributes.add(RECORDING, data)


def note(character: Any, text: str) -> None:
    """Something the game recorded during the current step (a clue, an idea, a move)."""
    data: dict[str, Any] | None = _data(character)
    if data is None or not data["steps"]:
        return
    notes: list[str] = data["steps"][-1][1]
    if text not in notes:
        notes.append(text)
        character.attributes.add(RECORDING, data)


def stop(character: Any) -> tuple[Path, int] | None:
    """Write the scenario file and end the recording. Returns its path and step count."""
    data: dict[str, Any] | None = _data(character)
    if data is None:
        return None
    name: str = str(data["name"])
    steps: list[tuple[str, list[str]]] = [(str(c), [str(n) for n in ns]) for c, ns in data["steps"]]
    path: Path = scenario_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scenario_text(name, str(character.key), steps), encoding="utf-8")
    character.attributes.remove(RECORDING)
    return path, len(steps)


def cancel(character: Any) -> bool:
    """End the recording without writing anything. Returns False if none was running."""
    if not is_recording(character):
        return False
    character.attributes.remove(RECORDING)
    return True


def scenario_text(name: str, who: str, steps: list[tuple[str, list[str]]]) -> str:
    """The batch file for a recording: a header, then each command with its notes."""
    lines: list[str] = [
        f"# SPOILERS. Phantom Island scenario '{name}', recorded by {who} on {date.today()}.",
        "#",
        "# Play it as a builder, with nobody else playing:",
        f"#   batchcommand/interactive scenarios.{name}   (ss: next command, qq: stop)",
        "# The notes after each command are what the game recorded. Fill in the reasons",
        f"# after '{WHY}' if you want this to be an annotated scenario, like island.ev.",
        "# Keep a '#' line after every command: it ends the command.",
        "#",
        FIRST_COMMAND,
        "# A new expedition: the ship in port, the journal and notebooks empty, you in Limbo.",
    ]
    for command, notes in steps:
        lines.append(command)
        lines.extend(f"#   {text}" for text in notes)
        lines.append(f"#   {WHY}")
    return "\n".join(lines) + "\n"


def _data(character: Any) -> dict[str, Any] | None:
    raw: Any = character.attributes.get(RECORDING)
    if raw is None:
        return None
    from evennia.utils.dbserialize import deserialize

    data: dict[str, Any] = deserialize(raw)
    return data
