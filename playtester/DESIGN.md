# Playtester: design

How the playtester is built and why. Read this before the code; [README.md](README.md) is
the user's guide (setup, options, reports).

## Purpose

A developer who knows a game's secrets can't play it with fresh eyes. The playtester is a
player agent that plays a Terrific Travel game the way a kid might, knowing nothing of the
game but its screens, and reports where it got confused, bored or stuck, and what it took
for a clue. It finds dead ends, unclear hints, texts too long to read and false leads
before real kids play. It does not replace them.

## Principles

1. **It knows only the screens.** The agent connects over telnet like any player. It never
   sees the game's code, content files or design documents, and no part of the playtester
   runs inside the game. Everything it learns, it learns by playing.
2. **The program enforces the kid; the model only plays it.** A model told "you skim" still
   reads every word. So attention, memory, boredom, tiredness, typos and sitting length are
   applied by the program to what the model receives and what it sends. The persona's
   description sets voice and attitude; the traits are mechanics.
3. **One fresh request per turn.** No chat history is resent. Each turn's request is rebuilt
   from the kid's state: the persona, the notes, the few turns still remembered and the
   current screen. Forgetting is exact, and every request is about the same size, so cost
   per turn doesn't grow over a long run.
4. **Games and kids are data.** A game profile (`games/*.toml`) says how to reach, reset and
   read a game; a persona (`personas/*.toml`) says who plays. The code knows no game.
5. **The game decides, the program observes.** The playtester never changes the game's
   state except through a player's commands, and through the developer's own reset command
   (`startover`), typed by a separate admin account before the player logs in.

## The parts

```
 games/*.toml   personas/*.toml
      │               │
      ▼               ▼
  profiles.py ──► playtester.py  (command line, login, reset, the game loop)
                   │    │    │
       ┌───────────┘    │    └─────────────┐
       ▼                ▼                  ▼
   telnet.py         kid.py           brain.py / local.py
   (bytes ⇄ text)    (the kid's       (the mind: Claude, or a local Qwen3)
       │              limits and
       ▼              memory)
   screen.py                               report.py   state.py
   (ANSI → <colour> tags)                  (Markdown)  (memory between runs)
```

| Module | Job |
|---|---|
| [telnet.py](telnet.py) | A minimal telnet client: refuses every option the server offers, so the server sends plain text with ANSI colours; reads until the game has been quiet for a while. |
| [screen.py](screen.py) | Turns ANSI colour codes (basic, 256-colour, true colour) into tags named after the colour: `<white>compass</white>`. Tidies line ends and blank lines. |
| [profiles.py](profiles.py) | Reads personas and game profiles into frozen dataclasses (`Persona`, `Traits`, `GameProfile`). |
| [kid.py](kid.py) | The kid: what it reads of a screen, what it remembers, how bored and tired it is, how long its sitting lasts, its typos. No model calls. |
| [brain.py](brain.py) | The prompts, and the mind on Claude: one structured answer (`Move`) per turn, cost counting (`Spend`), the `Mind` interface. |
| [local.py](local.py) | The same `Mind` on a local Qwen3, reading a JSON answer leniently. |
| [playtester.py](playtester.py) | The command line; reset and login; the loop; what ends a run. |
| [report.py](report.py) | The run and its sittings (`Run`, `Sitting`); the Markdown report. |
| [state.py](state.py) | Saving and loading a playthrough between runs, and noting resets. |
| [tests.py](tests.py) | Unit tests that need no game and no API. |

## One turn

```
 game ──telnet──► raw text ──screen.py──► screen with colour tags
                                              │
                              kid.see(): cut to attention, notice progress,
                              update boredom, tiredness, time
                                              │  Seen
                              turn_prompt(): notes, howto, remembered turns
                              (with kept thoughts), the screen, any state lines
                                              │
                              mind.decide() ──► Move
                              {thought, command, feeling, noticed,
                               hard_words, notes, howto, quit}
                                              │
                              kid.type(): maybe a typo ──► game
                              kid.remember(): the turn, the notes cut to size
```

The loop in `play()` checks, before each turn, whether the run ends: the game's end text,
the kid giving up (bored), the sitting's time being up at a good moment or a few turns
later, the connection closing, `--turns`, or `--max-cost`. A `quit` in the move ends it too.
After the loop, the kid is asked how it went (the debrief), the report is written and the
state saved.

The game is read until it has been silent for `quiet_seconds` (4 s for Phantom Island,
whose voyages print a line every 3 s). That makes a turn take at least that long, and it
is why a voyage arrives as one screen.

## The prompt

**The system prompt** ([brain.py](brain.py), `system_prompt`) is fixed for the run: who the
kid is (persona name, age, `about`, `experience`), that it is playing a text game it knows
nothing about, how the screen is shown (colour tags, skipped words, typos), the fields of
the answer, and "stay in character; use real-world knowledge as someone your age has, but
nothing about this game from outside it". It does **not** explain what the colours mean or
how text games work.

**The turn prompt** (`turn_prompt`) holds, in order: the turn number; the notes about this
game; the howto notes; the remembered turns, oldest first (each screen, the thought for the
latest few, what was typed and, after a typo, what was meant); "you have just started" or
"you've come back after a break"; the current screen; and state lines when they apply
(tired, bored, time to stop soon).

**The answer** is a `Move`: the thought (said aloud, in the kid's voice), the command, a
feeling from a fixed list, what looked important, words not understood, the rewritten
notes and howto, and whether to quit. The fields serve the report as much as the play:
`noticed` is how false leads are found, `feeling` how confusion and boredom are mapped.

## The kid's memory

| Store | Trait | What it holds | How it is kept |
|---|---|---|---|
| Remembered turns | `memory_turns` | the last few screens (as read) and commands | the program keeps the last N |
| Kept thoughts | `thoughts_kept` | the reasoning of the latest of those turns | the program adds them back |
| Notes about the game | `notes_lines` | people, places, things, the mystery | the model rewrites them each turn; the program cuts them to N lines |
| Howto | `howto_lines` | commands that work, how to talk, getting unstuck | the same, kept apart so game facts can't push it out |

Nothing else carries over between turns: the model's thinking is not resent. Between runs
of the same playthrough all four stores are saved ([state.py](state.py)). A new playthrough
(`--reset`) starts with all of them empty, so nothing is learned across playthroughs yet.
The game's own memory aids (the journal, the notebook) are outside the playtester: the kid
uses them only if it thinks of it, which is itself something to test.

## The kid's limits

- **Attention** (`attention_words`): only that many words of each screen reach the model;
  the rest is replaced by `[... N more words you didn't read ...]`. Tired (`tired_after`
  turns into a sitting), attention halves. This is a deliberately crude model: a fixed
  cut always hides the ends of long texts, where real kids would often still catch a line.
  It exaggerates problems with long screens, so findings that depend on it are weighed
  accordingly. A better reading model is open work (below).
- **Progress** is defined by the game profile: patterns of the game's own messages (a new
  clue, a new notebook entry, a council's conclusion...) and a room title not seen before.
  The whole screen counts, read or not.
- **Boredom** (`patience`): progress ends it; a screen with a good amount of new text (12
  words or more) eases it by a turn; anything else adds a turn. Lines differing only in a
  short quoted word ("Command 'norht' is not available") are not new. At `patience` the
  kid is told it's bored; at twice that it gives up and the run ends.
- **Sitting length** (`sitting_minutes`): each run picks a length between the persona's
  bounds, at about 30 seconds a turn. When it's up, the kid is told it must stop soon, and
  the run ends at the next progress or 5 turns later. `--no-time-limit` turns this off.
- **Typos** (`typo_rate`): a swapped, dropped or doubled letter in one word of three
  letters or more. The kid sees what it typed and what it meant.
- **Smartness** (`effort`): how hard the model thinks (Claude's effort; a local model
  thinks first above `low`).

Randomness (typos, sitting length, a local model's sampling) comes from `--seed`. The Claude
model itself can't be seeded, so runs differ; treat each run as one afternoon, and look for
what repeats across runs.

## Playthroughs and sittings

A **sitting** is one run of the program. A **playthrough** is one or more sittings of the
same persona, from a reset. Each run saves the kid's side (turns, notes, howto, the lines
already seen, the sittings) in `runs/<game>-<persona>.state.json`; the game keeps its own
side on the server.

- Without `--reset`, a run carries on the saved playthrough: turns are numbered on, the kid
  is told it has come back, rested and no longer bored.
- `--reset` types the game profile's reset commands as an admin account, notes the time in
  `runs/<game>.reset.txt`, and starts a new playthrough.
- A run refuses to carry on when nothing is saved, the playthrough has finished, or the
  game was reset after it began (by another persona's run, say).
- Leaving the game has effects in the game: Phantom Island puts back what the player
  carried. So several sittings are not one long run; comparisons use one long run.
- `--manual` lets the developer type, seeing exactly what the agent would see; it neither
  loads nor saves memory.

## The minds

`Mind` ([brain.py](brain.py)) is the interface: `decide(kid, seen) -> Move`,
`debrief(kid, outcome) -> str`, plus `model`, `spend`, `cost_note`, `unreadable`.

- **Claude** (`Brain`): the Messages API with structured output (`messages.parse` with
  `Move`), so every answer has the right shape. Adaptive thinking, the persona's effort,
  and server-side fallback on a refusal. The system prompt is marked for caching, though
  it is probably below the minimum length to be cached.
- **Local Qwen3** (`LocalBrain`): 0.6B, 1.7B or 4B with `transformers`, on the GPU when it
  fits. The model is asked for one JSON object, read leniently; an unreadable answer is
  asked for once more, then the kid types `look` and the turn is counted. First tests: 0.6B
  produces nonsense commands; 1.7B plays sensibly but slowly on the CPU here.

**Cost** is counted from the token usage each answer reports, at the prices in
`brain.PRICES`. A local model's tokens are priced as the cheapest Claude model: the figure
shows what it saved. `--max-cost` stops a run on that figure.

## The report

`report.py` renders one Markdown file per playthrough, rewritten after every sitting:

- the header (persona, traits, model, outcome, turns, hints, typos, cost);
- the sittings table;
- the debriefs;
- feelings, turn by turn;
- the confused, bored or frustrated moments;
- what the kid thought was important (to compare with the real clues);
- words not understood, and screens too long to read;
- what it kept in mind at the end;
- the transcript, screens as the kid read them.

Reports quote the game, spoilers included, so `runs/` is git-ignored.

## Known limits

- **The model is not a kid.** It is more patient and more obedient than a 12-year-old, and
  knows how text games and the history behind the story work (clocks and longitude, for
  one). The persona holds this back only partly.
- **Reading** is a fixed cut (above).
- **One screen per turn.** Text that arrives after the quiet period ends shows on the next
  turn.
- **Progress patterns are hand-written** in the game profile; a new kind of progress
  message must be added there.
- **No learning across playthroughs.** A returning player (a second adventure) can't be
  simulated yet.

## Open work

These have been discussed but not built yet:

- **A better reading model.** Short screens read whole; long ones skimmed: the first
  paragraph, sentences with highlighted words, the last line, the rest by chance; rereading
  when stuck.
- **A full-reading "checker" persona** for verifying that a game can be finished.
- **A plan** (`plan_depth`): goals and next steps carried between turns, at a depth set by
  the persona, with a plan timeline in the report.
- **Howto notes kept across playthroughs,** for an experienced player.
- **A scenario file** of a run's commands, in the game's `.ev` format, to replay its path.

## Where to change what

| To change | Look in |
|---|---|
| who plays | `personas/*.toml` (traits in `profiles.Traits`) |
| a game's address, reset, end, progress | `games/*.toml` (fields in `profiles.GameProfile`) |
| what the model is told | `brain.system_prompt`, `brain.turn_prompt` |
| the answer's fields | `brain.Move` (and `local.ANSWER_FORMAT`, `local.read_move`) |
| reading, boredom, sitting, typos, memory | `kid.py` |
| what ends a run | `playtester.play` |
| the report | `report.render` |
| prices | `brain.PRICES` |
