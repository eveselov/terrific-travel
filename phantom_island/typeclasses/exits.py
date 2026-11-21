"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from typing import Any

from evennia.objects.objects import DefaultExit

from world.content import LIMBO_ID
from world.paths import NO_PATH, is_known
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

    def leads_to_hidden_place(self) -> bool:
        """Whether this exit leads to a place players don't know the way to yet (40)."""
        destination: Any = self.destination
        place_id: str | None = place_id_of(destination) if destination is not None else None
        return place_id is not None and not is_known(place_id)

    def access(
        self,
        accessing_obj: Any,
        access_type: str = "read",
        default: bool = False,
        no_superuser_bypass: bool = False,
        **kwargs: Any,
    ) -> bool:
        """
        Paths are learned (DECISIONS.md, 40): an exit to a hidden place is neither seen nor
        used, by anyone, until the story opens it.
        """
        if access_type in ("view", "search", "traverse") and self.leads_to_hidden_place():
            return False
        return bool(
            super().access(
                accessing_obj,
                access_type=access_type,
                default=default,
                no_superuser_bypass=no_superuser_bypass,
                **kwargs,
            )
        )

    def at_failed_traverse(self, traversing_object: Any, **kwargs: Any) -> None:
        if self.leads_to_hidden_place():
            traversing_object.msg(NO_PATH)
            return
        super().at_failed_traverse(traversing_object, **kwargs)

    def at_traverse(self, traversing_object: Any, target_location: Any, **kwargs: Any) -> None:
        location: Any = self.location
        if location is not None and place_id_of(location) == LIMBO_ID:
            from world.ship import begin_destination

            line: str | None
            target_location, line = begin_destination(target_location)
            if line is not None:
                traversing_object.msg(line)
        super().at_traverse(traversing_object, target_location, **kwargs)
