"""
Maps for the web client's Map pane, and their text version for the `map` command.

Copied from the playground (`game/world/maps.py`) and changed for this game:

- **Maps** come from `world/content/maps.yaml`, not from Python modules.
- **Places** are rooms. A room is on a map when it has a tag with the map's key in the
  `MAP_TAG_CATEGORY` category, and its position on the picture is its `map_pos` attribute.
  The world builder sets both from `places.yaml`.
- **The ship** is drawn too, wherever she is: on the port plan when moored, on the sea chart
  at sea, on the island map at anchor. Her two rooms show the map she is on, with her marker
  as "You are here", plus a small side view of the ship in a corner of the map showing which
  of her rooms (Deck or Cabin) you are in. On the sea chart her track is a dashed line.

The map is rendered on the server as an inline SVG string and sent to the web client as a
`map` message (see `web/static/webclient/js/plugins/panes.js`). Telnet clients never see it;
the `map` command (`text_map`) gives the same information in words.
"""

from dataclasses import dataclass, field
from html import escape
from typing import Any

from evennia.utils.search import search_tag

from world.content import Content, MapSpec, Point, PositionSpec, load_content
from world.expedition import current_position, get_expedition

MAP_TAG_CATEGORY: str = "map"
SHIP_LABEL: str = "Your ship"


@dataclass(frozen=True)
class MapLocation:
    """Where something is: which map, and where on its picture."""

    map_key: str
    pos: Point


@dataclass(frozen=True)
class MapPlace:
    """One labelled place to draw on a map."""

    label: str
    x: int
    y: int
    is_here: bool
    is_ship: bool = False


@dataclass(frozen=True)
class ShipRoomMark:
    """One of the ship's rooms in the "aboard" inset."""

    label: str
    kind: str  # "deck" or "cabin"
    is_here: bool


@dataclass(frozen=True)
class MapView:
    """Everything one map shows to one viewer."""

    picture_map: MapSpec
    places: list[MapPlace]
    track: list[Point]
    track_names: list[str]
    aboard: list[ShipRoomMark] = field(default_factory=list)  # empty unless aboard


def room_map_location(room: Any) -> MapLocation | None:
    """A room's map and position, from its map tag and `map_pos` attribute."""
    keys: list[str] = room.tags.get(category=MAP_TAG_CATEGORY, return_list=True)
    pos: Any = room.attributes.get("map_pos")
    if not keys or pos is None:
        return None
    x, y = pos
    return MapLocation(map_key=keys[0], pos=(int(x), int(y)))


def ship_map_location(position: PositionSpec, content: Content) -> MapLocation:
    """Where the ship is drawn: on the position's own map if it has one, else the sea chart."""
    if position.map is not None and position.map_pos is not None:
        return MapLocation(map_key=position.map, pos=position.map_pos)
    return MapLocation(map_key=content.sea_chart, pos=position.chart_pos)


def places_on_map(map_key: str, here: Any) -> list[MapPlace]:
    """The rooms on a map, marking the one that is `here`."""
    places: list[MapPlace] = []
    for room in search_tag(map_key, category=MAP_TAG_CATEGORY):
        location: MapLocation | None = room_map_location(room)
        if location is None:
            continue
        x, y = location.pos
        places.append(MapPlace(label=room.key, x=x, y=y, is_here=room == here))
    places.sort(key=lambda place: place.label)
    return places


def build_map_view(here: Any, location: MapLocation, ship_kind: str | None) -> MapView | None:
    """
    The map a viewer sees from `here`, a room at `location`.

    `ship_kind` is the kind of ship's room `here` is ("deck" or "cabin"), or None ashore.
    Aboard, the ship's marker is "You are here" and the map gets the ship inset.
    """
    content: Content = load_content()
    picture_map: MapSpec | None = content.maps.get(location.map_key)
    if picture_map is None:
        return None
    places: list[MapPlace] = places_on_map(picture_map.key, here)
    ship: MapLocation = ship_map_location(current_position(), content)
    if ship.map_key == picture_map.key:
        x, y = ship.pos
        label: str = SHIP_LABEL
        if ship_kind is not None:
            label = f"{SHIP_LABEL} ({content.place_of_kind(ship_kind).name})"
        places.append(MapPlace(label=label, x=x, y=y, is_here=ship_kind is not None, is_ship=True))
    aboard: list[ShipRoomMark] = []
    if ship_kind is not None:
        aboard = [
            ShipRoomMark(
                label=content.place_of_kind(kind).name, kind=kind, is_here=kind == ship_kind
            )
            for kind in ("deck", "cabin")
        ]
    track: list[Point] = []
    track_names: list[str] = []
    if picture_map.key == content.sea_chart:
        for position_id in get_expedition().track:
            position: PositionSpec | None = content.positions.get(position_id)
            if position is not None:
                track.append(position.chart_pos)
                track_names.append(position.name)
    return MapView(
        picture_map=picture_map,
        places=places,
        track=track,
        track_names=track_names,
        aboard=aboard,
    )


# --- Web client (SVG) -----------------------------------------------------------------


def _label_svg(x: int, y: int, text: str, size: int, weight: str) -> str:
    """A text label with a dark outline, so it stays readable on any background."""
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="{size}" font-weight="{weight}" fill="#fffbe8" stroke="#1d2b36" '
        f'stroke-width="4" paint-order="stroke">{escape(text)}</text>'
    )


def _place_svg(place: MapPlace) -> str:
    """The dot (or ship marker) and label for one place, with "You are here" if it applies."""
    parts: list[str] = []
    if place.is_here:
        parts.append(
            f'<circle cx="{place.x}" cy="{place.y}" r="24" fill="none" stroke="#e63946" '
            'stroke-width="5"/>'
        )
        parts.append(_label_svg(place.x, place.y + 54, "You are here", 22, "bold"))
    if place.is_ship:
        # A small hull with a sail, centred on the position.
        parts.append(
            f'<g transform="translate({place.x},{place.y})">'
            '<path d="M -16 4 L 16 4 L 10 14 L -10 14 Z" fill="#7a4a21" stroke="#fffbe8" '
            'stroke-width="2"/>'
            '<path d="M -1 2 L -1 -18 L 12 0 Z" fill="#fffbe8" stroke="#1d2b36" '
            'stroke-width="2"/></g>'
        )
    else:
        parts.append(
            f'<circle cx="{place.x}" cy="{place.y}" r="9" fill="#e63946" stroke="#fffbe8" '
            'stroke-width="3"/>'
        )
    parts.append(_label_svg(place.x, place.y - 26, place.label, 26, "bold"))
    return "".join(parts)


def _track_svg(track: list[Point]) -> str:
    """The ship's track as a dashed line."""
    if len(track) < 2:
        return ""
    points: str = " ".join(f"{x},{y}" for x, y in track)
    return (
        f'<polyline points="{points}" fill="none" stroke="#7a4a21" stroke-width="4" '
        'stroke-dasharray="12 10" stroke-linecap="round" stroke-linejoin="round"/>'
    )


# Where each ship's room is in the inset's side view (inset units: 260 x 160).
_INSET_ROOM_POS: dict[str, Point] = {"deck": (70, 62), "cabin": (95, 112)}


def _aboard_inset_svg(view: MapView) -> str:
    """A small side view of the ship in the bottom right corner, marking your room."""
    if not view.aboard:
        return ""
    scale: float = view.picture_map.width / 1000
    width: float = 260 * scale
    height: float = 160 * scale
    x: float = view.picture_map.width - width - 16 * scale
    y: float = view.picture_map.height - height - 16 * scale
    parts: list[str] = [
        f'<g transform="translate({x:.0f},{y:.0f}) scale({scale:.3f})">',
        '<rect width="260" height="160" rx="12" fill="#f3e6c4" fill-opacity="0.92" '
        'stroke="#7a4a21" stroke-width="4"/>',
        # Mast and sail, then the hull with the deck as its top edge.
        '<path d="M 175 72 L 175 14" stroke="#3b2a14" stroke-width="4"/>',
        '<path d="M 178 18 L 178 64 L 225 64 Z" fill="#fffbe8" stroke="#3b2a14" stroke-width="2"/>',
        '<path d="M 20 72 L 240 72 L 212 144 L 48 144 Z" fill="#b98b5e" stroke="#3b2a14" '
        'stroke-width="4"/>',
    ]
    for mark in view.aboard:
        mx, my = _INSET_ROOM_POS.get(mark.kind, (130, 100))
        if mark.is_here:
            parts.append(
                f'<circle cx="{mx}" cy="{my}" r="15" fill="none" stroke="#e63946" '
                'stroke-width="4"/>'
            )
        parts.append(
            f'<circle cx="{mx}" cy="{my}" r="7" fill="#e63946" stroke="#fffbe8" stroke-width="2"/>'
        )
        weight: str = "bold" if mark.is_here else "normal"
        parts.append(
            f'<text x="{mx + 24}" y="{my + 7}" font-family="Georgia, serif" font-size="22" '
            f'font-weight="{weight}" fill="#1d2b36">{escape(mark.label)}</text>'
        )
    parts.append("</g>")
    return "".join(parts)


def render_map_html(view: MapView) -> str:
    """Render a map view as an inline SVG inside a small HTML block."""
    picture_map: MapSpec = view.picture_map
    width: int = picture_map.width
    height: int = picture_map.height
    # The current place is drawn last, so its marker is on top.
    ordered: list[MapPlace] = sorted(view.places, key=lambda place: place.is_here)
    return (
        '<div class="pi-map">'
        f'<div class="pi-pane-title">{escape(picture_map.title)}</div>'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{escape(picture_map.title)}" '
        'class="pi-picture">'
        f'<image href="{escape(picture_map.image)}" x="0" y="0" '
        f'width="{width}" height="{height}"/>'
        f"{_track_svg(view.track)}"
        f"{''.join(_place_svg(place) for place in ordered)}"
        f"{_aboard_inset_svg(view)}"
        "</svg></div>"
    )


def render_no_map_html() -> str:
    """What the Map pane shows in a place that is on no map."""
    return '<div class="pi-map"><div class="pi-pane-title">No map for this place.</div></div>'


# --- Telnet (text) --------------------------------------------------------------------


def text_map(view: MapView | None) -> str:
    """The map in words, for players without the web client (and for everyone else too)."""
    if view is None:
        return "There is no map of this place."
    lines: list[str] = [f"|wMap: {view.picture_map.title}|n"]
    here: list[str] = [place.label for place in view.places if place.is_here]
    others: list[str] = [place.label for place in view.places if not place.is_here]
    if here:
        lines.append(f"You are here: {here[0]}.")
    if others:
        lines.append(f"Also on this map: {', '.join(others)}.")
    if len(view.track_names) > 1:
        lines.append(f"Your ship's track: {' -> '.join(view.track_names)}.")
    return "\n".join(lines)
