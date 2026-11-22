# Phantom Island Authoring Guide

*How to write the game's story: places, people, clues, things, the voyage and the notebook,
all in YAML files, without touching Python. For the players' view, see
[GAME_GUIDE.md](GAME_GUIDE.md); for the code, the README's "How it fits together".*

**SPOILERS.** This guide and every content file it describes give the mystery away. Don't
show them to the players (DECISIONS.md, 11).

## What goes where

Story lives in YAML, in `world/content/`; mechanics live in Python. Each file starts with a
comment listing its fields: that list is the reference, and this guide doesn't repeat it.

| File | Holds |
|---|---|
| `places.yaml` | Limbo (the title page), the port and the island: names, descriptions, exits, details to look at |
| `ship.yaml` | The ship's Deck (with its chart house), and the positions she can sail to: what is seen from them, routes, orders, voyage passages |
| `maps.yaml` | The map pictures for the Map pane: one per act (port, sea chart, island) |
| `characters.yaml` | The people and the Ship: where they stand, how they speak, what they answer (`ask`) |
| `clues.yaml` | The task at the top of the journal (what the expedition is for), the clues (a title and the line written into the shared journal), and the connection questions that link them (`think`) |
| `things.yaml` | Objects: to look at, examine, read, use, and sometimes carry |
| `ideas.yaml` | The notebook: areas and ideas about how the world works (optional) |
| `hints.yaml` | The next step for players who ask (`hint`) or are stuck: situations of play, each with three hints, nudge first (optional) |
| `councils.yaml` | Councils where exploring must converge on one decision: the steps the Ship asks, one at a time, each with choices and the proof the right one needs (optional) |
| `report.yaml` | The report: the choices for each of the task's questions, the proof each right answer needs, and the epilogue (optional) |

The design behind the content (the truth of the mystery, the clue table, the facts that
depend on each other) is in [GAME_STORY.md](GAME_STORY.md). The reasons for the rules below
are in [DECISIONS.md](DECISIONS.md).

## How the files refer to each other

The entities behind the files, and how they relate, are drawn in GAME_SCHEMA.md ("The
entities"); this section is the same model at the level of files and fields.

Entries are named by ids, and other files use those ids. A typo isn't silently ignored: the
content check runs whenever the files are read, and stops with the file and entry at fault
(`ship.yaml, position charted, route west: unknown position 'anchorag'`).

| Id | Defined in | Used in |
|---|---|---|
| Place id (`quay`, `deck`) | `places.yaml`, `ship.yaml` (`rooms`) | exits; a character's `where`; a thing's `where`; a position's `ashore`; an action's `only_in` |
| Map key (`port`, `island`) | `maps.yaml` | a place's `map`; a position's `map`; `sea_chart` in `ship.yaml` |
| Position id (`charted`) | `ship.yaml` (`positions`) | routes' `to`; `start`; a thing's `at:` (what it does at that position); a council's `at` |
| Clue id (`C4`) | `clues.yaml` | `clue:` beside any text that reveals it; `needs:`; a report answer's `proof` |
| Flag (`sight_charted`, `briefed`, `line_settled`) | `sets:` on a thing's `at:` step, on a topic, or on a council's step | `needs:` elsewhere; the task's `after:` (until it is set, the journal and the report show their `before:` texts) |
| Thing id (`chart`) | `things.yaml` | `with:` on details (more to see when carrying it) |
| Area id, idea id | `ideas.yaml` | an idea's `area`; `teaches:` beside any text that teaches it |
| Topic id (`storm`) | a character's `topics` | `suggest`; `topic_aliases` (words shared by all characters) |

## The marks in the texts

Two colours carry meaning (DECISIONS.md, 20). Never use them for decoration.

- **White, `|wlike this|n`:** something worth following up: a topic to ask about, a detail to
  look at, a command to try. Mark only words the game understands: a white word that leads
  nowhere is a broken promise. In what a character says, a white word is always one of
  *that character's* topics (players read it as "ask me about this"), or a whole command
  (`|waboard|n`, `|wexamine compass|n`); a person or a place elsewhere stays plain. The
  content check enforces it, and also that every topic can be found: in `suggest`, white in
  one of the character's own texts, or marked `hidden: true` (a surprise for whoever thinks
  of asking, like the Good Hope's name).
- **Plain still answers** (playtest 2026-11-22): anything a description names, white or not,
  can be looked at. Give it a short detail in `details` (aliases for the other words that
  name it), a line or two of flavour or of real knowledge, never a clue nobody points to.
  What slips through gets a safety net: a word that appears in the room's text answers
  "no more to it than you've seen", not "Could not find". The ship herself, seen from the
  shore she lies off, is `from_shore` in `ship.yaml`.
- **Yellow, `[[like this]]`:** a clue's fact. The text needs a `clue:` beside it, and only
  the fact itself is marked, never a whole reply. Only true facts: a mistaken or lying
  reply stays plain, so spotting it is the player's job. The check fails on a `clue:`
  without marks, and on marks without a `clue:`.
- **A paragraph break** in descriptions and thing texts: `|/`.

## Recipes

### A place or an exit

Add the place to `places.yaml` with a `name`, `desc`, `map` and `map_pos`, and give it exits.
Exits go one way: add the way back from the other place too. Compass directions get their
short forms (`se`) automatically. Then `batchcode build`.

A place players must discover first gets `hidden_until:` (DECISIONS.md, 40): the clues or
flags that show the way there. Until they hold, the place isn't on the map and the exits to
it are neither shown nor usable; when they hold, everyone is told of the new path. Something
in the story must set that flag (a topic's or truth's `sets`, or a place's `sets`, set on
arrival: the Hilltop shows the Village), and a hint situation must point to it.

### A character, or a topic

In `characters.yaml`: `where` they stand, a `voice` (how they speak), a `greeting`, a few
topics to `suggest`, and a polite `fallback`. The greeting names the suggested topics in
white, in the character's own words, and the game adds no list of its own (playtest
2026-11-22); only the Good Hope's topics come as a list, since they change with where she
is. Each topic needs a `stance` (truth, mistaken, hiding). A reply that starts with a quote is shown as speech (`Old Barnaby says: "..."`).

- Words every character should understand the same way (`the storm`, `old chart`) go in
  `topic_aliases` at the top of the file; asking several witnesses about the same word and
  comparing is the historian's lesson.
- A character who must be won over gets `trust:` (DECISIONS.md, 41): the `marks` (flags
  set by what players do), a `label` for the progress shown with each mark, and `won`.
  Name the rule in their own words, and in someone else's, and set each mark from a
  `truth` whose `needs` include the flag that the rule was told (`respect_rule`), so
  nothing counts by chance.
- Give each character a `self` topic (`hidden: true`): what they say when asked about
  themselves (`yourself`, `who are you`). A little character, and now and then a useful
  pointer (Barnaby was at sea the year of the storm). Without one, a short default.
- Mark the topic words in a reply in white, so players see what else to ask. Most replies
  should lead somewhere.
- Something a character **hides** gets a `truth:` with `needs:` (clue ids or flags) and
  its own reply: they say it once the expedition has found what it needs (Crane admits the
  truth once the coral, C2, is in the journal).

New topics or replies need only a `reload`; a new character, or a changed `where`, needs
`batchcode build`.

### A clue

1. Add it to `clues.yaml`: a short `title` and the `journal` line. The journal line says
   what was found and a little of why it matters, never the big conclusion.
2. Reveal it: put `clue: C<n>` beside the text that shows it (a topic reply, a detail, a
   thing's look or action, a position's Deck view) and mark the fact in it `[[...]]`.
3. Add it to the clue table in GAME_STORY.md: where it's found, what gates it, and what it
   proves for the `report`. If it proves an answer, add it to that answer's `proof` in
   `report.yaml`.

If the new clue fits together with another one, consider a connection question in `clues.yaml` (`connections`): the clues it `needs`, and a `question` that leads one step further, towards a question of the report, and says where the background lives. It must never state the conclusion. Say what `settled` it (a council step's flag, or `report:<question id>`), so it leaves `think` once it has done its job. List the notebook `ideas` that help with it: `think` shows players which they have, and the `learn` text of the others (ideas.yaml), so every idea a connection lists needs a `learn`. Give ideas general titles ("How winds are named"): a title that sounds like a find gets mixed up with the clues.

The same clue can be revealed in several places, in different words. Finding it again adds
the new source to the journal entry instead of a new entry, so players can compare sources.

### A thing, something to read, something to use

In `things.yaml`: `where` it starts, a `desc` for `look`, optionally `close` for
`examine`, `read` and `use` actions. Set `portable: true` if it can be carried, and say so
in its `desc` (`You can |wget|n it`): players won't guess. A thing that isn't portable can
have a `stays:` line for when someone tries.

- `only_in` with `elsewhere`: it works only in one place (the sextant needs the Deck).
- `at:`, aboard only: what it does instead at each ship position. A position without an
  `at:` entry gets the plain `text`, so check every position where the thing can be used
  (the sextant has a reading at each).
- `sets:` and `needs:` on an `at:` step: the first step remembers a flag for the whole
  expedition, and a later one waits for it, with an `otherwise` text until then. That is how
  the noon sight and the chronometer make one measurement in two steps, whoever does each.

### A ship position, a route, a voyage

In `ship.yaml`, under `positions`:

- `deck`: what is seen from the Deck there. `clue:` on the Deck view reveals
  a clue on arrival (the empty sea, C4).
- `coords` (`14 S, 40 W`): lets players sail there by naming the position. `orders`: what
  `sail` alone says there, in words (leave out a ready-made menu where the choice should be
  the players' own).
- `routes`, by direction: `to`, optional `names` (`sail home`), the Ship's `order` reply,
  the `text` as she sets off, and the `passage`: lines shown a few seconds apart while her
  marker moves on the sea chart, the last one the arrival.
- `under_way` is the ship between positions; it has no routes.

Distances and days must agree with GAME_STORY.md's facts table (about 200 km, 2 degrees of
longitude here, a day).

### The report and the epilogue

In `report.yaml`, one entry per question of the task in `clues.yaml`, in the same order.
Each question has two to five `choices`; exactly one has `right: true`, an `answer` (the
line shown in the journal) and a `proof`: groups of clues, each needing any one of its
clues in the journal, with a `missing` hint shown while it isn't. Every other choice has a
`reply`: why it doesn't fit, and where to look.

The wrong choices are what the witnesses believe or claim, or a natural misunderstanding
(the wrong number of the chart). Never invent a new element just to be wrong: it would be a
false lead. A reply turns a choice down gently and points somewhere, never "wrong!".

The report is the players' case board, consulted all through the game, so it must show
only what they could know (DECISIONS.md, 32). Give each choice the clues that raise it
(`opens`); a choice without `opens` is what the Society believes at the start. The right
one must open together with a wrong rival (the same `opens`), or its appearing gives it
away. Write the right one as a claim, not an explanation, and check that no reply
mentions what the players can't know yet when its theory opens. Put the ones open from
the start first: theories are lettered among those open, in the file's order.

The epilogue is a list of pages, each a `title` and a `text`. Real facts in it go into
the "Sources" list in GAME_STORY.md and on the epilogue's last page (DECISIONS.md, 9).

### A council

Where many findings must become one decision (DECISIONS.md, 35), write a council in
`councils.yaml`. First find the decision's parts, each ruling something out: at the
chart's position, which number is wrong, which side, how far. If a decision has no parts,
it's a guess, and players will feel it. Each part is a `step`: the Ship's `question`,
two to five `choices` (one `right`, with its `proof`: clue ids or flags), a `reply` for
each, and the flag it `sets` once settled. A wrong reply leads back to the evidence; a
`missing` text says where to look while the proof isn't there. The `summary` sums up and
leaves the action to the player, but spells out what the decision means in the game's own
terms (a position to sail to, not only "about a degree"). Give each step a hint situation
(`missing:` its flag), so the hints follow the council, and have the scene offer it where
it can't be missed: in the place's own view (the Deck's `deck` text there, seen on arrival
and on every `look`), not in a passage line that scrolls past.

If the council answers questions of the report, list them in `concludes` (report question
id: a short conclusion). The report shows the conclusion once the council has decided, and
the game adds the command that signs it after the summary, so the summary itself needn't
mention the report. A council near the end needs a reason to come back to where it is held:
offer it in the view players see there, and in what they see of that place from nearby (the
ship as seen from the shore).

### A hint

In `hints.yaml`, situations are checked from the top, and the first that matches gives the
hint: put a situation before the ones it should win over. Its conditions say when it applies
(`ship` positions, clues or flags it `needs` or that are still `missing`, an `unanswered`
report question). Its three `hints` go from a nudge (where to look) to the exact command.
They are spoken by the Ship aboard and by the journal elsewhere, so write them as plain
advice that suits both, with no "I". When you add a clue, a gate or a timed event, check
that some situation leads players to it.

### An area or an idea for the notebook

In `ideas.yaml`: areas first (a `title` each), then ideas, each with an `area`, a `title`
and up to three texts, `heard`, `understood`, `used`, written to read as one paragraph:
the entry shows the texts up to the level a player reached.

Then tag what teaches it, beside where a `clue:` would go: `teaches: {latitude: understood}`.
A ship's route can teach too (on the route, next to `to:`): giving the order is `used`.
Conversations, reading and using teach everyone who hears them, up to `understood`; `used`
is only for whoever did it (put it on actions); looking teaches only the looker.

**The rule:** an idea states how the world works, never what it means for the mystery.
"Coral grows only under the sea" is an idea; "so the compass lay in the sea" is a clue's
journal line; "so she wrecked on a reef" is the player's own conclusion. Keep the notebook
small: ideas the game actually uses.

## How to write

The full rules are at the top of `characters.yaml` (DECISIONS.md, 23). In short:

- **Short:** about 30–60 words, the answer first, then one concrete detail that is both
  vivid and a fact that fits the world. Depth is one question further down, behind a white
  word.
- **Plot, not prose:** richness comes from connections between people, things and clues
  (Barnaby on Crane's compass), not adjectives. Every noun is a promise players act on.
- **Facts not conclusions:** the game gives the facts and the knowledge behind them; the
  connection is the players' to make (DECISIONS.md, 22).
- **Every fact fits:** a number, distance, direction or date goes into GAME_STORY.md's
  "Facts that depend on each other", and is checked there whenever it changes. Real history
  is checked against sources (DECISIONS.md, 9).
- **Name the subject** at its first mention in each reply ("the Halcyon", not "she"):
  players read replies in any order.
- **Three ships, one "she".** The story has the *Halcyon*, your ship and the boat built on
  the island. Say "she" or "her" for a ship only right after naming that ship in the same
  text, never when another ship came up in between. Charts, islands and positions are "it".
  ("Take your ship to the island on *her* chart": whose? Write "on the Halcyon's chart".)
- **No dead ends:** every obstacle has at least two ways through and a hint path
  (DECISIONS.md, 6b).

## Trying a change

| Changed | Then, in the game as a builder |
|---|---|
| Anything read during play: replies and topics, clues, ideas, hints, councils, the report, details, things' texts, everything about the ship's positions (`deck`, `shore`, routes...), maps | `reload` |
| What the builder copies into the game: a place's name, description, exits, map position or picture; a character's or thing's name, aliases, `where` (and a character's description, a thing's `portable` or `stays`); the Deck's name and description; adding or removing a place, character or thing | `batchcode build` (rooms are updated in place; players stay where they are) |
| A map picture or other file in `web/static/` | `reload`, then a hard refresh in the browser |

- `startover`, `startover at sea`, `startover island` start a new expedition with the ship in
  port, at the charted position or at the island, for testing a later act without sailing
  there.
- `batchcommand/interactive scenarios.island` plays the normal scenario
  ([world/scenarios/island.ev](../world/scenarios/island.ev)): a typical way from Limbo to
  the island, with why each step is taken and what players know after it. `ss` runs the
  next command (`ss 5` the next five), `qq` stops, and you can play normally in between. It
  reaches a point in the story with a real journal and notebook, and shows the story as
  players meet it. It uses `sail/now` (builders only: the whole voyage at once). After a
  content change that touches its path, update its commands and comments.
- `record start <name> yes` makes a new scenario as you play: it starts a new expedition,
  keeps the commands you type (only yours, and only those any player could type), and
  `record stop` writes `world/scenarios/<name>.ev`, with what the game recorded after each
  command (new clues, notebook entries, where you are) and a `Why:` line for your reasons.
  To build a chain of scenarios, use `record checkpoint <next>` instead of `record stop`: it
  writes the file and goes on recording as `<next>`, from where you are, without replaying
  anything (the next file holds everything from the start). `record start <name> from
  <earlier> yes` plays an earlier scenario first, unrecorded, and starts the new file with
  its text, your `Why:` lines included.
- The content check runs on every `reload` and `batchcode build`, and the tests run it too:
  `uv run evennia test --settings settings.py .` from this folder. A content mistake shows
  up as a `ContentError` naming the file and entry.
