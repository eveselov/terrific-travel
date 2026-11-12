"""
Builds the world of Phantom Island from the content files in `world/content/`.

Run in the game as a builder with `batchcode build` (see `world/build.py`). It also runs once by
itself when a new database starts for the first time (`server/conf/at_initial_setup.py`).

Building again after editing the YAML files is safe and is the normal way to work:

- rooms are found by their place id and updated in place, so they keep their dbref and
  everyone in them stays where they are;
- the exits the builder made are deleted and made again from the files;
- Limbo (`settings.DEFAULT_HOME`) is dressed as the title page;
- the ship's `ashore` and `aboard` exits are put where the ship is now;
- inhabitants are found by their character id and updated in place, and put back in their
  place if they aren't in one of their places; characters removed from the file are deleted;
- things are found by their thing id and updated in place, and put back in their place
  unless a player is carrying them; things removed from the file are deleted.
"""

from typing import Any

from django.conf import settings
from evennia.utils import logger
from evennia.utils.create import create_object
from evennia.utils.search import search_object, search_tag

from typeclasses.characters import Character
from typeclasses.exits import Exit
from typeclasses.inhabitants import Inhabitant
from typeclasses.rooms import Deck, Room, ShipRoom
from typeclasses.things import Thing
from world.content import (
    LIMBO_ID,
    CharacterSpec,
    Content,
    ExitName,
    PlaceSpec,
    ThingSpec,
    reload_content,
)
from world.expedition import current_position
from world.maps import MAP_TAG_CATEGORY
from world.places import (
    BUILT_TAG,
    BUILT_TAG_CATEGORY,
    INHABITANT_TAG_CATEGORY,
    PLACE_TAG_CATEGORY,
    SHIP_EXIT_TAG_CATEGORY,
    THING_TAG_CATEGORY,
    all_inhabitants,
    all_things,
    find_inhabitant,
    find_place,
    find_thing,
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


def _place_inhabitant(spec: CharacterSpec, rooms: dict[str, Room]) -> Inhabitant:
    """Make or update one inhabitant, standing in one of its places (the first, if moved)."""
    home: Room = rooms[spec.places[0]]
    found: Any = find_inhabitant(spec.id)
    inhabitant: Inhabitant
    if found is None:
        inhabitant = create_object(Inhabitant, key=spec.name, location=home, home=home)
        inhabitant.tags.add(spec.id, category=INHABITANT_TAG_CATEGORY)
    else:
        inhabitant = found
        if not inhabitant.is_typeclass(Inhabitant, exact=True):
            inhabitant.swap_typeclass(Inhabitant, clean_attributes=False)
    inhabitant.key = spec.name
    inhabitant.aliases.clear()
    inhabitant.aliases.add(list(spec.aliases))
    inhabitant.db.desc = spec.desc
    inhabitant.home = home
    if inhabitant.location not in [rooms[place_id] for place_id in spec.places]:
        inhabitant.move_to(home, quiet=True, move_type="teleport")
    return inhabitant


def place_inhabitants(content: Content, rooms: dict[str, Room]) -> int:
    """Make, update or remove the inhabitants. Returns how many there are."""
    count: int = 0
    for spec in content.characters.values():
        if spec.places:  # the Ship has no object: she is the ship
            _place_inhabitant(spec, rooms)
            count += 1
    for inhabitant in all_inhabitants():
        if inhabitant.character_id not in content.characters:
            inhabitant.delete()
    return count


def _place_thing(spec: ThingSpec, rooms: dict[str, Room]) -> Thing:
    """Make or update one thing. It goes back to its place unless a player is carrying it."""
    home: Room = rooms[spec.where]
    found: Any = find_thing(spec.id)
    thing: Thing
    if found is None:
        thing = create_object(Thing, key=spec.name, location=home, home=home)
        thing.tags.add(spec.id, category=THING_TAG_CATEGORY)
    else:
        thing = found
        if not thing.is_typeclass(Thing, exact=True):
            thing.swap_typeclass(Thing, clean_attributes=False)
    thing.key = spec.name
    thing.aliases.clear()
    thing.aliases.add(list(spec.aliases))
    thing.home = home
    thing.locks.add("get:true()" if spec.portable else "get:false()")
    thing.db.get_err_msg = spec.stays or f"The {spec.name} stays where it is."
    if not isinstance(thing.location, Character) and thing.location != home:
        thing.move_to(home, quiet=True, move_type="teleport")
    return thing


def place_things(content: Content, rooms: dict[str, Room]) -> int:
    """Make, update or remove the things. Returns how many there are."""
    for spec in content.things.values():
        _place_thing(spec, rooms)
    for thing in all_things():
        if not isinstance(thing, Thing) or thing.thing_id not in content.things:
            thing.delete()
    return len(content.things)


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

    inhabitant_count: int = place_inhabitants(content, rooms)
    thing_count: int = place_things(content, rooms)

    _tell(
        caller,
        f"Phantom Island built: {len(rooms)} places, {exit_count} exits, "
        f"{inhabitant_count} inhabitants and {thing_count} things, the ship "
        f"{current_position().name.lower()}.",
    )
    return rooms
