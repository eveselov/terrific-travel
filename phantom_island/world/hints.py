"""
Hints: the next step, at three levels, for a player who asks or goes long without progress.

No dead ends (DECISIONS.md, 6b and 31). `hint` finds the first situation in hints.yaml that
matches the state of play (where the ship is, the journal, the flags, the report) and gives
its next level: a nudge, then more direct, then the exact command. The level starts over
whenever the expedition makes progress (a clue found, a report question answered).

Pushed hints: after every command a player types, the expedition's clock adds the time
since the last command (at most `GAP_CAP` seconds, so a break or a night away doesn't count
as play). Once `push_after` minutes of play pass without progress, the player gets the first
level, once per stretch without progress, with a quiet note if `think` or `report` holds
something new the player hasn't looked at (DECISIONS.md, 33).

Aboard, the Ship speaks the hint; anywhere else, the journal does, as the expedition's own
thinking.
"""

import time
from typing import Any

from typeclasses.rooms import Room, ShipRoom
from world.clues import news
from world.content import LIMBO_ID, Content, HintsSpec, SituationSpec, load_content
from world.expedition import get_expedition
from world.notices import quiet

HINT: str = "hint"
HINT_STATE: str = "hint_state"  # on a character: the situation, level and progress last hinted
GAP_CAP: float = 60.0  # seconds: the most one pause between commands counts as play
NO_HINTS: str = "There are no hints in this game."


def now() -> float:
    """The time in seconds (a function, so tests can move the clock)."""
    return time.time()


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


def current_situation() -> SituationSpec | None:
    """The first situation in hints.yaml that matches the state of play, or None."""
    content: Content = load_content()
    if content.hints is None:
        return None
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
    situation: SituationSpec | None = current_situation()
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
    Count a command's play on the expedition's clock, and push a first-level hint once
    `push_after` minutes of play have passed without progress.
    """
    spec: HintsSpec | None = load_content().hints
    if spec is None or not _in_the_expedition(caller):
        return
    expedition: Any = get_expedition()
    progress: int = expedition.progress
    time_now: float = now()
    clock: dict[str, Any] = expedition.hint_clock
    if clock.get("progress") != progress:
        expedition.set_hint_clock(
            {"progress": progress, "played": 0.0, "last": time_now, "pushed": False}
        )
        return
    played: float = float(clock.get("played", 0.0))
    played += max(0.0, min(time_now - float(clock.get("last", time_now)), GAP_CAP))
    clock.update({"played": played, "last": time_now})
    due: bool = not clock.get("pushed") and played >= spec.push_after * 60
    if due and expedition.voyage is None:
        situation: SituationSpec | None = current_situation()
        if situation is not None:
            clock["pushed"] = True
            caller.attributes.add(
                HINT_STATE, {"situation": situation.id, "level": 0, "progress": progress}
            )
            text: str = spoken(caller, spec, situation.hints[0])
            text += f" (Stuck? |w{HINT}|n tells you more.)"
            fresh: list[str] = news(caller)
            if fresh:  # found earlier, never announced (DECISIONS.md, 33)
                commands: str = " and ".join(f"|w{command}|n" for command in fresh)
                text += "\n" + quiet(f"Something new you haven't looked at yet: {commands}.")
            caller.msg(text)
    expedition.set_hint_clock(clock)
