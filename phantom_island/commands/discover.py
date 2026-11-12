"""Commands for discovering things: looking, examining, reading, using, and the journal."""

from evennia.commands.default.general import CmdLook as DefaultCmdLook

from world.clues import journal_text
from world.discovery import act, look_at, notice_surroundings

from .command import Command


class CmdLook(DefaultCmdLook):
    """
    Look around, or at something.

    Usage:
      look
      look <something>

    Words shown in white in a description are worth a look, or a question. Some things show
    more to someone carrying the right book or chart.

    Examples:
      look
      look compass
      look beams
    """

    help_category = "General"

    def func(self) -> None:
        if self.args.strip() and look_at(self.caller, self.args.strip()):
            return
        super().func()
        if not self.args.strip():
            notice_surroundings(self.caller)


class CmdExamine(Command):
    """
    Take a closer look at something.

    Usage:
      examine <something>
      x <something>

    Like look, but closer: sometimes you notice more.

    Example:
      examine compass
    """

    key = "examine"
    aliases = ["x"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        target: str = self.args.strip()
        if not target:
            self.caller.msg("What do you want to examine? (For example: |wexamine compass|n)")
            return
        if not look_at(self.caller, target, close=True):
            self.caller.msg(f"You don't see any '{target}' here.")


class CmdRead(Command):
    """
    Read something: a book, a chart, an instrument's scale.

    Usage:
      read <something>

    Everyone in the room hears what you read out.

    Examples:
      read plant guide
      read chronometer
    """

    key = "read"
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        act(self.caller, "read", self.args)


class CmdUse(Command):
    """
    Use something, such as an instrument.

    Usage:
      use <something>

    Everyone in the room sees what happens.

    Example:
      use sextant
    """

    key = "use"
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        act(self.caller, "use", self.args)


class CmdJournal(Command):
    """
    Read the expedition's journal.

    Usage:
      journal

    Every clue anyone in the expedition finds is written here, with who found it and
    where. Clues are shown in yellow when you find them.
    """

    key = "journal"
    aliases = ["notes", "clues"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        self.caller.msg(journal_text())
