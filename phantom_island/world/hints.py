"""
Hints: the next step, at three levels, for a player who asks or goes long without progress.

No dead ends (DECISIONS.md, 6b and 31). `hint` finds the first situation in hints.yaml that
matches the state of play (where the ship is, the journal, the flags, the report) and gives
its next level: a nudge, then more direct, then the exact command. The level starts over
whenever the expedition makes progress (a clue found, a report question answered).

Pushed hints: the expedition's clock counts the commands players type. Once `push_after`
commands pass without progress, the player gets the first level, and after as many more the
second (playtest 2026-11-26: a nudge alone was read past for 30 commands), never the exact
command. With it, a quiet note if `think` or `report` holds something new the player hasn't
looked at (DECISIONS.md, 33). Commands, not minutes (playtest 2026-11-25): a slow reader
and a fast one get it after the same amount of trying, and a break never counts.

Aboard, the Ship speaks the hint; anywhere else, the journal does, as the expedition's own
thinking.

A report answer that waits for proof names what's missing; until it's found, that player's
hints are about it too, from the first situation whose `missing` holds it (playtest
2026-11-26: the report asked for the coastline while `hint` spoke of the beams).
"""

from typing import Any

from typeclasses.rooms import Room, ShipRoom
from world.clues import news
from world.content import LIMBO_ID, Content, HintsSpec, SituationSpec, load_content
from world.expedition import get_expedition
from world.notices import quiet

HINT: str = "hint"
HINT_STATE: str = "hint_state"  # on a character: the situation, level and progress last hinted
WANTED_PROOF: str = "wanted_proof"  # on a character: the clues the report last asked for
NO_HINTS: str = "There are no hints in this game."
PUSHES: int = 2  # pushed hints per stretch without progress: the first level, then the second


def matches(situation: SituationSpec, content: Content) -> bool:
    """Whether a situation fits the state of play."""
    expedition: Any = get_expedition()
    if situation.ship and expedition.ship_position not in situation.ship:
        return False
    if situation.needs and not expedition.met(situation.needs):
        return False
    if any(expedition.met((item,)) for item in situation.missing):
        return False
    answers: dict[str, str] = expedition.answers
    if situation.unanswered is not None and situation.unanswered in answers:
        return False
    if situation.answered:
        report_ids: list[str] = (
            [question.id for question in content.report.questions] if content.report else []
        )
        if not report_ids or not all(question in answers for question in report_ids):
            return False
    return True


def want_proof(caller: Any, clues: tuple[str, ...]) -> None:
    """Remember the proof a report answer waits for (any one of these clues will do)."""
    caller.attributes.add(WANTED_PROOF, list(clues))


def current_situation(caller: Any = None) -> SituationSpec | None:
    """
    The situation to hint at: for a caller whose report answer waits for proof not found
    yet, the first that leads to it; otherwise the first in hints.yaml that matches the
    state of play. None if there's none.
    """
    content: Content = load_content()
    if content.hints is None:
        return None
    wanted: list[str] = (
        [str(c) for c in (caller.attributes.get(WANTED_PROOF) or [])] if caller else []
    )
    if wanted and any(get_expedition().met((clue,)) for clue in wanted):
        caller.attributes.remove(WANTED_PROOF)  # found: back to the usual order
        wanted = []
    for situation in content.hints.situations:
        if any(clue in situation.missing for clue in wanted) and matches(situation, content):
            return situation
    for situation in content.hints.situations:
        if matches(situation, content):
            return situation
    return None


def spoken(caller: Any, spec: HintsSpec, text: str) -> str:
    """A hint in the voice of where the player is: the Ship aboard, the journal elsewhere."""
    voice: str = spec.aboard if isinstance(caller.location, ShipRoom) else spec.ashore
    return voice.replace("{hint}", text)


def hint(caller: Any) -> None:
    """`hint`: the next level of the hint for the current situation."""
    spec: HintsSpec | None = load_content().hints
    situation: SituationSpec | None = current_situation(caller)
    if spec is None or situation is None:
        caller.msg(NO_HINTS)
        return
    progress: int = get_expedition().progress
    state: dict[str, Any] = dict(caller.attributes.get(HINT_STATE) or {})
    level: int = 0
    if state.get("situation") == situation.id and state.get("progress") == progress:
        level = min(int(state.get("level", -1)) + 1, len(situation.hints) - 1)
    caller.attributes.add(
        HINT_STATE, {"situation": situation.id, "level": level, "progress": progress}
    )
    more: str = f" (More: |w{HINT}|n again.)" if level < len(situation.hints) - 1 else ""
    caller.msg(spoken(caller, spec, situation.hints[level]) + more)


def _in_the_expedition(caller: Any) -> bool:
    """Whether the caller is a character who has joined (not in Limbo, the title page)."""
    location: Any = getattr(caller, "location", None)
    if location is None:
        return False
    return not (isinstance(location, Room) and location.place_id == LIMBO_ID)


def after_command(caller: Any) -> None:
    """
    Count a command on the expedition's clock, and push a hint once `push_after` commands
    have passed without progress: the first level, then, as many commands later, the second
    (or the one after the level the player has asked for).
    """
    spec: HintsSpec | None = load_content().hints
    if spec is None or not _in_the_expedition(caller):
        return
    expedition: Any = get_expedition()
    progress: int = expedition.progress
    clock: dict[str, Any] = expedition.hint_clock
    if clock.get("progress") != progress:
        expedition.set_hint_clock({"progress": progress, "commands": 0, "pushed": 0})
        return
    typed: int = int(clock.get("commands", 0)) + 1
    clock["commands"] = typed
    pushed: int = int(clock.get("pushed") or 0)  # `True` in clocks kept before 2026-11-26
    due: bool = pushed < PUSHES and typed >= spec.push_after * (pushed + 1)
    if due and expedition.voyage is None:
        situation: SituationSpec | None = current_situation(caller)
        if situation is not None:
            clock["pushed"] = pushed + 1
            state: dict[str, Any] = dict(caller.attributes.get(HINT_STATE) or {})
            level: int = pushed
            if state.get("situation") == situation.id and state.get("progress") == progress:
                level = max(level, int(state.get("level", -1)) + 1)
            level = min(level, len(situation.hints) - 2)  # the exact command only when asked
            caller.attributes.add(
                HINT_STATE, {"situation": situation.id, "level": level, "progress": progress}
            )
            text: str = spoken(caller, spec, situation.hints[level])
            text += f" (Stuck? |w{HINT}|n tells you more.)"
            fresh: list[str] = news(caller)
            if fresh:  # found earlier, never announced (DECISIONS.md, 33)
                commands: str = " and ".join(f"|w{command}|n" for command in fresh)
                text += "\n" + quiet(f"Something new you haven't looked at yet: {commands}.")
            caller.msg(text)
    expedition.set_hint_clock(clock)
