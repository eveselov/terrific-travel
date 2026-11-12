"""
Talking to the characters: `ask <character> about <topic>`.

Who can be asked: the inhabitants standing in the asker's room, and, anywhere aboard (Deck
and Cabin), the Ship. What they say comes from `world/content/characters.yaml`.

Conversations are heard by everyone in the room, so players exploring together hear the same
answers. Nothing is logged (DECISIONS.md, 8).

A character who hides something gives their `truth` reply once its `needs` are met: clue ids
in the journal (Crane admits the truth once the coral in the compass hinge, C2, has been
found), or flags set by what players do (Ama's `respect`, from stage A4). A reply that reveals
a clue shows the fact in yellow and writes the clue into the journal (`world/clues.py`).
"""

from dataclasses import dataclass
from typing import Any

from typeclasses.inhabitants import Inhabitant
from typeclasses.rooms import ShipRoom
from world.clues import discover, show_marks
from world.content import (
    CharacterSpec,
    Content,
    Reveal,
    TopicSpec,
    TruthSpec,
    find_look,
    load_content,
    normalise_words,
)
from world.discovery import find_thing_at_hand, location_details
from world.expedition import get_expedition

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
    `old barnaby storm` -> (`old barnaby`, `storm`). If no start names anyone here, it's
    all the what: `halcyon` -> (``, `halcyon`), for whoever is here to answer.
    """
    words: list[str] = text.split()
    lowered: list[str] = [word.lower() for word in words]
    if ABOUT in lowered:
        at: int = lowered.index(ABOUT)
        return " ".join(words[:at]), " ".join(words[at + 1 :])
    for end in range(len(words), 0, -1):
        if find_listener(caller, " ".join(words[:end])) is not None:
            return " ".join(words[:end]), " ".join(words[end:])
    return "", text.strip()


def speech(spec: CharacterSpec, text: str) -> str:
    """
    A line from a character: `Old Barnaby says: "..."`, or the text itself if it narrates.
    A clue's fact in it, marked `[[...]]`, is shown in yellow.
    """
    if text.startswith('"'):
        text = f"{spec.name[0].upper()}{spec.name[1:]} says: {text}"
    return show_marks(text)


def answer(topic: TopicSpec) -> Reveal:
    """What a character says about a topic now: the truth, once its `needs` are met."""
    truth: TruthSpec | None = topic.truth
    if truth is not None and get_expedition().met(truth.needs):
        return Reveal(text=truth.reply, clue=truth.clue)
    return Reveal(text=topic.reply, clue=topic.clue)


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


def _players_here(caller: Any) -> list[Any]:
    """The player characters in the caller's room (the caller too), not the inhabitants."""
    location: Any = caller.location
    if location is None:
        return []
    return [
        obj
        for obj in location.contents_get(content_type="character")
        if not isinstance(obj, Inhabitant)
    ]


def _player_called(caller: Any, name: str) -> Any:
    """The player here called exactly `name` (their name or an alias), or None."""
    wanted: str = normalise_words(name)
    for player in _players_here(caller):
        names: list[str] = [player.key, *player.aliases.all()]
        if wanted in (normalise_words(n) for n in names):
            return player
    return None


def _not_here(caller: Any, name: str) -> str:
    """
    Why nobody called `name` answers: it's a player (who talks with `say`), the Ship while
    ashore, or nobody here at all.
    """
    player: Any = _player_called(caller, name)
    if player is caller:
        return "That's you! Talking to yourself won't help much."
    if player is not None:
        return (
            f"{player.get_display_name(caller)} is another player, not one of the story's "
            "characters. Talk to them with |wsay|n."
        )
    content: Content = load_content()
    aboard: list[CharacterSpec] = [s for s in content.characters.values() if s.aboard]
    ship: CharacterSpec | None = _match(name, aboard)
    if ship is not None and not isinstance(caller.location, ShipRoom):
        return f"{ship.name[0].upper()}{ship.name[1:]} can only hear you when you're aboard."
    return f"There's nobody called '{name}' here. {_who_is_here(caller)}"


def _someone_else(caller: Any, text: str) -> str | None:
    """
    If `text` starts with the name of someone who isn't here to answer (a player, or a
    character elsewhere: `crane compass` on the Quay), why they don't answer. Only whole
    names count, so `old chart` isn't taken for Old Barnaby.
    """
    content: Content = load_content()
    words: list[str] = text.split()
    for end in range(len(words), 0, -1):
        name: str = " ".join(words[:end])
        wanted: str = normalise_words(name)
        named: bool = any(wanted in spec.words for spec in content.characters.values())
        if named or _player_called(caller, name) is not None:
            return _not_here(caller, name)
    return None


def _look_hint(caller: Any, text: str) -> str:
    """If `text` is something to look at here, a line saying so, else an empty string."""
    if (
        find_thing_at_hand(caller, text) is None
        and find_look(text, location_details(caller)) is None
    ):
        return ""
    return f"(To look at it: |wlook {normalise_words(text)}|n)"


def _one_at_a_time(rest: list[TopicSpec]) -> str:
    """The note after answering the first of several topics asked at once."""
    names: list[str] = [f"|w{topic.id}|n" for topic in rest]
    listed: str = names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"
    return f"(One thing at a time: you can ask about {listed} next.)"


def _say_to_room(caller: Any, mine: str, theirs: str, reply: str) -> None:
    """The asker's line, what the others in the room see of it, then the answer for all."""
    caller.msg(mine)
    location: Any = caller.location
    if location is not None:
        location.msg_contents(theirs, exclude=[caller], from_obj=caller)
        location.msg_contents(reply, from_obj=caller)
    else:
        caller.msg(reply)


def ask(caller: Any, text: str) -> TopicSpec | None:
    """
    Handle `ask <text>`. Returns the topic that was answered, or None (a greeting, a
    fallback, or nobody to ask).

    Without `about`, text that names nobody here is the topic, for the one person here
    (`ask halcyon` in the Society Office). Several topics at once get the first answered.
    """
    text = text.strip()
    who, what = split_request(caller, text)
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
        if ABOUT not in text.lower().split():
            elsewhere: str | None = _someone_else(caller, what)
            if elsewhere is not None:
                caller.msg(elsewhere)
                return None
        here: list[Listener] = listeners(caller)
        if len(here) != 1:
            hint: str = _look_hint(caller, what)
            if not here:
                caller.msg(
                    "\n".join(line for line in ("There is nobody here to talk to.", hint) if line)
                )
            else:
                whom: str = f"Whom do you want to ask about {what}? {_who_is_here(caller)}"
                caller.msg("\n".join(line for line in (whom, hint) if line))
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
    rest: list[TopicSpec] = []
    if topic is None:
        several: list[TopicSpec] = spec.topics_in(what)
        if len(several) > 1:
            topic, rest = several[0], several[1:]
            what = topic.id
    mine: str = f"You ask {spec.name} about {what}."
    theirs: str = f"{asker} asks {spec.name} about {what}."
    if topic is None:
        _say_to_room(caller, mine, theirs, f"{speech(spec, spec.fallback)}\n{suggestions(spec)}")
        hint = _look_hint(caller, what)
        if hint:
            caller.msg(hint)
        return None
    said: Reveal = answer(topic)
    _say_to_room(caller, mine, theirs, speech(spec, said.text))
    if rest:
        caller.msg(_one_at_a_time(rest))
    if said.clue is not None:
        discover(said.clue, caller)
    return topic
