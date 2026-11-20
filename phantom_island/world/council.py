"""
Councils: where exploring must converge on one decision (`council`, DECISIONS.md, 35).

Exploring has no single result; at a convergence point (the empty sea at the chart's
position) many findings must become one decision. A council gives that a process: the
captain calls it aboard, and the Ship asks the decision's parts one at a time, each a
question with lettered choices. As in the report, only the journal counts: the right
choice is accepted once the journal holds its proof; until then the Ship says where to
look, and the council waits there. A wrong choice leads back to the evidence. The last step
sums up, and the captain still gives the order: the council builds the decision, the
captain makes it. It is offered, never forced.

A council can conclude questions of the report (DECISIONS.md, 37): its summary is followed
by the command that signs each one (`report 2 d`), or by where its conclusion waits until
the journal can prove it. The council guides; the report records and signs.

Where a council stands is derived from the flags its steps set when settled, so it carries
on where it stopped, is shared by everyone, and starting over clears it with the flags.
Everyone in the caller's room is at the council and hears it.
"""

from typing import Any

from typeclasses.rooms import ShipRoom
from world import recorder
from world.content import (
    CHOICE_LETTERS,
    CouncilChoiceSpec,
    CouncilSpec,
    CouncilStepSpec,
    ProofSpec,
    load_content,
)
from world.expedition import get_expedition
from world.notices import quiet
from world.report import signing_command

COUNCIL: str = "council"
NO_COUNCIL: str = (
    "There's nothing to hold a council about here. When the expedition has a big decision "
    "to make aboard, the Ship will say so."
)
WAITS: str = f"The council waits: |w{COUNCIL}|n carries on where it stopped."


def council_here(caller: Any) -> CouncilSpec | None:
    """The council the caller can hold where they are: aboard, at its position."""
    if not isinstance(caller.location, ShipRoom):
        return None
    expedition: Any = get_expedition()
    if expedition.voyage is not None:
        return None
    for spec in load_content().councils.values():
        if spec.at == expedition.ship_position:
            return spec
    return None


def current_step(spec: CouncilSpec) -> CouncilStepSpec | None:
    """The first step not settled yet, or None once the council has decided."""
    expedition: Any = get_expedition()
    for step in spec.steps:
        if not expedition.met((step.sets,)):
            return step
    return None


def _letters(step: CouncilStepSpec) -> str:
    letters: list[str] = [
        f"|w{COUNCIL} {letter}|n" for letter in CHOICE_LETTERS[: len(step.choices)]
    ]
    return ", ".join(letters[:-1]) + f" or {letters[-1]}"


def step_text(step: CouncilStepSpec) -> str:
    """A step as the council hears it: the question, the lettered choices, how to answer."""
    lines: list[str] = [step.question]
    lines.extend(
        f"  {CHOICE_LETTERS[index]}) {choice.text}" for index, choice in enumerate(step.choices)
    )
    lines.append(quiet(f"Answer: {_letters(step)}."))
    return "\n".join(lines)


def _missing(choice: CouncilChoiceSpec) -> ProofSpec | None:
    """The first part of a choice's proof the journal (or the flags) doesn't hold yet."""
    expedition: Any = get_expedition()
    for part in choice.proof:
        if not any(expedition.met((need,)) for need in part.clues):
            return part
    return None


def summary_text(spec: CouncilSpec) -> str:
    """
    The council's summary, then, for each report question it concludes, how to write it in
    the report, or that it waits there for proof, or that it's already answered.
    """
    report: Any = load_content().report
    lines: list[str] = [spec.summary]
    if report is None:
        return spec.summary
    answers: dict[str, str] = get_expedition().answers
    for number, question in enumerate(report.questions, start=1):
        if question.id not in spec.concludes:
            continue
        if question.id in answers:
            lines.append(quiet(f"Question {number} of the report is already answered."))
            continue
        command: str | None = signing_command(question)
        lines.append(
            f"Write it in the report: |w{command}|n."
            if command is not None
            else f"The council's conclusion stands in the |wreport|n, beside question "
            f"{number}, until the journal can prove it."
        )
    return "\n".join(lines)


def _tell_room(caller: Any, text: str) -> None:
    """Everyone in the caller's room is at the council."""
    location: Any = caller.location
    others: list[Any] = list(location.contents_get(content_type="character"))
    for character in dict.fromkeys([caller, *others]):
        character.msg(text, from_obj=caller)


def council(caller: Any, args: str) -> None:
    """What `council` does with what the player typed after it."""
    spec: CouncilSpec | None = council_here(caller)
    if spec is None:
        caller.msg(NO_COUNCIL)
        return
    step: CouncilStepSpec | None = current_step(spec)
    words: list[str] = args.strip().lower().replace(")", " ").split()
    if step is None:
        caller.msg(summary_text(spec))
        return
    if not words:
        opening: str = f"{spec.opening}\n" if step is spec.steps[0] else ""
        _tell_room(caller, f"{caller.key} calls a council.\n{opening}{step_text(step)}")
        return
    letter: str = words[0]
    if len(letter) != 1 or letter not in CHOICE_LETTERS[: len(step.choices)]:
        caller.msg(f"{step_text(step)}")
        return
    choice: CouncilChoiceSpec = step.choices[CHOICE_LETTERS.index(letter)]
    heading: str = f"{caller.key} answers: {letter}) {choice.text}"
    if not choice.right:
        recorder.note(caller, f"Council: {spec.id} {step.id} {letter}, turned down")
        _tell_room(
            caller, f"{heading}\n{choice.reply}\n{quiet('Answer again: ' + _letters(step) + '.')}"
        )
        return
    missing: ProofSpec | None = _missing(choice)
    if missing is not None:
        recorder.note(caller, f"Council: {spec.id} {step.id}, not proved yet")
        _tell_room(caller, f"{heading}\n{missing.missing}\n{quiet(WAITS)}")
        return
    get_expedition().set_flag(step.sets)
    recorder.note(caller, f"Council: {spec.id} {step.id} settled")
    following: CouncilStepSpec | None = current_step(spec)
    after: str = step_text(following) if following is not None else summary_text(spec)
    _tell_room(caller, f"{heading}\n{choice.reply}\n{after}")
