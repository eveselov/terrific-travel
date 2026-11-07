# Building and Running

## Requirements

- [uv](https://docs.astral.sh/uv/) (tested with 0.8.18).
- Python 3.12 or newer. Evennia 6.x requires it. The repo pins 3.13 in `.python-version`,
  and uv downloads it if it isn't installed.
- Windows, Linux or macOS. Development so far has been on Windows 11.

All packages live in the project's own `.venv`, managed by uv. Never `pip install` into the
global Python.

## First-time setup

From the repository root:

```powershell
uv sync
```

This creates `.venv`, installs Evennia (the only runtime dependency) and the dev tools, all
pinned by `uv.lock`. Check it:

```powershell
uv run evennia --version
```

Then create the server's secret settings and the database. Evennia commands must run
**from inside `game/`**:

```powershell
cd game
uv run evennia --initmissing
uv run evennia migrate
```

`--initmissing` creates `game/server/conf/secret_settings.py` with a freshly generated
`SECRET_KEY`. It is git-ignored and must stay private. Without it, Evennia falls back to the
default key published in its own source. That is acceptable for local play only, never for a
server other people connect to.

`migrate` creates `game/server/evennia.db3` (SQLite). It is git-ignored, because it holds
accounts and password hashes.

## Running the server

```powershell
cd game
uv run evennia start      # starts Portal + Server in the background
uv run evennia stop
uv run evennia reload     # reload code changes without disconnecting players
uv run evennia status
uv run evennia --log      # follow the logs (Ctrl-C to stop following)
```

The **first** `evennia start` asks for a superuser name and password. That is the admin
("god") account you build the world with.

Connect with a browser at <http://localhost:4001>, or with telnet/a MUD client at
`localhost:4000`. The Django admin site is at <http://localhost:4001/admin>.

To start over with an empty world: stop the server, delete `game/server/evennia.db3`, and
run `evennia migrate` again.

### Windows notes

- Clone into a short path such as `C:\git\terrific-travel`. Evennia contains a migration file
  with a 108-character name, and in a deeply nested folder its path inside `.venv` passes
  Windows' 260-character limit, so the server and tests fail with a `ModuleNotFoundError` for
  `evennia.typeclasses.migrations.0003_...`. The other fix is to enable long paths
  (`LongPathsEnabled` in the registry, or the "Enable Win32 long paths" group policy).
- Windows may ask to allow Python through the firewall on first start. Allowing private
  networks is enough for local play.
- If `evennia start` reports the ports are in use, another server is still running.
  Run `uv run evennia stop`, or check with `netstat -ano | findstr :4000`.

## Checks

Run from the repository root:

```powershell
uv run ruff check game        # lint
uv run ruff format game       # format
uv run mypy game              # strict type check
```

Run tests from inside `game/`:

```powershell
cd game
uv run evennia test --settings settings.py .
```

Evennia's test runner is Django's, so the tests are `EvenniaTest` subclasses, not pytest
tests. Put tests in a `tests.py` next to the code they cover (see `game/typeclasses/tests.py`).

### Type checking and Evennia

Code is fully type-annotated and mypy runs in `strict` mode. Evennia and Django ship no type
hints, so in `pyproject.toml`:

- their imports are treated as `Any`;
- subclassing their classes is allowed (`disallow_subclassing_any = false`);
- ruff's `ANN401` (no `Any`) is off. `Any` is the honest type for a raw Evennia object, but
  prefer this game's own typeclasses (`Character`, `Room`...) in annotations where you can.

`game/server/conf/settings.py` is excluded from both tools, because it is a star import of
Evennia's defaults by design.

## Managing dependencies

```powershell
uv add <package>               # runtime dependency
uv add --group dev <package>   # dev-only tool
uv lock --upgrade-package evennia   # upgrade Evennia within the pinned range
```

Commit `pyproject.toml` and `uv.lock` together. After upgrading Evennia, run
`uv run evennia migrate` in `game/`: new versions often bring database migrations.
