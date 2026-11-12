# Decisions

The settled meta-decisions for Phantom Island, with what each one means for the work. The
discussion that led to them is in [GAME_INCEPTION.md](GAME_INCEPTION.md); the story draft is in
[GAME_STORY.md](GAME_STORY.md). Add a line here whenever something is settled, and change an
entry rather than adding a contradicting one.

Settled on 2026-11-10 unless noted.

## Development staging

The full playable game comes first, with no AI. AI characters come second, after a side step
to build the base AI package from the `llm_lab` findings.

| Phase | Content | Ends with |
|---|---|---|
| **A. Complete game without AI** | A1 island skeleton (rooms, exits, map) · A2 scripted inhabitants (`ask <char> about <topic>`) · A3 discovery and shared journal · A4 mystery, gates, events, ending · A5 polish · playtest with the co-designers · fixes | A finished adventure the co-designers have played and approved |
| **B. Base AI package** | B1 package design, its interface taken from A2 · B2 implementation · B3 one character switched to AI | One AI character in the game; the game still decides which clues are revealed |
| **C. AI characters** | One character at a time, tested against playtest transcripts · free conversation · second playtest | The same adventure with AI inhabitants |
| **D. Growth** | More adventures, islands, modes | — |

Every stage ends with something playable from start to finish, tested with two players logged
in (two browser windows are enough).

## Meta-decisions

| # | Topic | Decision | What it means for the work |
|---|---|---|---|
| 0 | **Name** | Working title **Phantom Island**, folder `phantom_island`. The co-designers choose the final title. | `SERVERNAME` and texts say "Phantom Island" until then. |
| 1 | **Sharing code with `game/`** | Share nothing. Copy what's needed. | Common abstractions get extracted only after at least two real games exist. `game/` stays a playground for trying things out, not a game to finish. |
| 2 | **Folder** | Created with `evennia --init phantom_island`. Design documents live in `docs/`. | Evennia's own layout is kept. The template hooks were copied from `game/` for their type annotations; the map feature was not copied. |
| 3 | **Repo docs** | Updated to "one folder per game", with `game/` as the playground. | — |
| 4 | **Ports** | Telnet 4010, web 4011, websocket 4012 (internal: web 4015, AMP 4016). | Set in `server/conf/settings.py`. It can run at the same time as `game/`. |
| 5 | **Language** | English only. | All texts, character topics and, later, AI prompts and tests. |
| 6 | **Connection and player count** | Mostly online from two homes, sometimes on a shared computer. **The game must also be playable by one player alone.** | Hosting over the internet (see BUILD.md: Tailscale is the simplest safe option). Two players must not be required. |
| 6a | **Solo play and roles** (2026-11-11) | **No exclusive roles.** Every player is an expedition member and can find every clue. Navigator and naturalist knowledge lives in the world: instruments (sextant, chronometer, spyglass), books aboard, and the Ship explaining things when asked. Cooperation is an advantage, not a requirement: with timed events (tide, dusk, Jonah's hours), two players who split up finish sooner. | The same game for one player, two friends, or a grandparent playing alongside as an adviser. No role tags; extra description lines come from using an instrument or book, not from who is looking. |
| 6b | **No dead ends** (2026-11-11) | **Move players forward gently; test understanding at the end.** Each bottleneck (above all At Sea) has several routes and escalating hints from the Ship. Reaching the island is guaranteed; *why* the chart was wrong is asked in the `report`. | Every gate needs at least two ways through and a hint path. |
| 7 | **World model** | One shared world. During solo development, resets are done by hand (wiping or restoring the database, see BUILD.md). **Checkpoints and rollbacks** are decided when the game goes to the co-designers. | Nothing to build now. Keeping the adventure's state (clues found, gates opened, journal) in one well-defined place will make checkpoints easy to add later. |
| 8 | **Privacy** | The real game does not log conversations. `llm_lab`'s replayable logs are for development only. | No transcript storage in the game. Playtest transcripts, if any, are made deliberately by the developer. |
| 9 | **History and culture** | Invented but plausible story. Real facts are checked and listed with sources. The islanders are an invented people, shown as capable and kind. The level of scariness is set by the co-designers. | A sources list goes with the epilogue and the educational facts. |
| 10 | **Scope guard** | None for now. Claude may suggest limits as work goes on. | The first month is solo development. Scope is discussed with the co-designers after the draft. |
| 11 | **How the co-designers take part** (2026-11-11) | **Eugene builds Phantom Island alone**, learning Evennia and game design along the way. The kids play, test and give feedback, and are not shown the game's secrets (co-designing a mystery spoils it). Their contributions are spoiler-free: e.g. the ship's name, how scary it gets. Later adventures can be co-designed openly. | Design documents in `docs/` are spoilers and are not shown to the kids. The grandson will likely play first (with Eugene), so he will know the answers when his friend plays; he can act as the friend's guide. |
| 12 | **Story content format** | **YAML** files, so story content can be edited without touching code. | Story content is kept in data files separate from the code. `pyyaml` is a declared dependency, and `types-pyyaml` (dev) lets strict mypy check code that reads it. |

## World and screen

Settled on 2026-11-11.

| # | Topic | Decision | What it means for the work |
|---|---|---|---|
| 13 | **Rooms** | 12 places: **Port** (Society Office, Quay, Market), **Ship** (Deck, Cabin), **Island** (Lagoon Beach, Village, Western Reef, Forest Path, Spring, Hilltop, Boat Cove), plus Limbo as the prologue. | The island layout in A1 is a first sketch, open to change. |
| 14 | **The ship: two rooms that travel** | **Deck** is for observing: sky, sea, birds, coastlines; `sail`, the noon sight and going ashore happen here. **Cabin** is for instruments and records: chronometer, chart table with the *Halcyon*'s chart and the ship's own track, water casks, books, later `report`. Longitude needs both: noon seen on deck, the chronometer read below (it really stayed below). **The Ship's voice is heard anywhere aboard** (2026-11-12): she answers `ask ship` on the Deck and in the Cabin, and is silent ashore. | The ship doesn't move between rooms; its Deck view and its `ashore` exit change with where the ship is (Quay, positions at sea, island anchorage). Places the ship can sail to are kept as data. The Ship is one character, found by `ask` from either ship room. Gates live in the destination rooms (e.g. the Western Reef checks the tide), so no exit can bypass them. |
| 15 | **Limbo is the prologue** | The game starts in Evennia's Limbo (`#2`), dressed as a title page: its description is the pitch, with one exit into the Society Office. | Limbo is not one of the 12 places and has no map; the Focus pane can show a title picture. |
| 16 | **Screen: three panes, maps switch by act** | **Main** (text scroll: descriptions, conversations, journal), **Map** (where am I?) and **Focus** (the current room's picture, or whatever is being examined: compass, letter, chart). The map switches with the act: a **port plan**, the **sea chart** (the *Halcyon*'s chart with the island where she put it and the ship's track; the true island appears once found) and an **island map**. | The picture-map feature is copied from `game/` and extended with the Focus pane. Pictures stay out of the text scroll. Everything shown in Map or Focus also exists as text, for telnet players. Placeholder pictures in A1; real art in A5. |
| 17 | **Nobody is left behind** (2026-11-11) | The ship won't sail while another connected player is still ashore. Players still in Limbo (the title page) haven't joined the expedition, so they don't count. | `sail` names who is still ashore and refuses. Follows from 6b: no player can be stranded by another. |
| 18 | **Late joiners** (2026-11-11) | **`begin` leads to wherever the expedition is.** While the ship is in port, `begin` goes to the Society Office as usual. While she is away, it puts the new player on the Deck, with a short in-story line (they were aboard all along, e.g. seasick below). The shared journal (A3) is how they catch up; the other player can guide them. Fresh runs (a reset world) stay possible. | To build in A3 or A4, next to the journal. Until then, an admin brings late joiners aboard with `teleport`. |
| 19 | **Conversation** (2026-11-12) | `ask <character> about <topic>`, scripted in [characters.yaml](../world/content/characters.yaml). **Topic words are shared on purpose, replies are per character**: asking several witnesses about the same thing (*halcyon*, *compass*, *storm*...) and comparing is the historian's lesson. Every character has a polite fallback for unknown topics. `ask <character>` alone greets and suggests a few topics, and replies mark further topic words in white. A first version has 4–6 topics per character and about 10 for the Ship. | Each topic records its stance (truth, mistaken, hiding), the clue it reveals (A3) and, for hidden things, a `truth` reply with its conditions (A4). Rooms and objects don't answer `ask`; they answer `look` (details), `read` and `use`. `show <thing> to <character>` is left for A4. In phase B this topic list is what an AI character may reveal. |

## Open questions

- Checkpoints: needed when the game goes to the co-designers; which commands, and what is saved? (from 7)
- How did the *Halcyon*'s chart and last letter reach home, if she wrecked soon after charting the island? (from A2: Fairweather's replies leave it vague)
- The spoiler-free questions for the kids at the end of [GAME_STORY.md](GAME_STORY.md).
