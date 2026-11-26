# Qwen3 Model Failure As PlayTester

**Q:** *I am trying to use local models with Max. 0.6B looks helpless. Is it a final verdict on its applicability to the task, or am I missing something?*

```
uv run python playtester/playtester.py phantom_island --persona max --reset --model qwen3-0.6b
Loading qwen3-0.6b...
W1125 18:11:19.774000 18596 Lib\site-packages\torch\distributed\elastic\multiprocessing\redirects.py:29] NOTE: Redirects are currently not supported in Windows or MacOs.
Loading weights: 100%|██████████████████████████████████████████████████████████████| 311/311 [00:00<00:00, 333.72it/s]
[reset] startover yes: New expedition started. The ship's track: port.
Max is playing Phantom Island. Max has about 31 minutes today. Ctrl+C stops.
   1 [curious] > <white>begin</white>  $0.00
       I'm curious about the game and the story of the ship, <cyan>Phantom Island</cyan>!
   2 [curious] > help  $0.00
       I'm curious about the game and the story of the ship, Phantom Island!
   3 [curious] > help  $0.00
       I'm curious about the game and the story of the ship, Phantom Island!
   4 [curious] > hlp (meant help)  $0.00
       I'm curious about the game and the story of the ship, Phantom Island!
   5 [curious] > hlp  $0.00
       I'm curious about the game and the story of the ship, Phantom Island!
   6 [curious] > hlp  $0.00
       I'm curious about the game and the story of the ship, Phantom Island!
   7 [curious] > hlp  $0.00
       I'm curious about the game and the story of the ship, Phantom Island!
   8 [curious] > hlp  $0.00
       I'm curious about the game and the story of the ship, Phantom Island!
   9 [curious] > hlp  $0.00
       I'm curious about the game and the story of the ship, Phantom Island!
  10 [curious] > hlp  $0.00
       I'm curious about the game and the story of the ship, Phantom Island!

Max: stopped by you (Ctrl+C).
```

## Claude About Qwen3-0.6B

Mostly yes: 0.6B is too small for this task. But your log also shows two faults in the playtester, and the first would affect any model.

**What went wrong:**

1. **It typed the colour tags.** Turn 1 sent `<white>begin</white>` to the game, which doesn't know that command. The tags are how the program shows colours to the model, and a small model copies them literally. The program should strip tags from what the model types, since no kid would type them. It's a one-line fix that helps every model.
2. **It copied its own past.** The remembered turns include lines like "You typed: hlp (you meant: help)". From turn 5 on, the model just repeats the last command it sees there, typo included, and it repeats its thought word for word. Small models do this: they continue the text in front of them instead of reasoning about it.
3. **The prompt is too much for 0.6B.** A persona, rules for reading the screen, eight answer fields in JSON, and several earlier turns are a lot for a model this size. It manages the JSON format and nothing more.

**What could make small models better:**
- strip tags from commands;
- a much shorter prompt for local models;
- one worked example of a good answer;
- discouraging repetition when the model generates text;
- letting the model think before answering;
- the strongest option: let it *choose* the next command from candidates taken from the screen (the exits, the white words, a few basic commands), the way `llm_lab` ranks intents, instead of writing one.

**Why it's still a verdict on 0.6B:** even with all of that, it would at best follow hints. Spotting false leads, getting confused the way a kid does, and explaining afterwards what was unclear is the reasoning a 0.6B model doesn't have. A multiple-choice player would also be a different test from a kid typing freely. On this PC, 1.7B plays sensibly but takes about 100 seconds a turn on the CPU, and 4B would be slower still.

**The cheap option that works is Haiku 5.5.** A 200-turn run with Max is about 400,000 tokens in at $0.10 per million and 100,000 out at $0.50 per million, so roughly **10 cents a run**. That's an estimate from Max's earlier runs, not a measurement. Haiku is far stronger than any local model here, and runs in seconds a turn:

```cmd
uv run python playtester/playtester.py phantom_island --persona max --reset --model claude-haiku-5-5
```

Local models are still useful for trying the playtester itself, offline and for free.

Shall I make the tag fix? It's small and helps every model. The small-model changes are worth doing only if you want local play for its own sake.

## Claude About Qwen3-1.7B

It is better: 1.7B reads the screen and tries sensible commands. Two things to watch in these five turns, though:

- **It makes things up.** At turn 4 it thinks "I just talked to Mrs. Fairweather", which never happened. What actually happened: it typed `meeting`, which the game accepted as another word for `council`, and got "There's nothing to hold a council about here." It then read that as a conversation. When the kid's thoughts invent events, the report's "confused" and "thought was important" sections get less trustworthy. So check its findings against the transcript, which shows what the game really said.
- **It repeats itself.** Turn 2 repeats `begin` with the same thought word for word. That's the same copying 0.6B did, in a milder form.

**On time:** at about 100 seconds a turn, Max's 30-minute sitting (about 60 turns) will take well over an hour and a half of real time. You can stop it with Ctrl+C at any point, and the report is still written. The interview at the end takes another minute or two. The cost shown stays near $0.00: that's the Haiku-priced figure, so the saving is real but small.

To judge whether 1.7B is useful, compare its report with a Haiku run of the same persona over a similar number of turns. A Haiku run costs about 10 cents by my estimate and finishes in minutes. If the two find the same problems in the game, 1.7B is usable when you're offline. If 1.7B mostly finds its own confusions, Haiku is the better cheap option.

My earlier offer still stands: strip colour tags from commands, which 0.6B tripped over and which helps every model.