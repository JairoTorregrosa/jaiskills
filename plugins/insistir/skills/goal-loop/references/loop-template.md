# Loop state templates

Two files per loop. `loop.md` is the implementer-visible state; `heldout.md` is judge/diagnoser-only and must never be quoted into an implementer prompt.

## `loops/<slug>/loop.md`

```markdown
---
slug: {{slug}}
created: {{ISO-date}}
status: in-progress  # in-progress | met | exhausted | plateau
max_epochs: {{N}}
patience: {{N}}
epochs_used: 0
edit_scope: {{broad|targeted}}   # learning rate
judge: {{codex|claude}}
factory_seeds: [{{archive entries that seeded the agent designs}}]
---

# Goal: {{objective}}

## Desired End State

{{What "done" looks like — concrete, unambiguous.}}

## Evidence (visible validation)

| # | Command | Expected | Last Result |
|---|---------|----------|-------------|
| 1 | {{`pytest tests/auth -q`}} | {{exits 0}} | — |

## Constraints

- {{Must-not-violate invariant — e.g. "do not delete or weaken existing tests"}}

## Momentum (recurring patterns)

| Pattern | Seen (epochs) | Status |
|---------|---------------|--------|
| {{e.g. "forgets to invalidate session cache on reset"}} | {{1,3}} | open |

## Descent Log

### Epoch 1

- **Attempt summary:** {{what the implementer tried}}
- **Visible loss:** {{k/n passing; per-command pass/fail + truncated output}}
- **Gradients:** {{diagnoser output — per-failure cause + direction}}
- **Contrastive:** {{what changed on newly-passing checks; behaviors to preserve}}
- **Held-out direction (abstracted):** {{directional guidance only — no commands/expected values}}
- **Judge verdict:** {{MET / NOT MET / not run (visible loss > 0)}} — {{reason}}
```

## `loops/<slug>/heldout.md`

```markdown
---
slug: {{slug}}
visibility: judge-only   # NEVER include any part of this file in an implementer prompt
---

## Held-out Evidence (compositional / end-to-end)

| # | Command | Expected | Epoch 1 | Epoch 2 |
|---|---------|----------|---------|---------|
| 1 | {{`./scripts/e2e_signup_login_reset.sh`}} | {{exits 0}} | — | — |

## Hacking Gap per Epoch

| Epoch | Visible pass rate | Held-out pass rate | Gap |
|-------|-------------------|--------------------|-----|
| 1 | — | — | — |
```

## `loops/archive.md` (cross-goal, append one entry per finished loop)

```markdown
## {{slug}} ({{ISO-date}}) — {{met|exhausted|plateau}} in {{N}} epochs

- **Domain:** {{e.g. Python API + pytest}}
- **Factory designs that worked:** {{e.g. "diagnoser with pytest-failure taxonomy", "judge checking assertion diffs"}}
- **Recurring patterns worth pre-seeding:** {{momentum patterns likely to recur in this domain}}
- **Hacking attempts caught:** {{if any — how the judge caught them}}
```
