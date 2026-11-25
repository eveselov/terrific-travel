"""The player agent's mind: Claude, playing as the persona.

Each turn is one request, built afresh: the persona, the kid's notes, the few turns
still remembered and the screen as the kid read it. Nothing else reaches the model,
so it knows the game only from its screens. One answer per turn, in a fixed shape
(structured output): what the kid thinks, types and feels.
"""

from dataclasses import dataclass
from typing import Literal

import anthropic
from anthropic.types.beta import BetaTextBlockParam
from pydantic import BaseModel, Field

from kid import Kid, Seen, Turn

DEFAULT_MODEL: str = "claude-opus-5-5"
# Refused requests are re-run on a substitute model chosen by the API. A kids' game
# should never trip a refusal, but a run shouldn't end on one either.
FALLBACK_BETA: str = "server-side-fallback-2026-07-01"

# US dollars per million tokens (input, output, cache read), as of 2026-11. Only for the
# cost estimate printed during a run; the Console's Usage page has the real figure.
PRICES: dict[str, tuple[float, float, float]] = {
    "claude-opus-5-5": (4.00, 20.00, 0.20),
    "claude-sonnet-5-5": (2.00, 10.00, 0.10),
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
}

Feeling = Literal["curious", "excited", "happy", "proud", "confused", "bored", "frustrated"]


class Move(BaseModel):
    """The kid's answer to one screen."""

    thought: str = Field(description="What goes through your head now, said out loud.")
    command: str = Field(description="Exactly what you type next: one line.")
    feeling: Feeling
    noticed: str = Field(description="Something on this screen that looks important, or ''.")
    hard_words: list[str] = Field(description="Words on this screen you didn't understand.")
    notes: str = Field(description="What you keep in your head about the game, short lines.")
    quit: bool = Field(description="True only if you stop playing now.")


@dataclass
class Spend:
    """Tokens used so far, and what they cost (an estimate)."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    dollars: float = 0.0

    def add(self, model: str, usage: anthropic.types.beta.BetaUsage) -> None:
        cache_read: int = usage.cache_read_input_tokens or 0
        cache_write: int = usage.cache_creation_input_tokens or 0
        fresh: int = usage.input_tokens
        self.input_tokens += fresh + cache_write
        self.output_tokens += usage.output_tokens
        self.cache_read_tokens += cache_read
        price_in, price_out, price_cache = PRICES.get(model, PRICES[DEFAULT_MODEL])
        self.dollars += (
            fresh * price_in
            + cache_write * price_in * 1.25
            + cache_read * price_cache
            + usage.output_tokens * price_out
        ) / 1_000_000


def system_prompt(kid: Kid) -> str:
    """Who the model is playing, and how its screens and answers work."""
    p = kid.persona
    return f"""\
You are {p.name}, {p.age} years old. {p.about}

{p.experience}

Right now you are playing a computer game. It is a text game: the screen shows text, and \
you play by typing commands. You know nothing about this game except what its screen has \
shown you. Play it the way you really would at {p.age}: you are not a tester, and nobody is \
watching or marking you.

How the screen is shown to you:
- Text the game showed in colour is wrapped in a tag named after the colour, like \
<white>word</white> or <yellow>some words</yellow>. That is only how it looked; nobody has \
told you what the colours mean.
- On a long screen you read only the start. A line like [... 85 more words you didn't \
read ...] marks what you skipped: you know there was more, but not what it said.
- Sometimes your fingers slip, and you see what you really typed.

Each turn, answer with:
- thought: what goes through your head right now, one or two short sentences, the way you \
would say it out loud to a friend sitting next to you.
- command: exactly what you type next, one line, typed the way you would type it.
- feeling: how you feel right now.
- noticed: if something on this screen looks important to you (a clue, something to try, \
someone to talk to), say what in a few words; otherwise ''.
- hard_words: words on this screen you didn't understand, often none.
- notes: what you keep in your head about the game so far, at most \
{p.traits.notes_lines} short lines. They replace your earlier notes: what you leave out, \
you forget.
- quit: true only if you would stop playing now; then say why in your thought.

Stay {p.name}: a {p.age}-year-old's words, patience and attention. You may use what you know \
about the real world, as much as someone your age knows, but nothing about this game that \
you could only know from outside it."""


def turn_prompt(kid: Kid, seen: Seen) -> str:
    """This turn's request: notes, the remembered turns, and the screen now."""
    parts: list[str] = [f"Turn {kid.turn_number}."]
    parts.append("Your notes:\n" + (kid.notes or "(nothing yet)"))
    recent: list[Turn] = kid.recent()
    if recent:
        lines: list[str] = ["What happened just before (oldest first):"]
        for turn in recent:
            lines.append(f"<screen>\n{turn.seen.text}\n</screen>")
            if not turn.typed and not turn.intended:  # the last screen of an earlier sitting
                lines.append("(You stopped playing here.)")
            elif turn.typed != turn.intended:
                lines.append(f"You typed: {turn.typed}   (you meant: {turn.intended})")
            else:
                lines.append(f"You typed: {turn.typed}")
        parts.append("\n".join(lines))
    elif kid.turn_number == 1:
        parts.append("You have just started the game.")
    if kid.just_back:
        parts.append("You stopped playing for a while, and now you've come back to the game.")
    parts.append(f"Now the screen shows:\n<screen>\n{seen.text}\n</screen>")
    if seen.tired:
        parts.append("You have been playing for a long time, and you're getting tired.")
    if seen.bored:
        parts.append("Nothing new has happened for a while, and you're getting bored.")
    return "\n\n".join(parts)


class Brain:
    """Asks Claude for the kid's next move."""

    def __init__(self, model: str) -> None:
        self.model: str = model
        self.client: anthropic.Anthropic = anthropic.Anthropic()
        self.spend: Spend = Spend()

    def _system(self, kid: Kid) -> list[BetaTextBlockParam]:
        # The same for the whole run, so it is cached once long enough to be.
        return [
            {"type": "text", "text": system_prompt(kid), "cache_control": {"type": "ephemeral"}}
        ]

    def decide(self, kid: Kid, seen: Seen) -> Move:
        response = self.client.beta.messages.parse(
            model=self.model,
            max_tokens=16000,
            betas=[FALLBACK_BETA],
            fallbacks="default",
            thinking={"type": "adaptive"},
            output_config={"effort": kid.persona.traits.effort},
            system=self._system(kid),
            messages=[{"role": "user", "content": turn_prompt(kid, seen)}],
            output_format=Move,
        )
        self.spend.add(self.model, response.usage)
        if response.stop_reason == "refusal":
            raise RuntimeError("The model declined this turn (stop reason: refusal).")
        if response.parsed_output is None:
            raise RuntimeError(f"No move in the answer (stop reason: {response.stop_reason}).")
        return response.parsed_output

    def debrief(self, kid: Kid, outcome: str) -> str:
        """Afterwards, the kid tells the grown-up who made the game how it went."""
        recent: str = "\n".join(
            f"You typed: {turn.typed}. You thought: {turn.thought}" for turn in kid.recent()
        )
        question: str = (
            f"You have stopped playing ({outcome}) after {len(kid.turns)} turns.\n\n"
            f"Your notes:\n{kid.notes or '(nothing)'}\n\nYour last turns:\n{recent}\n\n"
            "The grown-up who made the game asks you how it went. Answer honestly, in your own "
            "words, in a few short paragraphs: what was fun, what was boring or confusing, "
            "where you got stuck, what you think the game wanted you to do or find out, and "
            "whether you'd play again. Don't answer with JSON this time; just talk."
        )
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            betas=[FALLBACK_BETA],
            fallbacks="default",
            thinking={"type": "adaptive"},
            output_config={"effort": kid.persona.traits.effort},
            system=self._system(kid),
            messages=[{"role": "user", "content": question}],
        )
        self.spend.add(self.model, response.usage)
        return "\n".join(block.text for block in response.content if block.type == "text")
