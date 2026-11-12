"""Commands for talking to the characters of the story."""

from world.conversation import ask

from .command import Command


class CmdAsk(Command):
    """
    Ask someone about something.

    Usage:
      ask <someone> about <something>
      ask <someone>

    Asking someone without a topic greets them, and they suggest a few things to ask about.
    Words shown in white in their answers are often worth asking about too. Aboard the
    ship, on the Deck or in the Cabin, you can always ask the Ship herself.

    Examples:
      ask barnaby about the storm
      ask ship about longitude
      ask tui
    """

    key = "ask"
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        ask(self.caller, self.args)
