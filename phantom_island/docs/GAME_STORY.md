# Proposal: "The Island That Moved"

A draft for the first Terrific Travel adventure: an expedition (structure #2) with a mystery
at its centre (#3), built on free exploration (#1). Everything here is a proposal to change,
rename or throw away. Names in particular are placeholders. This file contains the solution:
don't show it to the players.

## Pitch (to read aloud)

> It is 1790. Fifteen years ago the ship *Halcyon* sailed to chart a small island far out in
> the ocean, and never came back. Most people say she sank in a storm. But last month a
> trader in the port began selling a brass compass with one word engraved on it: HALCYON.
>
> You join a new expedition. Your ship carries the tools of two sciences: the navigator's
> sextant, clock and charts, which read the sun, the stars and the sea, and the naturalist's
> books, which read plants, animals, birds and the land. Your job: find out what really
> happened to the *Halcyon* and her crew.
>
> Look carefully, and trust nothing until it fits: in this story, every detail has a reason.

The game is played alone or together (see DECISIONS.md, 6a and 6b). There are no exclusive
roles: anyone can use any instrument and find any clue. Two players who split up just get
there sooner.

## The idea underneath

**A map is a theory about the world, and it can be wrong.** In 1790, sailors could measure
**latitude** (how far north or south they were) quite well from the height of the noon sun.
**Longitude** (how far east or west) was much harder: you needed an accurate clock, and the
first good sea clocks (chronometers) were new and rare. Older charts often put islands in
the wrong east-west position, and some "phantom islands" stayed on maps for centuries.
One of them, Sandy Island, was removed from maps only in 2012.

The *Halcyon*'s chart has the island at the right latitude (14° S) but 2 degrees too far
east: 40° W on the chart, 42° W in truth, about 215 km at that latitude, a day's sail. That
one mistake is why nobody found the wreck. It is small enough that seabirds fishing at the
charted position still fly home to the island at dusk (C6), and the arithmetic stays easy:
4 minutes of time per degree, so noon comes 160 minutes after home noon at the charted
position and 168 minutes after at the island.

## The truth (fixed, stored in the game)

The game keeps this as data. Characters reveal parts of it; they never make up new parts.

1. In 1775 the *Halcyon* reached the island, charted it with a longitude error, and
   anchored off the western reef.
2. A storm drove her onto the reef. Nobody died: islanders paddled out and rescued the crew.
3. The crew lived in the village for a season. They salvaged oak timbers from the wreck and,
   with the islanders' help, built a small boat in a sheltered cove.
4. Most of the crew sailed west in the boat, hoping to reach a known trading route. What
   happened to them after that is unknown, and the game leaves it open.
5. The ship's carpenter, **Jonah Pike**, stayed. He married into the village and still lives
   there, 15 years later.
6. As a gift, the crew left the ship's compass with a fisherman's family. Years later it
   was traded from island to island and reached the port. That's the hook.
7. Goats and a patch of European onions are still on the island, left by the crew.

## Facts that depend on each other

The game's details are meant to hold together (DECISIONS.md, 22). Each chain below lists
facts that rely on each other, and where each one is written. **Whenever one of them
changes, check the rest of its chain.** "Holds" says whether the chain is consistent and
plausible as it stands.

### Longitude: why nobody found her

| Fact | Depends on | Where it's written |
|---|---|---|
| The island is at 14° S, 42° W | — (the truth) | `things.yaml` (sextant, chronometer) |
| The *Halcyon*'s chart says 14° S, 40° W: latitude right, longitude 2° too far east | Latitude from the noon sun was easy in 1775; longitude needed a sea clock, which she didn't have | `things.yaml` (chart), Jonah's *chart*, the Ship's *latitude* and *longitude* |
| Noon comes 160 minutes after home noon at the charted position, 168 at the island | 4 minutes of time per degree (the Earth turns 15° an hour) | `things.yaml` (chronometer), the Ship's *longitude* |
| 2° at 14° S is about 215 km, a long day's sail | 1° of longitude ≈ 111 km × cos(latitude) | `ship.yaml` (the route west: "After a long day") |
| The charted position shows empty sea (C4) | The island is 215 km away, below the horizon even from the masthead | `ship.yaml` (charted position) |
| The Society trusted the chart; Barnaby thinks she sank | Nobody could check the longitude | Fairweather's *chart*, Barnaby's *halcyon* |

Holds, except the birds (next chain).

### Birds: which way is land (C6)

| Fact | Depends on | Where it's written |
|---|---|---|
| At dusk at the charted position, seabirds all fly west | They fish at sea by day and fly home to land at night; land is to the west | `ship.yaml` (the *sky* detail), the Ship's *birds* |

**Doesn't hold yet.** Terns and noddies, the birds island navigators watched, are usually
taken as a sign of land within roughly 20–50 km. The island is about 215 km from the charted
position. To check against sources (DECISIONS.md, 9) and then fix: either birds that range
further and still roost on land (boobies, frigatebirds: check), or the birds seen on the
voyage west, nearer the island, or a smaller error. A smaller error is limited by C4: a
hilly island can be seen from a masthead at about 50–70 km.

### The wreck: where she was lost

| Fact | Depends on | Where it's written |
|---|---|---|
| The great storm of '75: three days of wind out of the west | Winds are named for where they come from: it blew towards the east | Barnaby's *storm* |
| The *Halcyon* anchored off the island's west side | She had come from the east and charted the island | Jonah's *halcyon* |
| The anchors dragged and she struck the Western Reef at night (C7, C13) | A west wind drives a ship anchored off the west side onto that shore | Jonah's *wreck*, the *bones* on the Western Reef |
| The reef can be walked only at low tide | The ribs stand in the shallows | Ama's *reef*, the Ship's *tide* (A4: the tide gate) |

Holds.

### The compass: Crane's lie (meant not to hold)

| Fact | Depends on | Where it's written |
|---|---|---|
| Crane says it washed up on a beach after last winter's storm | His lie | Crane's *compass*, *beach*, *storm* |
| A coral crust has grown in its hinge (C2) | Coral takes years under water, not one winter on a beach | `things.yaml` (compass, `examine`) |
| The *Halcyon* was lost fifteen years ago, in the great storm of '75 | — (the truth) | Barnaby's *storm*, Fairweather's *halcyon* |
| Once C2 is found he admits fishermen from the west traded it to him (C3) | It came from island to island, eastward | Crane's *compass* and *fishermen* (truth) |

Holds as a lie: the dates and the coral contradict him, which is the point.

### Survival: what became of the crew

| Fact | Depends on | Where it's written |
|---|---|---|
| Nobody died: the islanders rescued the crew in their canoes | — (the truth) | Jonah's *wreck*, Tui's song, Ama (A4) |
| Oak beams hold up a village hut (C8) | No oak grows on a tropical island: it's the *Halcyon*'s timber, cut by shipwrights (nail, peg holes) | `places.yaml` (the *beams*), Fairweather's *halcyon* ("built of good oak") |
| Goats and onions on the island (C9) | Ships carried live goats and onions for long voyages; neither is native here | `places.yaml` (*goats*, *shoots*), the guides |
| A boat was built at the cove from the ship's oak, with island rope and a canvas sail | The slipway and old wood chips at the Boat Cove | Jonah's *boat*, `places.yaml` (*slipway*) |
| "A new canoe with a white wing flew away to where the sun goes to sleep" (C11) | A sailing boat, seen by children: the white sail is the wing; the sun sets in the west | Tui's *song* |
| Most of the crew sailed west, Jonah stayed | West led to the trading routes; he had married into the village | Jonah's *crew* |
| The compass reached the port through fishermen from the west (C3) | The crew left it as a gift; it was traded from island to island, eastward to the port | Crane's *compass* (truth), *fishermen* |

Holds.

## Structure: three acts, one session (30–60 minutes)

### Prologue: Limbo

The game starts in Limbo, dressed as a title page. Its description is the pitch above, and
its one exit leads into the Society Office.

### The ship

The players' ship is two rooms that travel with them through all three acts:

| Place | What's there |
|---|---|
| Deck | For observing: the sky, the sea, birds, coastlines. `sail`, the noon sight and going ashore happen here. What you see changes with where the ship is and the time of day. |
| Cabin | For instruments and records: the chronometer, the chart table with the *Halcyon*'s chart and the ship's own track, water casks, books, the Ship's voice, and the `report`. |

### Act 1: The Port

Get the mission, find the first real clue, and set sail.

| Place | What happens |
|---|---|
| Society Office | The patron gives the mission, the *Halcyon*'s old chart and her last letter home. |
| Quay | The old sailor tells the storm story (the wrong version). The players' ship is moored here. |
| Market | The trader has the HALCYON compass and lies about where it came from. |

Sailing from the Deck starts Act 2.

**Gate:** the players must learn from the trader that the compass came "from fishermen
who sailed in from the west". Then the ship can leave.

### Act 2: At Sea

This is the main puzzle.

- The ship reaches the charted position. **There is nothing there.** Just open sea. (Big
  moment: "the map is wrong".)
- **Navigation:** a player takes a noon sight with the sextant on the Deck (latitude matches
  the chart) and compares the moment of noon with the chronometer in the Cabin (longitude
  doesn't). Two players can do it together: one calls "noon!", the other reads the clock. So the latitude can be trusted
  and the longitude can't, and the fix is to sail along the same latitude. This is a real
  technique called *latitude sailing*.
- **Nature:** a player on the Deck watches the sky at dusk: seabirds that fish at sea return to land in
  the evening. Their flight shows which direction the land is. (Pacific navigators really
  used birds this way.)
- **Several routes west:** the trader's "fishermen from the west" (C3), the birds (C6) and
  the navigation (C5) each point west, and any one is enough to try `sail west`.
- **No dead end:** if players sail the wrong way or drift for a while, the Ship's hints get
  more direct until they all but say "west". Reaching the island is guaranteed; *why* the
  chart was wrong is asked again in the report.
- Sailing the wrong way costs a day and some water. That's the only resource pressure in
  the draft.

### Act 3: The Island

Explore, talk, collect clues, then make the report.

| Place | What's there |
|---|---|
| Lagoon Beach | Landing place. Goats (the animal guide: "goats aren't native to islands like this"). |
| Village | The elder, the child, a hut built with a dark, heavy timber. |
| Western Reef | **Only reachable at low tide.** Ship's ribs in the coral, a corroded cannon. |
| Forest Path | Native trees (the plant guide names them, and they are not oak). |
| Spring | Fresh water (refill casks). A small onion patch nearby. |
| Hilltop | View of the whole island. With the chart, the coastline can be compared to it. |
| Boat Cove | Old wood chips, a slipway, a carved board. Jonah Pike is often here. |

**Ending:** back in the ship's Cabin, the players `report` what happened. The game checks three
questions against the journal:
- Where did the *Halcyon* wreck?
- Why was she never found?
- What became of the crew?

A full answer gets the full epilogue. A partial answer gets a partial one, plus a hint of
what they missed. They can go back and look again, so it doesn't feel like failing a quiz.

## Characters

Each character has a short list of **topics** they know about. For each topic the game
records whether they know the truth, are mistaken, or are hiding it. In the draft their
replies are scripted lines. Later, the AI writes the replies, and the game still decides
what gets revealed.

| Character | Where | Role in the mystery | Knows / believes |
|---|---|---|---|
| **Mrs. Fairweather**, patron of the Society | Office | Gives the mission | The *Halcyon*'s plan, the chart, her last letter. Honest but knows little. |
| **Old Barnaby**, retired sailor | Quay | **Mistaken** | Sure the *Halcyon* sank in "the great storm of '75". Right about the storm, wrong about the sinking. Good on weather and sailing lore. |
| **Silas Crane**, trader | Market | **Hiding something** | Claims he "found the compass on the beach". The truth: he traded for it with fishermen from the west and fears being called a looter. He admits it if shown a journal clue that contradicts him (e.g. coral crust on the compass, spotted on a close look). |
| **Elder Ama** | Village | **Holds the key, cautious** | Remembers the rescue. Talks openly only after the players show respect (asking before going to the reef, or helping with something). |
| **Tui**, a village child | Village / Reef | **Knows the truth, not its meaning** | Plays on "the big bones in the reef", collects brass buttons, knows a song about "people from the sea who made a canoe with a white wing". Kids playing will probably love Tui most. |
| **Jonah Pike**, the *Halcyon*'s carpenter | Boat Cove | **Final witness** | Knows almost everything, including the direction the boat sailed. Only met late (after the reef and the elder), so he confirms the story rather than solving it. |
| **The Ship** (named by the kids) | Always aboard | **Hint-giver and explainer** | The players' own ship, with "a mind of her own". Gives hints that get more direct when the players seem stuck, and explains the instruments and the science when asked. A natural first AI character later. |

## Clues (the authoritative table)

Any player can find any clue. The "Needs" column says what it takes. Where it is built
(stage A3), each clue lives in the content files under `world/content/` (`clue: C<n>`); the
journal lines are in `clues.yaml`. "(A4)" marks a condition that is designed but not built yet.

| ID | Clue | Found by | Needs | Shows |
|---|---|---|---|---|
| C1 | Compass engraved HALCYON | `look compass`, Market | — | The ship didn't vanish without a trace |
| C2 | Coral crust in the compass hinge | `examine compass`, Market | a close look | It has been in seawater, not just "on a beach" (breaks Crane's lie) |
| C3 | "From fishermen who came from the west" | `ask crane` about the compass (or the fishermen) | C2 in the journal (he lies until then) | Direction to search |
| C4 | Empty sea at the charted position | Deck, on arriving at the charted position | — | The chart is wrong |
| C5 | Latitude right, longitude wrong | `use sextant` on the Deck (the noon sight, a flag for the expedition), then `read chronometer` in the Cabin; at the charted position or at the island | the sight first; two players can share the steps. Noon (A4) | *Why* the chart is wrong |
| C6 | Birds flying west at dusk | `look sky` on the Deck, charted position | dusk (A4) | Land is to the west |
| C7 | Ship's ribs and cannon on the reef | `look bones` at the Western Reef | low tide (A4) | Where she wrecked |
| C8 | Oak timbers in a village hut | `look beams` in the Village | carrying the plant guide, or `examine beams` | Ship wood was reused, so the crew survived to build |
| C9 | Goats and onions | `look goats` on the Beach, or `look shoots` at the Spring | the animal guide (goats) or the plant guide (onions): either one is enough | Europeans lived here for a while |
| C10 | Coastline matches the chart's shape | `look coastline` on the Hilltop | carrying the *Halcyon*'s chart (from the Cabin) | This *is* the charted island, just misplaced |
| C11 | Tui's song about the winged canoe | `ask tui` about the song | — | The crew built a boat and left |
| C12 | Elder's account of the rescue | `ask ama` | showing respect (A4: not findable in A3) | Nobody died; the crew lived here |
| C13 | Jonah Pike's story | `ask jonah` at the Boat Cove (about the halcyon, the wreck, the boat or the crew) | C7 + C12 (A4: free in A3) | Confirms everything; the boat sailed west |

**Report needs:** wreck site = C7; why not found = C4 + C5 (or C10); crew = C12 or C13, plus
C11 or C8. Several paths reach each answer, so players can find things in different orders.

## World events (things that happen without the players)

- **Tide:** the Western Reef opens and closes on a timer, so players may have to wait or come back.
- **Day and evening:** the birds appear only in the evening, and the fisherman goes out in the morning.
- **Characters move:** Tui wanders between the village and the reef; Jonah Pike is at the cove only part of the day.

## What it teaches

- Latitude vs longitude, and why longitude needed clocks (Harrison's chronometer).
- Dead reckoning and latitude sailing; birds as navigation signs.
- Tides and reefs.
- Plants and animals that travel with people as evidence of contact.
- How historians work: comparing witnesses, spotting contradictions, trusting evidence over rumour.

**Epilogue, "The real story":** after the ending, the game tells a short true story. The
French explorer **La Pérouse** vanished in the Pacific in 1788. In 1826 the Irish captain
**Peter Dillon** noticed a silver sword guard on the island of Tikopia. It led him to the reefs
of **Vanikoro**, where the wrecks were found. Some survivors are believed to have built a boat
and sailed away. The players have just solved a mystery shaped like a real one.

## How it maps onto Evennia (for the draft without AI)

- **Clues** are stored data (a module or prototypes) with the fields in the table above.
  Discovering one writes it to a **shared journal** object for the expedition (`journal` command).
- **Expertise** lives in objects, not in roles: instruments and books aboard the ship. Using one (`use sextant`, `read bird guide`) reveals extra description lines or a clue, for whoever uses it.
- **Conversation:** `ask <character> about <topic>`. Each character has a topic dictionary;
  each entry has a reply, the clue it reveals, and its conditions.
- **Gates** (leaving port, the reef at low tide, reaching Jonah) are conditions checked by
  the destination room or the topic, so no exit can bypass them.
- **Events** (tide, evening, characters moving) are Evennia Scripts.
- **The ship** is two rooms (Deck, Cabin) that never move. The Deck's view and its `ashore`
  exit change with the ship's position (Quay, positions at sea, island anchorage), which
  `sail <direction>` updates. The places the ship can reach are kept as data.
- **Ending:** a `report` command in the Cabin that checks the journal.
- **The screen** has three panes: Main (text), Map and Focus (the room's picture, or the
  thing being examined). The map switches by act: the port plan, the sea chart (the
  *Halcyon*'s chart, with the island in the wrong place until it's found, and the ship's
  track) and the island map. Everything in Map and Focus is also in text.

Size: 12 rooms (3 port, 2 ship, 7 island) plus the Limbo prologue, 7 characters, 13 clues. That's small enough to build quickly and play in
one visit.

## Questions for the kids (spoiler-free)

1. What is our ship called, and does she really have a mind of her own?
2. How scary should storms and wrecks be?

## Open questions for the author

1. What happened to the crew who sailed west? Leave it as a mystery for a later adventure?
