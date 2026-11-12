# Ideas for Games

This file is a collection of random ideas for games. Not a plan or commitment.

## Idea 1. Space-Map Travel

The world is a spatial map divided into several regions (rooms).
While moving the gamers see the overall space map on the right panel for general orientation and a local world view on every move or look.

**CLAUDE:** *The demo you have now already does this: a map pane for the big picture, and a room view on each move. It's a good base for every other idea here, not a game in itself.*

## Idea 2. Time-Map Travel

The world is a set of time slices - real historic maps or images of the world as historic people imagined and knew the world.

The characters can move both through the space in a particular time-map and through time - from one world view to another. The world maps mismatches can produce interesting gaming effects.

**CLAUDE:** *I think this is the strongest one.* The "mismatches" are the real gem, because historical maps were often *wrong*, and the errors can become gameplay:
- 17th-century maps showed **California as an island**. A player who trusts the 1650 map tries to sail around it and runs aground.
- **Columbus** used a too-small estimate of the Earth and expected Asia where America is.
- Medieval *mappae mundi* put Jerusalem at the centre and Paradise in the east. The world was drawn by belief, not measurement.

The player learns that a map is a *theory* about the world. That's exactly the "world view development" you wrote about. It also fits ships and planes naturally: one era per vessel type. Technically it's the demo plus one thing. Each place exists once per time slice, and "travel in time" is an exit to the same place on another era's map. Many of these old maps are public domain.

Possibly good for learning world view development.

## Idea 3. Chemistry Ensembles

Characters in the world are molecules. They can meet each other, split and merge thus creating different materials - liquids, gases, metals, ... They can create explosive nuclear masses or frozen crystals.

Possibly good for chemistry learning.

**CLAUDE:** *It's playable if it stays a **rules puzzle, not a simulation*: atoms with a few free "bonding hands" (valence), simple merge and split rules, and states that depend on temperature. A room can be a flask or a furnace, and heating or cooling the room changes what forms. "Critical mass" works as a rule too: too many uranium atoms in one room trigger a chain reaction. It's harder to design than travel, because the rules *are* the game, but you can't fake them.

## Idea 4. Miscelanneous ensembles

- musical notes and phrases
- electrical circuits with resistors, transformers, gyrators, capacitors
- mechanical analogies for friction, inertia, levers, springs
- These two can be combined into one world to demonstrate their equivalence

**CLAUDE:** The force–voltage analogy (mass ↔ inductance, spring ↔ capacitor, friction ↔ resistor) is a beautiful idea. As a whole world it's quite abstract for 12-year-olds. It might work better as **puzzles inside another world**, like a ship's rigging or a lighthouse's machinery. Music could work, since the web client can play sounds, but in a text game it's the weakest fit.

## Idea 5. Specific historic events

- American Revolution
- American Civil War
- Marco Polo trip
- Magellan trip
- Iliad and Odyssey
- Sumer history
- Roman empire

**CLAUDE:** 
- **Journeys** fit straight away, because they *are* Map Travel: Magellan, Marco Polo, and the Odyssey (mythic geography against the real Mediterranean is itself a time-map mismatch). **Magellan** is especially good. His voyage *changed the maps*: it showed the Pacific was far bigger than anyone thought. So it ties together both of your strongest ideas.
- **Wars and empires** (the American Revolution, the Civil War, Rome, Sumer) are about events and people more than space. They're better as eras you visit inside Time-Map Travel than as games of their own.

## Idea 6. Character Memories (AI)

AI-supported characters could maintain their memories along the game history. Without AI it could be just a log of their moves and encounteres. With AI support it will be set of AI-recognized and estimated memory records - individual character memory. Such a memory can be used by AI character to make all following interactions/cponversation enriched with broader context. The characters will accumulate individual personalities.

**CLAUDE:** *A character who remembers you is one of the things that would make AI characters feel truly alive, and kids notice it at once* ("Tui remembered I gave her a button!"). Two cautions shape how to build it:
- **Memories should be records the game keeps, not something the model invents.** Small models make up facts, and they would also make up memories. So the game stores short structured records: who met whom, when, what was said about which topic or clue, what was given or shown. The AI only *phrases* them ("You're the one who asked about the reef"). It's the same rule as the clues: the game holds the truth. It also keeps the prompt small, which matters on local hardware: pick the few records relevant to the moment, not the whole history.
- **It runs into the privacy decision.** Phantom Island doesn't log conversations (DECISIONS 8). A memory of "what the kids said" is a kind of log. Keeping only game-level facts ("asked about the compass", "showed respect"), never the kids' own words, gives most of the benefit and keeps that promise.

The non-AI half already exists in small form. A gate like "the Elder talks openly once you've shown respect" *is* a character memory. So the scripted version can grow naturally from A2–A4, and the AI version later adds phrasing and choosing which memories matter. **Personality change** over the game is worth trying, in a modest form: a few simple dials on top of a fixed character card, moved by what happens. For example, the cautious Elder warms up, or the trader grows more nervous each time he's caught in a lie. That's enough for characters to feel like they grow, without a full model of personality traits.

## Idea 7. Characters Network (AI)

A specific aspect of Character Memory (see above) it could build a character network: collection of interactions of a specific character with other characters in within the game.
That might create an additional enrichment of game scenarios and appearence. Implementing it hard-coded wold require mini-FaceBook logic (dev-costly, most likely boring); with AI support
it might be almost automatic and fun.

**CLAUDE:** *The most fun form of this is **gossip**: what one character learns travels to others.* Tell the trader you're looking for the *Halcyon*, and next day the old sailor on the quay says "I hear you've been asking about that compass…". Players see that the world reacts to them even when they aren't in the room.

I'd split the work differently than "hard-coded vs AI", though:
- **The network itself is cheap to keep as data.** It's not mini-Facebook, just a small table: who knows whom, how much they trust each other, and which facts (clue IDs, things players did) each one has heard, and from whom. A few simple rules move facts along it, for example "the trader tells the sailor what he hears, but not the Elder". For a handful of characters that's a small amount of code, and it's predictable, which a mystery needs.
- **The AI is the right tool for the wording**, not for running the network. If the model decides who becomes friends with whom, the story can drift in ways the game can't check, and running off-screen character-to-character conversations through a local model would be slow. So simulate the spread as data, and generate text only when a player is there to read it.

It has a strong educational side that fits Terrific Travel: **rumours change as they travel**. If each retelling can lose or distort a detail (the "telephone game"), players learn to ask *who told you that?* and to trust a witness who saw something over one who heard about it. That's exactly what historians do, and it's already one of Phantom Island's teaching goals (comparing witnesses, evidence over rumour). The old sailor's wrong storm story could even be explained by the network: he heard it third-hand.


## Idea 8. Episodic AI Reviews

Since low-brain AI (Qwen3-0.6) included into the game might present various dangers for privacy, safety, etc. And it could just start producing too much noise or noncese, it could be useful to use a real powerful AI. The game implementation might include an API subscription to a real AI (like Anthropic) and the game can request periodic reviews for its logged content from such strong reviewer. The results of such reviews could be various - from safety warnings to real game participation.

**CLAUDE:** *A small model playing live, with a strong model reviewing now and then, is a sound pattern.* The small one is fast, free and local; the strong one is slow and costs money, but it judges well. They complement each other. Three points shape how to use it:
- **Periodic review can't be the safety net.** By the time a review runs, a bad reply has already reached the child. Live safety has to stay local and immediate: the game decides what's revealed, topics are limited, replies are short, and a simple filter checks them. The reviewer's job is to find *patterns* afterwards ("Tui keeps drifting off topic", "the trader gave away C3 too early") so you can fix the prompts and rules.
- **It conflicts with two decisions, and sending things out makes it bigger.** The game doesn't log conversations (DECISIONS 8). A review needs a log, and sending it to an outside service means kids' words leave the house, so the parents' agreement would be needed too. A gentler version reviews only what the *AI characters* said, plus game-level facts, never the kids' own words.
- **The best first use is during development, where none of this applies.** In `llm_lab` and in Phase C, the strong model can grade the small model's replies against the character card and the clue rules, for many test questions at once, including the playtest transcripts you make deliberately. That's the "testing characters against transcripts" step from the staging plan, automated.

**Game participation** fits best where speed doesn't matter, between sessions rather than during play. For example: a "previously on the expedition…" recap, new rumours for the gossip network (Idea 7), or a longer epilogue. The usual rule still applies: it words and suggests, and the game keeps the truth.