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
and a **report**, the players' case board, shows the questions with the possibilities met
so far and accepts only conclusions the evidence proves. All content is data, checked
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

## Content as data

Everything above is written in plain data files (YAML), not code: places, characters and
their topics, things, clues, the task, connections, notebook ideas, hints and the report.
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
with the game, not the AI, deciding what may be revealed.

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
  serve authors, hints and evaluation at once.
- **Hints that understand parallel goals.** Hints now follow one fixed order of situations.
  A larger game needs hints that prefer what is near the player, or let the player choose
  which goal to get help with.
- **The play-through check** described above.
- **Evaluation by design**, with records that respect the players' privacy.
- **A second episode**, to show which parts are truly general. Shared code is extracted only
  once two real games exist.
