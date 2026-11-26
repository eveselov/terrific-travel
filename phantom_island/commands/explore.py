"""Commands for finding your way around."""

from typing import Any

from typeclasses.rooms import Room
from world.content import LookSpec, find_look, names_whole
from world.discovery import find_thing_at_hand, location_details
from world.ship import ABOARD, ASHORE, not_aboard_here, not_ashore_here
from world.ways import way_to_place

from .command import Command

# `go to the ship`: anywhere but where she's boarded, says where she lies (2026-11-26).
SHIP_WORDS: frozenset[str] = frozenset({"ship", "boat", "hope", "good hope", "the good hope"})


class CmdGo(Command):
    """
    Go through an exit.

    Usage:
      go <exit>

    The same as typing the exit's name: go east is east, go aboard is aboard.
    look lists the exits of the place you are in. enter works too.

    Examples:
      go east
      go to the market
    """

    key = "go"
    aliases = ["walk", "enter"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        caller: Any = self.caller
        ignored: tuple[str, ...] = ("to", "the", "in", "into", "inside")
        words: list[str] = [w for w in self.args.lower().split() if w not in ignored]
        wanted: str = " ".join(words)
        location: Any = caller.location
        exits: list[Any] = list(location.exits) if location is not None else []
        if not wanted:
            caller.msg("Go where? " + _exits_line(exits))
            return
        for exit_obj in exits:
            names: list[str] = [str(exit_obj.key).lower()]
            names.extend(str(alias).lower() for alias in exit_obj.aliases.all())
            destination: Any = exit_obj.destination
            if destination is not None:
                names.append(str(destination.key).lower())  # `go to the market`
            if wanted in names:
                caller.execute_cmd(str(exit_obj.key))
                return
        if wanted in (ABOARD, ASHORE):  # no gangway here: say where it is
            caller.msg(not_aboard_here(caller) if wanted == ABOARD else not_ashore_here(caller))
            return
        if wanted in SHIP_WORDS:
            caller.msg(not_aboard_here(caller))
            return
        way: str | None = way_to_place(caller, wanted)  # a place further off: the way there
        if way is not None:
            caller.msg(way)
            return
        if _here_to_look_at(caller, wanted):
            # Something here, not a way out (playtest 2026-11-25: `enter chart house`).
            caller.msg(
                f"That isn't a place you can go into, but you can look at it: |wlook {wanted}|n."
            )
            return
        caller.msg(f"You can't go '{wanted}' from here. " + _exits_line(exits))


def _here_to_look_at(caller: Any, wanted: str) -> bool:
    """True if `wanted` names, as a whole, a thing at hand or a detail of this place."""
    thing: Any = find_thing_at_hand(caller, wanted)
    if thing is not None and thing.spec is not None and names_whole(wanted, thing.spec.look.words):
        return True
    detail: LookSpec | None = find_look(wanted, location_details(caller))
    return detail is not None and names_whole(wanted, detail.words)


def _exits_line(exits: list[Any]) -> str:
    if not exits:
        return "There is no way out of here."
    return "Exits: " + ", ".join(f"|w{exit_obj.key}|n" for exit_obj in exits) + "."


class CmdAboard(Command):
    """
    Go aboard your ship, from the place where she lies.

    Usage:
      aboard
    """

    # Where the ship lies, her `aboard` exit takes this word first; anywhere else this
    # says where to go (playtest 2026-11-26: "Command 'aboard' is not available").
    key = ABOARD
    locks = "cmd:all()"
    help_category = "General"
    auto_help = False

    def func(self) -> None:
        self.caller.msg(not_aboard_here(self.caller))


class CmdAshore(Command):
    """
    Go ashore from your ship.

    Usage:
      ashore
    """

    key = ASHORE
    locks = "cmd:all()"
    help_category = "General"
    auto_help = False

    def func(self) -> None:
        self.caller.msg(not_ashore_here(self.caller))


class CmdMap(Command):
    """
    Show where you are on the map.

    Usage:
      map

    Describes the current map in words: where you are, what else is on it and, at sea, the
    ship's track. In the web client it also redraws the Map pane.
    """

    key = "map"
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        location: Any = self.caller.location
        if not isinstance(location, Room):
            self.caller.msg("There is no map of this place.")
            return
        self.caller.msg(location.map_text())
        location.send_visuals(self.caller)
