"""
The players' ship: sailing between positions, and the exits between ship and shore.

The ship is two rooms (Deck and Cabin) that never move. Sailing changes the ship's position
in the expedition state, and moves two exits: `ashore` on the Deck and `aboard` on the shore.
At sea both are put nowhere (location None), so they disappear until the ship moors again.
"""

from typing import Any

from typeclasses.rooms import Room, ShipRoom
from world.clues import discover
from world.content import (
    DIRECTION_ALIASES,
    LIMBO_ID,
    Content,
    PositionSpec,
    RouteSpec,
    load_content,
)
from world.expedition import connected_characters, current_position, get_expedition
from world.places import find_place, find_ship_exit

ASHORE: str = "ashore"
ABOARD: str = "aboard"

SHORE_DEPARTURE: str = "Your ship sets sail and slowly heads out to sea."
SHORE_ARRIVAL: str = "A ship sails in and drops anchor nearby."

# n -> north, etc., so `sail w` works like `sail west`.
_DIRECTIONS: dict[str, str] = {short: full for full, short in DIRECTION_ALIASES.items()}


def ship_rooms() -> list[ShipRoom]:
    """The ship's built rooms (the Deck first), skipping any that haven't been built."""
    content: Content = load_content()
    rooms: list[ShipRoom] = []
    for kind in ("deck", "cabin"):
        room: Any = find_place(content.place_of_kind(kind).id)
        if isinstance(room, ShipRoom):
            rooms.append(room)
    return rooms


def moor_ship(position: PositionSpec) -> None:
    """Put the `ashore` and `aboard` exits where this position needs them (or nowhere)."""
    deck: Any = find_place(load_content().place_of_kind("deck").id)
    ashore_exit: Any = find_ship_exit(ASHORE)
    aboard_exit: Any = find_ship_exit(ABOARD)
    if deck is None or ashore_exit is None or aboard_exit is None:
        return
    shore: Any = find_place(position.ashore) if position.ashore else None
    if shore is None:
        ashore_exit.location = None
        aboard_exit.location = None
        return
    ashore_exit.location = deck
    ashore_exit.destination = shore
    aboard_exit.location = shore
    aboard_exit.destination = deck


def crew_ashore() -> list[Any]:
    """
    Connected players who are not aboard, so the ship mustn't leave without them.

    Players still in Limbo (the title page) haven't joined the expedition yet, so they
    don't count.
    """
    ashore: list[Any] = []
    for character in connected_characters():
        location: Any = character.location
        if location is None or isinstance(location, ShipRoom):
            continue
        if isinstance(location, Room) and location.place_id == LIMBO_ID:
            continue
        ashore.append(character)
    return ashore


LATE_JOINER: str = (
    "You've been aboard all along, too seasick to leave your hammock below. Today you feel "
    "better at last, and climb up on deck. (Type |wjournal|n to catch up on what the "
    "expedition has found so far.)"
)


def begin_destination(default: Any) -> tuple[Any, str | None]:
    """
    Where `begin` leads, and what a player is told on the way (DECISIONS.md, 18).

    While the ship is in port, the usual place (the Society Office). While she's away, the
    Deck, with a line for a player joining an expedition already under way.
    """
    content: Content = load_content()
    if current_position().id == content.start_position:
        return default, None
    deck: Any = find_place(content.place_of_kind("deck").id)
    if deck is None:
        return default, None
    return deck, LATE_JOINER


def normalise_direction(text: str) -> str:
    """`w` -> `west`, `to the west` -> `west`."""
    words: list[str] = [w for w in text.lower().split() if w not in ("to", "the")]
    direction: str = " ".join(words)
    return _DIRECTIONS.get(direction, direction)


def sailing_options(position: PositionSpec) -> str:
    """Where the ship is and where she can sail from here, in words."""
    directions: list[str] = [route.direction for route in position.routes]
    where: str = f"The ship is here: {position.name}."
    if not directions:
        return f"{where} There is nowhere to sail from here."
    return f"{where} You can sail: {', '.join(directions)}. (For example: sail {directions[0]})"


def sail(caller: Any, text: str) -> bool:
    """Sail the ship in a direction. Returns True if she sailed."""
    content: Content = load_content()
    position: PositionSpec = current_position()
    direction: str = normalise_direction(text)
    if not direction:
        caller.msg(sailing_options(position))
        return False
    route: RouteSpec | None = position.route(direction)
    if route is None:
        caller.msg(f"You can't sail {direction} from here. {sailing_options(position)}")
        return False
    left_behind: list[Any] = crew_ashore()
    if left_behind:
        names: str = ", ".join(character.get_display_name(caller) for character in left_behind)
        caller.msg(f"Not without {names}! Wait until everyone is aboard.")
        return False

    old_shore: Any = find_place(position.ashore) if position.ashore else None
    new_position: PositionSpec = content.positions[route.to]
    get_expedition().move_ship(new_position.id)
    moor_ship(new_position)
    new_shore: Any = find_place(new_position.ashore) if new_position.ashore else None

    if old_shore is not None:
        old_shore.msg_contents(SHORE_DEPARTURE)
    for room in ship_rooms():
        room.msg_contents(route.text)
        for character in room.contents_get(content_type="character"):
            room.send_visuals(character)
            character.msg(room.return_appearance(character))
    if new_shore is not None:
        new_shore.msg_contents(SHORE_ARRIVAL)
    if new_position.clue is not None:  # what the Deck shows here (the empty sea, C4)
        discover(new_position.clue, caller)
    return True
