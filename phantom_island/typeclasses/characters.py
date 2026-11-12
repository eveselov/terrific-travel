"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from typing import Any

from evennia.objects.objects import DefaultCharacter

from world.discovery import notice_surroundings, return_things_home
from world.focus import render_focus_html
from world.maps import render_no_map_html

from .objects import ObjectParent
from .rooms import Room


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    Each move and each login also updates the web client's Map and Focus panes.
    """

    def show_location_visuals(self) -> None:
        """Update this character's Map and Focus panes for where they are."""
        location: Any = self.location
        if isinstance(location, Room):
            location.send_visuals(self)
        else:
            self.msg(map=render_no_map_html())
            self.msg(focus=render_focus_html("Nowhere", None))

    def at_post_move(self, source_location: Any, move_type: str = "move", **kwargs: Any) -> None:
        """
        After a move: update the panes, show the room description as usual, then note any
        clue the view reveals (the empty sea seen from the Deck).
        """
        self.show_location_visuals()
        super().at_post_move(source_location, move_type=move_type, **kwargs)
        notice_surroundings(self)

    def at_post_puppet(self, **kwargs: Any) -> None:
        """On entering the game, also fill the Map and Focus panes for this location."""
        self.show_location_visuals()
        super().at_post_puppet(**kwargs)

    def at_post_unpuppet(self, account: Any = None, session: Any = None, **kwargs: Any) -> None:
        """
        On leaving the game, put back the things this character carries, so the others can
        still find the books and the chart (DECISIONS.md, 6b: no dead ends).
        """
        super().at_post_unpuppet(account=account, session=session, **kwargs)
        if not self.sessions.count():
            return_things_home(self)
