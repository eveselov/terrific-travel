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
placeholder card for now). The map switches between the port plan, the *Halcyon*'s sea chart
(with the ship's track) and the island map. Everything in Map and Focus is also in the text.

In stage A1 nothing is gated yet: you can sail straight to the island.

## How it fits together

| Part | Files |
|---|---|
| Story content (YAML) and its typed loader | `world/content/*.yaml`, `world/content.py` |
| World builder (`batchcode build`) | `world/builder.py`, `world/build.py`, `server/conf/at_initial_setup.py` |
| Expedition state (where the ship is, her track) | `typeclasses/scripts.py` (`Expedition`), `world/expedition.py` |
| Rooms: land, Cabin, Deck | `typeclasses/rooms.py` |
| Sailing, and the `ashore`/`aboard` exits | `world/ship.py`, `commands/ship.py` (`sail`) |
| Map and Focus panes, `map` command | `world/maps.py`, `world/focus.py`, `commands/explore.py` |
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
that two players aboard see each other. Next: A2, scripted inhabitants.
