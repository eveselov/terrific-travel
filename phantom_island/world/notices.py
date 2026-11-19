"""
Quiet notes: what the journal and the notebook took down, after the scene (DECISIONS.md, 33).

A first encounter reads like a book: the scene in the game's own voice, then one dim,
indented line from the system, such as `(Noted in the journal: ... New in your notebook:
Latitude.)`. The journal and the notebook each add a part; inside `together()` the parts a
command gives one character are joined into that one line, sent when the block ends.
Outside it (an arrival at sea, say), each part is sent at once.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

QUIET: str = "|x"  # dim (dark grey): the system's voice, apart from the game's (20)
INDENT: str = "  "

_pending: dict[Any, tuple[Any, list[str]]] | None = None


def quiet(text: str) -> str:
    """A text in the system's quiet voice: indented, dim, in brackets. White words stay white."""
    return f"{INDENT}{QUIET}({text.replace('|n', '|n' + QUIET)})|n"


def tell(character: Any, text: str) -> None:
    """Note `text` for a character: at the end of the `together()` block, or now."""
    if _pending is None:
        character.msg(quiet(text))
        return
    _pending.setdefault(character.id, (character, []))[1].append(text)


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
        pending: dict[Any, tuple[Any, list[str]]] = _pending
        _pending = None
        for character, parts in pending.values():
            character.msg(quiet(" ".join(parts)))
