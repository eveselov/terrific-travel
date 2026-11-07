# Game Ideas

This file is a collection of random ideas for games. Not a plan or commitment.

## Map Travel

The world is a map divided into several regions (rooms).
While moving the gamers see the overall map on the right panel for general orientation and a local world view on every move or look.

## Time-Map Travel

The world is a set of time slices - real historic maps or images of the world as historic people imagined and knew the world.

The characters can move both through the space in a particular time-map and through time - from one world view to another. The world maps mismatches can produce interesting gaming effects.

Possibly good for learning world view development.

## Chemistry Ensembles

Characters in the world are molecules. They can meet each other, split and merge thus creating different materials - liquids, gases, metals, ... They can create explosive nuclear masses or frozen crystals.

Possibly good for chemistry learning.

## Other ensembles

- musical notes and phrases
- electrical circuits with resistors, transformers, gyrators, capacitors
- mechanical analogies for friction, inertia, levers, springs
- These two can be combined into one world to demonstrate their equivalence

## Specific historic events

- American Revolution
- American Civil War
- Marco Polo trip
- Magellan trip
- Iliad and Odyssey
- Sumer history
- Roman empire

## Claude Review

A common thread runs through all of it: **the player is a thing in a space with rules** (a ship on a map, a molecule in a flask, a note in a phrase), and the learning comes from working out those rules. That fits Evennia well, and it fits your AI plans too: an agent playing a ship or a molecule is the same "embodied object" idea.

**Map Travel.** The demo you have now already does this: a map pane for the big picture, and a room view on each move. It's a good base for every other idea here, not a game in itself.

**Time-Map Travel: I think this is the strongest one.** The "mismatches" are the real gem, because historical maps were often *wrong*, and the errors can become gameplay:
- 17th-century maps showed **California as an island**. A player who trusts the 1650 map tries to sail around it and runs aground.
- **Columbus** used a too-small estimate of the Earth and expected Asia where America is.
- Medieval *mappae mundi* put Jerusalem at the centre and Paradise in the east. The world was drawn by belief, not measurement.

The player learns that a map is a *theory* about the world. That's exactly the "world view development" you wrote about. It also fits ships and planes naturally: one era per vessel type. Technically it's the demo plus one thing. Each place exists once per time slice, and "travel in time" is an exit to the same place on another era's map. Many of these old maps are public domain.

**Chemistry Ensembles.** It's playable if it stays a **rules puzzle, not a simulation**: atoms with a few free "bonding hands" (valence), simple merge and split rules, and states that depend on temperature. A room can be a flask or a furnace, and heating or cooling the room changes what forms. "Critical mass" works as a rule too: too many uranium atoms in one room trigger a chain reaction. It's harder to design than travel, because the rules *are* the game, but you can't fake them.

**Other ensembles.** The force–voltage analogy (mass ↔ inductance, spring ↔ capacitor, friction ↔ resistor) is a beautiful idea. As a whole world it's quite abstract for 12-year-olds. It might work better as **puzzles inside another world**, like a ship's rigging or a lighthouse's machinery. Music could work, since the web client can play sounds, but in a text game it's the weakest fit.

**Specific historic events.**
- **Journeys** fit straight away, because they *are* Map Travel: Magellan, Marco Polo, and the Odyssey (mythic geography against the real Mediterranean is itself a time-map mismatch). **Magellan** is especially good. His voyage *changed the maps*: it showed the Pacific was far bigger than anyone thought. So it ties together both of your strongest ideas.
- **Wars and empires** (the American Revolution, the Civil War, Rome, Sumer) are about events and people more than space. They're better as eras you visit inside Time-Map Travel than as games of their own.

**My suggestion:** treat **Time-Map Travel** as the frame, with **Magellan** as the first episode. Chemistry can be a later, separate world. Its "beings that merge and split" rules would also be a good test bed for your agents.
