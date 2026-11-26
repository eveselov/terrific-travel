# Playtester Reasoning

**Q:** *I am curious. I hoped that the task in this game is not serious enough to require a powerful model, so that Sonnet or Haiku or even Qwen3 should be sufficient. After all they all have context window big enough to represent much information about the situation in the game, and for reasoning eve Qwen3 can solve Math500 tasks, so why not Phantom Island? Please give me information in terms of internal LLM organization.*

Short answer: a long context window and a good Math500 score measure different things from what the game asks of a player. In terms of how these models are built, it comes down to five points.

## 1. The context window is storage, not understanding

The window says how many tokens the model *can be given*: about 41,000 for these Qwen3 models (`max_position_embeddings` = 40960). Our prompt uses only 2,000–7,000, so the window was never the limit.

What matters is how well the model **uses** what's in its context. At every new token, each layer's attention heads pick out a few earlier tokens and copy information from them into the current position. These are the cached configurations:

| | 0.6B | 1.7B |
|---|---|---|
| Layers | 28 | 28 |
| Width of each token's state (hidden size) | 1,024 | 2,048 |
| Attention heads per layer (sharing 8 key/value heads) | 16 | 16 |
| Parameters in the 28 layers (my arithmetic from the config) | ≈ 440 M | ≈ 1.4 B |
| Parameters in the vocabulary table (152,000 tokens) | ≈ 156 M (a quarter of the model) | ≈ 311 M |

Everything the model knows about the situation must be gathered, layer by layer, into that one vector of 1,024 or 2,048 numbers at the current position. With few, narrow layers there's little room to collect and combine many separate facts: the persona, the rules, the notes, six earlier turns, the screen. In practice small models attend mostly to what's **recent** and what's **repeated**.

## 2. Copying is a built-in shortcut

One of the first circuits language models learn is the *induction head*. It notices "this pattern appeared earlier, so continue it the same way." It's cheap and often right, so it dominates when the model can't do better.

Our prompt is full of such patterns: "You typed: hlp", "You thought: I'm curious…". So 0.6B simply continued them: the same command, typo included, and the same thought word for word. 1.7B did the same at turn 2. Larger models have that circuit too, but enough capacity to override it when the screen says it didn't work.

## 3. Math500 is a trained, short, closed task

- **Trained for it.** Qwen3 was trained hard on mathematics, including reinforcement learning with checkable answers. Math500 is very close to what it practised.
- **Scored with thinking.** The published scores use thinking mode, often with thousands of tokens of working before the answer. Max runs at `low` effort, so the local model **didn't think at all**: it had to choose a move in one pass.
- **One clear question.** A maths problem is short, complete, and has one goal and one answer.

The game is the opposite:
- **Partly hidden:** the model sees one screen at a time.
- **Long:** hundreds of turns.
- **Open:** no single right move.
- **Several jobs at once:** speak as a 12-year-old, write eight JSON fields, rewrite two sets of notes, read a tagged screen, and decide what to do.

Each extra instruction competes for the same small capacity, and small models drop some of them. 0.6B kept the JSON format and dropped the thinking.

## 4. Mistakes feed back into the next turn

A per-step score hides what happens over many steps. A model that gets 95% of turns right still makes about 10 bad moves in 200 turns. In our design, the model's own words come back to it as notes, thoughts and remembered commands. So one invented "fact", like 1.7B's "I just talked to Mrs. Fairweather", becomes part of what it reads next turn, and it builds on it.

Recovering from that takes two abilities:
- **telling what the screen actually said from what it expected,** which small models do poorly: with too little evidence they fill gaps from their training habits;
- **noticing its own error.**

Large models are also trained specifically on long, many-step tasks of this kind; small ones much less.

## 5. Parameters hold know-how as well as facts

How conversations work, how people answer questions, what "ask about the white words" implies, what a 12-year-old would try next: that know-how is stored in the parameters too. 440 million working parameters is little room for general knowledge, pragmatics and playing a role all at once.

## What follows

- **Playing Phantom Island doesn't need the strongest model.** It's a modest task for a mid-sized model, and a heavy one for a very small one. Opus was my default because the API guidance I follow recommends it; I haven't tried Sonnet 5.5 or Haiku 5.5 here. Both are far larger and trained for multi-step agent work, and I'd expect both to play well. That's worth checking with one run each, about 10 cents with Haiku.
- **If you want local models to do better,** these follow from the points above:
  1. let the model think before answering (personas at `medium` effort do this already);
  2. a much shorter prompt with fewer answer fields;
  3. no repeated "You typed" lines to copy from;
  4. a lower sampling temperature;
  5. choosing the command from a list taken from the screen rather than writing it.

  These would help 1.7B more than 0.6B.