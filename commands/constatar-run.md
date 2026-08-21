---
description: Execute a constatar plan.toml and report grounded results
argument-hint: "<plan.toml> [run-dir]"
---

Execute a constatar plan end to end.

1. Load the constatar-verify and constatar-plan skills' rules (verification ladder, invariants).
2. `constatar preflight` — abort with the error if adapters are missing.
3. Parse arguments: `$ARGUMENTS` = plan file, optional run dir (default `runs/<plan-name>-<date>`).
4. If the plan's repo has uncommitted changes, stop and tell the user (the engine will refuse with DirtyRepo; do not stash or commit for them without asking).
5. `constatar run <plan> --run-dir <run-dir>` — stream progress to the user.
6. On success: `constatar inspect --conformance --run-dir <run-dir> --plan <plan> --assert-all-pass`, then summarize per unit: verification rungs passed, evidence highlights, cost (`inspect --cost`).
7. On failure: report the failing unit, rung, and error verbatim; list surviving `constatar/<unit>` branches; suggest `constatar resume` after the cause is fixed. Never re-run units by hand.
