"""
Quiet notes: what the journal and the notebook took down, after the scene (DECISIONS.md, 33).

A first encounter reads like a book: the scene in the game's own voice, then one dim,
indented line from the system, such as `(Noted in the journal: ... New in your notebook:
Latitude.)`. The journal and the notebook each add a part; inside `together()` the parts a
command gives one character are joined into that one line, sent when the block ends.
Outside it (an arrival at sea, say), each part is sent at once. A line that must not be
missed (`after`) is sent in the game's ordinary voice, after that quiet line.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

QUIET: str = "|x"  # dim (dark grey): the system's voice, apart from the game's (20)
INDENT: str = "  "

# Per character: the character, its quiet parts and its ordinary lines after them.
_pending: dict[Any, tuple[Any, list[str], list[str]]] | None = None


def quiet(text: str) -> str:
    """A text in the system's quiet voice: indented, dim, in brackets. White words stay white."""
    return f"{INDENT}{QUIET}({text.replace('|n', '|n' + QUIET)})|n"


def tell(character: Any, text: str) -> None:
    """Note `text` for a character: at the end of the `together()` block, or now."""
    if _pending is None:
        character.msg(quiet(text))
        return
    _pending.setdefault(character.id, (character, [], []))[1].append(text)


def after(character: Any, text: str) -> None:
    """
    Tell a character `text` in the ordinary voice, after the quiet line of the `together()`
    block, or now: for what the player must not miss (playtest 2026-11-25: grey asides
    were read past).
    """
    if _pending is None:
        character.msg(text)
        return
    _pending.setdefault(character.id, (character, [], []))[2].append(text)


@contextmanager
def together() -> Iterator[None]:
    """Join the notes given inside this block into one line per character."""
    global _pending
    if _pending is not None:  # already inside a block: the outer one sends
        yield
        return
    _pending = {}
    try:
        yield
    finally:
        pending: dict[Any, tuple[Any, list[str], list[str]]] = _pending
        _pending = None
        for character, parts, lines in pending.values():
            if parts:
                character.msg(quiet(" ".join(parts)))
            for line in lines:
                character.msg(line)
