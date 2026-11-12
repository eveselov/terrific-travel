# Phantom Island

The first Terrific Travel adventure (working title): an expedition with a mystery at its centre. The players, alone or together, look for a ship that vanished fifteen years ago and find out why nobody ever found her.

This is an Evennia game directory, created with `evennia --init phantom_island`, separate from
the playground in `../game/`. It has its own database, `secret_settings.py` and `mypy.ini`.

## Documents

| File | What it is |
|---|---|
| [docs/DECISIONS.md](docs/DECISIONS.md) | Settled decisions and development stages. Start here. |
| [docs/GAME_STORY.md](docs/GAME_STORY.md) | The story, structure, characters and clue table (draft). |
| [docs/GAME_INCEPTION.md](docs/GAME_INCEPTION.md) | The design conversation, kept for history. |

## Running

From the repository root, after `uv sync` (see [../BUILD.md](../BUILD.md)):

```powershell
cd phantom_island
uv run evennia migrate      # first time only: creates server/evennia.db3
uv run evennia start        # first start asks for the superuser (admin) account
```

Connect with a browser at <http://localhost:4011>, or with telnet/a MUD client at
`localhost:4010`. The ports are Evennia's defaults plus 10, so this game can run at the same
time as `game/` (4000/4001).

You were right that two tabs with two accounts is the way to do it. Tabs fail because they share the same browser session: you're logged in as Admin on the game's website, and every web client tab in that browser automatically logs in as Admin too. Each player needs a separate browser session.

**To use a second account** on the same computer (for testing and demo) open the second player at `http://127.0.0.1:4011`. The browser treats them as two different sites, each with its own login.

**Switching accounts:** In the web client: type quit. This back at the welcome screen, where connect <name> <password> logs in as someone else. (Logging into the same account twice kicks out the first connection.)

**Using telnet:** Switch on Windows' own telnet (Start → type "Turn Windows features on or off" → check Telnet Client → OK. No restart is needed); Then `telnet localhost 4010` works from any command prompt. To leave, type `quit` in the game. If you get stuck, press `Ctrl+]` and type `quit` at the telnet> prompt.

## Building the world

The world is built from the story content files in [world/content/](world/content/): places,
the ship and the maps, as YAML. On a new database it's built by itself the first time the
server starts. Otherwise, log in as the superuser and type:

```
batchcode build
```

Run it again whenever you've edited a YAML file. Rooms are updated in place, so nobody gets
moved, and the exits are made again from the files. A mistake in a file (an exit to a place
that doesn't exist, a position outside its map...) stops the build with a message naming the
file and the entry.

## Playing stage A1

New characters start in Limbo, which is the title page. Type `begin` to go into the Society
Office. From there:

- walk with compass directions (`se`, `east`...); `look` lists a room's exits;
- on the Quay, `aboard` takes you onto the ship's Deck; `down` goes to the Cabin;
- on the Deck, `sail` shows where the ship can go, and `sail west` sails. The ship won't leave
  while another connected player is still ashore (players in Limbo don't count);
- at the island, `ashore` lands you on Lagoon Beach;
- `map` describes the current map in words (for telnet) and redraws the Map pane.

The web client has three panes: Main (the text), **Map** and **Focus** (the room's picture, a
placeholder card for now). Main shows each command you type in light green after a divider
line, so the log reads as one section per command (login lines with a password aren't shown;
telnet clients show what you type themselves). Another player's turns (what they ask, say,
read or do, their comings and goings) start with a fainter dotted line and a muted first
line, so they sit between your own sections without looking like them. The server tags
those messages (`Character.msg`, and a turn count in `server/conf/inputfuncs.py`). The map switches between the port plan, the *Halcyon*'s sea chart
(with the ship's track) and the island map. Everything in Map and Focus is also in the text.

In stage A1 nothing is gated yet: you can sail straight to the island.

## Playing stage A2

The characters of the story stand in their places, and rooms list them under
"Characters". Talk to them with `ask`:

- `ask barnaby` greets Old Barnaby, who suggests a few topics;
- `ask barnaby about the storm` asks about one (`ask barnaby storm` works too). Words in
  white in an answer are worth asking about next; unknown topics get a polite "don't know";
- with only one person in the room, the name can be left out: `ask about storm`, or just
  `ask storm`. With several, the game asks whom you mean;
- one topic at a time: `ask fairweather about halcyon chart` answers *halcyon* and
  suggests asking about *chart* next;
- `ask` is for the story's characters. Another player gets a pointer to `say`, and
  something to look at (`ask beams`) gets a pointer to `look beams`;
- aboard, on the Deck or in the Cabin, `ask ship about longitude` asks the Ship herself;
- everyone in the room hears the conversation.

Who is where (as admin, `teleport Village` and so on gets you there quickly): Mrs. Fairweather in
the Society Office, Old Barnaby on the Quay, Silas Crane in the Market, Elder Ama and Tui
in the Village, Jonah Pike at the Boat Cove.

What they say is in [world/content/characters.yaml](world/content/characters.yaml)
(spoilers!). After editing replies, `reload` is enough; after adding characters or
changing where they stand, also `batchcode build`. In A2 everyone gives their first
answer: Crane doesn't admit the truth yet, and Ama doesn't wait for respect. Those come
with the clues and conditions in A3 and A4.

## Playing stage A3

Clues can now be found, and every clue goes into the expedition's shared **journal**:

- **Two colours carry meaning** (`help colours`): white words are worth following up (ask
  about them, or look at them), yellow words are a clue. A journal line always follows the
  yellow text, and every connected player hears about the new clue.
- `look <something>` looks at things (`look compass`) and at parts of a room
  (`look beams`); `examine <something>` (or `x`) looks closer. Builders still have Evennia's
  own `@examine` (and `ex`).
- **Things**: the compass in the Market (it stays on Crane's stall) and, in the Cabin, the
  sextant, the chronometer, the *Halcyon*'s chart and two guide books. `get` and `drop`
  the portable ones. Carrying a book or the chart shows more of what you look at: the plant
  guide in the Village and at the Spring, the animal guide on the Beach, the chart on the
  Hilltop. Carried things go back to their place when their carrier leaves the game, and
  also when the server starts cold or on `batchcode build`, if their carrier isn't being played.
- Looking at a thing or a detail shows a card with its name in the Focus pane; a plain
  `look` or moving on brings back the room's picture.
- `read <thing>` and `use <thing>` are heard by the whole room. The longitude puzzle: at sea,
  `use sextant` on the Deck (the noon sight), then `read chronometer` in the Cabin. One
  player can do each.
- `journal` lists everything found, in the order it was found, with who found it and
  where.
- Crane tells the truth about the compass once the coral in its hinge (`examine compass`)
  is in the journal. Ama still waits for respect, which comes in A4.
- **Late joiners**: while the ship is away, `begin` puts a new player on the Deck with a
  line about being seasick below. The journal is how they catch up.

In A3 nothing waits for time yet: the Western Reef is always open, the birds are always
there at the charted position, and noon is whenever you use the sextant. The tide, dusk and
noon come in A4.

To try it (spoilers):

```
uv run evennia reload        (new code: a reload is needed, then)
batchcode build              (as admin: places the things)
journal                      → still empty
teleport Market
look compass                 → C1
examine compass              → C2
ask crane about compass      → now he admits the truth, C3
teleport Cabin
get sextant
up
sail west                    → the empty sea, C4
look sky                     → the birds, C6
use sextant
down
read chronometer             → C5
journal
```

What each clue is, and the line it writes in the journal, is in
[world/content/clues.yaml](world/content/clues.yaml). The things are in
[world/content/things.yaml](world/content/things.yaml), and the details of each place in
`places.yaml` and `ship.yaml`. The content check stops the build if a text with a `clue`
has no `[[marked]]` part, if a marked part has no `clue`, or if a clue, thing or flag
doesn't exist. To start the journal again, reset the database (see BUILD.md).

## How it fits together

| Part | Files |
|---|---|
| Story content (YAML) and its typed loader | `world/content/*.yaml`, `world/content.py` |
| World builder (`batchcode build`) | `world/builder.py`, `world/build.py`, `server/conf/at_initial_setup.py` |
| Expedition state (where the ship is, her track, the journal, flags) | `typeclasses/scripts.py` (`Expedition`), `world/expedition.py` |
| Clues, yellow marks and the journal | `world/content/clues.yaml`, `world/clues.py`, `commands/discover.py` (`journal`) |
| Things, details, `look`/`examine`/`read`/`use` | `world/content/things.yaml`, `typeclasses/things.py`, `world/discovery.py`, `commands/discover.py` |
| Late joiners (`begin` while the ship is away) | `typeclasses/exits.py`, `world/ship.py` |
| Rooms: land, Cabin, Deck | `typeclasses/rooms.py` |
| Sailing, and the `ashore`/`aboard` exits | `world/ship.py`, `commands/ship.py` (`sail`) |
| Map and Focus panes, `map` command | `world/maps.py`, `world/focus.py`, `commands/explore.py` |
| Characters and `ask` | `world/content/characters.yaml`, `typeclasses/inhabitants.py`, `world/conversation.py`, `commands/talk.py` |
| Web client | `web/templates/webclient/webclient.html`, `web/static/webclient/js/plugins/`, `web/static/phantom_island/` (pane styles, map pictures) |

When you change `panes.css` or `panes.js`, bump `ASSET_VERSION` in `webclient.html`; otherwise
browsers keep using their cached copy.

The map code is copied from the playground (`game/world/maps.py`) and changed: maps come from
YAML, the ship is drawn wherever she is, and the room picture goes to the Focus pane instead of
the text scroll.

## Checks

From inside this folder:

```powershell
uv run mypy .
uv run evennia test --settings settings.py .
```

Ruff runs from the repository root and covers all games.

## Status

Stage A1 (island skeleton): 12 places plus the Limbo prologue, the ship with `sail`, and the
Map and Focus panes with placeholder pictures. Tests check that every place can be reached and
that two players aboard see each other.

Stage A2 (scripted inhabitants): six inhabitants and the Ship, 41 scripted topics, and the
`ask` command. Next: A3, discovery and the shared journal.
