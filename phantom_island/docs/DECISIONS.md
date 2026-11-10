# Decisions

The settled meta-decisions for Phantom Island, with what each one means for the work. The
discussion that led to them is in [GAME_INCEPTION.md](GAME_INCEPTION.md); the story draft is in
[GAME_STORY.md](GAME_STORY.md). Add a line here whenever something is settled, and change an
entry rather than adding a contradicting one.

Settled on 2026-11-10 unless noted.

## Development staging

The full playable game comes first, with no AI. AI characters come second, after a side step
to build the base AI package from the `llm_lab` findings.

| Phase | Content | Ends with |
|---|---|---|
| **A. Complete game without AI** | A1 island skeleton (rooms, exits, map) · A2 scripted inhabitants (`ask <char> about <topic>`) · A3 discovery and shared journal · A4 mystery, gates, events, ending · A5 polish · playtest with the co-designers · fixes | A finished adventure the co-designers have played and approved |
| **B. Base AI package** | B1 package design, its interface taken from A2 · B2 implementation · B3 one character switched to AI | One AI character in the game; the game still decides which clues are revealed |
| **C. AI characters** | One character at a time, tested against playtest transcripts · free conversation · second playtest | The same adventure with AI inhabitants |
| **D. Growth** | More adventures, islands, modes | — |

Every stage ends with something playable from start to finish, tested with two players logged
in (two browser windows are enough).

## Meta-decisions

| # | Topic | Decision | What it means for the work |
|---|---|---|---|
| 0 | **Name** | Working title **Phantom Island**, folder `phantom_island`. The co-designers choose the final title. | `SERVERNAME` and texts say "Phantom Island" until then. |
| 1 | **Sharing code with `game/`** | Share nothing. Copy what's needed. | Common abstractions get extracted only after at least two real games exist. `game/` stays a playground for trying things out, not a game to finish. |
| 2 | **Folder** | Created with `evennia --init phantom_island`. Design documents live in `docs/`. | Evennia's own layout is kept. The template hooks were copied from `game/` for their type annotations; the map feature was not copied. |
| 3 | **Repo docs** | Updated to "one folder per game", with `game/` as the playground. | — |
| 4 | **Ports** | Telnet 4010, web 4011, websocket 4012 (internal: web 4015, AMP 4016). | Set in `server/conf/settings.py`. It can run at the same time as `game/`. |
| 5 | **Language** | English only. | All texts, character topics and, later, AI prompts and tests. |
| 6 | **Connection and player count** | Mostly online from two homes, sometimes on a shared computer. **The game must also be playable by one player alone.** | Hosting over the internet (see BUILD.md: Tailscale is the simplest safe option). Two players must not be required. *How solo play works (both roles, switching role, or something else) gets its own discussion before the game details are designed.* |
| 7 | **World model** | One shared world. During solo development, resets are done by hand (wiping or restoring the database, see BUILD.md). **Checkpoints and rollbacks** are decided when the game goes to the co-designers. | Nothing to build now. Keeping the adventure's state (clues found, gates opened, journal) in one well-defined place will make checkpoints easy to add later. |
| 8 | **Privacy** | The real game does not log conversations. `llm_lab`'s replayable logs are for development only. | No transcript storage in the game. Playtest transcripts, if any, are made deliberately by the developer. |
| 9 | **History and culture** | Invented but plausible story. Real facts are checked and listed with sources. The islanders are an invented people, shown as capable and kind. The level of scariness is set by the co-designers. | A sources list goes with the epilogue and the educational facts. |
| 10 | **Scope guard** | None for now. Claude may suggest limits as work goes on. | The first month is solo development. Scope is discussed with the co-designers after the draft. |
| 11 | **How the co-designers take part** | Open. To be discussed once the draft exists. | — |
| 12 | **Story content format** | **YAML** files, so the co-designers can edit characters later. | Story content is kept in data files separate from the code. `pyyaml` is a declared dependency, and `types-pyyaml` (dev) lets strict mypy check code that reads it. |

## Open questions

- Solo play: how does one player get past role-only clues? Not blocking A1–A2; needed before
  A3, where role-based descriptions come in. (from 6)
- Checkpoints: needed when the game goes to the co-designers; which commands, and what is saved? (from 7)
- The questions for the co-designers at the end of [GAME_STORY.md](GAME_STORY.md).
