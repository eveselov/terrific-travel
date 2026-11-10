"""
Smoke tests for the game's typeclasses.

Run from the game directory with `uv run evennia test --settings settings.py .`
"""

from evennia.utils.test_resources import EvenniaTest

from typeclasses.characters import Character
from typeclasses.rooms import Room


class TestTypeclassesSmoke(EvenniaTest):
    """Checks that the test fixtures are built from this game's own typeclasses."""

    character_typeclass: type[Character] = Character
    room_typeclass: type[Room] = Room

    def test_character_is_in_room(self) -> None:
        self.assertIsInstance(self.char1, Character)
        self.assertIsInstance(self.room1, Room)
        self.assertEqual(self.char1.location, self.room1)
