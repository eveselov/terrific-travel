"""
The story content of Phantom Island, read from the YAML files in `world/content/`.

The YAML files are meant to be edited without touching code (see the comments at the top of
each file). This module turns them into typed, frozen dataclasses and checks that they fit
together: every exit leads to a known place, every map exists, every route leads to a known
position, every character stands in a known place, and so on. A mistake raises
`ContentError`, naming the file and the entry.

`load_content()` reads the files once and caches the result; `reload_content()` reads them
again (the world builder does that, so `batchcode build` picks up edits without a reload).
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import yaml

CONTENT_DIR: Path = Path(__file__).parent / "content"
PLACES_FILE: str = "places.yaml"
SHIP_FILE: str = "ship.yaml"
MAPS_FILE: str = "maps.yaml"
CHARACTERS_FILE: str = "characters.yaml"
CLUES_FILE: str = "clues.yaml"
THINGS_FILE: str = "things.yaml"

# A clue's fact inside a text: `[[coral, grown into the brass]]` (DECISIONS.md, 20).
CLUE_MARK: re.Pattern[str] = re.compile(r"\[\[(.+?)\]\]", re.DOTALL)
CLUE_ID: re.Pattern[str] = re.compile(r"C\d+")

LIMBO_ID: str = "limbo"
ROOM_KINDS: tuple[str, ...] = ("room", "deck", "cabin")
STANCES: tuple[str, ...] = ("truth", "mistaken", "hiding")
ABOARD_WHERE: str = "aboard"  # a character's `where` for the Ship: the Deck and the Cabin

# Words dropped from the front of what players type, so `about the storm` finds `storm`.
_LEADING_WORDS: tuple[str, ...] = ("the", "a", "an", "her", "his", "your")

# Short forms that compass-style exits get automatically.
DIRECTION_ALIASES: dict[str, str] = {
    "north": "n",
    "south": "s",
    "east": "e",
    "west": "w",
    "northeast": "ne",
    "northwest": "nw",
    "southeast": "se",
    "southwest": "sw",
    "up": "u",
    "down": "d",
    "in": "i",
    "out": "o",
}

Point = tuple[int, int]


class ContentError(ValueError):
    """The story content files are inconsistent or malformed."""


@dataclass(frozen=True)
class ExitSpec:
    """One exit from a place."""

    key: str
    aliases: tuple[str, ...]
    to: str


@dataclass(frozen=True)
class Reveal:
    """A text that may reveal a clue; the clue's fact is marked `[[...]]` in it."""

    text: str
    clue: str | None


@dataclass(frozen=True)
class LookSpec:
    """
    Something to look at: a detail of a place (`look beams`) or a thing (`look compass`).

    `desc` is what `look` shows, `close` what `examine` shows (if it has nothing closer,
    `examine` is the same as `look`), and `extras` what's added for someone carrying a thing
    (by thing id), on either.
    """

    id: str
    words: tuple[str, ...]  # the id and its aliases, normalised
    desc: Reveal
    close: Reveal | None
    extras: dict[str, Reveal]


@dataclass(frozen=True)
class PlaceSpec:
    """One room: Limbo, a place in the port or on the island, or a room of the ship."""

    id: str
    name: str
    kind: str
    desc: str
    map: str | None
    map_pos: Point | None
    image: str | None
    exits: tuple[ExitSpec, ...]
    details: dict[str, LookSpec]


@dataclass(frozen=True)
class RouteSpec:
    """A way the ship can sail from a position."""

    direction: str
    to: str
    text: str


@dataclass(frozen=True)
class PositionSpec:
    """A place the ship can be: moored, at sea, or at anchor."""

    id: str
    name: str
    chart_pos: Point
    map: str | None
    map_pos: Point | None
    ashore: str | None
    deck: str
    clue: str | None  # revealed by the `deck` text
    details: dict[str, LookSpec]  # seen from the Deck
    cabin: str
    shore: str
    routes: tuple[RouteSpec, ...]

    def route(self, direction: str) -> RouteSpec | None:
        """The route in this direction, or None if the ship can't sail that way from here."""
        for route in self.routes:
            if route.direction == direction:
                return route
        return None


@dataclass(frozen=True)
class MapSpec:
    """A map picture. Coordinates on it are in picture pixels, (0, 0) at the top left."""

    key: str
    title: str
    image: str
    width: int
    height: int


@dataclass(frozen=True)
class ExitName:
    """The key and aliases of one of the ship's exits (`ashore`, `aboard`)."""

    key: str
    aliases: tuple[str, ...]


def normalise_words(text: str) -> str:
    """`  The Storm? ` -> `storm`: lower case, no punctuation, no leading `the`."""
    cleaned: str = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text.lower())
    words: list[str] = [w for w in cleaned.split() if w != "s"]  # `halcyon's` -> `halcyon`
    while len(words) > 1 and words[0] in _LEADING_WORDS:
        words.pop(0)
    return " ".join(words)


def match_words[T](text: str, candidates: Sequence[tuple[T, tuple[str, ...]]]) -> T | None:
    """
    The candidate a player means by `text`, from (candidate, its normalised words) pairs.

    First the whole text (`big hut`); if that finds nothing, any single word of it, as long
    as only one candidate matches (`old beams` finds `beams`; two matches find nothing).
    """
    wanted: str = normalise_words(text)
    if not wanted:
        return None
    for candidate, words in candidates:
        if wanted in words:
            return candidate
    found: list[T] = []
    for word in wanted.split():
        for candidate, words in candidates:
            if word in words and candidate not in found:
                found.append(candidate)
    return found[0] if len(found) == 1 else None


def find_look(text: str, looks: Sequence[LookSpec]) -> LookSpec | None:
    """The detail (or thing's look) a player means, or None."""
    return match_words(text, [(look, look.words) for look in looks])


@dataclass(frozen=True)
class ClueSpec:
    """One clue of the mystery, as written into the journal."""

    id: str
    title: str
    journal: str


@dataclass(frozen=True)
class StepSpec:
    """What reading or using a thing does at one ship position."""

    text: str
    clue: str | None
    needs: tuple[str, ...]  # flags or clue ids that must already be found
    sets: str | None  # a flag to remember for the expedition
    otherwise: str | None  # shown while `needs` isn't met

    @property
    def reveal(self) -> Reveal:
        return Reveal(text=self.text, clue=self.clue)


@dataclass(frozen=True)
class ActionSpec:
    """What `read <thing>` or `use <thing>` does."""

    default: Reveal
    only_in: str | None  # the place id where it works, or None for anywhere
    elsewhere: str | None  # shown anywhere else
    at: dict[str, StepSpec]  # by ship position id, aboard only


@dataclass(frozen=True)
class ThingSpec:
    """An object in the world: something to look at, read, use, and perhaps carry."""

    id: str
    name: str
    aliases: tuple[str, ...]
    where: str
    portable: bool
    stays: str | None
    look: LookSpec
    read: ActionSpec | None
    use: ActionSpec | None


@dataclass(frozen=True)
class TruthSpec:
    """What a character says about a topic once they stop hiding it (used from stage A4)."""

    needs: tuple[str, ...]
    reply: str
    clue: str | None


@dataclass(frozen=True)
class TopicSpec:
    """One thing a character can be asked about."""

    id: str
    words: tuple[str, ...]  # the id, its shared aliases and its own aliases, normalised
    reply: str
    stance: str
    clue: str | None
    truth: TruthSpec | None


@dataclass(frozen=True)
class CharacterSpec:
    """One of the people (or the Ship) players can talk to."""

    id: str
    name: str
    aliases: tuple[str, ...]
    places: tuple[str, ...]  # place ids; empty for a character who is aboard
    aboard: bool
    desc: str
    greeting: str
    suggest: tuple[str, ...]
    fallback: str
    topics: dict[str, TopicSpec]

    @property
    def words(self) -> tuple[str, ...]:
        """Everything players can call this character, normalised."""
        names: tuple[str, ...] = (self.id, self.name, *self.aliases)
        return tuple(dict.fromkeys(normalise_words(name) for name in names))

    def topic(self, text: str) -> TopicSpec | None:
        """
        The topic a player means, or None if this character doesn't know it.

        First the whole text (`great storm`); if that finds nothing, any single word of it,
        as long as only one topic matches (`weather and sailing` matches two, so it's None).
        """
        wanted: str = normalise_words(text)
        for topic in self.topics.values():
            if wanted in topic.words:
                return topic
        found: list[TopicSpec] = []
        for word in wanted.split():
            for topic in self.topics.values():
                if word in topic.words and topic not in found:
                    found.append(topic)
        return found[0] if len(found) == 1 else None

    def topics_in(self, text: str) -> list[TopicSpec]:
        """
        Every topic named by a single word of the text, in the order the words come:
        `halcyon chart` -> [halcyon, chart]. Used when `topic` finds nothing because the
        player asked about several things at once.
        """
        found: list[TopicSpec] = []
        for word in normalise_words(text).split():
            for topic in self.topics.values():
                if word in topic.words and topic not in found:
                    found.append(topic)
        return found


@dataclass(frozen=True)
class Content:
    """All story content of the game."""

    places: dict[str, PlaceSpec]
    maps: dict[str, MapSpec]
    positions: dict[str, PositionSpec]
    start_position: str
    sea_chart: str
    ashore_exit: ExitName
    aboard_exit: ExitName
    characters: dict[str, CharacterSpec]
    clues: dict[str, ClueSpec]
    things: dict[str, ThingSpec]

    def place_of_kind(self, kind: str) -> PlaceSpec:
        """The one place of this kind (`deck` or `cabin`)."""
        for place in self.places.values():
            if place.kind == kind:
                return place
        raise ContentError(f"No place of kind {kind!r}.")


# --- Reading single values ------------------------------------------------------------


def _mapping(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContentError(f"{where}: expected a mapping (name: value lines).")
    return {str(key): item for key, item in value.items()}


def _text(data: dict[str, Any], field: str, where: str, default: str | None = None) -> str:
    value: Any = data.get(field, default)
    if value is None:
        raise ContentError(f"{where}: `{field}` is missing.")
    if not isinstance(value, str) or not value.strip():
        raise ContentError(f"{where}: `{field}` must be a non-empty text.")
    return value.strip()


def _optional_text(data: dict[str, Any], field: str, where: str) -> str | None:
    if data.get(field) is None:
        return None
    return _text(data, field, where)


def _int(data: dict[str, Any], field: str, where: str) -> int:
    value: Any = data.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ContentError(f"{where}: `{field}` must be a whole number above 0.")
    return value


def _point(data: dict[str, Any], field: str, where: str) -> Point | None:
    value: Any = data.get(field)
    if value is None:
        return None
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(v, int) and not isinstance(v, bool) for v in value)
    ):
        raise ContentError(f"{where}: `{field}` must be [x, y] with two whole numbers.")
    return int(value[0]), int(value[1])


def _words(value: Any, field: str, where: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
        raise ContentError(f"{where}: `{field}` must be a list of words.")
    return tuple(v.strip() for v in value)


def _aliases(value: Any, where: str) -> tuple[str, ...]:
    return _words(value, "aliases", where)


# --- Reading entries ------------------------------------------------------------------


def _exit(key: str, value: Any, where: str) -> ExitSpec:
    aliases: list[str] = []
    if key in DIRECTION_ALIASES:
        aliases.append(DIRECTION_ALIASES[key])
    if isinstance(value, str):
        return ExitSpec(key=key, aliases=tuple(aliases), to=value)
    data: dict[str, Any] = _mapping(value, where)
    aliases.extend(a for a in _aliases(data.get("aliases"), where) if a not in aliases)
    return ExitSpec(key=key, aliases=tuple(aliases), to=_text(data, "to", where))


def _reveal(data: dict[str, Any], field: str, where: str) -> Reveal:
    """A text (in `field`) and the clue it may reveal (in `clue`)."""
    return Reveal(text=_text(data, field, where), clue=_optional_text(data, "clue", where))


def _look(look_id: str, data: dict[str, Any], aliases: tuple[str, ...], where: str) -> LookSpec:
    close: Reveal | None = None
    if data.get("close") is not None:
        close = _reveal(_mapping(data["close"], f"{where}, close"), "text", f"{where}, close")
    extras_data: dict[str, Any] = _mapping(data.get("with") or {}, f"{where}, with")
    return LookSpec(
        id=look_id,
        words=tuple(dict.fromkeys(normalise_words(word) for word in (look_id, *aliases))),
        desc=_reveal(data, "desc", where),
        close=close,
        extras={
            thing_id: _reveal(_mapping(item, f"{where}, with {thing_id}"), "text", where)
            for thing_id, item in extras_data.items()
        },
    )


def _details(value: Any, where: str) -> dict[str, LookSpec]:
    details: dict[str, LookSpec] = {}
    for key, item in _mapping(value or {}, f"{where}, details").items():
        detail_where: str = f"{where}, detail {key}"
        data: dict[str, Any] = _mapping(item, detail_where)
        details[key] = _look(key, data, _aliases(data.get("aliases"), detail_where), detail_where)
    return details


def _place(place_id: str, value: Any, file: str) -> PlaceSpec:
    where: str = f"{file}, {place_id}"
    data: dict[str, Any] = _mapping(value, where)
    kind: str = _text(data, "kind", where, default="room")
    if kind not in ROOM_KINDS:
        raise ContentError(f"{where}: `kind` must be one of {', '.join(ROOM_KINDS)}.")
    exits_data: dict[str, Any] = _mapping(data.get("exits") or {}, f"{where}, exits")
    return PlaceSpec(
        id=place_id,
        name=_text(data, "name", where),
        kind=kind,
        desc=_text(data, "desc", where),
        map=_optional_text(data, "map", where),
        map_pos=_point(data, "map_pos", where),
        image=_optional_text(data, "image", where),
        exits=tuple(_exit(key, item, f"{where}, exit {key}") for key, item in exits_data.items()),
        details=_details(data.get("details"), where),
    )


def _route(direction: str, value: Any, where: str) -> RouteSpec:
    data: dict[str, Any] = _mapping(value, where)
    return RouteSpec(
        direction=direction, to=_text(data, "to", where), text=_text(data, "text", where)
    )


def _position(position_id: str, value: Any) -> PositionSpec:
    where: str = f"{SHIP_FILE}, position {position_id}"
    data: dict[str, Any] = _mapping(value, where)
    chart_pos: Point | None = _point(data, "chart_pos", where)
    if chart_pos is None:
        raise ContentError(f"{where}: `chart_pos` is missing.")
    ashore: str | None = _optional_text(data, "ashore", where)
    routes_data: dict[str, Any] = _mapping(data.get("routes") or {}, f"{where}, routes")
    return PositionSpec(
        id=position_id,
        name=_text(data, "name", where),
        chart_pos=chart_pos,
        map=_optional_text(data, "map", where),
        map_pos=_point(data, "map_pos", where),
        ashore=ashore,
        deck=_text(data, "deck", where),
        clue=_optional_text(data, "clue", where),
        details=_details(data.get("details"), where),
        cabin=_text(data, "cabin", where),
        shore=_text(data, "shore", where) if ashore else "",
        routes=tuple(
            _route(direction, item, f"{where}, route {direction}")
            for direction, item in routes_data.items()
        ),
    )


def _map(key: str, value: Any) -> MapSpec:
    where: str = f"{MAPS_FILE}, {key}"
    data: dict[str, Any] = _mapping(value, where)
    return MapSpec(
        key=key,
        title=_text(data, "title", where),
        image=_text(data, "image", where),
        width=_int(data, "width", where),
        height=_int(data, "height", where),
    )


def _exit_name(data: dict[str, Any], field: str) -> ExitName:
    where: str = f"{SHIP_FILE}, {field}"
    exit_data: dict[str, Any] = _mapping(data.get(field), where)
    return ExitName(
        key=_text(exit_data, "key", where), aliases=_aliases(exit_data.get("aliases"), where)
    )


def _truth(value: Any, where: str) -> TruthSpec | None:
    if value is None:
        return None
    data: dict[str, Any] = _mapping(value, where)
    needs: tuple[str, ...] = _words(data.get("needs"), "needs", where)
    if not needs:
        raise ContentError(f"{where}: `needs` must name at least one clue or flag.")
    return TruthSpec(
        needs=needs, reply=_text(data, "reply", where), clue=_optional_text(data, "clue", where)
    )


def _topic(topic_id: str, value: Any, shared: dict[str, tuple[str, ...]], where: str) -> TopicSpec:
    data: dict[str, Any] = _mapping(value, where)
    stance: str = _text(data, "stance", where)
    if stance not in STANCES:
        raise ContentError(f"{where}: `stance` must be one of {', '.join(STANCES)}.")
    words: list[str] = [topic_id, *shared.get(topic_id, ()), *_aliases(data.get("aliases"), where)]
    return TopicSpec(
        id=topic_id,
        words=tuple(dict.fromkeys(normalise_words(word) for word in words)),
        reply=_text(data, "reply", where),
        stance=stance,
        clue=_optional_text(data, "clue", where),
        truth=_truth(data.get("truth"), f"{where}, truth"),
    )


def _character(character_id: str, value: Any, shared: dict[str, tuple[str, ...]]) -> CharacterSpec:
    where: str = f"{CHARACTERS_FILE}, {character_id}"
    data: dict[str, Any] = _mapping(value, where)
    where_value: Any = data.get("where")
    places: tuple[str, ...]
    if isinstance(where_value, str):
        places = () if where_value == ABOARD_WHERE else (where_value,)
    else:
        places = _words(where_value, "where", where)
        if not places:
            raise ContentError(
                f"{where}: `where` must be a place id, a list of them, or {ABOARD_WHERE}."
            )
    topics_data: dict[str, Any] = _mapping(data.get("topics") or {}, f"{where}, topics")
    return CharacterSpec(
        id=character_id,
        name=_text(data, "name", where),
        aliases=_aliases(data.get("aliases"), where),
        places=places,
        aboard=where_value == ABOARD_WHERE,
        desc=_text(data, "desc", where),
        greeting=_text(data, "greeting", where),
        suggest=_words(data.get("suggest"), "suggest", where),
        fallback=_text(data, "fallback", where),
        topics={
            key: _topic(key, item, shared, f"{where}, topic {key}")
            for key, item in topics_data.items()
        },
    )


def _clues(data: dict[str, Any]) -> dict[str, ClueSpec]:
    clues_data: dict[str, Any] = _mapping(data.get("clues") or {}, f"{CLUES_FILE}, clues")
    clues: dict[str, ClueSpec] = {}
    for clue_id, value in clues_data.items():
        where: str = f"{CLUES_FILE}, {clue_id}"
        if not CLUE_ID.fullmatch(clue_id):
            raise ContentError(f"{where}: clue ids are C and a number, like C7.")
        item: dict[str, Any] = _mapping(value, where)
        clues[clue_id] = ClueSpec(
            id=clue_id, title=_text(item, "title", where), journal=_text(item, "journal", where)
        )
    return clues


def _step(value: Any, where: str) -> StepSpec:
    data: dict[str, Any] = _mapping(value, where)
    needs: tuple[str, ...] = _words(data.get("needs"), "needs", where)
    otherwise: str | None = _optional_text(data, "otherwise", where)
    if needs and otherwise is None:
        raise ContentError(f"{where}: with `needs`, also say what happens `otherwise`.")
    return StepSpec(
        text=_text(data, "text", where),
        clue=_optional_text(data, "clue", where),
        needs=needs,
        sets=_optional_text(data, "sets", where),
        otherwise=otherwise,
    )


def _action(value: Any, where: str) -> ActionSpec | None:
    if value is None:
        return None
    data: dict[str, Any] = _mapping(value, where)
    only_in: str | None = _optional_text(data, "only_in", where)
    at_data: dict[str, Any] = _mapping(data.get("at") or {}, f"{where}, at")
    return ActionSpec(
        default=_reveal(data, "text", where),
        only_in=only_in,
        elsewhere=_text(data, "elsewhere", where) if only_in else None,
        at={key: _step(item, f"{where}, at {key}") for key, item in at_data.items()},
    )


def _thing(thing_id: str, value: Any) -> ThingSpec:
    where: str = f"{THINGS_FILE}, {thing_id}"
    data: dict[str, Any] = _mapping(value, where)
    portable: Any = data.get("portable", False)
    if not isinstance(portable, bool):
        raise ContentError(f"{where}: `portable` must be true or false.")
    name: str = _text(data, "name", where)
    aliases: tuple[str, ...] = _aliases(data.get("aliases"), where)
    look: LookSpec = _look(thing_id, data, (name, *aliases), where)
    return ThingSpec(
        id=thing_id,
        name=name,
        aliases=aliases,
        where=_text(data, "where", where),
        portable=portable,
        stays=_optional_text(data, "stays", where),
        look=look,
        read=_action(data.get("read"), f"{where}, read"),
        use=_action(data.get("use"), f"{where}, use"),
    )


def _things(data: dict[str, Any]) -> dict[str, ThingSpec]:
    things_data: dict[str, Any] = _mapping(data.get("things") or {}, f"{THINGS_FILE}, things")
    return {key: _thing(key, value) for key, value in things_data.items()}


def _characters(data: dict[str, Any]) -> dict[str, CharacterSpec]:
    shared_data: dict[str, Any] = _mapping(
        data.get("topic_aliases") or {}, f"{CHARACTERS_FILE}, topic_aliases"
    )
    shared: dict[str, tuple[str, ...]] = {
        key: _aliases(value, f"{CHARACTERS_FILE}, topic_aliases, {key}")
        for key, value in shared_data.items()
    }
    characters_data: dict[str, Any] = _mapping(
        data.get("characters") or {}, f"{CHARACTERS_FILE}, characters"
    )
    return {key: _character(key, value, shared) for key, value in characters_data.items()}


# --- Checking that it all fits together -----------------------------------------------


def _check_on_map(
    where: str, map_key: str | None, pos: Point | None, maps: dict[str, MapSpec]
) -> None:
    if map_key is None:
        if pos is not None:
            raise ContentError(f"{where}: has `map_pos` but no `map`.")
        return
    picture_map: MapSpec | None = maps.get(map_key)
    if picture_map is None:
        raise ContentError(f"{where}: unknown map {map_key!r}.")
    if pos is None:
        raise ContentError(f"{where}: has `map` but no `map_pos`.")
    x, y = pos
    if not (0 <= x <= picture_map.width and 0 <= y <= picture_map.height):
        raise ContentError(f"{where}: {list(pos)} is outside the {map_key!r} map.")


def _check(content: Content) -> None:
    places: dict[str, PlaceSpec] = content.places
    if LIMBO_ID not in places:
        raise ContentError(f"{PLACES_FILE}: the `{LIMBO_ID}` prologue is missing.")
    for kind in ("deck", "cabin"):
        found: list[str] = [p.id for p in places.values() if p.kind == kind]
        if len(found) != 1:
            raise ContentError(f"Exactly one place must have kind {kind!r} (found {found}).")

    for place in places.values():
        where: str = f"place {place.id}"
        if place.kind != "room" and place.map is not None:
            raise ContentError(f"{where}: ship rooms take their map from the ship's position.")
        _check_on_map(where, place.map, place.map_pos, content.maps)
        for exit_spec in place.exits:
            if exit_spec.to not in places:
                raise ContentError(
                    f"{where}, exit {exit_spec.key}: unknown place {exit_spec.to!r}."
                )

    positions: dict[str, PositionSpec] = content.positions
    if content.start_position not in positions:
        raise ContentError(f"{SHIP_FILE}: unknown start position {content.start_position!r}.")
    sea_chart: MapSpec | None = content.maps.get(content.sea_chart)
    if sea_chart is None:
        raise ContentError(f"{SHIP_FILE}: unknown sea chart map {content.sea_chart!r}.")
    for position in positions.values():
        where = f"position {position.id}"
        _check_on_map(where, content.sea_chart, position.chart_pos, content.maps)
        _check_on_map(where, position.map, position.map_pos, content.maps)
        if position.ashore is not None:
            shore: PlaceSpec | None = places.get(position.ashore)
            if shore is None or shore.kind != "room" or shore.id == LIMBO_ID:
                raise ContentError(
                    f"{where}: `ashore` must be a place on land, not {position.ashore!r}."
                )
        for route in position.routes:
            if route.to not in positions:
                raise ContentError(
                    f"{where}, route {route.direction}: unknown position {route.to!r}."
                )

    _check_characters(content)
    _check_things(content)
    _check_clue_marks(content)


def _look_texts(where: str, look: LookSpec) -> list[tuple[str, str, str | None]]:
    texts: list[tuple[str, str, str | None]] = [(where, look.desc.text, look.desc.clue)]
    if look.close is not None:
        texts.append((f"{where}, close", look.close.text, look.close.clue))
    for thing_id, extra in look.extras.items():
        texts.append((f"{where}, with {thing_id}", extra.text, extra.clue))
    return texts


def _action_texts(where: str, action: ActionSpec | None) -> list[tuple[str, str, str | None]]:
    if action is None:
        return []
    texts: list[tuple[str, str, str | None]] = [(where, action.default.text, action.default.clue)]
    if action.elsewhere is not None:
        texts.append((f"{where}, elsewhere", action.elsewhere, None))
    for position_id, step in action.at.items():
        texts.append((f"{where}, at {position_id}", step.text, step.clue))
        if step.otherwise is not None:
            texts.append((f"{where}, at {position_id}, otherwise", step.otherwise, None))
    return texts


def all_texts(content: Content) -> list[tuple[str, str, str | None]]:
    """Every text players can read, as (where it is, the text, the clue it reveals)."""
    texts: list[tuple[str, str, str | None]] = []
    for place in content.places.values():
        texts.append((f"place {place.id}", place.desc, None))
        for detail in place.details.values():
            texts.extend(_look_texts(f"place {place.id}, detail {detail.id}", detail))
    for position in content.positions.values():
        where: str = f"position {position.id}"
        texts.append((f"{where}, deck", position.deck, position.clue))
        texts.append((f"{where}, cabin", position.cabin, None))
        if position.shore:
            texts.append((f"{where}, shore", position.shore, None))
        for route in position.routes:
            texts.append((f"{where}, route {route.direction}", route.text, None))
        for detail in position.details.values():
            texts.extend(_look_texts(f"{where}, detail {detail.id}", detail))
    for character in content.characters.values():
        where = f"{CHARACTERS_FILE}, {character.id}"
        for field, text in (
            ("desc", character.desc),
            ("greeting", character.greeting),
            ("fallback", character.fallback),
        ):
            texts.append((f"{where}, {field}", text, None))
        for topic in character.topics.values():
            texts.append((f"{where}, topic {topic.id}", topic.reply, topic.clue))
            if topic.truth is not None:
                texts.append(
                    (f"{where}, topic {topic.id}, truth", topic.truth.reply, topic.truth.clue)
                )
    for thing in content.things.values():
        where = f"{THINGS_FILE}, {thing.id}"
        texts.extend(_look_texts(where, thing.look))
        if thing.stays is not None:
            texts.append((f"{where}, stays", thing.stays, None))
        texts.extend(_action_texts(f"{where}, read", thing.read))
        texts.extend(_action_texts(f"{where}, use", thing.use))
    return texts


def _check_clue_marks(content: Content) -> None:
    """Every text with a clue marks its fact `[[...]]`, and no other text has marks."""
    for where, text, clue in all_texts(content):
        marked: bool = CLUE_MARK.search(text) is not None
        leftover: str = CLUE_MARK.sub("", text)
        if "[[" in leftover or "]]" in leftover:
            raise ContentError(f"{where}: a [[ has no matching ]] (or the other way round).")
        if clue is None:
            if marked:
                raise ContentError(f"{where}: has a [[marked]] part but no `clue`.")
            continue
        if clue not in content.clues:
            raise ContentError(f"{where}: unknown clue {clue!r} (see {CLUES_FILE}).")
        if not marked:
            raise ContentError(f"{where}: reveals {clue} but marks no part of it [[like this]].")


def _check_extras(where: str, look: LookSpec, things: dict[str, ThingSpec]) -> None:
    for thing_id in look.extras:
        if thing_id not in things:
            raise ContentError(f"{where}: `with` names unknown thing {thing_id!r}.")


def _check_needs(where: str, needs: tuple[str, ...], content: Content, flags: set[str]) -> None:
    for need in needs:
        if CLUE_ID.fullmatch(need):
            if need not in content.clues:
                raise ContentError(f"{where}: needs unknown clue {need!r}.")
        elif need not in flags:
            raise ContentError(f"{where}: needs flag {need!r}, but nothing `sets` it.")


def _check_things(content: Content) -> None:
    for place in content.places.values():
        for detail in place.details.values():
            _check_extras(f"place {place.id}, detail {detail.id}", detail, content.things)
    for position in content.positions.values():
        for detail in position.details.values():
            _check_extras(f"position {position.id}, detail {detail.id}", detail, content.things)
    flags: set[str] = set()
    for thing in content.things.values():
        for action in (thing.read, thing.use):
            if action is not None:
                flags.update(step.sets for step in action.at.values() if step.sets)
    for character in content.characters.values():
        for topic in character.topics.values():
            if topic.truth is not None:
                # Flags such as `respect` are set by what players do (stage A4).
                clue_needs: tuple[str, ...] = tuple(
                    need for need in topic.truth.needs if CLUE_ID.fullmatch(need)
                )
                where: str = f"{CHARACTERS_FILE}, {character.id}, topic {topic.id}"
                _check_needs(where, clue_needs, content, flags)
    for thing in content.things.values():
        where = f"{THINGS_FILE}, {thing.id}"
        start: PlaceSpec | None = content.places.get(thing.where)
        if start is None or start.id == LIMBO_ID:
            raise ContentError(f"{where}: `where` must be a place, not {thing.where!r}.")
        _check_extras(where, thing.look, content.things)
        for verb, action in (("read", thing.read), ("use", thing.use)):
            if action is None:
                continue
            if action.only_in is not None and action.only_in not in content.places:
                raise ContentError(f"{where}, {verb}: unknown place {action.only_in!r}.")
            for position_id, step in action.at.items():
                if position_id not in content.positions:
                    raise ContentError(f"{where}, {verb}: unknown position {position_id!r}.")
                _check_needs(f"{where}, {verb}, at {position_id}", step.needs, content, flags)


def _check_characters(content: Content) -> None:
    for character in content.characters.values():
        where: str = f"{CHARACTERS_FILE}, {character.id}"
        for place_id in character.places:
            place: PlaceSpec | None = content.places.get(place_id)
            if place is None or place.kind != "room" or place.id == LIMBO_ID:
                raise ContentError(
                    f"{where}: `where` must be places on land or {ABOARD_WHERE}, not {place_id!r}."
                )
        for topic_id in character.suggest:
            if topic_id not in character.topics:
                raise ContentError(f"{where}: suggested topic {topic_id!r} isn't one of theirs.")
        owner: dict[str, str] = {}
        for topic in character.topics.values():
            for word in topic.words:
                if word in owner:
                    raise ContentError(
                        f"{where}: {word!r} means both topic {owner[word]!r} and {topic.id!r}."
                    )
                owner[word] = topic.id


# --- Loading --------------------------------------------------------------------------


def _read_yaml(directory: Path, file: str) -> dict[str, Any]:
    path: Path = directory / file
    try:
        data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ContentError(f"{file}: not valid YAML: {error}") from error
    return _mapping(data or {}, file)


def read_content(directory: Path = CONTENT_DIR) -> Content:
    """Read and check the content files in a directory (no caching)."""
    places_data: dict[str, Any] = _read_yaml(directory, PLACES_FILE)
    ship_data: dict[str, Any] = _read_yaml(directory, SHIP_FILE)
    maps_data: dict[str, Any] = _read_yaml(directory, MAPS_FILE)
    characters_data: dict[str, Any] = _read_yaml(directory, CHARACTERS_FILE)
    clues_data: dict[str, Any] = _read_yaml(directory, CLUES_FILE)
    things_data: dict[str, Any] = _read_yaml(directory, THINGS_FILE)

    places: dict[str, PlaceSpec] = {
        key: _place(key, value, PLACES_FILE) for key, value in places_data.items()
    }
    ship_rooms: dict[str, Any] = _mapping(ship_data.get("rooms") or {}, f"{SHIP_FILE}, rooms")
    for key, value in ship_rooms.items():
        if key in places:
            raise ContentError(
                f"{SHIP_FILE}, {key}: a place with this id is already in {PLACES_FILE}."
            )
        places[key] = _place(key, value, SHIP_FILE)

    positions_data: dict[str, Any] = _mapping(
        ship_data.get("positions") or {}, f"{SHIP_FILE}, positions"
    )
    content: Content = Content(
        places=places,
        maps={key: _map(key, value) for key, value in maps_data.items()},
        positions={key: _position(key, value) for key, value in positions_data.items()},
        start_position=_text(ship_data, "start", SHIP_FILE),
        sea_chart=_text(ship_data, "sea_chart", SHIP_FILE),
        ashore_exit=_exit_name(ship_data, "ashore_exit"),
        aboard_exit=_exit_name(ship_data, "aboard_exit"),
        characters=_characters(characters_data),
        clues=_clues(clues_data),
        things=_things(things_data),
    )
    _check(content)
    return content


@cache
def load_content() -> Content:
    """The game's content, read once and then cached."""
    return read_content()


def reload_content() -> Content:
    """Forget the cached content and read the files again."""
    load_content.cache_clear()
    return load_content()
