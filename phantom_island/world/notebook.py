"""
Each player's notebook: the ideas they have learned about how the world works (DECISIONS.md,
27). The journal (`world/clues.py`) holds the expedition's facts; the notebook holds one
player's growing understanding.

An idea is learned at a level (heard, understood, used: `LEVELS`), and its entry shows the
texts up to the level reached, so it grows as the player learns more. Ideas live in
`world/content/ideas.yaml`; texts teach them with `teaches` in the other content files.
Conversations and reading or using a thing teach everyone in the room who hears them, up to
`understood`; `used` is for whoever did it. Looking is private and teaches only the looker.

The notebooks are kept in the `Expedition` script, by character id, so starting over clears
them with everything else.
"""

from typing import Any

from evennia.utils.ansi import strip_ansi

from typeclasses.scripts import NoteEntry
from world import recorder
from world.content import LEVELS, Content, IdeaSpec, Teaching, load_content
from world.expedition import get_expedition

NOTEBOOK: str = "|wnotebook|n"
# Set on a character once they have opened their notebook: the "Type notebook" hint stops.
READ_IT: str = "has_read_notebook"
USED: str = "used"


def learn(doer: Any, teaching: Teaching, source: str, hearers: list[Any] | None = None) -> None:
    """
    `doer` (and `hearers`, who heard or watched it) learned what a text teaches, from
    `source` ("Old Barnaby", "the sextant"). Each learner gets one line naming the new ideas,
    and one for entries that grew; nothing is said when they knew it this well already. How
    to read the notebook is said only until they have opened it.
    """
    if not teaching:
        return
    content: Content = load_content()
    ideas: list[tuple[IdeaSpec, str]] = [
        (content.ideas[idea_id], level) for idea_id, level in teaching if idea_id in content.ideas
    ]
    for learner in dict.fromkeys([doer, *(hearers or [])]):
        new: list[str] = []
        grew: list[str] = []
        for idea, level_name in ideas:
            if learner is not doer and level_name == USED:
                level_name = LEVELS[LEVELS.index(USED) - 1]  # watching isn't doing
            change: str | None = _note(learner, idea, level_name, source)
            if change == "new":
                new.append(f"|w{idea.title}|n")
            elif change == "grew":
                grew.append(f"|w{idea.title}|n")
        _note_learned(learner, new, grew)
        read_it: bool = bool(learner.attributes.get(READ_IT, False))
        if new:
            hint: str = "" if read_it else f" Type {NOTEBOOK} to read it."
            learner.msg(f"New in your notebook: {', '.join(new)}.{hint}")
        if grew:
            entries: str = "entry" if len(grew) == 1 else "entries"
            hint = "" if read_it else f" ({NOTEBOOK})"
            learner.msg(f"Your notebook {entries} on {', '.join(grew)} grew.{hint}")


def _note_learned(learner: Any, new: list[str], grew: list[str]) -> None:
    """Tell a scenario recording what the learner's notebook gained."""
    parts: list[str] = []
    if new:
        parts.append("new " + ", ".join(new))
    if grew:
        parts.append("grew " + ", ".join(grew))
    if parts:
        recorder.note(learner, strip_ansi("Notebook: " + "; ".join(parts)))


def _note(learner: Any, idea: IdeaSpec, level_name: str, source: str) -> str | None:
    """Note what the learner learned. Returns "new", "grew", or None if nothing showed."""
    level: int = LEVELS.index(level_name)
    before: int = get_expedition().note(learner.id, idea.id, level, level_name, source)
    if before < 0:
        return "new"
    if level > before and idea.entry(level_name) != idea.entry(LEVELS[before]):
        return "grew"
    return None


def _entries(owner: Any) -> dict[str, NoteEntry]:
    """The owner's notebook entries for ideas still in the content, by idea id."""
    ideas: dict[str, IdeaSpec] = load_content().ideas
    return {
        entry.idea: entry for entry in get_expedition().notebook(owner.id) if entry.idea in ideas
    }


def notebook_text(owner: Any) -> str:
    """The notebook as `notebook` shows it: the areas started, each with its ideas."""
    content: Content = load_content()
    known: dict[str, NoteEntry] = _entries(owner)
    if not known:
        return (
            "Your notebook is still empty. When you learn how something works, from people, "
            "books or instruments, it's written here."
        )
    lines: list[str] = ["|wYour notebook|n"]
    unstarted: bool = False
    for area in content.areas.values():
        ideas: list[IdeaSpec] = [i for i in content.ideas.values() if i.area == area.id]
        mine: list[IdeaSpec] = [i for i in ideas if i.id in known]
        if not mine:
            unstarted = unstarted or bool(ideas)
            continue
        lines.append(f"\n|w{area.title}|n: {len(mine)} of {len(ideas)}")
        for idea in mine:
            lines.append(f"  |w{idea.title}.|n {idea.entry(LEVELS[known[idea.id].level])}")
    if unstarted:
        lines.append("\nThere is more to discover.")
    lines.append("\n(Who taught you what: |wnotebook sources|n)")
    return "\n".join(lines)


def sources_text(owner: Any) -> str:
    """Where each idea in the notebook came from, and who else in the expedition knows it."""
    content: Content = load_content()
    known: dict[str, NoteEntry] = _entries(owner)
    if not known:
        return notebook_text(owner)
    lines: list[str] = ["|wWho taught you what|n"]
    for idea in content.ideas.values():
        entry: NoteEntry | None = known.get(idea.id)
        if entry is None:
            continue
        taught: str = "; ".join(f"{level}: {source}" for level, source in entry.sources)
        line: str = f"  |w{idea.title}|n: {taught}."
        others: list[str] = _others_who_know(owner, idea.id)
        if others:
            line += f" Also in the notebook of {', '.join(others)}."
        lines.append(line)
    return "\n".join(lines)


def _others_who_know(owner: Any, idea_id: str) -> list[str]:
    from evennia.utils.search import search_object

    names: list[str] = []
    for key, book in (get_expedition().db.notebooks or {}).items():
        if key == str(owner.id) or idea_id not in book:
            continue
        found: list[Any] = list(search_object(f"#{key}"))
        if found:
            names.append(str(found[0].key))
    return names
