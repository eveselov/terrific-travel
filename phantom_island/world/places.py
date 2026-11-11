"""
How the built world is found again in the database.

The world builder (`world/builder.py`) tags every room it makes with its place id from the
content files (`office`, `deck`...), and every exit it makes with `BUILT_TAG`. Code finds rooms
by these tags, never by name or dbref, so names can change in the YAML files freely.
"""

from typing import Any

from evennia.utils.search import search_tag

PLACE_TAG_CATEGORY: str = "place"
BUILT_TAG: str = "built"
BUILT_TAG_CATEGORY: str = "phantom_island"
SHIP_EXIT_TAG_CATEGORY: str = "ship_exit"  # tags `ashore` and `aboard`


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
