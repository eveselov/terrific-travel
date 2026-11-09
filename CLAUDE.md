# CLAUDE.md — Persistent Context for Terrific Travel Sessions

## Project identity

**Terrific Travel**: a text-based multiplayer game (MUD) built on
[Evennia](https://www.evennia.com/), developed together with young co-designers (around 12
years old), so it should be both fun and educational. The name is settled; the
details are **not decided yet**. Directions discussed: travel by ship (and later by plane)
with real historical context, possibly ships and planes with minds of their own. Loose game
ideas are collected in [IDEAS.md](IDEAS.md). Don't invent setting, lore or mechanics unless
asked.

**Fun first.** The aim is to learn Evennia by building a game quickly with and for the young
co-designers. Visuals in the web client (maps, pictures) are welcome. The one habit to keep:
everything shown as a picture also exists as text (descriptions, exits, labels), so telnet
players can play too.

## Layout

- The repo root holds the uv environment (`pyproject.toml`, `uv.lock`). It is not an
  installable package (`[tool.uv] package = false`).
- `game/` is an Evennia game directory. The repo can hold several games as sibling folders at
  the root, each independent, with its own database and `mypy.ini` (see BUILD.md, "Several
  games in one repo"). Evennia puts the game folder on `sys.path`, so imports inside it are
  top-level (`from typeclasses.rooms import Room`, not `from game.typeclasses...`).
- Evennia CLI commands, mypy and tests run from inside a game folder; ruff runs from the
  repo root and covers all games.

## Implementation rules

1. **Explicit type annotations everywhere.** All parameters, return values and non-trivial
   locals are annotated. Use `list[T]`, `dict[K, V]`, `T | None`. `uv run mypy .` (strict),
   run inside each game folder, must pass. Evennia/Django are untyped: annotate with this game's own typeclasses where
   possible, and `Any` only for raw framework objects.
2. **uv only**, no raw `pip`/`venv`. `uv add <pkg>` / `uv add --group dev <pkg>`, run things
   with `uv run`. Commit `uv.lock`. Keep dependencies minimal; ask before adding any.
3. **Lint and format with ruff** (`uv run ruff check`, `uv run ruff format`, from the repo root).
4. **Tests** are `EvenniaTest` subclasses in `tests.py` modules, run with
   `uv run evennia test --settings settings.py .` from inside the game folder.
5. **Follow Evennia idioms** (typeclasses, cmdsets, prototypes, scripts) rather than working
   around the framework. Customise through `game/`; never patch `.venv`.
6. **Never commit runtime data**: `*.db3`, logs, `secret_settings.py` (git-ignored).
7. **Claude does not stage, commit or push.** Only edit files and leave them as uncommitted
   changes; the maintainer runs `git add`, `git commit` and `git push`. Creating or switching
   branches, or other history changes (reset, rebase, amend), also need an explicit request.

Hardware and run notes are in [BUILD.md](BUILD.md).
