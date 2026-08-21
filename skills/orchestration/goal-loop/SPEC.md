# SPEC — goal-loop v0.3

Formal specification of the goal-loop skill (loop engineering as gradient descent, executed by
an agent + instrument factory). Keywords MUST/MUST NOT/SHOULD/MAY per RFC 2119. This document is
the contract; SKILL.md is the executable procedure; `references/` are the supporting frameworks.

## 1. Purpose and scope

Given a user goal, drive it to *provably met* through iterated epochs of
FORWARD → LOSS → BACKWARD → MOMENTUM → JUDGE, where every role (implementer, verifier,
diagnoser, judge) and every measurement instrument is generated per goal by a factory and
verified before use.

**In scope:** goals expressible as observable evidence, resistant to a single attempt.
**Out of scope (MUST decline or redirect):** goals with no observable done-state (refine first);
trivially one-shottable goals (implement directly); open-ended exploration.

## 2. Definitions

| Term | Meaning |
|---|---|
| Observable | A behavior/property/side-effect that must be seen for "done" to be believable |
| Instrument | A tool through which an observable is measured; sees only a projection of the goal |
| Blind spot | An observable no registered instrument covers |
| Visible evidence | Checks the implementer optimizes against (the training loss) |
| Held-out evidence | Compositional checks run only by verifier/judge (the test set) |
| Hacking gap | visible pass-rate − held-out pass-rate |
| Epoch | One full loop iteration |
| Gradient | Textual diagnosis: responsible behavior + direction of change (not raw error output) |
| Momentum | Recurring patterns accumulated across epochs with counts and status |
| Edit scope | The learning rate: `broad` \| `targeted` |

## 3. Artifacts and layout

```
loops/
  archive.md                    # cross-goal library: agent designs, instruments, patterns
  <slug>/
    loop.md                     # contract + descent log (implementer-visible)
    heldout.md                  # held-out evidence + hacking-gap table (judge-only)
    agents/{implementer,verifier,diagnoser,judge}.md
    tools/                      # generated instruments (assets, not scripts)
```

- A1. `loop.md` MUST contain: frontmatter (slug, status ∈ {in-progress, met, exhausted, plateau},
  max_epochs, patience, epochs_used, edit_scope, judge, factory_seeds), desired end state,
  visible evidence table, constraints, momentum table, descent log (one entry per epoch).
- A2. `heldout.md` MUST contain the held-out evidence table and per-epoch hacking-gap rows,
  and MUST carry `visibility: judge-only`.
- A3. No fragment of `heldout.md` (commands, expected outputs, assertion text) may ever appear
  in an implementer prompt or in `loop.md`. **[INV-1, the leak invariant]**
- A4. Every generated instrument in `tools/` MUST have: a typed interface declared before
  implementation, structured output, exit-code verdict, declared blind spots, and passing
  positive + negative/boundary validation.

## 4. Phase contracts

### Phase 0 — Intake → goal contract
- P0.1 The contract MUST define: end state, evidence (partitioned visible/held-out),
  constraints, max_epochs (default 6), patience (default 2), initial edit_scope.
- P0.2 Evidence MUST be observable commands or artifacts. Self-assessment MUST NOT count.
- P0.3 If no held-out check exists, one MUST be derived by composing visible checks into an
  end-to-end scenario; the split MUST NOT be silently skipped.
- P0.4 Unverifiable goals MUST be pushed back to the user; one-shottable goals SHOULD bypass
  the loop with a direct implement+verify.
- **Postcondition:** `loop.md` and `heldout.md` exist and are internally consistent.

### Phase 0.5 — Observability plan (instrument factory)
- P5.1 Observables MUST be enumerated explicitly before any implementation work.
- P5.2 Instruments MUST be acquired via the ladder reuse → configure → compose → generate →
  escalate; generation requires the amortization rule (expected reuse justifies cost).
- P5.3 **Calibration [INV-2, red-first]:** every visible and held-out evidence command, and
  every generated instrument, MUST demonstrably FAIL against the pre-implementation state
  (or a known-bad sample) and SHOULD pass a known-good reference where one exists, before epoch 1.
- P5.4 Each instrument's coverage, cost, and blind spots MUST be registered in `loop.md`.
- **Postcondition:** every contract observable maps to ≥1 calibrated instrument, or the gap is
  escalated to the user.

### Phase 1 — Agent factory
- P1.1 Four agent files MUST be generated per goal, specialized from
  `references/factory-templates.md` with domain, toolchain, constraints, and archive seeds.
- P1.2 `loops/archive.md` and `docs/solutions/` MUST be consulted before generating;
  seeds used MUST be recorded in `loop.md` frontmatter.
- P1.3 The implementer file MUST NOT reference held-out artifacts (per INV-1).

### Phase 2 — Descent loop (per epoch, while epochs_used < max_epochs)
- P2.1 FORWARD: a **fresh** subagent MUST be spawned per epoch **[INV-3, no agent reuse]**,
  receiving `agents/implementer.md` + current `loop.md`. A leak check on the prompt MUST
  precede spawning.
- P2.2 LOSS: all visible commands run and recorded in `loop.md`; all held-out commands run and
  recorded ONLY in `heldout.md`. Integrity checks MUST pass: evidence files unmodified by the
  implementer, no skip/xfail markers added, test count non-decreasing **[INV-4, oracle integrity]**.
  An integrity failure invalidates the epoch's loss and is treated as a constraint violation.
- P2.3 BACKWARD: if any check failed (or any previously-failing check now passes), the
  diagnoser MUST produce: per-failure gradients, contrastive diagnosis of new passes, and
  held-out direction *abstracted* (no held-out specifics, per INV-1). SHOULD be skipped when
  loss = 0 with no prior epochs.
- P2.4 MOMENTUM: diagnoses merge into the momentum table with counts and status.
- P2.5 LEARNING RATE: same top pattern ≥2 epochs without visible-loss improvement →
  edit_scope MUST shrink to `targeted`; no improvement for `patience` epochs → early stop
  with status `plateau` **[INV-5, non-monotonicity guard]**.
- P2.6 JUDGE: runs only when visible loss = 0. Inputs: contract, epoch diff, visible + held-out
  results. The judge MUST NOT receive implementer reasoning **[INV-6, judge independence]**;
  SHOULD be a different model/provider than the implementer (default: Codex via
  `mcp__codex__codex`, sandbox read-only, kebab-case params; fallback: fresh Claude subagent).
  Output MUST be `{"met": bool, "hacking_gap": number, "reason": string}`. The judge MUST hunt
  the 7 hacking behaviors (arXiv:2606.26300) and the registered blind spots. A positive
  hacking gap with green visible evidence MUST yield met=false absent contrary proof in the diff.
- P2.7 DECIDE: met → Phase 3; not met → append full epoch entry (attempt summary, loss,
  gradients, verdict verbatim — never truncated **[INV-7, mistakes are signal]**) and continue.

### Phase 3 — Report + archive
- P3.1 Final report MUST state: status (met / exhausted / plateau), epochs used, evidence
  summary, final hacking gap, and — if not met — closest state plus a proposed decomposition.
- P3.2 `loops/archive.md` MUST gain an entry: domain, agent designs that worked, instruments
  worth reusing, recurring patterns, hacking attempts caught.
- P3.3 If a non-obvious problem was solved, `/jaiskills:compound` SHOULD be suggested.

## 5. Evidence-dispute protocol

If an implementer claims the evidence itself is defective: the implementer MUST NOT modify it
(per INV-4) and MUST report; the verifier (lead) adjudicates and, if the claim is valid, fixes
the evidence, re-calibrates it (P5.3), and logs the incident in the descent log and archive.

## 6. Invariants (summary)

| ID | Invariant |
|---|---|
| INV-1 | Held-out content never reaches an implementer, in any form |
| INV-2 | No evidence or instrument enters the loop uncalibrated (red-first) |
| INV-3 | Fresh implementer per epoch; no agent context reuse |
| INV-4 | Implementers never modify evidence, tests, or instruments |
| INV-5 | Loops stop on plateau; iteration count alone never forces continuation past patience |
| INV-6 | The judge never sees implementer reasoning and is provider-independent when possible |
| INV-7 | The descent log preserves failures verbatim across epochs |

## 7. Interface

Command: `/jaiskills:goal <objective> [--max-epochs N] [--patience N] [--judge codex|claude]`
Defaults: max-epochs 6, patience 2, judge codex.
Parallel mode (MAY): independent goals may run their loops concurrently, phase-batched, with
per-goal state fully isolated under `loops/<slug>/`.

## 8. Conformance checks

A run is conforming iff:
1. Both state files existed before epoch 1 and every evidence command failed red-first (INV-2).
2. `git log`/diffs show no implementer commits touching evidence or `tools/` (INV-4).
3. Every implementer prompt is reproducible from `agents/implementer.md` + `loop.md` alone (INV-1).
4. Every epoch has a complete descent-log entry (INV-7).
5. Terminal status is one of met/exhausted/plateau with the required report fields.
6. On met: final visible AND held-out pass rates are 100% and the judge verdict JSON is recorded.

## 9. Known limitations

- INV-1 is enforced by instruction and prompt-construction discipline, not by filesystem
  sandboxing; a hostile implementer with read access could locate held-out files. Mitigation:
  storing held-out evidence outside the implementer's working tree is RECOMMENDED.
- The judge receives verifier-reported results; it independently inspects artifacts but does
  not re-execute evidence by default. Judges MAY re-run held-out commands where sandboxing allows.
- Verifier–generator co-evolution (upgrading instruments when the judge finds gaming) is
  specified as an escalation trigger but its execution is manual, guided by
  `references/factory-framework.md` §8.
