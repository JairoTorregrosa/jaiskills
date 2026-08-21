# The Software Factory — dynamic generation of agents and instruments per problem

High-level framework. Deliberately abstract: no tool names, no domain examples — those live in
[instrument-catalog.md](instrument-catalog.md) as replaceable instance data.

## Core thesis

A goal is not solved by an agent; it is solved by a **production system generated for that goal**.
The factory takes a goal and generates three artifact classes, all specified, all verified, all archived:

1. **Contracts** — what "done" means, expressed as observables (the loss function and its splits).
2. **Instruments** — the sensors and actuators through which those observables can be measured.
3. **Agents** — the roles that produce, diagnose, and judge work, specialized to the goal.

Everything the factory emits is the same kind of thing: an artifact with an interface, an
implementation, and a validation. The factory applies its own discipline to itself.

## Beyond QA: the sensorium framing

This is not quality assurance. QA verifies artifacts at a gate; this framework builds systems
that **perceive whether they are fulfilling an intent**. The inversion driving it: generation
has become cheap; *knowing that something works* is now the expensive, scarce resource
(the verification-horizon inversion). Consequences:

- **No artifact is born without its measurement apparatus.** The factory's unit of output is
  not "code + tests" but an organism: artifact + sensorium + regeneration capability. When the
  goal is met, the loop does not end — it becomes the runtime. The same cycle that converged
  development (sense → error → diagnose → correct) maintains homeostasis in production.
  Vocabulary: setpoint = intent, sensors = instruments, controller = diagnoser,
  actuator = implementer. Control theory, not inspection.
- **The sensorium defends against an adversary, not against mistakes.** Classic suites protect
  against human error — a static threat. Here the producer is an optimizer that grows stronger
  and flows toward blind spots (Goodhart under pressure). Measurement must therefore be
  adversarial, diverse, and co-evolving, or it decays into theater.
- **Measurement capability is the accumulating capital.** Artifacts are exhaust; the durable
  output is the registry of calibrated instruments, hunted gaming taxonomies, and proven
  oracles. Each loop lowers the cost of trusting the next one. The factory does not produce
  software; it produces verified trust, and the software comes with it.
- **The artifact's consumers are agents too.** Verification must cover the agentic surface,
  not only the human one: can an agent interrogate the artifact and extract correct answers?
  Is the ground truth exposed in a machine-interrogable form? The interrogator instrument and
  the future user are the same entity — measure with what will consume.

## The learning isomorphism

The framework is structurally isomorphic to neural-network training with the differentiable
substrate replaced by language: parameters = artifact · dataset curation = contract/oracle
engineering (label errors = evidence bugs) · data augmentation = metamorphic relations ·
train loss = visible evidence · test set = held-out · generalization gap = hacking gap ·
shortcut learning = reward hacking · backprop = textual gradients · momentum/LR/early
stopping/curriculum/transfer = momentum table/edit scope/patience/decomposition/libraries.

Where it breaks — and why the design compensates:
1. Gradients are semantic hypotheses, not derivatives (no descent guarantee → early stopping mandatory).
2. Parameter space is discrete/structural (no convergence theorems → verbatim failure memory + explicit momentum).
3. **The optimizer is intelligent and adversarial** — SGD does not conspire against its loss;
   an agent does. The ecosystem framing is therefore GAN, not supervised learning: the
   discriminator (judge + sensorium) must improve at the generator's pace or collapse.

Practical payoff: forty years of named pathologies→remedies transfer. When the loop misbehaves,
ask "what is the deep-learning equivalent?" — overfitting→more held-out/OOD, label noise→clean
the evidence, plateau→LR schedule/curriculum, benchmark saturation→build the next benchmark.

## 1. Observable space

Every goal induces a set of observables O = {o₁…oₙ}: the behaviors, properties, and side-effects
that must be *seen* for completion to be believable. Verification design is a **coverage problem**:
each observable needs at least one instrument whose field of view contains it.

- An observable with no instrument is a **blind spot**. Failures and reward hacking concentrate
  in blind spots, because optimization pressure flows toward whatever the instruments cannot see.
- An instrument never observes the goal; it observes a **projection** of the goal. Combining
  instruments with different projections (execution, structure, runtime behavior, judgment) is
  the only way to approximate coverage — no single instrument family achieves scalability,
  faithfulness, and robustness simultaneously.

**Factory step:** enumerate O explicitly at intake, before any work. The unenumerated observable
is the one that ships broken.

## 2. Capability gap analysis

Diff the required observables (and required actuations — things the loop must *do* to exercise
the system) against the current instrument inventory:

```
gap = observables(goal) ∪ actuations(goal) − field_of_view(inventory)
```

The gap list, not habit or availability, drives instrument acquisition. Inventory includes
everything already in the environment: test frameworks, CI, CLIs, services, prior factory output.

## 3. The acquisition ladder

Acquire instruments in strict cost order — descend a rung only when the one above fails:

1. **Reuse** — an existing instrument already covers the observable.
2. **Configure/adapt** — an existing instrument covers it after parametrization or a thin wrapper.
3. **Compose** — a pipeline of existing instruments covers it (output of one is input to another).
4. **Generate** — synthesize a new instrument (see §4). Last resort by design: one-shot tool
   creation is empirically error-prone, and interface flaws amplify through everything built on them.
5. **Escalate** — no instrument can cover the observable; a human must observe it, or the
   contract must be renegotiated to observables that can be covered.

**Amortization rule:** generate a persistent instrument when expected reuses × per-use saving
exceeds creation + calibration cost; otherwise a disposable inline check is correct. Disposable
checks used more than once across epochs must be promoted to verified assets.

## 4. Instrument lifecycle (generation path)

Tool creation decomposes into two phases with separate failure modes — keep them separate so
errors are attributable:

1. **Interface prediction** — from the abstract requirement, infer the *contract*: name, typed
   parameters with constraints, semantics, output form (binary / score / text evidence),
   granularity (step / trajectory), and declared blind spots. The contract is machine-checkable
   and exists before any implementation.
2. **Materialization** — implement against the contract. Grammar: single purpose; structured
   output; deterministic where possible (seeded, mockable); exit status = verdict,
   output = evidence; side-effect-free observation or explicitly declared actuation.
3. **Validation** — the instrument is itself an implementation and gets the full treatment:
   positive cases, **negative and boundary cases**, and calibration (§5). An unvalidated
   instrument is a rumor.
4. **Registration** — enter it in the registry with metadata: what it observes, form,
   granularity, source (program-based vs model-based), cost per run, blind spots,
   calibration status, provenance.
5. **Maintenance** — instruments drift as the system evolves; a failing instrument is repaired
   or deprecated through the same lifecycle, never patched around.

## 5. Calibration — who verifies the verifier

An instrument earns trust only by demonstrating discrimination:

- **Red**: it must FAIL against the pre-implementation state or a known-bad sample.
- **Green**: it must PASS against a known-good sample or reference, where one exists.
- An instrument that cannot be made to fail measures nothing; an instrument that cannot pass
  its reference is broken. Both are label bugs waiting to poison the loss.

Calibration is the ground-truth discipline: curating (input, expected) pairs for the instrument
is dataset curation, and label errors there corrupt everything downstream.

## 6. Registry and routing

The registry is the factory's memory of measurement capability. Routing is matching:
observables → registry entries, by metadata — never by familiarity. Conflicts between
instruments (one passes, one fails) are resolved by source precedence: program-based
evidence outranks model-based judgment for anything a program can decide; model-based
judgment covers only what programs cannot express, and is itself audited (it is the most
gameable instrument class).

## 7. Maker/user separation

The intelligence that *makes* an instrument is spent once; the instrument then runs many times
at near-zero marginal intelligence. Route expensive capability to interface prediction and
validation; execution of a calibrated instrument is cheap and delegable. The same separation
applies to agents: the factory (maker) is the expensive step; the generated agents (users of
contracts and instruments) run repeatedly.

## 8. Co-evolution

A fixed verification stack goes stale as the producer strengthens: proxies saturate, gaming
appears, the proxy–intent gap widens under optimization pressure. Triggers for instrument
upgrade (climb the faithfulness ladder, accept higher cost):

- visible loss saturates while held-out or judged quality does not;
- the judge detects gaming (a blind spot was found — instrument the blind spot);
- the same defect class escapes to a later stage twice (the earlier stage lacks an instrument).

Verification is not a phase; it is infrastructure that must be rebuilt as the system it
measures improves.

## 9. Compounding

The factory keeps three libraries, each consumed at intake and fed at close:

| Library | Contains | Compounds into |
|---|---|---|
| Solutions | problems solved, root causes, preventions | better contracts |
| Agent designs | role prompts that worked, per domain | better agents |
| Instruments | calibrated tools + registry metadata | better observability, cheaper loops |

This is what distinguishes a factory from a workshop: assets accumulate, and the marginal cost
of observing — and therefore achieving — the next goal decreases.

## Mapping to the goal loop

| Loop phase | Factory activity |
|---|---|
| Intake | Enumerate observables; contract = observables + splits |
| Phase 0.5 | Gap analysis → acquisition ladder → calibration → registry |
| Factory | Generate agents *and* instruments, seeded from the libraries |
| Descent | Agents act; instruments measure; conflicts resolved by source precedence |
| Judge | Runs the held-out projection; hunts the blind spots the registry declares |
| Close | Promote assets; record instrument upgrades; feed the three libraries |
