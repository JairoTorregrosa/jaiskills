# Changelog

## 0.3.0 (2026-07-12)

- **goal-loop becomes a software factory**: new Phase 0.5 (observability plan + dynamic instrument generation) grounded in a second literature deep-dive (The Verification Horizon arXiv:2606.26300, Verifier Engineering arXiv:2411.11504, Tool-Genesis arXiv:2603.05578, LATM arXiv:2305.17126, metamorphic-testing surveys):
  - New `references/factory-framework.md` — high-level framework: observable space, capability gap analysis, acquisition ladder (reuse → configure → compose → generate → escalate), interface-first instrument lifecycle, red-first calibration, registry/routing, maker/user separation, verifier–generator co-evolution, compounding libraries.
  - New `references/instrument-catalog.md` — problem-class → instrument routing table plus three planes: classic OSS stacks (from awesome-* repos and Better Stack guides, mid-2026), agent-native instruments (steipete-pattern sensors/actuators design grammar), and 2026 verifier constructions (rubric + interactive agentic judges, behavior monitors, held-out splits).
  - SKILL.md: loss calibration (evidence must fail red-first before epoch 1), evidence-dispute protocol (verifier owns evidence fixes), one-shottable-goal gate, `loops/<slug>/tools/` output, judge upgraded to the 7-behavior hacking taxonomy + declared-blind-spot probing.
  - New `SPEC.md` — formal contract: definitions, artifact schemas, phase pre/postconditions, 7 invariants (leak, red-first calibration, fresh implementer, oracle integrity, plateau stop, judge independence, verbatim failure log), conformance checks, and known limitations.

## 0.2.0 (2026-07-12)

- **goal-loop rewritten from scratch** as loop engineering = gradient descent, built by an agent factory. Literature-grounded redesign (TextGrad 2406.07496, ProTeGi 2305.03495, SkillGrad 2605.27760, ADAS 2408.08435, SpecBench 2605.21384):
  - **Agent factory phase**: generates goal-specialized implementer/verifier/diagnoser/judge prompts into `loops/<slug>/agents/`, seeded by a cross-goal `loops/archive.md` (ADAS stepping stones).
  - **Backward pass**: a diagnoser converts failures into textual gradients and newly-passing checks into contrastive preserve-this signal; a momentum section accumulates recurring patterns across epochs.
  - **Visible/held-out evidence split**: implementer optimizes visible validation only; the judge runs hidden compositional checks and reports the hacking gap (SpecBench: agents saturate visible tests while failing composition).
  - **Adaptive learning rate + early stopping**: plateau shrinks edit scope, `--patience` (default 2) stops non-monotonic loops; flags now `--max-epochs`/`--patience`/`--judge`.
  - Replaced `references/goal-template.md` with `references/loop-template.md` and `references/factory-templates.md`.

## 0.1.0 (2026-07-12)

- Initial release: **jaiskills** — Jairo's collection of Claude Code agent skills and plugins.
- **Plugin** `insistir` (Insistir Sin Desistir — Agents Checking Agents): multi-agent orchestration with cross-validation using Claude Code Agent Teams. Includes cross-provider Codex/GPT-5 judge, `/insistir:advisor` second opinions, goal loop (loop engineering), knowledge compounding (`docs/solutions/`), file-based TODO lifecycle, and plan deepening with parallel research agents.
