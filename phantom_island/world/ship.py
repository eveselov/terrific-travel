"""
The players' ship: sailing between positions, and the exits between ship and shore.

The ship is one room, her Deck, that never moves (DECISIONS.md, 36). Sailing changes the
ship's position in the expedition state, and moves two exits: `ashore` on the Deck and
`aboard` on the shore. At sea both are put nowhere (location None), so they disappear until
the ship moors again.

An order names where to go: a position from the chart (`sail to 14 south 40 west`), a
direction (`sail west`), or a name (`sail to the island`, `sail home`). The Ship answers the
order, and the voyage is told as a short passage: one line every `STEP_SECONDS` real
seconds, the ship's marker moving along the sea chart, and the arrival with the last line.
Nothing needs doing while she sails. Her position meanwhile is `under_way` (ship.yaml), so
the Deck and the instruments show the open sea.
"""

from collections.abc import Callable
from typing import Any

from evennia.utils.utils import delay

from typeclasses.rooms import Room, ShipRoom
from typeclasses.scripts import Voyage
from world.clues import discover, show_marks
from world.content import (
    DIRECTION_ALIASES,
    LIMBO_ID,
    UNDER_WAY,
    Content,
    Coords,
    PositionSpec,
    RouteSpec,
    coords_text,
    load_content,
    parse_coords,
)
from world.expedition import connected_characters, current_position, get_expedition
from world.notebook import learn
from world.places import find_place, find_ship_exit

ASHORE: str = "ashore"
ABOARD: str = "aboard"

SHORE_DEPARTURE: str = "Your ship sets sail and slowly heads out to sea."
SHORE_ARRIVAL: str = "A ship sails in and drops anchor nearby."

# Real seconds between two lines of a voyage's passage.
STEP_SECONDS: float = 3.0

STILL_SAILING: str = (
    "The ship is under way. There's nothing to do until she gets there: the crew sail her. "
    "Watch the sea, or go below."
)
ALREADY_THERE: str = 'The Ship creaks, amused. "We\'re there already: {where}. Look around!"'
NO_SUCH_PLACE: str = (
    'The Ship creaks doubtfully. "{where}? I know of nothing there worth sailing to. The '
    "island's position is written on the Halcyon's chart, in the chart house: |wread chart|n.\""
)
BOTH_NUMBERS: str = (
    "The Ship creaks. \"Both numbers at once? Then we'd be searching blind. Keep one of "
    'them, Captain, the one we can trust, and change the other."'
)
NOT_A_POSITION: str = (
    "A position needs two numbers, each with its side of the world: the latitude, north or "
    "south, and the longitude, east or west. For example: |wsail to 10 north 25 east|n."
)

# n -> north, etc., so `sail w` works like `sail west`.
_DIRECTIONS: dict[str, str] = {short: full for full, short in DIRECTION_ALIASES.items()}


def ship_rooms() -> list[ShipRoom]:
    """The ship's built rooms (the Deck first), skipping any that haven't been built."""
    content: Content = load_content()
    rooms: list[ShipRoom] = []
    for kind in ("deck",):
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
    where: str = f"The ship is here: {position.name}."
    if position.orders:
        return f"{where} {position.orders}"
    directions: list[str] = [route.direction for route in position.routes]
    if not directions:
        return f"{where} There is nowhere to sail from here."
    return f"{where} You can sail: {', '.join(directions)}. (For example: sail {directions[0]})"


def find_route(position: PositionSpec, text: str) -> RouteSpec | str:
    """
    The route an order means from here, or what to tell the player if it means none.

    The order can be a position (`to 14 south 40 west`), a direction (`west`, `w`) or a
    name (`to the island`, `home`).
    """
    content: Content = load_content()
    words: list[str] = text.lower().split()
    if words and words[0] == "to":
        words = words[1:]
    order: str = " ".join(words)
    coords: Coords | None = parse_coords(order)
    if coords is not None:
        if position.coords == coords:
            return ALREADY_THERE.format(where=coords_text(coords))
        for route in position.routes:
            if content.positions[route.to].coords == coords:
                return route
        if position.search and position.coords is not None:
            return _search_route(position, position.coords, coords)
        return NO_SUCH_PLACE.format(where=coords_text(coords))
    if any(ch.isdigit() for ch in order):
        return NOT_A_POSITION
    found: RouteSpec | None = position.route(normalise_direction(order))
    if found is None:
        found = position.route_named(order)
    if found is None:
        return f"You can't sail {order} from here. {sailing_options(position)}"
    return found


def _search_route(position: PositionSpec, here: Coords, there: Coords) -> RouteSpec | str:
    """
    Where nobody knows the true position, an order by position is read as a direction
    (DECISIONS.md, 34): the same latitude further west is west, as in latitude sailing, and
    the ship finds whatever lies on the way. Changing both numbers at once is refused.
    """
    latitude_change: int = there[0] - here[0]
    longitude_change: int = there[1] - here[1]
    if latitude_change and longitude_change:
        return BOTH_NUMBERS
    direction: str
    if latitude_change:
        direction = "north" if latitude_change > 0 else "south"
    else:
        direction = "east" if longitude_change > 0 else "west"
    found: RouteSpec | None = position.route(direction)
    if found is None:
        return f"You can't sail {direction} from here. {sailing_options(position)}"
    return found


def route_open(route: RouteSpec) -> bool:
    """Whether the ship may sail this route now: what it `needs` is in the journal or set."""
    return not route.needs or bool(get_expedition().met(route.needs))


def sail(caller: Any, text: str, now: bool = False) -> bool:
    """
    Give the ship an order. Returns True if she set off. With `now`, the whole passage is
    told at once and the ship has arrived when this returns (`sail/now`, for scenarios).
    """
    if get_expedition().voyage is not None:
        caller.msg(STILL_SAILING)
        return False
    position: PositionSpec = current_position()
    if not text.strip():
        caller.msg(sailing_options(position))
        return False
    found: RouteSpec | str = find_route(position, text)
    if isinstance(found, str):
        caller.msg(found)
        return False
    if not route_open(found):
        caller.msg(found.refused or "Not yet, Captain.")  # a gate (leaving port, DECISIONS 39)
        return False
    left_behind: list[Any] = crew_ashore()
    if left_behind:
        names: str = ", ".join(character.get_display_name(caller) for character in left_behind)
        caller.msg(f"Not without {names}! Wait until everyone is aboard.")
        return False
    set_off(caller, position, found, now)
    return True


def later(seconds: float, callback: Callable[..., None], *args: Any) -> None:
    """Call `callback(*args)` in `seconds` real seconds (the tests call it at once)."""
    delay(seconds, callback, *args)


def _aboard() -> list[tuple[ShipRoom, Any]]:
    """Every character aboard, with the ship's room they are in."""
    return [
        (room, character)
        for room in ship_rooms()
        for character in room.contents_get(content_type="character")
    ]


def set_off(caller: Any, position: PositionSpec, route: RouteSpec, now: bool = False) -> None:
    """
    The ship leaves `position` along `route`: the Ship answers, and the passage begins (all
    at once, with `now`).
    """
    content: Content = load_content()
    old_shore: Any = find_place(position.ashore) if position.ashore else None
    voyage: Voyage = get_expedition().set_off(UNDER_WAY, route.to, route.direction, caller.id)
    moor_ship(content.positions[UNDER_WAY])
    if old_shore is not None:
        old_shore.msg_contents(SHORE_DEPARTURE, from_obj=caller)
    for room in ship_rooms():
        if route.order:
            room.msg_contents(show_marks(route.order), from_obj=caller)
        room.msg_contents(route.text, from_obj=caller)
    aboard: list[tuple[ShipRoom, Any]] = _aboard()
    for room, character in aboard:
        room.send_visuals(character)
    learn(caller, route.teaches, "an order to sail", [character for _, character in aboard])
    _next_step(voyage.number, now)


def _next_step(number: int, now: bool) -> None:
    """The passage's next line: in a few seconds, or at once with `now`."""
    if now:
        sail_on(number, now=True)
    else:
        later(STEP_SECONDS, sail_on, number)


def sail_on(number: int, now: bool = False) -> None:
    """
    The next line of the passage, with the ship's marker moved on; the last line arrives.
    Does nothing if voyage `number` is over (or a new expedition began meanwhile).
    """
    voyage: Voyage | None = get_expedition().voyage
    if voyage is None or voyage.number != number:
        return
    route: RouteSpec | None = load_content().positions[voyage.origin].route(voyage.direction)
    passage: tuple[str, ...] = route.passage if route is not None else ()
    step: int = voyage.step + 1
    if step <= len(passage):
        for room in ship_rooms():
            room.msg_contents(passage[step - 1])
    if step >= len(passage):
        arrive()
        return
    get_expedition().sail_on(step)
    for room, character in _aboard():
        room.send_visuals(character)
    _next_step(number, now)


def arrive() -> None:
    """The voyage ends: the ship is at her destination, and everyone aboard sees it."""
    voyage: Voyage | None = get_expedition().voyage
    if voyage is None:
        return
    get_expedition().arrive()
    new_position: PositionSpec = current_position()
    moor_ship(new_position)
    new_shore: Any = find_place(new_position.ashore) if new_position.ashore else None
    if new_shore is not None:
        new_shore.msg_contents(SHORE_ARRIVAL)
    aboard: list[tuple[ShipRoom, Any]] = _aboard()
    for room, character in aboard:
        room.send_visuals(character)
        character.msg(room.return_appearance(character))
    if new_position.clue is not None:  # what the Deck shows here (the empty sea, C4)
        finder: Any = _deck_watcher(voyage, aboard)
        if finder is not None:
            discover(new_position.clue, finder)


def _deck_watcher(voyage: Voyage, aboard: list[tuple[ShipRoom, Any]]) -> Any:
    """Who sees the view on arrival: whoever gave the order if on deck, else anyone on deck."""
    on_deck: list[Any] = [character for room, character in aboard if room.ship_kind == "deck"]
    for character in on_deck:
        if character.id == voyage.finder:
            return character
    return on_deck[0] if on_deck else None


def resume_voyage() -> None:
    """After a server restart, carry on with a voyage that was under way."""
    voyage: Voyage | None = get_expedition().voyage
    if voyage is not None:
        later(STEP_SECONDS, sail_on, voyage.number)
