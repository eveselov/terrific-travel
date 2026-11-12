"""
How the built world is found again in the database.

The world builder (`world/builder.py`) tags every room it makes with its place id from the
content files (`office`, `deck`...), every exit it makes with `BUILT_TAG`, every inhabitant
with its character id (`barnaby`...) and every thing with its thing id (`sextant`...). Code
finds them by these tags, never by name or dbref, so names can change in the YAML files
freely.
"""

from typing import Any

from evennia.utils.search import search_tag

PLACE_TAG_CATEGORY: str = "place"
BUILT_TAG: str = "built"
BUILT_TAG_CATEGORY: str = "phantom_island"
SHIP_EXIT_TAG_CATEGORY: str = "ship_exit"  # tags `ashore` and `aboard`
INHABITANT_TAG_CATEGORY: str = "inhabitant"  # tags each inhabitant with its character id
THING_TAG_CATEGORY: str = "thing"  # tags each thing with its thing id


def find_place(place_id: str) -> Any | None:
    """The room built for this place id, or None if it hasn't been built."""
    found: list[Any] = list(search_tag(place_id, category=PLACE_TAG_CATEGORY))
    return found[0] if found else None


def find_ship_exit(name: str) -> Any | None:
    """The ship's `ashore` or `aboard` exit, or None if it hasn't been built."""
    found: list[Any] = list(search_tag(name, category=SHIP_EXIT_TAG_CATEGORY))
    return found[0] if found else None


def place_id_of(obj: Any) -> str | None:
    """The place id a room was built for, or None for rooms the builder didn't make."""
    ids: list[str] = obj.tags.get(category=PLACE_TAG_CATEGORY, return_list=True)
    return ids[0] if ids else None


def find_inhabitant(character_id: str) -> Any | None:
    """The inhabitant built for this character id, or None if it hasn't been built."""
    found: list[Any] = list(search_tag(character_id, category=INHABITANT_TAG_CATEGORY))
    return found[0] if found else None


def all_inhabitants() -> list[Any]:
    """Every inhabitant the builder made."""
    return list(search_tag(category=INHABITANT_TAG_CATEGORY))


def find_thing(thing_id: str) -> Any | None:
    """The object built for this thing id, or None if it hasn't been built."""
    found: list[Any] = list(search_tag(thing_id, category=THING_TAG_CATEGORY))
    return found[0] if found else None


def all_things() -> list[Any]:
    """Every thing the builder made."""
    return list(search_tag(category=THING_TAG_CATEGORY))
