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
4. **Each role sees different things.** One room description changes with the role, which Evennia can do when it builds a room's text. For example, the navigator notices the stars and the coastline, and the naturalist notices the plants and the tracks.
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

- **Keep it playable at every stage.** Each stage ends with something two people can play from start to finish, even if it's crude. Never finish a stage with only a part that can't be played yet.
- **Plain placeholders first** (game designers call this "greyboxing"). Rooms and characters with plain placeholder text come first, polished writing and pictures later. You find out whether the structure works before spending effort on decoration.
- **The core loop.** This is what players do minute to minute: move → look → notice something → ask someone → note it in the journal → think → move on. If this loop is fun with dull text, it will be great with good text. If it isn't fun, AI won't save it.
- **Playtests: watch, don't help.** Let the kids play while you watch silently. Note where they get stuck, bored or excited, then ask them afterwards. This is the main tool of game design, and kids are very honest testers.
- **Three ways to every conclusion.** Mystery writers use a rule of thumb: players miss clues, so every conclusion they need should be reachable by about three clues. A mystery with one path gets stuck. My proposal has about two paths per answer, and playtests will show whether that's enough.

One more trick suits your situation well: **you play the character yourself**. Evennia lets an admin take control of any character with the `ic` command. During a playtest you can *be* Tui or Elder Ama and answer the kids live as a human. Game designers call this a "Wizard of Oz" test. It's the best preview of AI characters you can get. The transcripts also give you exactly what stage 4 needs: real questions kids ask, and examples of good answers to test the AI characters against in llm_lab.

## Revised stages

Times are in **working sessions** (about 2–3 hours with me). They're rough and could easily be off by 1.5–2×.

### Phase A: The complete game without AI (this is what gets "customer approval")

| Stage | What gets built | Done when | Time |
|---|---|---|---|
| **A1. Island skeleton** | 12 rooms with exits, short placeholder texts, the map pane, the ship and the sea room | Two players can walk everywhere and see each other | 2–3 |
| **A2. Scripted inhabitants** | 7 characters, `ask <char> about <topic>` with scripted replies, characters placed in rooms | Every character answers its topics; unknown topics get a polite in-character reply | 2–3 |
| **A3. Discovery and shared journal** | Clue table as data, role-based descriptions (navigator/naturalist), the `journal` command | A clue found by one player appears in both players' journals | 2–3 |
| **A4. The mystery and the ending** | Gates (leaving port, meeting Jonah), tide and evening scripts, the `report` command, the epilogue | The adventure can be played from start to finish and reach every ending | 3–4 |
| **A5. Polish for the kids** | Better texts, a few pictures, a `help`/hint path through the Ship | You'd be happy to show it | 2–3 |
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
