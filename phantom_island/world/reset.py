"""
Starting a new expedition without resetting the database: the `startover` command.

Everything the adventure remembers is in one place (DECISIONS.md, 7): the `Expedition`
script (journal, flags, where the ship is and where she has been), where the things are, and
where the players are. Starting over clears the script, sails the ship to the chosen
position, puts every thing back and sends every player character, online or not, to Limbo,
the title page, so each one begins again with `begin`.

For testing the later acts, a new expedition can start with the ship already at sea or at
the island. `begin` then leads to the Deck, as for a late joiner (DECISIONS.md, 18).

Accounts, characters, the inhabitants and the built rooms are kept. This is also where
checkpoints can grow from later: starting over is loading the starting state.
"""

from collections import deque
from typing import Any

from typeclasses.characters import Character
from typeclasses.things import Thing
from world.builder import default_home
from world.content import LIMBO_ID, Content, load_content
from world.expedition import connected_characters, get_expedition
from world.places import all_things, find_place
from world.ship import moor_ship

# What can follow `startover`, and the position the ship starts at.
SHORTCUTS: dict[str, str] = {
    "": "port",
    "port": "port",
    "sea": "charted",
    "at sea": "charted",
    "charted": "charted",
    "island": "anchorage",
    "at the island": "anchorage",
    "anchorage": "anchorage",
}

NEW_EXPEDITION: str = (
    "|wA new expedition begins.|n Everything found so far is forgotten, and everyone is back "
    "on the title page. Type |wbegin|n to set out."
)


def route_to(content: Content, position_id: str) -> list[str] | None:
    """
    The positions the ship passes sailing from the start to `position_id`, both included
    (the shortest way), or None if she can't get there.
    """
    start: str = content.start_position
    came_from: dict[str, str | None] = {start: None}
    queue: deque[str] = deque([start])
    while queue:
        here: str = queue.popleft()
        if here == position_id:
            path: list[str] = []
            step: str | None = here
            while step is not None:
                path.append(step)
                step = came_from[step]
            return path[::-1]
        for route in content.positions[here].routes:
            if route.to not in came_from:
                came_from[route.to] = here
                queue.append(route.to)
    return None


def shortcut_position(text: str) -> str | None:
    """The position a `startover` argument names (`at sea` -> `charted`), or None."""
    words: list[str] = text.lower().split()
    return SHORTCUTS.get(" ".join(words))


def player_characters() -> list[Character]:
    """Every player character in the game, online or not (not the inhabitants)."""
    found: list[Any] = list(Character.objects.all())
    return [obj for obj in found if isinstance(obj, Character)]


def start_over(position_id: str) -> list[str]:
    """
    Start a new expedition with the ship at `position_id`. Returns the track she starts
    with. Raises ValueError if the ship can't reach that position.
    """
    content: Content = load_content()
    track: list[str] | None = route_to(content, position_id)
    if track is None:
        raise ValueError(f"The ship can't sail to '{position_id}'.")

    get_expedition().start_over(track)
    moor_ship(content.positions[track[-1]])

    for thing in all_things():
        if isinstance(thing, Thing) and thing.home is not None and thing.location != thing.home:
            thing.move_to(thing.home, quiet=True, move_type="teleport")

    limbo: Any = find_place(LIMBO_ID) or default_home()
    online: list[Any] = connected_characters()
    for character in player_characters():
        if character.location != limbo:
            character.move_to(limbo, quiet=True, move_type="teleport")
        if character in online:
            character.msg(NEW_EXPEDITION)
    return track
