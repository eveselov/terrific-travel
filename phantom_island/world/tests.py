"""
Tests for the content files, the world builder, the ship, and the Map and Focus panes.

Run from the game directory with `uv run evennia test --settings settings.py .`
"""

from collections import deque
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

from evennia.utils.test_resources import EvenniaTest

from typeclasses.characters import Character
from typeclasses.exits import Exit
from typeclasses.rooms import Deck, Room, ShipRoom
from world.builder import build_world
from world.content import (
    CONTENT_DIR,
    LIMBO_ID,
    MAPS_FILE,
    PLACES_FILE,
    SHIP_FILE,
    Content,
    ContentError,
    load_content,
    read_content,
)
from world.expedition import current_position, get_expedition
from world.focus import render_focus_html
from world.maps import SHIP_LABEL, MapPlace, MapView, render_map_html
from world.places import find_ship_exit
from world.ship import ABOARD, ASHORE, moor_ship, normalise_direction, sail

PORT_PLACES: set[str] = {"office", "quay", "market"}
SHIP_PLACES: set[str] = {"deck", "cabin"}
ISLAND_PLACES: set[str] = {"beach", "village", "reef", "forest", "spring", "hilltop", "cove"}


def sent(mock_msg: MagicMock, cmdname: str) -> list[Any]:
    """The values of every `msg(<cmdname>=...)` call on a mocked msg method."""
    return [call.kwargs[cmdname] for call in mock_msg.call_args_list if cmdname in call.kwargs]


def texts(mock_msg: MagicMock) -> str:
    """Everything sent as plain text to a mocked msg method, joined."""
    parts: list[str] = []
    for call in mock_msg.call_args_list:
        text: Any = call.args[0] if call.args else call.kwargs.get("text")
        if isinstance(text, tuple):
            text = text[0]
        if text is not None:
            parts.append(str(text))
    return "\n".join(parts)


class TestContent(TestCase):
    """The content files themselves, without a database."""

    def test_the_twelve_places_and_the_prologue(self) -> None:
        content: Content = read_content()
        self.assertEqual(
            set(content.places), {LIMBO_ID} | PORT_PLACES | SHIP_PLACES | ISLAND_PLACES
        )

    def test_every_land_place_is_on_a_map(self) -> None:
        content: Content = read_content()
        for place in content.places.values():
            if place.kind == "room" and place.id != LIMBO_ID:
                self.assertIsNotNone(place.map, place.id)

    def test_compass_exits_get_short_aliases(self) -> None:
        office_exits = {e.key: e for e in read_content().places["office"].exits}
        self.assertEqual(office_exits["southeast"].aliases, ("se",))

    def _broken_copy(self, file: str, old: str, new: str) -> ContentError:
        """Copy the content files with one change, and return the error reading them gives."""
        with TemporaryDirectory() as tmp:
            for name in (PLACES_FILE, SHIP_FILE, MAPS_FILE):
                text: str = (CONTENT_DIR / name).read_text(encoding="utf-8")
                if name == file:
                    self.assertIn(old, text)
                    text = text.replace(old, new, 1)
                (Path(tmp) / name).write_text(text, encoding="utf-8")
            with self.assertRaises(ContentError) as caught:
                read_content(Path(tmp))
        return caught.exception

    def test_exit_to_unknown_place_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(PLACES_FILE, "east: market", "east: markt")
        self.assertIn("markt", str(error))

    def test_route_to_unknown_position_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(SHIP_FILE, "to: anchorage", "to: nowhere")
        self.assertIn("nowhere", str(error))

    def test_position_off_the_map_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(PLACES_FILE, "[300, 230]", "[3000, 230]")
        self.assertIn("outside", str(error))


class WorldTest(EvenniaTest):
    """A test with the whole world built, room1 standing in for Limbo."""

    character_typeclass: type[Character] = Character
    room_typeclass: type[Room] = Room
    exit_typeclass: type[Exit] = Exit

    def setUp(self) -> None:
        super().setUp()
        self.rooms: dict[str, Room] = build_world(limbo=self.room1)
        self.char1.move_to(self.room1, quiet=True)
        self.char2.move_to(self.room1, quiet=True)

    def exits_from(self, place_id: str) -> dict[str, Any]:
        return {exit_obj.key: exit_obj for exit_obj in self.rooms[place_id].exits}

    def go(self, character: Character, exit_key: str) -> None:
        """Walk through an exit the way the exit command does."""
        exits: dict[str, Any] = {e.key: e for e in character.location.exits}
        self.assertIn(exit_key, exits, f"No exit {exit_key!r} in {character.location.key}")
        exits[exit_key].at_traverse(character, exits[exit_key].destination)


class TestBuild(WorldTest):
    def test_builds_every_place_with_its_typeclass(self) -> None:
        content: Content = load_content()
        self.assertEqual(set(self.rooms), set(content.places))
        self.assertIsInstance(self.rooms["deck"], Deck)
        self.assertIsInstance(self.rooms["cabin"], ShipRoom)
        self.assertNotIsInstance(self.rooms["cabin"], Deck)
        self.assertEqual(self.rooms[LIMBO_ID], self.room1)
        self.assertEqual(self.room1.key, "Phantom Island")

    def test_limbo_leads_into_the_society_office(self) -> None:
        self.assertEqual(self.exits_from(LIMBO_ID)["begin"].destination, self.rooms["office"])

    def test_rebuilding_keeps_the_rooms_and_does_not_double_the_exits(self) -> None:
        before: dict[str, int] = {key: room.id for key, room in self.rooms.items()}
        exits_before: int = len(self.rooms["village"].exits)
        rooms_again: dict[str, Room] = build_world(limbo=self.room1)
        self.assertEqual({key: room.id for key, room in rooms_again.items()}, before)
        self.assertEqual(len(self.rooms["village"].exits), exits_before)

    def test_deck_has_the_sail_command(self) -> None:
        self.assertTrue(self.rooms["deck"].cmdset.has("DeckCmdSet"))


class TestWalkEverywhere(WorldTest):
    """Stage A1 is done when two players can walk everywhere and see each other."""

    def reachable(self) -> set[str]:
        """
        Every place reachable on foot, with the ship at each of her positions in turn.

        The walk starts in Limbo and on the Deck: players sail to a position aboard.
        """
        content: Content = load_content()
        reached: set[str] = set()
        for position in content.positions.values():
            moor_ship(position)
            get_expedition().move_ship(position.id)
            queue: deque[Room] = deque([self.room1, self.rooms["deck"]])
            seen: set[int] = {room.id for room in queue}
            while queue:
                room: Room = queue.popleft()
                if room.place_id:
                    reached.add(room.place_id)
                for exit_obj in room.exits:
                    if exit_obj.destination.id not in seen:
                        seen.add(exit_obj.destination.id)
                        queue.append(exit_obj.destination)
        return reached

    def test_every_place_can_be_reached(self) -> None:
        self.assertEqual(self.reachable(), set(load_content().places))

    def test_two_players_walk_aboard_and_see_each_other(self) -> None:
        for character in (self.char1, self.char2):
            for exit_key in ("begin", "southeast", "aboard"):
                self.go(character, exit_key)
        self.assertEqual(self.char1.location, self.rooms["deck"])
        self.assertEqual(self.char2.location, self.rooms["deck"])
        self.assertIn(self.char2.key, self.rooms["deck"].return_appearance(self.char1))

    def test_ship_view_follows_the_ship(self) -> None:
        deck: Room = self.rooms["deck"]
        self.assertIn("moored at the quay", deck.return_appearance(self.char1))
        moor_ship(load_content().positions["charted"])
        get_expedition().move_ship("charted")
        self.assertIn("nothing but water", deck.return_appearance(self.char1))


class TestSail(WorldTest):
    def setUp(self) -> None:
        super().setUp()
        self.char1.move_to(self.rooms["deck"], quiet=True)
        self.char2.move_to(self.rooms["deck"], quiet=True)
        crew_patch: Any = patch("world.ship.crew_ashore", return_value=[])
        self.crew_ashore: MagicMock = crew_patch.start()
        self.addCleanup(crew_patch.stop)

    def test_directions_are_normalised(self) -> None:
        self.assertEqual(normalise_direction("W"), "west")
        self.assertEqual(normalise_direction("to the west"), "west")

    def test_sailing_moves_the_ship_and_her_exits(self) -> None:
        self.assertTrue(sail(self.char1, "west"))
        self.assertEqual(current_position().id, "charted")
        ashore_exit: Any = find_ship_exit(ASHORE)
        self.assertIsNone(ashore_exit.location)
        self.assertNotIn("aboard", self.exits_from("quay"))

        self.assertTrue(sail(self.char1, "w"))
        self.assertEqual(current_position().id, "anchorage")
        self.assertEqual(self.exits_from("deck")["ashore"].destination, self.rooms["beach"])
        self.assertEqual(self.exits_from("beach")["aboard"].destination, self.rooms["deck"])
        self.assertEqual(get_expedition().track, ["port", "charted", "anchorage"])

    def test_wrong_direction_says_where_you_can_sail(self) -> None:
        with patch.object(self.char1, "msg") as mock_msg:
            self.assertFalse(sail(self.char1, "north"))
        self.assertIn("You can sail: west", texts(mock_msg))
        self.assertEqual(current_position().id, "port")

    def test_does_not_leave_anyone_ashore(self) -> None:
        self.char2.move_to(self.rooms["quay"], quiet=True)
        self.crew_ashore.return_value = [self.char2]
        with patch.object(self.char1, "msg") as mock_msg:
            self.assertFalse(sail(self.char1, "west"))
        self.assertIn(self.char2.key, texts(mock_msg))
        self.assertEqual(current_position().id, "port")

    def test_everyone_aboard_sees_the_new_view(self) -> None:
        self.char2.move_to(self.rooms["cabin"], quiet=True)
        with patch.object(self.char2, "msg") as mock_msg:
            sail(self.char1, "west")
        self.assertIn("many days", texts(mock_msg))
        self.assertIn("open sea", texts(mock_msg))
        self.assertIn("sea_chart.svg", sent(mock_msg, "map")[0])

    def test_sail_command(self) -> None:
        self.char1.execute_cmd("sail west")
        self.assertEqual(current_position().id, "charted")


class TestMapsAndFocus(WorldTest):
    def test_moving_sends_map_and_focus(self) -> None:
        with patch.object(self.char1, "msg") as mock_msg:
            self.char1.move_to(self.rooms["market"])
        maps: list[Any] = sent(mock_msg, "map")
        self.assertEqual(len(maps), 1)
        self.assertIn("The port", maps[0])
        self.assertIn("You are here", maps[0])
        self.assertIn("Market", sent(mock_msg, "focus")[0])

    def test_limbo_has_no_map(self) -> None:
        with patch.object(self.char1, "msg") as mock_msg:
            self.room1.send_visuals(self.char1)
        self.assertIn("No map", sent(mock_msg, "map")[0])

    def test_the_ship_is_on_the_port_plan_and_marks_you_aboard(self) -> None:
        on_quay: MapView | None = self.rooms["quay"].map_view()
        aboard: MapView | None = self.rooms["deck"].map_view()
        assert on_quay is not None and aboard is not None
        self.assertEqual(aboard.picture_map.key, "port")
        ship_on_quay: list[MapPlace] = [p for p in on_quay.places if p.is_ship]
        ship_aboard: list[MapPlace] = [p for p in aboard.places if p.is_ship]
        self.assertFalse(ship_on_quay[0].is_here)
        self.assertTrue(ship_aboard[0].is_here)

    def test_aboard_the_map_shows_which_ship_room_you_are_in(self) -> None:
        quay: MapView | None = self.rooms["quay"].map_view()
        assert quay is not None
        self.assertEqual(quay.aboard, [])
        for place_id, here_label in (("deck", "Deck"), ("cabin", "Cabin")):
            view: MapView | None = self.rooms[place_id].map_view()
            assert view is not None
            self.assertEqual([m.label for m in view.aboard if m.is_here], [here_label])
            ship: list[MapPlace] = [p for p in view.places if p.is_ship]
            self.assertEqual(ship[0].label, f"{SHIP_LABEL} ({here_label})")
            self.assertIn(
                f"You are here: {SHIP_LABEL} ({here_label})", self.rooms[place_id].map_text()
            )

    def test_going_below_updates_the_map(self) -> None:
        self.char1.move_to(self.rooms["deck"], quiet=True)
        with patch.object(self.char1, "msg") as mock_msg:
            self.go(self.char1, "down")
        map_html: str = sent(mock_msg, "map")[0]
        self.assertIn(f"{SHIP_LABEL} (Cabin)", map_html)
        self.assertIn('font-weight="bold" fill="#1d2b36">Cabin', map_html)

    def test_at_sea_the_deck_shows_the_sea_chart_with_the_track(self) -> None:
        get_expedition().move_ship("charted")
        view: MapView | None = self.rooms["cabin"].map_view()
        assert view is not None
        self.assertEqual(view.picture_map.key, "sea_chart")
        self.assertEqual(len(view.track), 2)
        self.assertIn("polyline", render_map_html(view))
        self.assertIn("track", self.rooms["cabin"].map_text())

    def test_map_command_describes_the_map_in_words(self) -> None:
        self.char1.move_to(self.rooms["village"], quiet=True)
        with patch.object(self.char1, "msg") as mock_msg:
            self.char1.execute_cmd("map")
        words: str = texts(mock_msg)
        self.assertIn("You are here: Village", words)
        self.assertIn("Hilltop", words)
        self.assertNotIn(SHIP_LABEL, words)  # the ship is still in port

    def test_labels_and_titles_are_escaped(self) -> None:
        view: MapView | None = self.rooms["quay"].map_view()
        assert view is not None
        bad: MapView = MapView(
            picture_map=view.picture_map,
            places=[MapPlace(label="<b>Fort</b>", x=1, y=2, is_here=False)],
            track=[],
            track_names=[],
        )
        self.assertIn("&lt;b&gt;Fort&lt;/b&gt;", render_map_html(bad))
        self.assertNotIn("<b>", render_focus_html("<b>Fort</b>", None))
        self.assertNotIn("<script>", render_focus_html("x", '"><script>'))
        self.assertIsNotNone(find_ship_exit(ABOARD))
