"""
Talking to the characters: `ask <character> about <topic>`.

Who can be asked: the inhabitants standing in the asker's room, and, anywhere aboard (Deck
and Cabin), the Ship. What they say comes from `world/content/characters.yaml`.

Conversations are heard by everyone in the room, so players exploring together hear the same
answers. Nothing is logged (DECISIONS.md, 8).

In stage A2 every topic gives its `reply`. The `truth` replies of characters who hide
something, and the clues replies reveal, come with the journal and the conditions (A3, A4).
"""

from dataclasses import dataclass
from typing import Any

from typeclasses.inhabitants import Inhabitant
from typeclasses.rooms import ShipRoom
from world.content import CharacterSpec, Content, TopicSpec, load_content, normalise_words

ABOUT: str = "about"
USAGE: str = "Usage: |wask <someone> about <something>|n, or just |wask <someone>|n."


@dataclass(frozen=True)
class Listener:
    """Someone who can be asked things here: an inhabitant, or the Ship (who has no object)."""

    spec: CharacterSpec
    inhabitant: Inhabitant | None


def listeners(caller: Any) -> list[Listener]:
    """Everyone the caller can talk to where they are."""
    location: Any = caller.location
    found: list[Listener] = []
    if location is None:
        return found
    for obj in location.contents:
        if isinstance(obj, Inhabitant):
            spec: CharacterSpec | None = obj.spec
            if spec is not None:
                found.append(Listener(spec=spec, inhabitant=obj))
    if isinstance(location, ShipRoom):
        content: Content = load_content()
        found.extend(
            Listener(spec=s, inhabitant=None) for s in content.characters.values() if s.aboard
        )
    return found


def _match(name: str, candidates: list[CharacterSpec]) -> CharacterSpec | None:
    """The character called `name`: a full name or alias, or else one unambiguous word of one."""
    wanted: str = normalise_words(name)
    if not wanted:
        return None
    for spec in candidates:
        if wanted in spec.words:
            return spec
    partial: list[CharacterSpec] = [
        spec for spec in candidates if any(wanted in word.split() for word in spec.words)
    ]
    return partial[0] if len(partial) == 1 else None


def find_listener(caller: Any, name: str) -> Listener | None:
    """The listener here called `name`, or None."""
    here: list[Listener] = listeners(caller)
    spec: CharacterSpec | None = _match(name, [listener.spec for listener in here])
    return next((listener for listener in here if listener.spec is spec), None)


def split_request(caller: Any, text: str) -> tuple[str, str]:
    """
    Split what follows `ask` into (who, what).

    `barnaby about the storm` -> (`barnaby`, `the storm`); `about the storm` -> (``, `the
    storm`). Without `about`, the longest start that names someone here is the who:
    `old barnaby storm` -> (`old barnaby`, `storm`).
    """
    words: list[str] = text.split()
    lowered: list[str] = [word.lower() for word in words]
    if ABOUT in lowered:
        at: int = lowered.index(ABOUT)
        return " ".join(words[:at]), " ".join(words[at + 1 :])
    for end in range(len(words), 0, -1):
        if find_listener(caller, " ".join(words[:end])) is not None:
            return " ".join(words[:end]), " ".join(words[end:])
    return text.strip(), ""


def speech(spec: CharacterSpec, text: str) -> str:
    """A line from a character: `Old Barnaby says: "..."`, or the text itself if it narrates."""
    if text.startswith('"'):
        return f"{spec.name[0].upper()}{spec.name[1:]} says: {text}"
    return text


def suggestions(spec: CharacterSpec) -> str:
    """A line offering a few topics to ask this character about."""
    if not spec.suggest:
        return ""
    topics: str = ", ".join(f"|w{topic_id}|n" for topic_id in spec.suggest)
    return (
        f"You could ask {spec.name} about: {topics}. "
        f"(For example: |wask {spec.id} about {spec.suggest[0]}|n)"
    )


def _who_is_here(caller: Any) -> str:
    here: list[Listener] = listeners(caller)
    if not here:
        return "There is nobody here to talk to."
    names: str = ", ".join(f"|w{listener.spec.name}|n" for listener in here)
    return f"You can talk to: {names}."


def _not_here(caller: Any, name: str) -> str:
    """Why nobody called `name` answers: not here at all, or the Ship while ashore."""
    content: Content = load_content()
    aboard: list[CharacterSpec] = [s for s in content.characters.values() if s.aboard]
    ship: CharacterSpec | None = _match(name, aboard)
    if ship is not None and not isinstance(caller.location, ShipRoom):
        return f"{ship.name[0].upper()}{ship.name[1:]} can only hear you when you're aboard."
    return f"There's nobody called '{name}' here. {_who_is_here(caller)}"


def _say_to_room(caller: Any, mine: str, theirs: str, reply: str) -> None:
    """The asker's line, what the others in the room see of it, then the answer for all."""
    caller.msg(mine)
    location: Any = caller.location
    if location is not None:
        location.msg_contents(theirs, exclude=[caller])
        location.msg_contents(reply)
    else:
        caller.msg(reply)


def ask(caller: Any, text: str) -> TopicSpec | None:
    """
    Handle `ask <text>`. Returns the topic that was answered, or None (a greeting, a
    fallback, or nobody to ask).
    """
    who, what = split_request(caller, text.strip())
    if not who and not what:
        caller.msg(f"{USAGE}\n{_who_is_here(caller)}")
        return None

    listener: Listener | None
    if who:
        listener = find_listener(caller, who)
        if listener is None:
            caller.msg(_not_here(caller, who))
            return None
    else:
        here: list[Listener] = listeners(caller)
        if len(here) != 1:
            caller.msg(f"Who do you want to ask? {_who_is_here(caller)}")
            return None
        listener = here[0]

    spec: CharacterSpec = listener.spec
    asker: str = caller.get_display_name(caller)
    if not what:
        lines: str = "\n".join(
            line for line in (speech(spec, spec.greeting), suggestions(spec)) if line
        )
        _say_to_room(caller, f"You greet {spec.name}.", f"{asker} greets {spec.name}.", lines)
        return None

    topic: TopicSpec | None = spec.topic(what)
    mine: str = f"You ask {spec.name} about {what}."
    theirs: str = f"{asker} asks {spec.name} about {what}."
    if topic is None:
        _say_to_room(caller, mine, theirs, f"{speech(spec, spec.fallback)}\n{suggestions(spec)}")
        return None
    _say_to_room(caller, mine, theirs, speech(spec, topic.reply))
    return topic
