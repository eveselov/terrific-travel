"""
Clues and the expedition's shared journal.

A text that reveals a clue marks the fact itself `[[like this]]` in the content files. Players
see that part in yellow, and a journal line always follows it, so the meaning never depends
on colour alone (DECISIONS.md, 20). That line is a quiet one (`world/notices.py`): what the
clue means for the task waits in `journal`, `think` and `report`, which mark what each player
hasn't seen there yet (33). The journal is kept in the `Expedition` script, shared by
everyone: a clue found by one player is in every player's journal, and every connected
player is told about it.
"""

from typing import Any

from typeclasses.scripts import JournalEntry
from world import notices, recorder
from world.content import (
    CLUE_MARK,
    REPORT_SETTLES,
    ChoiceSpec,
    ClueSpec,
    ConnectionSpec,
    Content,
    IdeaSpec,
    QuestionSpec,
    ReportSpec,
    TaskSpec,
    load_content,
)
from world.expedition import connected_characters, get_expedition

CLUE_COLOUR: str = "|y"
NOTED: str = "Noted in the journal:"
JOURNAL: str = "journal"
JOURNAL_SOURCES: str = "journal sources"
THINK: str = "think"
REPORT: str = "report"
NEW: str = "(new)"
# Set on a character once they have opened the journal: the "Type journal" hint stops.
READ_JOURNAL: str = "has_read_journal"


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
    if not get_expedition().add_clue(clue_id, str(finder.key), place, source):
        number: int | None = entry_number(clue_id)
        entry: str = f"{number}. " if number is not None else ""
        recorder.note(finder, f"Journal: again {clue_id}, {clue.title}")
        notices.tell(finder, f"Already in the journal, {entry}{clue.title}: {clue.journal}")
        return False
    for character in [finder, *_room_characters(finder.location), *connected_characters()]:
        recorder.note(character, f"Journal: new {clue_id}, {clue.title}")
    opened: list[ConnectionSpec] = [c for c in open_connections() if c.id not in open_before]
    if opened:
        recorder.note(finder, "Think: " + ", ".join(c.id for c in opened))
    told: list[Any] = list(dict.fromkeys([finder, *_room_characters(finder.location)]))
    for character in dict.fromkeys([*told, *connected_characters()]):
        line: str = f"{NOTED} {clue.journal}"
        if character not in told:
            line = f"{finder.key} found something at {place}. {line}"
        if not character.attributes.get(READ_JOURNAL, False):
            line += f" Type |w{JOURNAL}|n to read it."
        notices.tell(character, line)
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


def theory_key(question: QuestionSpec, choice: ChoiceSpec) -> str:
    """How `seen` remembers a theory of the report: `theory:wreck:2`."""
    return f"theory:{question.id}:{question.choices.index(choice)}"


def briefed() -> bool:
    """
    Whether the expedition has been given its task (the task's `after` flag, `briefed`):
    until then the journal and the report only introduce themselves (DECISIONS.md, 33).
    """
    task: TaskSpec | None = load_content().task
    return task is None or task.after is None or get_expedition().met((task.after,))


def unseen(owner: Any, keys: list[str]) -> set[str]:
    """Which of these `seen` keys the owner hasn't been shown yet."""
    known: set[str] = get_expedition().seen(owner.id)
    return {key for key in keys if key not in known}


def report_keys() -> list[str]:
    """The `seen` keys of the theories open for the report's unanswered questions."""
    report: ReportSpec | None = load_content().report
    if report is None or not briefed():
        return []
    answers: dict[str, str] = get_expedition().answers
    known: set[str] = found_clues()
    return [
        theory_key(question, choice)
        for question in report.questions
        if question.id not in answers
        for choice in open_theories(question, known)
    ]


def news(owner: Any) -> list[str]:
    """
    The commands with something the owner hasn't seen yet there: `think` (a connection
    question) and `report` (a possibility), for a pushed hint to mention.
    """
    commands: list[str] = []
    if unseen(owner, [f"think:{c.id}" for c in open_connections()]):
        commands.append(THINK)
    if unseen(owner, report_keys()):
        commands.append(REPORT)
    return commands


def open_connections() -> list[ConnectionSpec]:
    """
    The connection questions open now: those whose every group of needed clues has at
    least one in the journal (DECISIONS.md, 22), and not yet `settled`, in the content's
    order.
    """
    known: set[str] = found_clues()
    return [
        connection
        for connection in load_content().connections.values()
        if groups_met(connection.needs, known) and not settled(connection)
    ]


def settled(connection: ConnectionSpec) -> bool:
    """
    Whether a connection question has been settled, so `think` no longer lists it: any of its
    `settled` holds (a clue, a flag such as a council's step, or an answered report question).
    """
    expedition: Any = get_expedition()
    for settler in connection.settled:
        if settler.startswith(REPORT_SETTLES):
            if settler.removeprefix(REPORT_SETTLES) in expedition.answers:
                return True
        elif expedition.met((settler,)):
            return True
    return False


THINK_OPENING: str = (
    "|wQuestions worth turning over.|n Talk them over, or ask someone who might know."
)


def _about(connection: ConnectionSpec, word: str, content: Content) -> bool:
    """
    Whether a connection question involves `word`: a journal number (`think 2`), or a word
    in the question or in the title or text of one of its clues (`think compass`).
    """
    clue_ids: set[str] = {clue_id for group in connection.needs for clue_id in group}
    if word.isdigit():
        return any(entry_number(clue_id) == int(word) for clue_id in clue_ids)
    texts: list[str] = [connection.question]
    for clue_id in clue_ids:
        clue: ClueSpec | None = content.clues.get(clue_id)
        if clue is not None:
            texts.extend((clue.title, clue.journal))
    return any(word in text.lower() for text in texts)


def _idea_lines(owner: Any, connection: ConnectionSpec, content: Content) -> list[str]:
    """
    The notebook ideas that help with a question: those the owner has, and where to learn
    the others (DECISIONS.md, A4: clues and ideas apart, and joined).
    """
    if not connection.ideas:
        return []
    known: set[str] = {entry.idea for entry in get_expedition().notebook(owner.id)}
    have: list[str] = []
    lacking: list[str] = []
    for idea_id in connection.ideas:
        idea: IdeaSpec | None = content.ideas.get(idea_id)
        if idea is None:
            continue
        if idea_id in known:
            have.append(idea.title)
        else:
            lacking.append(f"{idea.title} ({idea.learn})" if idea.learn else idea.title)
    lines: list[str] = []
    if have:
        lines.append(f"  In your notebook: {', '.join(have)}.")
    if lacking:
        lines.append(f"  Worth learning: {'; '.join(lacking)}.")
    return lines


def think_text(owner: Any, word: str = "") -> str:
    """
    The open connection questions (`think`), or only those involving `word` (`think
    compass`), each with the notebook ideas that help; the owner's new ones are marked.
    """
    opened: list[ConnectionSpec] = open_connections()
    content: Content = load_content()
    if not opened:
        known: set[str] = found_clues()
        if any(groups_met(connection.needs, known) for connection in content.connections.values()):
            return (
                "Nothing left to puzzle over: every question the journal has raised is "
                "settled. If new clues fit together, a new question comes up here."
            )
        return (
            "Nothing to think about yet. When two clues in the journal fit together, a "
            "question about them comes up here."
        )
    wanted: str = " ".join(word.lower().split())
    if wanted:
        opened = [connection for connection in opened if _about(connection, wanted, content)]
        if not opened:
            return (
                f"Nothing to think about on '{word.strip()}' yet. |wthink|n alone shows every "
                "question."
            )
    keys: list[str] = [f"think:{connection.id}" for connection in opened]
    new: set[str] = unseen(owner, keys)
    lines: list[str] = [THINK_OPENING]
    for connection, key in zip(opened, keys, strict=True):
        lines.append(f"- {connection.question}" + (f" {NEW}" if key in new else ""))
        lines.extend(_idea_lines(owner, connection, content))
    get_expedition().mark_seen(owner.id, keys)
    return "\n".join(lines)


def _room_characters(location: Any) -> list[Any]:
    if location is None:
        return []
    return list(location.contents_get(content_type="character"))


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
    (DECISIONS.md, 29), and how to answer them or read the epilogue again. Before the
    briefing, only what the journal is for (33).
    """
    assert content.task is not None
    if not briefed():
        return [content.task.before or ""]
    report: ReportSpec | None = content.report
    answers: dict[str, str] = get_expedition().answers
    lines: list[str] = [content.task.title]
    for number, text in enumerate(content.task.questions, start=1):
        lines.append(f"  - {text}")
        if report is not None and report.questions[number - 1].id in answers:
            lines.append(f"    Answered: {report.questions[number - 1].right.answer}")
    if report is not None:
        if all(question.id in answers for question in report.questions):
            lines.append(f"The report is complete: |w{REPORT}|n tells the whole story again.")
        else:
            lines.append(f"When you know an answer, and can prove it: |w{REPORT}|n.")
    return lines


def journal_text(owner: Any) -> str:
    """
    The journal, as shown by the `journal` command: the expedition's task first (always
    there, once given, so players can look up what they are here for), then the clues
    found, those the owner hasn't seen here yet marked new, and what's new in `think`
    and `report`.
    """
    content: Content = load_content()
    entries: list[JournalEntry] = _listed_entries()
    owner.attributes.add(READ_JOURNAL, True)
    lines: list[str] = ["|wThe expedition's journal|n"]
    if content.task is not None:
        lines.append("")
        lines.extend(_task_lines(content))
        lines.append("")
    if not entries:
        lines.append(
            "No clues yet. When you find a clue (shown in "
            f"{CLUE_COLOUR}yellow|n), it is written here, for the whole expedition."
        )
        return "\n".join(lines)
    keys: list[str] = [f"clue:{entry.clue}" for entry in entries]
    new: set[str] = unseen(owner, keys)
    for number, (entry, key) in enumerate(zip(entries, keys, strict=True), start=1):
        clue: ClueSpec = content.clues[entry.clue]
        mark: str = f" {NEW}" if key in new else ""
        lines.append(f"{number}. {CLUE_COLOUR}{clue.title}|n: {clue.journal}{mark}")
    get_expedition().mark_seen(owner.id, keys)
    lines.append(f"\n(Who found what, and from whom: |w{JOURNAL_SOURCES}|n)")
    connections: list[str] = [f"think:{c.id}" for c in open_connections()]
    if connections:
        fresh: int = len(unseen(owner, connections))
        more: str = f", {fresh} new" if fresh else ""
        lines.append(f"(Questions to think about, from what you've found: |w{THINK}|n{more})")
    if unseen(owner, report_keys()):
        lines.append(f"(New possibilities for the report: |w{REPORT}|n)")
    return "\n".join(lines)


def journal_sources_text(owner: Any) -> str:
    """
    Who found each clue, where and from whom or what, and every later source that
    confirmed it (`journal sources`): for comparing sources, kept out of the plain journal
    so that it stays short.
    """
    content: Content = load_content()
    entries: list[JournalEntry] = _listed_entries()
    if not entries:
        return journal_text(owner)
    lines: list[str] = ["|wWho found what|n"]
    for number, entry in enumerate(entries, start=1):
        clue: ClueSpec = content.clues[entry.clue]
        found: str = f"found by {_where_from(entry.finder, entry.place, entry.source)}"
        again: list[str] = [_where_from(s.finder, s.place, s.source) for s in entry.also]
        if again:
            found += "; again by " + "; ".join(again)
        lines.append(f"{number}. {CLUE_COLOUR}{clue.title}|n: {found}.")
    return "\n".join(lines)
