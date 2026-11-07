"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from typing import Any

from evennia.objects.objects import DefaultCharacter

from world.maps import render_no_map_html

from .objects import ObjectParent
from .rooms import Room


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    def show_location_visuals(self) -> None:
        """Update this character's Map pane and show the room picture, if any."""
        location: Any = self.location
        if isinstance(location, Room):
            location.send_visuals(self)
        else:
            self.msg(map=render_no_map_html())

    def at_post_move(self, source_location: Any, move_type: str = "move", **kwargs: Any) -> None:
        """After a move: show the picture first, so the room description follows it."""
        self.show_location_visuals()
        super().at_post_move(source_location, move_type=move_type, **kwargs)

    def at_post_puppet(self, **kwargs: Any) -> None:
        """On entering the game, also fill the Map pane for this location."""
        self.show_location_visuals()
        super().at_post_puppet(**kwargs)
