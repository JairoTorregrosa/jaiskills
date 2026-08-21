---
description: Audit a constatar run — conformance, health trends, cost
argument-hint: "<run-dir> [plan.toml]"
---

Audit a completed or halted constatar run.

1. Parse `$ARGUMENTS`: run dir, optional plan file (enables the plan-dependent conformance checks).
2. `constatar inspect --conformance --run-dir <dir> [--plan <plan>]` — report each of the 10 postconditions: pass/fail/warn/skipped with the engine's detail text. Failures are integrity findings, lead with them.
3. `constatar inspect --health --run-dir <dir>` — report trends (pass-rate trajectory, conflicts, hotspots, spawns-per-unit). Per SPEC P19, never reduce this to a single number; describe the trajectory.
4. `constatar inspect --cost --run-dir <dir>` — per-role cost; call out roles marked incomplete (missing adapter usage data) rather than treating them as zero.
5. Close with an overall verdict grounded ONLY in the above outputs, and concrete follow-ups for any failed check.
