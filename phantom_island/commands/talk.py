"""Commands for talking to the characters of the story."""

from world.conversation import ask

from .command import Command


class CmdAsk(Command):
    """
    Ask someone about something.

    Usage:
      ask <someone>
      ask <someone> about <something>
      ask about <something>

    Asking someone without a topic greets them, and they suggest a few things to ask about
    (talk to <someone> does the same).
    Words shown in white in their answers are often worth asking about too. Aboard, you
    can always ask the ship herself, the Good Hope: ask hope.

    ask about <something> (or ask him, her or them about ...) asks the person you spoke
    to last, if they're still here, or the only person here. The start of a long name is
    enough: ask fair about the chart.

    Examples:
      ask tui
      ask barnaby about the storm
      ask about the halcyon
      ask ship about longitude
    """

    key = "ask"
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        ask(self.caller, self.args)


class CmdTalk(Command):
    """
    Talk to someone: the same as ask.

    Usage:
      talk to <someone>
      talk to <someone> about <something>

    Kids type it first (playtest 2026-11-25), so it greets as ask does. It isn't listed
    in help: ask is the one command to learn.
    """

    key = "talk"
    aliases = ["speak", "chat"]
    locks = "cmd:all()"
    auto_help = False

    def func(self) -> None:
        words: list[str] = self.args.split()
        if words and words[0].lower() in ("to", "with"):
            words = words[1:]
        ask(self.caller, " ".join(words))
