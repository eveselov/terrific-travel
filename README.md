# Terrific Travel

A text-based multiplayer adventure game (MUD) built on [Evennia](https://www.evennia.com/),
meant to be both fun and educational.

"Terrific Travel" is the series name. Directions discussed so far: travelling by ship (and
later by plane) with real historical context, and vessels that might have minds of their own.
The first adventure, **Phantom Island** (working title), is in
[phantom_island/](phantom_island/README.md).

## Quick start

```powershell
uv sync                     # create .venv with Evennia and dev tools (pinned by uv.lock)
cd game                     # or phantom_island
uv run evennia --initmissing  # create secret_settings.py with a fresh key (first time only)
uv run evennia migrate      # create the local database (first time only)
uv run evennia start        # first start asks you to create the superuser (admin) account
```

Then connect:

| Game | Browser | Telnet / MUD client |
|---|---|---|
| `game/` (playground) | <http://localhost:4001> | `localhost`, port `4000` |
| `phantom_island/` | <http://localhost:4011> | `localhost`, port `4010` |

Full instructions, checks and troubleshooting are in [BUILD.md](BUILD.md).

## Layout

```
pyproject.toml      # environment definition (uv), plus ruff and mypy settings
uv.lock             # pinned dependency versions (committed)
docs/               # series-wide design notes
game/               # the playground: an Evennia game dir for learning and trying features
  commands/         # player commands and command sets
  typeclasses/      # Python classes for rooms, characters, exits, objects...
  world/            # prototypes, help entries, batch-build files
  server/conf/      # settings.py and server hooks
  web/              # website and web client customisation
phantom_island/     # the first adventure: same Evennia layout, plus docs/ for its design
llm_lab/            # standalone lab for small local language models as game characters
```

Each game folder is independent, with its own database and settings. Games share no code.

## Status

- `game/`: picture maps and room pictures in the web client, plus a small map demo.
- `phantom_island/`: story drafted and decisions recorded in its `docs/`; the game folder is
  Evennia's template, with no content yet.
- `llm_lab/`: working; see its README.

## License

Copyright 2026 Eugene Veselov. Licensed under the [Apache License, Version 2.0](LICENSE).

The license covers everything in this repository. Evennia itself is a separate dependency under
its own BSD 3-Clause license. Runtime data (the game database, logs, `secret_settings.py`) is
never part of the repository. A separate license for game prose (room descriptions, stories)
may be added once such content exists.
