"""
Talking to the characters: `ask <character> about <topic>`.

Who can be asked: the inhabitants standing in the asker's room, and, aboard (her Deck), the
Ship. What they say comes from `world/content/characters.yaml`.

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
from world import notices
from world.clues import discover, show_marks, unseen
from world.content import (
    CharacterSpec,
    Content,
    Reveal,
    TopicSpec,
    TrustSpec,
    TruthSpec,
    find_look,
    load_content,
    normalise_words,
)
from world.discovery import find_thing_at_hand, location_details
from world.expedition import current_position, get_expedition
from world.notebook import learn

ABOUT: str = "about"
USAGE: str = "Usage: |wask <someone> about <something>|n, or just |wask <someone>|n."
# `ask him about the storm`: whoever the asker last spoke to.
LAST_PERSON: tuple[str, ...] = ("him", "her", "them")
MIN_NAME_START: int = 3  # `ask fai` is too short to mean Mrs. Fairweather


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
    if partial:
        return partial[0] if len(partial) == 1 else None
    # The start of a name is enough, if only one fits: `ask fair about the chart`.
    if len(wanted) < MIN_NAME_START or " " in wanted:
        return None
    starts: list[CharacterSpec] = [
        spec
        for spec in candidates
        if any(part.startswith(wanted) for word in spec.words for part in word.split())
    ]
    return starts[0] if len(starts) == 1 else None


def find_listener(caller: Any, name: str) -> Listener | None:
    """The listener here called `name`, or None."""
    here: list[Listener] = listeners(caller)
    spec: CharacterSpec | None = _match(name, [listener.spec for listener in here])
    return next((listener for listener in here if listener.spec is spec), None)


def split_request(text: str) -> tuple[str, str] | None:
    """
    Split what follows `ask` at `about` into (who, what): `barnaby about the storm` ->
    (`barnaby`, `the storm`), `about the storm` -> (``, `the storm`). None without `about`:
    then all of it names whom to greet.
    """
    words: list[str] = text.split()
    lowered: list[str] = [word.lower() for word in words]
    if ABOUT not in lowered:
        return None
    at: int = lowered.index(ABOUT)
    return " ".join(words[:at]), " ".join(words[at + 1 :])


def last_listener(caller: Any) -> Listener | None:
    """Whoever the caller spoke to last, if they can still hear the caller here."""
    last: Any = caller.ndb.last_asked
    return next((item for item in listeners(caller) if item.spec.id == last), None)


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
    expedition: Any = get_expedition()
    if truth is not None and expedition.met(truth.needs):
        return Reveal(text=truth.reply, clue=truth.clue, teaches=truth.teaches, sets=truth.sets)
    for meanwhile in topic.meanwhile:  # part of the way there (playtest 2026-11-24)
        if expedition.met(meanwhile.needs):
            return Reveal(text=meanwhile.reply, clue=topic.clue, teaches=topic.teaches)
    return Reveal(text=topic.reply, clue=topic.clue, teaches=topic.teaches)


def suggested(spec: CharacterSpec) -> tuple[str, ...]:
    """
    The topics to offer for this character: the Ship's depend on where she is, when her
    position has its own `suggest` (ship.yaml), and everyone else's are their own.
    """
    if spec.aboard:
        here: tuple[str, ...] = current_position().suggest
        if here:
            return here
    return spec.suggest


ASKED_KEY: str = "ask:topic"  # `seen` once a player has asked someone about a topic


def suggestions(spec: CharacterSpec) -> str:
    """
    The Good Hope's line offering a few topics, which change with where she is. Everyone
    else names their topics in white in their own greeting (playtest 2026-11-22).
    """
    offered: tuple[str, ...] = suggested(spec)
    if not offered or not spec.aboard:
        return ""
    topics: str = ", ".join(f"|w{topic_id}|n" for topic_id in offered)
    return (
        f"You could ask {spec.name} about: {topics}. "
        f"(For example: |wask {spec.aliases[0] if spec.aliases else spec.id} about {offered[0]}|n)"
    )


def ask_example(caller: Any, spec: CharacterSpec) -> str:
    """How to ask about a white word, until the player has asked someone about a topic."""
    offered: tuple[str, ...] = suggested(spec)
    if spec.aboard or not offered or not unseen(caller, [ASKED_KEY]):
        return ""
    return notices.quiet(f"To ask about a white word: |wask {spec.id} about {offered[0]}|n.")


def crew_talk() -> bool:
    """Whether the crew can be talked to (`crew_talk` in characters.yaml, 2026-11-23)."""
    return load_content().crew_talk


def _who_is_here(caller: Any) -> str:
    here: list[Listener] = [
        listener for listener in listeners(caller) if crew_talk() or not listener.spec.crew
    ]
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


def trust_progress(flag: str) -> str | None:
    """
    The quiet line acknowledging a mark of someone's trust (DECISIONS.md, 41): `Elder Ama's
    respect: 1 of 2.`, or what it means once it's won. None if the flag is no such mark.
    """
    for spec in load_content().characters.values():
        trust: TrustSpec | None = spec.trust
        if trust is None or flag not in trust.marks:
            continue
        return _progress(trust)
    return None


def _progress(trust: TrustSpec) -> str:
    """`Elder Ama's respect: 1 of 2. Still to do: ...`, or what it means once it's won."""
    expedition: Any = get_expedition()
    left: list[str] = [mark for mark in trust.marks if not expedition.met((mark,))]
    line: str = f"{trust.label}: {len(trust.marks) - len(left)} of {len(trust.marks)}."
    if not left:
        return f"{line} {trust.won}"
    todo: list[str] = [trust.todo[mark] for mark in left if mark in trust.todo]
    return f"{line} Still to do: {'; '.join(todo)}." if todo else line


def waiting_on_trust(spec: CharacterSpec, topic: TopicSpec) -> str | None:
    """
    The progress line after a refusal that waits on someone's trust, once some of it is
    earned (playtest 2026-11-24), so a refusal never sounds as if nothing counted.
    """
    trust: TrustSpec | None = spec.trust
    truth: TruthSpec | None = topic.truth
    expedition: Any = get_expedition()
    if trust is None or truth is None or expedition.met(truth.needs):
        return None
    if not any(mark in truth.needs for mark in trust.marks):
        return None
    if not any(expedition.met((mark,)) for mark in trust.marks):
        return None
    return _progress(trust)


def _remember(caller: Any, flag: str) -> None:
    """Set a flag a reply sets; a new mark of trust is acknowledged to the room."""
    expedition: Any = get_expedition()
    if expedition.met((flag,)):
        return
    expedition.set_flag(flag)
    progress: str | None = trust_progress(flag)
    if progress is not None and caller.location is not None:
        for character in caller.location.contents_get(content_type="character"):
            if not isinstance(character, Inhabitant):
                notices.tell(character, progress)


def _lines(*lines: str) -> str:
    return "\n".join(line for line in lines if line)


def _without_about(caller: Any, text: str) -> str:
    """
    What to say to `ask <text>` when `text` names nobody here to greet: how to put it
    with `about` (`ask barnaby storm`), why someone named doesn't answer (`ask ship` ashore,
    `ask crane` on the Quay), or that a topic needs someone to ask (`ask halcyon`).
    """
    words: list[str] = text.split()
    for end in range(len(words) - 1, 0, -1):
        name: str = " ".join(words[:end])
        listener: Listener | None = find_listener(caller, name)
        if listener is not None:
            rest: str = " ".join(words[end:])
            return f"To ask {listener.spec.name} about {rest}: |wask {name} about {rest}|n"
    elsewhere: str | None = _someone_else(caller, text)
    if elsewhere is not None:
        return elsewhere
    hint: str = _look_hint(caller, text)
    if not listeners(caller):
        return _lines("There is nobody here to talk to.", hint)
    return _lines(
        f"To ask about {text}, say whom you're asking: |wask <someone> about {text}|n. "
        + _who_is_here(caller),
        hint,
    )


def _addressee(caller: Any, who: str, what: str) -> Listener | str:
    """
    Whom `ask <who> about <what>` is for, or what to tell the caller instead. Without a
    name, or with `him`, `her` or `them`: whoever the caller spoke to last, if they're
    still here, else the only person here.
    """
    if who and normalise_words(who) not in LAST_PERSON:
        return find_listener(caller, who) or _not_here(caller, who)
    last: Listener | None = last_listener(caller)
    if last is not None:
        return last
    here: list[Listener] = listeners(caller)
    if len(here) == 1:
        return here[0]
    aboard: list[Listener] = [listener for listener in here if listener.spec.aboard]
    if aboard:  # with the crew on the Deck too, an unnamed question is for the Good Hope
        return aboard[0]
    hint: str = _look_hint(caller, what)
    if not here:
        return _lines("There is nobody here to talk to.", hint)
    return _lines(f"Whom do you want to ask about {what}? {_who_is_here(caller)}", hint)


def ask(caller: Any, text: str) -> TopicSpec | None:
    """
    Handle `ask <text>`. Returns the topic that was answered, or None (a greeting, a
    fallback, or nobody to ask).

    `ask <someone>` greets them; `ask <someone> about <topic>` asks; `ask about <topic>`
    (or `ask him about <topic>`) asks whoever the asker last spoke to, or the only person
    here. Several topics at once get the first answered.
    """
    text = text.strip()
    if not text:
        caller.msg(f"{USAGE}\n{_who_is_here(caller)}")
        return None
    split: tuple[str, str] | None = split_request(text)
    what: str
    if split is None:
        greeted: Listener | None = find_listener(caller, text)
        if greeted is None:
            caller.msg(_without_about(caller, text))
            return None
        listener: Listener = greeted
        what = ""
    else:
        who: str
        who, what = split
        if not what:
            caller.msg(f"Ask about what? {USAGE}")
            return None
        found: Listener | str = _addressee(caller, who, what)
        if isinstance(found, str):
            caller.msg(found)
            return None
        listener = found

    spec: CharacterSpec = listener.spec
    if spec.crew and not crew_talk():  # off: they have their say in councils only
        caller.msg(speech(spec, spec.busy or f"{spec.name} is busy."))
        return None
    caller.ndb.last_asked = spec.id
    asker: str = caller.get_display_name(caller)
    if not what:
        lines: str = "\n".join(
            line for line in (speech(spec, spec.greeting), suggestions(spec)) if line
        )
        _say_to_room(caller, f"You greet {spec.name}.", f"{asker} greets {spec.name}.", lines)
        example: str = ask_example(caller, spec)
        if example:
            caller.msg(example)
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
        offer: str = suggestions(spec)
        said_back: str = speech(spec, spec.fallback) + (f"\n{offer}" if offer else "")
        _say_to_room(caller, mine, theirs, said_back)
        hint = _look_hint(caller, what)
        if hint:
            caller.msg(hint)
        return None
    said: Reveal = answer(topic)
    waiting: str | None = waiting_on_trust(spec, topic)
    get_expedition().mark_seen(caller.id, [ASKED_KEY])
    _say_to_room(caller, mine, theirs, speech(spec, said.text))
    if waiting is not None:
        caller.msg(notices.quiet(waiting))
    if rest:
        caller.msg(_one_at_a_time(rest))
    with notices.together():
        for flag in (topic.sets, said.sets):
            if flag is not None:
                _remember(caller, flag)
        if said.clue is not None:
            discover(said.clue, caller, spec.name)
        learn(caller, said.teaches, spec.name, _players_here(caller))
    return topic
