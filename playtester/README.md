# playtester: a player agent that plays like a kid

A developer who knows every secret of a game can't play it with fresh eyes. The playtester
plays it for you: Claude, playing a kid **persona**, connects to the running game over
telnet like any player and sees only its screens. It doesn't read the game's code or
content files or this repo, so it knows the game only from what the screen shows. Afterwards
it writes a report: where the kid got confused, bored or stuck, what it took for a clue,
which words it didn't know, and what it says about the game when asked.

It works for any game in the repo: a **game profile** in `games/` says how to reach and
reset it. It's not a replacement for kids: it is more patient and more obedient than a
real 12-year-old, and it knows how text games usually work. Use it to find dead ends,
unclear hints, texts too long to read and false leads before the kids play.

## Setup

1. An Anthropic API key, from <https://platform.claude.com> (API keys). The API is billed
   on its own prepaid credit, not through a Claude Pro subscription. Save the key for
   your user, then open a new terminal:

   ```powershell
   setx ANTHROPIC_API_KEY "sk-ant-..."
   ```

2. A game developer account in Evennia game to start the game over before 
   each run (`startover yes` for Phantom Island). The player can't do it: 
   its account is an ordinary player's.

   ```powershell
   setx PLAYTESTER_ADMIN_NAME "<your developer account>"
   setx PLAYTESTER_ADMIN_PASSWORD "<its password>"
   ```

   They are needed for `--reset`, which every new playthrough begins with.

3. The game's server running (`uv run evennia start`, inside the game folder).

The player logs in with the persona's name (Max, Lena, Sam...) and creates that account
the first time. Its password is `PLAYTESTER_PASSWORD` if set, or a fixed default.

## Run it

From the repo root:

```powershell
uv run python playtester/playtester.py phantom_island --persona max --reset
uv run python playtester/playtester.py phantom_island --persona max --turns 30
uv run python playtester/playtester.py phantom_island --persona lena --reset --model claude-sonnet-5-5
uv run python playtester/playtester.py phantom_island --persona sam --reset --turns 60
uv run python playtester/playtester.py phantom_island --persona max --manual
```

The first starts a new playthrough: the game is started over and Max begins with fresh
memory. The second carries on Max's playthrough from where the last run stopped.

Each turn prints what the kid typed, what it thought and the cost so far. Ctrl+C stops
the run; the report is still written.

| Option | What it does |
|---|---|
| `--persona <key>` | who plays: a file in `personas/` (default `max`) |
| `--model <id>` | `claude-opus-5-5` (default), `claude-sonnet-5-5`, `claude-haiku-5-5`... the same key works for all. Or a local model: `qwen3-0.6b`, `qwen3-1.7b`, `qwen3-4b` (see below) |
| `--turns <n>` | most turns to play in this run (200) |
| `--max-cost <dollars>` | stop this run once its estimated cost reaches this much (5; `0` for no limit). Checked before each turn, so a run can go over by one turn and the talk afterwards |
| `--reset` | start the game over and a new playthrough with fresh memory; without it, the persona's last playthrough carries on (see below) |
| `--no-debrief` | skip the talk afterwards |
| `--no-time-limit` | ignore the persona's sitting length (below), so only `--turns` and `--max-cost` end the run: for one long run to compare with another |
| `--manual` | you type instead of the model, and see each screen exactly as the agent would (no API key needed). Plays the game as it stands, or started over with `--reset`; no memory is loaded or saved, and the report is named `...-manual-...` |
| `--seed <n>` | the same typos and sitting length on every run |

**Cost:** each turn is one request, a few thousand tokens. With Opus 5.5, an estimate of
1 to 4 cents a turn (Sam about 1, Max 2, Lena 4: longer attention and memory mean more
text sent); Sonnet 5.5 about half that; Haiku 5.5 well under a cent. The printed figure is an
estimate; the Console's Usage page has the real one. Set a spend limit there.

### Local models

`--model qwen3-0.6b` (or `qwen3-1.7b`, `qwen3-4b`) plays with a Qwen3 model in this
process, with `transformers`, as in `llm_lab/` ([local.py](local.py)): no API key and no
cost. It gets the same prompts and the same kid limits as Claude, so the reports compare.

- **The cost shown** is what the same tokens would cost on the cheapest Claude model
  (Haiku 5.5), labelled "as the cheapest Claude model would cost; locally: free": the
  saving. `--max-cost` counts that figure too.
- **No structured output.** The model is asked for a JSON object and its answer is read
  leniently; an answer that still can't be read is asked for once more, then the kid just
  types `look`. The console and the report count those turns ("unreadable").
- **Thinking:** personas with `effort` above `low` (Lena) let the model think first, which
  is slower.
- **Where it runs:** the GPU in fp16 when the weights fit in its free memory, otherwise the
  CPU in fp32. On this PC (GTX 1650, 4 GB) only 0.6B fits; 1.7B runs on the CPU at about
  100 seconds a turn, and 4B would be slower still (and needs about 16 GB of RAM).
- **The first use** of a size downloads it into the Hugging Face cache (4B is about 8 GB);
  `HF_HUB_OFFLINE=1` keeps to the cache.

A first test (2026-11-25), one screen of the Society Office as Max: 0.6B answered in valid
JSON but typed nonsense (`type <screen> and press enter`), about 25 seconds a turn on the
GPU; 1.7B typed sensible commands (`help`, `look around`). For finding problems in the
game, the small models are much weaker players than Claude; they are useful for trying
the playtester itself at no cost.

### Progress

What counts as the game moving on is set in the game profile (`games/*.toml`): `progress`,
patterns of the game's own messages (for Phantom Island a new clue, a new or grown notebook
entry, an answer proved, a council's conclusion), and `room_title`, the pattern of a room's
title, so that reaching a place for the first time counts too. Progress ends boredom, and
it is where a kid whose time is up stops. Colours are taken out before matching, and the
whole screen counts, whether the kid read that far or not.

### Playing in several sittings

A sitting is one run: it ends when the kid stops for today, gives up, finishes, or hits
`--turns` or `--max-cost`, and the kid leaves the game. Leaving has effects in the game
too: Phantom Island puts back whatever the player carried (DECISIONS.md, 21). So several
short runs are not the same as one long one; for comparing two versions of the game, use
one long run (`--no-time-limit`).

Every run saves the kid's side of the playthrough in `runs/<game>-<persona>.state.json`:
the turns, both kinds of notes and what it has already seen. The game keeps its own side on the
server. A run without `--reset` picks both up: the turns numbered on from where they
stopped, and the kid told it has come back after a break. It comes back rested (tiredness
counts from the start of the sitting) and no longer bored. The report stays one file, with
a section per sitting. A run with `--reset` starts a new playthrough and replaces the saved
one.

A run without `--reset` stops, and says to use `--reset`, when there is nothing to carry
on: no saved playthrough for this persona yet, the playthrough has finished, or the game
has been started over since it began (by another persona's `--reset`, say: a reset starts
the whole game over, so the saved memory no longer matches it). The playtester never
starts the game over unless asked. A `startover` you type yourself isn't noticed, so don't
carry on a playthrough after one.

Two things can differ from where the kid stopped: things it carried go back to their
places when it leaves the game (Phantom Island, DECISIONS.md 21), and anyone else who
plays in between, or a `startover`, changes the game.

## Personas: what the playtester enforces

Telling a model "you have a short attention span" doesn't work: it still reads every word.
So the persona's traits are enforced by the program, not left to the model
([kid.py](kid.py)):

| Trait | Enforced how |
|---|---|
| `attention_words` | only that many words of each screen reach the model; the rest is marked `[... 85 more words you didn't read ...]` |
| `tired_after` | after that many turns, attention is halved and the kid is told it's tired |
| `patience` | how long the kid stands nothing happening before it is told it's bored; at twice that it gives up and the run ends. Progress (below) ends boredom, a screen with a good amount of new text eases it by a turn, and anything else adds a turn. Text that differs only in a short quoted word (a different typo in "Command 'norht' is not available") isn't new |
| `sitting_minutes` | `[shortest, longest]`: how long one sitting lasts, picked at random between the two (at about 30 seconds a turn). When the time is up the kid is told it must stop soon, and stops at the next good moment (progress), or 5 turns later anyway |
| `memory_turns` | how many earlier turns it remembers word for word (each screen and what it typed) |
| `thoughts_kept` | of those turns, how many of the latest bring back what the kid thought then, so its line of reasoning carries on (0 for none) |
| `notes_lines` | its notes "in the head" about this game (people, places, things, the mystery), rewritten every turn and cut to this many lines |
| `howto_lines` | its notes about how to play (commands that work, how to talk to people, getting unstuck), kept apart so game facts can't push them out |
| `typo_rate` | the chance that a command gets a slip of the fingers before it is sent |
| `effort` | how hard the model thinks (`low`, `medium`, `high`): the persona's smartness |

The persona's `about` and `experience` texts set its voice and what it knows. To add a
kid, copy a file in `personas/`. The shipped ones: **max** (12, keen, skims), **lena**
(12, reads everything, asks questions), **sam** (10, short attention, needs hints).

**Colours** reach the model as tags (`<white>compass</white>`), with no explanation of what
they mean: a kid sees colours too, and working out what they mean is part of playing.

## The report

`runs/<game>-<persona>-<time>.md` (git-ignored: it quotes the game, spoilers included):

- the outcome (finished, gave up bored, quit and why, stopped for today at a good moment
  or because time was up, turn or cost limit), turns, hints, typos, cost;
- **what the kid said afterwards**: fun, boring, confusing, stuck, what it thinks the
  game wanted;
- feelings turn by turn, and every confused, bored or frustrated moment with its thought;
- **what it thought was important**: compare with the real clues, since anything here that
  leads nowhere looked like a lead (Phantom Island's design rule 1);
- words it didn't understand, and screens too long to read;
- what it kept in mind at the end: its notes about the game, and about how to play;
- the transcript: each screen as the kid read it, its thought and what it typed.

## Files

| File | What it is |
|---|---|
| [playtester.py](playtester.py) | the command line, login and reset, the game loop |
| [telnet.py](telnet.py) | a small telnet client (Python 3.13 has no `telnetlib`) |
| [screen.py](screen.py) | the game's output as text, colours as tags |
| [kid.py](kid.py) | the persona's limits: attention, boredom, memory, typos |
| [brain.py](brain.py) | the prompts and the Claude call, one structured answer per turn |
| [local.py](local.py) | the same on a local Qwen3, its JSON answer read leniently |
| [report.py](report.py) | the Markdown report |
| [state.py](state.py) | the kid's memory between runs, and when the game was last started over |
| [profiles.py](profiles.py) | reading `personas/*.toml` and `games/*.toml` |
| [tests.py](tests.py) | tests that need no game and no API: `uv run python -m unittest tests` (inside this folder) |

mypy runs from inside this folder (`uv run mypy .`); ruff from the repo root.
