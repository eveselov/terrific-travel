"""
Picture maps for the web client's Map pane.

A picture map is a static background image with the places on it drawn on top as labels.

- **Maps** are defined in modules of the `world.picture_maps` package. Each such module has a
  `PICTURE_MAPS: list[PictureMap]`. They are found automatically the first time a map is
  looked up, so a game adds a map by adding a module there, not by editing this one.
- **Places** are rooms. A room is on a map when it has a tag with the map's key in the
  `MAP_TAG_CATEGORY` category, and its position on the picture is its `map_pos` attribute.
  So builders can add places to a map from inside the game.

The map is rendered on the server as an inline SVG string and sent to the web client as a
`map` message (see `web/static/webclient/js/plugins/picture_map.js`). Telnet clients never
see it; they get only the text.
"""

import importlib
import pkgutil
from dataclasses import dataclass
from html import escape
from types import ModuleType
from typing import Any

from evennia.utils.search import search_tag

MAP_TAG_CATEGORY: str = "map"
PICTURE_MAPS_PACKAGE: str = "world.picture_maps"


@dataclass(frozen=True)
class PictureMap:
    """A static map picture. Coordinates on it are in picture pixels, (0, 0) at top left."""

    key: str
    title: str
    image_url: str
    width: int
    height: int


@dataclass(frozen=True)
class MapPlace:
    """One labelled place to draw on a map."""

    label: str
    x: int
    y: int
    is_here: bool


_maps: dict[str, PictureMap] | None = None


def discover_maps(package_name: str = PICTURE_MAPS_PACKAGE) -> dict[str, PictureMap]:
    """Collect `PICTURE_MAPS` from every module in a package, keyed by map key."""
    package: ModuleType = importlib.import_module(package_name)
    found: dict[str, PictureMap] = {}
    for module_info in pkgutil.iter_modules(package.__path__):
        module: ModuleType = importlib.import_module(f"{package_name}.{module_info.name}")
        picture_maps: list[PictureMap] = getattr(module, "PICTURE_MAPS", [])
        for picture_map in picture_maps:
            if picture_map.key in found:
                raise ValueError(f"Picture map key {picture_map.key!r} is defined twice.")
            found[picture_map.key] = picture_map
    return found


def all_maps() -> dict[str, PictureMap]:
    """All known picture maps, keyed by map key (discovered once, then cached)."""
    global _maps
    if _maps is None:
        _maps = discover_maps()
    return _maps


def get_map(key: str) -> PictureMap | None:
    """Return the picture map with this key, or None if there is none."""
    return all_maps().get(key)


def map_pos_of(room: Any) -> tuple[int, int] | None:
    """Return a room's `map_pos` attribute as an (x, y) pair, or None if it has none."""
    pos: Any = room.attributes.get("map_pos")
    if pos is None:
        return None
    x, y = pos
    return int(x), int(y)


def places_on_map(picture_map: PictureMap, here: Any) -> list[MapPlace]:
    """Collect the labelled places of a map, marking the one that is `here`."""
    places: list[MapPlace] = []
    for room in search_tag(picture_map.key, category=MAP_TAG_CATEGORY):
        pos: tuple[int, int] | None = map_pos_of(room)
        if pos is None:
            continue
        places.append(MapPlace(label=room.key, x=pos[0], y=pos[1], is_here=room == here))
    places.sort(key=lambda place: place.label)
    return places


def _label_svg(x: int, y: int, text: str, size: int, weight: str) -> str:
    """A text label with a dark outline, so it stays readable on any background."""
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="{size}" font-weight="{weight}" fill="#fffbe8" stroke="#1d2b36" '
        f'stroke-width="4" paint-order="stroke">{escape(text)}</text>'
    )


def _place_svg(place: MapPlace) -> str:
    """The dot and label for one place, with the 'you are here' marker if it applies."""
    parts: list[str] = []
    if place.is_here:
        parts.append(
            f'<circle cx="{place.x}" cy="{place.y}" r="22" fill="none" stroke="#e63946" '
            'stroke-width="5"/>'
        )
        parts.append(_label_svg(place.x, place.y + 52, "You are here", 22, "bold"))
    parts.append(
        f'<circle cx="{place.x}" cy="{place.y}" r="9" fill="#e63946" stroke="#fffbe8" '
        'stroke-width="3"/>'
    )
    parts.append(_label_svg(place.x, place.y - 22, place.label, 26, "bold"))
    return "".join(parts)


def render_map_html(picture_map: PictureMap, places: list[MapPlace]) -> str:
    """Render the map picture with its places as an inline SVG inside a small HTML block."""
    width: int = picture_map.width
    height: int = picture_map.height
    places_svg: str = "".join(_place_svg(place) for place in places)
    return (
        '<div class="tt-map">'
        f'<div class="tt-map-title">{escape(picture_map.title)}</div>'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{escape(picture_map.title)}" '
        'style="width:100%;height:auto;display:block">'
        f'<image href="{escape(picture_map.image_url)}" x="0" y="0" '
        f'width="{width}" height="{height}"/>'
        f"{places_svg}"
        "</svg></div>"
    )


def render_no_map_html() -> str:
    """What the Map pane shows in a room that is on no map."""
    return '<div class="tt-map"><div class="tt-map-title">No map for this place.</div></div>'
