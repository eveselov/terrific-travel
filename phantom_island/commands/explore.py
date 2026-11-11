"""Commands for finding your way around."""

from typing import Any

from typeclasses.rooms import Room

from .command import Command


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
