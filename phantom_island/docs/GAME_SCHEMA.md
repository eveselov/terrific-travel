# The Game Schema: Inquiry Games Built on Structured Content

A summary of the design that grew out of Phantom Island, the first Terrific Travel
adventure, written so that it can serve other games, other subjects, and other purposes
such as evaluation. Phantom Island is used for examples (and they give parts of its
solution away). How it is built is in [GAME_AUTHORING.md](GAME_AUTHORING.md); why, in
[DECISIONS.md](DECISIONS.md).

## In one paragraph

A frame for inquiry-based games built on structured content. A **task** keeps players
focused; a shared **journal** collects the evidence; a personal **notebook** grows the
background knowledge, by area and level; **connection questions** prompt reasoning without
giving answers; **hints** at three levels end fruitless wandering without prescribing a path;
a **council** turns many findings into one decision, step by step, wherever exploring must
converge; and a **report**, the players' case board, shows the questions with the
possibilities met so far and accepts only conclusions the evidence proves. All content is data, checked
for consistency, so authors can write new episodes and subjects without code. It supports
fun, learning and, with deliberate design, evaluation. It doesn't produce them by itself:
the content does, within the frame.

## The elements

| Element | What it does | For the player | In Phantom Island |
|---|---|---|---|
| **World and story** | Places, characters, things and events give the task a reason and a setting | explore, `look`, `examine`, `ask`, `read`, `use` | 1790: find out what happened to the lost ship *Halcyon* |
| **Task** | States what the game is for, as a few questions, from the very first moment | always at the top of the journal | What happened to her, and where? Why did nobody find her? What became of her crew? |
| **Clues** | The facts of the mystery, each found somewhere in the world, some only under conditions | shown in yellow when found | coral in the compass hinge; empty sea where the chart puts the island |
| **Journal** | The shared record of evidence: every clue found, by whom, where, from what source | `journal`, `journal sources` | one journal for the whole expedition; a clue confirmed by a second source keeps one entry and lists both |
| **Notebook** | Personal background knowledge: ideas about how the world works, by area, at three levels (*heard*, *understood*, *used*) | `notebook` | latitude, longitude, coral, tides, seabirds at dusk |
| **Connections** | Questions that link two or more clues once all are found; never the answer | shown when they open; `think` | "Oak ribs on the reef, oak beams in the village: what else could her timber have been used for?" |
| **Hints** | The next step, at three levels, from a nudge to the exact command; given when asked, or offered after a long stretch without progress | `hint` | aboard the ship she speaks; ashore the player "thinks it over with the journal" |
| **Council** | At a convergence point, where many findings must become one decision: a short sequence of questions, one at a time, each answered by a choice the journal must support; the last step sums up, and the player then acts | `council`, offered at the moment, never forced | at the empty chart position, the Ship asks: which number is wrong, which side, how far; then "Your order, Captain" |
| **Report (the case board)** | The task's questions, each with the possibilities (theories) met so far; an answer counts only when the journal proves it; an epilogue tells the whole story once all are answered | `report`, consulted all through the game | at first only "she sank in a storm" and "she sailed on"; the coral on the compass adds "sank in the deep ocean" and "wrecked on a reef near the island" |

### How they work together

```
      task ──────────────► report ◄──── proof ──── journal ◄──── clues ◄──── world
       │                     ▲                        │                       ▲
       │                     │                        ▼                       │
       └── focus      understanding ◄── connections (why?)                    │
                             ▲                                                │
                         notebook (how the world works) ◄── teaching ─────────┤
                                                                              │
                         hints (what next?) ─────────── lead back into ───────┘
```

The task says *why* we are here; the journal holds *what* was found; the notebook holds *how
the world works*; connections ask *how it fits*; hints answer *what next*; the report shows
*that it is understood*.

### The report is the centre, not the end

Designed as the final step, the report turned out in play to be the tool players consult
whenever they don't know what to do. Used all through the game, it does three jobs:

1. **Focus.** The task restated as structured questions, with which ones are answered: a
   status, not a greeting.
2. **Hypotheses.** The possibilities met so far, side by side: what the players are trying
   to decide between. A theory belongs to someone or something: it arrives with the witness
   or the evidence that raises it.
3. **Feedback.** Trying a possibility tells whether it fits what is known, and if it can't
   be proved yet, what kind of evidence is missing.

So it is less a final exam than a **case board**, like a detective's wall of questions,
suspects and proof (in inquiry teaching, a "driving question board"). Handing in the
answers is only one thing done at it. Because players read it so often, it is also where
spoilers do the most harm, hence rule 11 below.

### Exploring and converging: the council

A game of this kind has two kinds of play. **Exploring** has no single result: players
wander, meet people and look at things in any order, and every find is a small reward on
its own, which suits short attention spans. **Converging** must turn many findings into one
decision: where to search, whom to believe, what happened. At a convergence point, the
tools for exploring (reading the journal, connection questions, hints) expect the insight
to come silently and at once, in one head. In Phantom Island's first playtest it didn't,
even for the author, who knew the plot.

So a convergence point gets a **process**: a council. In the story, the captain gathers the
crew and the discussion is held in steps; in the game, a guide character (in Phantom
Island, the Ship) asks one question at a time, each with a few choices, and the player
answers. A step is accepted only when the journal holds its evidence; when it doesn't, the
guide says where to look and the council waits, to carry on where it stopped. A wrong
choice leads back to the evidence. The last step sums up, and the player still makes the
decision themselves (gives the order, picks the door): the council builds the decision, the
player takes it.

- **It is the report's machinery, used mid-game.** A step is a question with possibilities
  and a proved right answer; what a council adds is the order of the steps, the moment and
  place it belongs to, and the summing up.
- **The report records and signs; councils guide** (DECISIONS.md, 37). The report keeps the
  purpose and the status, from the start, and is where the player signs an answer. A
  council can conclude report questions: the report then shows its conclusion, and the
  council ends by naming the command that signs it. The player still types it. A game's
  last council is usually the one that prepares the report.
- **Steps are the parts of the decision, each ruling something out.** At the chart's
  position: which number is wrong (so search east or west, not north or south), which side
  (west, not east), how far (near). Designing a convergence point means finding these parts
  first; if a decision has no parts, it is a guess, and players will feel it.
- **It is offered, never forced.** A player who knows can act at once, which keeps replays
  and experienced players free.
- **Together, it is a real discussion.** Everyone present takes part and anyone may answer:
  the council structures the conversation between the players (a child and a grandparent on
  the sofa), which is the best discussion a game can have.
- **An episode may have several.** The game's structure becomes phases of exploration, each
  ending in a convergence point with its council, and the report at the end.

## The entities (a conceptual model)

The elements above are built from a small number of entities. Three diagrams show them: the
task side and the world side are written by authors; the state of play is what the game keeps
while it is played. A line is a relationship, read along its label; the numbers say how many
on each end (1, N, M, 0..1).

**The task side: what is asked, and what proves it.**

```
+------+ 1     N +----------+ 1     N +------------------------+
| Task |---------| Question |---------| Theory (a possibility) |
+------+         +----------+         +------------------------+
                                        |N              |1 the right one
                                  opens |               | is proven by
                                        |M              |N
                                     +------+ M    N +-------------+
                                     | Clue |--------| Proof group |
                                     +------+        +-------------+
                                        |M   any one clue of a group will do
                                  needs |
                                        |N
                                  +------------+
                                  | Connection |
                                  +------------+
```

**The world side: where clues and knowledge come from.**

```
+-----------+ N    1..N +-------+ 1     N +--------+
| Character |-----------| Place |---------| Detail |
+-----------+ stands in +-------+         +--------+
    |1                      |1                 :
    |N                      |N  starts at      :
+-------+               +-------+              :
| Topic |               | Thing |              :
+-------+               +-------+              :
    :                       :                  :
    :.......................:..................:   (also: what is seen from each
                            |                         position of the ship)
                            | each of these is a Source
                 +---------------------+ N   0..1+------+
                 | Source              |---------| Clue |
                 | a text players read | reveals +------+
                 +---------------------+
                            | N   teaches, at a level
                            | M
                         +------+ N     1 +------+
                         | Idea |---------| Area |
                         +------+         +------+
```

**The state of play: what the game keeps.**

```
+------------+ 1     N +---------------+ N     1 +------+
| Expedition |---------| Journal entry |---------| Clue |
+------------+         +---------------+         +------+
  |1  |1  |1               |1  found first: by whom, where, from what
  |   |   |                |N
  |   |   |          +----------+
  |   |   |          | Sighting |  confirmed again: by whom, where, from what
  |   |   |          +----------+
  |   |   |N
  |   | +--------+ N     1 +----------+
  |   | | Answer |---------| Question |  answered by one player, for everyone
  |   | +--------+         +----------+
  |   |N
  | +------+  set by what players do (the noon sight); the expedition also
  | | Flag |  keeps where the ship is, her track, and a voyage under way
  | +------+
  |N
+----------------+ N     1 +------+
| Notebook entry |---------| Idea |
+----------------+         +------+
  |N  level: heard, understood or used, and who taught it
  |1
+--------+
| Player |
+--------+
```

Three things the diagrams show that the element table doesn't:

- **The Clue is the hub.** Sources reveal clues; theories open with them; proof groups and
  connections need them; journal entries record them. Almost every rule of the schema is a
  rule about clues, which is why the clue table is the first thing to design in a new
  episode.
- **Conditions point at clues and flags.** A topic's hidden truth, a thing's reading at a
  given place, and a hint situation all have conditions on clues found and flags set (a hint
  situation also on where the ship is, and which report questions are open).
- **Much is derived, never stored.** Which theories are open, which connections are open,
  which hint situation applies, and whether the report is complete are all worked out from the
  state of play each time. The state stays small (journal, answers, flags, notebooks, the
  ship), which keeps checkpoints and evaluation simple.

## Design rules that make it work

These are the rules the schema depends on; without them the elements are just features.

1. **Facts, not conclusions.** The world shows facts and offers background knowledge on
   request (characters, books, instruments). The conclusion stays the player's to draw.
   A clue's journal line says what was found, and a little of why it matters, never the
   answer to a task question.
2. **Every detail has a reason.** The facts depend on each other as in the real world, and
   the dependencies are written down (a table of "facts that depend on each other") and
   checked whenever one changes. Real facts are checked against sources, which are listed
   for the players at the end.
3. **Evidence over testimony.** Characters tell the truth, are mistaken, or hide something,
   and this is recorded for every topic. Things can't lie. Comparing witnesses and checking
   claims against what can be seen is the central skill.
4. **The proof rule.** A report answer is accepted only when the journal holds its proof
   (groups of clues, any one of each group). The choices never change, so the right one
   never gives itself away by appearing. Wrong choices are what witnesses believe, or a
   natural misunderstanding, never an invented element; turning one down is gentle and
   points somewhere.
5. **No dead ends.** Every bottleneck has at least two ways through and a hint path.
   Hints escalate (a nudge, more direct, the exact command) and start over when the player
   makes progress. Being stuck for long brings one gentle hint by itself.
6. **Questions, not answers.** Connection questions never state the conclusion; hints for
   the report never say which choice. Understanding is tested where it matters: at the end.
7. **Learning shows as text, not scores.** A notebook entry grows with the level reached;
   *used* (having done it yourself) is the test, instead of quizzes.
8. **Short texts, depth one question further.** Replies are short, with the answer first and
   one concrete detail; richness comes from connections between the elements, not from
   more elements or more adjectives. Every noun is a promise players will act on.
9. **Everything shown as a picture also exists as text**, so the game works in a plain text
   client too.
10. **Solo or together.** One player can do everything; two players who split up just get
    there sooner. There are no exclusive roles, and the evidence is shared.
11. **The board shows only what the players could know.** Every possibility arrives with
    the evidence or the witness that raises it, and the right one never arrives alone: it
    comes with a wrong rival raised by the same evidence, so its appearing gives nothing
    away. Right answers are written as claims; their explanation waits for the epilogue.
12. **Where exploring must converge, give it a process.** A decision that needs several
    findings at once gets a council: its parts as steps, one at a time, each supported by
    the journal, offered but never forced. A pile of clues and a hint are not enough.

## Content as data

Everything above is written in plain data files (YAML), not code: places, characters and
their topics, things, clues, the task, connections, notebook ideas, hints, councils and the
report.
A **content check** runs every time the world is built and stops it with a precise message
if the content doesn't fit together: a clue revealed without being marked, a proof naming a
clue that doesn't exist, a hint for a position the ship can't reach, a topic nobody can
discover.

This is what makes the schema practical. Its real bottleneck is the cost of writing good
content, and the check turns the design rules into something the build enforces. A natural
next step is an automatic **play-through check**: because the whole game is data, a program
can explore every reachable state and prove that every task can be answered, every clue
found, and every situation reached by some hint.

## Where it fits

The schema suits subjects that can be **investigated**: history (sources and witnesses),
geography and navigation, natural science (observation and measurement), detective and
diagnostic reasoning. It suits drill and procedural skills (arithmetic, spelling) much
less: there is little to find out, and the proof rule has nothing to hold.

## What is new and what is not

The idea itself has relatives. In educational research, multi-user and narrative learning
environments have long used mysteries to teach science through inquiry (for example *River
City*, from Harvard, and *Crystal Island*, from North Carolina State University). Detective
games check deductions against evidence (*Return of the Obra Dinn*, *The Case of the Golden
Idol*), link facts on a deduction board (the Frogwares Sherlock Holmes games), and give
graded hints (Infocom's InvisiClues). On the assessment side, evidence-centered design and
stealth assessment formalise "claims backed by evidence".

What may be distinctive is the form: lightweight and text-first; multiplayer, with solo and
cooperative play in one world; authored in plain data files with a checker that keeps the
story consistent; a notebook that shows competence as text; and AI characters planned on top,
with the game, not the AI, deciding what may be revealed. The council may be new in its
framing: deduction boards and fill-in conclusions are worked alone, while a council is led
inside the story, step by step, and held together by everyone present (to check against the
prior art, like the rest of this section).

## Evaluation

The schema can support evaluation, but only by design.

**What can be observed.** Clues found, and in what order; which possibilities were
considered, and when (the case board makes this visible); which sources were compared;
connections opened; notebook ideas *used* rather than only *heard*; hints asked for, and at
which level; report choices tried before the right one; time between finding the evidence and
answering.

**What the report alone measures.** With escalating hints and the proof gate, almost
everyone reaches the end, so a finished report shows persistence more than understanding.
Evaluation needs the path, not just the result.

**Asking rather than answering.** A strong signal of competence is the quality of the
questions someone asks: whether they question a source, check a claim themselves, or look for
the missing piece. The schema is well placed to judge questions, because the game knows the
truth and what every question can reveal. A question can be scored by its value (did it reach
evidence the task needs? did it test a witness's claim?) and its timing, not merely counted.
Two cautions:

- With scripted characters, asking is choosing from offered topics, which measures
  attentiveness more than the ability to frame a question. Free conversation with AI
  characters makes asking open, and since the game still decides what can be revealed, every
  question can be judged against the same fixed truth.
- Connection questions would be inverted: instead of offering them, observe whether the
  player raises the connection; offering it becomes help, and counts as such.

**Before using it for high stakes** (hiring, grading): validity (does it predict what it
claims to?), fairness across language and background, accessibility, resistance to gaming
(once questions are scored, people ask many: score their value, not their number), and the
law (in the EU, AI used in recruitment is classed as high-risk). Evaluation also needs
records of play, which a game for children deliberately doesn't keep (Phantom Island logs no
conversations). Share the schema and the content format between such uses, not the running
game or its players.

## Open work before it is a general schema

- **An explicit knowledge model.** Today the links between tasks, claims, evidence and ideas
  are spread across several fields (a report answer's proof, a topic's conditions, what a text
  teaches, the connections). One model linking task → claim → evidence → source → idea would
  serve authors, hints and evaluation at once. The Source of the diagrams, in particular,
  exists only as a concept: in the files it is spread across topics, details, things' actions
  and the views from the ship.
- **Hints that understand parallel goals.** Hints now follow one fixed order of situations,
  and only the shared state of play decides which applies, not where the player stands or
  what they are doing. Three ways forward, cheapest first:
  1. prefer a situation tied to the player's place;
  2. let the player choose the goal (`hint` lists what is open, `hint wreck` helps with that
     one), as classic adventure hints were organised by question;
  3. a small graph of goals with prerequisites, choosing the one nearest the player or the
     one they touched last.
- **Finding the convergence points.** Phantom Island found its first one in a playtest.
  A method would help authors: list the decisions with a single right result, and for each,
  its parts and the evidence for each part. Candidates in Phantom Island besides the chart's
  position: whom to believe about the sinking (the two witnesses), and the report itself.
- **The play-through check** described above.
- **Evaluation by design**, with records that respect the players' privacy. One known leak
  to design out: feedback on an answer can reveal more than intended (in Phantom Island, "the
  Society will want proof" tells the player the theory is right, only unproved).
- **A second episode**, to show which parts are truly general. Shared code is extracted only
  once two real games exist.
- **Check the prior art before citing it.** The relatives named above are given from
  general knowledge; check them against sources before this document is shared widely.

## Engine and episode

What would carry over to every game, and what belongs to one episode, as it looks after
Phantom Island:

| Engine (would carry over) | Episode (Phantom Island's own) |
|---|---|
| clues and the shared journal, the task, the case board with proof, the epilogue | the 13 clues, the three questions, the theories, the epilogue's text |
| councils at convergence points, on the report's machinery | the council at the chart's position, its three steps, the Ship as its guide |
| connection questions; hints with situations, pushed after a stretch without progress | which clues connect; the hint path |
| the notebook of ideas and its three levels | latitude, coral, tides, seabirds... |
| the content loader and checker, the scenario recorder, starting over | places, characters, things |
| the ship that travels between positions (perhaps) | the sea chart, the 1 degree error |

## Replay

A mystery is spent once it is solved; that is normal for the genre, and can be designed as a
feature. Ways to give a series lasting value, cheapest first:

1. **The series is the replay.** Each episode is played once, like a book in a series. The
   notebook carries over: a player who learned latitude in one adventure arrives at the next
   with it already *understood*, and the new episode can build on it. Competence then grows
   across the series, which suits learning better than replaying one story.
2. **Replay as a guide.** A player who has finished can join a newcomer as an adviser, who
   can talk but not find clues or report. In Phantom Island the first young player is
   expected to guide the next one this way.
3. **A record of how it went**, on the epilogue's last page: clues found (11 of 13),
   connections opened, hints used, notebook ideas *used*. It gives a reason to go back for
   what was missed, without turning the game into a quiz, and it costs little: all of it is
   already in the state of play.
4. **Variation between runs**: another island, another error, different witnesses holding
   different facts. This is expensive, because "everything fits together" must then be
   computed, not written. Facts that are arithmetic (4 minutes of time per degree) can vary;
   the story and its people can't without many more texts. Free conversation with AI
   characters will bring some variety by itself.
