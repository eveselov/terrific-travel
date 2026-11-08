"""
Tests for the map demo builder.

Run from the game directory with `uv run evennia test --settings settings.py .`
"""

from evennia.utils.batchprocessors import BATCHCODE
from evennia.utils.test_resources import EvenniaTest

from typeclasses.characters import Character
from typeclasses.rooms import Room
from world.map_demo.builder import (
    DEMO_EXITS,
    DEMO_ROOMS,
    build_map_demo,
    demo_objects,
    remove_map_demo,
)
from world.maps import get_map
from world.picture_maps.demo_sea import DEMO_SEA

# The demo's rooms and exits, plus the entrance and the way back.
DEMO_OBJECT_COUNT: int = len(DEMO_ROOMS) + len(DEMO_EXITS) + 2


class TestMapDemo(EvenniaTest):
    character_typeclass: type[Character] = Character
    room_typeclass: type[Room] = Room

    def test_demo_map_is_discovered(self) -> None:
        self.assertEqual(get_map(DEMO_SEA.key), DEMO_SEA)

    def test_build_and_remove(self) -> None:
        rooms: list[Room] = build_map_demo(self.char1)
        self.assertEqual(len(rooms), len(DEMO_ROOMS))
        self.assertEqual(len(demo_objects()), DEMO_OBJECT_COUNT)
        self.assertEqual([ex.key for ex in self.room1.exits if ex.key == "harbour"], ["harbour"])
        self.assertTrue(all(room.picture_map == DEMO_SEA for room in rooms))

        self.assertEqual(build_map_demo(self.char1), [], "a second build must do nothing")

        remove_map_demo(self.char1)
        self.assertEqual(demo_objects(), [])
        self.assertEqual([ex for ex in self.room1.exits if ex.key == "harbour"], [])

    def test_batchcode_files_run(self) -> None:
        """The batch files work in Evennia's real batchcode processor, as `batchcode` runs them."""
        for pythonpath in ("map_demo.build", "map_demo.remove"):
            blocks: list[str] = BATCHCODE.parse_file(pythonpath)
            for block in blocks:
                error: str | None = BATCHCODE.code_exec(block, extra_environ={"caller": self.char1})
                self.assertIsNone(error, error)
            if pythonpath == "map_demo.build":
                self.assertEqual(len(demo_objects()), DEMO_OBJECT_COUNT)
        self.assertEqual(demo_objects(), [])
