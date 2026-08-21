---
description: Verify a unit of work with grounded evidence via constatar
argument-hint: "<unit-name> -- <oracle commands...>"
---

Run ad-hoc rung-1 verification through the constatar engine so the evidence is journaled and grounded (never self-assessed).

1. Parse `$ARGUMENTS`: unit name, then oracle commands (split on `--`; if the user gave none, derive the project's canonical gate: test + lint + build commands from the repo's tooling).
2. `constatar verify --unit <name> --run-dir .constatar-adhoc --cwd . --cmd <c1> --cmd <c2> ...`
3. Report the evidence JSON: pass/fail per command with exit codes. A non-zero exit is a FAIL to report verbatim — never soften it.
4. For verification beyond rung 1 (adversarial/judge), tell the user to declare it in a plan.toml (see the constatar-plan skill) — ad-hoc CLI verification is rung 1 only.
