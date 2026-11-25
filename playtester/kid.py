"""The kid's limits, enforced by the playtester rather than asked of the model.

A model told "you have a short attention span" still reads every word. So the
playtester decides what the player agent gets to see and remember: long screens are
cut off where attention runs out, only the last few turns are remembered, fingers
slip, and boredom grows when nothing new happens.
"""

import random
import re
from dataclasses import dataclass, field

from profiles import Persona

TAG: re.Pattern[str] = re.compile(r"</?\w+>")


@dataclass
class Seen:
    """One screen as the kid took it in."""

    text: str  # what was read, colour tags kept
    skipped: int  # words not read
    novel: bool  # something the kid hadn't seen before
    bored: bool  # nothing new for `patience` turns
    tired: bool  # past `tired_after` turns


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


def plain(line: str) -> str:
    """A line without colour tags, for comparing."""
    return " ".join(TAG.sub("", line).lower().split())


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

    def __init__(self, persona: Persona, rng: random.Random) -> None:
        self.persona: Persona = persona
        self.rng: random.Random = rng
        self.turns: list[Turn] = []
        self.notes: str = ""
        self.boredom: int = 0  # turns in a row with nothing new
        self.known: set[str] = set()  # lines already seen, for noticing what's new
        self.sitting_start: int = 0  # turns played in earlier sittings

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

    def come_back(self, turns: list[Turn], notes: str, known: set[str]) -> None:
        """Pick up a saved playthrough: the same memory, rested and no longer bored."""
        self.turns = turns
        self.notes = notes
        self.known = known
        self.sitting_start = len(turns)
        self.boredom = 0

    def attention(self) -> int:
        """Words read on one screen; halved once the kid is tired."""
        words: int = self.persona.traits.attention_words
        return max(20, words // 2) if self.tired() else words

    def tired(self) -> bool:
        """Played more than `tired_after` turns in this sitting."""
        return self.turns_this_sitting >= self.persona.traits.tired_after

    def see(self, screen: str) -> Seen:
        """Read a screen as far as attention goes, and notice whether anything is new."""
        text, skipped = cut_words(screen, self.attention())
        fresh: set[str] = {
            plain(line) for line in text.split("\n") if len(plain(line)) >= 4
        } - self.known
        self.known |= fresh
        novel: bool = bool(fresh)
        self.boredom = 0 if novel else self.boredom + 1
        if skipped:
            text += f"\n[... {skipped} more words you didn't read ...]"
        return Seen(
            text=text,
            skipped=skipped,
            novel=novel,
            bored=self.boredom >= self.persona.traits.patience,
            tired=self.tired(),
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

    def remember(self, turn: Turn, notes: str) -> None:
        """Keep the turn, and the notes cut to what fits in the head."""
        self.turns.append(turn)
        lines: list[str] = [line for line in notes.strip().split("\n") if line.strip()]
        self.notes = "\n".join(lines[: self.persona.traits.notes_lines])
