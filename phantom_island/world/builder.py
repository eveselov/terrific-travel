"""
Builds the world of Phantom Island from the content files in `world/content/`.

Run in the game as a builder with `batchcode build` (see `world/build.py`). It also runs once by
itself when a new database starts for the first time (`server/conf/at_initial_setup.py`).

Building again after editing the YAML files is safe and is the normal way to work:

- rooms are found by their place id and updated in place, so they keep their dbref and
  everyone in them stays where they are;
- the exits the builder made are deleted and made again from the files;
- Limbo (`settings.DEFAULT_HOME`) is dressed as the title page;
- the ship's `ashore` and `aboard` exits are put where the ship is now.
"""

from typing import Any

from django.conf import settings
from evennia.utils import logger
from evennia.utils.create import create_object
from evennia.utils.search import search_object, search_tag

from typeclasses.exits import Exit
from typeclasses.rooms import Deck, Room, ShipRoom
from world.content import LIMBO_ID, Content, ExitName, PlaceSpec, reload_content
from world.expedition import current_position
from world.maps import MAP_TAG_CATEGORY
from world.places import (
    BUILT_TAG,
    BUILT_TAG_CATEGORY,
    PLACE_TAG_CATEGORY,
    SHIP_EXIT_TAG_CATEGORY,
    find_place,
)
from world.ship import ABOARD, ASHORE, moor_ship

ROOM_CLASSES: dict[str, type[Room]] = {"room": Room, "deck": Deck, "cabin": ShipRoom}


def _tell(caller: Any | None, message: str) -> None:
    if caller is not None:
        caller.msg(message)
    else:
        logger.log_info(f"Phantom Island builder: {message}")


def default_home() -> Room | None:
    """Limbo, the room new characters start in."""
    found: list[Any] = list(search_object(settings.DEFAULT_HOME))
    return found[0] if found else None


def _room_for(spec: PlaceSpec) -> Room:
    """The existing room for a place, with the right typeclass, or a new one."""
    room_class: type[Room] = ROOM_CLASSES[spec.kind]
    room: Any = find_place(spec.id)
    if room is None:
        created: Room = create_object(room_class, key=spec.name)
        return created
    if not room.is_typeclass(room_class, exact=True):
        room.swap_typeclass(room_class, clean_attributes=False)
    return room  # type: ignore[no-any-return]


def _dress(room: Any, spec: PlaceSpec) -> None:
    """Give a room its name, description, place tag, map position and picture."""
    room.key = spec.name
    room.db.desc = spec.desc
    room.tags.add(spec.id, category=PLACE_TAG_CATEGORY)
    room.tags.clear(category=MAP_TAG_CATEGORY)
    if spec.map is not None:
        room.tags.add(spec.map, category=MAP_TAG_CATEGORY)
        room.db.map_pos = spec.map_pos
    else:
        room.attributes.remove("map_pos")
    if spec.image is not None:
        room.db.image = spec.image
    else:
        room.attributes.remove("image")


def _make_exit(key: str, aliases: tuple[str, ...], location: Any, destination: Any) -> Any:
    exit_obj: Any = create_object(
        Exit, key=key, aliases=list(aliases), location=location, destination=destination
    )
    exit_obj.tags.add(BUILT_TAG, category=BUILT_TAG_CATEGORY)
    return exit_obj


def _make_ship_exit(name: ExitName, tag: str, location: Any, destination: Any) -> None:
    exit_obj: Any = _make_exit(name.key, name.aliases, location, destination)
    exit_obj.tags.add(tag, category=SHIP_EXIT_TAG_CATEGORY)


def remove_built_exits() -> int:
    """Delete every exit the builder made. Returns how many."""
    exits: list[Any] = list(search_tag(BUILT_TAG, category=BUILT_TAG_CATEGORY))
    for exit_obj in exits:
        exit_obj.delete()
    return len(exits)


def build_world(caller: Any | None = None, limbo: Room | None = None) -> dict[str, Room]:
    """
    Build (or rebuild) every place and exit from the content files.

    `limbo` is the room to dress as the title page; by default `settings.DEFAULT_HOME`.
    Returns the rooms by place id.
    """
    content: Content = reload_content()
    if limbo is None:
        limbo = default_home()
    if limbo is None:
        _tell(caller, f"Can't find Limbo ({settings.DEFAULT_HOME}); nothing was built.")
        return {}

    rooms: dict[str, Room] = {}
    for spec in content.places.values():
        room: Room = limbo if spec.id == LIMBO_ID else _room_for(spec)
        _dress(room, spec)
        rooms[spec.id] = room

    remove_built_exits()
    exit_count: int = 0
    for spec in content.places.values():
        for exit_spec in spec.exits:
            _make_exit(exit_spec.key, exit_spec.aliases, rooms[spec.id], rooms[exit_spec.to])
            exit_count += 1

    # The ship's exits are made on the Deck and then moved to where the ship is.
    deck: Room = rooms[content.place_of_kind("deck").id]
    _make_ship_exit(content.ashore_exit, ASHORE, deck, deck)
    _make_ship_exit(content.aboard_exit, ABOARD, deck, deck)
    moor_ship(current_position())

    _tell(
        caller,
        f"Phantom Island built: {len(rooms)} places and {exit_count} exits, "
        f"the ship {current_position().name.lower()}.",
    )
    return rooms
