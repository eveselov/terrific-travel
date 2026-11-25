"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from typing import Any

from evennia import default_cmds

from .admin import CmdRecord, CmdStartOver
from .discover import (
    CmdExamine,
    CmdGet,
    CmdHint,
    CmdJournal,
    CmdLook,
    CmdNotebook,
    CmdRead,
    CmdThink,
    CmdUse,
)
from .explore import CmdGo, CmdMap
from .report import CmdCouncil, CmdReport
from .talk import CmdAsk, CmdTalk

# Evennia's own commands a player of this game has no use for (playtest 2026-11-25: `help`
# listed them, and each looked like something to try). They still work, and builders still
# see them in `help`; players' `help` leaves them out.
BUILDERS_HELP_ONLY: frozenset[str] = frozenset(
    {
        "access",
        "nick",
        "setdesc",
        "pose",
        "whisper",
        "charcreate",
        "chardelete",
        "ic",
        "ooc",
        "quell",
        "sessions",
        "style",
        "option",
        "color",
        "channel",
        "about",
        "time",
    }
)


def hide_from_players_help(cmdset: Any) -> None:
    """
    Give the commands in BUILDERS_HELP_ONLY a `view` lock, so only builders see them.

    A command's locks are read from `lock_storage`, which Evennia fills once per class from
    `locks`: this instance gets both, and its lock handler is reset to read them.
    """
    for cmd in cmdset.commands:
        if cmd.key in BUILDERS_HELP_ONLY and "view:" not in cmd.lock_storage:
            locks: str = f"{cmd.lock_storage};view:perm(Builder)"
            cmd.locks = locks
            cmd.lock_storage = locks
            cmd.lockhandler.reset()


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self) -> None:
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(CmdMap())
        self.add(CmdGo())
        self.add(CmdAsk())
        self.add(CmdTalk())
        self.add(CmdLook())
        self.add(CmdGet())
        self.add(CmdExamine())
        self.add(CmdRead())
        self.add(CmdUse())
        self.add(CmdJournal())
        self.add(CmdNotebook())
        self.add(CmdThink())
        self.add(CmdHint())
        self.add(CmdReport())
        self.add(CmdCouncil())
        self.add(CmdStartOver())
        self.add(CmdRecord())
        hide_from_players_help(self)


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self) -> None:
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        hide_from_players_help(self)


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self) -> None:
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self) -> None:
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        hide_from_players_help(self)
