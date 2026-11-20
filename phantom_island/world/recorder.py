"""
The scenario recorder: a developer plays, and the game writes what they did as a batch file
that `batchcommand` can play back (`world/scenarios/<name>.ev`, like `island.ev`).

Only the recording developer's own commands are kept (DECISIONS.md, 8: transcripts are made
deliberately by the developer), and only commands any player could type: building and admin
commands, and lines the game didn't understand, are left out. After each command the file
notes what the game recorded (new clues, notebook entries, where you are now), and leaves a
`Why:` line to fill in by hand.

A recording always starts with a new expedition, so its file always plays back the same way.
It can start from an earlier scenario (`record start <name> from <earlier>`): that file is
played first, unrecorded, and its text, hand-written `Why:` lines included, opens the new
file. A checkpoint (`record checkpoint <next>`) writes the file and goes on recording under
the next name, so a chain of scenarios needs no replaying. The recording is kept in a
persistent Attribute on the character, so it survives a `reload`.
"""

import re
from datetime import date
from pathlib import Path
from typing import Any

from django.conf import settings

RECORDING: str = "recording"
NAME: re.Pattern[str] = re.compile(r"[a-z][a-z0-9_]*")
FIRST_COMMAND: str = "startover yes"
FIRST_NOTE: str = (
    "# A new expedition: the ship in port, the journal and notebooks empty, you in Limbo."
)
WHY: str = "Why:"


def scenario_dir() -> Path:
    """Where recorded scenarios are written: `world/scenarios/` in the game folder."""
    return Path(settings.GAME_DIR) / "world" / "scenarios"


def scenario_path(name: str) -> Path:
    return scenario_dir() / f"{name}.ev"


def bare_name(name: str) -> str:
    """A scenario's name as `record` takes it: `scenarios.island` (as `batchcommand` has it)."""
    return name.removeprefix(f"{scenario_dir().name}.")


def valid_name(name: str) -> bool:
    return bool(NAME.fullmatch(name))


def is_recording(character: Any) -> bool:
    return bool(character.attributes.has(RECORDING))


def recording_name(character: Any) -> str | None:
    data: dict[str, Any] | None = _data(character)
    return str(data["name"]) if data is not None else None


def begin(character: Any, name: str, base: list[str] | None = None) -> None:
    """
    Start recording into scenario `name` (the new expedition is the caller's to start).
    `base` is the text of an earlier scenario after its first command (`earlier_scenario`):
    the new file starts with it.
    """
    character.attributes.add(
        RECORDING, {"name": name, "steps": [], "base": list(base or []), "paused": False}
    )


def rename(character: Any, name: str) -> None:
    """Go on recording, the steps so far included, under scenario `name`."""
    data: dict[str, Any] | None = _data(character)
    if data is not None:
        data["name"] = name
        character.attributes.add(RECORDING, data)


def pause(character: Any, paused: bool) -> None:
    """While paused (an earlier scenario being played), nothing is recorded."""
    data: dict[str, Any] | None = _data(character)
    if data is not None:
        data["paused"] = paused
        character.attributes.add(RECORDING, data)


def step(character: Any, command: str) -> None:
    """The character typed `command`: a new step of the recording, if one is running."""
    data: dict[str, Any] | None = _data(character)
    if data is None or data.get("paused") or not command.strip():
        return
    data["steps"].append([command.strip(), []])
    character.attributes.add(RECORDING, data)


def note(character: Any, text: str) -> None:
    """Something the game recorded during the current step (a clue, an idea, a move)."""
    data: dict[str, Any] | None = _data(character)
    if data is None or data.get("paused") or not data["steps"]:
        return
    notes: list[str] = data["steps"][-1][1]
    if text not in notes:
        notes.append(text)
        character.attributes.add(RECORDING, data)


def save(character: Any) -> tuple[Path, int] | None:
    """Write the scenario file and go on recording. Returns its path and command count."""
    data: dict[str, Any] | None = _data(character)
    if data is None:
        return None
    name: str = str(data["name"])
    steps: list[tuple[str, list[str]]] = [(str(c), [str(n) for n in ns]) for c, ns in data["steps"]]
    base: list[str] = [str(line) for line in data.get("base", [])]
    path: Path = scenario_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scenario_text(name, str(character.key), steps, base), encoding="utf-8")
    return path, len(batch_commands(base)) + len(steps)


def stop(character: Any) -> tuple[Path, int] | None:
    """Write the scenario file and end the recording. Returns its path and command count."""
    saved: tuple[Path, int] | None = save(character)
    if saved is not None:
        character.attributes.remove(RECORDING)
    return saved


def cancel(character: Any) -> bool:
    """End the recording without writing anything. Returns False if none was running."""
    if not is_recording(character):
        return False
    character.attributes.remove(RECORDING)
    return True


def earlier_scenario(name: str) -> tuple[list[str], list[str]] | None:
    """
    An earlier scenario to go on from: its commands after the first `startover yes` (to
    play back) and its text after that line (to start the new file with). None if there
    is no such file, or it doesn't start a new expedition.
    """
    path: Path = scenario_path(name)
    if not path.is_file():
        return None
    lines: list[str] = path.read_text(encoding="utf-8").splitlines()
    if FIRST_COMMAND not in lines:
        return None
    base: list[str] = lines[lines.index(FIRST_COMMAND) + 1 :]
    if base and base[0] == FIRST_NOTE:
        base = base[1:]
    return batch_commands(base), base


def batch_commands(lines: list[str]) -> list[str]:
    """The commands in batch-file lines, as `batchcommand` reads them: a `#` line ends one."""
    commands: list[str] = []
    current: list[str] = []
    for line in [*lines, "#"]:
        if line.startswith("#"):
            if current:
                commands.append("\n".join(current).strip())
            current = []
        elif line.strip():
            current.append(line.rstrip())
    return [command for command in commands if command]


def scenario_text(
    name: str, who: str, steps: list[tuple[str, list[str]]], base: list[str] | None = None
) -> str:
    """
    The batch file for a recording: a header, the earlier scenario's text it went on
    from (if any), then each new command with its notes.
    """
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
        FIRST_NOTE,
        *(base or []),
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
