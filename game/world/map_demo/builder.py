"""Builds and removes the map demo rooms (see the package docstring for how to run it)."""

from dataclasses import dataclass
from typing import Any

from evennia.utils.create import create_object
from evennia.utils.search import search_tag

from typeclasses.exits import Exit
from typeclasses.rooms import Room
from world.maps import MAP_TAG_CATEGORY
from world.picture_maps.demo_sea import DEMO_SEA

DEMO_TAG: str = "map_demo"
DEMO_TAG_CATEGORY: str = "demo"


@dataclass(frozen=True)
class DemoRoom:
    key: str
    desc: str
    map_pos: tuple[int, int]
    image: str


@dataclass(frozen=True)
class DemoExit:
    key: str
    aliases: list[str]
    source: str
    destination: str


DEMO_ROOMS: list[DemoRoom] = [
    DemoRoom(
        key="Harbour",
        desc="A placeholder harbour for the map demo. Small boats bob beside a wooden pier.",
        map_pos=(290, 365),
        image="/static/terrific_travel/map_demo/harbour.svg",
    ),
    DemoRoom(
        key="Lighthouse",
        desc="A placeholder lighthouse for the map demo. Its lamp turns slowly overhead.",
        map_pos=(640, 165),
        image="/static/terrific_travel/map_demo/lighthouse.svg",
    ),
    DemoRoom(
        key="Cove",
        desc="A placeholder cove for the map demo. Waves wash over a quiet, sandy beach.",
        map_pos=(790, 430),
        image="/static/terrific_travel/map_demo/cove.svg",
    ),
]

DEMO_EXITS: list[DemoExit] = [
    DemoExit("north", ["n"], source="Harbour", destination="Lighthouse"),
    DemoExit("south", ["s"], source="Lighthouse", destination="Harbour"),
    DemoExit("east", ["e"], source="Harbour", destination="Cove"),
    DemoExit("west", ["w"], source="Cove", destination="Harbour"),
    DemoExit("northwest", ["nw"], source="Cove", destination="Lighthouse"),
    DemoExit("southeast", ["se"], source="Lighthouse", destination="Cove"),
]

ENTRANCE_KEY: str = "harbour"
EXIT_BACK_KEY: str = "back"


def _tag_as_demo(obj: Any) -> None:
    obj.tags.add(DEMO_TAG, category=DEMO_TAG_CATEGORY)


def demo_objects() -> list[Any]:
    """All objects the demo created (rooms and exits)."""
    return list(search_tag(DEMO_TAG, category=DEMO_TAG_CATEGORY))


def build_map_demo(caller: Any) -> list[Room]:
    """Create the demo rooms and exits, with an entrance from the caller's location."""
    if demo_objects():
        caller.msg("The map demo is already built. Remove it first: batchcode map_demo.remove")
        return []

    rooms: dict[str, Room] = {}
    for spec in DEMO_ROOMS:
        room: Room = create_object(Room, key=spec.key)
        room.db.desc = spec.desc
        room.db.map_pos = spec.map_pos
        room.db.image = spec.image
        room.tags.add(DEMO_SEA.key, category=MAP_TAG_CATEGORY)
        _tag_as_demo(room)
        rooms[spec.key] = room

    for exit_spec in DEMO_EXITS:
        _tag_as_demo(
            create_object(
                Exit,
                key=exit_spec.key,
                aliases=exit_spec.aliases,
                location=rooms[exit_spec.source],
                destination=rooms[exit_spec.destination],
            )
        )

    origin: Any = caller.location
    harbour: Room = rooms["Harbour"]
    if origin is not None:
        _tag_as_demo(create_object(Exit, key=ENTRANCE_KEY, location=origin, destination=harbour))
        _tag_as_demo(create_object(Exit, key=EXIT_BACK_KEY, location=harbour, destination=origin))
        caller.msg(f"Map demo built. Type |w{ENTRANCE_KEY}|n to go there.")
    else:
        caller.msg(f"Map demo built, but with no entrance. Use: teleport {harbour.dbref}")
    return list(rooms.values())


def remove_map_demo(caller: Any) -> int:
    """Delete everything the demo created. Characters inside are moved to their home."""
    objects: list[Any] = demo_objects()
    # Exits first, so no room is left with a dangling exit while rooms are deleted.
    objects.sort(key=lambda obj: 0 if obj.destination else 1)
    for obj in objects:
        obj.delete()
    caller.msg(f"Map demo removed ({len(objects)} objects deleted).")
    return len(objects)
