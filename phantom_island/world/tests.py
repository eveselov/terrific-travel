"""
Tests for the content files, the world builder, the ship, the Map and Focus panes, and
talking to the characters.

Run from the game directory with `uv run evennia test --settings settings.py .`
"""

from collections import deque
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

from evennia.objects.objects import DefaultCharacter
from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest

import world.content
from typeclasses.characters import Character
from typeclasses.exits import Exit
from typeclasses.inhabitants import Inhabitant
from typeclasses.rooms import Deck, Room, ShipRoom
from typeclasses.scripts import JournalEntry
from world.builder import build_world
from world.clues import journal_sources_text, journal_text, show_marks
from world.content import (
    CHARACTERS_FILE,
    CLUES_FILE,
    CONTENT_DIR,
    COUNCILS_FILE,
    HINTS_FILE,
    IDEAS_FILE,
    LIMBO_ID,
    MAPS_FILE,
    PLACES_FILE,
    REPORT_FILE,
    SHIP_FILE,
    THINGS_FILE,
    UNDER_WAY,
    AreaSpec,
    CharacterSpec,
    Content,
    ContentError,
    IdeaSpec,
    RouteSpec,
    TopicSpec,
    _character,
    all_teachings,
    all_texts,
    load_content,
    parse_coords,
    read_content,
)
from world.conversation import ask, listeners
from world.discovery import return_stray_things, return_things_home
from world.expedition import current_position, get_expedition
from world.focus import render_focus_html
from world.maps import SHIP_LABEL, MapPlace, MapView, render_map_html
from world.paths import hidden_places
from world.places import (
    PLACE_TAG_CATEGORY,
    find_inhabitant,
    find_place,
    find_ship_exit,
    find_thing,
)
from world.reset import route_to, shortcut_position, start_over
from world.ship import (
    ABOARD,
    ASHORE,
    LATE_JOINER,
    STEP_SECONDS,
    find_route,
    moor_ship,
    normalise_direction,
    resume_voyage,
    route_open,
    sail,
    sail_on,
)

CONTENT_FILES: tuple[str, ...] = (
    PLACES_FILE,
    SHIP_FILE,
    MAPS_FILE,
    CHARACTERS_FILE,
    CLUES_FILE,
    THINGS_FILE,
    IDEAS_FILE,
    REPORT_FILE,
    HINTS_FILE,
    COUNCILS_FILE,
)

PORT_PLACES: set[str] = {"office", "quay", "market"}
SHIP_PLACES: set[str] = {"deck"}
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

    def test_positions_as_players_write_them(self) -> None:
        for text in ("14 south 40 west", "14S, 40W", "latitude 14 degrees S, longitude 40 W"):
            self.assertEqual(parse_coords(text), (-14, -40), text)
        self.assertEqual(parse_coords("40 west 14 south"), (-14, -40))
        self.assertEqual(parse_coords("10 north 25 east"), (10, 25))
        self.assertIsNone(parse_coords("14 40"))
        self.assertIsNone(parse_coords("14 south 15 south"))

    def test_a_white_word_must_be_the_speakers_topic(self) -> None:
        error: ContentError = self._broken_copy(
            CHARACTERS_FILE, "Ask old Barnaby on the quay", "Ask old |wBarnaby|n on the quay"
        )
        self.assertIn("isn't one of Silas Crane's topics", str(error))

    def test_every_topic_can_be_found(self) -> None:
        error: ContentError = self._broken_copy(
            CHARACTERS_FILE,
            "        hidden: true  # a surprise",
            "        hidden: false  # a surprise",
        )
        self.assertIn("ship, topic self: players can't find it", str(error))

    def test_a_council_concludes_only_questions_of_the_report(self) -> None:
        error: ContentError = self._broken_copy(COUNCILS_FILE, "      why: >", "      whom: >")
        self.assertIn("`concludes` names 'whom'", str(error))

    def test_settled_by_something_unknown_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(
            CLUES_FILE, "settled: [far_settled]", "settled: [report:nowhere]"
        )
        self.assertIn("`settled` by 'report:nowhere'", str(error))

    def test_the_ship_suggests_only_her_own_topics(self) -> None:
        error: ContentError = self._broken_copy(
            SHIP_FILE, "suggest: [council, tide,", "suggest: [goats, tide,"
        )
        self.assertIn("`suggest` names 'goats'", str(error))

    def test_a_connection_idea_must_be_known_and_say_where_to_learn_it(self) -> None:
        unknown: ContentError = self._broken_copy(
            CLUES_FILE, "    ideas: [coral]", "    ideas: [nowhere]"
        )
        self.assertIn("connection compass_sea: unknown idea 'nowhere'", str(unknown))
        silent: ContentError = self._broken_copy(
            IDEAS_FILE, '    learn: "|wread animal guide|n, in the chart house"\n', ""
        )
        self.assertIn("needs a `learn` text", str(silent))

    def test_teaching_an_unknown_idea_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(
            CHARACTERS_FILE, "teaches: {oak: heard}", "teaches: {nowhere: heard}"
        )
        self.assertIn("unknown idea 'nowhere'", str(error))

    def test_teaching_a_level_without_text_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(
            CHARACTERS_FILE, "teaches: {oak: heard}", "teaches: {horizon: heard}"
        )
        self.assertIn("which has no text", str(error))

    def test_the_task_must_be_a_list_of_questions(self) -> None:
        error: ContentError = self._broken_copy(
            CLUES_FILE, "  questions:\n", "  questions: Where is she?\n  old:\n"
        )
        self.assertIn("task: `questions` must be a list of texts", str(error))

    def test_the_notebook_is_optional(self) -> None:
        """Without ideas.yaml and without any `teaches`, the game's content still works."""
        with TemporaryDirectory() as tmp:
            for name in CONTENT_FILES:
                if name == IDEAS_FILE:
                    continue
                text: str = (CONTENT_DIR / name).read_text(encoding="utf-8")
                kept: list[str] = [
                    line for line in text.split("\n") if not line.strip().startswith("teaches:")
                ]
                (Path(tmp) / name).write_text("\n".join(kept), encoding="utf-8")
            self.assertEqual(read_content(Path(tmp)).ideas, {})

    def test_every_idea_is_taught_somewhere(self) -> None:
        content: Content = read_content()
        taught: set[str] = {idea for _, teaching in all_teachings(content) for idea, _ in teaching}
        self.assertEqual(set(content.ideas) - taught, set())

    def test_route_without_passage_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(SHIP_FILE, "passage:", "voyage:")
        self.assertIn("passage", str(error))

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
            CHARACTERS_FILE,
            "aliases: [weather, sky, wind]",
            "aliases: [weather, sky, wind, sailing]",
        )
        self.assertIn("sailing", str(error))

    def test_the_thirteen_clues_and_the_things(self) -> None:
        content: Content = read_content()
        self.assertEqual(list(content.clues), [f"C{n}" for n in range(1, 14)])
        self.assertEqual(content.things["sextant"].where, "deck")
        self.assertFalse(content.things["sextant"].portable)  # used where it's kept (36)
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
            PLACES_FILE, "One |wstall|n draws", "One [[|wstall|n]] draws"
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

    def test_a_council_proof_with_an_unknown_flag_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(
            COUNCILS_FILE, "clues: [sight_charted]", "clues: [sight_chartd]"
        )
        self.assertIn("council charted, step line", str(error))

    def test_a_council_step_needs_exactly_one_right_choice(self) -> None:
        error: ContentError = self._broken_copy(
            COUNCILS_FILE, "- text: West.\n            right: true\n", "- text: West.\n"
        )
        # Caught as a proof on a wrong choice, before the count of right choices.
        self.assertIn("step 2 (side), choice b", str(error))

    def test_a_hint_at_an_unknown_position_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(HINTS_FILE, "ship: [charted]", "ship: [chartd]")
        self.assertIn("chartd", str(error))

    def test_a_hint_needs_three_levels(self) -> None:
        error: ContentError = self._broken_copy(
            HINTS_FILE, "      - Wait a few moments, then |wlook|n.\n", ""
        )
        self.assertIn("situation under_way", str(error))

    def test_a_connection_with_an_unknown_clue_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(CLUES_FILE, "needs: [C7, C8]", "needs: [C7, C88]")
        self.assertIn("connection oak", str(error))

    def test_the_right_theory_must_not_open_alone(self) -> None:
        rival: str = "        opens: [[C2, C7, C13]]\n        reply: >\n          Coral grows"
        error: ContentError = self._broken_copy(
            REPORT_FILE, rival, "        reply: >\n          Coral grows"
        )
        self.assertIn("must open together with a wrong one", str(error))

    def test_the_report_asks_the_task_questions(self) -> None:
        content: Content = load_content()
        assert content.report is not None and content.task is not None
        self.assertEqual(
            [question.text for question in content.report.questions], list(content.task.questions)
        )

    def test_two_right_choices_are_an_error(self) -> None:
        sank: str = (
            "      - text: She sank far out at sea in the great storm of '75, with all hands."
        )
        error: ContentError = self._broken_copy(REPORT_FILE, sank, f"{sank}\n        right: true")
        self.assertIn("question wreck", str(error))

    def test_proof_with_an_unknown_clue_is_an_error(self) -> None:
        error: ContentError = self._broken_copy(REPORT_FILE, "clues: [C7]", "clues: [C99]")
        self.assertIn("C99", str(error))


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

    def test_everyone_can_be_asked_about_themselves(self) -> None:
        for character_id in self.characters:
            for text in ("yourself", "you", "who are you", "your name"):
                self.assertEqual(self.topic_id(character_id, text), "self", (character_id, text))

    def test_you_counts_only_as_the_whole_question(self) -> None:
        self.assertEqual(self.topic_id("ship", "how do you sail"), "course")

    def test_a_character_without_a_self_topic_gets_the_default(self) -> None:
        data: dict[str, Any] = {
            "name": "the Cook",
            "where": "quay",
            "desc": "A cook.",
            "greeting": "Hello.",
            "fallback": "No idea.",
        }
        cook: CharacterSpec = _character("cook", data, {"self": ("yourself",)})
        self.assertEqual(
            cook.topics["self"].reply, "The Cook would rather talk about other things."
        )
        self.assertEqual(cook.topic("yourself"), cook.topics["self"])

    def test_the_ship_answers_sail_and_advice(self) -> None:
        for text in ("sail", "sails", "sailing"):
            self.assertEqual(self.topic_id("ship", text), "course", text)
        for text in ("advice", "help", "hint", "stuck"):
            self.assertEqual(self.topic_id("ship", text), "advice", text)


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
        # Voyages happen at once in tests, instead of a line every few seconds.
        clock: Any = patch("world.ship.later", side_effect=lambda _s, step, *args: step(*args))
        clock.start()
        self.addCleanup(clock.stop)
        # Crane's confession opens the port (DECISIONS.md, 39); TestLeavingPort tests it.
        gates: Any = patch("world.ship.route_open", return_value=True)
        gates.start()
        self.addCleanup(gates.stop)

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
        self.assertIsInstance(self.rooms["deck"], ShipRoom)
        self.assertEqual(self.rooms[LIMBO_ID], self.room1)
        self.assertEqual(self.room1.key, "Phantom Island")

    def test_rebuilding_removes_a_place_no_longer_in_the_content(self) -> None:
        old_cabin: Room = create_object(Room, key="Cabin")
        old_cabin.tags.add("cabin", category=PLACE_TAG_CATEGORY)
        self.char2.move_to(old_cabin, quiet=True)
        build_world(limbo=self.room1)
        self.assertIsNone(find_place("cabin"))
        self.assertEqual(self.char2.location, self.rooms["deck"])

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

    def test_wrong_direction_says_how_to_give_an_order(self) -> None:
        with patch.object(self.char1, "msg") as mock_msg:
            self.assertFalse(sail(self.char1, "north"))
        self.assertIn("sail to 10 north 25", texts(mock_msg))
        self.assertIn("read chart", texts(mock_msg))
        self.assertEqual(current_position().id, "port")

    def test_sailing_to_the_position_on_the_chart(self) -> None:
        with patch.object(self.char2, "msg") as mock_msg:
            self.assertTrue(sail(self.char1, "to 14 south 40 west"))
        self.assertEqual(current_position().id, "charted")
        self.assertIn("Fourteen degrees South, forty", texts(mock_msg))  # the Ship's answer

    def test_sailing_to_the_island_by_name(self) -> None:
        self.assertTrue(sail(self.char1, "to the island"))
        self.assertEqual(current_position().id, "charted")

    def test_a_position_nobody_knows(self) -> None:
        with patch.object(self.char1, "msg") as mock_msg:
            self.assertFalse(sail(self.char1, "to 14 north 40 west"))
        self.assertIn("14 degrees North, 40 degrees West?", texts(mock_msg))
        self.assertIn("read chart", texts(mock_msg))
        self.assertEqual(current_position().id, "port")

    def test_a_position_needs_its_sides_of_the_world(self) -> None:
        with patch.object(self.char1, "msg") as mock_msg:
            self.assertFalse(sail(self.char1, "to 14 40"))
        self.assertIn("north or south", texts(mock_msg))

    def test_at_the_position_already(self) -> None:
        sail(self.char1, "west")
        with patch.object(self.char1, "msg") as mock_msg:
            self.assertFalse(sail(self.char1, "to 14S 40W"))
        self.assertIn("there already", texts(mock_msg))

    def test_going_home_by_name(self) -> None:
        sail(self.char1, "west")
        self.assertTrue(sail(self.char1, "home"))
        self.assertEqual(current_position().id, "port")

    def test_does_not_leave_anyone_ashore(self) -> None:
        self.char2.move_to(self.rooms["quay"], quiet=True)
        self.crew_ashore.return_value = [self.char2]
        with patch.object(self.char1, "msg") as mock_msg:
            self.assertFalse(sail(self.char1, "west"))
        self.assertIn(self.char2.key, texts(mock_msg))
        self.assertEqual(current_position().id, "port")

    def test_everyone_aboard_sees_the_new_view(self) -> None:
        self.char2.move_to(self.rooms["deck"], quiet=True)
        with patch.object(self.char2, "msg") as mock_msg:
            sail(self.char1, "west")
        self.assertIn("Day 21", texts(mock_msg))
        self.assertIn("open sea", texts(mock_msg))
        self.assertIn("sea_chart.svg", sent(mock_msg, "map")[0])

    def test_sail_command(self) -> None:
        self.char1.execute_cmd("sail west")
        self.assertEqual(current_position().id, "charted")


class TestVoyage(WorldTest):
    """A voyage step by step, as the real clock would run it."""

    def setUp(self) -> None:
        super().setUp()
        self.char1.move_to(self.rooms["deck"], quiet=True)
        crew_patch: Any = patch("world.ship.crew_ashore", return_value=[])
        crew_patch.start()
        self.addCleanup(crew_patch.stop)
        clock: Any = patch("world.ship.later")
        self.clock: MagicMock = clock.start()
        self.addCleanup(clock.stop)

    def ship_pos(self) -> tuple[int, int]:
        view: MapView | None = self.rooms["deck"].map_view()
        assert view is not None and view.ship_pos is not None
        self.assertEqual(view.picture_map.key, "sea_chart")
        return view.ship_pos

    def test_a_builder_can_sail_now(self) -> None:
        told: str = self.do(self.char1, "sail/now to 14 south 40 west")
        self.assertEqual(current_position().id, "charted")  # arrived, without waiting
        self.clock.assert_not_called()
        self.assertIn("Day 21", told)

    def test_a_player_who_types_sail_now_sails_as_usual(self) -> None:
        self.char2.move_to(self.rooms["deck"], quiet=True)
        self.do(self.char2, "sail/now west")
        self.assertEqual(current_position().id, UNDER_WAY)
        self.assertEqual(self.clock.call_args.args[0], STEP_SECONDS)

    def do(self, character: Character, command: str) -> str:
        with patch.object(character, "msg") as mock_msg:
            character.execute_cmd(command)
        return texts(mock_msg)

    def test_the_ship_sails_on_line_by_line(self) -> None:
        self.assertTrue(sail(self.char1, "west"))
        self.assertEqual(current_position().id, UNDER_WAY)
        ashore_exit: Any = find_ship_exit(ASHORE)
        self.assertIsNone(ashore_exit.location)
        self.assertIn("under way", self.rooms["deck"].return_appearance(self.char1))
        self.assertEqual(self.clock.call_args.args[0], STEP_SECONDS)
        number: int = self.clock.call_args.args[2]
        start_x: int = self.ship_pos()[0]

        with patch.object(self.char1, "msg") as mock_msg:
            sail_on(number)
        self.assertIn("Day 4", texts(mock_msg))
        self.assertLess(self.ship_pos()[0], start_x)  # westward, to the left of the chart
        self.assertEqual(current_position().id, UNDER_WAY)

        for _ in range(3):
            sail_on(number)
        self.assertEqual(current_position().id, "charted")
        self.assertIsNone(get_expedition().voyage)
        self.assertEqual(get_expedition().track, ["port", "charted"])

    def test_no_new_order_while_under_way(self) -> None:
        sail(self.char1, "west")
        with patch.object(self.char1, "msg") as mock_msg:
            self.assertFalse(sail(self.char1, "east"))
        self.assertIn("under way", texts(mock_msg))

    def test_the_sextant_under_way(self) -> None:
        sail(self.char1, "west")
        sextant: Any = find_thing("sextant")
        sextant.move_to(self.char1, quiet=True)
        with patch.object(self.char1, "msg") as mock_msg:
            self.char1.execute_cmd("use sextant")
        self.assertIn("holding her latitude", texts(mock_msg))

    def test_a_new_expedition_ends_the_voyage(self) -> None:
        sail(self.char1, "west")
        number: int = self.clock.call_args.args[2]
        start_over("port")
        sail_on(number)  # the step scheduled before starting over
        self.assertEqual(current_position().id, "port")

    def test_a_restart_carries_on(self) -> None:
        sail(self.char1, "west")
        self.clock.reset_mock()
        resume_voyage()
        self.assertEqual(self.clock.call_args.args[1], sail_on)


class TestGo(WorldTest):
    def test_go_is_the_same_as_the_exit(self) -> None:
        self.char1.move_to(self.rooms["office"], quiet=True)
        self.char1.execute_cmd("go southeast")
        self.assertEqual(self.char1.location, self.rooms["quay"])
        self.char1.execute_cmd("go aboard")
        self.assertEqual(self.char1.location, self.rooms["deck"])

    def test_go_to_a_place_by_its_name(self) -> None:
        self.char1.move_to(self.rooms["office"], quiet=True)
        self.char1.execute_cmd("go to the market")
        self.assertEqual(self.char1.location, self.rooms["market"])

    def test_go_nowhere_lists_the_exits(self) -> None:
        self.char1.move_to(self.rooms["office"], quiet=True)
        with patch.object(self.char1, "msg") as mock_msg:
            self.char1.execute_cmd("go north")
        self.assertIn("Exits:", texts(mock_msg))
        self.assertEqual(self.char1.location, self.rooms["office"])


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

    def test_aboard_the_map_shows_you_on_the_ship(self) -> None:
        quay: MapView | None = self.rooms["quay"].map_view()
        assert quay is not None
        self.assertEqual([m.label for m in quay.ship_rooms], ["Deck"])
        self.assertFalse(any(m.is_here for m in quay.ship_rooms))
        view: MapView | None = self.rooms["deck"].map_view()
        assert view is not None
        self.assertEqual([m.label for m in view.ship_rooms if m.is_here], ["Deck"])
        ship: list[MapPlace] = [p for p in view.places if p.is_ship]
        self.assertEqual(ship[0].label, f"{SHIP_LABEL} (Deck)")
        self.assertIn(f"You are here: {SHIP_LABEL} (Deck)", self.rooms["deck"].map_text())

    def test_the_callout_follows_the_ship(self) -> None:
        self.assertIn("<line", render_map_html(self._view("quay")))
        get_expedition().move_ship("charted")
        on_quay: MapView = self._view("quay")
        self.assertEqual(on_quay.ship_rooms, [])
        self.assertNotIn("<line", render_map_html(on_quay))
        self.assertEqual(len(self._view("deck").ship_rooms), 1)  # on the sea chart now

    def _view(self, place_id: str) -> MapView:
        view: MapView | None = self.rooms[place_id].map_view()
        assert view is not None
        return view

    def test_going_aboard_updates_the_map(self) -> None:
        self.char1.move_to(self.rooms["quay"], quiet=True)
        with patch.object(self.char1, "msg") as mock_msg:
            self.go(self.char1, "aboard")
        map_html: str = sent(mock_msg, "map")[0]
        self.assertIn(f"{SHIP_LABEL} (Deck)", map_html)
        self.assertIn('font-weight="bold" fill="#1d2b36">Deck', map_html)

    def test_at_sea_the_deck_shows_the_sea_chart_with_the_track(self) -> None:
        get_expedition().move_ship("charted")
        view: MapView | None = self.rooms["deck"].map_view()
        assert view is not None
        self.assertEqual(view.picture_map.key, "sea_chart")
        self.assertEqual(len(view.track), 2)
        self.assertIn("polyline", render_map_html(view))
        self.assertIn("track", self.rooms["deck"].map_text())

    def test_map_command_describes_the_map_in_words(self) -> None:
        get_expedition().set_flag("village_seen")  # the Village is a learned path (40)
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

    def test_without_about_the_game_shows_how_to_ask(self) -> None:
        self.at("quay")
        heard: str = self.ask("old barnaby storm")
        self.assertNotIn("Worst I ever saw", heard)
        self.assertIn("ask old barnaby about storm", heard)

    def test_the_ship_is_not_a_topic_ashore(self) -> None:
        self.at("quay")  # Barnaby is here, but `ask ship` means the Ship
        heard: str = self.ask("ship")
        self.assertIn("can only hear you when you're aboard", heard)
        self.assertNotIn("Old Barnaby says", heard)

    def test_the_start_of_a_name_is_enough(self) -> None:
        self.at("office")
        self.assertIn("left this harbour", self.ask("fair about halcyon"))
        self.assertIn("nobody called", self.ask("fa about halcyon"))  # too short

    def test_about_alone_goes_to_whoever_you_spoke_to_last(self) -> None:
        self.at("village")
        self.ask("tui")
        self.assertIn("Tui", self.ask("about song").split("\n")[0])
        self.assertIn("Tui", self.ask("her about song").split("\n")[0])
        self.ask("ama")
        self.assertIn("Elder Ama", self.ask("them about halcyon").split("\n")[0])

    def test_an_unknown_topic_gives_the_fallback_in_their_own_words(self) -> None:
        self.at("quay")
        heard: str = self.ask("barnaby about pirates")
        self.assertIn("Can't say I know aught", heard)
        self.assertIn("|wthe great storm|n", heard)
        self.assertNotIn("You could ask", heard)  # no list from the game (playtest 2026-11-22)

    def test_asking_with_no_topic_greets_and_suggests(self) -> None:
        self.at("market")
        heard: str = self.ask("crane")
        self.assertIn("honestly come by", heard)
        self.assertIn("|wcompass|n", heard)
        self.assertNotIn("You could ask", heard)
        self.assertIn("ask crane about compass", heard)  # how to ask, until the first time

    def test_the_example_stops_once_someone_has_been_asked(self) -> None:
        self.at("market")
        self.ask("crane about trade")
        self.assertNotIn("ask crane about compass", self.ask("crane"))

    def test_the_good_hope_still_offers_what_fits_where_she_is(self) -> None:
        self.at("deck")
        heard: str = self.ask("hope")
        self.assertIn("You could ask the Good Hope about", heard)
        self.assertIn("ask hope about", heard)

    def test_fairweather_explains_the_journal_and_the_report(self) -> None:
        self.at("office")
        self.assertIn("|wjournal|n", self.ask("fairweather about mission"))
        self.assertIn("can't prove anything", self.ask("fairweather about journal"))
        self.assertIn("check it against your journal", self.ask("fairweather about report"))

    def test_with_one_person_here_the_name_can_be_left_out(self) -> None:
        self.at("quay")
        self.assertIn("Worst I ever saw", self.ask("about storm"))

    def test_fairweather_can_be_asked_about_the_compass(self) -> None:
        self.at("office")
        self.assertIn("lie on a beach", self.ask("fairweather about compass"))

    def test_with_two_people_here_ask_who(self) -> None:
        self.at("village")
        heard: str = self.ask("about goats")
        self.assertIn("Whom do you want to ask about goats?", heard)
        self.assertIn("Elder Ama", heard)
        self.assertIn("Tui", heard)

    def test_a_topic_alone_needs_someone_to_ask(self) -> None:
        self.at("office")
        heard: str = self.ask("halcyon")
        self.assertIn("ask <someone> about halcyon", heard)
        self.assertIn("Mrs. Fairweather", heard)

    def test_the_ship_answers_about_alone_on_deck(self) -> None:
        self.at("deck")
        self.assertIn("15 degrees every hour", self.ask("about longitude"))

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
        self.assertIn("most precious paper", self.ask("about old chart"))

    def test_several_topics_at_once_get_the_first_answered(self) -> None:
        self.at("office")
        heard: str = self.ask("fairweather about halcyon chart")
        self.assertIn("You ask Mrs. Fairweather about halcyon.", heard)
        self.assertIn("left this harbour", heard)
        self.assertNotIn("most precious paper", heard)
        self.assertIn("One thing at a time: you can ask about |wchart|n next.", heard)

    def test_something_to_look_at_gets_a_hint(self) -> None:
        self.at("spring")
        heard: str = self.ask("about shoots")
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
        self.assertIn("Noted in the journal", heard)
        self.assertTrue(get_expedition().has_clue("C3"))

    def test_ama_still_waits_for_respect(self) -> None:
        self.at("village")
        self.assertIn("shows |wrespect|n first", self.ask("ama about halcyon"))

    def test_others_in_the_room_hear_the_conversation(self) -> None:
        self.at("quay")
        with patch.object(self.char2, "msg") as mock_msg:
            ask(self.char1, "barnaby about island")
        heard: str = texts(mock_msg)
        self.assertIn(f"{self.char1.key} asks Old Barnaby about island.", heard)
        self.assertIn("call it a phantom", heard)

    def test_another_players_turn_is_tagged_for_the_web_client(self) -> None:
        self.at("quay")
        # Patched on the class, so the calls don't record who received them; the class each
        # message carries is enough to tell.
        with patch.object(DefaultCharacter, "msg") as mock_msg:
            for turn in (1, 2):
                self.char1.ndb.turn = turn
                ask(self.char1, "barnaby about island")  # teaches nothing: no notebook line
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

    def test_the_ship_answers_on_deck(self) -> None:
        self.at("deck")
        self.assertIn("15 degrees every hour", self.ask("ship about longitude"))

    def test_the_ship_is_silent_ashore(self) -> None:
        self.at("quay")
        self.assertIn("can only hear you when you're aboard", self.ask("ship about longitude"))
        names: list[str] = [listener.spec.name for listener in listeners(self.char1)]
        self.assertNotIn("the Good Hope", names)

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
        # Most tests play after the briefing: the task is in the journal and the report.
        get_expedition().set_flag("briefed")

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

    def test_watching_is_looking(self) -> None:
        self.at(self.char1, "market")
        self.do(self.char1, "look compass")  # the first look notes the clue in the journal
        self.assertEqual(self.do(self.char1, "watch compass"), self.do(self.char1, "look compass"))

    def test_books_can_be_carried(self) -> None:
        self.at(self.char1, "deck")
        self.do(self.char1, "get plant guide")
        self.assertEqual(self.thing("plant_guide").location, self.char1)

    def test_rebuilding_leaves_carried_things_with_their_carrier(self) -> None:
        self.at(self.char1, "deck")
        self.do(self.char1, "get chart")
        build_world(limbo=self.room1)
        self.assertEqual(self.thing("chart").location, self.char1)

    def test_carried_things_go_home_when_their_carrier_leaves(self) -> None:
        self.at(self.char1, "deck")
        self.do(self.char1, "get chart")
        self.at(self.char1, "hilltop")
        return_things_home(self.char1)
        self.assertEqual(self.thing("chart").location, self.rooms["deck"])

    def test_things_held_by_someone_nobody_plays_go_home(self) -> None:
        # char1 has a session in EvenniaTest, char2 has none (as after a server restart).
        self.assertTrue(self.char1.sessions.count())
        self.assertFalse(self.char2.sessions.count())
        self.thing("chart").move_to(self.char1, quiet=True)
        self.thing("plant_guide").move_to(self.char2, quiet=True)
        build_world(limbo=self.room1)
        self.assertEqual(self.thing("chart").location, self.char1)
        self.assertEqual(self.thing("plant_guide").location, self.rooms["deck"])
        self.thing("animal_guide").move_to(self.char2, quiet=True)
        self.assertEqual(return_stray_things(), [self.thing("animal_guide")])
        self.assertEqual(self.thing("animal_guide").location, self.rooms["deck"])

    def focus_after(self, command: str) -> str:
        """The last Focus pane content char1's client gets after a command."""
        with patch.object(self.char1, "msg") as mock_msg:
            self.char1.execute_cmd(command)
        focus: list[str] = [
            c.kwargs["focus"] for c in mock_msg.call_args_list if "focus" in c.kwargs
        ]
        self.assertTrue(focus, f"no Focus update after {command!r}")
        return focus[-1]

    def test_looking_at_a_character_shows_their_picture_or_card(self) -> None:
        self.at(self.char1, "market")
        self.assertIn("pictures/crane.svg", self.focus_after("look crane"))
        self.at(self.char1, "quay")
        self.assertIn("Old Barnaby", self.focus_after("look barnaby"))  # no picture yet: a card
        self.at(self.char2, "quay")
        self.assertIn(self.char2.key, self.focus_after(f"look {self.char2.key}"))

    def test_looking_at_anything_else_brings_back_the_room(self) -> None:
        self.at(self.char1, "market")
        self.focus_after("look crane")
        self.assertIn("Market", self.focus_after("look west"))  # the exit to the Office

    def test_looking_at_a_thing_shows_its_card_until_looking_around(self) -> None:
        self.at(self.char1, "market")
        with patch.object(self.char1, "msg") as mock_msg:
            self.char1.execute_cmd("look compass")
        focus: list[str] = [
            c.kwargs["focus"] for c in mock_msg.call_args_list if "focus" in c.kwargs
        ]
        self.assertEqual(len(focus), 1)
        self.assertIn("Brass compass", focus[0])
        with patch.object(self.char1, "msg") as mock_msg:
            self.char1.execute_cmd("look")
        focus = [c.kwargs["focus"] for c in mock_msg.call_args_list if "focus" in c.kwargs]
        self.assertIn("Market", focus[-1])


class TestLookingAndTheJournal(DiscoveryTest):
    def test_the_journal_names_each_source_once(self) -> None:
        expedition: Any = get_expedition()
        self.assertTrue(expedition.add_clue("C3", "Test", "Market", "Silas Crane"))
        # The same source again (his compass and fishermen topics) changes nothing...
        self.assertFalse(expedition.add_clue("C3", "Admin", "Market", "Silas Crane"))
        self.assertEqual(expedition.journal[0].also, ())
        # ...a new source is noted.
        self.assertFalse(expedition.add_clue("C3", "Admin", "Quay", "Old Barnaby"))
        entry: JournalEntry = expedition.journal[0]
        self.assertEqual(entry.source, "Silas Crane")
        self.assertEqual([s.source for s in entry.also], ["Old Barnaby"])
        listing: str = journal_sources_text(self.char1)
        self.assertIn("found by Test, Market, from Silas Crane", listing)
        self.assertIn("again by Admin, Quay, from Old Barnaby", listing)

    def test_a_clue_from_two_places_lists_both(self) -> None:
        self.thing("animal_guide").move_to(self.char1, quiet=True)
        self.thing("plant_guide").move_to(self.char1, quiet=True)
        self.at(self.char1, "beach")
        self.do(self.char1, "look goats")
        self.at(self.char1, "spring")
        self.do(self.char1, "look shoots")
        listing: str = journal_sources_text(self.char1)
        self.assertIn("from the goats, with the animal guide", listing)
        self.assertIn("again by", listing)
        self.assertIn("from the shoots, with the plant guide", listing)

    def test_the_compass_reveals_a_clue_in_yellow(self) -> None:
        self.at(self.char1, "market")
        seen: str = self.do(self.char1, "look compass")
        self.assertIn("|yHALCYON|n", seen)
        self.assertIn("Noted in the journal: Silas Crane is selling", seen)
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
        again: str = self.do(self.char1, "look compass")
        self.assertIn("Already in the journal, 1. ", again)
        self.assertIn(load_content().clues["C1"].journal, again)
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
        empty: str = self.do(self.char1, "journal")
        self.assertIn("No clues yet", empty)
        # The task is there from the start, and stays at the top.
        self.assertIn("  - What became of the Halcyon's crew?", empty)
        self.at(self.char1, "reef")
        self.do(self.char1, "look bones")
        listed: str = self.do(self.char2, "journal")
        self.assertIn("1. |yA wreck on the Western Reef|n", listed)
        self.assertNotIn("found by", listed)  # the sources are kept apart
        self.assertIn("|wjournal sources|n", listed)
        self.assertIn("Western Reef|n: ", listed)
        self.assertIn("(new)", listed)  # char2 hasn't seen it in the journal yet...
        self.assertEqual(listed.replace(" (new)", ""), journal_text(self.char2))  # ...now has
        sources: str = self.do(self.char2, "journal sources")
        self.assertIn(f"1. |yA wreck on the Western Reef|n: found by {self.char1.key}", sources)
        self.assertLess(listed.index("Why did nobody"), listed.index("1. "))

    def test_barnaby_answers_what_he_taught_and_points_to_the_ship(self) -> None:
        self.at(self.char1, "quay")
        told: str = self.do(self.char1, "ask barnaby about latitude")
        self.assertIn("a sextant and a steady hand", told)
        self.assertIn("Ask that ship of yours", told)
        self.assertNotIn("know aught", told)

    def test_jonah_explains_why_the_crew_sailed_west(self) -> None:
        self.at(self.char1, "cove")
        told: str = self.do(self.char1, "ask jonah about east")
        self.assertIn("trade wind blows from the east", told)
        self.assertIn("How winds are named", told)  # the notebook

    def test_the_ship_points_to_the_task(self) -> None:
        self.at(self.char1, "deck")
        told: str = self.do(self.char1, "ask ship about task")
        self.assertIn("three questions", told)
        self.assertIn("|wjournal|n", told)


class TestAtSea(DiscoveryTest):
    def test_the_empty_sea_is_noticed_on_arrival(self) -> None:
        self.at(self.char1, "deck")
        self.at(self.char2, "deck")
        with patch("world.ship.crew_ashore", return_value=[]):
            sail(self.char1, "west")
        self.assertEqual(self.journal_ids(), ["C4"])

    def test_the_empty_sea_shows_in_yellow(self) -> None:
        self.ship_at("charted")
        self.at(self.char1, "deck")
        seen: str = self.do(self.char1, "look")
        self.assertIn("|yThere is nothing but water", seen)
        self.assertNotIn("[[", seen)

    def test_the_birds_at_dusk(self) -> None:
        self.ship_at("charted")
        self.at(self.char1, "deck")
        self.assertIn("|yall flying the same way: west", self.do(self.char1, "look birds"))
        self.assertIn("C6", self.journal_ids())

    def test_the_sextant_stays_in_the_chart_house(self) -> None:
        self.at(self.char1, "deck")
        self.assertIn("used right here on deck", self.do(self.char1, "get sextant"))
        self.assertEqual(self.thing("sextant").location, self.rooms["deck"])
        self.assertIn("Latitude 14 degrees South", self.do(self.char1, "use sextant"))

    def test_take_and_pick_up_work_like_get(self) -> None:
        self.at(self.char1, "deck")
        self.do(self.char1, "take plant guide")
        self.assertEqual(self.thing("plant_guide").location, self.char1)
        self.do(self.char1, "drop plant guide")
        self.do(self.char1, "pick up plant guide")
        self.assertEqual(self.thing("plant_guide").location, self.char1)

    def test_at_the_charted_position_the_measurements_confirm_the_empty_sea(self) -> None:
        self.ship_at("charted")
        self.at(self.char2, "deck")
        self.assertIn("Measure the noon", self.do(self.char2, "read chronometer"))
        self.at(self.char1, "deck")
        self.do(self.char1, "look")  # the empty sea: C4
        self.assertIn("|yLatitude 14 degrees South", self.do(self.char1, "use sextant"))
        read: str = self.do(self.char2, "read chronometer")
        self.assertIn("|y40 degrees West", read)
        self.assertIn("Which one would you trust?", read)
        self.assertNotIn("C5", self.journal_ids())  # the why is the players' to work out
        sources: list[str | None] = [s.source for s in get_expedition().journal[0].also]
        self.assertEqual(sources, ["the sextant", "the chronometer"])

    def test_a_day_north_the_sextant_shows_the_latitude_changed(self) -> None:
        self.ship_at("charted")
        self.at(self.char1, "deck")
        with patch("world.ship.crew_ashore", return_value=[]):
            self.assertTrue(sail(self.char1, "north"))
        self.assertEqual(current_position().id, "north_of_chart")
        self.assertIn("Latitude 12 degrees South", self.do(self.char1, "use sextant"))
        with patch("world.ship.crew_ashore", return_value=[]):
            self.assertFalse(sail(self.char1, "west"))  # only back from here
            self.assertTrue(sail(self.char1, "south"))
        self.assertEqual(current_position().id, "charted")

    def test_a_day_east_the_chronometer_shows_the_way_back(self) -> None:
        self.ship_at("charted")
        self.at(self.char1, "deck")
        with patch("world.ship.crew_ashore", return_value=[]):
            sail(self.char1, "east")
        self.do(self.char1, "use sextant")
        self.assertIn("38 degrees West", self.do(self.char1, "read chronometer"))

    def test_no_list_of_directions_at_the_charted_position(self) -> None:
        self.ship_at("charted")
        self.at(self.char1, "deck")
        options: str = self.do(self.char1, "sail")
        self.assertNotIn("sail north", options)
        self.assertIn("|wsail to|n a latitude and a longitude", options)
        self.assertIn("|wcouncil|n", options)

    def test_at_the_island_the_longitude_is_ten_degrees_out(self) -> None:
        self.ship_at("anchorage")
        self.at(self.char1, "deck")
        self.do(self.char1, "use sextant")
        self.assertIn("1 degree further west", self.do(self.char1, "read chronometer"))

    def test_others_in_the_room_hear_what_is_read(self) -> None:
        self.at(self.char1, "deck")
        self.at(self.char2, "deck")
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


class TestStartOver(DiscoveryTest):
    def play_a_little(self) -> None:
        """Find a clue, set a flag, carry a book away and sail to the island."""
        get_expedition().add_clue("C1", "someone", "Market")
        get_expedition().set_flag("sight_charted")
        self.thing("plant_guide").move_to(self.char1, quiet=True)
        self.ship_at("charted")
        self.ship_at("anchorage")
        self.at(self.char1, "village")
        self.at(self.char2, "deck")

    def test_without_yes_nothing_happens(self) -> None:
        self.play_a_little()
        heard: str = self.do(self.char1, "startover")
        self.assertIn("startover yes", heard)
        self.assertEqual(self.journal_ids(), ["C1"])
        self.assertEqual(current_position().id, "anchorage")

    def test_starting_over_forgets_everything(self) -> None:
        self.play_a_little()
        heard: str = self.do(self.char1, "startover yes")
        self.assertIn("New expedition started", heard)
        expedition: Any = get_expedition()
        self.assertEqual(expedition.journal, [])
        self.assertEqual(expedition.flags, [])
        self.assertEqual(expedition.track, ["port"])
        self.assertEqual(current_position().id, "port")
        self.assertEqual(self.thing("plant_guide").location, self.rooms["deck"])
        # char1 is being played and is moved; char2 (no session) is kept nowhere, as Evennia
        # keeps offline characters, and comes back in Limbo at its next login.
        self.assertEqual(self.char1.location, self.rooms["limbo"])
        self.assertIsNone(self.char2.location)
        self.assertEqual(self.char2.db.prelogout_location, self.rooms["limbo"])
        ashore: Any = find_ship_exit(ASHORE)
        self.assertEqual(ashore.destination, self.rooms["quay"])

    def test_starting_at_the_island(self) -> None:
        self.do(self.char1, "startover island yes")
        self.assertEqual(get_expedition().track, ["port", "charted", "anchorage"])
        island_ashore: Any = find_ship_exit(ASHORE)
        self.assertEqual(island_ashore.destination, self.rooms["beach"])
        self.assertEqual(route_to(load_content(), "charted"), ["port", "charted"])
        self.assertEqual(shortcut_position("at sea"), "charted")
        self.assertIsNone(shortcut_position("the moon"))


def content_with_ideas() -> Content:
    """The real content, plus a few ideas taught by Barnaby, the Ship and the sextant."""
    content: Content = read_content()
    latitude: IdeaSpec = IdeaSpec(
        id="latitude",
        area="navigation",
        title="Latitude",
        texts={
            "heard": "How far north or south you are.",
            "understood": "The higher the noon sun, the nearer the equator.",
            "used": "You've measured it yourself.",
        },
    )
    longitude: IdeaSpec = IdeaSpec(
        id="longitude", area="navigation", title="Longitude", texts={"understood": "East-west."}
    )
    coral: IdeaSpec = IdeaSpec(
        id="coral", area="nature", title="Coral", texts={"heard": "Grows under the sea."}
    )
    characters: dict[str, CharacterSpec] = dict(content.characters)
    for character_id, topic_id, level in (
        ("barnaby", "sailing", "heard"),
        ("ship", "latitude", "understood"),
    ):
        spec: CharacterSpec = characters[character_id]
        topics: dict[str, TopicSpec] = dict(spec.topics)
        topics[topic_id] = replace(topics[topic_id], teaches=(("latitude", level),))
        characters[character_id] = replace(spec, topics=topics)
    sextant = content.things["sextant"]
    assert sextant.use is not None
    at = dict(sextant.use.at)
    at["charted"] = replace(at["charted"], teaches=(("latitude", "used"),))
    things = dict(content.things)
    things["sextant"] = replace(sextant, use=replace(sextant.use, at=at))
    return replace(
        content,
        characters=characters,
        things=things,
        areas={
            "navigation": AreaSpec(id="navigation", title="Navigation"),
            "nature": AreaSpec(id="nature", title="Nature"),
        },
        ideas={"latitude": latitude, "longitude": longitude, "coral": coral},
    )


class TestNotebook(DiscoveryTest):
    def setUp(self) -> None:
        load_content.cache_clear()
        with_ideas: Content = content_with_ideas()
        reading: Any = patch.object(world.content, "read_content", return_value=with_ideas)
        reading.start()
        self.addCleanup(reading.stop)
        self.addCleanup(load_content.cache_clear)
        super().setUp()

    def notebook(self, character: Character) -> str:
        return self.do(character, "notebook")

    def test_an_empty_notebook(self) -> None:
        self.assertIn("still empty", self.notebook(self.char1))

    def test_everyone_who_hears_learns(self) -> None:
        self.at(self.char1, "quay")
        self.at(self.char2, "quay")
        with patch.object(self.char2, "msg") as heard:
            told: str = self.do(self.char1, "ask barnaby about sailing")
        self.assertIn("New in your notebook: Latitude. Type |wnotebook|n|x to read it.", told)
        self.assertIn("New in your notebook", texts(heard))
        page: str = self.notebook(self.char2)
        self.assertIn("|wNavigation|n: 1 of 2", page)
        self.assertIn("How far north or south you are.", page)
        self.assertNotIn("noon sun", page)
        self.assertNotIn("Nature", page)  # not started yet
        self.assertIn("There is more to discover.", page)

    def test_an_entry_grows_and_counts_once(self) -> None:
        self.at(self.char1, "quay")
        self.do(self.char1, "ask barnaby about sailing")
        self.at(self.char1, "deck")
        self.assertIn("entry on Latitude grew", self.do(self.char1, "ask ship about latitude"))
        page: str = self.notebook(self.char1)
        self.assertIn("How far north or south you are. The higher the noon sun", page)
        self.assertIn("1 of 2", page)
        self.assertNotIn("grew", self.do(self.char1, "ask ship about latitude"))  # nothing new

    def test_only_the_one_who_does_it_has_used_it(self) -> None:
        self.ship_at("charted")
        self.at(self.char1, "deck")
        self.at(self.char2, "deck")
        self.do(self.char1, "use sextant")
        self.assertIn("measured it yourself", self.notebook(self.char1))
        watcher: str = self.notebook(self.char2)
        self.assertIn("noon sun", watcher)
        self.assertNotIn("measured it yourself", watcher)

    def test_sources_show_who_taught_what_and_who_else_knows(self) -> None:
        self.at(self.char1, "quay")
        self.at(self.char2, "quay")
        self.do(self.char1, "ask barnaby about sailing")
        self.at(self.char1, "deck")
        self.do(self.char1, "ask ship about latitude")
        page: str = self.do(self.char1, "notebook sources")
        self.assertIn("heard: Old Barnaby; understood: the Good Hope", page)
        self.assertIn(f"Also in the notebook of {self.char2.key}", page)

    def test_how_to_read_it_is_said_until_it_is_opened(self) -> None:
        self.at(self.char1, "quay")
        self.notebook(self.char1)
        told: str = self.do(self.char1, "ask barnaby about sailing")
        self.assertIn("New in your notebook: Latitude.", told)
        self.assertNotIn("Type |wnotebook", told)

    def test_a_new_expedition_starts_with_empty_notebooks(self) -> None:
        self.at(self.char1, "quay")
        self.do(self.char1, "ask barnaby about sailing")
        start_over("port")
        self.assertIn("still empty", self.notebook(self.char1))


class TestNotebookContent(DiscoveryTest):
    """The real ideas, taught by the real content."""

    def test_one_reply_can_teach_several_ideas_in_one_line(self) -> None:
        self.at(self.char1, "quay")
        told: str = self.do(self.char1, "ask barnaby about sailing")
        new_lines: list[str] = [line for line in told.split("\n") if "New in your notebook" in line]
        self.assertEqual(len(new_lines), 1)
        for title in ("Latitude", "Longitude", "Dead reckoning", "Sea clocks"):
            self.assertIn(title, new_lines[0])

    def test_giving_the_order_is_using_it(self) -> None:
        self.at(self.char1, "deck")
        self.at(self.char2, "deck")
        with patch("world.ship.crew_ashore", return_value=[]):
            sail(self.char1, "to 14 south 40 west")
        mine: str = self.do(self.char1, "notebook")
        theirs: str = self.do(self.char2, "notebook")
        self.assertIn("You have given the ship an order", mine)
        self.assertNotIn("You have given the ship an order", theirs)
        self.assertIn("lines of latitude", theirs)


class TestRecorder(DiscoveryTest):
    """A developer's play, written as a scenario that `batchcommand` can play back."""

    def setUp(self) -> None:
        super().setUp()
        tmp: TemporaryDirectory[str] = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder: Path = Path(tmp.name)
        folder_patch: Any = patch("world.recorder.scenario_dir", return_value=self.folder)
        folder_patch.start()
        self.addCleanup(folder_patch.stop)
        crew_patch: Any = patch("world.ship.crew_ashore", return_value=[])
        crew_patch.start()
        self.addCleanup(crew_patch.stop)

    def record(self, *commands: str) -> list[str]:
        """Record `commands` as char1 and return the lines of the file written."""
        self.do(self.char1, "record start demo yes")
        for command in commands:
            self.do(self.char1, command)
        self.assertIn("Saved world/scenarios/demo.ev", self.do(self.char1, "record stop"))
        return (self.folder / "demo.ev").read_text(encoding="utf-8").splitlines()

    def test_without_yes_nothing_starts(self) -> None:
        self.assertIn("Type |wrecord start demo yes|n", self.do(self.char1, "record start demo"))
        self.assertIn("Nothing is being recorded", self.do(self.char1, "record"))

    def test_a_recording_plays_back_from_a_new_expedition(self) -> None:
        self.at(self.char1, "quay")
        lines: list[str] = self.record("begin", "east", "look compass", "examine compass")
        commands: list[str] = [line for line in lines if not line.startswith("#")]
        self.assertEqual(
            commands, ["startover yes", "begin", "east", "look compass", "examine compass"]
        )
        self.assertIn("#   Now in: Market", lines)
        self.assertIn("#   Journal: new C2, Coral in the hinge", lines)
        self.assertIn("#   Notebook: new Coral", lines)
        # Every command is followed by a comment line, which ends it for batchcommand.
        for number, line in enumerate(lines[:-1]):
            if not line.startswith("#"):
                self.assertTrue(lines[number + 1].startswith("#"), line)

    def test_only_what_any_player_could_type_is_kept(self) -> None:
        lines: list[str] = self.record(
            "begin", "xyzzy", "help", "teleport Quay", "startover", "look"
        )
        commands: list[str] = [line for line in lines if not line.startswith("#")]
        self.assertEqual(commands, ["startover yes", "begin", "look"])

    def test_another_players_commands_are_not_recorded(self) -> None:
        self.do(self.char1, "record start demo yes")
        self.do(self.char1, "begin")
        self.do(self.char2, "begin")
        self.do(self.char2, "look")
        self.do(self.char1, "record stop")
        text: str = (self.folder / "demo.ev").read_text(encoding="utf-8")
        self.assertEqual([line for line in text.splitlines() if line == "look"], [])

    def test_a_voyage_is_written_as_sail_now(self) -> None:
        self.ship_at("port")
        self.at(self.char1, "deck")
        self.do(self.char1, "record start demo yes")
        self.at(self.char1, "deck")
        lines: list[str] = self.record_more("sail", "sail to 14 south 40 west")
        self.assertIn("sail", lines)
        self.assertIn("sail/now to 14 south 40 west", lines)
        self.assertIn("#   Journal: new C4, Nothing at the charted position", lines)

    def record_more(self, *commands: str) -> list[str]:
        for command in commands:
            self.do(self.char1, command)
        self.do(self.char1, "record stop")
        return (self.folder / "demo.ev").read_text(encoding="utf-8").splitlines()

    def test_an_existing_file_is_named_before_it_is_replaced(self) -> None:
        (self.folder / "demo.ev").write_text("# by hand\n", encoding="utf-8")
        self.assertIn("replace the existing", self.do(self.char1, "record start demo"))
        self.assertEqual((self.folder / "demo.ev").read_text(encoding="utf-8"), "# by hand\n")

    def commands_in(self, name: str) -> list[str]:
        text: str = (self.folder / f"{name}.ev").read_text(encoding="utf-8")
        return [line for line in text.splitlines() if not line.startswith("#")]

    def test_a_checkpoint_writes_and_goes_on_under_the_next_name(self) -> None:
        self.do(self.char1, "record start one yes")
        self.do(self.char1, "begin")
        reply: str = self.do(self.char1, "record checkpoint two")
        self.assertIn("Saved world/scenarios/one.ev: 1 commands", reply)
        self.assertIn("now as 'two'", reply)
        self.do(self.char1, "look")
        self.do(self.char1, "record stop")
        self.assertEqual(self.commands_in("one"), ["startover yes", "begin"])
        self.assertEqual(self.commands_in("two"), ["startover yes", "begin", "look"])
        self.assertIn("scenarios.two", (self.folder / "two.ev").read_text(encoding="utf-8"))

    def test_a_checkpoint_asks_before_replacing_another_file(self) -> None:
        (self.folder / "two.ev").write_text("# by hand\n", encoding="utf-8")
        self.do(self.char1, "record start one yes")
        self.assertIn("will replace", self.do(self.char1, "record checkpoint two"))
        self.assertFalse((self.folder / "one.ev").exists())
        self.assertIn("now as 'two'", self.do(self.char1, "record checkpoint two yes"))
        self.do(self.char1, "record cancel")
        self.assertIn("Nothing is being recorded", self.do(self.char1, "record checkpoint"))

    def test_a_recording_goes_on_from_an_earlier_one(self) -> None:
        self.do(self.char1, "record start one yes")
        self.do(self.char1, "begin")
        self.do(self.char1, "record stop")
        path: Path = self.folder / "one.ev"
        path.write_text(
            path.read_text(encoding="utf-8").replace("#   Why:", "#   Why: by hand", 1),
            encoding="utf-8",
        )
        self.assertIn("plays scenario 'one'", self.do(self.char1, "record start two from one"))
        reply: str = self.do(self.char1, "record start two from one yes")
        self.assertIn("Played scenario 'one' (1 commands)", reply)
        self.assertEqual(self.char1.location.key, "Society Office")
        self.do(self.char1, "look")
        self.do(self.char1, "record stop")
        self.assertEqual(self.commands_in("two"), ["startover yes", "begin", "look"])
        self.assertIn("#   Why: by hand", (self.folder / "two.ev").read_text(encoding="utf-8"))

    def test_going_on_needs_an_earlier_scenario(self) -> None:
        self.assertIn("There is no", self.do(self.char1, "record start two from none yes"))
        self.assertIn("Nothing is being recorded", self.do(self.char1, "record"))


class TestReport(DiscoveryTest):
    """The report (DECISIONS.md, 29): choices, proof from the journal, and the epilogue."""

    def setUp(self) -> None:
        super().setUp()
        connected: Any = patch(
            "world.report.connected_characters", return_value=[self.char1, self.char2]
        )
        connected.start()
        self.addCleanup(connected.stop)
        self.at(self.char1, "village")
        self.at(self.char2, "deck")

    def find(self, *clues: str) -> None:
        for clue in clues:
            get_expedition().add_clue(clue, "someone", "somewhere")

    def test_the_board_shows_only_what_the_society_knows(self) -> None:
        heard: str = self.do(self.char1, "report")
        self.assertIn("The report for the Society", heard)
        self.assertIn("1. What happened to the Halcyon, and where?", heard)
        self.assertIn("a) She sank far out at sea", heard)
        self.assertIn("More possibilities may come up", heard)
        for spoiler in ("reef", "longitude", "west", "boat"):
            self.assertNotIn(spoiler, heard.lower())

    def test_a_question_shows_its_open_theories(self) -> None:
        heard: str = self.do(self.char1, "report 1")
        self.assertIn("question 1 of 3", heard)
        self.assertIn("b) She reached the island, then sailed on", heard)
        self.assertNotIn("c)", heard)
        self.assertIn("report 1 b", heard)

    def test_theories_open_with_their_clues_and_never_alone(self) -> None:
        self.at(self.char1, "market")
        heard: str = self.do(self.char1, "examine compass")  # C1 and C2
        self.assertNotIn("report", heard)  # not announced: the board marks it (33)
        board: str = self.do(self.char1, "report 1")
        self.assertIn("c) She sank in the deep ocean", board)
        self.assertIn("d) She was wrecked on a reef near the island", board)
        self.assertIn("storm of '75. (new)", board)
        self.assertNotIn("a) She sank far out at sea (new)", self.do(self.char1, "report"))
        self.assertNotIn("(new)", self.do(self.char1, "report 1"))
        self.assertIn("(new)", self.do(self.char2, "report"))

    def test_a_letter_beyond_the_open_theories_is_not_a_choice(self) -> None:
        heard: str = self.do(self.char1, "report 1 d")
        self.assertIn("Pick one of the possibilities", heard)

    def test_a_wrong_choice_is_turned_down_with_a_hint(self) -> None:
        heard: str = self.do(self.char1, "report a")
        self.assertIn("Old Barnaby believes", heard)
        self.assertEqual(get_expedition().answers, {})

    def test_the_right_choice_needs_its_proof(self) -> None:
        self.find("C2")
        heard: str = self.do(self.char1, "report 1 d")
        self.assertIn("the journal doesn't hold it yet", heard)
        self.assertIn("report 1 d", heard)
        self.assertEqual(get_expedition().answers, {})

    def test_the_right_choice_with_proof_answers_for_everyone(self) -> None:
        self.find("C7")
        with patch.object(self.char2, "msg") as elsewhere:
            heard: str = self.do(self.char1, "report 1 d")
        self.assertIn("wrecked on the Western Reef", heard)
        self.assertIn("Proved by: A wreck on the Western Reef (1).", heard)
        self.assertEqual(get_expedition().answers, {"wreck": self.char1.key})
        self.assertIn("answered a question of the report", texts(elsewhere))
        journal: str = self.do(self.char2, "journal")
        self.assertIn("Answered: Wrecked on the island's Western Reef", journal)
        self.assertIn("Answered by", self.do(self.char1, "report"))

    def test_questions_can_be_answered_in_any_order(self) -> None:
        self.find("C12", "C9", "C8", "C11", "C13")
        self.assertIn("question 3 of 3", self.do(self.char1, "report 3"))
        self.do(self.char1, "report b")
        self.assertEqual(list(get_expedition().answers), ["crew"])
        self.assertIn("Answered by", self.do(self.char1, "report 3"))

    def test_every_part_of_the_proof_is_needed(self) -> None:
        self.find("C4")
        heard: str = self.do(self.char1, "report 2 d")
        self.assertIn("compare its coastline with the chart", heard)
        self.find("C10")
        self.assertIn("measure the island's position", self.do(self.char1, "report 2 d"))
        self.find("C5")  # one clue, one job (39): each part of the proof is its own clue
        self.do(self.char1, "report 2 d")
        self.assertIn("why", get_expedition().answers)

    def test_the_epilogue_follows_the_last_answer(self) -> None:
        self.find("C7", "C4", "C10", "C5", "C12", "C9", "C8", "C11", "C13")
        self.do(self.char1, "report 1 e")
        self.do(self.char1, "report 2 d")
        with patch.object(self.char2, "msg") as elsewhere:
            heard: str = self.do(self.char1, "report 3 b")
        self.assertIn("the report is complete", heard)
        self.assertIn("Epilogue, 1 of 4: What happened", heard)
        self.assertIn("Epilogue, 1 of 4", texts(elsewhere))
        self.assertIn("Epilogue, 2 of 4: How it all fits", self.do(self.char2, "report more"))
        self.do(self.char2, "report more")
        self.assertIn("Sources", self.do(self.char2, "report more"))
        self.assertIn("end of the story", self.do(self.char2, "report more"))
        self.assertIn("Epilogue, 1 of 4", self.do(self.char2, "report"))
        self.assertIn("The report is complete", self.do(self.char1, "journal"))

    def test_more_before_the_end_says_what_is_left(self) -> None:
        heard: str = self.do(self.char1, "report more")
        self.assertIn("once every question", heard)
        self.assertIn("report 1", heard)

    def test_starting_over_forgets_the_answers(self) -> None:
        self.find("C7")
        self.do(self.char1, "report 1 d")
        start_over("port")
        self.assertEqual(get_expedition().answers, {})


class TestConnections(DiscoveryTest):
    """Questions that link clues, never their answer (DECISIONS.md, 22 and 30)."""

    def test_nothing_to_think_about_at_first(self) -> None:
        self.assertIn("Nothing to think about yet", self.do(self.char1, "think"))
        self.assertNotIn("Questions to think about", self.do(self.char1, "journal"))

    def test_a_settled_question_leaves_think(self) -> None:
        for clue_id in ("C4", "C6", "C7", "C8"):
            get_expedition().add_clue(clue_id, "someone", "somewhere")
        self.assertIn("How far from land do they fish?", self.do(self.char1, "think"))
        get_expedition().set_flag("far_settled")  # the council's third step
        settled: str = self.do(self.char1, "think")
        self.assertNotIn("How far from land do they fish?", settled)
        self.assertIn("What else could her timber", settled)
        get_expedition().answer("crew", "someone")  # the report question it leads to
        self.assertIn("Nothing left to puzzle over", self.do(self.char1, "think"))

    def test_a_question_comes_with_the_second_clue(self) -> None:
        self.at(self.char1, "market")
        self.at(self.char2, "market")
        self.do(self.char1, "examine compass")  # C1 and C2
        get_expedition().add_clue("C7", "someone", "Western Reef")
        self.at(self.char1, "village")
        self.at(self.char2, "village")
        with patch.object(self.char2, "msg") as beside:
            heard: str = self.do(self.char1, "examine beams")  # C8 with C7: the oak question
        self.assertNotIn("What else could her timber", heard)  # not announced (33)
        self.assertNotIn("What else could her timber", texts(beside))
        self.assertIn("|wthink|n, 1 new", self.do(self.char2, "journal"))
        thought: str = self.do(self.char2, "think")
        self.assertIn("What else could her timber", thought)
        self.assertIn("(new)", thought)
        self.assertNotIn("(new)", self.do(self.char2, "think"))
        self.assertNotIn("1 new", self.do(self.char2, "journal"))

    def test_a_question_opens_with_all_its_clues(self) -> None:
        get_expedition().add_clue("C7", "someone", "Western Reef")
        self.assertNotIn("Which witness", self.do(self.char1, "think"))
        get_expedition().add_clue("C12", "someone", "Village")
        self.assertIn("Which witness", self.do(self.char1, "think"))

    def test_think_about_one_clue(self) -> None:
        for clue_id, place in (
            ("C2", "Market"),
            ("C3", "Market"),
            ("C7", "Reef"),
            ("C8", "Village"),
        ):
            get_expedition().add_clue(clue_id, "someone", place)
        everything: str = self.do(self.char1, "think")
        self.assertIn("Questions worth turning over.", everything)
        self.assertIn("where in the sea does coral grow", everything)
        self.assertIn("What else could her timber", everything)
        compass: str = self.do(self.char1, "think Compass")
        self.assertIn("where in the sea does coral grow", compass)
        self.assertNotIn("What else could her timber", compass)
        self.assertIn("What else could her timber", self.do(self.char1, "think 4"))  # C8
        self.assertNotIn("where in the sea does coral grow", self.do(self.char1, "think 4"))
        self.assertIn("Nothing to think about on 'pirates'", self.do(self.char1, "think pirates"))

    def test_a_question_shows_the_ideas_that_help(self) -> None:
        get_expedition().add_clue("C2", "someone", "Market")
        get_expedition().add_clue("C3", "someone", "Market")
        lacking: str = self.do(self.char1, "think")
        self.assertIn("Worth learning: Coral (|wread animal guide|n, in the chart house).", lacking)
        get_expedition().note(self.char1.id, "coral", 1, "heard", "brass compass")
        having: str = self.do(self.char1, "think")
        self.assertIn("In your notebook: Coral.", having)
        self.assertNotIn("Worth learning", having)
        self.assertIn("Worth learning: Coral", self.do(self.char2, "think"))  # notebooks are each

    def test_a_question_is_shown_only_when_it_opens(self) -> None:
        get_expedition().add_clue("C7", "someone", "Western Reef")
        get_expedition().add_clue("C8", "someone", "Village")
        self.at(self.char1, "village")
        self.do(self.char1, "think")
        heard: str = self.do(self.char1, "examine beams")  # C8 again: nothing new
        self.assertIn("Already in the journal", heard)
        self.assertNotIn("(new)", self.do(self.char1, "think"))


class TestHints(DiscoveryTest):
    """The next step at three levels, and pushed hints (DECISIONS.md, 31)."""

    def setUp(self) -> None:
        super().setUp()
        self.clock: list[float] = [1000.0]
        moved: Any = patch("world.hints.now", side_effect=lambda: self.clock[0])
        moved.start()
        self.addCleanup(moved.stop)

    def test_a_pushed_hint_mentions_what_is_new(self) -> None:
        get_expedition().add_clue("C7", "someone", "Western Reef")
        get_expedition().add_clue("C8", "someone", "Village")  # the oak question
        self.at(self.char1, "village")
        self.play(self.char1, 1, 0)
        pushed: str = self.play(self.char1, 20, 30)
        self.assertIn("Something new you haven't looked at yet: |wthink|n", pushed)

    def test_hints_get_more_direct(self) -> None:
        self.at(self.char1, "office")
        first: str = self.do(self.char1, "hint")
        self.assertIn("You leaf through the journal", first)
        self.assertIn("compass in the market", first)
        self.assertIn("hint|n again", first)
        self.assertIn("Silas Crane's stall", self.do(self.char1, "hint"))
        third: str = self.do(self.char1, "hint")
        self.assertIn("|wlook compass|n", third)
        self.assertNotIn("again", third)
        self.assertIn("|wlook compass|n", self.do(self.char1, "hint"))

    def test_progress_starts_the_hints_over(self) -> None:
        self.at(self.char1, "office")
        self.do(self.char1, "hint")
        self.do(self.char1, "hint")
        get_expedition().add_clue("C1", "someone", "Market")
        self.assertIn("closer look than a glance", self.do(self.char1, "hint"))

    def test_aboard_the_ship_speaks(self) -> None:
        self.at(self.char1, "deck")
        self.assertIn("The Good Hope creaks", self.do(self.char1, "hint"))

    def test_the_situation_follows_the_state_of_play(self) -> None:
        self.ship_at("charted")
        self.at(self.char1, "deck")
        self.assertIn("really at the chart's position", self.do(self.char1, "hint"))
        get_expedition().set_flag("sight_charted")
        self.assertIn("talked over", self.do(self.char1, "hint"))
        self.ship_at("anchorage")
        self.assertIn("From somewhere high", self.do(self.char1, "hint"))

    def test_a_complete_report_says_so(self) -> None:
        for question in ("wreck", "why", "crew"):
            get_expedition().answer(question, "someone")
        self.at(self.char1, "village")
        self.assertIn("The report is complete", self.do(self.char1, "hint"))

    def play(self, character: Character, commands: int, seconds: float) -> str:
        """Type `look` several times, `seconds` apart; what the character read meanwhile."""
        heard: list[str] = []
        for _ in range(commands):
            self.clock[0] += seconds
            heard.append(self.do(character, "look"))
        return "\n".join(heard)

    def test_a_hint_is_pushed_after_ten_minutes_without_progress(self) -> None:
        self.at(self.char1, "office")
        self.play(self.char1, 1, 0)  # starts the clock
        self.assertNotIn("leaf through the journal", self.play(self.char1, 19, 30))
        pushed: str = self.play(self.char1, 1, 30)  # 600 seconds of play
        self.assertIn("compass in the market", pushed)
        self.assertIn("Stuck?", pushed)
        self.assertNotIn("leaf through the journal", self.play(self.char1, 30, 30))
        # The next asked-for hint is the second level.
        self.assertIn("Silas Crane's stall", self.do(self.char1, "hint"))

    def test_a_break_does_not_count_as_play(self) -> None:
        self.at(self.char1, "office")
        self.play(self.char1, 1, 0)
        self.assertNotIn("leaf through the journal", self.play(self.char1, 5, 3600))

    def test_progress_resets_the_clock(self) -> None:
        self.at(self.char1, "office")
        self.play(self.char1, 1, 0)
        self.play(self.char1, 19, 30)
        get_expedition().add_clue("C1", "someone", "Market")
        self.assertNotIn("leaf through the journal", self.play(self.char1, 5, 30))

    def test_no_hints_are_pushed_in_limbo(self) -> None:
        self.play(self.char1, 1, 0)
        self.assertNotIn("leaf through the journal", self.play(self.char1, 30, 30))


class TestFindFirst(DiscoveryTest):
    """A first encounter reads like a book; the links to the task wait (DECISIONS.md, 33)."""

    def setUp(self) -> None:
        super().setUp()
        get_expedition().start_over(["port"])  # not briefed yet

    def test_before_the_briefing_the_journal_and_report_introduce_themselves(self) -> None:
        journal: str = self.do(self.char1, "journal")
        self.assertIn("will hold the clues", journal)
        self.assertNotIn("What became of the Halcyon's crew?", journal)
        report: str = self.do(self.char1, "report")
        self.assertIn("speak with Mrs. Fairweather", report)
        self.assertNotIn("a)", report)
        self.assertIn("speak with Mrs. Fairweather", self.do(self.char1, "report 1 a"))
        self.at(self.char1, "office")
        self.assertIn("Mrs. Fairweather will tell you", self.do(self.char1, "hint"))

    def test_the_mission_briefs_the_expedition(self) -> None:
        self.at(self.char1, "office")
        self.do(self.char1, "ask fairweather about mission")
        self.assertIn("What became of the Halcyon's crew?", self.do(self.char2, "journal"))
        self.assertIn("The report for the Society", self.do(self.char2, "report"))

    def test_the_ship_briefs_too(self) -> None:
        self.at(self.char1, "deck")
        self.do(self.char1, "ask ship about expedition")
        self.assertTrue(get_expedition().met(("briefed",)))

    def test_a_find_gives_one_quiet_line_for_journal_and_notebook(self) -> None:
        self.at(self.char1, "village")
        heard: str = self.do(self.char1, "ask tui about song")
        notes: list[str] = [line for line in heard.split("\n") if "|x(" in line]
        self.assertEqual(len(notes), 1)
        self.assertTrue(notes[0].startswith("  |x(Noted in the journal: "))
        self.assertIn("New in your notebook", notes[0])
        self.assertIn("Type |wjournal|n", notes[0])
        self.do(self.char1, "journal")
        self.at(self.char1, "market")
        self.assertNotIn("Type |wjournal", self.do(self.char1, "look compass"))

    def test_a_player_elsewhere_gets_a_quiet_line_too(self) -> None:
        self.at(self.char1, "market")
        self.at(self.char2, "quay")
        with patch.object(self.char2, "msg") as elsewhere:
            self.char1.execute_cmd("look compass")
        self.assertIn(f"|x({self.char1.key} found something at Market.", texts(elsewhere))

    def test_starting_over_forgets_what_was_seen(self) -> None:
        get_expedition().add_clue("C1", "someone", "Market")
        self.do(self.char1, "journal")
        get_expedition().start_over(["port"])
        get_expedition().add_clue("C1", "someone", "Market")
        self.assertIn("(new)", self.do(self.char1, "journal"))


class TestCouncil(DiscoveryTest):
    """Where exploring must converge: a council, one step at a time (DECISIONS.md, 35)."""

    def setUp(self) -> None:
        super().setUp()
        self.ship_at("charted")
        self.at(self.char1, "deck")
        self.at(self.char2, "deck")

    def test_no_council_elsewhere(self) -> None:
        self.ship_at("port")
        self.assertIn("nothing to hold a council about", self.do(self.char1, "council"))
        self.ship_at("charted")
        self.at(self.char1, "quay")
        self.assertIn("nothing to hold a council about", self.do(self.char1, "council"))

    def test_the_council_is_offered_where_it_is_needed(self) -> None:
        self.assertIn("call a |wcouncil|n", self.do(self.char1, "look"))
        self.assertIn("|wcouncil|n", self.do(self.char1, "ask ship about advice"))
        self.assertIn("big decision", self.do(self.char1, "ask ship about council"))

    def test_the_council_opens_with_its_first_question(self) -> None:
        with patch.object(self.char2, "msg") as beside:
            heard: str = self.do(self.char1, "council")
        self.assertIn("The crew gather on the Deck", heard)
        self.assertIn("Which one could the Halcyon's master", heard)
        self.assertIn("b) The longitude, east or west.", heard)
        self.assertIn("|wcouncil a|n", heard)
        self.assertIn("Which one could the Halcyon's master", texts(beside))  # all are there

    def test_a_wrong_choice_leads_back_to_the_evidence(self) -> None:
        heard: str = self.do(self.char1, "council a")
        self.assertIn(f"{self.char1.key} answers: a) The latitude", heard)
        self.assertIn("Which number had he no way to check?", heard)
        self.assertFalse(get_expedition().met(("line_settled",)))

    def test_the_right_choice_waits_for_its_evidence(self) -> None:
        heard: str = self.do(self.char1, "council b")
        self.assertIn("take a noon sight", heard)
        self.assertIn("The council waits", heard)
        self.assertFalse(get_expedition().met(("line_settled",)))

    def test_the_council_carries_on_where_it_stopped(self) -> None:
        get_expedition().set_flag("sight_charted")
        settled: str = self.do(self.char1, "council b")
        self.assertIn("Without a sea clock", settled)
        self.assertIn("Second: east or west?", settled)
        self.assertTrue(get_expedition().met(("line_settled",)))
        again: str = self.do(self.char2, "council")
        self.assertNotIn("The crew gather on the Deck", again)  # the opening is said once
        self.assertIn("Second: east or west?", again)
        self.assertIn("Watch the |wsky|n", self.do(self.char2, "council b"))  # no C6 yet
        get_expedition().add_clue("C6", "someone", "Deck")  # the terns, and only they (39)
        side: str = self.do(self.char2, "council b")
        self.assertIn("Third: how far west?", side)
        self.assertIn("Proved by: Birds flying west at dusk", side)
        decided: str = self.do(self.char2, "council b")
        self.assertIn("a day's sail", decided)
        self.assertIn("The order is yours, Captain", decided)
        self.assertIn("|wsail to 14 south 41 west|n", decided)
        self.assertIn("|wreport|n", decided)
        self.assertIn("The order is yours", self.do(self.char1, "council"))

    def test_the_ship_suggests_what_fits_where_she_is(self) -> None:
        here: str = self.do(self.char1, "ask ship")
        self.assertIn("|wcouncil|n, |wbirds|n, |whorizon|n", here)
        self.ship_at("anchorage")
        self.assertIn("about: |wcouncil|n, |wtide|n, |wwind|n", self.do(self.char1, "ask ship"))
        self.ship_at("port")
        self.assertIn("about: |wcourse|n, |wchart|n", self.do(self.char1, "ask ship"))

    def test_hints_follow_the_council(self) -> None:
        get_expedition().set_flag("sight_charted")
        self.assertIn("talked over", self.do(self.char1, "hint"))
        get_expedition().set_flag("line_settled")
        self.assertIn("East or west?", self.do(self.char1, "hint"))
        get_expedition().set_flag("side_settled")
        self.assertIn("How far?", self.do(self.char1, "hint"))
        get_expedition().set_flag("far_settled")
        self.assertIn("The council has decided", self.do(self.char1, "hint"))

    def test_starting_over_forgets_the_council(self) -> None:
        get_expedition().set_flag("sight_charted")
        self.do(self.char1, "council b")
        start_over("port")
        self.assertFalse(get_expedition().met(("line_settled",)))

    def test_the_report_shows_what_the_council_concluded(self) -> None:
        self.assertNotIn("The council concluded", self.do(self.char1, "report 2"))
        for flag in ("sight_charted", "line_settled", "side_settled", "far_settled"):
            get_expedition().set_flag(flag)
        decided: str = self.do(self.char1, "council")
        self.assertIn("conclusion stands in the |wreport|n, beside question 2", decided)
        board: str = self.do(self.char1, "report")
        self.assertIn("The council concluded: The chart's latitude is right", board)
        self.assertIn("The journal can't prove it yet.", board)
        get_expedition().add_clue("C10", "someone", "Hilltop")  # the island's coastline
        get_expedition().add_clue("C5", "someone", "Deck")  # measured at the island
        self.assertIn("To write it in the report: |wreport 2 d|n.", self.do(self.char1, "report"))
        self.assertIn("Write it in the report: |wreport 2 d|n.", self.do(self.char1, "council"))
        self.do(self.char1, "report 2 d")
        self.assertIn("already answered", self.do(self.char1, "council"))
        self.assertNotIn("The council concluded", self.do(self.char1, "report"))


class TestIslandCouncil(DiscoveryTest):
    """The final council, aboard at the island: the report's other questions (37)."""

    def setUp(self) -> None:
        super().setUp()
        self.ship_at("anchorage")
        self.at(self.char1, "deck")

    def test_the_island_offers_its_council(self) -> None:
        self.assertIn("call a |wcouncil|n", self.do(self.char1, "look"))
        self.assertIn("about: |wcouncil|n", self.do(self.char1, "ask ship"))
        self.at(self.char1, "beach")
        self.assertIn("go back |waboard|n and call a council", self.do(self.char1, "look"))
        for flag in ("village_seen", "respect_rule", "respect_ama", "respect_tui"):
            get_expedition().set_flag(flag)
        for clue_id in ("C5", "C7", "C8", "C9", "C10", "C11", "C12", "C13"):  # the evidence
            get_expedition().add_clue(clue_id, "someone", "somewhere")
        self.assertIn("put it together, aboard", self.do(self.char1, "hint"))

    def test_the_council_waits_for_the_island_evidence(self) -> None:
        self.assertIn("where did the Halcyon's voyage end?", self.do(self.char1, "council"))
        self.assertIn("on the Western Reef. Walk out there", self.do(self.char1, "council b"))
        self.assertFalse(get_expedition().met(("wreck_settled",)))

    def test_the_council_ends_with_the_report_to_sign(self) -> None:
        for clue_id in ("C2", "C7", "C12", "C9", "C8", "C11", "C13"):
            get_expedition().add_clue(clue_id, "someone", "somewhere")
        self.assertIn("did anyone live through", self.do(self.char1, "council b"))
        self.assertIn("how long did they stay?", self.do(self.char1, "council b"))
        self.assertIn("where are they now?", self.do(self.char1, "council b"))
        decided: str = self.do(self.char1, "council b")
        self.assertIn("yours to sign", decided)
        board: str = self.do(self.char1, "report")
        self.assertIn("The council concluded: She was wrecked on the island's Western Reef", board)
        signs: list[str] = [
            line for line in decided.split("\n") if "Write it in the report" in line
        ]
        self.assertEqual(len(signs), 2)  # the wreck and the crew
        for line in signs:
            command: str = line.split("|w")[1].split("|n")[0]
            self.do(self.char1, command)
        self.assertIn("wreck", get_expedition().answers)
        self.assertIn("crew", get_expedition().answers)
        self.assertNotIn("|wcouncil|n", self.do(self.char1, "hint"))  # the council is done


class TestSearchByPosition(DiscoveryTest):
    """At the chart's position an order by position is read as a direction (34)."""

    def setUp(self) -> None:
        super().setUp()
        self.ship_at("charted")
        self.at(self.char1, "deck")

    def route(self, order: str) -> RouteSpec | str:
        return find_route(current_position(), order)

    def test_further_west_on_the_same_latitude_is_west(self) -> None:
        for order in ("to 14 south 41 west", "to 14 south 45 west"):
            found: RouteSpec | str = self.route(order)
            assert not isinstance(found, str)
            self.assertEqual(found.direction, "west")

    def test_east_north_and_south(self) -> None:
        for order, direction in (
            ("to 14 south 38 west", "east"),
            ("to 12 south 40 west", "north"),
            ("to 16 south 40 west", "south"),
        ):
            found: RouteSpec | str = self.route(order)
            assert not isinstance(found, str)
            self.assertEqual(found.direction, direction)

    def test_both_numbers_at_once_are_refused(self) -> None:
        found: RouteSpec | str = self.route("to 13 south 41 west")
        self.assertIsInstance(found, str)
        self.assertIn("Both numbers at once", str(found))

    def test_elsewhere_an_unknown_position_is_still_unknown(self) -> None:
        self.ship_at("port")
        self.assertIn("nothing there worth sailing to", str(self.route("to 14 south 45 west")))


class TestLeavingPort(WorldTest):
    """The port's gate: the ship sails once Crane has said where the compass came from (39)."""

    def test_the_ship_waits_for_cranes_confession(self) -> None:
        self.char1.move_to(self.rooms["deck"], quiet=True)
        with patch("world.ship.route_open", side_effect=route_open):
            with patch.object(self.char1, "msg") as mock_msg:
                self.assertFalse(sail(self.char1, "to 14 south 40 west"))
            self.assertIn("Silas Crane", texts(mock_msg))
            self.assertEqual(current_position().id, "port")
            get_expedition().add_clue("C3", "someone", "Market")
            self.assertTrue(sail(self.char1, "to 14 south 40 west"))


class TestLearnedPaths(DiscoveryTest):
    """On the island, a path exists once something or someone has shown it (40)."""

    def setUp(self) -> None:
        super().setUp()
        self.ship_at("anchorage")

    def exits_here(self, character: Character) -> str:
        return self.do(character, "look")

    def test_from_the_beach_only_the_forest_path(self) -> None:
        self.at(self.char1, "beach")
        seen: str = self.exits_here(self.char1)
        self.assertIn("northwest", seen)
        self.assertNotIn("west,", seen.replace("northwest", ""))
        self.assertIn("no path that way", self.do(self.char1, "west"))
        self.assertEqual(self.char1.location, self.rooms["beach"])
        on_map: str = self.do(self.char1, "map")
        self.assertIn("Forest Path", on_map)
        self.assertNotIn("Village", on_map)
        self.assertNotIn("Western Reef", on_map)

    def test_the_hilltop_shows_the_village(self) -> None:
        self.at(self.char1, "forest")
        arrived: str = self.do(self.char1, "north")  # up to the Hilltop: smoke from a village
        # Named from the known place nearest to the listener: the Hilltop is above the forest.
        self.assertIn("A new path: the Village, south of the Forest Path.", arrived)
        self.at(self.char1, "forest")
        self.do(self.char1, "south")
        self.assertEqual(self.char1.location, self.rooms["village"])
        self.assertNotIn("Western Reef", self.do(self.char1, "map"))  # not shown yet

    def test_starting_over_hides_the_paths_again(self) -> None:
        get_expedition().set_flag("village_seen")
        start_over("port")
        self.assertIn("village", hidden_places())


class TestRespect(DiscoveryTest):
    """Elder Ama's respect: named, taught and acknowledged, never by chance (41)."""

    def setUp(self) -> None:
        super().setUp()
        self.ship_at("anchorage")
        get_expedition().set_flag("village_seen")
        self.at(self.char1, "village")

    def test_nothing_counts_before_the_rule_is_known(self) -> None:
        heard: str = self.do(self.char1, "ask ama about village")
        self.assertNotIn("That is respect", heard)
        self.assertNotIn("respect: 1 of 2", heard)
        self.assertFalse(get_expedition().met(("respect_ama",)))

    def test_the_rule_is_named_by_tui_and_by_ama(self) -> None:
        self.assertIn("|wrespect|n", self.do(self.char1, "ask tui"))
        self.assertIn(
            "Ask her about our village first", self.do(self.char1, "ask tui about respect")
        )
        self.assertTrue(get_expedition().met(("respect_rule",)))
        start_over("port")
        self.ship_at("anchorage")
        get_expedition().set_flag("village_seen")
        self.at(self.char1, "village")
        self.assertIn("shows |wrespect|n first", self.do(self.char1, "ask ama about halcyon"))
        self.assertTrue(get_expedition().met(("respect_rule",)))

    def test_two_marks_win_her_trust_and_the_way_to_jonah(self) -> None:
        self.do(self.char1, "ask tui about respect")
        first: str = self.do(self.char1, "ask ama about village")
        self.assertIn("That is respect", first)
        self.assertIn("Elder Ama's respect: 1 of 2.", first)
        second: str = self.do(self.char1, "ask tui about song")
        self.assertIn("I'll show you the way to the big bones", second)
        self.assertIn("Elder Ama's respect: 2 of 2. She trusts you now.", second)
        self.assertIn("A new path: the Western Reef", second)
        story: str = self.do(self.char1, "ask ama about halcyon")
        self.assertIn("|ybrought the whole |wcrew|n|y ashore", story)
        self.assertIn("A new path: the Boat Cove", story)
        self.assertIn("Old Jonah lives by the |wcove|n", self.do(self.char1, "ask tui about jonah"))

    def test_before_her_respect_ama_keeps_her_story(self) -> None:
        self.do(self.char1, "ask tui about respect")
        self.do(self.char1, "ask ama about village")
        self.assertNotIn("C12", [entry.clue for entry in get_expedition().journal])
        self.assertIn("shows |wrespect|n first", self.do(self.char1, "ask ama about halcyon"))
        self.assertIn("for her to tell", self.do(self.char1, "ask tui about jonah"))


class TestEverythingMentioned(DiscoveryTest):
    """What a description names can be looked at (playtest 2026-11-22)."""

    def test_the_office_window_shows_the_harbour(self) -> None:
        self.at(self.char1, "office")
        self.assertIn("the Good Hope, waiting for you", self.do(self.char1, "look window"))
        self.assertIn("carts rattling", self.do(self.char1, "look street"))

    def test_the_ship_can_be_seen_from_the_quay(self) -> None:
        self.at(self.char1, "quay")
        for name in ("ship", "hope", "good hope"):
            self.assertIn("sturdy old sailing ship", self.do(self.char1, f"look {name}"), name)
        self.do(self.char1, "aboard")
        self.assertEqual(self.char1.location, self.rooms["deck"])  # the exit still works

    def test_the_ship_is_seen_only_where_she_lies(self) -> None:
        self.at(self.char1, "office")
        self.assertNotIn("sturdy old sailing ship", self.do(self.char1, "look ship"))

    def test_a_named_thing_without_a_detail_still_answers(self) -> None:
        self.at(self.char1, "quay")
        self.assertIn("no more to it than you've seen", self.do(self.char1, "look stone"))
        self.assertNotIn("no more to it", self.do(self.char1, "look dragon"))

    def test_aboard_the_ship_is_underfoot(self) -> None:
        self.at(self.char1, "deck")
        self.assertIn("you're standing on her", self.do(self.char1, "look hope"))
