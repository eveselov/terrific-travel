# Proposal: "The Island That Moved"

A draft for the first Terrific Travel adventure: an expedition (structure #2) with a mystery
at its centre (#3), built on free exploration (#1). Everything here is a proposal to change,
rename or throw away. Names in particular are placeholders. This file contains the solution:
don't show it to the players.

## Pitch (to read aloud)

> It is 1790. Fifteen years ago a sailing ship, the *Halcyon*, left port to chart a small
> island far out in the ocean, and never came back. Most people say she sank in a storm. But
> last month a trader in the port began selling a brass compass with one word engraved on
> it: HALCYON.
>
> Now the Society sends a new expedition, and you lead it, as captain of its ship. She
> carries the tools of two sciences: the navigator's
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

The *Halcyon*'s chart has the island at the right latitude (14° S) but 1 degree too far
east: 40° W on the chart, 41° W in truth, about 108 km at that latitude, half a day's sail
(changed from 2° on 2026-11-16, so that the birds hold). That one mistake is why nobody
found the wreck: from the charted position the island is below the horizon, even from the
masthead. It is small enough that white terns fishing at the charted position still fly home
to the island at dusk (C6), and the arithmetic stays easy: 4 minutes of time per degree, so
noon comes 160 minutes after home noon at the charted position and 164 minutes after at the
island. Four minutes on the clock, a hundred kilometres of sea.

## The truth (fixed, stored in the game)

The game keeps this as data. Characters reveal parts of it; they never make up new parts.

1. In 1775 the *Halcyon* reached the island, charted it with a longitude error, and
   anchored off the western reef.
   - A passing whaler put in for water. The *Halcyon*'s master sent his last letter and a
     fair copy of his chart home with her ("We sail again soon"). The whaler left about a
     week before the storm. That is how the letter and the chart, error and all, reached the
     Society, and why nothing came after them. (Settled 2026-11-16.)
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
| The island is at 14° S, 41° W | — (the truth) | `things.yaml` (sextant, chronometer) |
| The *Halcyon*'s chart says 14° S, 40° W: latitude right, longitude 1° too far east | Latitude from the noon sun was easy in 1775; longitude needed a sea clock, which she didn't have | `things.yaml` (chart), Jonah's *chart*, the Ship's *latitude* and *longitude* |
| Noon comes 160 minutes after home noon at the charted position, 164 at the island | 4 minutes of time per degree (the Earth turns 15° an hour) | `things.yaml` (chronometer), the Ship's *longitude* |
| 1° at 14° S is about 108 km, half a day's sail | 1° of longitude ≈ 111 km × cos(latitude); about 200 km a day | `ship.yaml` (the route west from the charted position: morning to "early in the afternoon") |
| Home and the island lie on the same latitude, 14° S, so the course out is due west | Latitude sailing: keep the noon sun's latitude, sail east or west | `ship.yaml` (the Ship's answer to the order), `things.yaml` (chart, examined: the ruled line), the sea chart picture |
| The voyage out takes 21 days | 40° at 14° S ≈ 4,300 km, at about 200 km (110 nautical miles) a day | `ship.yaml` (the passage out, Day 4 to Day 21) |
| The wind out is steady from the southeast, and going home is slower | The southeast trade winds blow at 14° S; the great storm of '75 from the west was unusual (Barnaby's *storm*) | `ship.yaml` (the passages out and home, the Ship's "trade wind behind us") |
| Noon comes later by the home clock as the ship sails west | 4 minutes per degree, as above | `ship.yaml` (passage, Day 17), `things.yaml` (chronometer under way) |
| The charted position shows empty sea (C4) | The island is 108 km away, below the horizon even from the masthead (about 55–70 km) | `ship.yaml` (charted position) |
| From a masthead a lookout sees about 20 km of open sea, a hilly island 50–70 km away | The Earth's curve: horizon ≈ 3.6 km × √(height in m); a masthead of about 30 m sees a hill of 100–200 m from 55–70 km | the Ship's *horizon*, `ideas.yaml` (*The horizon*) |
| The Society trusted the chart; Barnaby thinks she sank | Nobody could check the longitude | Fairweather's *chart*, Barnaby's *halcyon* |
| The last letter and a copy of the chart reached home; nothing came after | A whaler that watered at the island carried them, a week before the storm | Fairweather's *letter* ("We sail again soon"), Jonah's *letter* |
| Barnaby found latitude with a sextant, like yours; your ship also carries a chronometer | The sextant (1757) gives latitude from the noon sun; only a sea clock gives longitude, so Barnaby's generation guessed it. Older sailors used Hadley's "quadrant" (really an octant, 1731), but the game says "sextant" for both, so players meet one instrument, not two (playtest 2026-11-19) | Barnaby's *sailing* and *sextant* (the old way), the Ship's *sextant*, *chronometer*, *longitude* (the new way) |

Holds.

### Birds: which way is land (C6)

| Fact | Depends on | Where it's written |
|---|---|---|
| At dusk at the charted position, white terns all fly west | They fish at sea by day and fly home to land to sleep, from as far as about 120 miles (about 190 km); the island is 108 km to the west | `ship.yaml` (the *sky* detail), the Ship's *birds*, `ideas.yaml` (*Seabirds at dusk*) |
| On the way west, noddies join the white terns | Noddies stray only about 40 miles (65 km) from land: seeing them means land is near | `ship.yaml` (the passage west) |

Holds (checked 2026-11-16: the Hōkūleʻa wayfinding pages and the Science Learning Hub, see
"Sources"). Red-footed boobies were considered and dropped: their foraging trips last one to
five days, so they don't reliably fly home at dusk.

### The wreck: where she was lost

| Fact | Depends on | Where it's written |
|---|---|---|
| The great storm of '75: three days of wind out of the west | Winds are named for where they come from: it blew towards the east | Barnaby's *storm*, the Ship's *wind*, `ideas.yaml` (*Names of winds*) |
| The *Halcyon* anchored off the island's west side | She had come from the east and charted the island | Jonah's *halcyon* |
| The anchors dragged and she struck the Western Reef at night (C7, C13) | A west wind drives a ship anchored off the west side onto that shore | Jonah's *wreck*, the *bones* on the Western Reef |
| The reef can be walked only at low tide | The ribs stand in the shallows | Ama's *reef*, the Ship's *tide*, the reef's own text ("you wait until the tide goes out": time is told, not kept, DECISIONS.md, 38) |

Holds.

### The compass: Crane's lie (meant not to hold)

| Fact | Depends on | Where it's written |
|---|---|---|
| Crane says it washed up on a beach after last winter's storm | His lie | Crane's *compass*, *beach*, *storm* |
| A coral crust has grown in its hinge (C2) | Coral takes years under water, not one winter on a beach; it is built by tiny sea animals in warm, clear, shallow water, and grows over anything lying on a reef | `things.yaml` (compass, `examine`; the animal guide), `ideas.yaml` (*Coral*) |
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
| Tui finds brass buttons with little anchors near the wreck, and Ama keeps more | Buttons off sailors' coats: the crew lived in the village (Jonah says so); Tui is Ama's grandchild | Tui's *buttons*, Ama's *tui* |
| Most of the crew sailed west, Jonah stayed | West led to the trading routes; he had married into the village | Jonah's *crew* |
| They sailed west, not home to the east | Out here the trade wind blows from the east (south-east) all year: the voyage out had it behind (Day 4), going home is slower against it, and a small boat can't beat into it for weeks | Jonah's *home*, the voyage's Day 4, the Ship's *home* route |
| The crew's families in the port still wait for news | Most of the crew came from this port; nobody ever came home, and the boat that sailed west was never heard of | Fairweather's *crew* |
| The compass reached the port through fishermen from the west (C3) | The crew left it as a gift; it was traded from island to island, eastward to the port | Crane's *compass* (truth), *fishermen* |

Holds.

## Structure: three acts, one session (30–60 minutes)

### Prologue: Limbo

The game starts in Limbo, dressed as a title page. Its description is the pitch above, and
its one exit leads into the Society Office.

### The ship

The players' ship is one room, her Deck, that travels with them through all three acts
(DECISIONS.md, 36):

| Place | What's there |
|---|---|
| Deck | The sky, the sea, birds, coastlines: what you see changes with where the ship is and the time of day. `sail`, the noon sight and going ashore happen here, and the Ship's voice is heard. Beside the wheel, the **chart house** keeps the instruments and records: the sextant, the chronometer, the chart table with the *Halcyon*'s chart, and the books. |

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
- **Navigation:** a player takes a noon sight with the sextant (latitude matches
  the chart) and compares the moment of noon with the chronometer (longitude doesn't). So the latitude can be trusted
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
  the draft. Built (2026-11-14): a day north, south or east of the charted position, where
  the instruments show what changed (latitude 12° or 16° S; longitude 38° W, on waters the
  ship crossed on her way out), and the only way on is back. The water isn't counted yet.

### Act 3: The Island

Explore, talk, collect clues, then make the report.

| Place | What's there |
|---|---|
| Lagoon Beach | Landing place. Goats (the animal guide: "goats aren't native to islands like this"). |
| Village | The elder, the child, a hut built with a dark, heavy timber. |
| Western Reef | **Walked at low tide** (told in the text, never waited for: DECISIONS.md, 38). Ship's ribs in the coral, a corroded cannon. |
| Forest Path | Native trees (the plant guide names them, and they are not oak). |
| Spring | Fresh water (refill casks). A small onion patch nearby. |
| Hilltop | View of the whole island. With the chart, the coastline can be compared to it. |
| Boat Cove | Old wood chips, a slipway, a carved board. Jonah Pike is often here. |

**Ending:** anywhere, at any moment, a player can `report` what happened (DECISIONS.md, 29).
The report asks three questions one at a time, the same ones that stand at the top of the
journal from the start (`task` in clues.yaml; DECISIONS.md, 28). Each is answered by picking
from choices that open with the clues in the journal:
- What happened to the *Halcyon*, and where? (The answer it checks: where she wrecked. The
  question doesn't say "wreck", which the Society doesn't know at the start.)
- Why did nobody ever find the *Halcyon*?
- What became of the *Halcyon*'s crew?

One player's answer counts for the whole expedition. A wrong choice is turned down with a
hint of what is missing, and the players can go back and look again, so it doesn't feel like
failing a quiz. Once all three questions are answered, the full epilogue follows; there is no
partial one.

## Characters

Each character has a short list of **topics** they know about. For each topic the game
records whether they know the truth, are mistaken, or are hiding it. In the draft their
replies are scripted lines. Later, the AI writes the replies, and the game still decides
what gets revealed.

| Character | Where | Role in the mystery | Knows / believes |
|---|---|---|---|
| **Mrs. Fairweather**, patron of the Society | Office | Gives the mission | The *Halcyon*'s plan, the chart, her last letter. Honest but knows little. |
| **Old Barnaby**, retired sailor | Quay | **Mistaken** | Sure the *Halcyon* sank in "the great storm of '75". Right about the storm, wrong about the sinking. Good on sailing lore. |
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
| C4 | Empty sea at the charted position | Deck, on arriving at the charted position; confirmed there by the noon sight (latitude 14° S) and the chronometer (40° W), each in yellow | — | The chart is wrong, not the ship's navigation |
| C5 | Latitude right, longitude wrong | `use sextant` (the noon sight, a flag for the expedition), then `read chronometer`, at the island | the sight first, by anyone. Noon (told: "you wait for noon") | *Which* of the chart's numbers is wrong; *why* is the players' to work out (the Ship's *latitude*, *longitude*, *reckoning*) |
| C6 | Birds flying west at dusk | `look sky` on the Deck, charted position | dusk (the ship arrives in the evening) | Land is to the west |
| C7 | Ship's ribs and cannon on the reef | `look bones` at the Western Reef | low tide (told: "you wait until the tide goes out") | Where she wrecked |
| C8 | Oak timbers in a village hut | `look beams` in the Village | carrying the plant guide, or `examine beams` | Ship wood was reused, so the crew survived to build |
| C9 | Goats and onions | `look goats` on the Beach, or `look shoots` at the Spring | the animal guide (goats) or the plant guide (onions): either one is enough | Europeans lived here for a while |
| C10 | Coastline matches the chart's shape | `look coastline` on the Hilltop | carrying the *Halcyon*'s chart (from the chart house) | This *is* the charted island, just misplaced |
| C11 | Tui's song about the winged canoe | `ask tui` about the song | — | The crew built a boat and left |
| C12 | Elder's account of the rescue | `ask ama` | showing respect (A4: not findable in A3) | Nobody died; the crew lived here |
| C13 | Jonah Pike's story | `ask jonah` at the Boat Cove (about the halcyon, the wreck, the boat or the crew) | C7 + C12 (A4: free in A3) | Confirms everything; the boat sailed west |

**Report needs:** wreck site = C7; why not found = C4 + C5 (or C10); crew = C12 or C13, plus
C11 or C8. Several paths reach each answer, so players can find things in different orders.

## World events (things that happen without the players)

None, by decision (DECISIONS.md, 38): time is told, not kept. The tide, dusk and noon are
part of what players read ("You wait for noon...", "You wait until the tide goes out..."),
so nothing is ever closed because of the hour, and nobody has to wait. The first plan was a
clock: the Western Reef opening and closing with the tide, the birds only in the evening,
Tui moving between the village and the reef, Jonah at the cove only part of the day. It was
dropped because the players may play online at different times, and waiting is the least
fun part of a short session. A later adventure could make time its theme.

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
- **Gates** (leaving port, reaching Jonah) are conditions checked by
  the destination room or the topic, so no exit can bypass them.
- **The ship** is one room, her Deck, that never moves. The Deck's view and its `ashore`
  exit change with the ship's position (Quay, positions at sea, island anchorage), which
  `sail <direction>` updates. The places the ship can reach are kept as data.
- **Ending:** a `report` command, usable anywhere, that checks answers against the journal (DECISIONS.md, 29).
- **The screen** has three panes: Main (text), Map and Focus (the room's picture, or the
  thing being examined). The map switches by act: the port plan, the sea chart (the
  *Halcyon*'s chart, with the island in the wrong place until it's found, and the ship's
  track) and the island map. Everything in Map and Focus is also in text.

Size: 12 rooms (3 port, 2 ship, 7 island) plus the Limbo prologue, 7 characters, 13 clues. That's small enough to build quickly and play in
one visit.

## Sources

Checked on 2026-11-16 (DECISIONS.md, 9). The players' version is the epilogue's last page in
[report.yaml](../world/content/report.yaml).

| Fact | Source |
|---|---|
| White terns range about 120 miles (about 190–200 km) from land, noddies about 40 miles (65 km); both fly home to land at dusk, and wayfinders follow them | Polynesian Voyaging Society, "Locating land" (archive.hokulea.com/navigate/land.html); Science Learning Hub, "Locating land" (sciencelearn.org.nz/resources/629-locating-land) |
| Red-footed boobies forage about 113 km out on trips of 1–5 days (why they weren't used) | Trevail et al., *Marine Ecology Progress Series* 724 (2023), doi 10.3354/meps14479 |
| Harrison's H4 tried at sea in 1761; Kendall's copy K1 went with Cook on his second voyage, his "never failing guide" | Royal Museums Greenwich (rmg.co.uk), K1 and the timekeeper method |
| La Pérouse vanished in 1788; Dillon saw a silver sword guard on Tikopia in 1826, which led to Vanikoro; anchors and cannon on the reefs; survivors built a small boat and left, never seen again | Australian Dictionary of Biography, "Dillon, Peter"; Solomon Islands Historical Encyclopaedia, "La Pérouse Expedition, 1785–1788" |
| Sandy Island: reported by the whaler *Velocity* in 1876, found to be deep water (over 1,400 m) by the *Southern Surveyor* in November 2012, then removed from maps | M. Seton et al., "Obituary: Sandy Island (1876–2012)", *Eos* 94(15), 2013 |
| 1° of longitude at 14° S ≈ 108 km; the Earth turns 15° an hour | arithmetic (111.3 km × cos 14°) |

Still to check: how fast coral grows over an object on a reef; ships carrying live goats and
onions on long voyages; the masthead horizon distances (the Ship's *horizon*).

## Questions for the kids (spoiler-free)

1. What is our ship called, and does she really have a mind of her own?
2. How scary should storms and wrecks be?

## Open questions for the author

1. ~~What happened to the crew who sailed west?~~ Left open on purpose (2026-11-16), as in
   the real story of La Pérouse's survivors; the epilogue says so. A later adventure can take
   it up.
