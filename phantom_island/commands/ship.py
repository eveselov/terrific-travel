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
      sail to <latitude> <longitude>
      sail <direction>
      sail to <place>

    Without an order, shows where the ship is and what you can order here.
    A position is two numbers, each with its side of the world, for example
    sail to 10 north 25 east. The island's position is on the Halcyon's chart,
    in the Cabin. At sea you can also sail by direction (sail west).

    The voyage takes a few moments: the crew sail her, and you watch. The ship
    only leaves when everyone is aboard.
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
