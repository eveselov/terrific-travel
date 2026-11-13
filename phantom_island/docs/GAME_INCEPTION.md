# Game Inception History

This file contains evolving notes regarding this game design.

---
## Possible Game Structures

**Eugene:** 

Now that the lab for exploring AI characters in a game is ready, it's time to start drsafting the game.

Five possible game structures. They are not mutually exclusive, but they represent genuinely different approaches.

### 1. The exploration game — discover the world
The players arrive in an unfamiliar world. They can move between locations, talk to inhabitants, inspect objects, discover places and gradually understand their surroundings.
There is no necessarily prescribed plot.

The game provides:
- A geographical space.
- Places with interesting properties.
- Characters with knowledge, interests and goals.
- Objects that can be discovered or used.
- Events that happen independently of the players.

What do the players do? They explore, investigate, exchange information and make discoveries. For example, on an ancient Mediterranean island:
- One player discovers an abandoned temple.
- The other talks to a fisherman who knows something about it.
- They compare their findings.
- They discover that the temple is connected to an ancient shipwreck.
The discovery is not necessarily a predefined sequence. The game world contains the underlying facts, and the players uncover them.

Multiplayer structure: Both players share the same world and can see each other. They can travel together or separately, exchange information and cooperate.

One interesting rule would be that discoveries made by either player become part of their shared expedition journal.

Advantages:
- Very natural for your project.
- Easy to start small.
- AI characters fit particularly well.
- Doesn't require complicated game mechanics.
Disadvantages:
- Without objectives, players may eventually wonder what they should do.
- The game needs interesting discoveries and events to maintain momentum.

### 2. The expedition game — accomplish a mission
The players form an expedition with a particular objective. For example: You have been sent to investigate an island that appears on an old nautical chart. A previous expedition disappeared there.

The expedition has:
- A starting point.
- An objective.
- A geographical area to explore.
- Limited resources.
- A collection of challenges.
- A conclusion.
Possible objectives:
- Find a lost settlement.
- Locate a missing ship.
- Establish whether an island is inhabited.
- Find a route across an unknown region.
- Investigate a mysterious astronomical phenomenon.

Multiplayer structure: The players are members of the same expedition, but they need not have identical responsibilities. One could be the navigator, the other the naturalist. The navigator understands maps, routes and celestial observations. The naturalist understands plants, animals and the landscape. These roles could have different information and capabilities. Only by combining their observations can they solve the problem.

Advantages
- Players always have a reason to do something.
- Clear beginning, middle and end.
- Easy to organize into relatively short adventures.
- Excellent opportunity for geographical and scientific discovery.
Disadvantages
- Requires more deliberate scenario design.
- Can become too linear if every discovery is prescribed.

### 3. The mystery game — discover what really happened
Something has happened, but the players don't initially know what.

For example: A ship has disappeared from an ancient harbor. Its cargo was found on the beach, but there is no sign of the crew.

The players must:
- Talk to witnesses.
- Examine objects.
- Visit relevant locations.
- Compare accounts.
- Identify contradictions.
- Construct a plausible explanation.

This is an excellent application of AI character system. Imagine that three inhabitants have different accounts of the disappearance. One is mistaken. Another is hiding something. The third knows the truth but doesn't understand its significance. The players have to work out what happened.

Multiplayer structure: This offers an interesting possibility: players can receive different information. Perhaps one player finds a letter while the other interviews a witness. They have to communicate their findings.

Advantages
- Strong motivation.
- Conversations become genuinely important.
- AI inhabitants can make the experience less predictable.
- Excellent for two-player cooperation.
Disadvantages
- Mysteries require careful construction.
- The underlying truth must be consistent.
- Small language models can invent facts, so the engine must maintain an authoritative record of clues and events.

### 4. The historical simulation — live inside another world
Here instead of sending the players on an adventure, you place them inside a functioning historical environment.

They might be:
- Merchants in an ancient Mediterranean port.
- Explorers in the Age of Discovery.
- Travelers along the Silk Road.
- Sailors aboard a Pacific expedition.

The world has its own activities and events. People work, trade, travel, argue, exchange information and pursue their own goals. The players can participate in these activities. For example, they might need to arrange a trading expedition, negotiate with a local merchant, find a reliable navigator and obtain supplies. There need not be a single prescribed plot.

Multiplayer structure: The players can have complementary interests. One is a merchant; the other is an explorer. They might cooperate, negotiate or compete.

Advantages
- Very good fit for autonomous inhabitants.
- Rich opportunities for historical exploration.
- High replayability.
- Can eventually become a persistent world.
Disadvantages
- More difficult to implement.
- Requires a functioning economic and social environment.
- Players may lack direction unless there are meaningful opportunities and events.

### 5. The competitive discovery game — two explorers, one world
This is worth considering because multiplayer doesn't necessarily mean cooperation.

Two players explore the same environment but have different objectives. For example:
- Both are trying to find an ancient astronomical instrument.
- One is following a historical account.
- The other is following clues from the local inhabitants.
They compete to discover it first. Alternatively, they could have different assignments:
- One must identify the island.
- The other must reconstruct its history.

The game can award points for:

- Discoveries.
- Correct interpretations.
- Efficient navigation.
- Solving mysteries.
- Finding objects.

An interesting variation is that the players can exchange information, trade discoveries or deliberately mislead each other.

Advantages
- Clear reason to play together.
- Simple scoring mechanisms can create motivation.
- Players have individual agency.
Disadvantages
- Competition can discourage collaborative exploration.
- Scoring can turn the game into a quiz.
- It may be less consistent with the exploratory spirit of TerrificTravel.

Please tell meabout such perspective and which of the options you would recommend as a starting point. I think that the next step will be implementing a game draft without AI but demonstrating apprppriate structural qualities, and maybe even approved by the customer (my grsndson with a friend]. After that we'll implement AI as a base package and start developingcharacters and world details with its help.

---
**CLAUDE:**

I'd start with **#2, the expedition, with a small mystery (#3) at its centre**, built from the exploration pieces in #1. I'd leave #4 and #5 for later.

### How the five options relate

They aren't really five separate games. They sit on top of each other:

- **#1 Exploration** is the base layer: places, objects, people, movement. Every other option needs it, but on its own it has no "why".
- **#2 Expedition** gives the players a goal, an ending and roles.
- **#3 Mystery** makes talking to people matter. That's where AI characters will earn their place later.
- **#4 Simulation** needs an economy and a working society. It's the most work and the hardest to make fun early. It's a good place to end up, not to start.
- **#5 Competition** is a mode you can switch on later in an existing world, such as two expeditions racing for the same wreck. It isn't a reason to build the world in the first place.

### Why expedition plus mystery

- **Two 12-year-olds need a reason to act within the first five minutes.** An expedition gives that: "a previous expedition disappeared there" is a hook a kid understands at once.
- **One session has a beginning, middle and end.** You can play a 30–45 minute adventure on a visit, finish it and talk about it. A world with no ending is hard to judge.
- **Different roles make two friends need each other.** If the navigator and the naturalist see different things in the same place, they have to talk, and that's the multiplayer game. Two players who see the same thing just walk around side by side.
- **It sets up the AI properly.** The weak spot of #3 is that small models make up facts. The fix is to have the game hold the truth and let the model only phrase it. If the draft works that way from the start, adding AI later means swapping one part, not rebuilding.
- **It fits what you've already discussed.** In [IDEAS.md](IDEAS.md), "the map is a theory" (old charts being wrong) works well as an expedition mystery: the lost expedition trusted a wrong chart. That's only a suggestion, though. The setting is for the co-designers to choose.

### What the draft without AI should show

The draft only needs to be small: 6–10 places, 3 characters, about 8 clues and one ending. But it should already have the parts the AI version will need:

1. **The game holds the truth.** Clues are stored data with IDs. Each one says where it is found and what it shows. Nothing important exists only in a sentence of text.
2. **Characters talk by topic.** `ask fisherman about temple` returns a scripted line that depends on what that character knows, gets wrong or is hiding. Later the AI rewrites the wording, but the game still decides which clue gets revealed.
3. **A shared expedition journal.** Whenever either player discovers something, it goes into a journal both can read with a `journal` command. This is the simplest way to make cooperation visible.
4. **Each role sees different things.** One room description changes with the role, which Evennia can do when it builds a room's text. For example, the navigator notices the stars and the coastline, and the naturalist notices the plants and the tracks. *(Later replaced: there are no roles. Every player can find every clue, and the navigator's and naturalist's knowledge lives in instruments, books and the Ship, so the game is the same alone or together. See [DECISIONS.md](DECISIONS.md), 6a.)*
5. **A way to finish.** Players `report` their explanation, and the game checks it against the clues needed. Saying "I think X happened" is more fun than ticking off a quiz.
6. **One event that happens without the players.** For example, a timed Evennia script makes the tide go out and opens a path, so the world feels alive.
7. **Text first, map on top.** Every location, exit and clue works over telnet, with the web map as an extra.

### Testing it with your grandson and his friend

Before writing much code, you could run one session at the table, with you playing the characters from a list of what each one knows. It costs an evening and shows you three things:
- whether the hook works on them
- whether the two roles actually make them talk to each other
- what each character needs to know

That list is exactly the data the draft and the AI will need. It also gives the kids their say before anything is built: they could choose between two or three one-line hooks.

---
## Game Story and Background

**Eugene:** Agreed on #2++. Can you try to give me a structural, story and charactersproposal for the game of that kind?

**CLAUDE:** I've written the proposal to [GAME_STORYL.md](GAME_STORY.md)

**The idea underneath:** a map is a theory about the world, and it can be wrong. In 1790 sailors could measure how far north or south they were (latitude) quite well, but east–west position (longitude) needed an accurate clock, and those were new and rare. The lost ship's chart has the island at the right latitude but about 110 km too far east, and that's why nobody ever found the wreck.

**Story:** in 1790 a trader in the port is selling a brass compass engraved "HALCYON". That's a ship that vanished 15 years earlier, and everyone thinks it sank in a storm. The players' expedition sails to the island on the Halcyon's chart and finds empty sea. The navigator works out that the chart's longitude is wrong, and the naturalist sees seabirds flying west at dusk, towards land. Only together do they know where to sail. On the real island they find the wreck on a reef that can only be reached at low tide. They also find oak timbers from the ship reused in a village hut, goats and onions left by the crew, and a child's song about a "canoe with a white wing". In the end the truth is that islanders rescued the crew, most of whom built a boat and sailed west, and the ship's carpenter stayed.

**Structure:**
- **Three acts in one session:** Port, At Sea, Island, about 12 rooms in all.
- **Ending:** the players `report` their answer to three questions. A partial answer gets a partial ending plus a hint, so it doesn't feel like failing a quiz.
- **Epilogue:** the real story it's modelled on. The explorer La Pérouse vanished in 1788, and decades later a sword guard seen on another island led Peter Dillon to the wreck.

**Characters:** there are seven, matching the three witness types we discussed:
- **Mistaken:** an old sailor who swears the ship sank in the storm.
- **Hiding something:** the trader, who lies about where the compass came from.
- **Knows the truth but not what it means:** Tui, the village child.
- **Cautious:** the village elder, who only talks openly once the players show respect.
- **Final witness:** the carpenter who stayed, Jonah Pike.
- **The patron** who sends the expedition.
- **The players' own ship**, which has "a mind of her own" and gives hints when they're stuck. She'd be a natural first AI character.

For the build, the most important part is the clue table: 13 clues, each saying where it's found, which role can find it and what it shows. The game holds that table as the single record of the truth. Each answer in the report can be reached by more than one route, so the two players can find things in different orders. The file also sketches how this maps onto Evennia.

All names, the island and the era are placeholders. The file ends with five questions for your grandson and his friend, including naming the ship.

**Halcyon** Name Choice Reasons

- **The meaning fits the story.** A halcyon is the kingfisher of Greek myth. "Halcyon days" were the calm days at sea when the kingfisher nested on the water. A ship named for calm weather that disappears in a storm is a quiet irony that adults will notice and kids can be told about.
- **It's a bird.** Birds are part of the mystery: the seabirds flying west at dusk show where land is. A ship named after a bird, found partly by watching birds, ties the two together.
- **It sounds right for 1790.** British ships of that time often had classical or poetic names, and Halcyon is in that style.
- **It works as the hook.** The whole mystery starts with one word engraved on a brass compass. That word needs to be short, unusual and easy to recognise. A common name like "Mary" or "Hope" wouldn't make anyone stop and think "that's the lost ship".
- **It's easy to spot in text.** In a text game, players will type and read it often, and it can't be mistaken for a place or a person.
---
## Game Development Staging

**Eugene:** Since the base AI model isnot yet available as a usable package (intentionally - to prevent developing platforms without deep understanding of practical experience), the first stages of game development should be planned as purely "unintelligent" design- static text, illustrative graphics, faked conversations- jusy for demo. Later the real AI characters development can be started (after side-stepping to developing base AI package). So theoverall staging could be something like this:

1. One small island with a dozen locations
2. Seven inhabitants characterized by preliminary static (non-AI) texts
3. Base AI madel package design and implementation (based on llm_lab findings
4. Using llm_lab for developing characters
5. Free exploration and conversation
6. A simple discovery mechanism and shared journal
7. One cooperative mystery
8. Two-player simultaneous play
9. A complete adventure with an ending

I think I can imagine how stages 1,2,3,4 will be happening with your help. As to further stages 5,6,7,8,9 - since I never designed/developed any games, they appear absolutely in dark to me, actually just as bling guesses asking for clarification. Please tell me what do you think of the overall plan and provide more elaborated development mrthod (I am not yet talking here about the details of the game itself, just development staging, and maybe estimates).

Starting from 4 the stages are not very clear tome

**CLAUDE:** Your list has the right pieces, but I'd change the order. Stages 5–9 are mostly game mechanics, not AI, so I'd build them all without AI first and add AI at the end. That's also why they feel unclear: in your list they come after the AI work, so they look like AI work.

## What I think of the plan

**1. Build the whole game "unintelligent" first, then add AI.** Stages 6, 7, 8 and 9 (journal, mystery, two players, ending) need no AI at all. If you build them first, you get a complete, playable adventure for your grandson and his friend to approve, and nothing waits on the AI package.

**2. Let the dumb game define the AI package.** It's best to design the AI package (stage 3) after you know exactly what a character has to do in the game. By then the scripted characters will have shown it: which topics they answer, which clues they may reveal, when they're allowed to, and what the game needs back from them. The AI package then has a clear job ("replace this scripted part") instead of being designed in the abstract. That fits your rule of building from practical experience.

**3. Two-player play isn't a stage.** Evennia is multiplayer from the start, so two people can log in on day one. Treat "two players at once" as a test you run at the end of every stage, not as a feature built at step 8.

**4. "Free conversation" (stage 5) is really the AI version of stage 2.** Without AI, talking means `ask Tui about reef`. With AI, the player types anything. So it belongs after the AI package, as an upgrade to characters that already work.

## Five game-development habits

These are the practices that make stages 5–9 less of a mystery:

- **Keep it playable at every stage.** Each stage ends with something one player alone, or two together, can play from start to finish, even if it's crude. Never finish a stage with only a part that can't be played yet.
- **Plain placeholders first** (game designers call this "greyboxing"). Rooms and characters with plain placeholder text come first, polished writing and pictures later. You find out whether the structure works before spending effort on decoration.
- **The core loop.** This is what players do minute to minute: move → look → notice something → ask someone → note it in the journal → think → move on. If this loop is fun with dull text, it will be great with good text. If it isn't fun, AI won't save it.
- **Playtests: watch, don't help.** Let the kids play while you watch silently. Note where they get stuck, bored or excited, then ask them afterwards. This is the main tool of game design, and kids are very honest testers.
- **Three ways to every conclusion.** Mystery writers use a rule of thumb: players miss clues, so every conclusion they need should be reachable by about three clues. A mystery with one path gets stuck. My proposal has about two paths per answer, and playtests will show whether that's enough.

One more trick suits your situation well: **you play the character yourself**. Evennia lets an admin take control of any character with the `ic` command. During a playtest you can *be* Tui or Elder Ama and answer the kids live as a human. Game designers call this a "Wizard of Oz" test. It's the best preview of AI characters you can get. The transcripts also give you exactly what stage 4 needs: real questions kids ask, and examples of good answers to test the AI characters against in llm_lab.

## Revised stages

Times are in **working sessions** (about 2–3 hours with me). They're rough and could easily be off by 1.5–2×.

*Updated 2026-11-12 for the game as it is now played: no roles, the same game for one player or several (DECISIONS.md, 6a and 6b). The settled version of these stages is the table in DECISIONS.md.*

### Phase A: The complete game without AI (this is what gets "customer approval")

| Stage | What gets built | Done when | Time |
|---|---|---|---|
| **A1. Island skeleton** | 12 rooms with exits, short placeholder texts, the map pane, the ship and the sea room | A player can walk everywhere; two players see each other | 2–3 |
| **A2. Scripted inhabitants** | 7 characters, `ask <char> about <topic>` with scripted replies, characters placed in rooms | Every character answers its topics; unknown topics get a polite in-character reply | 2–3 |
| **A3. Discovery and shared journal** | Clue table as data; details and things to look at and examine; instruments and books that anyone can use or carry and that show more (sextant and chronometer, the guides, the *Halcyon*'s chart); the shared `journal` command; late joiners | One player alone can find every clue not waiting for A4; a clue found by any player goes into the one shared journal, and every connected player hears of it | 2–3 |
| **A4. The mystery and the ending** | Gates (leaving port, meeting Jonah), each with at least two ways through and a hint path; tide, dusk and noon scripts; Ama's respect; the `report` command, the epilogue | The adventure can be played from start to finish, alone or together, and reach every ending | 3–4 |
| **A5. Polish for the kids** | Better texts, a few pictures, escalating hints from the Ship, the journal grouped under the report's questions (if the playtest asks for it) | You'd be happy to show it | 2–3 |
| **Playtest 1** | Kids play; you watch, possibly playing a character live | You have notes and transcripts | 1 visit |
| **Fixes** | Changes from what you saw | Kids want to play it again | 1–3 |

Phase A comes to about **13–20 sessions**. At two or three sessions a week, that's roughly **1.5–2.5 months** to a complete adventure without AI.

Two notes on doing it:
- Keep the story content (room texts, character topics, the clue table) in plain data files, separate from the code. The kids can then write and edit dialogue themselves, which is both co-design and learning.
- Run a two-player test at the end of every stage, even with just you in two browser windows.

### Phase B: The base AI package

| Stage | What gets built | Done when | Time |
|---|---|---|---|
| **B1. Package design** | Interface taken from A2: a character card, knowledge with clue IDs, the conversation so far in, a reply plus "clues mentioned" out | You can describe what the game asks of the package and what it gets back | 2–4 |
| **B2. Implementation** | The package itself, based on llm_lab findings (loading, prompting, streaming, logging) | It works standalone and has tests | 4–8 |
| **B3. First integration** | **One** character switched to AI (I'd pick the Ship or Tui); the rest stay scripted | The game still decides which clues are revealed; replies are fast enough on your hardware | 2–4 |

Phase B comes to about **8–16 sessions**, and it's the most uncertain part. The risks are response speed on your hardware, the model making up facts, and keeping a character's personality consistent.

### Phase C: AI characters (your stages 4 and 5)

| Stage | What gets built | Done when |
|---|---|---|
| **C1. One character at a time** | Develop each character in llm_lab, tested against the playtest transcripts | The character handles the real questions kids asked without breaking the clue rules |
| **C2. Free conversation** | Players type anything; topics become hidden "intents" the game still checks | Kids talk naturally and the mystery still works |
| **Playtest 2** | The same adventure with AI characters | You compare: did AI make it better, and where? |

This runs at about 1–3 sessions per character after the first. Playtest 2 matters because it shows exactly what AI added compared with the scripted version.

### Phase D: Growth (later)

More adventures, more islands, the crew who sailed west, a competitive mode, eventually the time-maps. By then you'll have a working pattern to repeat.

## Overall

The full plan is about **30–50 sessions**, or roughly 4–6 months at a relaxed pace. The milestone that matters most is the end of Phase A: a game the kids have played and approved, and a clear list of what the AI must do. I'd start with A1.

If it's useful, I can save this as a roadmap file in the repo, so the stages and "done when" checks stay next to the code.

---
---
---
## A1. Island Skeleton

**CLAUDE:** *A1 is built: the Phantom Island world now exists and the "done when" condition is met. Two players can walk everywhere and see each other. Nothing is staged or committed.*

**Checks:** 26 tests pass, and `mypy` (strict) and `ruff` are clean. I also started the server briefly: the web client page, the pane plugin, the CSS and the three map pictures are all served. I haven't looked at it in a browser, so the two-window test is still yours to do.

**What you can do in the game now:**
- **Limbo is the title page**, showing the pitch. `begin` leads into the Society Office.
- **12 places with exits and short placeholder texts:** 3 in the port, the ship's Deck and Cabin, and 7 on the island. The island layout is a first sketch.
- **The ship:**
  - On the Quay, `aboard` takes you onto the Deck; `down` goes to the Cabin.
  - On the Deck, `sail` lists where she can go. The route is port → `sail west` → the charted position (empty sea) → `sail west` → anchored at the island → `ashore` to Lagoon Beach.
  - What you see on the Deck and in the Cabin changes with where she is, and so does where the `ashore`/`aboard` exits lead.
- **Map and Focus panes:**
  - The Map pane switches between the port plan, the *Halcyon*'s sea chart (with the ship's track drawn on it) and the island map. All three pictures are placeholders.
  - The Focus pane shows a placeholder card with the room's name.
  - For telnet, a new `map` command describes the same map in words.

**How it's put together:**
- All story content is in YAML in [world/content/](phantom_island/world/content/), with comments on how to edit it. A loader checks it, for example that every exit leads to a real place, and names the file and entry if something's wrong.
- `batchcode build` builds or rebuilds the world from those files. Rebuilding after an edit is safe: rooms are updated in place and nobody gets moved. On a brand-new database it builds by itself.
- Where the ship is and her track are kept in one `Expedition` script, as decision 7 asks. The journal and clues can go there later.
- [README.md](phantom_island/README.md) has a short guide to building, playing and how the files fit together.

**Your database:** I built the world into your existing `phantom_island/server/evennia.db3`, which only had Admin and Limbo. The original is saved at `phantom_island/server/snapshots/before-a1.db3` (git-ignored) if you want it back.

**Three choices I made that aren't in DECISIONS.md yet:**
1. The ship won't sail while another connected player is still ashore, so nobody gets stranded (decision 6b). Players still in Limbo don't count.
2. A player who joins while the ship is away has no way to reach her yet. An admin can `teleport` them; this needs a proper answer later.
3. Text placed in pictures should eventually be readable in text too: the chart shows the island as charted with a dashed outline, and the true island isn't drawn.

Should I add 1 and 2 to DECISIONS.md? Next stage is A2, the scripted inhabitants.

## Late Joiners Problem

*It's the geography that breaks.*

## Where the problem comes from

There's **one shared world** (decision 7), and the ship is a single thing in it. When the first kid sails to the island, the ship's position changes for everyone.

A brand-new character always starts in Limbo. `begin` takes them to the Society Office, in the port. If the ship is still in port, nothing goes wrong: they walk to the Quay and go `aboard`. But if the ship is at the island, the port's `aboard` exit is gone, because it only exists while the ship is moored there. The newcomer can walk around the Office, Quay and Market, and that's all. There's no other way to the island. Only the ship goes there, and only someone on her Deck can sail her.

The first kid could sail back to fetch them (`sail east` twice, then back), and that does work. But a 12-year-old has to think of it. It also means going back across the sea, which later costs time and water.

Players who are already in the game are fine. When someone logs out, Evennia remembers where they were and puts them back there on return. So the first kid can stop on the island and pick up there the next day. Only a **new** character has this problem.

## The story side

This part is closer to your picture. Once the journal exists (A3), it's shared, so the friend can type `journal` and read everything found so far. That's the "overall description of the situation", built into the game. And the first kid can explain the rest. Decision 11 already expects your grandson to act as guide.

The game itself has no problem with a player who missed Act 1. Gates like "learn from the trader before leaving port" are already open for the whole expedition. The friend never sees the empty sea or meets the trader, so he misses some moments, but the first kid can tell him about them.

## Ways to fix it

1. **Admin teleport** (what we have now). You type `teleport <friend> = Deck`. It works when you're there, but it's not in the story, and it fails if the kids play without you.
2. **`begin` leads to wherever the expedition is.** If the ship is in port, `begin` goes to the Society Office as now. If she's away, it goes straight onto the Deck, with a line such as "You've been aboard all along, seasick in your hammock. You come up on deck…". It's a few lines of code, and kids would probably enjoy it.
3. **`join <name>`** puts you next to a friend who's already playing. It's flexible, but more of a game-system feature than part of the story.
4. **Fetch them by ship.** No code needed, but it's slow and depends on the first kid thinking of it.

## A question to settle first: same expedition, or a fresh one?

Decision 11 imagines your grandson playing first with you, and his friend playing later with your grandson as guide. In that case the friend may simply get **a new run from the start**: you reset the world (back up or wipe the database, as in BUILD.md), and both start in Limbo. Then the late-join problem never comes up. Your grandson knows the answers, but that's what makes him a good guide.

The problem only matters if the friend should join the **same ongoing** expedition.

**My recommendation:** option 2. It's cheap, it fits the story, it works without you, and it doesn't stop you from also doing fresh runs. It fits best in A3 or A4, next to the journal, since the two together make a good "catch up" for a newcomer.

I've recorded option 2 as decision 18 in [DECISIONS.md](phantom_island/docs/DECISIONS.md#L56), replacing the temporary "admin teleport" entry:

- **While the ship is in port**, `begin` goes to the Society Office as it does now.
- **While she's away**, `begin` puts the new player on the Deck, with a short line from the story: they were aboard all along, seasick below.
- **Catching up** happens through the shared journal (A3), with the other player as guide.
- **Fresh runs** (a reset world) stay possible.

It gets built in A3 or A4, next to the journal. Until then you can bring a late joiner aboard yourself with `teleport`.

## A2 Completed

The A2 code is done. All 51 tests pass, and ruff and strict mypy are clean. I tested through `ask` and `execute_cmd`, but didn't start your server, so you'll be the first to see it in the web client. Everything is left uncommitted for you.

**What's new**
- **[content.py](phantom_island/world/content.py):** reads `characters.yaml` and checks it. It stops the build with a clear message if a character stands in an unknown place, a suggested topic doesn't exist, or one word means two topics for the same character.
- **Topic matching** ignores capitals, punctuation, "the" and "'s". So `The Storm?`, `great storm` and `storm of '75` all reach Barnaby's *storm*. If the exact text doesn't match, one word of it can, as long as it points to only one topic.
- **[inhabitants.py](phantom_island/typeclasses/inhabitants.py):** the six inhabitants are characters nobody plays. Rooms list them under "Characters:", and they can't be picked up or played. What they say stays in the YAML.
- **[builder.py](phantom_island/world/builder.py):** `batchcode build` now also places the inhabitants. A rebuild updates them in place and deletes characters that are no longer in the file. The Ship has no object: `ask` finds her on the Deck and in the Cabin.
- **[conversation.py](phantom_island/world/conversation.py) and [talk.py](phantom_island/commands/talk.py):** the `ask` command. It handles:
  - `ask barnaby`: greeting plus suggested topics.
  - `ask barnaby about storm`, or `ask barnaby storm`.
  - `ask about storm`, when only one person is in the room.
  - A fallback plus suggestions for unknown topics.
  - "The Ship can only hear you when you're aboard" if you ask her ashore.
- **Speech or narration:** a reply that starts with a quote is shown as `Old Barnaby says: "..."`. Any other reply is narration and is shown as written. This rule is now in the YAML header.
- **Everyone in the room hears the conversation:** this suits playing together.
- **Docs:** I added a "Playing stage A2" section and a file-table row to the [README](phantom_island/README.md), and a note in the YAML header on when a `reload` is enough and when you also need `batchcode build`.

**One choice I made without asking:** Tui stands in the Village (her first `where`), since moving between places comes in A4. As agreed, Crane and Ama always give their first replies for now.

**To try it**
1. `uv run evennia reload`, or `start` if the server isn't running. This is needed because there's new code.
2. Log in as admin and run `batchcode build`.
3. Then try:

```
ask fairweather
ask fairweather about letter
se                                  (Quay)
ask barnaby about the storm
ask about pirates                   → his fallback
ask ship about longitude            → "only aboard"
aboard
ask ship about longitude
teleport Village
ask about goats                     → "Who do you want to ask?"
ask tui about song
```

For two players, open a second browser at `http://127.0.0.1:4011`. The second player hears what the first one asks.

## A3 Completed

A3 is built. All 84 tests pass (51 old ones and 33 new), and ruff and strict mypy are clean. I tested it only through tests, not in a running server, so you'll be the first to see it in the web client. Nothing is staged or committed.

**What's new**
- **The clue table:** [clues.yaml](phantom_island/world/content/clues.yaml) holds C1–C13, each with a title and its journal line. The content check stops the build if a text with a `clue` has no `[[marked]]` part, if a marked part has no clue, or if a clue, thing or flag doesn't exist. One test checks that every clue can be found somewhere.
- **Yellow and the journal:** marked text shows in yellow. A white topic word inside a clue, like *fishermen*, goes back to yellow after it. A "New in the journal:" line follows straight away. Players elsewhere hear who found it and where, and finding a clue a second time just says "Already in the journal". The journal is kept in the `Expedition` script, together with the flags. `help colours` explains the two colours.
- **Things** ([things.yaml](phantom_island/world/content/things.yaml)):
  - The compass stays on Crane's stall.
  - The sextant, chronometer, chart and two guide books are in the Cabin.
  - Carried books and the chart show more of what you look at.
  - Carried things go back to their place when their carrier leaves the game.
- **Details** in `places.yaml` and `ship.yaml`: the beams, goats, bones, shoots, coastline and so on. The empty sea (C4) is found when the ship arrives, and the birds (C6) with `look sky`.
- **Commands:**
  - `look`, now also for details and things, and `examine` or `x` for a closer look. Looking is private.
  - `read` and `use`, heard by the whole room.
  - `journal`.
- **Longitude (C5):** `use sextant` on the Deck sets a flag for the whole expedition, then `read chronometer` in the Cabin gives the clue. One player can do each step. It works at the charted position and, more clearly, at the island ("10 degrees further west").
- **Hidden truths:** Crane admits the truth (C3) once C2 is in the journal. Ama still waits for `respect`, which comes in A4.
- **Late joiners (decision 18):** while the ship is away, `begin` leads to the Deck with the "seasick below" line.
- **Docs:** I added a "Playing stage A3" section with a walkthrough to the [README](phantom_island/README.md). In [DECISIONS.md](phantom_island/docs/DECISIONS.md), decision 18 is marked built and there's a new decision 21 for the choices you approved.

**Two choices I made that you should check**
1. **I widened decision 20.** White now also marks words worth *looking at* (`look beams`) and commands to try, not only topics to ask about. Otherwise players would have to guess the details of a room. I've updated decision 20's text; say if you'd rather keep white for topics only.
2. **`examine` is now ours for everyone, admins included.** Evennia's builder command still works as `@examine` or `ex`.

In A3 nothing waits for time yet: the Reef is always open, the birds are always there, and noon is whenever you use the sextant. The tide, dusk and noon come in A4.

**To try it:** run `uv run evennia reload`, since there's new code, then `batchcode build` as admin to place the things. The README walkthrough goes from `look compass` through `read chronometer`.
### A New Principle Realized - Three Layers

**1. During play: facts, not conclusions, always on request.** For every clue there should be background knowledge somewhere in the world that makes it solid:
- how far seabirds fly from land;
- why oak doesn't grow on a tropical island;
- why goats and onions point to Europeans;
- four minutes of time per degree.

This knowledge lives with the Ship or in the books, and players who want to dig can ask. The connection itself, "so land is within a day's sail", stays the player's to make.

To make this systematic rather than accidental, each clue in clues.yaml could list the topics or books that hold its background, and the content check would fail if one is missing. That turns "every clue is backed by real knowledge" into a rule the build enforces, like the yellow-mark rule.

**2. Optional reflection: questions, not answers.** A quiet place to think, such as the chart table in the Cabin with a `think` command, or a note under the journal. Once two related clues are both found, it offers a question that links them, for example: "The birds fly home at dusk. How far can a tern fly in a day? Perhaps the Ship knows." Players who don't care never see it. Players who do get pointed to the right question without being given the answer.

It's a strong hint, the same concern as grouping the journal (decision 21). So it belongs in A5, after a playtest shows whether the kids need it.

**3. After the report: "How it all fits."** This is the right place for the full analysis we did today, because there's nothing left to spoil. The epilogue would cover:
- the chain from each clue to each answer;
- the numbers: 14° S, 40° and 42° W, 160 and 168 minutes, a day's sail, how far the birds fly;
- the real history: Harrison's chronometer, Sandy Island removed from maps in 2012, La Pérouse.

The kids would leave with the feeling you describe: what seemed random was solid all along. It fits A4, which already includes the report and the epilogue, plus the sources list from decision 9.
