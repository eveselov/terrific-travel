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

A council is never lost track of (playtest 2026-11-22): it is open from the moment the
ship reaches its position until it has decided, and players may leave it for anything
else. A right answer that waits for its proof is remembered (a `proposed:` flag); the
moment the proof comes in, everyone hears that the council can carry on, wherever they
are. Called again, the council says what it has agreed so far, takes up a waiting answer
whose proof has come in, and asks the next question. The Deck shows where it stands.
When the last proof the council needs comes in, everyone hears that too, in the game's
ordinary voice and with the way back to it (playtest 2026-11-25: a player who had found
everything never went back aboard).
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from typeclasses.rooms import ShipRoom
from world import notices, recorder
from world.content import (
    CHOICE_LETTERS,
    CouncilChoiceSpec,
    CouncilSpec,
    CouncilStepSpec,
    ProofSpec,
    load_content,
)
from world.expedition import connected_characters, get_expedition
from world.notices import quiet
from world.report import proved_by, signing_command
from world.ship import way_aboard

COUNCIL: str = "council"
NO_COUNCIL: str = (
    "There's nothing to hold a council about here. When the expedition has a big decision "
    "to make aboard, the Good Hope will say so."
)
WAITS: str = (
    f"The council waits for that. You'll hear when it's done; then |w{COUNCIL}|n carries on "
    "where it stopped."
)
PROPOSED: str = "proposed:"  # + a step's flag: its right answer waits for its proof
READY_ABOARD: str = f"That's what the council was waiting for: |w{COUNCIL}|n carries on."
# Ashore, with the way aboard from where the player stands (world/ship.py, `way_aboard`).
READY_ASHORE: str = (
    "That's what the council was waiting for. To carry on, {way}, then |w" + COUNCIL + "|n."
)
EVIDENCE_ABOARD: str = (
    f"The journal now holds all that the council needs. Type |w{COUNCIL}|n to put it together."
)
EVIDENCE_ASHORE: str = (
    "The journal now holds all that the council needs. To put it together, {way}, then |w"
    + COUNCIL
    + "|n."
)


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


def open_council() -> CouncilSpec | None:
    """The council at the ship's position that hasn't decided yet, wherever players are."""
    expedition: Any = get_expedition()
    if expedition.voyage is not None:
        return None
    for spec in load_content().councils.values():
        if spec.at == expedition.ship_position and current_step(spec) is not None:
            return spec
    return None


def _proposed(step: CouncilStepSpec) -> bool:
    return bool(get_expedition().met((PROPOSED + step.sets,)))


def ready_step() -> CouncilStepSpec | None:
    """The open council's step whose right answer waited for its proof, now that it holds."""
    spec: CouncilSpec | None = open_council()
    step: CouncilStepSpec | None = current_step(spec) if spec is not None else None
    if step is None or not _proposed(step) or _missing(step.right) is not None:
        return None
    return step


def evidence_complete() -> CouncilSpec | None:
    """
    The open council, once the journal holds the proof for every step it has left; None
    before, and once the report already holds what the council would conclude.
    """
    spec: CouncilSpec | None = open_council()
    step: CouncilStepSpec | None = current_step(spec) if spec is not None else None
    if spec is None or step is None:
        return None
    left: tuple[CouncilStepSpec, ...] = spec.steps[spec.steps.index(step) :]
    if any(_missing(each.right) is not None for each in left):
        return None
    answers: dict[str, str] = get_expedition().answers
    if spec.concludes and all(question in answers for question in spec.concludes):
        return None
    return spec


@contextmanager
def watching() -> Iterator[None]:
    """
    Tell everyone when what the council waits for comes in while the body runs: the proof
    of a waiting answer (quietly), or the last proof it needs (in the ordinary voice).
    """
    before: CouncilStepSpec | None = ready_step()
    complete_before: CouncilSpec | None = evidence_complete()
    yield
    if complete_before is None and evidence_complete() is not None:
        for character in connected_characters():
            aboard_now: bool = isinstance(character.location, ShipRoom)
            notices.after(
                character,
                EVIDENCE_ABOARD
                if aboard_now
                else EVIDENCE_ASHORE.format(way=way_aboard(character)),
            )
        return
    after: CouncilStepSpec | None = ready_step()
    if after is None or after == before:
        return
    for character in connected_characters():
        aboard: bool = isinstance(character.location, ShipRoom)
        notices.tell(
            character,
            READY_ABOARD if aboard else READY_ASHORE.format(way=way_aboard(character)),
        )


def status_line() -> str:
    """Where the open council stands, for the Deck, once it has begun."""
    spec: CouncilSpec | None = open_council()
    step: CouncilStepSpec | None = current_step(spec) if spec is not None else None
    if spec is None or step is None:
        return ""
    agreed: int = spec.steps.index(step)
    if agreed == 0 and not _proposed(step):
        return ""
    return quiet(
        f"The council is sitting: {agreed} of {len(spec.steps)} questions agreed. "
        f"|w{COUNCIL}|n carries on where it stopped."
    )


def _again(spec: CouncilSpec, step: CouncilStepSpec) -> str:
    """Where the council stands when it is called again: what it agreed, what is left."""
    done: tuple[CouncilStepSpec, ...] = spec.steps[: spec.steps.index(step)]
    if not done:
        return ""
    agreed: str = "; ".join(settled.agreed for settled in done)
    left: int = len(spec.steps) - len(done)
    still: str = "one question" if left == 1 else f"{left} questions"
    return f"The council sits again. Agreed so far: {agreed}. Still to settle: {still}."


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
        if ready_step() is step:  # the answer it waited for, now proved
            taken: str = CHOICE_LETTERS[step.choices.index(step.right)]
            resumed: str = (
                f"{caller.key} calls the council. The proof is in, so it takes up its answer "
                f"again: {taken}) {step.right.text}"
            )
            _settle(caller, spec, step, step.right, resumed)
            return
        again: str = _again(spec, step)
        intro: str = again or (spec.opening if step is spec.steps[0] else "")
        waiting: ProofSpec | None = _missing(step.right) if _proposed(step) else None
        lines: list[str] = [f"{caller.key} calls the council.", intro]
        lines.append(step_text(step))
        if waiting is not None:
            favoured: str = CHOICE_LETTERS[step.choices.index(step.right)]
            lines.append(f"The council already favours {favoured}) {step.right.text}")
            lines.append(waiting.missing)
            lines.append(quiet(WAITS))
        _tell_room(caller, "\n".join(line for line in lines if line))
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
        get_expedition().set_flag(PROPOSED + step.sets)
        recorder.note(caller, f"Council: {spec.id} {step.id}, not proved yet")
        _tell_room(caller, f"{heading}\n{missing.missing}\n{quiet(WAITS)}")
        return
    _settle(caller, spec, step, choice, heading)


def _settle(
    caller: Any,
    spec: CouncilSpec,
    step: CouncilStepSpec,
    choice: CouncilChoiceSpec,
    heading: str,
) -> None:
    """The council agrees on `choice`, and moves on to the next step or sums up."""
    get_expedition().set_flag(step.sets)
    recorder.note(caller, f"Council: {spec.id} {step.id} settled")
    following: CouncilStepSpec | None = current_step(spec)
    after: str = step_text(following) if following is not None else summary_text(spec)
    credit: str = proved_by(choice.proof)
    credited: str = f"\n{quiet(credit)}" if credit else ""
    _tell_room(caller, f"{heading}\n{choice.reply}{credited}\n{after}")
