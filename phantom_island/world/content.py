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
from dataclasses import field as dataclass_field
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
IDEAS_FILE: str = "ideas.yaml"  # optional: without it, the notebook stays empty
REPORT_FILE: str = "report.yaml"  # optional: without it, there is nothing to report

# How well a player knows an idea, from the first mention to having done it themselves.
LEVELS: tuple[str, ...] = ("heard", "understood", "used")
CHOICE_LETTERS: str = "abcde"  # how the report's choices are named

# A clue's fact inside a text: `[[coral, grown into the brass]]` (DECISIONS.md, 20).
CLUE_MARK: re.Pattern[str] = re.compile(r"\[\[(.+?)\]\]", re.DOTALL)
CLUE_ID: re.Pattern[str] = re.compile(r"C\d+")
# A white word: `|wcompass|n` (DECISIONS.md, 20).
WHITE_WORD: re.Pattern[str] = re.compile(r"\|w(.+?)\|n")
# In a character's reply, a white word is one of their topics, or a command to try, written
# out (`|waboard|n`, `|wexamine compass|n`): these are the words a command can start with.
COMMAND_WORDS: frozenset[str] = frozenset(
    "aboard ashore sail look examine x read use get take drop go map journal notebook ask "
    "up down begin help report".split()
)

LIMBO_ID: str = "limbo"
# The ship's position while she sails between two others (ship.yaml, `under_way`).
UNDER_WAY: str = "under_way"
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
# What a text teaches, for the players' notebooks: (idea id, level) pairs.
Teaching = tuple[tuple[str, str], ...]
# A position on the globe in whole degrees: (latitude, longitude), north and east positive.
# Longitude is counted from home, as on the Halcyon's chart.
Coords = tuple[int, int]

# `14 south`, `40 degrees W`, `14°S`: one number and the side of the world it lies on.
_COORD_PART: re.Pattern[str] = re.compile(
    r"(\d+)\s*(?:degrees?|deg|°)?\s*(north|south|east|west|n|s|e|w)\b"
)


def parse_coords(text: str) -> Coords | None:
    """
    `14 south 40 west`, `14S, 40W`, `latitude 14 degrees south, longitude 40 west`:
    the position it names, or None if it doesn't name exactly one latitude and one
    longitude. The order doesn't matter: north and south mark the latitude.
    """
    latitudes: list[int] = []
    longitudes: list[int] = []
    for number, side in _COORD_PART.findall(text.lower().replace("°", " ")):
        degrees: int = int(number)
        if side[0] in "ns":
            latitudes.append(degrees if side[0] == "n" else -degrees)
        else:
            longitudes.append(degrees if side[0] == "e" else -degrees)
    if len(latitudes) != 1 or len(longitudes) != 1:
        return None
    return latitudes[0], longitudes[0]


def coords_text(coords: Coords) -> str:
    """(-14, -40) -> `14 degrees South, 40 degrees West`."""
    latitude, longitude = coords
    north_south: str = "North" if latitude > 0 else "South"
    east_west: str = "East" if longitude > 0 else "West"
    return f"{abs(latitude)} degrees {north_south}, {abs(longitude)} degrees {east_west}"


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
    """
    A text that may reveal a clue (its fact marked `[[...]]` in it) and may teach ideas for
    the notebook.
    """

    text: str
    clue: str | None
    teaches: Teaching = ()


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
    """
    A way the ship can sail from a position: `sail <direction>`, `sail to <one of names>`,
    or `sail to <latitude> <longitude>` when the destination has `coords`.
    """

    direction: str
    to: str
    names: tuple[str, ...]  # normalised: `sail to the island` finds `island`
    order: str | None  # what the Ship says when she is given this order
    text: str  # shown at once, as she sets off
    passage: tuple[str, ...]  # shown one after another while she sails; the last one arrives
    teaches: Teaching = ()  # for the notebook: `used` for whoever gave the order


@dataclass(frozen=True)
class PositionSpec:
    """A place the ship can be: moored, at sea, or at anchor."""

    id: str
    name: str
    coords: Coords | None  # where it is on the globe, if anyone aboard can know
    orders: str | None  # what `sail` alone says here: the choices, in words
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

    def route_named(self, name: str) -> RouteSpec | None:
        """The route `sail to <name>` means (`the island`, `home`), or None."""
        word: str = normalise_words(name)
        for route in self.routes:
            if word in route.names:
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
class TaskSpec:
    """What the expedition is for: the top of the journal, from the very beginning."""

    title: str
    questions: tuple[str, ...]


@dataclass(frozen=True)
class ProofSpec:
    """One part of the proof of a report answer: any one of these clues will do."""

    clues: tuple[str, ...]
    missing: str  # the hint shown while none of them is in the journal


@dataclass(frozen=True)
class ChoiceSpec:
    """One choice of a report question. The right one has an `answer` and its `proof`."""

    text: str
    reply: str
    right: bool = False
    answer: str | None = None
    proof: tuple[ProofSpec, ...] = ()


@dataclass(frozen=True)
class QuestionSpec:
    """
    One question of the report: the task's question with the same number (`text`), and
    the choices players pick from.
    """

    id: str
    text: str
    choices: tuple[ChoiceSpec, ...]

    @property
    def right(self) -> ChoiceSpec:
        """The right choice (the content check makes sure there is exactly one)."""
        return next(choice for choice in self.choices if choice.right)


@dataclass(frozen=True)
class PageSpec:
    """One page of the epilogue."""

    title: str
    text: str


@dataclass(frozen=True)
class ReportSpec:
    """The report's questions, in the task's order, and the epilogue that follows them."""

    questions: tuple[QuestionSpec, ...]
    epilogue: tuple[PageSpec, ...]


@dataclass(frozen=True)
class AreaSpec:
    """A part of the notebook: Navigation, Nature..."""

    id: str
    title: str


@dataclass(frozen=True)
class IdeaSpec:
    """
    One idea for the notebook: how something in the world works. Its entry grows with each
    level the player reaches (`texts`, by level; a level may have none).
    """

    id: str
    area: str
    title: str
    texts: dict[str, str]

    def entry(self, level: str) -> str:
        """The notebook text up to this level: the texts of it and the levels before."""
        reached: tuple[str, ...] = LEVELS[: LEVELS.index(level) + 1]
        return " ".join(self.texts[name] for name in reached if name in self.texts)


@dataclass(frozen=True)
class StepSpec:
    """What reading or using a thing does at one ship position."""

    text: str
    clue: str | None
    needs: tuple[str, ...]  # flags or clue ids that must already be found
    sets: str | None  # a flag to remember for the expedition
    otherwise: str | None  # shown while `needs` isn't met
    teaches: Teaching = ()

    @property
    def reveal(self) -> Reveal:
        return Reveal(text=self.text, clue=self.clue, teaches=self.teaches)


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
    teaches: Teaching = ()


@dataclass(frozen=True)
class TopicSpec:
    """One thing a character can be asked about."""

    id: str
    words: tuple[str, ...]  # the id, its shared aliases and its own aliases, normalised
    reply: str
    stance: str
    clue: str | None
    truth: TruthSpec | None
    teaches: Teaching = ()
    hidden: bool = False  # found only by asking: never suggested, needs no white word


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
    image: str | None = None  # URL of their picture for the Focus pane, if there is one
    voice: str | None = None  # how they speak: for the writer and the AI characters (phase B)

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
    areas: dict[str, AreaSpec] = dataclass_field(default_factory=dict)
    ideas: dict[str, IdeaSpec] = dataclass_field(default_factory=dict)
    task: TaskSpec | None = None
    report: ReportSpec | None = None

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


def _teaches(data: dict[str, Any], where: str) -> Teaching:
    """`teaches: {latitude: understood}`: the ideas a text teaches, and how far."""
    found: dict[str, Any] = _mapping(data.get("teaches") or {}, f"{where}, teaches")
    teaching: list[tuple[str, str]] = []
    for idea_id, level in found.items():
        if level not in LEVELS:
            raise ContentError(
                f"{where}, teaches {idea_id}: the level must be one of {', '.join(LEVELS)}."
            )
        teaching.append((idea_id, str(level)))
    return tuple(teaching)


def _reveal(data: dict[str, Any], name: str, where: str) -> Reveal:
    """A text (in `name`), the clue it may reveal (in `clue`) and what it teaches."""
    return Reveal(
        text=_text(data, name, where),
        clue=_optional_text(data, "clue", where),
        teaches=_teaches(data, where),
    )


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
    passage: Any = data.get("passage") or []
    if not isinstance(passage, list) or not all(
        isinstance(line, str) and line.strip() for line in passage
    ):
        raise ContentError(f"{where}: `passage` must be a list of texts.")
    return RouteSpec(
        direction=direction,
        to=_text(data, "to", where),
        names=tuple(
            dict.fromkeys(
                normalise_words(name) for name in _words(data.get("names"), "names", where)
            )
        ),
        order=_optional_text(data, "order", where),
        text=_text(data, "text", where),
        passage=tuple(line.strip() for line in passage),
        teaches=_teaches(data, where),
    )


def _coords(data: dict[str, Any], where: str) -> Coords | None:
    text: str | None = _optional_text(data, "coords", where)
    if text is None:
        return None
    coords: Coords | None = parse_coords(text)
    if coords is None:
        raise ContentError(f"{where}: `coords` must be like `14 S, 40 W`, not {text!r}.")
    return coords


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
        coords=_coords(data, where),
        orders=_optional_text(data, "orders", where),
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
        needs=needs,
        reply=_text(data, "reply", where),
        clue=_optional_text(data, "clue", where),
        teaches=_teaches(data, where),
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
        teaches=_teaches(data, where),
        hidden=_flag(data, "hidden", where),
    )


def _flag(data: dict[str, Any], name: str, where: str) -> bool:
    value: Any = data.get(name, False)
    if not isinstance(value, bool):
        raise ContentError(f"{where}: `{name}` must be true or false.")
    return value


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
        image=_optional_text(data, "image", where),
        voice=_optional_text(data, "voice", where),
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


def _task(data: dict[str, Any]) -> TaskSpec | None:
    if data.get("task") is None:
        return None
    where: str = f"{CLUES_FILE}, task"
    item: dict[str, Any] = _mapping(data["task"], where)
    questions: Any = item.get("questions") or []
    if not isinstance(questions, list) or not all(
        isinstance(q, str) and q.strip() for q in questions
    ):
        raise ContentError(f"{where}: `questions` must be a list of texts.")
    return TaskSpec(
        title=_text(item, "title", where), questions=tuple(q.strip() for q in questions)
    )


def _proof(value: Any, where: str) -> ProofSpec:
    item: dict[str, Any] = _mapping(value, where)
    clues: tuple[str, ...] = _words(item.get("clues"), "clues", where)
    if not clues:
        raise ContentError(f"{where}: `clues` must name at least one clue.")
    return ProofSpec(clues=clues, missing=_text(item, "missing", where))


def _choice(value: Any, where: str) -> ChoiceSpec:
    item: dict[str, Any] = _mapping(value, where)
    right: bool = _flag(item, "right", where)
    proof_data: Any = item.get("proof") or []
    if not isinstance(proof_data, list):
        raise ContentError(f"{where}: `proof` must be a list.")
    proof: tuple[ProofSpec, ...] = tuple(
        _proof(part, f"{where}, proof {number}") for number, part in enumerate(proof_data, 1)
    )
    if right and not proof:
        raise ContentError(f"{where}: the right choice needs a `proof`.")
    if not right and (proof or item.get("answer") is not None):
        raise ContentError(f"{where}: only the right choice has an `answer` and a `proof`.")
    return ChoiceSpec(
        text=_text(item, "text", where),
        reply=_text(item, "reply", where),
        right=right,
        answer=_text(item, "answer", where) if right else None,
        proof=proof,
    )


def _report(data: dict[str, Any], task: TaskSpec | None) -> ReportSpec | None:
    if not data:
        return None
    if task is None:
        raise ContentError(f"{REPORT_FILE}: the report needs the task in {CLUES_FILE}.")
    questions_data: Any = data.get("questions") or []
    if not isinstance(questions_data, list) or len(questions_data) != len(task.questions):
        raise ContentError(
            f"{REPORT_FILE}: `questions` must be a list with one entry for each of the "
            f"task's {len(task.questions)} questions, in the same order."
        )
    questions: list[QuestionSpec] = []
    for number, value in enumerate(questions_data, start=1):
        where: str = f"{REPORT_FILE}, question {number}"
        item: dict[str, Any] = _mapping(value, where)
        question_id: str = _text(item, "id", where)
        where = f"{REPORT_FILE}, question {question_id}"
        choices_data: Any = item.get("choices") or []
        if not isinstance(choices_data, list) or not 2 <= len(choices_data) <= 5:
            raise ContentError(f"{where}: `choices` must be a list of two to five.")
        choices: tuple[ChoiceSpec, ...] = tuple(
            _choice(choice, f"{where}, choice {CHOICE_LETTERS[index]}")
            for index, choice in enumerate(choices_data)
        )
        if sum(choice.right for choice in choices) != 1:
            raise ContentError(f"{where}: exactly one choice must have `right: true`.")
        questions.append(
            QuestionSpec(id=question_id, text=task.questions[number - 1], choices=choices)
        )
    if len({question.id for question in questions}) != len(questions):
        raise ContentError(f"{REPORT_FILE}: two questions have the same id.")
    pages_data: Any = data.get("epilogue") or []
    if not isinstance(pages_data, list) or not pages_data:
        raise ContentError(f"{REPORT_FILE}: `epilogue` must be a list of pages.")
    pages: list[PageSpec] = []
    for number, value in enumerate(pages_data, start=1):
        where = f"{REPORT_FILE}, epilogue page {number}"
        page: dict[str, Any] = _mapping(value, where)
        pages.append(PageSpec(title=_text(page, "title", where), text=_text(page, "text", where)))
    return ReportSpec(questions=tuple(questions), epilogue=tuple(pages))


def _ideas(data: dict[str, Any]) -> tuple[dict[str, AreaSpec], dict[str, IdeaSpec]]:
    areas_data: dict[str, Any] = _mapping(data.get("areas") or {}, f"{IDEAS_FILE}, areas")
    areas: dict[str, AreaSpec] = {}
    for area_id, value in areas_data.items():
        where: str = f"{IDEAS_FILE}, area {area_id}"
        areas[area_id] = AreaSpec(id=area_id, title=_text(_mapping(value, where), "title", where))
    ideas_data: dict[str, Any] = _mapping(data.get("ideas") or {}, f"{IDEAS_FILE}, ideas")
    ideas: dict[str, IdeaSpec] = {}
    for idea_id, value in ideas_data.items():
        where = f"{IDEAS_FILE}, idea {idea_id}"
        item: dict[str, Any] = _mapping(value, where)
        area: str = _text(item, "area", where)
        if area not in areas:
            raise ContentError(f"{where}: unknown area {area!r}.")
        texts: dict[str, str] = {
            level: _text(item, level, where) for level in LEVELS if item.get(level) is not None
        }
        if not texts:
            raise ContentError(f"{where}: needs a text for at least one of {', '.join(LEVELS)}.")
        ideas[idea_id] = IdeaSpec(
            id=idea_id, area=area, title=_text(item, "title", where), texts=texts
        )
    return areas, ideas


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
        teaches=_teaches(data, where),
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
            if route.to not in positions or route.to == UNDER_WAY:
                raise ContentError(
                    f"{where}, route {route.direction}: unknown position {route.to!r}."
                )
            if not route.passage:
                raise ContentError(f"{where}, route {route.direction}: `passage` is missing.")
    under_way: PositionSpec | None = positions.get(UNDER_WAY)
    if under_way is None or under_way.routes or under_way.ashore:
        raise ContentError(
            f"{SHIP_FILE}: the position {UNDER_WAY!r} (the ship between two positions) is "
            "missing, or has routes or `ashore`."
        )

    _check_characters(content)
    _check_things(content)
    _check_clue_marks(content)
    _check_teachings(content)
    _check_report(content)


def _check_report(content: Content) -> None:
    """Every clue a report answer needs as proof exists."""
    if content.report is None:
        return
    for question in content.report.questions:
        for number, part in enumerate(question.right.proof, start=1):
            for clue in part.clues:
                if clue not in content.clues:
                    raise ContentError(
                        f"{REPORT_FILE}, question {question.id}, proof {number}: "
                        f"unknown clue {clue!r}."
                    )


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
        if position.orders:
            texts.append((f"{where}, orders", position.orders, None))
        for route in position.routes:
            route_where: str = f"{where}, route {route.direction}"
            texts.append((route_where, route.text, None))
            if route.order:
                texts.append((f"{route_where}, order", route.order, None))
            for number, line in enumerate(route.passage, start=1):
                texts.append((f"{route_where}, passage {number}", line, None))
        for detail in position.details.values():
            texts.extend(_look_texts(f"{where}, detail {detail.id}", detail))
    if content.task is not None:
        texts.append((f"{CLUES_FILE}, task", content.task.title, None))
        for number, question in enumerate(content.task.questions, start=1):
            texts.append((f"{CLUES_FILE}, task, question {number}", question, None))
    if content.report is not None:
        for asked in content.report.questions:
            for index, choice in enumerate(asked.choices):
                where = f"{REPORT_FILE}, question {asked.id}, choice {CHOICE_LETTERS[index]}"
                texts.append((where, choice.text, None))
                texts.append((f"{where}, reply", choice.reply, None))
                if choice.answer is not None:
                    texts.append((f"{where}, answer", choice.answer, None))
                for number, part in enumerate(choice.proof, start=1):
                    texts.append((f"{where}, proof {number}", part.missing, None))
        for number, page in enumerate(content.report.epilogue, start=1):
            texts.append((f"{REPORT_FILE}, epilogue page {number}", page.text, None))
    for idea in content.ideas.values():
        for level, text in idea.texts.items():
            texts.append((f"{IDEAS_FILE}, idea {idea.id}, {level}", text, None))
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


def _look_teachings(where: str, look: LookSpec) -> list[tuple[str, Teaching]]:
    found: list[tuple[str, Teaching]] = [(where, look.desc.teaches)]
    if look.close is not None:
        found.append((f"{where}, close", look.close.teaches))
    found.extend((f"{where}, with {key}", extra.teaches) for key, extra in look.extras.items())
    return found


def all_teachings(content: Content) -> list[tuple[str, Teaching]]:
    """Every text that may teach ideas, as (where it is, what it teaches)."""
    found: list[tuple[str, Teaching]] = []
    for place in content.places.values():
        for detail in place.details.values():
            found.extend(_look_teachings(f"place {place.id}, detail {detail.id}", detail))
    for position in content.positions.values():
        for detail in position.details.values():
            found.extend(_look_teachings(f"position {position.id}, detail {detail.id}", detail))
    for thing in content.things.values():
        where: str = f"{THINGS_FILE}, {thing.id}"
        found.extend(_look_teachings(where, thing.look))
        for verb, action in (("read", thing.read), ("use", thing.use)):
            if action is None:
                continue
            found.append((f"{where}, {verb}", action.default.teaches))
            found.extend(
                (f"{where}, {verb}, at {key}", step.teaches) for key, step in action.at.items()
            )
    for position in content.positions.values():
        found.extend(
            (f"{SHIP_FILE}, position {position.id}, route {route.direction}", route.teaches)
            for route in position.routes
        )
    for character in content.characters.values():
        for topic in character.topics.values():
            where = f"{CHARACTERS_FILE}, {character.id}, topic {topic.id}"
            found.append((where, topic.teaches))
            if topic.truth is not None:
                found.append((f"{where}, truth", topic.truth.teaches))
    return found


def _check_teachings(content: Content) -> None:
    """Every `teaches` names a known idea, at a level the idea has a text for."""
    for where, teaching in all_teachings(content):
        for idea_id, level in teaching:
            idea: IdeaSpec | None = content.ideas.get(idea_id)
            if idea is None:
                raise ContentError(f"{where}: teaches unknown idea {idea_id!r} ({IDEAS_FILE}).")
            if level not in idea.texts:
                raise ContentError(
                    f"{where}: teaches {idea_id} at level {level!r}, which has no text."
                )


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
        _check_white_words(character)


def _character_texts(character: CharacterSpec) -> list[tuple[str, str]]:
    """Everything a character says, as (which text, the text)."""
    texts: list[tuple[str, str]] = [
        ("greeting", character.greeting),
        ("fallback", character.fallback),
    ]
    for topic in character.topics.values():
        texts.append((f"topic {topic.id}", topic.reply))
        if topic.truth is not None:
            texts.append((f"topic {topic.id}, truth", topic.truth.reply))
    return texts


def _check_white_words(character: CharacterSpec) -> None:
    """
    In what a character says, a white word is one of their own topics or a command, never a
    word they can't be asked about. And every topic can be found: suggested, white in one of
    their texts, or deliberately `hidden`.
    """
    where: str = f"{CHARACTERS_FILE}, {character.id}"
    reachable: set[str] = set(character.suggest)
    for which, text in _character_texts(character):
        for word in WHITE_WORD.findall(text):
            topic: TopicSpec | None = character.topic(word)
            if topic is not None:
                reachable.add(topic.id)
                continue
            first: str = word.split()[0].lower() if word.split() else ""
            if first not in COMMAND_WORDS:
                raise ContentError(
                    f"{where}, {which}: |w{word}|n is white, but it isn't one of "
                    f"{character.name}'s topics or a command. Make it plain, add the topic, "
                    "or write the whole command."
                )
    for topic in character.topics.values():
        if topic.id not in reachable and not topic.hidden:
            raise ContentError(
                f"{where}, topic {topic.id}: players can't find it. Suggest it, mark it white "
                "in one of their replies, or set `hidden: true`."
            )


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
    ideas_data: dict[str, Any] = (
        _read_yaml(directory, IDEAS_FILE) if (directory / IDEAS_FILE).exists() else {}
    )
    areas, ideas = _ideas(ideas_data)
    report_data: dict[str, Any] = (
        _read_yaml(directory, REPORT_FILE) if (directory / REPORT_FILE).exists() else {}
    )
    task: TaskSpec | None = _task(clues_data)

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
        areas=areas,
        ideas=ideas,
        task=task,
        report=_report(report_data, task),
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
