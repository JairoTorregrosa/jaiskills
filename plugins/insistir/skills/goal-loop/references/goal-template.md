---
slug: {{slug}}
created: {{ISO-date}}
status: in-progress  # in-progress | met | exhausted
budget: {{N}}
iterations_used: 0
judge: {{codex|claude}}
---

# Goal: {{objective}}

## Desired End State

{{What "done" looks like — concrete, unambiguous.}}

## Evidence

| # | Command | Expected | Last Result |
|---|---------|----------|-------------|
| 1 | {{e.g. `pytest tests/ -q`}} | {{exits 0}} | — |
| 2 | {{e.g. `grep -c "def test_" tests/auth_test.py`}} | {{>= 5}} | — |

## Constraints

- {{Must-not-violate invariant 1}}
- {{Must-not-violate invariant 2}}

## Iteration Log

### Iteration 1

- **Attempt summary:** {{what the implementer tried}}
- **Evidence results:**
  | # | Pass/Fail | Output (truncated) |
  |---|-----------|-------------------|
  | 1 | — | — |
  | 2 | — | — |
- **Judge verdict:** {{MET / NOT MET}}
- **Judge reason:** {{verbatim reason from judge}}
