"""The kid's limits, enforced by the playtester rather than asked of the model.

A model told "you have a short attention span" still reads every word. So the
playtester decides what the player agent gets to see and remember: long screens are
cut off where attention runs out, only the last few turns are remembered, fingers
slip, boredom grows when nothing happens, and a sitting lasts as long as the kid has.

Boredom: progress (a new clue, a new place: the game profile says what that looks like)
ends it; a good amount of new text eases it a little; anything else adds to it. Text
that differs only in a short quoted word ("Command 'norht' is not available") is not new.

Sitting length: each sitting the kid has some minutes to play, picked from the persona's
range. When they are up, the kid is told it must stop soon, and stops at the next good
moment (progress), or a few turns later anyway.
"""

import random
import re
from dataclasses import dataclass, field

from profiles import GameProfile, Persona

TAG: re.Pattern[str] = re.compile(r"</?\w+>")
QUOTED: re.Pattern[str] = re.compile(r"'[^'\n]{1,30}'|\"[^\"\n]{1,30}\"")
SECONDS_PER_TURN: int = 30  # a kid's pace: read, think, type
NEW_WORDS: int = 12  # new words on a screen that count as something new to read
STOP_GRACE: int = 5  # turns after time is up before the kid stops anyway


@dataclass
class Seen:
    """One screen as the kid took it in."""

    text: str  # what was read, colour tags kept
    skipped: int  # words not read
    novel: bool  # a good amount of text the kid hadn't seen before
    bored: bool  # nothing has happened for `patience` turns
    tired: bool  # past `tired_after` turns
    progress: bool = False  # the game moved on: a clue, a new place...
    time_up: bool = False  # the sitting's minutes are over


@dataclass
class Turn:
    """One turn of the run, for the next prompts and the report."""

    number: int
    seen: Seen
    intended: str = ""  # what the kid meant to type
    typed: str = ""  # what reached the game (with a typo, sometimes)
    thought: str = ""
    feeling: str = ""
    noticed: str = ""
    hard_words: list[str] = field(default_factory=list)
    quit: bool = False
    notes: str = ""  # the notes about the game after this turn, as kept
    howto: str = ""  # the howto notes after this turn, as kept


def plain(line: str) -> str:
    """A line without colour tags or short quoted words, for comparing."""
    return " ".join(QUOTED.sub("'…'", TAG.sub("", line)).lower().split())


def cut_words(screen: str, limit: int) -> tuple[str, int]:
    """The screen up to `limit` words (colour tags don't count), and how many words are left.

    A colour still open where the cut falls is closed, so the tags stay paired.
    """
    kept: list[str] = []
    count: int = 0
    skipped: int = 0
    for line in screen.split("\n"):
        tokens: list[str] = line.split(" ")
        words: int = sum(1 for token in tokens if TAG.sub("", token).strip())
        if skipped or count >= limit:
            skipped += words
            continue
        if count + words <= limit:
            kept.append(line)
            count += words
            continue
        part: list[str] = []
        for token in tokens:
            if count < limit:
                part.append(token)
                count += 1 if TAG.sub("", token).strip() else 0
            elif TAG.sub("", token).strip():
                skipped += 1
        kept.append(" ".join(part) + " ...")
    text: str = "\n".join(kept)
    if skipped:
        open_tags: list[str] = []
        for match in re.finditer(r"<(/?)(\w+)>", text):
            if match.group(1):
                if open_tags and open_tags[-1] == match.group(2):
                    open_tags.pop()
            else:
                open_tags.append(match.group(2))
        text += "".join(f"</{tag}>" for tag in reversed(open_tags))
    return text.rstrip(), skipped


def add_typo(command: str, rng: random.Random) -> str:
    """The command with one slip of the fingers: two letters swapped, one dropped or doubled."""
    words: list[str] = command.split(" ")
    long_words: list[int] = [i for i, word in enumerate(words) if len(word) >= 3]
    if not long_words:
        return command
    index: int = rng.choice(long_words)
    word: str = words[index]
    spot: int = rng.randrange(len(word) - 1)
    slip: str = rng.choice(("swap", "drop", "double"))
    if slip == "swap":
        word = word[:spot] + word[spot + 1] + word[spot] + word[spot + 2 :]
    elif slip == "drop":
        word = word[:spot] + word[spot + 1 :]
    else:
        word = word[: spot + 1] + word[spot] + word[spot + 1 :]
    words[index] = word
    return " ".join(words)


class Kid:
    """What one persona can take in, remember and type."""

    def __init__(
        self,
        persona: Persona,
        rng: random.Random,
        game: GameProfile | None = None,
        timed: bool = True,
    ) -> None:
        self.persona: Persona = persona
        self.rng: random.Random = rng
        self.game: GameProfile | None = game  # what progress looks like; None: never
        self.timed: bool = timed  # False: no sitting length (manual, --no-time-limit)
        self.turns: list[Turn] = []
        self.notes: str = ""  # about this game: people, places, things, the mystery
        self.howto: str = ""  # about how to play: commands, talking, getting unstuck
        self.boredom: int = 0  # how long nothing has happened
        self.known: set[str] = set()  # lines already seen, for noticing what's new
        self.places: set[str] = set()  # room titles already seen
        self.sitting_start: int = 0  # turns played in earlier sittings
        self.sitting_turns: int = self.plan_sitting()  # turns this sitting has time for

    def plan_sitting(self) -> int:
        """How many turns this sitting has time for, picked from the persona's minutes."""
        low, high = self.persona.traits.sitting_minutes
        minutes: float = self.rng.uniform(low, high)
        return max(1, round(minutes * 60 / SECONDS_PER_TURN))

    @property
    def minutes_played(self) -> int:
        """This sitting's length so far, at a kid's pace."""
        return round(self.turns_this_sitting * SECONDS_PER_TURN / 60)

    def time_up(self) -> bool:
        return self.timed and self.turns_this_sitting >= self.sitting_turns

    def must_stop(self) -> bool:
        """Time was up a few turns ago, and no good moment came: the kid stops anyway."""
        return self.timed and self.turns_this_sitting >= self.sitting_turns + STOP_GRACE

    @property
    def turn_number(self) -> int:
        return len(self.turns) + 1

    @property
    def turns_this_sitting(self) -> int:
        return len(self.turns) - self.sitting_start

    @property
    def just_back(self) -> bool:
        """The first turn after a break (a run that carries on a playthrough)."""
        return self.sitting_start > 0 and self.turns_this_sitting == 0

    def come_back(self, turns: list[Turn], notes: str, howto: str, known: set[str]) -> None:
        """Pick up a saved playthrough: the same memory, rested and no longer bored."""
        self.turns = turns
        self.notes = notes
        self.howto = howto
        self.known = known
        self.places = {match for turn in turns for match in self._room_titles(turn.seen.text)}
        self.sitting_start = len(turns)
        self.sitting_turns = self.plan_sitting()
        self.boredom = 0

    def attention(self) -> int:
        """Words read on one screen; halved once the kid is tired."""
        words: int = self.persona.traits.attention_words
        return max(20, words // 2) if self.tired() else words

    def tired(self) -> bool:
        """Played more than `tired_after` turns in this sitting."""
        return self.turns_this_sitting >= self.persona.traits.tired_after

    def _room_titles(self, screen: str) -> list[str]:
        if self.game is None or not self.game.room_title:
            return []
        return re.findall(self.game.room_title, screen, re.M)

    def progressed(self, screen: str) -> bool:
        """The game moved on: one of its progress messages, or a place not seen before.

        The whole screen counts, read or not: the game moved on either way.
        """
        if self.game is None:
            return False
        flat: str = TAG.sub("", screen)
        if any(re.search(pattern, flat) for pattern in self.game.progress):
            return True
        new_places: set[str] = set(self._room_titles(screen)) - self.places
        self.places |= new_places
        return bool(new_places)

    def see(self, screen: str) -> Seen:
        """Read a screen as far as attention goes, and notice whether anything happened."""
        text, skipped = cut_words(screen, self.attention())
        fresh: set[str] = {
            plain(line) for line in text.split("\n") if len(plain(line)) >= 4
        } - self.known
        self.known |= fresh
        novel: bool = sum(len(line.split()) for line in fresh) >= NEW_WORDS
        progress: bool = self.progressed(screen)
        if progress:
            self.boredom = 0
        elif novel:
            self.boredom = max(0, self.boredom - 1)
        else:
            self.boredom += 1
        if skipped:
            text += f"\n[... {skipped} more words you didn't read ...]"
        return Seen(
            text=text,
            skipped=skipped,
            novel=novel,
            bored=self.boredom >= self.persona.traits.patience,
            tired=self.tired(),
            progress=progress,
            time_up=self.time_up(),
        )

    def gives_up(self) -> bool:
        """Bored for twice as long as patience lasts: the kid walks away."""
        return self.boredom >= 2 * self.persona.traits.patience

    def type(self, command: str) -> str:
        """The command as it reaches the game: now and then with a typo."""
        if self.rng.random() < self.persona.traits.typo_rate:
            return add_typo(command, self.rng)
        return command

    def recent(self) -> list[Turn]:
        """The turns still remembered word for word."""
        return self.turns[-self.persona.traits.memory_turns :]

    def kept_thoughts(self) -> list[Turn]:
        """The remembered turns whose thought is remembered too: the last `thoughts_kept`."""
        kept: int = self.persona.traits.thoughts_kept
        thinking: list[Turn] = [turn for turn in self.recent() if turn.thought]
        return thinking[-kept:] if kept > 0 else []

    def remember(self, turn: Turn, notes: str, howto: str | None = None) -> None:
        """Keep the turn, and the notes cut to what fits in the head.

        `howto` left out (the last screen of a sitting) keeps the howto as it was.
        """
        self.notes = cut_lines(notes, self.persona.traits.notes_lines)
        if howto is not None:
            self.howto = cut_lines(howto, self.persona.traits.howto_lines)
        turn.notes, turn.howto = self.notes, self.howto
        self.turns.append(turn)


def cut_lines(text: str, limit: int) -> str:
    """The first `limit` non-empty lines of `text`."""
    lines: list[str] = [line for line in text.strip().split("\n") if line.strip()]
    return "\n".join(lines[:limit])
