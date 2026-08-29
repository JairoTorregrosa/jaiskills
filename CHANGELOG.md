# Changelog

## 0.2.0 (2026-08-29) — new skill `agent-sdk-wizard` (agents)

- **New category `agents/`** — skills for building agents. First tenant:
  `skills/agents/agent-sdk-wizard`.
- **`agent-sdk-wizard`** asks **nine questions, one `AskUserQuestion` per step**, in this order:
  language → goal → model → instructions → tools/MCP → skills → subagents → permissions → hooks.
  Every option carries an **ASCII diagram in its `preview`** showing how the agent changes if you
  pick it, in plain language for someone who has never seen an agent. The recommended option
  comes first, so accepting all nine defaults yields a working agent in about two minutes.
- **What it generates**: a directory with `agente.py` (uv) or `agente.ts` (tsx) whose whole
  configuration is one visible block, every line annotated `# paso N: …`; the manifest; a stream
  reader that prints text, `🔧 tool(arg)`, tool errors and the `result` with turns and cost; a
  plain-language `README.md` with the loop drawn from the actual nine decisions and a
  step → line-of-code table; and a `decisiones.md` linking each answer to the public docs.
  `max_turns` and `max_budget_usd` are **always** set — no generated agent ships without both.
- **It is not done until the agent runs.** The wizard installs, runs once with the archetype's
  test prompt, shows the `result`, and repairs failures against `references/errores.md` before
  reporting done.
- **Verified against** TypeScript SDK 0.3.251, Python SDK 0.2.148 (bundling Claude Code 2.1.251),
  and the model prices published 2026-08-29. Every API name in the skill comes from
  `references/opciones-sdk.md`, including the traps that bite silently: `AgentDefinition` and hook
  return values are camelCase **in Python too**, `Stop` ignores matchers, `allowed_tools` approves
  but does not restrict, and Python's `can_use_tool` needs streaming input plus an empty
  `PreToolUse` hook.
- **New command `/agent-wizard [what the agent should do]`** — runs the wizard, using the
  argument as the proposal for step 2.
- Self-contained: five reference files (`previews`, `arquetipos`, `opciones-sdk`, `errores`,
  `glosario`) and ten templates ship inside the skill. No machine-specific paths, no runtime
  dependency on anything outside the plugin.

## 0.1.0 (2026-08-21) — single-plugin reset

- **BREAKING: one plugin instead of four.** The marketplace no longer publishes `insistir`, `metaprompt`, `constatar`, and `remoto` separately — everything ships as the single `jaiskills` plugin. Migration: uninstall the old plugins and `/plugin install jaiskills@jaiskills`. Command names are now flat and prefixed where they collided: `/constatar-run`, `/constatar-verify`, `/constatar-audit`, `/remoto-run`, `/remoto-status`; insistir's commands (`/advisor`, `/compound`, `/goal`, `/triage`, `/resolve-todos`, `/deepen-plan`) and `/metaprompt` keep their names.
- **Layout: `skills/<category>/<skill>/`** (orchestration, prompting, knowledge, openai), with plugin-level `commands/`, `agents/`, `hooks/`, `scripts/`, `references/` at the root — structure inspired by [mattpocock/skills](https://github.com/mattpocock/skills).
- **New skill `askcodex`** (openai): OpenAI GPT-5.x and image models as a CLI — one-shot text, image create/edit, models, quota. Canonical copy lives in the [askcodex repo](https://github.com/JairoTorregrosa/askcodex); this one tracks it.
- **New skill `image-to-frontend`** (openai): reference image or brief → 4 visual variants → build spec → working React/HTML page, iterated to pixel-close. Rewritten to drive image generation through the askcodex CLI instead of the Codex MCP server.
- README rewritten around the failure modes each skill fixes.

## 0.4.2 (2026-07-18)

- **metaprompt 0.3.0 — four new harness deep-dive guides** (pi, Amp, eve, Vercel AI Gateway), each researched against live docs on 2026-07-18 with per-section `Source:` URLs:
  - `references/pi-harness.md` — minimal harness (4 tools, no MCP, no permission rails, `.pi/SYSTEM.md` full system-prompt replacement); subscription auth via `/login` OAuth — ChatGPT sub is OpenAI-endorsed; Claude sub bills per-token "extra usage" since April 2026.
  - `references/amp-harness.md` — threads/orbs/subagents, mode-based multi-model routing (low/medium/high/ultra — write prompts model-agnostically), full-auto default permissions, BYOK removed; ChatGPT sub linkable at `/settings/model-providers`, Claude sub linking thinly documented.
  - `references/eve-harness.md` — Vercel's agent framework ("an agent is a directory", `agent/instructions.md` as system prompt); no consumer-subscription path — API keys or AI Gateway only.
  - `references/ai-gateway-harness.md` — model slugs, routing/fallback/BYOK, per-agent backend config; Claude Max pass-through works only with Claude Code as client and is fragile + ToS gray area; no ChatGPT pass-through.
  - SKILL.md: harness routing table extended with the four harnesses plus a subscription-auth quick-reference matrix (never recommend token-sharing workarounds — Anthropic ToS Feb 2026, enforced April 2026).

## 0.4.1 (2026-07-16)

- **remoto 0.2.0 — harness-agnostic engine/role policy**: Codex is always driven headless (`codex exec`, prompt on stdin — never the Codex MCP server), symmetric with `claude -p`; role (implementer/reviewer/judge) is orthogonal to engine.
  - Role matrix in the skill: orchestrator always Fable 5 (the local session); default implementer and judge codex `gpt-5.6-sol` at high reasoning; reviewer always the engine that did not author the work.
  - `remoto.sh spawn` gains `-r/--effort low|medium|high|xhigh` → Codex `model_reasoning_effort` (codex-only, rejected for claude); effort recorded in job `meta.env`.
  - New judge template in `prompt-templates.md` (scores goal fidelity, review rigor, fix completeness, evidence quality → PASS/FAIL) plus a universal no-background-remnants rule for headless workers (background children die with the process).

## 0.4.0 (2026-07-16)

- **New plugin `remoto`** (Remote Agent Orchestration over SSH): spawn and manage headless `claude -p` / `codex exec` workers on a remote host (Jetson) from the local Claude Code session.
  - `scripts/remoto.sh` — file-based job runner over SSH: `hosts`, `spawn` (nohup/setsid, per-job dir under `~/.remoto/jobs/`), `ls`, `status`, `wait`, `logs`, `result` (parses claude stream-json / codex last-message), `kill` (process group), `push`/`pull` (rsync), `clean`.
  - `remote-agents` skill — orchestration playbook: probe → prepare workspace → self-contained prompts → parallel spawn → background wait → collect → cross-provider cross-review (claude work reviewed by codex and vice versa).
  - `references/prompt-templates.md` — metaprompt-engineered worker/reviewer/fixer templates (Claude: XML structuring, default-to-action, grounded claims; Codex/GPT-5: contradiction-free hard requirements, persistence) sharing a machine-collectable REPORT contract.
  - Commands `/remoto:run` and `/remoto:status`.

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
