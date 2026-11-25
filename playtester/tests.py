"""Tests for the parts that need no game and no API. From inside this folder:

uv run python -m unittest tests
"""

import random
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest import mock

import state
from brain import turn_prompt
from kid import Kid, Turn, add_typo
from profiles import Persona, Traits, load_game, load_persona
from report import Run, render
from screen import to_screen
from telnet import DO, DONT, IAC, SB, SE, WILL, WONT, TelnetParser

ESC: str = "\x1b"


def persona(**traits: Any) -> Persona:
    return Persona(
        key="test", name="Tess", age=12, about="", experience="", traits=Traits(**traits)
    )


class TelnetParserTests(unittest.TestCase):
    def test_refuses_every_option(self) -> None:
        parser = TelnetParser()
        text = parser.feed(bytes((IAC, DO, 31, IAC, WILL, 86)) + b"Hello")
        self.assertEqual(text, "Hello")
        self.assertEqual(parser.take_replies(), bytes((IAC, WONT, 31, IAC, DONT, 86)))

    def test_skips_subnegotiation_split_between_reads(self) -> None:
        parser = TelnetParser()
        first = parser.feed(b"A" + bytes((IAC, SB, 24, 1)))
        second = parser.feed(bytes((IAC, SE)) + b"B")
        self.assertEqual(first + second, "AB")

    def test_utf8_split_between_reads(self) -> None:
        parser = TelnetParser()
        data = "café".encode()
        self.assertEqual(parser.feed(data[:-1]) + parser.feed(data[-1:]), "café")


class ScreenTests(unittest.TestCase):
    def test_colours_become_tags(self) -> None:
        raw = f"Ask about the {ESC}[1m{ESC}[37mcompass{ESC}[0m, or the {ESC}[33mstorm{ESC}[0m."
        self.assertEqual(
            to_screen(raw), "Ask about the <white>compass</white>, or the <yellow>storm</yellow>."
        )

    def test_plain_white_is_ordinary_text(self) -> None:
        self.assertEqual(to_screen(f"{ESC}[37mplain{ESC}[0m"), "plain")

    def test_xterm_colours(self) -> None:
        self.assertEqual(to_screen(f"{ESC}[38;5;226msun{ESC}[0m"), "<yellow>sun</yellow>")

    def test_lines_tidied(self) -> None:
        self.assertEqual(to_screen("\r\n\r\nOne  \r\n\r\n\r\n\r\nTwo\r\n"), "One\n\nTwo")


class KidTests(unittest.TestCase):
    def test_long_screen_is_cut_where_attention_ends(self) -> None:
        kid = Kid(persona(attention_words=5), random.Random(1))
        seen = kid.see("one two three\nfour <white>five six</white> seven\neight nine")
        self.assertEqual(seen.skipped, 4)
        self.assertEqual(
            seen.text,
            "one two three\nfour <white>five ...</white>\n[... 4 more words you didn't read ...]",
        )

    def test_short_screen_is_read_whole(self) -> None:
        kid = Kid(persona(attention_words=5), random.Random(1))
        seen = kid.see("one two\n\nthree")
        self.assertEqual((seen.text, seen.skipped), ("one two\n\nthree", 0))

    def test_boredom_grows_on_old_news(self) -> None:
        kid = Kid(persona(patience=2), random.Random(1))
        self.assertTrue(kid.see("You can't go that way.").novel)
        for _ in range(4):
            seen = kid.see("You can't go that way.")
            kid.remember(Turn(number=kid.turn_number, seen=seen), "")
        self.assertTrue(seen.bored)
        self.assertTrue(kid.gives_up())
        kid.see("A gull lands on the rail.")
        self.assertEqual(kid.boredom, 0)

    def test_notes_cut_to_what_fits(self) -> None:
        kid = Kid(persona(notes_lines=2), random.Random(1))
        kid.remember(Turn(number=1, seen=kid.see("x")), "one\ntwo\nthree")
        self.assertEqual(kid.notes, "one\ntwo")

    def test_typo_changes_one_word_a_little(self) -> None:
        typed = add_typo("look compass", random.Random(3))
        self.assertNotEqual(typed, "look compass")
        self.assertLessEqual(abs(len(typed) - len("look compass")), 1)

    def test_short_commands_keep_their_letters(self) -> None:
        self.assertEqual(add_typo("n", random.Random(1)), "n")


class PromptTests(unittest.TestCase):
    def test_prompt_shows_the_screen_and_what_was_typed(self) -> None:
        kid = Kid(persona(memory_turns=1), random.Random(1))
        first = kid.see("A dusty office.")
        kid.remember(Turn(number=1, seen=first, intended="look", typed="lok"), "an office")
        prompt = turn_prompt(kid, kid.see("You see no lok here."))
        self.assertIn("You typed: lok   (you meant: look)", prompt)
        self.assertIn("an office", prompt)
        self.assertIn("You see no lok here.", prompt)


class ContinueTests(unittest.TestCase):
    def played(self) -> Run:
        """A run of two turns, the second the last screen of the sitting."""
        kid = Kid(persona(memory_turns=2, tired_after=2), random.Random(1))
        kid.remember(Turn(number=1, seen=kid.see("A dusty office."), intended="n", typed="n"), "x")
        kid.remember(Turn(number=2, seen=kid.see("The quay.")), "an office, a quay")
        return Run(
            game=load_game("phantom_island"),
            kid=kid,
            model="m",
            started=datetime(2026, 11, 25, 8, 0),
            outcome="stopped at the turn limit (1)",
            dollars=0.5,
        )

    def test_saved_playthrough_comes_back(self) -> None:
        run = self.played()
        with (
            tempfile.TemporaryDirectory() as folder,
            mock.patch.object(state, "RUNS", Path(folder)),
        ):
            run.stamp = "20261125-0800"
            state.save_state(run)
            saved = state.load_state("phantom_island", "test")
        self.assertEqual([t.number for t in saved.turns], [1, 2])
        self.assertEqual(saved.turns[1].seen.text, "The quay.")
        self.assertEqual(saved.notes, "an office, a quay")
        self.assertEqual((saved.stamp, saved.sittings[0].last_turn), ("20261125-0800", 2))
        self.assertIn("the quay.", saved.known)

    def test_a_later_reset_is_noticed(self) -> None:
        run = self.played()
        with (
            tempfile.TemporaryDirectory() as folder,
            mock.patch.object(state, "RUNS", Path(folder)),
        ):
            self.assertEqual(state.last_reset("phantom_island"), "")
            run.reset_at = state.record_reset("phantom_island")
            state.save_state(run)
            saved = state.load_state("phantom_island", "test")
            self.assertEqual(saved.reset_at, state.last_reset("phantom_island"))
            state.reset_path("phantom_island").write_text("2099-01-01T00:00:00")
            self.assertNotEqual(saved.reset_at, state.last_reset("phantom_island"))

    def test_nothing_saved_says_to_reset(self) -> None:
        with (
            tempfile.TemporaryDirectory() as folder,
            mock.patch.object(state, "RUNS", Path(folder)),
            self.assertRaisesRegex(FileNotFoundError, "--reset"),
        ):
            state.load_state("phantom_island", "nobody")

    def test_kid_comes_back_rested_and_remembering(self) -> None:
        old = self.played()
        kid = Kid(old.kid.persona, random.Random(1))
        kid.come_back(old.kid.turns, old.kid.notes, old.kid.known)
        self.assertEqual((kid.turn_number, kid.just_back, kid.tired()), (3, True, False))
        prompt = turn_prompt(kid, kid.see("The quay."))
        self.assertIn("come back to the game", prompt)
        self.assertIn("(You stopped playing here.)", prompt)
        self.assertIn("an office, a quay", prompt)

    def test_report_has_a_section_per_sitting(self) -> None:
        first = self.played()
        run = Run(game=first.game, kid=first.kid, model="m", started=datetime(2026, 11, 26, 9, 0))
        run.kid.come_back(first.kid.turns, first.kid.notes, first.kid.known)
        run.earlier = first.sittings()
        run.kid.remember(Turn(number=3, seen=run.kid.see("A gull."), typed="z", intended="z"), "")
        text = render(run)
        self.assertIn("## Sitting 2", text)
        self.assertIn("| 2 | 2026-11-26 09:00 | 3–3 |", text)
        self.assertIn("$0.50", text)


class ProfileTests(unittest.TestCase):
    def test_shipped_profiles_load(self) -> None:
        for key in ("max", "lena", "sam"):
            self.assertEqual(load_persona(key).key, key)
        self.assertEqual(load_game("phantom_island").port, 4010)


if __name__ == "__main__":
    unittest.main()
