"""
The expedition's report and the epilogue (`report`, DECISIONS.md, 29).

The report asks the task's questions one at a time, anywhere and at any moment. A player
answers by picking one of a question's choices, and one player's answer counts for the whole
expedition. A wrong choice is turned down with a reason and a hint; the right one is accepted
only when the journal holds its proof. Once every question is answered, every connected
player is shown the epilogue's first page, and `report more` turns the pages.

What each player is looking at (a question, or a page of the epilogue) is kept on their
character; what has been answered is kept in the `Expedition` script.
"""

from typing import Any

from world import recorder
from world.clues import entry_number
from world.content import (
    CHOICE_LETTERS,
    ChoiceSpec,
    Content,
    PageSpec,
    ProofSpec,
    QuestionSpec,
    ReportSpec,
    load_content,
)
from world.expedition import connected_characters, get_expedition

QUESTION_SEEN: str = "report_question"  # the question a player last looked at (its id)
PAGE_SEEN: str = "report_page"  # the epilogue page a player last read (its index)
REPORT_MORE: str = "report more"
MORE_WORDS: tuple[str, ...] = ("more", "next", "on")
EPILOGUE_WORDS: tuple[str, ...] = ("epilogue", "story", "again")
NOTHING_TO_REPORT: str = "There is nothing to report on this expedition."


def report(caller: Any, args: str) -> None:
    """What `report` does with what the player typed after it."""
    spec: ReportSpec | None = load_content().report
    if spec is None:
        caller.msg(NOTHING_TO_REPORT)
        return
    words: list[str] = args.strip().lower().replace(")", " ").split()
    if not words:
        if is_complete(spec):
            show_page(caller, spec, int(caller.attributes.get(PAGE_SEEN, 0)))
        else:
            show_question(caller, current_question(caller, spec))
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
    if len(letter) == 1 and letter in CHOICE_LETTERS[: len(question.choices)]:
        answer(caller, spec, question, CHOICE_LETTERS.index(letter))
        return
    caller.msg(
        f"Pick one of the choices by its letter, like |wreport a|n, or a question by its "
        f"number, like |wreport 1|n. {_questions_left(spec)}"
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


def show_question(caller: Any, question: QuestionSpec) -> None:
    """A question of the report with its choices, or who answered it and how."""
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
    for index, choice in enumerate(question.choices):
        lines.append(f"  {CHOICE_LETTERS[index]}) {choice.text}")
    letters: str = ", ".join(
        f"|wreport {CHOICE_LETTERS[index]}|n" for index in range(len(question.choices))
    )
    others: list[str] = [
        f"|wreport {other}|n" for other in range(1, len(spec.questions) + 1) if other != number
    ]
    lines.append(
        f"Pick the answer you can prove: {letters}. Or look at another question: "
        + ", ".join(others)
        + "."
    )
    caller.msg("\n".join(lines))


def missing_proof(choice: ChoiceSpec) -> ProofSpec | None:
    """The first part of a choice's proof that the journal doesn't hold yet, or None."""
    expedition: Any = get_expedition()
    for part in choice.proof:
        if not any(expedition.has_clue(clue) for clue in part.clues):
            return part
    return None


def _proved_by(choice: ChoiceSpec) -> str:
    """The journal entries that prove a choice: `(The journal: 4, 7.)`."""
    content: Content = load_content()
    numbers: list[int] = []
    for part in choice.proof:
        for clue in part.clues:
            number: int | None = entry_number(clue) if clue in content.clues else None
            if number is not None and number not in numbers:
                numbers.append(number)
    if not numbers:
        return ""
    listed: str = ", ".join(str(number) for number in sorted(numbers))
    return f" (Proved in the journal: {listed}.)"


def answer(caller: Any, spec: ReportSpec, question: QuestionSpec, index: int) -> None:
    """A player picks a choice for a question of the report."""
    caller.attributes.add(QUESTION_SEEN, question.id)
    expedition: Any = get_expedition()
    number: int = _number(spec, question)
    if question.id in expedition.answers:
        show_question(caller, question)
        return
    choice: ChoiceSpec = question.choices[index]
    letter: str = CHOICE_LETTERS[index]
    heading: str = f"{caller.key} considers an answer to question {number}: {letter}) {choice.text}"
    if not choice.right:
        recorder.note(caller, f"Report: {question.id} {letter}, turned down")
        _tell_room(caller, f"{heading}\n{choice.reply}\n{_questions_left(spec)}")
        return
    missing: ProofSpec | None = missing_proof(choice)
    if missing is not None:
        recorder.note(caller, f"Report: {question.id} {letter}, not proved yet")
        _tell_room(caller, f"{heading}\nBefore you write that down: {missing.missing}")
        return
    expedition.answer(question.id, str(caller.key))
    recorder.note(caller, f"Report: {question.id} answered")
    done: str = f"Question {number} is answered in the report: {choice.answer}"
    here: str = f"{heading}\n{choice.reply}{_proved_by(choice)}\n{done}"
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
