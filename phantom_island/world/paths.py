"""
Paths are learned (DECISIONS.md, 40): a place with `hidden_until` (places.yaml) doesn't exist
for players until its clues or flags hold. Until then the exits that lead to it are neither
shown nor usable (`typeclasses.exits.Exit.access`), and the map leaves it out. A path is
opened by the story: a view from the Hilltop, a child leading the way, an elder telling where
someone lives. That moment is announced to everyone in the expedition in a quiet line, with
where the new path starts, and from then on the place is there for everyone: what is known
is the expedition's, like the journal.

Nothing is stored: whether a place is known follows from the flags and the journal, so
starting over hides the paths again.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from world import notices
from world.content import Content, PlaceSpec, load_content
from world.expedition import connected_characters, get_expedition

NO_PATH: str = "There's no path that way that you know of."


def hidden_places() -> set[str]:
    """The ids of the places players don't know the way to yet."""
    expedition: Any = get_expedition()
    return {
        place.id
        for place in load_content().places.values()
        if place.hidden_until and not expedition.met(place.hidden_until)
    }


def is_known(place_id: str) -> bool:
    """Whether players know the way to this place (most places: always)."""
    place: PlaceSpec | None = load_content().places.get(place_id)
    if place is None or not place.hidden_until:
        return True
    return bool(get_expedition().met(place.hidden_until))


def _way_in(content: Content, place_id: str, hidden: set[str]) -> str:
    """Where the new path starts: `west of the Village`, from a place already known."""
    for other in content.places.values():
        if other.id in hidden or other.id == place_id:
            continue
        for exit_spec in other.exits:
            if exit_spec.to == place_id:
                return f", {exit_spec.key} of the {other.name}"
    return ""


def announce(before: set[str]) -> None:
    """Tell everyone in the expedition about the paths that opened since `before`."""
    hidden: set[str] = hidden_places()
    opened: list[str] = [place_id for place_id in sorted(before) if place_id not in hidden]
    if not opened:
        return
    content: Content = load_content()
    for place_id in opened:
        line: str = notices.quiet(
            f"A new path: the {content.places[place_id].name}{_way_in(content, place_id, hidden)}."
        )
        for character in connected_characters():
            notices.tell(character, line)


@contextmanager
def watching() -> Iterator[None]:
    """Announce any path that opens while the body runs (a flag set, a clue found)."""
    before: set[str] = hidden_places()
    yield
    announce(before)
