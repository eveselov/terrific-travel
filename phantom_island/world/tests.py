"""
Tests for the content files, the world builder, the ship, the Map and Focus panes, and
talking to the characters.

Run from the game directory with `uv run evennia test --settings settings.py .`
"""

from collections import deque
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

from evennia.objects.objects import DefaultCharacter
from evennia.utils.test_resources import EvenniaTest

from typeclasses.characters import Character
from typeclasses.exits import Exit
from typeclasses.inhabitants import Inhabitant
from typeclasses.rooms import Deck, Room, ShipRoom
from typeclasses.scripts import JournalEntry
from world.builder import build_world
from world.clues import journal_text, show_marks
from world.content import (
    CHARACTERS_FILE,
    CLUES_FILE,
    CONTENT_DIR,
    LIMBO_ID,
    MAPS_FILE,
    PLACES_FILE,
    SHIP_FILE,
    THINGS_FILE,
    CharacterSpec,
    Content,
    ContentError,
    TopicSpec,
    all_texts,
    load_content,
    read_content,
)
from world.conversation import ask, listeners
from world.discovery import return_things_home
from world.expedition import current_position, get_expedition
from world.focus import render_focus_html
from world.maps import SHIP_LABEL, MapPlace, MapView, render_map_html
from world.places import find_inhabitant, find_ship_exit, find_thing
from world.ship import ABOARD, ASHORE, LATE_JOINER, moor_ship, normalise_direction, sail

CONTENT_FILES: tuple[str, ...] = (
    PLACES_FILE,
    SHIP_FILE,
    MAPS_FILE,
    CHARACTERS_FILE,
    CLUES_FILE,
    THINGS_FILE,
)

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
            for name in CONTENT_FILES:
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

    def test_character_in_unknown_place_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(CHARACTERS_FILE, "where: quay", "where: quai")
        self.assertIn("quai", str(error))

    def test_one_word_for_two_topics_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(
            CHARACTERS_FILE, "aliases: [sky, wind]", "aliases: [sky, wind, storm]"
        )
        self.assertIn("storm", str(error))

    def test_the_thirteen_clues_and_the_things(self) -> None:
        content: Content = read_content()
        self.assertEqual(list(content.clues), [f"C{n}" for n in range(1, 14)])
        self.assertEqual(content.things["sextant"].where, "cabin")
        self.assertTrue(content.things["plant_guide"].portable)
        self.assertFalse(content.things["compass"].portable)

    def test_every_clue_can_be_found_somewhere(self) -> None:
        content: Content = read_content()
        revealed: set[str] = {clue for _, _, clue in all_texts(content) if clue}
        self.assertEqual(revealed, set(content.clues))

    def test_a_clue_text_without_a_mark_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(THINGS_FILE, "[[HALCYON]]", "HALCYON")
        self.assertIn("marks no part", str(error))

    def test_a_mark_without_a_clue_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(
            PLACES_FILE, "Traders call out", "[[Traders]] call out"
        )
        self.assertIn("no `clue`", str(error))

    def test_an_unknown_clue_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(THINGS_FILE, "clue: C1\n", "clue: C99\n")
        self.assertIn("C99", str(error))

    def test_with_an_unknown_thing_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(PLACES_FILE, "animal_guide:", "animal_gide:")
        self.assertIn("animal_gide", str(error))

    def test_needing_a_flag_nothing_sets_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(
            THINGS_FILE, "needs: [sight_charted]", "needs: [sight_chartd]"
        )
        self.assertIn("sight_chartd", str(error))


class TestCharacterContent(TestCase):
    """The characters and their topics, without a database."""

    def setUp(self) -> None:
        self.characters: dict[str, CharacterSpec] = read_content().characters

    def topic_id(self, character_id: str, text: str) -> str | None:
        found: TopicSpec | None = self.characters[character_id].topic(text)
        return found.id if found else None

    def test_the_seven_characters(self) -> None:
        self.assertEqual(
            set(self.characters),
            {"fairweather", "barnaby", "crane", "ama", "tui", "jonah", "ship"},
        )
        self.assertTrue(self.characters["ship"].aboard)
        self.assertEqual(self.characters["ship"].places, ())
        self.assertEqual(self.characters["tui"].places, ("village", "reef"))

    def test_topics_are_found_by_id_alias_and_shared_alias(self) -> None:
        for text in ("storm", "The Storm?", "great storm", "storm of '75"):
            self.assertEqual(self.topic_id("barnaby", text), "storm", text)
        self.assertEqual(self.topic_id("barnaby", "dead reckoning"), "sailing")

    def test_unknown_or_ambiguous_topics_find_nothing(self) -> None:
        self.assertIsNone(self.topic_id("barnaby", "pirates"))
        self.assertIsNone(self.topic_id("barnaby", "weather and sailing"))

    def test_the_same_word_means_the_same_topic_for_everyone(self) -> None:
        for character_id in ("barnaby", "jonah", "ama", "crane", "fairweather"):
            self.assertEqual(self.topic_id(character_id, "the Halcyon"), "halcyon", character_id)


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
        self.assertEqual([m.label for m in quay.ship_rooms], ["Deck", "Cabin"])
        self.assertFalse(any(m.is_here for m in quay.ship_rooms))
        for place_id, here_label in (("deck", "Deck"), ("cabin", "Cabin")):
            view: MapView | None = self.rooms[place_id].map_view()
            assert view is not None
            self.assertEqual([m.label for m in view.ship_rooms if m.is_here], [here_label])
            ship: list[MapPlace] = [p for p in view.places if p.is_ship]
            self.assertEqual(ship[0].label, f"{SHIP_LABEL} ({here_label})")
            self.assertIn(
                f"You are here: {SHIP_LABEL} ({here_label})", self.rooms[place_id].map_text()
            )

    def test_the_callout_follows_the_ship(self) -> None:
        self.assertIn("<line", render_map_html(self._view("quay")))
        get_expedition().move_ship("charted")
        on_quay: MapView = self._view("quay")
        self.assertEqual(on_quay.ship_rooms, [])
        self.assertNotIn("<line", render_map_html(on_quay))
        self.assertNotIn("Cabin", render_map_html(on_quay))
        self.assertEqual(len(self._view("cabin").ship_rooms), 2)  # on the sea chart now

    def _view(self, place_id: str) -> MapView:
        view: MapView | None = self.rooms[place_id].map_view()
        assert view is not None
        return view

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


class TestInhabitants(WorldTest):
    def test_each_inhabitant_stands_in_its_place(self) -> None:
        for spec in load_content().characters.values():
            inhabitant: Any = find_inhabitant(spec.id)
            if spec.aboard:
                self.assertIsNone(inhabitant, "the Ship has no object")
                continue
            self.assertIsInstance(inhabitant, Inhabitant)
            self.assertEqual(inhabitant.location, self.rooms[spec.places[0]], spec.id)
            self.assertEqual(inhabitant.key, spec.name)

    def test_rooms_list_their_inhabitants(self) -> None:
        self.char1.move_to(self.rooms["quay"], quiet=True)
        self.assertIn("Old Barnaby", self.rooms["quay"].return_appearance(self.char1))

    def test_rebuilding_keeps_the_inhabitants(self) -> None:
        barnaby: Any = find_inhabitant("barnaby")
        build_world(limbo=self.room1)
        self.assertEqual(find_inhabitant("barnaby"), barnaby)
        self.assertEqual(len(barnaby.location.contents_get(content_type="character")), 1)

    def test_inhabitants_cannot_be_picked_up(self) -> None:
        barnaby: Any = find_inhabitant("barnaby")
        self.assertFalse(barnaby.access(self.char1, "get"))


class TestAsk(WorldTest):
    def at(self, place_id: str) -> None:
        self.char1.move_to(self.rooms[place_id], quiet=True)
        self.char2.move_to(self.rooms[place_id], quiet=True)

    def ask(self, text: str) -> str:
        """What char1 reads after `ask <text>`."""
        with patch.object(self.char1, "msg") as mock_msg:
            ask(self.char1, text)
        return texts(mock_msg)

    def test_a_topic_gives_its_reply(self) -> None:
        self.at("quay")
        heard: str = self.ask("barnaby about the storm")
        self.assertIn("You ask Old Barnaby about the storm.", heard)
        self.assertIn('Old Barnaby says: "Worst I ever saw.', heard)

    def test_ask_without_about_works_too(self) -> None:
        self.at("quay")
        self.assertIn("Worst I ever saw", self.ask("old barnaby storm"))

    def test_an_unknown_topic_gives_the_fallback_and_suggestions(self) -> None:
        self.at("quay")
        heard: str = self.ask("barnaby about pirates")
        self.assertIn("Can't say I know aught", heard)
        self.assertIn("You could ask Old Barnaby about", heard)

    def test_asking_with_no_topic_greets_and_suggests(self) -> None:
        self.at("market")
        heard: str = self.ask("crane")
        self.assertIn("honestly come by", heard)
        self.assertIn("ask crane about compass", heard)

    def test_with_one_person_here_the_name_can_be_left_out(self) -> None:
        self.at("quay")
        self.assertIn("Worst I ever saw", self.ask("about storm"))

    def test_with_two_people_here_ask_who(self) -> None:
        self.at("village")
        heard: str = self.ask("about goats")
        self.assertIn("Whom do you want to ask about goats?", heard)
        self.assertIn("Elder Ama", heard)
        self.assertIn("Tui", heard)

    def test_with_one_person_here_the_topic_alone_is_enough(self) -> None:
        self.at("office")
        heard: str = self.ask("halcyon")
        self.assertIn("You ask Mrs. Fairweather about halcyon.", heard)
        self.assertIn("She sailed from this harbour", heard)

    def test_the_ship_answers_a_topic_alone_on_deck(self) -> None:
        self.at("deck")
        self.assertIn("15 degrees every hour", self.ask("longitude"))

    def test_a_player_is_not_a_character_to_ask(self) -> None:
        self.at("office")
        heard: str = self.ask(self.char2.key)
        self.assertIn("is another player", heard)
        self.assertIn("say", heard)
        self.assertIn("That's you!", self.ask(f"{self.char1.key} about halcyon"))

    def test_a_character_elsewhere_is_not_taken_for_a_topic(self) -> None:
        self.at("quay")
        self.assertIn("There's nobody called 'crane' here", self.ask("crane compass"))

    def test_a_word_of_a_name_alone_is_still_a_topic(self) -> None:
        self.at("office")  # `old` is part of Old Barnaby's name, but `old chart` is the chart
        self.assertIn("This is the Halcyon's chart", self.ask("old chart"))

    def test_several_topics_at_once_get_the_first_answered(self) -> None:
        self.at("office")
        heard: str = self.ask("fairweather about halcyon chart")
        self.assertIn("You ask Mrs. Fairweather about halcyon.", heard)
        self.assertIn("She sailed from this harbour", heard)
        self.assertNotIn("This is the Halcyon's chart", heard)
        self.assertIn("One thing at a time: you can ask about |wchart|n next.", heard)

    def test_something_to_look_at_gets_a_hint(self) -> None:
        self.at("spring")
        heard: str = self.ask("shoots")
        self.assertIn("There is nobody here to talk to.", heard)
        self.assertIn("look shoots", heard)
        self.at("village")
        self.assertIn("look beams", self.ask("beams"))

    def test_crane_lies_until_the_coral_is_found(self) -> None:
        self.at("market")
        with patch("world.clues.connected_characters", return_value=[]):
            self.assertIn("Found it on a", self.ask("crane about compass"))
            self.assertEqual(get_expedition().journal, [])
            get_expedition().add_clue("C2", "someone", "Market")
            heard: str = self.ask("crane about compass")
        self.assertIn("I didn't find it", heard)
        self.assertIn("New in the journal", heard)
        self.assertTrue(get_expedition().has_clue("C3"))

    def test_ama_still_waits_for_respect(self) -> None:
        self.at("village")
        self.assertIn("Not every story", self.ask("ama about halcyon"))

    def test_others_in_the_room_hear_the_conversation(self) -> None:
        self.at("quay")
        with patch.object(self.char2, "msg") as mock_msg:
            ask(self.char1, "barnaby about weather")
        heard: str = texts(mock_msg)
        self.assertIn(f"{self.char1.key} asks Old Barnaby about weather.", heard)
        self.assertIn("Red sky at night", heard)

    def test_another_players_turn_is_tagged_for_the_web_client(self) -> None:
        self.at("quay")
        # Patched on the class, so the calls don't record who received them; the class each
        # message carries is enough to tell.
        with patch.object(DefaultCharacter, "msg") as mock_msg:
            for turn in (1, 2):
                self.char1.ndb.turn = turn
                ask(self.char1, "barnaby about weather")
        classes: list[str | None] = []
        for call in mock_msg.call_args_list:
            text: Any = call.kwargs["text"]
            classes.append(text[1].get("cls") if isinstance(text, tuple) else None)
        # char1: "You ask..." and the reply, untagged. char2: "asks..." (a new turn), then
        # the reply (the same turn). Barnaby hears both untagged too. Twice.
        self.assertEqual(classes.count("pi-other pi-turn"), 2)
        self.assertEqual(classes.count("pi-other"), 2)
        self.assertEqual(classes.count(None), 8)

    def test_nobody_by_that_name(self) -> None:
        self.at("quay")
        self.assertIn("There's nobody called 'crane' here", self.ask("crane about compass"))

    def test_the_ship_answers_on_deck_and_in_the_cabin(self) -> None:
        for place_id in ("deck", "cabin"):
            self.at(place_id)
            self.assertIn("15 degrees every hour", self.ask("ship about longitude"), place_id)

    def test_the_ship_is_silent_ashore(self) -> None:
        self.at("quay")
        self.assertIn("can only hear you when you're aboard", self.ask("ship about longitude"))
        self.assertNotIn("the Ship", [listener.spec.name for listener in listeners(self.char1)])

    def test_the_ask_command_is_available(self) -> None:
        self.at("quay")
        with patch.object(self.char1, "msg") as mock_msg:
            self.char1.execute_cmd("ask barnaby about compass")
        self.assertIn("waving that compass", texts(mock_msg))


class TestClueMarks(TestCase):
    def test_marked_parts_are_yellow(self) -> None:
        self.assertEqual(show_marks("A [[coral]] crust."), "A |ycoral|n crust.")

    def test_white_words_inside_a_clue_go_back_to_yellow(self) -> None:
        self.assertEqual(show_marks("[[the |wcove|n, here]]"), "|ythe |wcove|n|y, here|n")


class DiscoveryTest(WorldTest):
    """A world test where both players count as connected, so both hear of new clues."""

    def setUp(self) -> None:
        super().setUp()
        connected: Any = patch(
            "world.clues.connected_characters", return_value=[self.char1, self.char2]
        )
        connected.start()
        self.addCleanup(connected.stop)

    def at(self, character: Character, place_id: str) -> None:
        character.move_to(self.rooms[place_id], quiet=True)

    def do(self, character: Character, command: str) -> str:
        """What a character reads after typing a command."""
        with patch.object(character, "msg") as mock_msg:
            character.execute_cmd(command)
        return texts(mock_msg)

    def journal_ids(self) -> list[str]:
        return [entry.clue for entry in get_expedition().journal]

    def ship_at(self, position_id: str) -> None:
        get_expedition().move_ship(position_id)
        moor_ship(current_position())

    def thing(self, thing_id: str) -> Any:
        found: Any | None = find_thing(thing_id)
        assert found is not None, thing_id
        return found


class TestThings(DiscoveryTest):
    def test_things_are_built_in_their_places(self) -> None:
        for spec in load_content().things.values():
            thing: Any = find_thing(spec.id)
            self.assertIsNotNone(thing, spec.id)
            self.assertEqual(thing.location, self.rooms[spec.where], spec.id)
            self.assertEqual(thing.key, spec.name)

    def test_the_compass_stays_on_the_stall(self) -> None:
        self.at(self.char1, "market")
        self.assertIn("Looking is free", self.do(self.char1, "get compass"))
        self.assertEqual(self.thing("compass").location, self.rooms["market"])

    def test_books_can_be_carried(self) -> None:
        self.at(self.char1, "cabin")
        self.do(self.char1, "get plant guide")
        self.assertEqual(self.thing("plant_guide").location, self.char1)

    def test_rebuilding_leaves_carried_things_with_their_carrier(self) -> None:
        self.at(self.char1, "cabin")
        self.do(self.char1, "get chart")
        build_world(limbo=self.room1)
        self.assertEqual(self.thing("chart").location, self.char1)

    def test_carried_things_go_home_when_their_carrier_leaves(self) -> None:
        self.at(self.char1, "cabin")
        self.do(self.char1, "get chart")
        self.at(self.char1, "hilltop")
        return_things_home(self.char1)
        self.assertEqual(self.thing("chart").location, self.rooms["cabin"])


class TestLookingAndTheJournal(DiscoveryTest):
    def test_the_compass_reveals_a_clue_in_yellow(self) -> None:
        self.at(self.char1, "market")
        seen: str = self.do(self.char1, "look compass")
        self.assertIn("|yHALCYON|n", seen)
        self.assertIn("New in the journal:|n Silas Crane is selling", seen)
        entry: JournalEntry = get_expedition().journal[0]
        self.assertEqual((entry.clue, entry.finder, entry.place), ("C1", self.char1.key, "Market"))

    def test_a_player_elsewhere_hears_who_found_it(self) -> None:
        self.at(self.char1, "market")
        self.at(self.char2, "quay")
        with patch.object(self.char2, "msg") as mock_msg:
            self.char1.execute_cmd("look compass")
        self.assertIn(f"{self.char1.key} found something at Market.", texts(mock_msg))

    def test_a_clue_is_written_down_once(self) -> None:
        self.at(self.char1, "market")
        self.do(self.char1, "look compass")
        self.assertIn("Already in the journal", self.do(self.char1, "look compass"))
        self.assertEqual(self.journal_ids(), ["C1"])

    def test_examine_looks_closer(self) -> None:
        self.at(self.char1, "market")
        self.assertIn("coral, grown right into the brass", self.do(self.char1, "examine compass"))
        self.assertEqual(self.journal_ids(), ["C2"])

    def test_a_detail_with_a_closer_look(self) -> None:
        self.at(self.char1, "village")
        self.assertIn("much heavier", self.do(self.char1, "look beams"))
        self.assertEqual(self.journal_ids(), [])
        self.assertIn("shipwrights", self.do(self.char1, "x old beams"))
        self.assertEqual(self.journal_ids(), ["C8"])

    def test_a_book_shows_more(self) -> None:
        self.at(self.char1, "spring")
        self.assertNotIn("onions", self.do(self.char1, "look shoots"))
        self.thing("plant_guide").move_to(self.char1, quiet=True)
        self.assertIn("|yonions", self.do(self.char1, "look shoots"))
        self.assertEqual(self.journal_ids(), ["C9"])

    def test_the_chart_on_the_hilltop(self) -> None:
        self.thing("chart").move_to(self.char1, quiet=True)
        self.at(self.char1, "hilltop")
        self.assertIn("same island", self.do(self.char1, "look coastline"))
        self.assertEqual(self.journal_ids(), ["C10"])

    def test_look_still_finds_characters_and_rooms(self) -> None:
        self.at(self.char1, "quay")
        self.assertIn("retired sailor", self.do(self.char1, "look barnaby"))
        self.assertIn("long stone quay", self.do(self.char1, "look"))

    def test_a_reply_with_a_clue(self) -> None:
        self.at(self.char1, "village")
        heard: str = self.do(self.char1, "ask tui about song")
        self.assertIn("|ymade a new canoe", heard)
        self.assertEqual(self.journal_ids(), ["C11"])

    def test_the_journal_command(self) -> None:
        self.assertIn("still empty", self.do(self.char1, "journal"))
        self.at(self.char1, "reef")
        self.do(self.char1, "look bones")
        listed: str = self.do(self.char2, "journal")
        self.assertIn("1. |yA wreck on the Western Reef|n", listed)
        self.assertIn(f"found by {self.char1.key}, Western Reef", listed)
        self.assertEqual(listed, journal_text())


class TestAtSea(DiscoveryTest):
    def test_the_empty_sea_is_noticed_on_arrival(self) -> None:
        self.at(self.char1, "deck")
        self.at(self.char2, "deck")
        with patch("world.ship.crew_ashore", return_value=[]):
            sail(self.char1, "west")
        self.assertEqual(self.journal_ids(), ["C4"])

    def test_the_birds_at_dusk(self) -> None:
        self.ship_at("charted")
        self.at(self.char1, "deck")
        self.assertIn("|yall flying the same way: west", self.do(self.char1, "look birds"))
        self.assertIn("C6", self.journal_ids())

    def test_the_sextant_needs_the_deck(self) -> None:
        self.at(self.char1, "cabin")
        self.assertIn("Take the sextant up", self.do(self.char1, "use sextant"))

    def test_noon_sight_and_chronometer_find_the_longitude_clue(self) -> None:
        self.ship_at("charted")
        self.at(self.char2, "cabin")
        self.assertIn("Take a noon sight", self.do(self.char2, "read chronometer"))
        self.at(self.char1, "cabin")
        self.do(self.char1, "get sextant")
        self.at(self.char1, "deck")
        self.assertIn("Latitude 14 degrees South", self.do(self.char1, "use sextant"))
        self.assertIn("|ylatitude is easy", self.do(self.char2, "read chronometer"))
        self.assertIn("C5", self.journal_ids())

    def test_at_the_island_the_longitude_is_ten_degrees_out(self) -> None:
        self.ship_at("anchorage")
        self.thing("sextant").move_to(self.char1, quiet=True)
        self.at(self.char1, "deck")
        self.do(self.char1, "use sextant")
        self.at(self.char1, "cabin")
        self.assertIn("10 degrees further west", self.do(self.char1, "read chronometer"))

    def test_others_in_the_room_hear_what_is_read(self) -> None:
        self.at(self.char1, "cabin")
        self.at(self.char2, "cabin")
        with patch.object(self.char2, "msg") as mock_msg:
            self.char1.execute_cmd("read plant guide")
        heard: str = texts(mock_msg)
        self.assertIn(f"{self.char1.key} reads the plant guide.", heard)
        self.assertIn("Oak is heavy", heard)


class TestLateJoiners(DiscoveryTest):
    def begin(self, character: Character) -> str:
        character.move_to(self.room1, quiet=True)
        with patch.object(character, "msg") as mock_msg:
            self.go(character, "begin")
        return texts(mock_msg)

    def test_in_port_begin_leads_to_the_office(self) -> None:
        self.begin(self.char1)
        self.assertEqual(self.char1.location, self.rooms["office"])

    def test_with_the_ship_away_begin_leads_to_the_deck(self) -> None:
        self.ship_at("charted")
        told: str = self.begin(self.char1)
        self.assertEqual(self.char1.location, self.rooms["deck"])
        self.assertIn(LATE_JOINER, told)
