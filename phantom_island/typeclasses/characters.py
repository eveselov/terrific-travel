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

# The web client class for text caused by another player's command: styled in panes.css as
# a quieter "their turn" block between the player's own echoed commands.
OTHER_TURN_CLS: str = "pi-other"
# Added to the first message of each new turn (each line another player types), where the
# web client draws the divider.
TURN_START_CLS: str = "pi-turn"


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    Each move and each login also updates the web client's Map and Focus panes.
    """

    def msg(
        self,
        text: Any = None,
        from_obj: Any = None,
        session: Any = None,
        options: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Send a message to this character. Text caused by another player (their `from_obj`
        is another Character: what they say, ask, read or do, their moves) is tagged with
        the `pi-other` class, so the web client shows it as their turn; the first message of
        each of their turns (each line they type, counted in server/conf/inputfuncs.py) also
        gets `pi-turn`, where the divider goes. Telnet ignores both.
        """
        sender: Any = self._other_player(from_obj)
        if text is not None and sender is not None:
            body: Any = text
            extra: dict[str, Any] = {}
            if isinstance(text, tuple):
                body = text[0]
                if len(text) > 1 and isinstance(text[1], dict):
                    extra = dict(text[1])
            turn: tuple[int, int] = (int(sender.id), int(sender.ndb.turn or 0))
            cls: str = OTHER_TURN_CLS
            if self.ndb.last_other_turn != turn:
                self.ndb.last_other_turn = turn
                cls = f"{OTHER_TURN_CLS} {TURN_START_CLS}"
            extra.setdefault("cls", cls)
            text = (body, extra)
        super().msg(text=text, from_obj=from_obj, session=session, options=options, **kwargs)

    def _other_player(self, from_obj: Any) -> "Character | None":
        """The other player character among the senders, if any."""
        senders: list[Any] = list(from_obj) if isinstance(from_obj, (list, tuple)) else [from_obj]
        for sender in senders:
            if isinstance(sender, Character) and sender != self:
                return sender
        return None

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
