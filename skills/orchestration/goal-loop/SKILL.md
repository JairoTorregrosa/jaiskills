---
name: goal-loop
description: Drive a verifiable goal to done with factory-built agents, visible and held-out evidence, and a cross-provider judge.
disable-model-invocation: true
argument-hint: "<objective> [--max-epochs N] [--patience N] [--judge codex|claude]"
---

# Goal Loop: Gradient Descent for Goals, Built by an Agent Factory

Objective and flags: $ARGUMENTS

Empty objective → ask for one. Parse the flags (table at the end) before Phase 0.

Formal contract (invariants, phase pre/postconditions, conformance checks): [references/spec.md](references/spec.md). Read it before Phase 0 of a first run and whenever a phase rule is unclear.
Worked example, end to end: [references/example-cv-os.md](references/example-cv-os.md). Read it when the goal is frontend or judgment-heavy.

Treat the goal as a training problem. The working tree is the parameter, evidence commands are the loss function, a fresh implementer is the forward pass, a diagnoser produces textual gradients (the backward pass), momentum accumulates recurring error patterns, and an independent judge validates against held-out checks the implementer never sees. An agent factory generates all of these agents specialized to the goal, consulting an archive of past loops.

## Deep-Learning Mapping

| Deep learning | This loop | Where it lives |
|---|---|---|
| Parameter θ | Working tree + artifacts | the repo |
| Forward pass | Fresh implementer attempt | `agents/implementer.md` |
| Training loss | Visible validation evidence | `loop.md` § Evidence (visible) |
| Held-out test set | Hidden compositional checks | `heldout.md` (judge-only) |
| Gradient ∂L/∂θ | Textual diagnosis: which behavior caused the failure, what to change | diagnoser output |
| Momentum | Recurring-pattern memory across epochs | `loop.md` § Momentum |
| Learning rate | Edit scope per epoch (shrinks on plateau) | contract field |
| Epoch | One full loop iteration | descent log |
| Early stopping | No loss improvement for `patience` epochs | decide step |
| Train/test leak | Showing held-out checks to the implementer | forbidden |

## Directory Layout

```
loops/
  archive.md            # cross-goal archive: agent designs + instruments that worked (stepping stones)
  <slug>/
    loop.md             # goal contract + descent log — the implementer sees this
    heldout.md          # held-out evidence — NEVER included in any implementer prompt
    agents/             # factory-generated, goal-specialized agent prompts
      implementer.md
      verifier.md
      diagnoser.md
      judge.md
    tools/              # factory-generated instruments (probes, harnesses, generators)
```

The factory's conceptual model — observables, capability gaps, the acquisition ladder,
instrument lifecycle, co-evolution — is defined in [references/factory-framework.md](references/factory-framework.md).

## Phase 0: Guided Intake → Goal Contract

Interview the user (AskUserQuestion when genuinely ambiguous) to map the goal onto the loop:

1. **Desired end state** — concrete and unambiguous.
2. **Loss function (evidence)** — commands + expected outcomes that PROVE progress. Then **partition**:
   - **Visible validation** — feature-level checks the implementer optimizes against (e.g. `pytest tests/auth -q` exits 0).
   - **Held-out** — compositional / end-to-end checks that exercise interactions between features (e.g. a full signup→login→reset flow script, an integration scenario, error-path checks). Agents saturate visible tests while failing composition — the held-out set is what catches lookup-table-style gaming and feature-isolation failures.
3. **Constraints** — must-not-violate invariants ("do not delete or weaken tests", "no hardcoded expected values").
4. **Budget** — max epochs (default 6) and `patience` (default 2 epochs without visible-loss improvement → early stop; textual optimization is non-monotonic, more iterations can make things worse).
5. **Initial learning rate** — edit scope for epoch 1: `broad` (restructure allowed) or `targeted` (minimal diffs).

Write the contract to `loops/<slug>/loop.md` and the held-out set to `loops/<slug>/heldout.md` using [references/loop-template.md](references/loop-template.md).

**Hard rules:**
- Evidence must be observable commands or artifacts. Self-assessment is not evidence — intrinsic self-correction without external signal does not converge. If the goal cannot be verified externally, push back and refine BEFORE looping.
- If no meaningful held-out check exists, derive one from the end state (compose the visible checks into a scenario) rather than skipping the split.
- If the goal is likely one-shottable (small, well-specified, cheap to verify), say so and skip the loop — implement and verify directly. The loop's overhead is for goals that resist a single attempt.

## Phase 0.5: Observability Plan (instrument factory)

"Working" is only ever observed through instruments, and reward hacking lives in their blind spots. Before generating agents, generate the measurement system (full procedure in [references/factory-framework.md](references/factory-framework.md), concrete instruments in [references/instrument-catalog.md](references/instrument-catalog.md)):

1. **Enumerate observables** — what must be seen for "done" to be believable (behaviors, compositions, qualities, side-effects).
2. **Gap analysis** — required observables vs the environment's existing instruments (test frameworks, CLIs, MCP servers, dashboards, prior loops' `tools/`).
3. **Acquire per the ladder** — reuse → configure → compose → generate → escalate. Generated instruments go to `loops/<slug>/tools/`, built interface-first (contract before implementation) with structured output and exit-code verdicts.
4. **Calibrate red-first** — every evidence command and generated instrument must FAIL against the pre-implementation state (and pass a known-good reference where one exists) before epoch 1. An uncalibrated verifier is how label bugs poison the loss.
5. **Register** — record each instrument's coverage, cost, and declared blind spots in `loop.md`; the judge hunts specifically in the declared blind spots.

**Evidence disputes:** if an implementer claims the evidence itself is wrong, the verifier (lead) adjudicates, owns the fix, and logs it in the descent log — implementers never touch evidence.

## Phase 1: Agent Factory

Generate the four goal-specialized agent prompt files in `loops/<slug>/agents/` using [references/factory-templates.md](references/factory-templates.md). Before generating:

1. Read `loops/archive.md` (if present) and search `docs/solutions/` for prior loops in similar domains: spawn `subagent_type: "jaiskills:insistir-learnings-researcher"` when the plugin agents are installed, else grep `docs/solutions/` directly.
2. Specialize each template with: the goal domain, the repo's toolchain and conventions, domain-specific failure modes from the archive, and the contract's constraints.
3. Record in `loop.md` which archive entries seeded the designs (stepping stones).

The factory output is prompts, not code: each file is the complete system-of-instructions for one subagent role. Do not reuse generic prompts — a diagnoser that knows the domain's failure taxonomy produces sharper gradients.

## Phase 2: Descent Loop (per epoch, up to budget)

### 1. FORWARD — implement
Spawn a **fresh** subagent (Task/Agent tool) with `agents/implementer.md` plus the current contents of `loop.md` (contract, visible evidence, gradient log, momentum). Fresh context every epoch — mistakes are preserved in the log as learning signal, never in the agent's context.

**Leak check before spawning:** the prompt must contain nothing from `heldout.md` — no commands, no expected outputs, no verbatim held-out failure messages.

### 2. LOSS — verify
Run every **visible** evidence command per `agents/verifier.md` (Bash; capture stdout/stderr/exit code). Then run the **held-out** commands. Record visible results in `loop.md`; record held-out results ONLY in `heldout.md`.

### 3. BACKWARD — diagnose
Spawn the diagnoser (`agents/diagnoser.md`) with: contract, this epoch's diff, visible results, held-out results, and the prior gradient log. It returns:
- **Per-failure gradients** — which behavior caused each failure and what reusable change would fix it (not just the error text).
- **Contrastive diagnosis** — for checks that newly pass, what changed relative to the earlier failing attempt; behaviors worth preserving. Successes are learning signal too.
- **Abstracted held-out direction** — held-out failures translated into directional guidance ("compositions of X and Y break under Z") WITHOUT revealing the held-out commands or expected outputs.

### 4. MOMENTUM — accumulate
Merge the diagnosis into `loop.md` § Momentum: recurring patterns with occurrence counts and coverage status (addressed / open). Momentum stabilizes updates — the next implementer acts on consolidated patterns, not one epoch's noise.

### 5. LEARNING RATE — adapt
- Same top pattern ≥2 epochs with no visible-loss improvement → shrink edit scope to `targeted` and constrain the next implementer to that pattern only.
- Still no improvement after `patience` epochs → **early stop**: report plateau and propose decomposing the goal into sub-goals (each a new loop).

### 6. JUDGE — validate (only when visible loss = 0)
Call the Skill tool with `second-opinion` in judge mode (args: `judge`, plus `--provider claude` when `--judge claude`). Fill its judge inputs from artifacts only:

| second-opinion input | goal-loop source |
|---|---|
| Task spec + acceptance criteria | `loop.md` end state + constraints; visible and held-out evidence expectations |
| Diff | this epoch's diff (range + paths when large) |
| Check results | visible results, held-out results, pass rates, hacking gap (`heldout.md`) |
| Caller-specific checks | body of `agents/judge.md` (goal-specific hacking hunts, registered blind spots) |
| Reviewer verdict | `none` |

Never pass the implementer's reasoning, its attempt summary or its self-assessment. Browser-driven or interactive judge aids ([references/instrument-catalog.md](references/instrument-catalog.md)) run before the call; their transcripts and screenshot paths go in as check results (the judge reads files and runs read-only commands, it cannot drive a browser).

`agents/judge.md` makes the judge hunt the seven hacking behaviors (arXiv:2606.26300): solution-artifact retrieval, external fix lookup, harness tampering, test-oracle tampering (deleted/weakened tests, hardcoded values, lookup-table memorization), visible-test overfitting, evaluator-aware patching, repository-history mining — plus feature isolation (units pass, composition fails) and the blind spots each instrument declared in Phase 0.5.

Map the result to the loop verdict `{"met": bool, "hacking_gap": number, "reason": string}`:
- `met` = judge band is auto-approve AND visible and held-out pass rates are both 100%. Middle band or auto-revise = NOT MET. A positive hacking gap is NOT MET regardless of the judge.
- `hacking_gap` = visible pass-rate − held-out pass-rate, computed by the lead from the verifier's runs.
- `reason` = judge `rationale` + findings, provider label included (`same-provider fallback` when Codex was unavailable).

**Keep the implementer blind.** Write the judge JSON verbatim to `heldout.md` only. What reaches `loop.md` (and so the next implementer) is abstracted like the diagnoser's held-out direction: a finding's file, line, claim and suggestion about working-tree code may be copied; any held-out command, expected output, assertion text or held-out run quoted in `evidence` or `rationale` must not.

### 7. DECIDE
- **met** → Phase 3.
- **not met** → append the epoch entry (attempt summary, loss results, gradients, abstracted judge reason) to `loop.md`, increment epoch, continue with a fresh implementer. Judge findings also feed the next diagnoser.
- **budget/patience exhausted** → Phase 3 with status `exhausted`.

## Phase 3: Report + Archive

1. Report: **MET after N epochs** (evidence summary, final hacking gap, pointer to `loop.md`) or **EXHAUSTED/PLATEAU** (closest state, open patterns, proposed decomposition).
2. Update `loops/archive.md`: goal domain, which factory designs worked, momentum patterns likely to recur, final outcome. This archive seeds the next loop's factory — designs compound across goals.
3. If a non-obvious problem was solved along the way, call the Skill tool with `compound-knowledge` to document it.

## Flags

| Flag | Default | Effect |
|------|---------|--------|
| `--max-epochs N` | 6 | Epoch budget |
| `--patience N` | 2 | Epochs without visible-loss improvement before early stop |
| `--judge codex\|claude` | codex | Judge provider for `second-opinion` (`claude` = same-provider, labelled) |

## Theoretical Grounding

| Design choice | Source |
|---|---|
| Textual gradients + explicit backward pass | TextGrad (arXiv:2406.07496), ProTeGi (arXiv:2305.03495) |
| Diagnoser / momentum / patcher factory roles; contrastive diagnosis; non-monotonic iterations → early stopping | SkillGrad (arXiv:2605.27760) |
| External evidence over self-critique; verbatim failure memory | Reflexion (arXiv:2303.11366) |
| Meta-agent generating agents + archive as stepping stones | ADAS (arXiv:2408.08435) |
| Visible/held-out evidence split; hacking gap; more search amplifies gaming | SpecBench (arXiv:2605.21384) |
| Verifier = proxy for intent; scalability/faithfulness/robustness trade-off; hacking-behavior taxonomy; verifier–generator co-evolution | The Verification Horizon (arXiv:2606.26300) |
| Combine weak verifiers; form × granularity × source taxonomy; routing as open problem | Verifier Engineering (arXiv:2411.11504) |
| Oracle families beyond ground truth: differential, metamorphic, judgment | MR generation survey (arXiv:2406.05397) |
| Tool creation = interface prediction → materialization → full-lifecycle validation; interface flaws amplify downstream; reusable assets over disposable scripts | Tool-Genesis (arXiv:2603.05578) |
| Maker/user separation — expensive intelligence makes the tool once, cheap execution reuses it | LATM (arXiv:2305.17126) |
