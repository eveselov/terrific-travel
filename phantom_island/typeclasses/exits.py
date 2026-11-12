"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from typing import Any

from evennia.objects.objects import DefaultExit

from world.content import LIMBO_ID
from world.places import place_id_of

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exits.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects child classes like this.

    The exit out of Limbo (`begin`) leads to wherever the expedition is: the Society Office
    while the ship is in port, her Deck while she's away (DECISIONS.md, 18).
    """

    def at_traverse(self, traversing_object: Any, target_location: Any, **kwargs: Any) -> None:
        location: Any = self.location
        if location is not None and place_id_of(location) == LIMBO_ID:
            from world.ship import begin_destination

            line: str | None
            target_location, line = begin_destination(target_location)
            if line is not None:
                traversing_object.msg(line)
        super().at_traverse(traversing_object, target_location, **kwargs)
