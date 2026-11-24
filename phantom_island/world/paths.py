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
from world.places import place_id_of

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


def _distances(content: Content, start: str | None, hidden: set[str]) -> dict[str, int]:
    """How many steps each known place is from `start`, walking known paths only."""
    if start is None or start not in content.places:
        return {}
    steps: dict[str, int] = {start: 0}
    frontier: list[str] = [start]
    while frontier:
        following: list[str] = []
        for place_id in frontier:
            for exit_spec in content.places[place_id].exits:
                if exit_spec.to in hidden or exit_spec.to in steps:
                    continue
                if exit_spec.to in content.places:
                    steps[exit_spec.to] = steps[place_id] + 1
                    following.append(exit_spec.to)
        frontier = following
    return steps


def _way_in(content: Content, place_id: str, hidden: set[str], start: str | None = None) -> str:
    """
    Where the new path starts: `, south of the Forest Path`, from the known place nearest to
    `start` (where the listener stands), or the first one in the content when none is near.
    """
    ways: list[tuple[str, str]] = [
        (other.id, f", {exit_spec.key} of the {other.name}")
        for other in content.places.values()
        if other.id not in hidden and other.id != place_id
        for exit_spec in other.exits
        if exit_spec.to == place_id
    ]
    if not ways:
        return ""
    steps: dict[str, int] = _distances(content, start, hidden)
    nearest: tuple[str, str] = min(ways, key=lambda way: steps.get(way[0], len(content.places)))
    return nearest[1]


def announce(before: set[str]) -> None:
    """Tell everyone in the expedition about the paths that opened since `before`."""
    hidden: set[str] = hidden_places()
    opened: list[str] = [place_id for place_id in sorted(before) if place_id not in hidden]
    if not opened:
        return
    content: Content = load_content()
    for character in connected_characters():
        start: str | None = place_id_of(character.location) if character.location else None
        for place_id in opened:
            way: str = _way_in(content, place_id, hidden, start)
            notices.tell(character, f"A new path: the {content.places[place_id].name}{way}.")


@contextmanager
def watching() -> Iterator[None]:
    """Announce any path that opens while the body runs (a flag set, a clue found)."""
    before: set[str] = hidden_places()
    yield
    announce(before)
