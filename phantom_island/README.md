# Phantom Island

The first Terrific Travel adventure (working title): an expedition with a mystery at its
centre. Two players, a navigator and a naturalist, look for a ship that vanished fifteen years
ago and find out why nobody ever found her. It is also playable alone.

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

## Checks

From inside this folder:

```powershell
uv run mypy .
uv run evennia test --settings settings.py .
```

Ruff runs from the repository root and covers all games.

## Status

Just created: Evennia's template with type annotations and one smoke test. No game content
yet. Phase A1 (the island skeleton) comes next.
