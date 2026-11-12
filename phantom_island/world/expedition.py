"""
Access to the expedition's state (the `Expedition` script in `typeclasses/scripts.py`).

The script is looked up by key, and created the first time it's needed. This is what
Evennia's `GLOBAL_SCRIPTS` setting does too; doing it by hand keeps the tests independent,
because each test starts with an empty database and nothing is cached between them.
"""

from typing import Any

from evennia.utils.create import create_script
from evennia.utils.search import search_script

from typeclasses.scripts import EXPEDITION_KEY, Expedition
from world.content import Content, PositionSpec, load_content


def get_expedition() -> Expedition:
    """The expedition's state, created on first use."""
    found: list[Expedition] = list(search_script(EXPEDITION_KEY, typeclass=Expedition))
    if found:
        return found[0]
    created: Expedition = create_script(Expedition, key=EXPEDITION_KEY, persistent=True)
    return created


def connected_characters() -> list[Any]:
    """The characters puppeted by someone who is connected right now."""
    from evennia import SESSION_HANDLER

    characters: list[Any] = []
    for session in SESSION_HANDLER.get_sessions():
        puppet: Any = session.get_puppet()
        if puppet is not None and puppet not in characters:
            characters.append(puppet)
    return characters


def current_position() -> PositionSpec:
    """Where the ship is now. Falls back to the start if the content no longer has it."""
    content: Content = load_content()
    position: PositionSpec | None = content.positions.get(get_expedition().ship_position)
    return position or content.positions[content.start_position]
