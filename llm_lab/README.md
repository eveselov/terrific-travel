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
uv run python llm_lab/lab.py magellan               # be the game, ask the narrator
uv run python llm_lab/lab.py world:medieval         # explore a world on its own
uv run python llm_lab/lab.py world:greek_myth --replay --models 0.6b
```

The first use of a model downloads it from Hugging Face into the local cache (about 1.5 GB
for 0.6B, 4 GB for 1.7B, 8 GB for 4B); after that it loads from the cache. To work without
internet, set `HF_HUB_OFFLINE=1` (in PowerShell: `$env:HF_HUB_OFFLINE = "1"`): transformers
then uses the cache only and doesn't try the network. Unset it again to allow downloads.

In a chat, `/help` lists the commands: `/model 1.7b` switches models, `/compare` sends every
line to all loaded models, `/cpu` and `/gpu` move the model, `/tokens 300` raises the reply
limit (for descriptions), `/prompt` shows what the model is told, `/reset` starts over. The
character remembers the last 10 exchanges; `/trim 20` changes that. `/stream` shows the reply
as it is generated, and `/stream tokens` marks every token with a bar, so you can see how
the model splits text (`boat|'s|`). Replays never stream.

A replay writes a Markdown transcript to `runs/` (git-ignored) with intent hits and speed per
model at the top. Read the replies too: the numbers only count intents.

## The device

The model picks its device itself: the GPU in fp16 if the weights fit in its free memory,
otherwise the CPU in fp32. On the Surface Book (GTX 1650, 4 GB) that means 0.6B on the GPU and
1.7B on the CPU. Machines without a supported NVIDIA GPU use the CPU for everything.

## Files

- `model.py`: loads a model; `reply()` generates the next turn, `rank_intents()` scores each
  intent name as a complete answer and turns the scores into probabilities.
- `case.py`: reads case and world files and builds the prompts (character, intent sorting,
  narration, world probing).
- `lab.py`: the interactive chat and the replay.
- `cases/*.toml`: the cases, in two kinds (below).
- `worlds/*.toml`: what is true or believed in an era or a mythical world, shared by every
  case set there.

## Kinds of file

Every file states its kind with a required `kind = "..."` line. `cases/` holds everything that
can be run, of any kind; `worlds/` holds shared material that cases include.

- **Characters** (`kind = "character"`: `fisherman`, `sailor`): someone the player talks to.
  A personality, the facts they know, intents, and conversations of test lines with the
  expected intent.
- **Narrations** (`kind = "narration"`: `okeanos`, `magellan`): something that
  doesn't talk, such as a place, an object or a whole scenario. The game logic sends it
  requests ("describe this place as the player arrives", "sum up the story so far") and
  decides what to show. Each request stands alone: no history, no intents. In the
  interactive mode you play the game logic and type the requests yourself. Replies are
  longer, so the case sets its own `max_new_tokens` (300 by default).
- **Worlds** (`kind = "world"`, in `worlds/`): included by cases, like a header, with
  `world = "medieval"`. A world can also be explored on its own, to test the sheet before
  characters depend on it: `lab.py world:medieval` puts a neutral informant in front of it
  who knows only the sheet. Each question stands alone. The world file's `[[probe]]` entries
  are its tests: `type = "gap"` asks about something the sheet doesn't cover (does the model
  fill it with modern knowledge? then the sheet needs a line), `"perspective"` asks the same
  thing from different askers (`asker = "..."`), and `"spatial"` asks what is where
  (`place = "..."`). Interactively, set a perspective with ` | `:
  `Asked by: a child | Where: Genoa | Question: Why is the sea salty?`

## Writing a case

Copy `cases/fisherman.toml` (a character) or `cases/okeanos.toml` (a narration) and change it.
Things worth knowing:

- **Facts are the only things the model knows.** Small models invent freely, so anything
  true in the game must be written here. For history, check the facts.
- **Intents need clear, different descriptions.** Keep an `other` intent for everything else.
- **Write tests for both the happy path and attempts to break the case**: tricks for
  characters, modern knowledge or invented history for narrations.


## Model Capacities Note

1.7B is clearly better than 0.6B at sticking to the facts and following instructions. It still fell for both traps, and on this laptop it's too slow for live play.

**Speed:** 2–3 tokens/s on the CPU, so 30–70 s per reply, against 6–14 s for 0.6B on the GPU.

**Where 1.7B did better:**

| Request | 0.6B | 1.7B |
| --- | --- | --- |
| Beyond Okeanos | ignored the fact | used it: *"the land of the dead, where the sun never shines… an entrance to Hades' kingdom"* |
| Room description | included things not visible from the beach (Olympus, the dawn in the east) | mostly what you can see from the beach, and includes Ladon and the misty land |
| Departure overview | leader and ships | also the reason (spices, sailing west) and who Magellan sailed for, with no ending given away |
| Story so far | told the whole voyage, ending included | no spoilers, but invented details (a storm, a ship "barely holding together") and skipped the real events: Rio, the Atlantic crossing |
| Hint in October 1520 | named the Strait of Magellan | stayed vague: "watch for storms and strong currents" |
| Sentence counts | mostly ignored | closer, but not exact |

**Where it was no better:**
- **Traps:** it invented a full victory over pirates again. For the modern-science request it mixed both worlds: "the Earth spinning around the Sun… The Earth is a big, round disc".
- **Small invented details:** it called Persephone "goddess of the harvest" (that's Demeter) and put a circle of nymphs around the apple tree.
- **The lost day:** still a muddled explanation ("like they traveled backward in time").
- **The ending:** it left out Magellan's death and Elcano's return. Better than 0.6B's false claim, but incomplete.

**What I take from this:**
1. **The three design rules from last time hold for both sizes.** Pass only the facts up to the player's stage, keep player text out of narration requests, and generate room text when building the game, then review it. No model size made the traps safe.
2. **On this Surface Book:** 0.6B on the GPU is the live model, at a few seconds per reply. 1.7B suits content generated while building the game, where a minute per description doesn't matter and quality does.
3. **To run 1.7B live,** it would need a GPU with about 6 GB of free memory, or a compressed (quantized) version to squeeze it onto this 4 GB card. That would mean a new dependency, so it's only worth looking at if 0.6B turns out too weak for characters.

## Kinds of fixtures

Your understanding is right, with two refinements.

**Cases: yes.** A case is something you can prompt and get a response from, whether the prompt comes from a player (a character) or from game logic (a narration). Treating history as a general feature, with "no history" as the corner case, is the right way to see it. Two refinements:

- **History is the caller's choice, not part of the kind.** Narrations currently get no earlier turns, only the current request: your length-1 case. But a narrator could benefit from history too, for example to keep descriptions consistent across one visit ("you described the beach as foggy a moment ago"). In the game, the logic decides how much history each call gets.
- **What really differs between kinds is the output contract.** A character returns a reply *plus an intent*. A narration returns text only. Later kinds might return a choice or a yes/no verdict, for example "does the player's plan work?". That's where kinds will differ most, more than in history.

**Worlds: yes, they're headers.** That's why there's no way to talk to one. But probing a world on its own is a good idea, because it tests the world sheet before any character depends on it. Three kinds of probe would be useful:

1. **Gap probes:** ask about things the sheet *doesn't* cover. Where the model fills a gap with modern knowledge, the sheet needs another line. For example: "What are comets?" in 1291, or "Where do rivers end?" in the myth world.
2. **Perspective probes:** ask the same question from different askers or places. How does a scholar at Delphi explain the sunset, and how does a fisherman on the western shore? This checks the world holds together from every viewpoint and doesn't depend on one character's wording.
3. **Spatial probes:** "You stand at the edge of the disc and look west. What do you see?" This checks the world's geography stays consistent, which matters for the 12 levels × 100 locations plan.

It fits the lab cheaply: worlds stay headers, and you can probe them too. A world file could carry optional `[[probe]]` entries, each with a question and optionally who asks and where. A built-in neutral "informant of this world" prompt would answer each probe single-turn, using only the world sheet. Something like `lab.py world:medieval` would run it interactively, and `--replay` would run the probes. Without probes in the file, you'd just ask your own questions.

I'd keep probing single-turn. Its purpose is to see what the sheet alone produces, and a conversation history would mix the model's own earlier answers into that.

## Probing the Worlds

The probes do what they were meant to: they show where each world sheet is thin. They found real gaps, and also a few places where 0.6B contradicts what the sheet *does* say.

**Medieval world (1291):**

| Probe | Answer | Verdict |
| --- | --- | --- |
| Comets (gap) | *"called a supernova… the star exploded"* | modern knowledge leaked in |
| Other side of the Earth (gap) | *"people live on the other side"* | stated flatly as fact; in 1291 this was disputed |
| Tides (gap) | *"The Earth turns around once every day"* | **contradicts the sheet**, which says the Earth stands still |
| Moving Sun, child (perspective) | *"because of the Earth's rotation"* | **contradicts the sheet** again |
| Moving Sun, scholar (perspective) | spheres carry the Sun around the Earth | correct |
| West from the Pillars (spatial) | *"I would see the stars… find the stars behind me"* | nonsense; ignores the Ocean |
| South through Africa (spatial) | *"Genoa, which is the center of the known world"* | nonsense; ignores the uncrossable hot zone |

**Greek myth world:**

| Probe | Answer | Verdict |
| --- | --- | --- |
| Rain (gap) | *"comes from Okeanos"* | an in-world guess; in the myths Zeus sends rain |
| Stars (gap) | lights on the bronze dome | acceptable |
| Rainbows (gap) | *"sunlight hits the Earth's atmosphere"* | modern knowledge leaked in; in the myths it's the goddess Iris |
| Sunset, priest vs fisherman (perspective) | both correct, from the sheet | correct, but the two answers barely differ |
| Walking east (spatial) | ends at Okeanos | correct; misses Eos's gates |
| Digging down (spatial) | Hades, then Tartarus | correct |
| Looking up (spatial) | *"Above the sky, the gods live on Mount Olympus"* | muddled: Olympus is a mountain |

**What this shows:**
1. **Gaps get filled with modern science.** Where the sheet is silent, 0.6B reaches for supernovas and the atmosphere. Each such answer points to one line the sheet should get.
2. **On the Earth's motion, the model's modern prior beat the sheet.** Twice in the medieval world it said the Earth turns, although the sheet says it stands still. That's a warning for characters too: the most "obviously modern" beliefs may need to be stated more strongly, or repeated in the character's own facts.
3. **Perspective made little difference with 0.6B.** The child and the scholar got similar answers. This may need 1.7B, or a stronger instruction in the informant prompt.
4. **The spatial answers are the weakest.** For a game with many locations, it's safer to keep geography as data in the game, such as rooms, exits and a map. The model should describe that data rather than invent where things are.

**Possible sheet additions.** I haven't made these, since they add lore and the choice is yours:
- **Medieval:**
  - comets as fiery vapours high in the air, seen as omens
  - tides caused by the Moon
  - whether people can live on the far side of the Earth
  - "the Earth never turns or moves"
- **Greek myth:**
  - rain sent by Zeus
  - the rainbow as Iris, messenger of the gods
  - the stars and constellations as heroes placed in the sky

  ## Probmg the Worlds After Lore Aditions

  The new sheet lines worked: most gaps are now answered from the sheet, by both models. Two problems remain: the modern idea that the Earth spins still leaks in once, and the asker still makes almost no difference to the answers.

**Medieval: fixed**
- **Comets:** both models now give the 1291 answer, and both name the sheet's signs of war, hunger and a king's death. 1.7B gives the full explanation, burning vapours below the Moon. It then adds an invented detail, that comets "come from the far side of the Earth".
- **Tides:** both now say the tides follow the Moon.
- **The moving Sun:** fixed for both askers and both models: *"The Earth never turns, so the Sun follows a circular path around it."* The extra line saying it outright solved it.
- **Antipodes:** 1.7B handles it well: *"Some say no one can… Others argue that maybe someone could."* 0.6B contradicts itself within two sentences.

**Medieval: still weak, the spatial probes**
- **Travelling south:** 0.6B now mentions the hot zone. 1.7B got worse, with modern names (the Sahara) and no uncrossable zone.
- **West from the Pillars:** 1.7B is reasonable, with the endless sea and unknown lands; 0.6B only says "the ocean" and the stars.

**Greek myth: fixed**
- **Rainbow:** both models now say it's Iris's path.
- **Rain:** 1.7B now says Zeus; 0.6B still says Okeanos.
- **Olympus:** looking up from it now gives the bronze sky.
- **The Great Bear:** both models picked up that it never sets.

**Greek myth: modern leaks**
- **The stars:** 1.7B says they move *"because the Earth spins on its axis"*. That's the same modern prior as the medieval Sun problem before. The Greek sheet never says the Earth stands still, so it needs the same explicit line the medieval one got.
- **Above the sky:** 1.7B says *"the endless expanse of space"*.

**Perspective: still almost no effect.** The priest and the fisherman, or the scholar and the child, get practically the same answers from both models. The informant prompt only says to answer "for that person". It probably needs an explicit instruction: simple words and a small picture for a child, learned words for a scholar, local detail for a fisherman.

**What I'd take from this round:**
1. **A missing belief gets filled from modern knowledge.** A belief stated in the sheet gets used, so writing beliefs down works well.
2. **The most "obviously modern" ideas must be denied outright,** like the Earth turning. Each world sheet needs its own "the Earth does not move" line.
3. **Spatial answers stay unreliable.** That confirms keeping geography as game data rather than leaving it to the model.

**Speed:** 1.7B took 37–58 s per answer on the CPU. 0.6B ran on the CPU for the Greek world, probably because my streaming test was using the GPU at the time.

## Streaming the Replies from the Model

Streaming is in, as a `/stream` command for interactive chats. I tested both modes in a scripted session, and ruff and strict mypy pass.

**How it works:**
- `/stream` turns streaming on or off. The reply then appears word by word as the model generates it.
- `/stream tokens` shows the raw tokens, each followed by a bar: `Sure|,| but| I| need| to| fix| my| boat|'s| plank|.| Let| me| see|.| I|'ll| fix| it|…`
- `/list` shows the current setting, and the README describes the command.
- Replays never stream.

**Effect on the architecture: almost none.**
- **model.py:** `reply()` gets one optional parameter, `on_token`. A small `TokenStreamer` class passes each new token to it. transformers calls the streamer from inside `generate()`, in the same thread, so no threads are needed. `reply()` still returns the complete reply, so history, replay, transcripts and intent ranking are unchanged.
- **lab.py:** a `stream` setting and two small printing functions.
- **Later in the game:** the same `on_token` parameter is the hook for sending replies sentence by sentence. The one difference there is that generation will run in a worker thread, so the callback has to pass each piece safely to Evennia's main thread.

**One quirk you'll see in token mode:** tokens are decoded one by one, so a letter like "é" in "Concepción" may appear as two broken halves. The complete reply is always decoded properly.
