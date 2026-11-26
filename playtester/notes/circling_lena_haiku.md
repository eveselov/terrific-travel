# Lena + Haiku Failed To Finish THe Game - Why?

**Q:** *Please analyze the cmd trace of the test play by Lena (haiku-5-5).  The trace (phantom_island-lena-20261125-2333.txt) confirms (or looks like a confirmation) of my fear that the game might be too complicated / boring for a kid. In almost 200 turns Lena was not able to make a significant problem (even though she reached the island). Please tell me is the problem in Playtester, or model choice, or the game?*

## Claude On Lena+Haiku Circling

I've gone through the whole run. Short answer: **mostly the game, partly the playtester, a little the model.** It isn't that the puzzles are too hard. Lena solved every one she met. What made the run long and boring is loops and next steps that were easy to miss.

## Lena solved the puzzles

| Turns | What she did |
|---|---|
| 53–58 | The coral on the compass, then Crane's confession |
| 101–118 | The council at sea, reasoned correctly: latitude is trustworthy, longitude was guessed; the terns fly west; about a degree |
| 120–123 | `get guides`, then the goats |
| 132–135 | Respect: asked Ama about her people, listened to Tui's song |
| 136–137 | The wreck on the reef |
| 144 | The ship's oak in the beams |
| 161–171 | Ama's story, then Jonah |

By about turn 165 she had all the evidence the final council needs. What she never did was go back aboard and call it.

## Where the turns went

**About half the run, roughly 100 of 199 turns, went on asking characters things they had already answered:**
- Barnaby: about 41 turns, in five rounds;
- Crane: turns 73–84;
- Tui and Ama: turns 148–160 and 186–192;
- Jonah: turns 167–177 and 194–198.

The report shows "Already in the journal" 25 times.

The cause is visible in Barnaby's replies (turns 27–33):
- His *storm* answer highlights **island** in white.
- His *island* answer highlights nothing.
- For any topic he doesn't know, his fallback says: "Ask me about **the great storm**, though."

So the white words lead round in a circle (storm → island → anything → storm), and the fallback keeps offering a topic she's already heard. Tui ("the song" again), Ama ("my village" again) and Jonah behave the same way. Under rule 1, **an offer to ask about something already asked looks like a lead and leads nowhere.**

## Three problems in the game

1. **Fallbacks re-offer exhausted topics.** *Fix:* once a topic is asked, a fallback offers one not asked yet. When none are left: "That's all I know, Captain", plus a pointer to the next person (for Barnaby, Crane in the Market).
2. **The next step comes as a grey aside.** After Crane's confession (turn 58) the game said, in grey: "(That's what the council was waiting for. Back aboard, council carries on.)" Lena read it and went back to Barnaby for 40 more turns. Grey parentheses read as unimportant. *Fix:* put that line in ordinary text, or in the speaker's voice, and keep `aboard` and `council` in white.
3. **No nudge when the evidence is complete.** Once everything on the island is found, nothing outside the hints says "you have what you need: back aboard, call the council". *Fix:* a short line when the last proof is found, in the voice of the journal or the crew.

**Also, `hint` is hard to discover.** It's named only in the `help` list and in the Ship's *advice* topic. Lena never typed `help` and never asked for advice, so she didn't know hints existed. *Fix:* one line on the title page or in Mrs. Fairweather's briefing: "Stuck? Type `hint`."

## One problem in the playtester

**It plays about four times faster than a kid in real time, and the game's automatic hint is timed in minutes.** The game offers a hint after 10 minutes without progress. Lena's sittings took about 10 real minutes for 75 turns, about 8 seconds a turn against a kid's 30. Her worst stretch, turns 60–100, would have been 20 minutes for a kid, enough for one or two hints. The game never offered her one.

The cleanest fix is in the game: count **commands** without progress, say 20, rather than minutes. That works for both kids and the playtester.

## The model

Haiku reasoned well: the council at sea and the respect puzzle were both done correctly. Its weakness is getting stuck on one approach. Dozens of times it noted "same answer again" and then asked again anyway. Lena's persona ("asks lots of questions, wants to understand why") pushes the same way. Max on Opus finished, using hints and moving on sooner. A real 12-year-old might also keep asking, so some of this is realistic. But the loops in the game are what make it pay off so badly.

To separate model from persona, run Lena once on Sonnet 5.5 or Opus after the game fixes. If she still circles, it's the persona; if not, it was Haiku.

## What I'd do

The four game fixes, in this order:
1. fallbacks;
2. hints after a number of commands, not minutes;
3. "Stuck? Type `hint`" at the start;
4. a nudge when the evidence is complete.

The grey aside after Crane's confession can go with them, since it's one line. Then rerun Lena on Haiku: same persona, same model, so the difference is the game. Shall I propose the exact changes?