"""
Batchcode file: remove the map demo. In the game, as a builder: `batchcode map_demo.remove`.

Evennia runs this file with `caller` (whoever runs the command) already defined.
"""

from typing import Any

from world.map_demo.builder import remove_map_demo

caller: Any  # provided by Evennia's batchcode processor

remove_map_demo(caller)  # noqa: F821 (see above)
