"""
The way somewhere: for a player who names a place or a thing that isn't here (playtest
2026-11-26: "I don't know the way to the ship" ended a run; `go to lagoon beach` and `get
chart` only said no).

Routes follow the exits a player can use now, so a path not learned yet (DECISIONS.md, 40)
is never given away. Each answer names the way as exits to type, in white: `northeast,
then east`.
"""

from collections import deque
from collections.abc import Callable
from typing import Any

from typeclasses.rooms import Room, ShipRoom
from typeclasses.things import Thing
from world.content import Content, ThingSpec, load_content, normalise_words
from world.places import find_thing


def route(caller: Any, goal: Callable[[Any], bool]) -> tuple[Any, list[str]] | None:
    """
    The nearest room from the caller's that `goal` accepts, and the exits to type on the
    way there (empty if it's here), or None if no usable way leads to one.
    """
    start: Any = caller.location
    if start is None:
        return None
    queue: deque[tuple[Any, list[str]]] = deque([(start, [])])
    seen: set[int] = {start.id}
    while queue:
        room, steps = queue.popleft()
        if goal(room):
            return room, steps
        for exit_obj in getattr(room, "exits", []):
            there: Any = exit_obj.destination
            if there is None or there.id in seen or not exit_obj.access(caller, "traverse"):
                continue
            seen.add(there.id)
            queue.append((there, [*steps, str(exit_obj.key)]))
    return None


def steps_text(steps: list[str]) -> str:
    """`|wnortheast|n, then |weast|n`."""
    return ", then ".join(f"|w{step}|n" for step in steps)


def way_to_place(caller: Any, wanted: str) -> str | None:
    """
    For `go to <a place>` that isn't next door: the way there, or None if no place the
    caller can reach is called that.
    """
    name: str = normalise_words(wanted)
    if not name:
        return None

    def called(room: Any) -> bool:
        return isinstance(room, Room) and normalise_words(str(room.key)) == name

    found: tuple[Any, list[str]] | None = route(caller, called)
    if found is None:
        return None
    room, steps = found
    if not steps:
        return f"You're in the {room.key} already."
    return f"To get to the {room.key}: {steps_text(steps)}."


def _thing_named(text: str) -> ThingSpec | None:
    """The thing of the game a player means by `text` (its name or an alias), or None."""
    wanted: str = normalise_words(text)
    content: Content = load_content()
    for spec in content.things.values():
        if wanted in spec.look.words:
            return spec
    return None


def where_is_thing(caller: Any, text: str) -> str | None:
    """
    For `get`, `look` or `examine` of a thing of the game that isn't here: where it is,
    and the way there; None if `text` names no such thing.
    """
    spec: ThingSpec | None = _thing_named(text)
    thing: Any = find_thing(spec.id) if spec is not None else None
    if spec is None or not isinstance(thing, Thing):
        return None
    holder: Any = thing.location
    if holder is None:
        return None
    if holder == caller:
        return f"You already have the {spec.name}. (|winventory|n shows what you carry.)"
    if not isinstance(holder, Room):  # someone else carries it
        return f"The {spec.name} isn't here: {holder.get_display_name(caller)} has it."
    where: str = "aboard the Good Hope" if isinstance(holder, ShipRoom) else f"in the {holder.key}"
    found: tuple[Any, list[str]] | None = route(caller, lambda room: room == holder)
    way: str = f" To get there: {steps_text(found[1])}." if found and found[1] else ""
    return f"The {spec.name} isn't here: it's {where}.{way}"
