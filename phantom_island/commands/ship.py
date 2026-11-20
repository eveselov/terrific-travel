"""
Commands that only work on the ship's Deck. The Deck room carries `DeckCmdSet` (added in
`typeclasses.rooms.Deck.at_object_creation`), so these commands exist for whoever is on deck.
"""

from evennia import CmdSet

from world.ship import sail

from .command import Command

# `sail/now ...`: the whole voyage at once, for builders playing a scenario
# (`batchcommand scenarios.island`). Players who type it sail as usual.
NOW_SWITCH: str = "/now"


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
    in the chart house. At sea you can also sail by direction (sail west).

    The voyage takes a few moments: the crew sail her, and you watch. The ship
    only leaves when everyone is aboard.
    """

    key = "sail"
    locks = "cmd:all()"
    help_category = "Ship"

    def recorded_as(self) -> str:
        """In a recorded scenario, a voyage happens at once (`sail/now`)."""
        text: str = self.args.strip()
        if not text or text.split()[0].lower() == NOW_SWITCH:
            return super().recorded_as()
        return f"sail{NOW_SWITCH} {text}"

    def func(self) -> None:
        text: str = self.args.strip()
        now: bool = False
        first, _, rest = text.partition(" ")
        if first.lower() == NOW_SWITCH:  # `sail/now to ...`: builders, for scenarios
            text = rest.strip()
            now = bool(self.caller.check_permstring("Builder"))
        sail(self.caller, text, now)


class DeckCmdSet(CmdSet):
    """Commands available on the Deck."""

    key = "DeckCmdSet"

    def at_cmdset_creation(self) -> None:
        self.add(CmdSail())
