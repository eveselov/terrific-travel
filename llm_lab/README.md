# llm_lab: can a small local model play our characters?

A small program, separate from Evennia, for trying Qwen3 models (0.6B, 1.7B, 4B) as game
characters before anything goes into the game. The model runs inside this Python process with
`transformers`: no server, and no internet once the model is in the Hugging Face cache.

Each character reply is shown with an **intent**: what the model thinks the player meant
(`offer_help`, `ask_about_quarrel`...). In the game, intents are what the game logic reacts to.
The model talks, the game decides.

## Run it

From the repo root:

```powershell
uv run python llm_lab/lab.py fisherman              # talk to the fisherman (0.6B)
uv run python llm_lab/lab.py sailor --model 1.7b    # talk to the medieval sailor (1.7B)
uv run python llm_lab/lab.py fisherman --replay     # test lines through 0.6B and 1.7B
uv run python llm_lab/lab.py sailor --replay --models 0.6b
```

The first use of a model downloads it from Hugging Face into the local cache (about 1.5 GB
for 0.6B, 4 GB for 1.7B, 8 GB for 4B); after that it loads from the cache. To work without
internet, set `HF_HUB_OFFLINE=1` (in PowerShell: `$env:HF_HUB_OFFLINE = "1"`): transformers
then uses the cache only and doesn't try the network. Unset it again to allow downloads.

In a chat, `/help` lists the commands: `/model 1.7b` switches models, `/compare` sends every
line to all loaded models, `/cpu` and `/gpu` move the model, `/tokens 300` raises the reply
limit (for descriptions), `/prompt` shows what the model is told, `/reset` starts over. The
character remembers the last 10 exchanges; `/trim 20` changes that.

A replay writes a Markdown transcript to `runs/` (git-ignored) with intent hits and speed per
model at the top. Read the replies too: the numbers only count intents.

## The device

The model picks its device itself: the GPU in fp16 if the weights fit in its free memory,
otherwise the CPU in fp32. On the Surface Book (GTX 1650, 4 GB) that means 0.6B on the GPU and
1.7B on the CPU. Machines without a supported NVIDIA GPU use the CPU for everything.

## Files

- `model.py`: loads a model; `reply()` plays the character, `rank_intents()` scores each
  intent name as a complete answer and turns the scores into probabilities.
- `case.py`: reads case files and builds the two prompts (character, intent sorting).
- `lab.py`: the interactive chat and the replay.
- `cases/*.toml`: one character each: personality, the facts they know, the intents, and
  conversations of test lines with the expected intent.
- `worlds/*.toml`: what people of an era believe, shared by every character of that era.

## Writing a case

Copy `cases/fisherman.toml` and change it. Things worth knowing:

- **Facts are the only things the character knows.** Small models invent freely, so anything
  true in the game must be written here. For history, check the facts.
- **Intents need clear, different descriptions.** Keep an `other` intent for everything else.
- **Write test lines for both the happy path and attempts to break the character.**
