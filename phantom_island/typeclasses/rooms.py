"""
Room

Rooms are simple containers that has no location of their own.

Phantom Island has three room typeclasses:

- `Room`: Limbo and every place in the port and on the island;
- `ShipRoom`: the ship's Cabin. What it shows depends on where the ship is;
- `Deck`: the ship's Deck, a `ShipRoom` that also carries the `sail` command.

The rooms are built from the content files by `world/builder.py`, not by hand.
"""

from typing import TYPE_CHECKING, Any

from evennia.objects.objects import DefaultRoom

from world.content import PositionSpec, load_content
from world.expedition import current_position
from world.focus import render_focus_html
from world.maps import (
    MapLocation,
    MapView,
    build_map_view,
    render_map_html,
    render_no_map_html,
    room_map_location,
    ship_map_location,
    text_map,
)
from world.places import place_id_of

from .objects import ObjectParent

if TYPE_CHECKING:
    from .characters import Character


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.

    Set by the world builder from the content files:

    - tag `<place id>` in category `place`: which place this room is;
    - tag `<map key>` in category `map` and attribute `map_pos`: where it is on a map;
    - attribute `image`: URL of its picture for the Focus pane (optional).
    """

    ship_kind: str | None = None  # "deck" or "cabin" for the ship's rooms

    @property
    def place_id(self) -> str | None:
        """The place id from the content files, or None for rooms built by hand."""
        return place_id_of(self)

    @property
    def image_url(self) -> str | None:
        """URL of this room's picture, or None if it has none."""
        url: Any = self.attributes.get("image")
        return str(url) if url else None

    def map_location(self) -> MapLocation | None:
        """Which map this room is on, and where."""
        return room_map_location(self)

    def map_view(self) -> MapView | None:
        """The map seen from this room, or None if it is on no map."""
        location: MapLocation | None = self.map_location()
        if location is None:
            return None
        return build_map_view(self, location, ship_kind=self.ship_kind)

    def map_text(self) -> str:
        """The map seen from this room, in words."""
        return text_map(self.map_view())

    def situation_text(self) -> str:
        """Extra description that depends on where the ship is: here, if she is moored here."""
        place_id: str | None = self.place_id
        if place_id is None:
            return ""
        position: PositionSpec = current_position()
        return position.shore if position.ashore == place_id else ""

    def get_display_desc(self, looker: Any, **kwargs: Any) -> str:
        """
        The description, followed by what depends on the ship's position.

        Paragraphs are separated with Evennia's `|/` line break: `format_appearance` squeezes
        blank lines out of the text, but `|/` only becomes a line break after that.
        """
        desc: str = super().get_display_desc(looker, **kwargs)
        extra: str = self.situation_text()
        text: str = f"{desc}\n\n{extra}" if extra else desc
        return text.replace("\n\n", "\n|/")

    def send_visuals(self, viewer: "Character") -> None:
        """
        Send this room's map and picture to a viewer's web client.

        Text-only clients ignore these messages, so this is safe to call for any viewer.
        """
        view: MapView | None = self.map_view()
        viewer.msg(map=render_map_html(view) if view is not None else render_no_map_html())
        viewer.msg(focus=render_focus_html(self.key, self.image_url))


class ShipRoom(Room):
    """
    One of the ship's rooms. The rooms themselves never move: what is seen from them, and
    which map they show, follow the ship's position (`world/content/ship.yaml`).
    """

    ship_kind = "cabin"

    def position_text(self, position: PositionSpec) -> str:
        """What is noticed in this room at a position."""
        return position.cabin

    def map_location(self) -> MapLocation | None:
        """The ship's rooms are wherever the ship is."""
        return ship_map_location(current_position(), load_content())

    def situation_text(self) -> str:
        return self.position_text(current_position())


class Deck(ShipRoom):
    """The ship's Deck: the view of sea and sky, and where `sail` works."""

    ship_kind = "deck"

    def at_object_creation(self) -> None:
        """Give the Deck its `sail` command (a cmdset on the room, for those in it)."""
        super().at_object_creation()
        self.cmdset.add("commands.ship.DeckCmdSet", persistent=True)

    def position_text(self, position: PositionSpec) -> str:
        return position.deck
