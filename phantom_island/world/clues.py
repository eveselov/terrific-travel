"""
Clues and the expedition's shared journal.

A text that reveals a clue marks the fact itself `[[like this]]` in the content files. Players
see that part in yellow, and a journal line always follows it, so the meaning never depends
on colour alone (DECISIONS.md, 20). The journal is kept in the `Expedition` script, shared by
everyone: a clue found by one player is in every player's journal, and every connected
player is told about it.
"""

from typing import Any

from typeclasses.scripts import JournalEntry
from world.content import CLUE_MARK, ClueSpec, Content, load_content
from world.expedition import connected_characters, get_expedition

CLUE_COLOUR: str = "|y"
NEW_IN_JOURNAL: str = f"{CLUE_COLOUR}New in the journal:|n"


def _yellow(found: Any) -> str:
    """One marked part, in yellow. White topic words inside it turn back to yellow after."""
    fact: str = str(found.group(1)).replace("|n", f"|n{CLUE_COLOUR}")
    return f"{CLUE_COLOUR}{fact}|n"


def show_marks(text: str) -> str:
    """The text as players see it: `[[...]]` parts in yellow."""
    return CLUE_MARK.sub(_yellow, text)


def place_name(obj: Any) -> str:
    """Where someone is, for the journal: their room's name."""
    location: Any = obj.location
    return str(location.key) if location is not None else "somewhere"


def discover(clue_id: str, finder: Any) -> bool:
    """
    The finder has just been shown this clue: write it into the journal and tell everyone.

    Everyone in the finder's room has just seen the yellow text, so they get the journal line;
    players elsewhere also hear who found it and where. A clue already in the journal is only
    pointed out to the finder. Returns True if the clue is new.
    """
    content: Content = load_content()
    clue: ClueSpec = content.clues[clue_id]
    place: str = place_name(finder)
    if not get_expedition().add_clue(clue_id, str(finder.key), place):
        finder.msg(f"(Already in the journal: {clue.title}.)")
        return False
    line: str = f"{NEW_IN_JOURNAL} {clue.journal}"
    _tell_all(finder, line, f"{finder.key} found something at {place}. {line}")
    return True


def _room_characters(location: Any) -> list[Any]:
    if location is None:
        return []
    return list(location.contents_get(content_type="character"))


def _tell_all(finder: Any, here: str, elsewhere: str) -> None:
    """`here` to the finder and everyone in their room; `elsewhere` to other players."""
    location: Any = finder.location
    told: list[Any] = [finder, *_room_characters(location)]
    for character in dict.fromkeys(told):
        character.msg(here, from_obj=finder)
    for character in connected_characters():
        if character not in told:
            character.msg(elsewhere, from_obj=finder)


def discover_all(clue_ids: list[str | None], finder: Any) -> None:
    """Discover each clue named, once, in order (None entries are skipped)."""
    for clue_id in dict.fromkeys(clue_ids):
        if clue_id is not None:
            discover(clue_id, finder)


def journal_text() -> str:
    """The journal, as shown by the `journal` command."""
    content: Content = load_content()
    entries: list[JournalEntry] = get_expedition().journal
    if not entries:
        return (
            "The expedition's journal is still empty. When you find a clue (shown in "
            f"{CLUE_COLOUR}yellow|n), it is written here, for the whole expedition."
        )
    lines: list[str] = ["|wThe expedition's journal|n"]
    for number, entry in enumerate(entries, start=1):
        clue: ClueSpec | None = content.clues.get(entry.clue)
        if clue is None:  # removed from the content since it was found
            continue
        lines.append(
            f"{number}. {CLUE_COLOUR}{clue.title}|n: {clue.journal} "
            f"(found by {entry.finder}, {entry.place})"
        )
    return "\n".join(lines)
