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

## Idea 9. Lack of Sense of Progress

### Overall: yes, it's heading the right way

Several of your notes show the design working:

- **Sailing** (1, 3, 5): the chart was easy to find, the order was clear, the Ship helped you get home, and sailing west on to the island worked. That's how it's meant to feel: you can't get stuck, and the way forward is never spelled out.
- **The characters** (7, 8): the talk with Ama went well, and Pike gave you a clue. That's the core of the game, and it held up even when you wandered around without a plan.
- **Unplanned wandering still reached the island.** That's the "no dead ends" rule (decision 6b) doing its job.

### The real problem: you didn't know what you were looking for

Your sense of losing purpose is the most important finding, and you weren't playing it wrong. It's a gap in what's built so far:

- **The goal exists only in the design documents.** The game is built around the Society's three questions:
  1. Where did the *Halcyon* wreck?
  2. Why was she never found?
  3. What became of the crew?

  But the `report` that asks them is in stage A4, which isn't built yet. In the game, Fairweather only says *"see what is left to find."*
- **Your own memory proves it.** You remembered the goal as "save the crew". In the story, the crew were rescued by the islanders long ago, and the task is to find out the truth. If you mixed it up after designing the game, a 12-year-old will too.
- **Notes 4 and 6 are the same problem.** You found "coral" and had no idea what to think, because a clue only means something next to a question. "Coral grown into the brass" answers *where did she wreck?*, but only if you're holding that question. The game gives players facts and leaves the connections to them (decision 22). That only works if the questions are in view all the time.
- **Note 2 is a smaller form of it.** Without the port conversations, the empty sea at the chart's position is just empty sea. With the second question in mind ("why was she never found?"), empty sea at the charted position is a discovery.

**My recommendation:** put the three questions into the game now, before the rest of A4:

- Fairweather gives them explicitly, as the Society's three questions.
- The journal always shows them at the top.
- A `goal` (or `task`) command repeats them.
- The Ship reminds you of them when you first reach the island.

This doesn't group clues under questions, which decision 21 held back as too strong a hint. It just keeps the goal in sight.

### Points and competition

I agree with the motivation idea, but I'd change its form.

**Arguments for points:** kids love counting, and seeing progress is a strong motivator.

**Arguments against a head-to-head score:**
- The game is designed to be cooperative: one shared journal, no exclusive roles.
- Your goal is connection between you and the kids. A scoreboard between grandson and friend, or between you and a child, can work against that, especially since the grandson will know the answers on his second playthrough.
- Points for collecting reward grabbing over thinking. The real achievement is the report, where clues get connected.

**What I'd suggest instead:**
- **A team progress counter**, such as *"Clues found: 4 of 13."* For an aimless player, the biggest motivator is "there's more to find, and I'm getting somewhere." It also hints quietly that you haven't seen everything yet.
- **Personal credit, without ranking.** The journal already records who found each clue. A short tally ("Eugene 3, Sam 2") shows each player's contribution without making it a contest.
- **Possibly ranks or titles**: the expedition earns a title as clues come in (Landlubbers → Navigators → Explorers). Or each player does, for a bit of friendly rivalry inside the team.
- **The best reward for understanding** is the report's epilogue and the "How it all fits" explanation at the end, which rewards connecting the clues, not just collecting them.

You could try a counter with the kids and see whether they ask for more competition. Adding a scoreboard later is easy; taking one away after it changes how they play is harder.

### How much weight your impressions carry

They count for a lot. Playing as a boy who doesn't think systematically was the right test. One caveat: on the first playthrough your grandson will have you beside him, and you'll keep the purpose in mind for him. The friend may play without that help, so the game has to hold the purpose on its own.

If you agree, the next step could be a short decision entry covering "the three questions in play from the start" and "team progress, personal credit". Then I'd build those before the rest of A4.

## Idea 10. Suggsetion for Journal

**Q:** *I don't know whether you planned it or not, but my own unexpected perception of "journal" feature is that it works like a very useful tool - like a growing representation of a task to solve. All collected clues represent the full porblem definition leaving to the playe only conclusion to make. Technically the journal does not look like that, but produces such perception. Maybe we should tune it a little bit toward that, and maybe it will help addressing my sense of lacking a purpose (I know, that A4 is supposed to improve that though). I want you to tell me what do you think, without making changes, since my idea here is very vague.*

### Was it planned?

Only partly. The journal was designed for three jobs:
- a shared record of what's been found;
- a way for late joiners to catch up;
- a place to compare sources (who said what).

Seeing it as a growing statement of the problem wasn't written down anywhere. Still, it follows from two decisions:
- The journal holds only true facts (decision 20).
- The game gives players facts and leaves the conclusions to them (decision 22).

So the journal is, in effect, the case file. You noticed something the design produced without naming it, and I think it's worth building on.

### Why it works, and what to protect

It feels like a problem definition because every entry is a true fact, and connecting them is left to you. That gap is the fun part, so whatever we change should keep it. If the journal sorted facts under answers, the remaining puzzle would become trivial. That's why decision 21 held back grouping entries under the report's questions.

### Ways to tune it, mildest first

1. **The questions at the top.** Show the Society's three questions as the journal's heading, with the facts below in the order found:
   > **The Society asks:** Where did the *Halcyon* wreck? · Why was she never found? · What became of the crew?
   > **Found so far (5):** 1. … 2. …

   The journal then says outright what you sensed: "here is the problem, here is what you know." It also fixes the lack of purpose in the place players already look, without a separate `goal` command. The connections stay yours, since the entries aren't sorted under the questions.
2. **A progress count.** Something like "5 of 13 found" in the heading tells you there's more to find without saying what. It's also the team progress counter from our points discussion, now in a natural home.
3. **Your own notes.** A `note <text>` command adds a line in your own words to the shared journal, marked as a guess and not a clue:
   > *(Note by Eugene: maybe she sank near the island? The coral…)*

   For you and the kids this could be the best part: you'd see each other's theories, argue about them, and take them to the report. It costs little and gives nothing away. Players write the conclusions themselves, which makes them the detectives.
4. **Open questions raised by clues.** Some entries could leave a question behind ("How did coral grow on a compass sold in our market?") that stays open until another clue settles it. That's the most literal form of a growing problem definition. It's also the most authoring work, and the riskiest: a well-chosen question is a hint, and choosing them well is hard. I'd keep this for after a playtest, like the reflection layer in decision 22.
5. **Recording claims that don't hold up**, such as Crane's first story beside his later truth. It suits the historian's lesson, but it changes decision 20 (only true clues are recorded). I'd leave it alone unless the kids ask for it.

### My recommendation

Do 1 and 2 together as the opening step of A4. It's the same purpose fix as before, but put inside the journal instead of beside it, which I now think is better. Add 3 if you like the idea of the kids writing their own theories, since it fits your goal of connection especially well. Keep 4 as a candidate to judge after the next playtest.

## Idea 11. Lack of motivation

**Q:** *MAybe I am overthinking for now, but my biggest concern is about potential loosing interest to the game. If the kid played, say, 20 minutes, found a couple of clues, encountered a few characters, but did not make any signidficant discoveries, continuing the game might be not very motivating... I am comparing with his play Mindcraft - building something "right away", block by block. The process itse;f feels motivating. This game of cource has a very different nature, so my comparison is just to explain m,y concern... That is why I tried to suggest counting clues as points (which I agree was mnot a good idea). That's also why I liked journal - it gives a sense of accomplishment even if no probjems are solved yet. It would be good if after playing half hour I could see somthing like "progress in X is 12%, in Y 59%", whatever X and Y are... Again, please do not convert this into any actions or even plans. I am just brainstorming.*

Your concern is the right one. A mystery has a built-in weakness: its big rewards come late. Minecraft rewards you every few seconds, because every block you place stays there. A mystery can go twenty minutes without giving you anything, and that's where a child gives up. So the real question isn't "how do we count clues". It's "how does something keep growing between the big discoveries".

Here are some thoughts, for brainstorming only.

**Several meters, so one of them is always moving.** Your "X is 12%, Y is 59%" could be real meters that each grow from different activities:
- **Places:** how much of the world you've explored.
- **People:** who you've met and talked to properly.
- **Knowledge:** what you've learned from the Ship, the books and the instruments. Ask about latitude, take a noon sight, learn why oak doesn't grow here, and this meter rises.
- **The case:** clues in the journal.

Clues are rare, but the other three move almost every minute. The Knowledge meter matters most to me, because it rewards the educational part directly. Learning how longitude works then counts as progress in the game, not as a lesson in the way of it. That's your fun-plus-education aim in one number.

**The map as the Minecraft part.** The island map could start blank or faded and fill in as you walk it. After half an hour you'd see a map you uncovered yourself. That's the closest thing in this game to building block by block, it's visual, and the text version stays simple ("explored: 5 of 7 places").

**Making the ship yours.** Naming the ship is already planned as something the kids decide. It could happen inside the game instead of outside it. Ownership motivates a lot, and small choices of their own (a name, later maybe a figurehead or a flag) give a feeling of "this is ours" that solving puzzles doesn't.

**Titles that come with progress.** Ranks earned by the whole expedition, or by each player, as the meters grow (deckhand, navigator, explorer). They're cheap, and kids like them more than adults expect.

**One caution about percentages for the case itself.** Showing "Where did she wreck: 60%" would give away which clues matter for which question, which is the hint we've been avoiding. The case is better as a plain count. Percentages work fine for the other meters.

**Pacing is a design question too, not just a reward question.** It might be worth checking how long it takes from `begin` to the first yellow clue, and the longest gap between any two rewards. If the port gives a reward every few minutes, a lot of the problem goes away before any meters are needed.

**Two things in the kids' favour:**
- Your test was the hardest case: an adult who had already played the opening several times. For a child playing it for the first time, everything is new, and novelty carries the first half hour.
- He'll be playing with you. The shared time is probably the strongest motivation there is, and the game mainly needs to give you two things to talk about.

The most useful thing in the next playtest with your grandson may be simply watching for the moments he goes quiet or starts wandering. Those moments show where the gaps between rewards are.

### Idea 12. Game Sequel

**Q:** *Another thought (not for immediate implementation). Game extension. This game (unlike Mindcraft or Tetris) once playd doe not need any motivation for repetition. It might feel like "loss of investment". BY investment I mean development time, and playing time as well. That's by design, so OK. But maybe we can try to "save" some of both investents by thinking of game continuation - like what movie producers do - converting a successful one into a whole season, then into even more seasons. Same city, same heroes, new scenes. I know that I am jumping far ahead, but  for this game there might be other ship wrecks asking for finding in the nearby islands. Or something like that. What do you think?*

I don't think you're jumping too far ahead. A series is already partly built into the project. "Terrific Travel" is the series name, and stage D in DECISIONS.md is "more adventures, islands, modes". Your TV comparison gives it a clearer shape. Here's what I think carries over, from most to least valuable.

**1. The engine, which is most of the development investment.** Sailing to positions, the shared journal, `ask` with topics, things and instruments, the maps and the Focus pane: none of it is tied to the *Halcyon*. All the story lives in YAML. A new episode is mainly a new set of content files plus perhaps one new mechanic. So the second adventure should cost far less than the first, as long as we keep the code general and the story in data, as we have so far.

**2. The recurring cast and setting.** These are "same city, same heroes" in your terms:
- the home port;
- the Society, with Fairweather handing out each new case;
- the Ship herself, wearing the name the kids gave her.

The Ship is the strongest thread. She becomes the series' main character, the companion the kids already know.

**3. What the players have built up.** This is where the playing-time investment can be saved:
- the ship's name;
- ranks or titles earned;
- the Knowledge meter we talked about.

All of these could carry into the next episode. "Your navigator rank from the *Halcyon* case" makes going on feel like continuing, not starting over. It's the Minecraft feeling again: what you built stays.

**4. A curriculum across episodes.** Each episode could teach one new piece of science and rely on the earlier ones:
- latitude and longitude, here;
- then perhaps tides and currents, winds and weather, stars, or how islands and reefs form.

A skill learned in episode 1, like the noon sight, becomes a tool you just use in episode 2. That's how real knowledge builds up, and it's motivating to feel yourself getting good at something.

**5. The story already has a hook for the next season.** In the truth of this story, the survivors built a boat and sailed west (Jonah's clue, C13). Where did they go, and did they get home? A good series ends each season with one question left open. We wouldn't even have to invent this one, only decide not to close it in the epilogue.

**6. The kids as co-designers of season 2.** This may matter most for your goal. Decision 11 keeps the kids out of the design because a mystery can't be co-designed without spoiling it. That applies only to the first adventure. Once your grandson has solved it, he can help design the next one openly: suggest the island, the characters, the twist. Then he's no longer just playing a game you made; you're making one together.

**Two cautions:**
- **Writing the story is the cost per episode,** not the code. Episodes should probably be smaller than the first one. The first carries the cost of learning; later ones can be tighter.
- **One technical choice is coming up.** Decision 1 gives each game its own folder and shares no code. Episodes of the same series fit better as several adventures inside `phantom_island/`, using the same engine, than as separate games. Nothing needs deciding now. Just don't hard-code "the *Halcyon*" anywhere the engine doesn't need it.

If you'd like to keep this thought, IDEAS.md is the natural home for it when you're ready. For now, the only thing it changes is to keep the epilogue's ending open.

## Idea 13. Context-Sensitive Help

**Q:** *Can the "help" command be context sensitive by using red colors for commands that cannot be applied right now and green color for command that can be used?*

Yes, it can be done. Evennia's `help` is an ordinary command, and the game can replace it with its own version. I'd still suggest a different form than red and green.

**What's already context-sensitive.** Evennia's `help` lists only the commands you have right now. Since `sail` belongs to the Deck, it only appears in `help` while you stand on the Deck. So the commands that can't work are mostly hidden already, rather than shown in red.

**Why I'd avoid red and green:**
- **Colour-blindness.** Red–green colour-blindness affects about 1 boy in 12, so it could well affect one of your two players. Decision 20 already says that meaning must never depend on colour alone.
- **The colours already mean something.** White marks something to try, yellow marks a clue, and in the web client your own typed commands show in green. A green "you can use this" would clash with that.
- **"Can't right now" is usually about a thing, not a command.** `read` always works; what matters is whether there's something here to read. `use sextant` works only on the Deck. A red `read` tells you less than a line that says *what* you can read here.

**What I'd suggest instead: a short "Here and now" section at the top of `help`.** It would list only what makes sense in this spot, with commands in white as they are everywhere else. For example, on the Deck at the charted position:

```
Here and now:
  sail                - give the ship an order
  look sky            - something worth seeing from here
  use sextant         - you're carrying it, and this is where it works
  ask ship            - she listens anywhere aboard
  down                - to the Cabin
Type help <command> for more, or help all for every command.
```

Ashore on the island, the list would show the exits, the people here (`ask ama`), and things you can read or use.

**Why I like this form:**
- **It answers "what can I do now?"** That's the question a wandering 12-year-old actually has, and it ties into the loss of purpose you felt. Only the clues and the journal can answer "what should I do?", but this answers "what *can* I do here?".
- **It needs no new meanings.** White already means "try this", and the text says the rest, so it works on telnet and for colour-blind players.
- **It comes from data the game already has:** the exits of the room, the details and things here, the characters here, and the `only_in` and `at` rules on the instruments.

One caution: the list should name things to try, not the solution. "look sky" here works the same way as the white word in the deck description, so it gives nothing away. But the list should never point at something the room's own text doesn't already mark.

If you want it, it fits naturally in A5 (polish), or earlier if your grandson's first playtest shows him getting lost.

## Idea 14. Sailing Directions Interpretatoions

**The current interpetation**

Yes, it does, but a direction isn't a distance. A direction picks one of the routes from where the ship is now, and each route leads to a fixed position. So how far the ship goes depends on the route:

| From | `sail …` | To | How far |
|---|---|---|---|
| Port (14° S, 0° W) | `west` (or `sail to 14 south 40 west`, or by name: `sail to island`) | The chart's position, 14° S, 40° W | 40 degrees, about three weeks |
| Chart's position | `north` / `south` / `east` | 12° S / 16° S / 38° W | 2 degrees, about 200 km, a day |
| Chart's position | `west` | The island's anchorage, 14° S, 42° W | 2 degrees, a day |
| Chart's position | `home` | Port | the whole way back, slower against the wind |
| One day north, south or east | the way back | The chart's position | a day |
| East of the chart | `home` | Port | the whole way back |
| The island | `east` | The chart's position | a day |

So the same command can mean different things in different places:
- At the chart's position, `sail west` is a day's search.
- In port, `sail west` is the whole three-week voyage.
- Anywhere else, a direction with no route just gets the answer that there's no such route.

All this is in [world/content/ship.yaml](world/content/ship.yaml), under each position's `routes`. Each route has its own Ship's reply and passage text.

One thing to watch when the kids play: someone might expect `sail west` to be a step of a fixed size, the way walking `west` moves you one room. At sea, the steps are the day-long searches, and the passage text says so ("A day north of the chart's position…"). The one big exception is `sail west` from port, which takes you all the way to the chart's position.

**TODO: Possible refinement**

**Q:** *Oh, that explains my confusion first time when I sailed. I said "sail west" assuming a fixed duration (how long?) of saililn in the west position. Similar for all other directions. Turns out that the game has a very specific semantically predefined meanings, hasn't it? I am afraid that this might be misleading... Probably the simplest way to avoid this confusion is to restrict the "sail" command to only "to x south y west" format (with a clear explanation that it has not a directional but location meaning). Am I misinterpreting your definitions? (No need to change anything in code or tests yet).*

You're reading it right. Each `sail <direction>` is a predefined route, and its meaning depends on where the ship is. That's where your first confusion came from: in port, `sail west` isn't "sail west for a while", it's the whole three-week voyage to the chart's position.

I wouldn't go as far as positions only, though. I'd remove the case that misled you and keep the case that works.

**Why not positions only:** at the chart's position, the players' question really is a direction: *which way do we search?* With positions only, they'd have to give a number they can't know: how far west, 41, 45, 50? The game has only a few fixed places, so most numbers would get "nothing there". That turns the search into guessing coordinates, which is the guess-and-try navigation we worked to remove. To avoid it, the sea would need a position at every degree, which is a much bigger change.

**What I'd suggest: two meanings, each only where it fits:**
- **In port, a position (or a name), never a direction.** `sail west` in port would get the Ship asking where to: *"West to where? Give me a position: the island's is on the Halcyon's chart."* That's the confusing case, so it goes. `sail to 14 south 40 west` and `sail to island` stay.
- **At sea, a direction always means one day's search,** and the game says so every time:
  - in the orders text at the chart's position: "Each order is a day's sail, about 200 km";
  - in the Ship's reply: "West it is: a day's sail, two degrees."

  Some replies already say "a day's sail"; the west route to the island doesn't yet.

With that, every `sail` means one of two clear things: *go to that place*, or *search a day that way*. The ship never goes further than the player expects.

This is a small change: one rule in the `sail` code for the port, and a few texts in `ship.yaml`. I'll wait until you ask.
