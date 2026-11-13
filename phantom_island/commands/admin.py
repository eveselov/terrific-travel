"""Commands for the developer: starting a new expedition while testing."""

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
