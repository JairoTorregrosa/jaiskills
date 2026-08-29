---
description: Build a Claude Agent SDK agent by answering 9 illustrated questions, then run it.
argument-hint: "[qué quieres que haga el agente — opcional]"
---

# Agent SDK wizard

Invoke the `agent-sdk-wizard` skill and run it end to end.

$ARGUMENTS

## How to start

- **Arguments given** → that text is the goal. Use it as the pre-filled proposal for step 2:
  ask the question anyway, but say in one line which archetype it maps to and put that option
  first. Do not skip step 2 — the user's phrasing is a goal, not an archetype.
- **No arguments** → start at step 1 with no preamble.

Then follow `SKILL.md`: nine `AskUserQuestion` calls, one per step, every option carrying its
ASCII `preview` from `references/previews.md`, recommended option first. Generate the agent
from `templates/`, and do not report done until it has actually run and printed its `result`.

If the user says "dame todos los recomendados" / "just use the defaults", skip the remaining
questions, take every recommended option, generate, run, and then show the nine decisions so
nothing is a surprise.
