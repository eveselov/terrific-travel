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
from world import recorder
from world.content import (
    CLUE_MARK,
    ChoiceSpec,
    ClueSpec,
    ConnectionSpec,
    Content,
    QuestionSpec,
    ReportSpec,
    load_content,
)
from world.expedition import connected_characters, get_expedition

CLUE_COLOUR: str = "|y"
NEW_IN_JOURNAL: str = f"{CLUE_COLOUR}New in the journal:|n"
JOURNAL_SOURCES: str = "journal sources"
THINK: str = "think"
SOMETHING_TO_THINK: str = f"Something to think about (|w{THINK}|n):"


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
    open_before: set[str] = {connection.id for connection in open_connections()}
    theories_before: dict[str, int] = _open_theory_count()
    if not get_expedition().add_clue(clue_id, str(finder.key), place, source):
        number: int | None = entry_number(clue_id)
        entry: str = f"{number}. " if number is not None else ""
        recorder.note(finder, f"Journal: again {clue_id}, {clue.title}")
        finder.msg(f"(Already in the journal, {entry}{CLUE_COLOUR}{clue.title}|n: {clue.journal})")
        return False
    line: str = f"{NEW_IN_JOURNAL} {clue.journal}"
    for character in [finder, *_room_characters(finder.location), *connected_characters()]:
        recorder.note(character, f"Journal: new {clue_id}, {clue.title}")
    opened: list[ConnectionSpec] = [c for c in open_connections() if c.id not in open_before]
    here: str = line + "".join(f"\n{SOMETHING_TO_THINK} {c.question}" for c in opened)
    here += "".join(f"\n{text}" for text in _new_theories(theories_before))
    if opened:
        recorder.note(finder, "Think: " + ", ".join(c.id for c in opened))
    _tell_all(finder, here, f"{finder.key} found something at {place}. {line}")
    return True


def found_clues() -> set[str]:
    """The ids of the clues in the journal (read once, for checking many conditions)."""
    return {entry.clue for entry in get_expedition().journal}


def groups_met(groups: tuple[tuple[str, ...], ...], found: set[str] | None = None) -> bool:
    """Whether every group of clues has at least one in the journal (none: always)."""
    known: set[str] = found_clues() if found is None else found
    return all(any(clue in known for clue in group) for group in groups)


def open_theories(question: QuestionSpec, found: set[str] | None = None) -> list[ChoiceSpec]:
    """A report question's theories the expedition has come across, in the content's order."""
    known: set[str] = found_clues() if found is None else found
    return [choice for choice in question.choices if groups_met(choice.opens, known)]


def _open_theory_count() -> dict[str, int]:
    """How many theories are open for each report question (by id)."""
    report: ReportSpec | None = load_content().report
    if report is None:
        return {}
    known: set[str] = found_clues()
    return {question.id: len(open_theories(question, known)) for question in report.questions}


def _new_theories(before: dict[str, int]) -> list[str]:
    """`New for the report: ...` lines for questions that gained theories since `before`."""
    report: ReportSpec | None = load_content().report
    if report is None:
        return []
    answers: dict[str, str] = get_expedition().answers
    known: set[str] = found_clues()
    lines: list[str] = []
    for number, question in enumerate(report.questions, start=1):
        opened: int = len(open_theories(question, known))
        if question.id in answers or opened <= before.get(question.id, 0):
            continue
        lines.append(
            f"New for the report: another possibility for question {number} (|wreport {number}|n)."
        )
    return lines


def open_connections() -> list[ConnectionSpec]:
    """
    The connection questions open now: those whose every group of needed clues has at
    least one in the journal (DECISIONS.md, 22), in the content's order.
    """
    known: set[str] = found_clues()
    return [
        connection
        for connection in load_content().connections.values()
        if groups_met(connection.needs, known)
    ]


def think_text() -> str:
    """Every open connection question (`think`), or how they come."""
    opened: list[ConnectionSpec] = open_connections()
    if not opened:
        return (
            "Nothing to think about yet. When two clues in the journal fit together, a "
            "question about them comes up here."
        )
    lines: list[str] = [
        "|wSomething to think about|n (the game won't answer these: talk them over, or ask "
        "someone who might know)"
    ]
    lines.extend(f"- {connection.question}" for connection in opened)
    return "\n".join(lines)


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


def _task_lines(content: Content) -> list[str]:
    """
    The task's questions, each with the expedition's answer once the report has it
    (DECISIONS.md, 29), and how to answer them or read the epilogue again.
    """
    assert content.task is not None
    report: ReportSpec | None = content.report
    answers: dict[str, str] = get_expedition().answers
    lines: list[str] = []
    for number, text in enumerate(content.task.questions, start=1):
        lines.append(f"  - {text}")
        if report is not None and report.questions[number - 1].id in answers:
            lines.append(f"    Answered: {report.questions[number - 1].right.answer}")
    if report is not None:
        if all(question.id in answers for question in report.questions):
            lines.append("The report is complete: |wreport|n tells the whole story again.")
        else:
            lines.append("When you know an answer, and can prove it: |wreport|n.")
    return lines


def journal_text() -> str:
    """
    The journal, as shown by the `journal` command: the expedition's task first (always
    there, so players can look up what they are here for), then the clues found.
    """
    content: Content = load_content()
    entries: list[JournalEntry] = _listed_entries()
    lines: list[str] = ["|wThe expedition's journal|n"]
    if content.task is not None:
        lines.append(f"\n{content.task.title}")
        lines.extend(_task_lines(content))
        lines.append("")
    if not entries:
        lines.append(
            "No clues yet. When you find a clue (shown in "
            f"{CLUE_COLOUR}yellow|n), it is written here, for the whole expedition."
        )
        return "\n".join(lines)
    for number, entry in enumerate(entries, start=1):
        clue: ClueSpec = content.clues[entry.clue]
        lines.append(f"{number}. {CLUE_COLOUR}{clue.title}|n: {clue.journal}")
    lines.append(f"\n(Who found what, and from whom: |w{JOURNAL_SOURCES}|n)")
    if open_connections():
        lines.append(f"(Questions to think about, from what you've found: |w{THINK}|n)")
    return "\n".join(lines)


def journal_sources_text() -> str:
    """
    Who found each clue, where and from whom or what, and every later source that
    confirmed it (`journal sources`): for comparing sources, kept out of the plain journal
    so that it stays short.
    """
    content: Content = load_content()
    entries: list[JournalEntry] = _listed_entries()
    if not entries:
        return journal_text()
    lines: list[str] = ["|wWho found what|n"]
    for number, entry in enumerate(entries, start=1):
        clue: ClueSpec = content.clues[entry.clue]
        found: str = f"found by {_where_from(entry.finder, entry.place, entry.source)}"
        again: list[str] = [_where_from(s.finder, s.place, s.source) for s in entry.also]
        if again:
            found += "; again by " + "; ".join(again)
        lines.append(f"{number}. {CLUE_COLOUR}{clue.title}|n: {found}.")
    return "\n".join(lines)
