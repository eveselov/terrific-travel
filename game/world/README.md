# world/

This folder is meant as a miscellaneous folder for all that other stuff
related to the game. Code which are not commands or typeclasses go
here, like custom economy systems, combat code, batch-files etc. 

You can restructure and even rename this folder as best fits your
sense of organisation. Just remember that if you add new sub
directories, you must add (optionally empty) `__init__.py` files in
them for Python to be able to find the modules within. 

# Branching Game Development

When you want to stop temporarily working on a game branch and switch to another branch you should make a checkpoint of the game state (evennia.db3 file). Here is the policy for that.

## Use the branch name in the checkpoint name

**Why the branch name:** the database changes whenever you *play*, not when you commit. After a session on `magellan`, the database is newer than any commit, and a hash name would be wrong after your very next commit. What really belongs together is "the `magellan` world" and "the `magellan` code, whatever its latest commit". The branch name says exactly that.

**Where to keep them:** a folder such as `game\server\snapshots\`. The existing `*.db3` rule in `.gitignore` covers every folder, so the copies are never committed. Branch names with a slash, like `try/magellan`, can't go straight into a file name, so use `try-magellan.db3`.

## The routine
Stop the server **before switching branches**, not only before copying. Otherwise the running server can pick up the other branch's code on its next reload while still holding the old world.

```powershell
cd C:\git\terrific-travel\game
uv run evennia stop
Copy-Item server\evennia.db3 server\snapshots\magellan.db3            # save magellan's world
git switch main
git switch -c trafalgar
Copy-Item server\evennia-clean.db3 server\evennia.db3 -Force          # trafalgar starts from the clean base
uv run evennia start
```
Going back later works the same way: stop, save `trafalgar.db3`, switch to `magellan`, copy `magellan.db3` back to `evennia.db3`, start.

## Two things that make the pairing matter even more
- **Evennia upgrades.** If one branch upgrades Evennia, its database gets new migrations, and older code can't use that database. A database is tied to its branch, not just to a moment in time.
- **The clean base.** Keep `evennia-clean.db3` as your shared starting point: superuser and Limbo, maybe the tutorial world. Every new game branch starts from a copy of it.

## An automatic option, for later
Evennia reads the database location from its settings. A few lines in your private `secret_settings.py` could pick the file from the current git branch, such as `snapshots\magellan.db3` on `magellan`. Then there's no copying at all: you stop, switch branches and start. The cost is a bit of hidden magic, and every new branch needs `evennia migrate` plus a superuser, or a copy of the clean base. I'd do the routine by hand a few times first. If it gets tedious, I can set up the automatic version.