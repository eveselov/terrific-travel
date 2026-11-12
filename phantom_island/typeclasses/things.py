"""
Things: the objects of the story (the compass, the sextant, the books...), built from
`world/content/things.yaml` by the world builder.

Like inhabitants, a thing only knows which thing id it is (its tag in category `thing`) and
looks everything else up in the content. What looking, reading and using it shows is handled
in `world/discovery.py`, which also writes the clues it reveals into the journal.
"""

from typing import Any

from world.clues import show_marks
from world.content import ThingSpec, load_content
from world.places import THING_TAG_CATEGORY

from .objects import Object


class Thing(Object):
    """
    An object players can look at, and perhaps read, use or carry.

    Set by the world builder from the content files:
    - tag `<thing id>` in category `thing`: which thing this is;
    - key and aliases: its name and other names;
    - the `get` lock and `get_err_msg`: whether it can be picked up, and what is said if not;
    - `home`: the place it goes back to when the player carrying it leaves the game.
    """

    @property
    def thing_id(self) -> str | None:
        """The thing id from the content files, or None if it wasn't built from them."""
        ids: list[str] = self.tags.get(category=THING_TAG_CATEGORY, return_list=True)
        return ids[0] if ids else None

    @property
    def spec(self) -> ThingSpec | None:
        """What the content files say about this thing, or None if they no longer do."""
        thing_id: str | None = self.thing_id
        if thing_id is None:
            return None
        return load_content().things.get(thing_id)

    def get_display_desc(self, looker: Any, **kwargs: Any) -> str:
        """The description from the content, for any code that shows the default appearance."""
        spec: ThingSpec | None = self.spec
        if spec is None:
            return str(super().get_display_desc(looker, **kwargs))
        return show_marks(spec.look.desc.text)
