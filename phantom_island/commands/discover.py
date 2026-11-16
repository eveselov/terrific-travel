"""Commands for discovering things: looking, examining, reading, using, and the journal."""

from typing import Any

from evennia.commands.default.general import CmdGet as DefaultCmdGet
from evennia.commands.default.general import CmdLook as DefaultCmdLook

from typeclasses.rooms import Room
from world.clues import journal_sources_text, journal_text
from world.discovery import act, look_at, notice_surroundings, show_focus_for
from world.notebook import READ_IT, notebook_text, sources_text

from .command import Command


class CmdGet(DefaultCmdGet):
    """
    Pick something up and carry it with you.

    Usage:
      get <thing>
      take <thing>
      pick up <thing>

    Some things can be carried: the sextant up to the Deck, a book or the chart ashore.
    Put them down again with drop. inventory (or i) shows what you carry.

    Examples:
      get sextant
      take chart
    """

    aliases = ["grab", "take", "pick up"]
    help_category = "General"


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
        caller: Any = self.caller
        text: str = self.args.strip()
        if not text:
            super().func()
            location: Any = caller.location
            if isinstance(location, Room):  # back from a thing's card to the room's picture
                location.send_visuals(caller)
            notice_surroundings(caller)
            return
        if look_at(caller, text):  # a thing or a detail of the room
            return
        # Anything else (a character, an exit...): as Evennia's own look does, then the
        # Focus pane follows what was looked at.
        target: Any = caller.search(text)
        if not target:
            return
        self.msg(text=(caller.at_look(target), {"type": "look"}), options=None)
        show_focus_for(caller, target)


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
      journal sources

    The journal starts with the expedition's task. Every clue anyone in the
    expedition finds is written below it. Clues are shown in yellow when you find
    them. journal sources shows who found each clue, where, and from whom or what,
    so you can compare what different sources said.
    """

    key = "journal"
    aliases = ["notes", "clues"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        if self.args.strip().lower() in ("sources", "source", "who"):
            self.caller.msg(journal_sources_text())
        else:
            self.caller.msg(journal_text())


class CmdNotebook(Command):
    """
    Read your notebook: the ideas you've learned about how the world works.

    Usage:
      notebook
      notebook sources

    The journal holds the expedition's clues, shared by everyone. Your notebook is
    your own: how latitude works, why coral grows only under the sea... An entry
    grows as you learn more about it, from people, books, and doing things yourself.
    notebook sources shows who taught you what, and who else knows it.
    """

    key = "notebook"
    aliases = ["knowledge", "ideas"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        self.caller.attributes.add(READ_IT, True)  # no more "Type notebook" hints
        if self.args.strip().lower() in ("sources", "source", "who"):
            self.caller.msg(sources_text(self.caller))
        else:
            self.caller.msg(notebook_text(self.caller))
