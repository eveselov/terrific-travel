"""
Discovery: looking at details and things (`look beams`), looking closer (`examine compass`),
reading and using things (`read chronometer`, `use sextant`).

What each shows comes from the content files: details from `places.yaml` (and, seen from the
Deck, from the ship's current position in `ship.yaml`), things from `things.yaml`. Whatever
reveals a clue writes it into the shared journal (`world/clues.py`).

Looking is private: only the looker reads it (the journal line still goes to everyone).
Reading and using are heard by the whole room, like conversations, so players working
together share a noon sight.
"""

from typing import Any

from typeclasses.rooms import Deck, Room, ShipRoom
from typeclasses.things import Thing
from world.clues import discover, discover_all, show_marks
from world.content import (
    ActionSpec,
    Content,
    LookSpec,
    PlaceSpec,
    PositionSpec,
    Reveal,
    StepSpec,
    ThingSpec,
    find_look,
    load_content,
    match_words,
)
from world.expedition import current_position, get_expedition

VERBS: tuple[str, ...] = ("read", "use")


def things_at_hand(caller: Any) -> list[Thing]:
    """The things the caller carries, then the things in their room."""
    found: list[Thing] = [obj for obj in caller.contents if isinstance(obj, Thing)]
    location: Any = caller.location
    if location is not None:
        found.extend(obj for obj in location.contents if isinstance(obj, Thing))
    return [thing for thing in found if thing.spec is not None]


def carried_ids(caller: Any) -> set[str]:
    """The thing ids of everything the caller carries."""
    return {obj.thing_id for obj in caller.contents if isinstance(obj, Thing) and obj.thing_id}


def find_thing_at_hand(caller: Any, text: str) -> Thing | None:
    """The thing at hand the caller means, or None."""
    candidates: list[tuple[Thing, tuple[str, ...]]] = []
    for thing in things_at_hand(caller):
        spec: ThingSpec | None = thing.spec
        if spec is not None:
            candidates.append((thing, spec.look.words))
    return match_words(text, candidates)


def location_details(caller: Any) -> list[LookSpec]:
    """The details of the caller's room, and from the Deck, those of the ship's position."""
    location: Any = caller.location
    if not isinstance(location, Room):
        return []
    content: Content = load_content()
    details: list[LookSpec] = []
    place: PlaceSpec | None = content.places.get(location.place_id or "")
    if place is not None:
        details.extend(place.details.values())
    if isinstance(location, Deck):
        details.extend(current_position().details.values())
    return details


def show_look(caller: Any, look: LookSpec, close: bool) -> None:
    """Show a detail or thing to the caller, and write any clue it reveals into the journal."""
    first: Reveal = look.close if close and look.close is not None else look.desc
    carried: set[str] = carried_ids(caller)
    reveals: list[Reveal] = [first]
    reveals.extend(extra for thing_id, extra in look.extras.items() if thing_id in carried)
    caller.msg("\n\n".join(show_marks(reveal.text) for reveal in reveals))
    discover_all([reveal.clue for reveal in reveals], caller)


def look_at(caller: Any, text: str, close: bool = False) -> bool:
    """
    `look <text>` (or, with `close`, `examine <text>`) at a thing or a detail.

    Returns False if there is no such thing or detail here, so the default `look` can try
    (for characters, exits and anything else).
    """
    thing: Thing | None = find_thing_at_hand(caller, text)
    if thing is not None and thing.spec is not None:
        show_look(caller, thing.spec.look, close)
        return True
    detail: LookSpec | None = find_look(text, location_details(caller))
    if detail is not None:
        show_look(caller, detail, close)
        return True
    return False


def notice_surroundings(caller: Any) -> None:
    """After the caller saw their room: on the Deck, the view may reveal a clue (C4)."""
    if isinstance(caller.location, Deck):
        position: PositionSpec = current_position()
        if position.clue is not None:
            discover(position.clue, caller)


def _outcome(caller: Any, action: ActionSpec) -> Reveal:
    """What an action does here and now, remembering any flag it sets."""
    step: StepSpec | None = None
    if isinstance(caller.location, ShipRoom):
        step = action.at.get(current_position().id)
    if step is None:
        return action.default
    if not get_expedition().met(step.needs):
        return Reveal(text=step.otherwise or step.text, clue=None)
    if step.sets is not None:
        get_expedition().set_flag(step.sets)
    return step.reveal


def act(caller: Any, verb: str, text: str) -> bool:
    """`read <thing>` or `use <thing>`. Returns True if something happened."""
    if not text.strip():
        caller.msg(f"What do you want to {verb}?")
        return False
    thing: Thing | None = find_thing_at_hand(caller, text)
    spec: ThingSpec | None = thing.spec if thing is not None else None
    if spec is None:
        caller.msg(f"You don't see any '{text.strip()}' here.")
        return False
    action: ActionSpec | None = spec.read if verb == "read" else spec.use
    if action is None:
        caller.msg(f"You can't {verb} the {spec.name}.")
        return False
    location: Any = caller.location
    place_id: str | None = location.place_id if isinstance(location, Room) else None
    if action.only_in is not None and place_id != action.only_in:
        caller.msg(show_marks(action.elsewhere or f"You can't {verb} the {spec.name} here."))
        return False

    outcome: Reveal = _outcome(caller, action)
    caller.msg(f"You {verb} the {spec.name}.")
    text_shown: str = show_marks(outcome.text)
    if location is not None:
        location.msg_contents(
            f"{caller.key} {verb}s the {spec.name}.", exclude=[caller], from_obj=caller
        )
        location.msg_contents(text_shown, from_obj=caller)
    else:
        caller.msg(text_shown)
    if outcome.clue is not None:
        discover(outcome.clue, caller)
    return True


def return_things_home(character: Any) -> list[Thing]:
    """Put the things a character carries back in their places. Returns them."""
    returned: list[Thing] = []
    for obj in list(character.contents):
        if isinstance(obj, Thing) and obj.home is not None:
            obj.move_to(obj.home, quiet=True, move_type="teleport")
            returned.append(obj)
    return returned
