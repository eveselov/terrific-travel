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
| **A4. The mystery and the ending** | In this order (2026-11-16, after a playtest of Act 3: the story could be found, but nothing let a player say they had found it): (1) the `report`, one question at a time and open at any moment, each answered question marked under the task in the journal, and the epilogue once all three are answered; (2) connection questions: once two related clues are found, a question that links them, never the answer (DECISIONS.md, 22); (3) hints: next steps at three levels when asked for, then pushed in the story's voice to a player who goes long without progress or reads too fast (whose voice ashore is for the kids to decide); (4) gates (leaving port, meeting Jonah), each with at least two ways through and a hint path; tide, dusk and noon scripts; Ama's respect | The adventure can be played from start to finish, alone or together, and reach every ending; a player who wanders is led back towards the task | 4–5 |
| **A5. Polish for the kids** | Better texts, a few pictures, the journal grouped under the report's questions (if the playtest asks for it) | You'd be happy to show it | 2–3 |
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

## Richness: plot, not prose

*2026-11-13.* Playing the Port, the replies started to feel like a novel: the more detail,
the more enjoyable to sit and discuss, but a 12-year-old hurrying to the end doesn't want
long texts. Two questions came out of it: how long should replies be, and what kind of
richness does a game need?

### Depth in layers, not long replies

Every reply stays short, and the depth sits one question further down, behind the white
words. A player in a hurry reads two or three sentences and gets the gist, one vivid detail
and a next step. Players who want more (a grandparent and grandson sitting together) follow
every white word and get the whole story, piece by piece. It's decision 22 (facts on
request) applied to storytelling, and it's what an AI character will do naturally in phase
C: brief by default, deeper when asked.

### Two kinds of richness

Richness can come from the **plot** (how many people, things and relationships there are,
the twists) or from the **prose** (descriptions, metaphors). Authors differ; games prefer
the first, for three reasons:

- **Players act on what they read.** Every noun in a text is a silent promise: you can look
  at this, ask about it, use it. Decoration makes promises the game can't keep (`ask masts`
  on the Deck, expecting the chart in the Office). A child who tries three false leads stops
  trying. Plot richness is the opposite: everything in it can be acted on.
- **A mystery works like Chekhov's gun.** Every detail is evidence, a red herring or
  atmosphere, and readers assume it's evidence. "Everything fits together" makes that
  promise explicit; ornament for its own sake would break it.
- **Prose still has two jobs, and both serve the plot.** *Details that do double duty*, vivid
  and evidence at once ("an old iron nail, bent flat"; "built of good oak", which prepares
  C8; "seas like hills"). And *voice*, which is characterisation: Crane's salesman evasions
  signal a liar, Barnaby's sayings mark the old sailor who is sure and wrong, and Tui's
  "canoe with a white wing" is a clue disguised as a child's poetry. Metaphor belongs in a
  character's mouth when it shows who they are, not in the narration.

One caution about plot richness: for a 30–60-minute session with kids, more elements isn't
better (13 clues and 7 characters is about the limit). Richness should come from **more
connections between the elements we have**: Barnaby and Crane disagree about the compass;
Fairweather's "good oak" matters in the Village; Crane's "last winter's storm" clashes
with Barnaby's storm of '75. Each cross-reference makes the world feel solid without adding
anything to keep track of.

### The rules

Recorded as decision 23, with the rules at the top of `characters.yaml` and a written
`voice` for each character:

- replies of about 30–60 words, the answer first;
- one concrete detail that is vivid *and* a fact that fits; a detail that is only pretty is
  cut;
- most replies end with a white word leading somewhere new;
- the subject is named at its first mention in each reply;
- figurative language only in a character's voice; narration stays plain;
- prefer a connection to another person, thing or clue over a new detail;
- every fact is in "The truth" or in the table of facts that depend on each other.

The first pass applied them to Mrs. Fairweather and Old Barnaby. Her *halcyon* reply got
shorter (the flags and white sails went, the oak stayed) and gained a new topic, the *crew*
and their families waiting for news. His *halcyon* reply gained a connection rather than
adjectives: he watched her sail, and is sure Crane's compass "came off the bottom".

## Think: Connections

Connection questions: Think feature added

The connection questions are built. The targeted tests (56) pass, and ruff and mypy are clean. The full suite is running now, and I'll report when it finishes.

How it plays:

Once all the clues a question needs are in the journal, the question appears right after the journal line, once, for everyone in the room. For example:


New in the journal: A hut in the village is built with oak beams. ...

Something to think about (think): The ribs on the reef and the beams in the village are both oak, from the Halcyon. What else could her timber have been used for? Look for a place where something was built.
think (or wonder, questions) lists every open question, anywhere.

The journal's footer points to think once there is a question to show.

Where they live: think works anywhere, instead of the chart table that decision 22 first suggested, for the same reason the task is in the journal: on the island there's nobody to ask. This is recorded as decision 30. The questions are worked out from the journal each time, so there's no new state.

The seven questions, in connections at the end of clues.yaml:

| Clues | Question leads to |

|---|---|

| C2 + C3 | where in the sea a compass could lie for years (the reef) |

| C4 + C6 | how far seabirds fish from land (ask ship about birds) |

| C4 + C5 | why one number of the chart was right and the other wrong (report question 2) |

| C7 + (C12 or C13) | which witness was there: Barnaby or the island (ask ship about witnesses) |

| C7 + C8 | what else the oak was used for (the boat at the cove) |

| C8 + C9 | how long the crew stayed, and where they went |

| C11 + C8 | what boat has a white wing, which way is sunset, what it was built of |

Several clue journal lines already state the first conclusion (C8 says "ship timber", C10 "charted in the wrong place"), so each question goes one step further, towards a report question.

For you to check:

Some questions lean towards the answer. The staying and white wing ones are fairly leading. Decision 22 had them as optional reflection, "a strong hint". If they feel too strong once you play them, they're easy to soften in the YAML.

I left out C3 + C4. "The compass came from the west, the chart's position is empty: which way would you search?" would have taken over the central choice of Act 2, which belongs to the players (decision 24). The hints step can push there later, if players get stuck.

The docs are updated: decision 30, GAME_AUTHORING (the files table and the clue recipe), GAME_GUIDE and the README.

## Hints

The hints are built. The targeted tests pass (64), and ruff and mypy are clean. The full suite is running, because the clock for pushed hints now runs after every command in the game. I'll report when it's done.

**How it plays:**
- **Three levels:** `hint` (or `stuck`) gives a nudge, `hint` again is more direct, and a third time gives the exact command. When the expedition finds a new clue or answers a report question, the hints start gently again.
- **Who speaks:**
  - Aboard: *The Ship creaks: "Watch the seabirds at dusk from the Deck, and remember where Crane's fishermen came from."*
  - Anywhere else: *You leaf through the journal, and think. Ask Tui in the Village about the song.*
- **Pushed hints:** after 10 minutes of play without progress, the player's next command is followed by the first level, with "(Stuck? hint tells you more.)". This happens once per stretch without progress. A pause between commands counts at most one minute, so coffee breaks don't trigger it. Nothing is pushed in Limbo or during a voyage.
- **Next step:** the next step is worked out from the state of play, using 19 situations in [hints.yaml](phantom_island/world/content/hints.yaml), checked from the top:
  - **Port:** compass, coral, Crane, sailing out.
  - **Sea:** check the reckoning, which way to go, back from a wrong direction.
  - **Island:** go ashore, the song, the beams, the reef, Jonah, the island's position.
  - **Report:** the three questions, then a final "complete".
- **The Ship's *help* topic** now points to `hint` as well.

**For you to check:**
1. **Report hints never give the letter.** The third level says `report 2` and to "pick the answer the journal proves". It doesn't say which choice, because the report tests understanding.
2. **"Which way" points the way at level 3.** The third level at the empty sea says "look sky, then sail the way the birds fly". That's as far as I'd go without saying "west", since the choice is the players' (decision 24). After a wrong direction, the hint leads back to the chart's position.
3. **Island order.** The island steps follow one path: song, beams, reef, Jonah, position. Players exploring in another order just skip the ones they've done, because a situation stops matching once its clue is found.
4. **Hints change as A4 goes on.** When the gates, the tide and Ama's respect come, each gets its own situation. The authoring guide now says to add one for every new gate.

The docs are updated: decision 31 (including why not a talking Island), the GAME_AUTHORING recipe, a Hints section in GAME_GUIDE, and the README.

### How `hint` picks its hint

There's no reasoning involved: `hint` follows a fixed list. [hints.yaml](phantom_island/world/content/hints.yaml) has 19 situations in the order I wrote them. Each situation has conditions on the **expedition's state**, and `hint` takes the **first situation whose conditions all hold**. The conditions are:
- where the ship is;
- clues or flags that must be found, or still be `missing`;
- report questions still open.

It then shows that situation's next level of text. So on the island, the order is song, beams, reef, Jonah, position, then the report. Whatever is first and still unsolved gets suggested.

**What counts as context:**
- **It uses:** the shared state of the expedition (the ship, the journal, the flags, the report).
- **It doesn't use:** where *you* stand, what you just did, or what you're working on.

Your location only picks the voice (the Ship aboard, the journal ashore). Each player has their own hint level, but the situation is the same for everyone.

**This matters with parallel paths.** Say you're on the Hilltop with the chart in hand, about to compare the coastline. `hint` still says "the village children remember things… ask Tui", because the song comes first in the list and isn't found yet. Two players who split up get the same hint. For Phantom Island, with one main path and short parallel branches, that's tolerable. For a bigger game it would feel deaf.

**Ways to make it fit the context, cheapest first:**
1. **Prefer what's nearby.** Give situations an optional `place`. `hint` first looks for a matching situation at the player's location, and falls back to the list order otherwise. On the Hilltop you'd get the coastline hint.
2. **Let the player choose.** `hint` alone lists what's still open ("the song, the wreck, the island's position"), and `hint wreck` gives that one's next level. This is how classic adventure hints worked (InvisiClues were organised by question), and it handles any number of parallel goals. It also respects the player's own plan.
3. **Goals with prerequisites** instead of a list: a small graph of what's available now, picking the one nearest to the player or the one they touched last. This is the most general and the most work. I'd only build it for a second, bigger episode.

I'd do 1 now, since it's a small change and fixes the Hilltop case, and keep 2 in mind if playtests show players juggling several goals.

### How `hint` and `think` are related

They're independent mechanisms that answer different questions:

| | `think` | `hint` |
|---|---|---|
| Answers | *why?* How do these facts fit together? | *what next?* Where to go, what to do |
| Comes from | pairs of clues found (connections in clues.yaml) | the first matching situation (hints.yaml) |
| Shown | automatically when a question opens, then listed by `think` | on request, or pushed after 10 minutes without progress |
| Levels | none, and never an answer | three, the last one the exact command |
| Same for everyone? | yes, from the shared journal | the situation yes, the level is per player |

Neither looks at the other. They also overlap a little: a few connection questions also say what to do ("Look for a place where something was built"), which is really a hint's job.

They could work together in two ways:
- **When the next step is understanding, not finding:** for example before the report, the hint's first level could point to an open `think` question.
- **Trimming the overlap:** connection questions could drop their "go and do" parts, keeping each tool to its own job.

Should I make the "prefer what's nearby" change, and trim the connection questions to pure *why* questions?

## Schema

I think the core of your formulation is right. The schema is a good frame for content that teaches through a task. Two parts are optimistic: the novelty, and the claim about evaluation. Both deserve a closer look before you build a series on them.

### What's strong

- **Each piece has one job, and together they cover the learning loop:**
  - the task says *why* we're here;
  - the journal holds *what* was found;
  - the notebook holds *how the world works*;
  - `think` asks *how it fits*;
  - `hint` answers *what next*;
  - the report shows *that it's understood*.

  Learning research calls this inquiry-based learning with scaffolding. You've arrived at a coherent version of it from the game side.
- **The proof rule is the most valuable idea.** An answer counts only when the journal backs it. It turns "guess the answer" into "show your evidence", which is the historian's and the scientist's habit, and it's what makes the report more than a quiz.
- **Everything is data, with a checker.** I'd argue this matters more for a series than any single feature. The schema's real bottleneck is the cost of writing good content, and a checker that enforces the rules is what keeps that cost down: every clue backed by background, no dead ends, every hint situation reachable. The next step would be a tool that *plays through* the content files automatically and proves every ending can be reached. That's possible precisely because everything is data.

### Where I'd temper it

**1. Novelty.** The concept has close relatives in educational research:
- *River City* (Chris Dede's group at Harvard, 2000s): a multi-user virtual environment, close to a graphical MUD. Students investigate why the people of a 19th-century town fall ill, and gather evidence.
- *Crystal Island* (James Lester's group at NC State): a science mystery for middle school, with a notebook, characters to question and a final diagnosis to prove.
- On the evaluation side, **evidence-centered design** (Mislevy) and **stealth assessment** (Shute) formalise "claims backed by evidence". That is your report's proof structure, seen from the testing side.

So the idea isn't new. What could be distinctive is the *form*: lightweight, text-first, multiplayer, authored in plain YAML with a checker, playable by one child or a family together, and ready for AI characters while the game keeps control of what is revealed. That's a real and practical niche. I'd claim that, not the concept itself.

**2. Evaluation is the weakest part today.**
- **The report measures persistence more than understanding.** With hints at three levels and the proof gate, almost anyone gets there in the end.
- **Real evaluation needs evidence of *how* they got there:** hints used, wrong choices tried, connections opened, notebook ideas *used* versus only *heard*, which clues were found before which answers.
- **That clashes with decision 8 (no conversation logging).** The tension can be solved: counts and choices aren't conversations. But it has to be designed on purpose, not assumed.

**3. Over-scaffolding.** `hint` and `think` together can end up doing the thinking for the player. The schema doesn't prevent that; the content and playtests do. That's your own point that it "might not work automatically by itself", and I'd make it explicit.

**4. Domain fit.** The schema suits subjects you can *investigate*: history, geography, natural science, detective reasoning. It suits drill and procedural skills (arithmetic, grammar) much less. Saying so makes the claim stronger.

**5. Small corrections to your formulation:**
- What keeps players focused is the task at the top of the journal. The report is the check against it. Calling `report` early helps only because a wrong or unproved answer tells you what's missing.
- The notebook isn't free-form: it's structured by area and level. Its freedom is that it isn't tied to the tasks.
- `think` doesn't make the connections; it asks the question, and the player connects.

### A tightened formulation

> A frame for inquiry-based games built on structured content. A **task** keeps players focused; a shared **journal** collects the evidence; a personal **notebook** grows the background knowledge, by area and level; **connection questions** prompt reasoning without giving answers; **hints** at three levels end fruitless wandering without prescribing a path; and a **report** accepts only conclusions the evidence proves. All content is data, checked for consistency, so authors can write new episodes and domains without code. It supports fun, learning and, with deliberate design, evaluation; it doesn't produce them by itself: the content does, within the frame.

### What generalising would take

When the second episode exists:
- an explicit model linking tasks, claims, evidence and ideas (today it's implicit, spread across `proof`, `needs`, `teaches` and `connections`);
- hints that understand parallel goals;
- an automatic play-through checker;
- an evaluation design that respects the privacy decision.

None of this needs doing before Phantom Island is finished. It's worth writing the schema down now, while the reasons are fresh.

Should I put the tightened formulation and these notes into a short design document, for example `docs/SCHEMA.md`, kept separate from Phantom Island's own docs as your earlier note about general guides suggested?

## Report as Case Board

The report now works as a case board, and it shows only what the players could know. The targeted tests pass (71), and ruff and mypy are clean. The full suite is running in the background, and I'll report when it finishes.

**What players see now.** `report` alone, at the start:
```
The report for the Society: the task's questions, and what might be
1. What happened to the Halcyon, and where?
   a) She sank far out at sea in the great storm of '75, with all hands.
   b) She reached the island, then sailed on and was lost somewhere else.
   (More possibilities may come up as the expedition finds out more.)
2. Why did nobody ever find the Halcyon?
   a) Because she sank in deep water, and the sea keeps what it takes.
   b) Nobody searched long enough. The island is where the chart says it is.
   (More possibilities ...)
3. What became of the Halcyon's crew?
   a) They all drowned when she went down.
   (More possibilities ...)
Answer a question with the letter of the possibility you can prove, like report 1 a. ...
```

**How possibilities open.** A test checks that the starting board mentions no reef, no longitude, no west and no boat. When a clue opens a possibility, the room hears "New for the report: another possibility for question 1 (report 1)", but not what it is.
- **Question 1:** the coral (or the wreck, or Jonah) adds "she sank in the deep ocean" (wrong: coral grows only in shallow water) and "wrecked on a reef near the island" (right).
- **Question 2:** the empty sea adds "latitude wrong", "longitude wrong" and "the island moves". The right one is now a claim: "the chart's longitude was wrong: it put the island too far east or west". The *no sea clock* explanation moved to the accepted reply and the epilogue.
- **Question 3:** the oak beams, the song, Ama or Jonah add three survival stories: west with one staying (right), home to the east, or all staying.

**The rule, enforced.** The content check fails if a question's right possibility doesn't share its exact `opens` with a wrong one. So a new possibility never gives itself away by appearing. Letters count only the possibilities shown, in file order, with the starting ones first, so their letters never change.

**Replies.** I rewrote the replies of the possibilities shown from the start, because three of them mentioned things players can't know yet: "somebody on the island remembers", "at the chart's position there was no island", "a piece of her in the shallows".

**Docs:** decision 32 (it amends decision 29's "the choices are always the same"), GAME_SCHEMA (a section "The report is the centre, not the end" and design rule 11), and the GAME_AUTHORING recipe, GAME_GUIDE and the README walkthrough.

## Council

I think you've found something real, and it's more than a metaphor.

## What you noticed

The game has two kinds of play, and until now we've built only one of them:
- **Exploring:** wander, meet people, look and examine, in any order. Nothing has to come out of it right away, so a short attention span is fine. Every find is a small reward.
- **Converging:** many findings have to become one decision. This is where the chart's position sits, and where the report sits at the end.

For converging, the game currently offers the same tools as for exploring: read the journal, `think`, `hint`. Those are tools for thinking alone. They expect the "eureka" to happen silently in one head, all at once, and you've shown it doesn't, even for you. My decision 34 improves the material (three clear questions), but it is still silent reading. It doesn't give the moment a **process**.

Your picture of the captain calling the crew together is the right model. A council is a way of thinking in steps, out loud, with someone keeping order. It suits a 12-year-old much better than a pile of notes: one question at a time, each answered before the next, and the conclusion builds up step by step. It also suits the sofa. The council structures the conversation between you and your grandson, which is the best discussion the game can have.

## What a council could look like

The captain calls it: `council`, on the Deck. The Ship leads the questions, which fits her written voice: she "asks questions back instead of giving answers". The captain answers. Each step is one of the three parts from the table:

```
> council
The crew gather on the Deck. The Ship's timbers creak: "Open sea, Captain, where the
chart put the island. So the chart is wrong somewhere. Let's settle it, one thing at
a time.
First: the chart gives two numbers. Which one could the Halcyon's master have got
wrong without knowing it?"
  a) The latitude, north or south.
  b) The longitude, east or west.
  c) Both of them.
(Answer: council a, b or c.)

> council a
"The noon sun gave him his latitude every day, and our sextant says the same as his
chart. What did he have no way to check?"

> council b
"Yes. Without a sea clock, longitude is only a reckoning. So the island lies on our
own latitude: east of us or west.
Second: east or west? What does the journal say about that?"
  a) East.
  b) West.
  c) There's no way to tell.

> council c
"Is there not? Something here knows where land is. Watch the sky at dusk, Captain,
and call us again."
(The council waits. council carries on where it stopped.)
```

At the end, the Ship sums up: "So: west along our latitude, and not far: the terns say land is within a day. Your order, Captain." The player still types `sail west` (or, with option (b) from my last message, `sail to 14 south 41 west`). The council builds the decision; the captain makes it.

## The rules I'd give it

- **Only the journal counts.** As in the report, an answer is accepted only once the journal holds its evidence. If something is missing, the Ship says where to look, and the council waits there. It doesn't hand out the clue. This keeps exploring meaningful: the council can't skip it.
- **A wrong answer leads back to the evidence, never to failure.** This is the same rule as the report (29).
- **It's offered, never forced.** The Ship suggests a council when the ship arrives, and a pushed hint can suggest it too. A player who already knows can simply `sail west`. That protects replays and keeps the no-dead-ends rule (6b).
- **Playing together, everyone aboard is at the council,** and any captain may answer. Arguing it out in the room is exactly the point.

## How it fits what we have

**The council is the report's machinery, used mid-game.**
- A step is a question with theories, and a right answer that needs its evidence. That's what a report question already is.
- What's new: the steps come in order, they belong to one place and moment, and finishing sums up and leads to an action.
- So it costs less than it sounds: most of `world/report.py` carries over, and the content format is almost the same.

**It gives the schema a new element.**
- The game becomes **exploration phases that end in convergence points**, and each convergence point has a council.
- The final report is simply the last and biggest council.
- That belongs in GAME_SCHEMA.md. It's general: every episode will have its "where now?" moments.
- Other mystery games have similar devices: deduction boards, fill-in-the-blank conclusions, and confirming several answers together. But in those the player works alone. Making it a council the captain leads, with the crew in the story, is ours. That claim needs a proper prior-art check before we write it down.

**It also changes decision 34:**
- The Ship's framing on arrival becomes her offer of a council.
- The three `think` questions become the council's three steps. `think` stays for open-ended links, such as the compass and the reef.
- The hints point to the council first, then down the same ladder to the command.
- The coordinate answer from my last message stays.

## Decisions for you

1. **Voices:** the Ship alone, or a few crew voices too (the lookout on the horizon, a hand who watched the birds)? Crew voices make it feel like a real council, but they mean new speakers. Decision 23 warns against adding elements for decoration. I'd start with the Ship alone, plus a line or two of background crew ("The lookout nods.").
2. **Answers:** pick a letter only, or also name the journal entry that shows it, like presenting evidence? Naming evidence is a stronger detective lesson, but harder for a 12-year-old. I'd start with letters only and see how it plays.
3. **Scope:** build the council now as the way decision 34 is done, with this one council at the chart's position, and add it to the schema as a general element? That's my recommendation.

If you agree, I'll write this up as a new decision (it replaces most of 34) before building anything.

# A4 Half Way

**Status: A4 is about halfway.** The playtest fixes (item 0) are all built. Items 1–4 haven't been started, and each still needs design before building. Your playtest also only reached the island, so the second half of the game hasn't been played since the recent changes.

**What I'd do to finish A4, in this order:**

1. **Play the second half** (island → Jonah → report), with the new texts, the council and `think`, before designing anything new. The second half has the gates, the tide and Ama's respect. It's better to find out how it plays now than to design for it on paper.

2. **Settle two small loose ends** while playing:
   - **The compass's coral** (open question): how the compass lay in the sea for years if the crew gave it away straight after the rescue. It's a story decision, maybe one for the kids. Jonah's *compass* reply and GAME_STORY change with it.
   - **The *birds_range* question in `think`**: decision 34 says the council's "how far" step replaces it. Keep it or drop it.

3. **Gates (item 1).** Each needs a second way through and a hint situation:
   - **Leaving port:** today the ship can sail before Crane confesses (C3). It's a design choice whether to enforce this gate at all, now that the council accepts the birds (C6) as proof for west.
   - **Meeting Jonah:** after the wreck and Ama's account (C7 + C12). This also needs "Jonah's hours": where he is when he isn't at the cove.

4. **Ama's respect (item 3).** The `respect` flag is currently unreachable, so C12 can't be found through Ama. That makes it the most urgent gap in A4: as built, the Jonah gate (C7 + C12) could never open. It needs two ways: asking her about the reef first, plus one more for players who went to the reef first.

5. **Time (item 2): the tide, dusk and noon.** This is the biggest item, and it needs a design session first:
   - how long a game day is in real time;
   - what time it is when the ship arrives;
   - whether there's a `wait` command.

   Then the reef only at low tide, the birds only at dusk, the noon sight only at noon, and Tui moving with the tide. Each timed gate needs a hint situation, and waiting must stay short in a 30–60 minute session. My view: keep it simple, with a few fixed times of day and `wait` to jump to the next one. That would be enough for A4.

6. **Build or drop (item 4):**
   - **Counting the water (26):** I'd drop it, or keep it as flavour only. A countdown adds pressure that a 12-year-old's first game doesn't need.
   - **`show <thing> to <character>` (19):** I'd build it if the gates need it. For example, showing Crane the compass's coral is a natural second way to his confession.

7. **Decide the three waiting proposals:**
   - hints prefer what's near the player;
   - connection questions ask only "why";
   - a neutral first reply to an unproved right theory.

   They're all small. The first two are worth doing, and the third can wait for a playtest.

8. **A full end-to-end scenario** (`record`, from start to report) as the A4 acceptance test. Then a final playtest with the kids.

**My overall view:** the cheapest next step is item 1 on this list (play the second half), and the most urgent build is Ama's respect (item 4). Time is the one big design question left in A4. It's worth a separate discussion before any code.