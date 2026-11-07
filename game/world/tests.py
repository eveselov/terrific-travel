"""
Tests for the picture maps and the room visuals.

Run from the game directory with `uv run evennia test --settings settings.py .`
"""

from typing import Any
from unittest.mock import MagicMock, patch

from evennia.utils.test_resources import EvenniaTest

from typeclasses.characters import Character
from typeclasses.rooms import Room
from world.maps import (
    MAP_TAG_CATEGORY,
    MapPlace,
    PictureMap,
    all_maps,
    discover_maps,
    places_on_map,
    render_map_html,
)

TEST_MAP: PictureMap = PictureMap(
    key="test_map", title="Test map", image_url="/static/test/map.png", width=100, height=50
)


def sent(mock_msg: MagicMock, cmdname: str) -> list[Any]:
    """The values of every `msg(<cmdname>=...)` call on a mocked msg method."""
    return [call.kwargs[cmdname] for call in mock_msg.call_args_list if cmdname in call.kwargs]


class TestMapDiscovery(EvenniaTest):
    def test_discovered_maps_are_picture_maps(self) -> None:
        found: dict[str, PictureMap] = discover_maps()
        for key, picture_map in found.items():
            self.assertIsInstance(picture_map, PictureMap)
            self.assertEqual(key, picture_map.key)


class TestRenderMap(EvenniaTest):
    def test_labels_are_escaped(self) -> None:
        places: list[MapPlace] = [MapPlace(label="<b>Fort</b>", x=10, y=20, is_here=False)]
        html: str = render_map_html(TEST_MAP, places)
        self.assertIn("&lt;b&gt;Fort&lt;/b&gt;", html)
        self.assertNotIn("<b>Fort</b>", html)

    def test_marker_only_on_current_place(self) -> None:
        places: list[MapPlace] = [
            MapPlace(label="A", x=10, y=20, is_here=True),
            MapPlace(label="B", x=30, y=40, is_here=False),
        ]
        html: str = render_map_html(TEST_MAP, places)
        self.assertEqual(html.count("You are here"), 1)
        self.assertIn(TEST_MAP.image_url, html)


class TestRoomVisuals(EvenniaTest):
    character_typeclass: type[Character] = Character
    room_typeclass: type[Room] = Room

    def setUp(self) -> None:
        super().setUp()
        # Register the test map for this test only.
        maps_patch: Any = patch.dict(all_maps(), {TEST_MAP.key: TEST_MAP})
        maps_patch.start()
        self.addCleanup(maps_patch.stop)
        for room, pos in ((self.room1, (10, 20)), (self.room2, (30, 40))):
            room.tags.add(TEST_MAP.key, category=MAP_TAG_CATEGORY)
            room.db.map_pos = pos
        self.room2.db.image = "/static/test/room2.png"

    def test_places_on_map_marks_here(self) -> None:
        places: list[MapPlace] = places_on_map(TEST_MAP, self.room2)
        self.assertEqual([(p.x, p.y) for p in places if p.is_here], [(30, 40)])
        self.assertEqual(len(places), 2)

    def test_move_sends_map_and_picture(self) -> None:
        with patch.object(self.char1, "msg") as mock_msg:
            self.char1.move_to(self.room2)
        maps: list[Any] = sent(mock_msg, "map")
        self.assertEqual(len(maps), 1)
        self.assertIn("You are here", maps[0])
        self.assertEqual(
            sent(mock_msg, "room_image"), [(("/static/test/room2.png",), {"alt": "Room2"})]
        )

    def test_room_without_map_clears_the_pane(self) -> None:
        self.room2.tags.remove(TEST_MAP.key, category=MAP_TAG_CATEGORY)
        self.room2.db.image = None
        with patch.object(self.char1, "msg") as mock_msg:
            self.char1.move_to(self.room2)
        self.assertIn("No map", sent(mock_msg, "map")[0])
        self.assertEqual(sent(mock_msg, "room_image"), [])
