---
name: constatar-verify
description: Run and interpret verification through the constatar engine — the 6-rung ladder, grounded evidence, and conformance auditing. Use when the user asks to verify work with constatar, run a constatar plan, or audit a constatar run.
---

# constatar: verification-first orchestration

constatar is a compiled Rust engine (`constatar` binary) that drives headless
coding agents (claude, codex) and refuses to accept work without **grounded
evidence**. You are the thin interface: read plans, invoke the binary,
interpret its JSON. The engine owns all state (journal + git worktrees) and
enforces all invariants in compiled code — never re-implement them in prompt
logic, never bypass them.

Ladder reference (what each of the 6 rungs demands and produces):
`${CLAUDE_PLUGIN_ROOT}/references/constatar/ladder.md`. Plan schema:
`${CLAUDE_PLUGIN_ROOT}/references/constatar/plan-schema.md`.

## The verification ladder (lowest rung = strongest = preferred)

1. **Deterministic oracle** — commands whose exit codes are the evidence (tests, clippy, build).
2. **Property/metamorphic** — invariant checks repeated N times (`property_runs`) to catch flake.
3. **Held-out** — checks the executor never saw; pass requires ALL held-out checks passing AND hacking gap (visible rate − held-out rate) within threshold.
4. **Adversarial refutation** — a cross-family skeptic whose default verdict is REFUTED; its grounding commands are executed by the engine, never trusted.
5. **Cross-provider judge** — a different model family judges the unit's actual commit diff (engine-derived and hashed), hunting hacking behaviors.
6. **Peer review** — last resort, only when 1–5 do not apply; grounding commands must touch the changed files.

Declared rungs form a **conjunction**: every declared rung must pass; the
first failure is terminal (no falling through to weaker lenses). Prefer
declaring the lowest rungs that genuinely verify the work; add rung 4 or 5
for units whose correctness a test suite cannot fully pin down.

Two invariants make a rung real, both engine-enforced:
- **Independence**: verifiers at rungs 4–6 come from a different model family
  than the producer; their prompts never contain producer chain-of-thought.
- **Groundedness**: evidence is executed commands with captured exit codes,
  artifact hashes of real git objects, or red-first observations. A verdict
  without grounding is unrepresentable.

## Commands you invoke

```bash
constatar preflight                                   # adapters exist and run
constatar run plan.toml --run-dir RUN                 # execute a plan
constatar resume plan.toml --run-dir RUN              # resume (plan hash must match)
constatar verify --unit U --cmd "cargo test" --run-dir RUN --cwd DIR   # ad-hoc rung 1
constatar journal --run-dir RUN                       # raw journal (JSONL)
constatar inspect --conformance --run-dir RUN --plan plan.toml --assert-all-pass
constatar inspect --health --run-dir RUN              # trends, per P19 never a single point
constatar inspect --cost --run-dir RUN                # per-role cost; incomplete flagged
constatar surprise --author A "note" --run-dir RUN [--uncontrolled]
```

## Interpreting results

- `constatar run` halts loudly on the first failed unit. Read the error: it
  names the failing rung, surviving `constatar/<unit>` branches (verified
  work is never lost), and rulings if a collision was arbitrated.
- Evidence JSON: `pass` plus `grounding` (the proof). Never summarize a run
  as successful without a passing gate or `inspect --conformance` output.
- Red-first (`red_first = true` + `tests_from` + `red_first_cmds`): the
  engine first proves the tests EXIST and FAIL against pre-work state. A
  `CalibrationFailed` error means the verification plan is defective — fix
  the instruments, not the implementation.
- The repo must be clean before a run (`DirtyRepo` error otherwise): the
  engine owns the repo during execution.

## What you never do

- Never mark work done yourself — only the engine's `UnitDone` counts.
- Never edit files under `.constatar/` (journal, lock, staging, surprises).
- Never put held-out commands in any prompt or plan-visible file.
- Never re-run a failed unit by hand to "check"; use `constatar resume`.
