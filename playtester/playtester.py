"""Playtester: a player agent that plays a Terrific Travel game the way a kid might.

Run from the repo root, with the game's server running:

    uv run python playtester/playtester.py phantom_island --persona max --reset   (new)
    uv run python playtester/playtester.py phantom_island --persona max           (carry on)
    uv run python playtester/playtester.py phantom_island --persona max --manual

See README.md for the personas, the options and the report.
"""

import argparse
import os
import random
import sys
from datetime import datetime
from pathlib import Path

import anthropic

from brain import DEFAULT_MODEL, Brain, Mind, Move
from console import console_log
from kid import SECONDS_PER_TURN, Kid, Seen, Turn
from profiles import GameProfile, Persona, load_game, load_persona
from report import STAMP, Run, report_path, write_report
from screen import to_screen
from state import Saved, last_reset, load_state, record_reset, save_state
from telnet import TelnetClient

# The player's account password, unless PLAYTESTER_PASSWORD is set. The accounts are
# ordinary players on a development server; the password only has to pass Evennia's checks.
DEFAULT_PASSWORD: str = "kid-playtester-26"
LOGIN_FAILED: tuple[str, ...] = ("incorrect", "too many")
FINISHED: str = "finished the game"
# The local models (local.py), named here so --help lists them without loading torch.
LOCAL_MODELS: tuple[str, ...] = ("qwen3-0.6b", "qwen3-1.7b", "qwen3-4b")


def make_mind(model: str, seed: int) -> Mind:
    """Claude through the API, or a local Qwen3 (imported only then: torch takes a while)."""
    if model in LOCAL_MODELS:
        print(f"Loading {model}...")
        from local import LocalBrain

        return LocalBrain(model, seed)
    return Brain(model)


def log_in(client: TelnetClient, game: GameProfile, name: str, password: str) -> str:
    """Log in (creating the account the first time) and return the first screen."""
    client.connect()
    client.read(quiet=1.0)  # the connection screen
    client.send(f"connect {name} {password}")
    answer: str = client.read(quiet=game.quiet_seconds)
    if any(word in answer.lower() for word in LOGIN_FAILED):
        client.send(f"create {name} {password}")
        created: str = client.read(quiet=1.0)
        if "intended?" in created.lower():  # Evennia asks to confirm the name and password
            client.send("y")
            created = client.read(quiet=1.0)
        if "created" not in created.lower():
            raise RuntimeError(f"Couldn't create the account {name}:\n{to_screen(created)}")
        client.send(f"connect {name} {password}")
        answer = client.read(quiet=game.quiet_seconds)
        if any(word in answer.lower() for word in LOGIN_FAILED):
            raise RuntimeError(f"Couldn't log in as {name}:\n{to_screen(answer)}")
    return answer


def reset_game(game: GameProfile) -> None:
    """Start the game over with the admin account, before the player logs in."""
    if not game.reset:
        return
    name: str | None = os.environ.get("PLAYTESTER_ADMIN_NAME")
    password: str | None = os.environ.get("PLAYTESTER_ADMIN_PASSWORD")
    if not name or not password:
        raise RuntimeError(
            "Starting the game over needs a developer account: set PLAYTESTER_ADMIN_NAME and "
            "PLAYTESTER_ADMIN_PASSWORD (see README.md)."
        )
    admin: TelnetClient = TelnetClient(game.host, game.port)
    try:
        admin.connect()
        admin.read(quiet=1.0)
        admin.send(f"connect {name} {password}")
        answer: str = admin.read(quiet=2.0)  # all of the login, so it isn't taken for the reply
        if any(word in answer.lower() for word in LOGIN_FAILED):
            raise RuntimeError(f"The admin account couldn't log in:\n{to_screen(answer)}")
        for command in game.reset:
            admin.send(command)
            reply: list[str] = to_screen(admin.read(quiet=1.0)).split("\n")
            print(f"[reset] {command}: {reply[-1]}")
        admin.send("quit")
        admin.read(quiet=0.5, first_wait=2.0)
    finally:
        admin.close()


def manual_move(seen: Seen, kid: Kid) -> Move:
    """You type instead of the model, and see exactly what it would see."""
    print(f"\n----- turn {kid.turn_number} (boredom {kid.boredom}) -----")
    print(seen.text)
    line: str = input("> ")
    return Move(
        thought="",
        command=line,
        feeling="curious",
        noticed="",
        hard_words=[],
        notes=kid.notes,
        howto=kid.howto,
        quit=line.strip() == "/quit",
    )


def show(turn: Turn, spend: float | None) -> None:
    cost: str = f"  ${spend:.2f}" if spend is not None else ""
    typed: str = (
        turn.typed if turn.typed == turn.intended else f"{turn.typed} (meant {turn.intended})"
    )
    print(f"{turn.number:>4} [{turn.feeling}] > {typed}{cost}")
    if turn.thought:
        print(f"       {turn.thought}")


def play(
    run: Run,
    client: TelnetClient,
    brain: Mind | None,
    first: str,
    turns: int,
    max_cost: float,
) -> None:
    """The game loop: read the screen, decide, type, until the run ends one way or another."""
    kid: Kid = run.kid
    game: GameProfile = run.game
    screen: str = to_screen(first)
    while True:
        seen: Seen = kid.see(screen)
        finished: bool = any(text in screen for text in game.end_texts)
        limit: bool = kid.turns_this_sitting >= turns
        spent: bool = brain is not None and max_cost > 0 and brain.spend.dollars >= max_cost
        good_moment: bool = seen.time_up and seen.progress
        late: bool = kid.must_stop()
        stop: bool = finished or kid.gives_up() or client.closed or limit or spent
        if stop or good_moment or late:
            kid.remember(Turn(number=kid.turn_number, seen=seen), kid.notes)
            minutes: str = f"after about {kid.minutes_played} minutes"
            if finished:
                run.outcome = FINISHED
            elif client.closed:
                run.outcome = "the game closed the connection"
            elif kid.gives_up():
                run.outcome = f"gave up, bored (nothing happening for {kid.boredom} turns)"
            elif good_moment:
                run.outcome = f"stopped for today at a good moment, {minutes}"
            elif late:
                run.outcome = f"had to stop for today, {minutes}"
            elif spent:
                run.outcome = f"stopped at the cost limit (${max_cost:.2f})"
            else:
                run.outcome = f"stopped at the turn limit ({turns})"
            return
        move: Move = brain.decide(kid, seen) if brain else manual_move(seen, kid)
        turn: Turn = Turn(
            number=kid.turn_number,
            seen=seen,
            intended=move.command.strip(),
            thought=move.thought,
            feeling=move.feeling if brain else "",
            noticed=move.noticed,
            hard_words=move.hard_words,
            quit=move.quit,
        )
        if move.quit:
            kid.remember(turn, move.notes, move.howto)
            run.outcome = "quit" + (f": {move.thought}" if brain else "")
            return
        turn.typed = kid.type(turn.intended) if brain else turn.intended  # you type yourself
        kid.remember(turn, move.notes, move.howto)
        if brain:
            show(turn, brain.spend.dollars)
        client.send(turn.typed)
        screen = to_screen(client.read(quiet=game.quiet_seconds))


def main() -> int:
    parser = argparse.ArgumentParser(description="A kid-like player agent for a text game.")
    parser.add_argument("game", help="a game profile in games/, e.g. phantom_island")
    parser.add_argument("--persona", default="max", help="a persona in personas/ (default: max)")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"a Claude model (default: {DEFAULT_MODEL}), or a local one: "
        + ", ".join(LOCAL_MODELS),
    )
    parser.add_argument("--turns", type=int, default=200, help="most turns to play now (200)")
    parser.add_argument(
        "--max-cost",
        type=float,
        default=5.0,
        help="stop this run once its estimated cost reaches this many dollars (5; 0: no limit)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="start the game over and a new playthrough with fresh memory",
    )
    parser.add_argument("--no-debrief", action="store_true", help="skip the talk afterwards")
    parser.add_argument(
        "--no-time-limit",
        action="store_true",
        help="ignore the persona's sitting length: play on until --turns or --max-cost",
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="type yourself, as the agent sees (no memory loaded or saved)",
    )
    parser.add_argument(
        "--seed", type=int, help="random seed for typos and sitting length (repeatable runs)"
    )
    args = parser.parse_args()

    try:
        game: GameProfile = load_game(args.game)
        persona: Persona = load_persona(args.persona)
        saved: Saved | None = None
        if not args.reset and not args.manual:
            saved = load_state(game.key, persona.key)
    except (FileNotFoundError, ValueError, KeyError) as error:
        print(error)
        return 2
    if saved:
        problem: str = ""
        if saved.sittings and saved.sittings[-1].outcome == FINISHED:
            problem = f"{persona.name} has already finished this playthrough."
        elif saved.reset_at != last_reset(game.key):
            problem = (
                f"The game has been started over since {persona.name}'s playthrough began, "
                "so it no longer matches the saved memory."
            )
        if problem:
            print(f"{problem} Add --reset to start a new playthrough.")
            return 2
    # The console goes into a text file beside the report: started by a new playthrough,
    # appended to by a run that carries one on.
    stamp: str = saved.stamp if saved and saved.stamp else datetime.now().strftime(STAMP)
    log: Path = report_path(game.key, persona.key, stamp, args.manual).with_suffix(".txt")
    with console_log(log, append=saved is not None):
        command: str = " ".join(["uv run python playtester/playtester.py", *sys.argv[1:]])
        print(f"{datetime.now():%Y-%m-%d %H:%M} > {command}")
        code: int = sitting(args, game, persona, saved, stamp)
    print(f"Console: {log}")
    return code


def sitting(
    args: argparse.Namespace, game: GameProfile, persona: Persona, saved: Saved | None, stamp: str
) -> int:
    """One run of the program: reset or carry on, log in, play, then report and save."""
    try:
        brain: Mind | None = None if args.manual else make_mind(args.model, args.seed or 0)
    except anthropic.AnthropicError as error:  # e.g. no API key at all
        print(f"Can't use the Claude API: {error}\nSee README.md, or play with --manual.")
        return 1
    except (OSError, ValueError) as error:  # a local model that isn't cached, or no such one
        print(f"Can't load the local model: {error}")
        return 1
    run: Run = Run(
        game=game,
        kid=Kid(
            persona,
            random.Random(args.seed),
            game,
            timed=not args.manual and not args.no_time_limit,
        ),
        model="(you, typing)" if brain is None else brain.model,
        started=datetime.now(),
        cost_note="estimate" if brain is None else brain.cost_note,
    )
    run.stamp = stamp
    if saved:
        run.kid.come_back(saved.turns, saved.notes, saved.howto, saved.known)
        run.earlier, run.reset_at = saved.sittings, saved.reset_at
    client: TelnetClient = TelnetClient(game.host, game.port)
    try:
        if args.reset:
            reset_game(game)
            run.reset_at = record_reset(game.key)
        password: str = os.environ.get("PLAYTESTER_PASSWORD", DEFAULT_PASSWORD)
        first: str = log_in(client, game, persona.name, password)
        again: str = f", from turn {run.kid.turn_number}" if saved else ""
        minutes: int = round(run.kid.sitting_turns * SECONDS_PER_TURN / 60)
        has: str = f" {persona.name} has about {minutes} minutes today." if run.kid.timed else ""
        print(f"{persona.name} is playing {game.title}{again}.{has} Ctrl+C stops.")
        play(run, client, brain, first, args.turns, args.max_cost)
        if brain and not args.no_debrief:
            run.debrief = brain.debrief(run.kid, run.outcome)
    except KeyboardInterrupt:
        run.outcome = run.outcome or "stopped by you (Ctrl+C)"
    except (ConnectionError, RuntimeError) as error:
        print(error)
        run.outcome = run.outcome or f"error: {error}"
        if not run.kid.turns_this_sitting:
            return 1
    except anthropic.AuthenticationError:
        print("The API key was refused. Check ANTHROPIC_API_KEY (see README.md).")
        return 1
    except anthropic.APIError as error:
        print(f"The Claude API failed: {error}")
        run.outcome = run.outcome or f"API error: {error}"
    except anthropic.AnthropicError as error:  # e.g. no API key at all
        print(f"Can't use the Claude API: {error}\nSee README.md, or play with --manual.")
        return 1
    finally:
        if not client.closed:
            try:
                client.send("quit")
            except OSError:
                pass
        client.close()
    if brain:
        run.dollars = brain.spend.dollars
        run.unreadable = brain.unreadable
    path: Path = write_report(run, manual=args.manual)
    if not args.manual:
        save_state(run)
    print(f"\n{persona.name}: {run.outcome}.")
    if brain:
        print(f"Cost ({brain.cost_note}): ${run.dollars:.2f}")
        if brain.unreadable:
            print(f"Turns whose answer couldn't be read: {brain.unreadable}")
    print(f"Report: {path}")
    if brain and run.outcome != FINISHED:
        print("To carry on from here, run the same command again, without --reset.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
