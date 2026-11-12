"""
Inhabitants: the people players can talk to (Mrs. Fairweather, Old Barnaby, Tui...).

They are characters nobody plays, built from `world/content/characters.yaml` by the world
builder. Because they are characters, rooms list them under "Characters" like players. What
they say lives in the content file, not on the object: an inhabitant only knows which
character id it is (its tag in category `inhabitant`) and looks the rest up.

The Ship has no inhabitant object: she is the ship, so `ask` finds her from her own rooms
(see `world/conversation.py`).
"""

from evennia.objects.objects import DefaultCharacter

from world.content import CharacterSpec, load_content
from world.places import INHABITANT_TAG_CATEGORY

from .objects import ObjectParent


class Inhabitant(ObjectParent, DefaultCharacter):
    """
    A character of the story, standing in a room and waiting to be asked things.

    Set by the world builder from the content files:
    - tag `<character id>` in category `inhabitant`: which character this is;
    - key, aliases and `desc`: name, other names and description.
    """

    def basetype_setup(self) -> None:
        """Nobody can pick up or play an inhabitant."""
        super().basetype_setup()
        self.locks.add("get:false();puppet:false()")

    @property
    def character_id(self) -> str | None:
        """The character id from the content files, or None if it wasn't built from them."""
        ids: list[str] = self.tags.get(category=INHABITANT_TAG_CATEGORY, return_list=True)
        return ids[0] if ids else None

    @property
    def spec(self) -> CharacterSpec | None:
        """What the content files say about this character, or None if they no longer do."""
        character_id: str | None = self.character_id
        if character_id is None:
            return None
        return load_content().characters.get(character_id)
