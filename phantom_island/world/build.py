"""
Batchcode file: build (or rebuild) Phantom Island from the content files.

In the game, as a builder: `batchcode build`. Safe to run again after editing the YAML files
in `world/content/`; see `world/builder.py`.

Evennia runs this file with `caller` (whoever runs the command) already defined.
"""

from typing import Any

from world.builder import build_world

caller: Any  # provided by Evennia's batchcode processor

build_world(caller)  # noqa: F821 (see above)
