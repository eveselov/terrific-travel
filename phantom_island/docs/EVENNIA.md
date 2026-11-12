# Evennia Game Building Process

This document describes the steps typically performed for building a game on Evennia platform, and defines related concepts.

It supposed to be used as a guide for a typical game building in Evennia.

## Phase 1. Game Space Skeleton

### Rooms

In Evennia, everything in the game world is ultimately an Object. Characters and Rooms are just specialized kinds of Objects.

```
Object
├── Room
├── Character
└── Item/Object
```

- A Character is an in-game entity that can be controlled (puppeted) by an Account. It usually represents a player avatar such as a wizard, warrior, merchant, etc. By default, Evennia creates a Character for a new Account and lets the Account puppet it.
- A Room is a location in the game world. Rooms contain Characters and other Objects.
- An Object is the generic base type for things in the game world. Anything that is not specifically a Room or Character is often implemented as an Object. Objects can have attributes, commands, descriptions, and behaviors.

### How to Try/Test

Connect to the game, visit all places, verify connectivity, plan needed visuals for future work.
Check multi-play presence.

## Phase 2. Scripted Inhabitants

### Topics

#### What a topic is

A topic is the word the player types after "about": `ask barnaby about storm`. For each character, a topic leads to a scripted reply. Later it can also carry more:

| Field | Meaning | Needed from |
|---|---|---|
| keyword + aliases | `storm`, also `weather`, `great storm` | A2 |
| reply | the scripted line | A2 |
| stance | truth / mistaken / hiding (from GAME_STORY.md) | A2 as a note to yourself, in use from B |
| clue | which clue this reply reveals (e.g. C11) | A3 |
| condition | when the reply is available (e.g. Crane's true answer needs C2) | A4 |

A2 only needs the first two. The others can go in the YAML as empty fields so the format doesn't change later.

#### Per character or shared?

Both. **Each character has their own replies, but the same topic words are used across characters on purpose.** This is how the mystery works: players ask different witnesses about the same thing and compare.

```
ask barnaby about halcyon  → "Went down in the great storm of '75, all hands."
ask ama about halcyon      → (after respect) "The sea brought them to us. We brought them home."
ask jonah about halcyon    → "I was her carpenter. I helped put her on that reef, in a way..."
```

So I'd make two kinds of topics:

- **Common topics** that almost everyone answers in their own way: *halcyon, compass, island, storm, crew*. Comparing these answers is the historian's lesson from GAME_STORY.md.
- **Personal topics** that only one character knows: Tui's *bones*, *buttons* and *song*, the Ship's *sextant* and *chronometer*.

The aliases (`halcyon` = `the halcyon` = `ship's name`...) should be shared, so the same word means the same thing whoever you ask. Everything else stays per character. A topic one character doesn't know gets that character's own polite fallback ("Barnaby scratches his beard. 'Can't say I know much about that.'"), never an error message.

#### Topics and objects or rooms

- **Rooms and objects don't answer `ask`.** They answer `look`/`examine` (and `read`/`use` for books and instruments). Evennia has a ready-made idiom for this, *details*: `look ribs` on the Reef shows a line without needing an object. That's the A3 discovery layer, separate from conversation.
- **A topic can still be about an object or a place.** `ask crane about compass`, `ask ama about reef` and `ask ship about sextant` are all normal topics. The Ship is where object knowledge goes: she explains the instruments, so `use sextant` does the measuring and `ask ship about sextant` explains how it works.
- Showing something to a character (`show compass to crane`, which breaks his lie) is a separate verb, and I'd leave it for A4.

#### How players find topics

This is the classic weakness of `ask/about`: players guessing words. For 12-year-olds, I'd make `ask <character>` with no topic suggest a few, and have replies mention new topics in a highlighted colour (Barnaby mentions "the great storm", and `storm` becomes something to ask about). This is a design choice, not something already settled, so it's yours to accept or not.

#### How many topics

Start with 4-6 for most characters, 8-10 for central objects like Ship

#### AI Supported Characters

One longer-term point: in phase B, this topic list becomes the AI character's knowledge and its limits ("the game decides what is revealed"). Writing the topics carefully now is also preparing the AI interface.

### How to Try/Text

You can't try it in the game yet. `characters.yaml` is content only: nothing in the code reads it, there are no character objects in the rooms, and there's no `ask` command. If you rebuild the world now, nothing changes.

To make it playable, A2 needs this code:

1. **A loader** in `world/content.py` that reads `characters.yaml` into typed classes, the same way places and the ship are loaded.
2. **A `Character` typeclass** for the inhabitants. The build places each one in its `where` room, so `look barnaby` shows the description. The Ship gets no object in a room; `ask` finds her whenever you're on the Deck or in the Cabin.
3. **An `ask` command** that handles `ask <character>` (greeting plus suggested topics), `ask <character> about <topic>` (a reply, or the fallback), and aliases.
4. **Tests** for the loader and the command, with strict mypy and ruff passing.

Two simplifications for A2, since the rest belongs to later stages:
- **Hidden truths:** Crane and Ama always give their first reply. Their `truth` replies wait for A4's conditions.
- **Tui:** she stays in the Village. Moving her between the Village and the Reef also comes later.

Once that's built, trying it works like A1:

```
cd phantom_island
uv run evennia start          (or: uv run evennia reload, if it's already running)
```

Then open http://localhost:4011, log in, and run `batchcode build` as a builder to place the characters. After that you can type commands like these:

```
begin
ask fairweather
ask fairweather about halcyon
se
ask barnaby about storm
ask barnaby about pirates        → his fallback
```

On the island, `teleport village` (as admin) takes you straight to Ama and Tui. Aboard, `ask ship about longitude` works on the Deck and in the Cabin.

After that, editing a reply in the YAML needs only `uv run evennia reload`. Adding or removing characters, or changing where they stand, also needs `batchcode build` again.

Shall I go ahead and implement this?