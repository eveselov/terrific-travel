# Building A PLan In PlayTester

I haven't built it. It's listed under "Open work" in [DESIGN.md](playtester/DESIGN.md) as `plan_depth`: goals and next steps carried between turns, at a depth set by the persona, with a plan timeline in the report.

**Is it still worth adding? Yes, but mainly as a way to see what the kid thought it was doing, and less to make the kid play better.**

**What the runs since then showed:**
- **Sonnet already plans, in its notes.** Its notes held lines like "The game said to go to the Lagoon Beach and type aboard, then council", and it carried them out. Adding a plan wouldn't change much for Sonnet.
- **Haiku's failures were mostly failures to keep a goal.** It read "go aboard and type council", then asked Jonah the same things for 20 turns. It knew "get the chart from the ship, then the Hilltop", then got lost on the way and forgot. A plan would help it, but that's a mixed blessing:
  - **The good part:** a cheap model that keeps a goal would make Haiku runs usable for "can a kid finish?".
  - **The risk:** a kid made more organised than real kids hides exactly the problems the playtester exists to find. The `aboard` and routing bugs came to light because Haiku lost its thread.

**Where a plan would earn its place: the report.** Today I reconstruct "what did she think the next step was?" from 200 thoughts by hand, and that's how every finding so far was made. The hint against the report, for one: she believed the next step was the coastline while the game said the beams. A plan field, one goal and two or three next steps updated each turn, would let the report show:
- a timeline of the plan's changes;
- where the plan and the game's hint disagree (rule 1, two next steps);
- how long each goal took, and which goals were dropped.

That turns my manual analysis into part of the report.

**How I'd build it:**
- A `plan_lines` trait, default 0, so current personas and the comparisons between runs stay as they are.
- A `plan` field in the answer, kept and shown back each turn like the notes.
- A "Plan" section in the report: the timeline, plus the turns where the plan didn't change for a long stretch, which is a sign of being stuck.
- About an hour or two of work and a few tests.

**Then measure it** with two pairs of runs, Haiku with and without a plan, then Sonnet with and without. If the plan makes Haiku finish without changing Sonnet's path much, it's a useful setting. If it smooths over the game's problems, keep it off for realistic runs and use it only for the report.

Shall I build it this way?