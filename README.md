# Carribean

A text-based multiplayer game (MUD) built on [Evennia](https://www.evennia.com/).

The game's purpose and setting aren't decided yet. Ideas being considered: something
educational, or a game based on historical pirate stories of the Caribbean. For now the
repository is a clean, working Evennia environment for learning the platform.

## Relation to ANIMA

The sibling [anima2](../anima2) project proposes Evennia as the shared world its fine-tuned
models would eventually live in (see `anima2/docs/MUD.md`). This repo is the place to learn
Evennia first. **There is no AI code here**, and none is planned for this phase. If that
changes later, see [BUILD.md](BUILD.md#future-ai-integration) for how to add it without mixing
dependencies.

## Quick start

```powershell
uv sync                     # create .venv with Evennia and dev tools (pinned by uv.lock)
cd game
uv run evennia migrate      # create the local database (first time only)
uv run evennia start        # first start asks you to create the superuser (admin) account
```

Then connect:

- browser: <http://localhost:4001>
- telnet / MUD client: `localhost`, port `4000`

Full instructions, checks and troubleshooting are in [BUILD.md](BUILD.md).

## Layout

```
pyproject.toml      # environment definition (uv), plus ruff and mypy settings
uv.lock             # pinned dependency versions (committed)
game/               # the Evennia game directory (created by `evennia --init game`)
  commands/         # player commands and command sets
  typeclasses/      # Python classes for rooms, characters, exits, objects...
  world/            # prototypes, help entries, batch-build files
  server/conf/      # settings.py and server hooks
  web/              # website and web client customisation
```

## Status

Just scaffolded: the default Evennia game template, with type annotations added to the
template hooks and one smoke test.
