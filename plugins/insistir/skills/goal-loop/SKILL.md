---
name: goal-loop
description: >
  Loop-engineering goal loop — implement → verify → judge → iterate until the goal is provably met.
  Separates worker from judge (different model instances) to prevent self-comforting optimism.
  Fresh implementer each iteration preserves mistakes as learning signal without context pollution.
  Use when: (1) user says /insistir:goal, (2) a task needs verifiable completion evidence,
  (3) "goal loop", "loop until done", "iterate until passing", "keep going until tests pass".
  Do NOT use for: (1) goals that cannot be expressed as observable evidence (ask user to refine first),
  (2) trivial one-shot tasks, (3) open-ended exploration with no clear done-state.
---

# Goal Loop: Implement → Verify → Judge → Iterate

Loop engineering applied to goal completion. A fresh implementer attempts the goal each iteration, concrete evidence commands verify the result, and an independent judge (different model, no access to implementer reasoning) decides whether the goal is genuinely met — catching reward hacking, deleted tests, and weakened assertions.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   GOAL CONTRACT                          │
│  end state · evidence commands · constraints · budget   │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │   ITERATION N       │◄──────────────────┐
              └──────────┬──────────┘                    │
                         │                              │
              ┌──────────▼──────────┐                    │
              │  A. IMPLEMENT       │  fresh subagent    │
              │  (goal contract +   │  (no reuse)        │
              │   iteration log)    │                    │
              └──────────┬──────────┘                    │
                         │                              │
              ┌──────────▼──────────┐                    │
              │  B. VERIFY          │  run evidence      │
              │  (Bash commands,    │  commands, capture  │
              │   check outputs)    │  pass/fail         │
              └──────────┬──────────┘                    │
                         │                              │
              ┌──────────▼──────────┐                    │
              │  C. JUDGE           │  independent model  │
              │  (goal + evidence   │  (Codex or Claude)  │
              │   + diff — NO       │                    │
              │   implementer       │                    │
              │   reasoning)        │                    │
              └──────────┬──────────┘                    │
                         │                              │
                    ┌────▼────┐                          │
                    │  MET?   │── no ── append log ──────┘
                    └────┬────┘
                         │ yes
              ┌──────────▼──────────┐
              │  D. REPORT          │
              │  status + evidence  │
              └─────────────────────┘
```

## Phase A: Goal Contract

Convert the user's objective into a goal contract. Ensure the directory exists (`mkdir -p goals`), then write it to `goals/<slug>-goal.md` using the template at [references/goal-template.md](references/goal-template.md).

**Four required fields:**

| Field | Purpose | Example |
|-------|---------|---------|
| Desired end state | What "done" looks like | "Auth module handles login, signup, reset with tests" |
| Evidence | Commands + expected outcomes that PROVE success | `pytest tests/auth exits 0`, `grep -c "def test_" >= 5` |
| Constraints | Must-not-violate invariants | "Do not delete existing tests", "No hardcoded credentials" |
| Budget | Max iterations before giving up | Default: 5 |

**Critical rule:** If evidence cannot be expressed as observable commands or artifacts, push back and refine with the user BEFORE entering the loop. Unverifiable goals are rejected — never silently accepted.

## Phase B: Loop (iterate up to budget)

For each iteration:

### 1. IMPLEMENT

Spawn a fresh subagent (Task tool) with:
- The full goal contract
- The accumulated iteration log (previous failures preserved verbatim — mistakes are learning signal, never truncated)
- Instructions to implement and leave the working tree in a state that satisfies the evidence

The implementer is a general-purpose coding agent. Do NOT reuse agents across iterations — fresh context prevents compounding hallucinations.

### 2. VERIFY

Run every evidence command via Bash. Capture stdout, stderr, and exit code. Record pass/fail for each command in the goal file's Evidence table (last result column).

### 3. JUDGE

If all evidence commands pass, send to the judge:
- Goal contract (end state + constraints)
- Evidence outputs (raw command results)
- `git diff` of changes made this iteration

The judge prompt:

> You are an independent judge. Given the goal contract and evidence below, determine whether the goal is genuinely met. Look specifically for reward hacking: deleted tests, weakened assertions, hardcoded expected values, disabled checks, or any shortcut that makes evidence pass without truly satisfying the objective. Return JSON: {"met": true/false, "reason": "..."}

**Judge selection:**
- Default (`--judge codex`): use `mcp__codex__codex` with `sandbox: "read-only"` and `approval-policy: "never"`
- Fallback (`--judge claude` or Codex unavailable): spawn a fresh Claude subagent with the same prompt

The judge NEVER sees the implementer's reasoning or chain of thought — only artifacts and outputs.

### 4. DECIDE

- **met = true** → exit loop, proceed to Report
- **met = false** → append iteration entry to the goal file (attempt summary, evidence results, judge verdict + reason), increment counter, continue with a FRESH implementer

## Phase C: Report

Output final status:
- **MET after N iterations** — evidence summary, pointer to goal file
- **BUDGET EXHAUSTED** — closest state achieved, remaining failures, and suggestion: "Consider decomposing this goal into smaller sub-goals"

## Flags

| Flag | Default | Effect |
|------|---------|--------|
| `--max-iterations N` | 5 | Override iteration budget |
| `--judge codex\|claude` | codex | Select judge provider |

## Relation to Native /goal

Claude Code ships a native `/goal` command (v2.1.139+) that uses Stop hooks with a prompt-based evaluator on the same conversation context. This skill complements it by adding:

1. **Fresh-context iterations** — each implementer starts clean, avoiding context window exhaustion on hard problems
2. **Cross-provider judging** — Codex (GPT-5.x) judges Claude's work, eliminating same-model optimism bias
3. **Persistent goal file** — the iteration log survives sessions and compounds learnings
4. **Explicit reward-hacking detection** — the judge prompt specifically targets gaming behaviors

Use native `/goal` for quick single-session convergence. Use `/insistir:goal` for hard problems that need multiple fresh attempts and adversarial verification.
