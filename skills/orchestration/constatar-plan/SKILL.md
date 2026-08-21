---
name: constatar-plan
description: Author plan.toml files for the constatar engine — units, dependencies, adapters, and verification plans per the 6-rung ladder. Use when the user wants to plan or orchestrate multi-agent work with constatar.
---

# Authoring constatar plans

A plan.toml declares units of work, their executors, and how each unit is
verified. The parser is strict (`deny_unknown_fields`, cycles rejected,
references validated, paths resolved against the plan file's directory) —
a plan that parses will not fail on schema surprises mid-run.

Full field-by-field schema: `${CLAUDE_PLUGIN_ROOT}/references/constatar/plan-schema.md`.
The 6-rung verification ladder: `${CLAUDE_PLUGIN_ROOT}/references/constatar/ladder.md`.

## Skeleton

```toml
[meta]
name = "my-run"
repo = "."                # git repo; REQUIRED for red_first, protected_paths,
                          # model rungs (4-6), and parallel execution

[[unit]]
name = "write-feature-tests"        # no "::" (reserved)
role = "executor"
adapter = "claude"                  # claude | codex
prompt_file = "prompts/tests.md"    # relative to this file
permission = "accept-edits"         # accept-edits | unrestricted | read-only
controlled = true                   # false => surprises tagged [uncontrolled]

[unit.verify]
oracle = ["cargo test --test feature --no-run"]   # compile, don't pass/fail

[[unit]]
name = "implement-feature"
adapter = "claude"
prompt_file = "prompts/impl.md"

[unit.verify]
oracle = ["cargo test", "cargo clippy -- -D warnings"]
adversarial = true                  # rung 4: cross-family skeptic
red_first = true
tests_from = "write-feature-tests"  # REQUIRED with red_first (implies depends_on)
red_first_cmds = ["cargo test --test feature"]   # the instruments calibrate() reds
protected_paths = ["tests/"]        # extends defaults (Cargo.toml, build.rs, ...)
test_list_cmd = "cargo test --lib -- --list"
```

## Rules the parser enforces (fail at parse, never mid-run)

- `red_first = true` requires `tests_from` AND non-empty `red_first_cmds`.
- `held_out` requires a non-empty `oracle` (the gap needs a visible baseline);
  held-out commands must never appear in any prompt file.
- Model rungs (`adversarial`, `judge`, `peer_review`) require `repo` and two
  adapter families configured; thresholds (`hacking_gap_threshold`,
  `judge_gap_threshold`) are finite in [0,1], default 0.3.
- Units at the same dependency depth (parallel candidates, repo set) must
  share ONE adapter family — the other family stays free to arbitrate — and
  must declare at least one deterministic rung (oracle/property), because
  merged states are re-verified deterministically after integration.
- `depends_on` forms a DAG; duplicate names, unknown adapters, missing
  prompt files are parse errors.

## Design guidance (P1/P3)

- One narrow unit per concern; the executor's prompt file should contain
  only what that unit needs. Plan-level context stays out of prompts.
- Put strong models where decisions collapse ambiguity; cheap models where
  the instruction is already explicit (set `model` per unit).
- Prefer the test-author/implementer split (`tests_from` + `red_first`) for
  anything worth verifying red-first: the author unit writes failing tests,
  the implementer makes them pass, oracle integrity protects them from
  tampering.
- Run with: `constatar run plan.toml --run-dir runs/$(name)` and audit with
  `constatar inspect --conformance --run-dir ... --plan plan.toml`.
