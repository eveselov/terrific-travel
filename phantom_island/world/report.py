"""
The expedition's report and the epilogue (`report`, DECISIONS.md, 29 and 32).

The report is the expedition's case board: `report` alone shows the task's questions, each
answered or with the possibilities (theories) the expedition has come across so far; a theory
opens with the clues that raise it. It works anywhere and at any moment. A player answers by
picking one of a question's open theories, and one player's answer counts for the whole
expedition. A wrong choice is turned down with a reason and a hint; the right one is accepted
only when the journal holds its proof. Once every question is answered, every connected
player is shown the epilogue's first page, and `report more` turns the pages.

What each player is looking at (a question, or a page of the epilogue) is kept on their
character; what has been answered is kept in the `Expedition` script.

The report records and signs; councils guide (DECISIONS.md, 37). Once a council has decided,
the report shows its conclusion under the questions it `concludes`, with the command that
signs it once the journal proves it. The council never answers for the captain.
"""

from typing import Any

from world import recorder
from world.clues import NEW, briefed, entry_number, open_theories, theory_key, unseen
from world.content import (
    CHOICE_LETTERS,
    ChoiceSpec,
    Content,
    CouncilSpec,
    PageSpec,
    ProofSpec,
    QuestionSpec,
    ReportSpec,
    load_content,
)
from world.expedition import connected_characters, get_expedition
from world.hints import want_proof

QUESTION_SEEN: str = "report_question"  # the question a player last looked at (its id)
PAGE_SEEN: str = "report_page"  # the epilogue page a player last read (its index)
REPORT_MORE: str = "report more"
VERDICT_COLOUR: str = "|c"  # the report's verdict on an answer (DECISIONS.md, 20 and 29)
NOT_PROVED: str = "The Society will want proof of that, and the journal doesn't hold it yet."
DOES_NOT_FIT: str = "This answer doesn't fit what the expedition knows."
PROVED: str = "Proved: this answer goes into the report."
MORE_WORDS: tuple[str, ...] = ("more", "next", "on")
EPILOGUE_WORDS: tuple[str, ...] = ("epilogue", "story", "again")
NOTHING_TO_REPORT: str = "There is nothing to report on this expedition."
MORE_TO_COME: str = "(More possibilities may come up as the expedition finds out more.)"


def report(caller: Any, args: str) -> None:
    """What `report` does with what the player typed after it."""
    spec: ReportSpec | None = load_content().report
    if spec is None:
        caller.msg(NOTHING_TO_REPORT)
        return
    if spec.before is not None and not briefed():
        caller.msg(spec.before)
        return
    words: list[str] = args.strip().lower().replace(")", " ").split()
    if not words:
        if is_complete(spec):
            show_page(caller, spec, int(caller.attributes.get(PAGE_SEEN, 0)))
        else:
            show_board(caller, spec)
        return
    if words[0] in MORE_WORDS:
        if is_complete(spec):
            show_page(caller, spec, int(caller.attributes.get(PAGE_SEEN, -1)) + 1)
        else:
            caller.msg(
                "The epilogue comes once every question of the report is answered. "
                + _questions_left(spec)
            )
        return
    if words[0] in EPILOGUE_WORDS and is_complete(spec):
        show_page(caller, spec, 0)
        return
    question: QuestionSpec | None = find_question(spec, words[0])
    if question is not None:
        if len(words) == 1:
            show_question(caller, question)
            return
        words = words[1:]
    else:
        question = current_question(caller, spec)
    letter: str = words[0]
    if len(letter) == 1 and letter in CHOICE_LETTERS[: len(open_theories(question))]:
        answer(caller, spec, question, CHOICE_LETTERS.index(letter))
        return
    caller.msg(
        f"Pick one of the possibilities by its letter, like |wreport 1 a|n, or a question by "
        f"its number, like |wreport 1|n. {_questions_left(spec)}"
    )


def is_complete(spec: ReportSpec) -> bool:
    """Whether every question of the report has been answered."""
    answered: dict[str, str] = get_expedition().answers
    return all(question.id in answered for question in spec.questions)


def find_question(spec: ReportSpec, word: str) -> QuestionSpec | None:
    """The question a player means, by its number (from 1) or its id; None otherwise."""
    if word.isdigit():
        number: int = int(word)
        if 1 <= number <= len(spec.questions):
            return spec.questions[number - 1]
        return None
    for question in spec.questions:
        if question.id == word:
            return question
    return None


def current_question(caller: Any, spec: ReportSpec) -> QuestionSpec:
    """
    The question a player is working on: the one they last looked at, unless it has been
    answered since; then the first one still open (or the first, once all are answered).
    """
    answered: dict[str, str] = get_expedition().answers
    seen: QuestionSpec | None = find_question(spec, str(caller.attributes.get(QUESTION_SEEN, "")))
    if seen is not None and seen.id not in answered:
        return seen
    for question in spec.questions:
        if question.id not in answered:
            return question
    return spec.questions[0]


def _number(spec: ReportSpec, question: QuestionSpec) -> int:
    return spec.questions.index(question) + 1


def _questions_left(spec: ReportSpec) -> str:
    """Which questions are still open, as commands to try."""
    answered: dict[str, str] = get_expedition().answers
    left: list[str] = [
        f"|wreport {number}|n"
        for number, question in enumerate(spec.questions, start=1)
        if question.id not in answered
    ]
    if not left:
        return "Every question is answered."
    return "Questions still open: " + ", ".join(left) + "."


def _theory_lines(caller: Any, question: QuestionSpec, indent: str) -> list[str]:
    """
    The theories open for a question, lettered, those the caller hasn't seen here marked
    new (DECISIONS.md, 33), and a note if more may come.
    """
    theories: list[ChoiceSpec] = open_theories(question)
    keys: list[str] = [theory_key(question, choice) for choice in theories]
    new: set[str] = unseen(caller, keys)
    lines: list[str] = [
        f"{indent}{CHOICE_LETTERS[index]}) {choice.text}" + (f" {NEW}" if key in new else "")
        for index, (choice, key) in enumerate(zip(theories, keys, strict=True))
    ]
    get_expedition().mark_seen(caller.id, keys)
    if len(theories) < len(question.choices):
        lines.append(f"{indent}{MORE_TO_COME}")
    return lines


def show_board(caller: Any, spec: ReportSpec) -> None:
    """
    The case board (`report` alone): every question of the task, answered or not, with the
    possibilities the expedition has come across so far (DECISIONS.md, 32).
    """
    answers: dict[str, str] = get_expedition().answers
    lines: list[str] = ["|wThe report for the Society|n: the task's questions, and what might be"]
    for number, question in enumerate(spec.questions, start=1):
        lines.append(f"{number}. {question.text}")
        if question.id in answers:
            lines.append(f"   Answered by {answers[question.id]}: {question.right.answer}")
        else:
            lines.extend(_theory_lines(caller, question, "   "))
            lines.extend(conclusion_lines(question, "   "))
    lines.append(
        "Answer a question with the letter of the possibility you can prove, like "
        "|wreport 1 a|n. Only what the journal proves is accepted."
    )
    caller.msg("\n".join(lines))


def show_question(caller: Any, question: QuestionSpec) -> None:
    """A question of the report with its open theories, or who answered it and how."""
    spec: ReportSpec | None = load_content().report
    assert spec is not None
    caller.attributes.add(QUESTION_SEEN, question.id)
    number: int = _number(spec, question)
    lines: list[str] = [
        f"|wThe report, question {number} of {len(spec.questions)}:|n {question.text}"
    ]
    answered_by: str | None = get_expedition().answers.get(question.id)
    if answered_by is not None:
        lines.append(f"Answered by {answered_by}: {question.right.answer}")
        lines.append(_questions_left(spec))
        caller.msg("\n".join(lines))
        return
    lines.extend(_theory_lines(caller, question, "  "))
    lines.extend(conclusion_lines(question, "  "))
    letters: str = ", ".join(
        f"|wreport {number} {CHOICE_LETTERS[index]}|n"
        for index in range(len(open_theories(question)))
    )
    lines.append(f"Pick the one you can prove: {letters}. All the questions: |wreport|n.")
    caller.msg("\n".join(lines))


def council_decided(council: CouncilSpec) -> bool:
    """Whether every step of a council is settled (its flags are set)."""
    return get_expedition().met(tuple(step.sets for step in council.steps))


def concluded(question: QuestionSpec) -> str | None:
    """What a council that has decided concluded about a question, or None."""
    for council in load_content().councils.values():
        if question.id in council.concludes and council_decided(council):
            return council.concludes[question.id]
    return None


def signing_command(question: QuestionSpec) -> str | None:
    """
    `report 2 d`, the command that answers a question with its right theory, once that theory
    is open and the journal proves it; None until then.
    """
    spec: ReportSpec | None = load_content().report
    assert spec is not None
    theories: list[ChoiceSpec] = open_theories(question)
    right: ChoiceSpec = question.right
    if right not in theories or missing_proof(right) is not None:
        return None
    return f"report {_number(spec, question)} {CHOICE_LETTERS[theories.index(right)]}"


def conclusion_lines(question: QuestionSpec, indent: str) -> list[str]:
    """The council's conclusion on an unanswered question, and how to sign it, if any."""
    conclusion: str | None = concluded(question)
    if conclusion is None or question.id in get_expedition().answers:
        return []
    command: str | None = signing_command(question)
    how: str = (
        f" To write it in the report: |w{command}|n."
        if command is not None
        else " The journal can't prove it yet."
    )
    return [f"{indent}The council concluded: {conclusion}{how}"]


def missing_proof(choice: ChoiceSpec) -> ProofSpec | None:
    """The first part of a choice's proof that the journal doesn't hold yet, or None."""
    expedition: Any = get_expedition()
    for part in choice.proof:
        if not any(expedition.has_clue(clue) for clue in part.clues):
            return part
    return None


def proved_by(proof: tuple[ProofSpec, ...]) -> str:
    """
    The clues that proved something, by name and journal number, so every find is seen to
    pay off (DECISIONS.md, 39): `Proved by: Nothing at the charted position (4), The
    coastline on the chart (10).` Empty if no clue of the journal proves it (only flags).
    """
    content: Content = load_content()
    found: list[tuple[int, str]] = []
    for part in proof:
        for clue in part.clues:
            number: int | None = entry_number(clue) if clue in content.clues else None
            if number is not None and (number, clue) not in found:
                found.append((number, clue))
    if not found:
        return ""
    listed: str = ", ".join(
        f"{content.clues[clue].title} ({number})" for number, clue in sorted(found)
    )
    return f"Proved by: {listed}."


def answer(caller: Any, spec: ReportSpec, question: QuestionSpec, index: int) -> None:
    """A player picks a choice for a question of the report."""
    caller.attributes.add(QUESTION_SEEN, question.id)
    expedition: Any = get_expedition()
    number: int = _number(spec, question)
    if question.id in expedition.answers:
        show_question(caller, question)
        return
    choice: ChoiceSpec = open_theories(question)[index]
    letter: str = CHOICE_LETTERS[index]
    heading: str = f"{caller.key} considers an answer to question {number}: {letter}) {choice.text}"
    if not choice.right:
        recorder.note(caller, f"Report: {question.id} {letter}, turned down")
        _tell_room(
            caller,
            f"{heading}\n{verdict(DOES_NOT_FIT)}\n{choice.reply} Pick another answer, or find "
            f"out more first. {_questions_left(spec)}",
        )
        return
    missing: ProofSpec | None = missing_proof(choice)
    if missing is not None:
        recorder.note(caller, f"Report: {question.id} {letter}, not proved yet")
        want_proof(caller, missing.clues)  # the next hint agrees (2026-11-26)
        _tell_room(
            caller,
            f"{heading}\n{verdict(NOT_PROVED)}\n{missing.missing} Once the proof is in the "
            f"|wjournal|n, report this answer again: |wreport {number} {letter}|n.",
        )
        return
    expedition.answer(question.id, str(caller.key))
    recorder.note(caller, f"Report: {question.id} answered")
    done: str = f"Question {number} is answered in the report: {choice.answer}"
    credit: str = proved_by(choice.proof)
    credited: str = f" ({credit})" if credit else ""
    here: str = f"{heading}\n{verdict(PROVED)}\n{choice.reply}{credited}\n{done}"
    elsewhere: str = f"{caller.key} answered a question of the report. {done}"
    told: list[Any] = _tell_room(caller, here)
    for character in connected_characters():
        if character not in told:
            character.msg(elsewhere)
    if is_complete(spec):
        for character in dict.fromkeys([*told, *connected_characters()]):
            character.msg("\nEvery question is answered: the report is complete.")
            show_page(character, spec, 0)
    else:
        caller.msg(_questions_left(spec))


def verdict(text: str) -> str:
    """
    The report's verdict on an answer, on its own line and in its own colour, so that it
    stands out from the longer texts around it. White words inside stay white.
    """
    return VERDICT_COLOUR + text.replace("|n", f"|n{VERDICT_COLOUR}") + "|n"


def _tell_room(caller: Any, text: str) -> list[Any]:
    """Tell the caller and everyone in their room; returns who was told."""
    location: Any = caller.location
    others: list[Any] = (
        list(location.contents_get(content_type="character")) if location is not None else []
    )
    told: list[Any] = list(dict.fromkeys([caller, *others]))
    for character in told:
        character.msg(text, from_obj=caller)
    return told


def show_page(caller: Any, spec: ReportSpec, index: int) -> None:
    """One page of the epilogue, with the way on to the next."""
    pages: tuple[PageSpec, ...] = spec.epilogue
    if index >= len(pages):
        caller.attributes.add(PAGE_SEEN, -1)
        caller.msg(
            "That is the end of the story. |wreport|n tells it again from the start, and "
            "|wjournal|n shows everything the expedition found."
        )
        return
    index = max(index, 0)
    caller.attributes.add(PAGE_SEEN, index)
    page: PageSpec = pages[index]
    more: str = f"(Next page: |w{REPORT_MORE}|n)" if index + 1 < len(pages) else "(The end.)"
    caller.msg(f"|wEpilogue, {index + 1} of {len(pages)}: {page.title}|n\n{page.text}\n{more}")
