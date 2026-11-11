"""
Commands that only work on the ship's Deck. The Deck room carries `DeckCmdSet` (added in
`typeclasses.rooms.Deck.at_object_creation`), so these commands exist for whoever is on deck.
"""

from evennia import CmdSet

from world.ship import sail

from .command import Command


class CmdSail(Command):
    """
    Sail the ship.

    Usage:
      sail
      sail <direction>

    Without a direction, shows where the ship is and which ways she can sail.
    The ship only leaves when everyone is aboard.
    """

    key = "sail"
    locks = "cmd:all()"
    help_category = "Ship"

    def func(self) -> None:
        sail(self.caller, self.args.strip())


class DeckCmdSet(CmdSet):
    """Commands available on the Deck."""

    key = "DeckCmdSet"

    def at_cmdset_creation(self) -> None:
        self.add(CmdSail())
