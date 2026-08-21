# The constatar verification ladder — reference

| Rung | Name | Evidence | Pass condition | Engine API |
|------|------|----------|----------------|------------|
| 1 | Deterministic oracle | Executed commands, exit codes, output tails | every command exits 0 | `verify_oracle` |
| 2 | Property / metamorphic | Same, repeated `property_runs` times | all runs of all commands pass | `verify_property` |
| 3 | Held-out | Visible + hidden command sets, hacking gap | ALL held-out pass AND gap ≤ `hacking_gap_threshold` | `verify_held_out` |
| 4 | Adversarial refutation | Skeptic JSON + engine-executed grounding commands (`expected_exit` enforced) | skeptic pass AND grounding consistent | `verify_adversarial` |
| 5 | Cross-provider judge | Judge JSON + engine-derived commit diff hash (`git-commit:<sha>`) | judge pass AND gap ≤ `judge_gap_threshold` AND no hacking behaviors reported | `verify_judge` |
| 6 | Peer review | Reviewer JSON + grounding commands that must reference changed files | reviewer pass AND grounding artifact-linked | `verify_peer` |

Semantics: declared rungs are a **conjunction** evaluated lowest-first; the
first failing rung is terminal (lenses stack, they never substitute — SPEC P7).

Invariants (engine-enforced, not conventions):
- **Independence** — rungs 4–6 require a verifier family ≠ producer family
  (`IndependenceViolation`), and verifier prompts are checked against
  producer output on the exact final spawned string (`ContextLeakDetected`).
- **Groundedness** — `Evidence` cannot be constructed with empty grounding
  (`UngroundedVerdict`); model verdicts that cannot be parsed are refused by
  default; grounding command exit mismatches are `GroundingMismatch`.

Red-first calibration (goal-loop INV-2): `red_first = true` units require
`tests_from` (a predecessor authoring the tests) and `red_first_cmds` — the
engine proves each instrument discovers ≥1 test AND fails with a
`test result: FAILED` line against pre-work state before the implementer runs.

Oracle integrity (INV-4): opt-in per unit — it protects evidence from the
unit that CONSUMES it (the implementer), never from the unit authoring it
(a test-author must touch `tests/`). When declared: protected paths
(defaults extended: `tests/`, `Cargo.toml`, `.cargo/config.toml`,
`build.rs`, at any depth, tracked or untracked), `#[ignore]`/skip/xfail
markers, `#[cfg(test)]` add/delete tampering, and test-name preservation
via `test_list_cmd` against a pre-spawn baseline. `red_first` units must
declare `protected_paths` (parse-enforced).

Integration (parallel plans): each candidate is trial-merged in a staging
worktree, really merged only when clean, then re-verified across ALL its
deterministic rungs against the integrated tree (`<unit>::integration`
evidence) before `UnitDone`. Conflicts are journaled, arbitrated by the
free family (strict JSON ruling), and halt the run.
