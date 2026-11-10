# world/

This folder is meant as a miscellaneous folder for all that other stuff
related to the game. Code which are not commands or typeclasses go
here, like custom economy systems, combat code, batch-files etc. 

You can restructure and even rename this folder as best fits your
sense of organisation. Just remember that if you add new sub
directories, you must add (optionally empty) `__init__.py` files in
them for Python to be able to find the modules within. 

# Games are folders, not branches

Each game lives in its own folder at the repository root, with its own database, so switching
between games needs no database snapshots. Snapshots for resetting or experimenting inside one
game are described in [BUILD.md](../../BUILD.md#resetting-the-game).
