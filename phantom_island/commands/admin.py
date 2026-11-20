"""Commands for the developer: starting a new expedition, recording a scenario."""

from pathlib import Path

from world import recorder
from world.reset import SHORTCUTS, shortcut_position, start_over

from .command import Command

CONFIRM: str = "yes"


class CmdStartOver(Command):
    """
    Start a new expedition (developers only).

    Usage:
      startover [at sea | island]
      startover [at sea | island] yes

    Forgets the journal and the flags, sails the ship back to port (or to the
    charted position, or to the island), puts every thing back in its place and
    sends every player character, online or not, to Limbo. Accounts, characters
    and the built world are kept.

    Without `yes` it only says what it would do. With the ship away, `begin`
    leads to the Deck, as for a late joiner.

    (Not called `reset`: that is Evennia's own command, which reboots the server.)
    """

    key = "startover"
    locks = "cmd:perm(Developer)"
    help_category = "Building"

    def func(self) -> None:
        words: list[str] = self.args.lower().split()
        confirmed: bool = bool(words) and words[-1] == CONFIRM
        where: str = " ".join(words[:-1] if confirmed else words)
        position_id: str | None = shortcut_position(where)
        if position_id is None:
            choices: str = ", ".join(sorted({key for key in SHORTCUTS if key}))
            self.caller.msg(f"Start over where? Leave it out for the port, or one of: {choices}.")
            return
        command: str = " ".join(part for part in ("startover", where, CONFIRM) if part)
        if not confirmed:
            self.caller.msg(
                "This forgets the journal and the flags, puts the ship "
                f"{'in port' if position_id == 'port' else f'at {position_id}'}, puts every "
                "thing back, and sends every player to Limbo.\n"
                f"Type |w{command}|n to go ahead."
            )
            return
        try:
            track: list[str] = start_over(position_id)
        except ValueError as error:
            self.caller.msg(str(error))
            return
        self.caller.msg(f"New expedition started. The ship's track: {' -> '.join(track)}.")


class CmdRecord(Command):
    """
    Record a scenario as you play (developers only).

    Usage:
      record start <name> [from <earlier>] yes
      record checkpoint [<next>]
      record stop
      record cancel
      record

    `record start <name> yes` starts a new expedition (as `startover yes` does:
    everyone goes to Limbo) and records the commands you type from then on. Only
    your own commands are kept, and only those any player could type: building
    and admin commands, and lines the game didn't understand, are left out. `sail`
    is written as `sail/now`.

    With `from <earlier>`, the scenario <earlier> is played first and not recorded
    again: the new file starts with its text, your `Why:` lines included, and
    goes on with what you type.

    `record stop` writes world/scenarios/<name>.ev, with what the game recorded
    after each command (new clues, notebook entries, where you are), ready to play
    back with `batchcommand/interactive scenarios.<name>`. `record checkpoint
    <next>` writes it too, then goes on recording under the name <next>: the next
    file holds everything from the start, and nothing is replayed. `record
    checkpoint` alone writes the file and goes on under the same name. Names may
    be written `scenarios.<name>`. `record cancel` drops the recording (files
    already written stay). `record` alone says whether one is running.

    Without `yes`, `record start` only says what it would do, and whether it would
    replace a scenario file of that name. A checkpoint asks for `yes` only when it
    would replace another file.
    """

    key = "record"
    locks = "cmd:perm(Developer)"
    help_category = "Building"

    def func(self) -> None:
        words: list[str] = self.args.lower().split()
        action: str = words[0] if words else ""
        if action == "start":
            self._start(words[1:])
        elif action == "checkpoint":
            self._checkpoint(words[1:])
        elif action == "stop":
            self._stop()
        elif action == "cancel":
            done: bool = recorder.cancel(self.caller)
            self.caller.msg("Recording dropped." if done else "Nothing is being recorded.")
        else:
            name: str | None = recorder.recording_name(self.caller)
            self.caller.msg(
                f"Recording scenario '{name}'. |wrecord checkpoint <next>|n or "
                "|wrecord stop|n writes it."
                if name
                else "Nothing is being recorded. |wrecord start <name>|n begins."
            )

    def _names(self, words: list[str]) -> list[str] | None:
        """Scenario names as typed (`scenarios.` dropped); None if one isn't a valid name."""
        names: list[str] = [recorder.bare_name(word) for word in words]
        return names if all(recorder.valid_name(name) for name in names) else None

    def _start(self, words: list[str]) -> None:
        confirmed: bool = bool(words) and words[-1] == CONFIRM
        typed: list[str] = words[:-1] if confirmed else words
        if len(typed) == 3 and typed[1] == "from":
            typed = [typed[0], typed[2]]
        names: list[str] | None = self._names(typed)
        if names is None or len(names) not in (1, 2):
            self.caller.msg(
                "Usage: |wrecord start <name> [from <earlier>]|n, with names of small "
                "letters, digits and _."
            )
            return
        name: str = names[0]
        earlier: str | None = names[1] if len(names) == 2 else None
        if recorder.is_recording(self.caller):
            self.caller.msg(
                f"Already recording '{recorder.recording_name(self.caller)}'. "
                "|wrecord checkpoint <next>|n, |wrecord stop|n or |wrecord cancel|n first."
            )
            return
        found: tuple[list[str], list[str]] | None = None
        if earlier is not None:
            found = recorder.earlier_scenario(earlier)
            if found is None:
                self.caller.msg(
                    f"There is no world/scenarios/{earlier}.ev starting with "
                    f"'{recorder.FIRST_COMMAND}' to go on from."
                )
                return
        path: Path = recorder.scenario_path(name)
        if not confirmed:
            replace: str = (
                f" It will replace the existing world/scenarios/{path.name}."
                if path.exists()
                else ""
            )
            plays: str = f", plays scenario '{earlier}'" if earlier else ""
            again: str = f"{name} from {earlier}" if earlier else name
            self.caller.msg(
                "This starts a new expedition (the journal and the flags are forgotten, and "
                f"everyone goes to Limbo){plays}, then records what you type.{replace}\n"
                f"Type |wrecord start {again} yes|n to go ahead."
            )
            return
        start_over("port")
        if found is None:
            recorder.begin(self.caller, name)
            self.caller.msg(
                f"Recording scenario '{name}'. Type |wbegin|n to set out; "
                "|wrecord stop|n when done."
            )
            return
        commands, base = found
        recorder.begin(self.caller, name, base)
        recorder.pause(self.caller, True)
        try:
            for command in commands:
                self.caller.execute_cmd(command)
        finally:
            recorder.pause(self.caller, False)
        self.caller.msg(
            f"Played scenario '{earlier}' ({len(commands)} commands). Recording scenario "
            f"'{name}' from here; |wrecord stop|n when done."
        )

    def _checkpoint(self, words: list[str]) -> None:
        confirmed: bool = bool(words) and words[-1] == CONFIRM
        names: list[str] | None = self._names(words[:-1] if confirmed else words)
        if names is None or len(names) > 1:
            self.caller.msg(
                "Usage: |wrecord checkpoint [<next>]|n, with a name of small letters, digits and _."
            )
            return
        current: str | None = recorder.recording_name(self.caller)
        if current is None:
            self.caller.msg("Nothing is being recorded. |wrecord start <name>|n begins.")
            return
        following: str = names[0] if names else current
        path: Path = recorder.scenario_path(following)
        if following != current and path.exists() and not confirmed:
            self.caller.msg(
                f"Going on as '{following}' will replace the existing "
                f"world/scenarios/{path.name} when it is written.\n"
                f"Type |wrecord checkpoint {following} yes|n to go ahead."
            )
            return
        saved: tuple[Path, int] | None = recorder.save(self.caller)
        if saved is None:
            return
        recorder.rename(self.caller, following)
        written, count = saved
        self.caller.msg(
            f"Saved world/scenarios/{written.name}: {count} commands. Still "
            f"recording, now as '{following}'."
        )

    def _stop(self) -> None:
        saved: tuple[Path, int] | None = recorder.stop(self.caller)
        if saved is None:
            self.caller.msg("Nothing is being recorded.")
            return
        path, count = saved
        self.caller.msg(
            f"Saved world/scenarios/{path.name}: {count} commands. Play it back with "
            f"|wbatchcommand/interactive scenarios.{path.stem}|n."
        )
