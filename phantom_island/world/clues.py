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


def discover(clue_id: str, finder: Any, source: str | None = None) -> bool:
    """
    The finder has just been shown this clue: write it into the journal and tell everyone.

    Everyone in the finder's room has just seen the yellow text, so they get the journal line;
    players elsewhere also hear who found it and where. A clue already in the journal is only
    pointed out to the finder, with its entry as the journal shows it: the yellow words may
    be put differently (Crane's "many days' sailing to the west" is entry "Fishermen from
    the west"), so the finder can see which entry they confirm. The journal also notes the
    new `source` (who said it, or what showed it), if it's one it doesn't have yet. Returns
    True if the clue is new.
    """
    content: Content = load_content()
    clue: ClueSpec = content.clues[clue_id]
    place: str = place_name(finder)
    if not get_expedition().add_clue(clue_id, str(finder.key), place, source):
        number: int | None = entry_number(clue_id)
        entry: str = f"{number}. " if number is not None else ""
        finder.msg(f"(Already in the journal, {entry}{CLUE_COLOUR}{clue.title}|n: {clue.journal})")
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


def discover_all(clue_ids: list[str | None], finder: Any, source: str | None = None) -> None:
    """Discover each clue named, once, in order (None entries are skipped)."""
    for clue_id in dict.fromkeys(clue_ids):
        if clue_id is not None:
            discover(clue_id, finder, source)


def _where_from(finder: str, place: str, source: str | None) -> str:
    """`Test, Market, from Silas Crane`: one sighting of a clue, for the journal."""
    return f"{finder}, {place}" + (f", from {source}" if source else "")


def _listed_entries() -> list[JournalEntry]:
    """The journal entries the `journal` command lists (clues still in the content)."""
    content: Content = load_content()
    return [entry for entry in get_expedition().journal if entry.clue in content.clues]


def entry_number(clue_id: str) -> int | None:
    """The number this clue has in the listed journal, or None if it isn't there."""
    for number, entry in enumerate(_listed_entries(), start=1):
        if entry.clue == clue_id:
            return number
    return None


def journal_text() -> str:
    """The journal, as shown by the `journal` command."""
    content: Content = load_content()
    entries: list[JournalEntry] = _listed_entries()
    if not entries:
        return (
            "The expedition's journal is still empty. When you find a clue (shown in "
            f"{CLUE_COLOUR}yellow|n), it is written here, for the whole expedition."
        )
    lines: list[str] = ["|wThe expedition's journal|n"]
    for number, entry in enumerate(entries, start=1):
        clue: ClueSpec = content.clues[entry.clue]
        found: str = f"found by {_where_from(entry.finder, entry.place, entry.source)}"
        again: list[str] = [_where_from(s.finder, s.place, s.source) for s in entry.also]
        if again:
            found += "; again by " + "; ".join(again)
        lines.append(f"{number}. {CLUE_COLOUR}{clue.title}|n: {clue.journal} ({found})")
    return "\n".join(lines)
