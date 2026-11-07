"""
Room

Rooms are simple containers that has no location of their own.

"""

from typing import TYPE_CHECKING, Any

from evennia.objects.objects import DefaultRoom

from world.maps import (
    MAP_TAG_CATEGORY,
    PictureMap,
    get_map,
    places_on_map,
    render_map_html,
    render_no_map_html,
)

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

    Web client visuals (all optional, set by builders):

    - tag `<map key>` in category `map`: the room is a place on that picture map;
    - attribute `map_pos`: the room's (x, y) position on the map picture;
    - attribute `image`: URL of a picture shown when a character arrives here.
    """

    @property
    def picture_map(self) -> PictureMap | None:
        """The first picture map this room is on, or None."""
        keys: list[str] = self.tags.get(category=MAP_TAG_CATEGORY, return_list=True)
        for key in keys:
            picture_map: PictureMap | None = get_map(key)
            if picture_map is not None:
                return picture_map
        return None

    @property
    def image_url(self) -> str | None:
        """URL of this room's picture, or None if it has none."""
        url: Any = self.attributes.get("image")
        return str(url) if url else None

    def send_visuals(self, viewer: "Character") -> None:
        """
        Send this room's map and picture to a viewer's web client.

        Text-only clients ignore these messages, so this is safe to call for any viewer.
        """
        picture_map: PictureMap | None = self.picture_map
        if picture_map is None:
            viewer.msg(map=render_no_map_html())
        else:
            viewer.msg(map=render_map_html(picture_map, places_on_map(picture_map, self)))
        url: str | None = self.image_url
        if url is not None:
            viewer.msg(room_image=((url,), {"alt": self.key}))
