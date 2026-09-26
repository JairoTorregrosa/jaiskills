# Changelog

## 1.0.0 (2026-09-26): the catalog

The repo becomes a catalog of Jairo's personal skills: `README.md` is the human catalog (what each
skill does, what he uses it for); every other file is written for coding agents. Layout and rules
modeled on mattpocock/skills (promoted set = plugin = README, user- vs model-invoked,
`agents/openai.yaml`) and owersbrett/potato-skills (skills compose into paths, the tree is the
catalog). The pre-catalog layout is tagged `v0.3.0`.

**Breaking**

- **Skills are the slash commands; `commands/` is gone.** Folded: `/advisor` → `second-opinion`
  (advise mode), `/agent-wizard` → `agent-sdk-wizard`, `/compound` → `compound-knowledge`,
  `/deepen-plan` → `insistir` `references/deepen-plan.md`, `/goal` → `goal-loop`, `/metaprompt` →
  `metaprompt`, `/remoto-run` + `/remoto-status` → `remote-agents`, `/triage` + `/resolve-todos` →
  `file-todos` (`references/triage.md`, `references/resolve.md`). Invoke as `/jaiskills:<skill>`.
- **Removed `constatar-plan`, `constatar-verify`, `/constatar-*`, `references/constatar/`**: the
  engine is private and no longer maintained.
- **`codex-judge` → `second-opinion`**, model-invoked, two modes: `advise` (independent read on a
  plan/diff/question, follow-ups via `--resume`) and `judge` (verdict JSON forced by
  `references/verdict.schema.json`; bands auto-approve = APPROVED, ≥ 4.0, no critical or major; auto-revise < 2.5 or
  any critical or major finding (major = unmet acceptance criterion), middle → reviewer breaks the
  tie). Codex runs through `scripts/ask_codex.sh` (default timeout 540 s, under the 600 s agent Bash cap) =
  headless `codex exec --sandbox read-only --ephemeral`; missing/logged-out/timed-out Codex (exit
  3/4/5) falls back to a fresh Claude subagent labelled "same-provider fallback". Schema-forced
  verdicts whose evidence lacks file:line are rejected and rerun once (a forced schema answers even
  an empty prompt with a vacuous APPROVED).
- **The plugin no longer bundles the Codex MCP server** (`.mcp.json` removed): installing
  jaiskills no longer starts `codex mcp-server` in every session.
- **Buckets by use:** `creative/` (motion-design, image-to-frontend), `orchestration/` (insistir,
  goal-loop, second-opinion, remote-agents), `models/` (agent-sdk-wizard, metaprompt, askcodex),
  `knowledge/` (compound-knowledge, file-todos). `openai/`, `prompting/`, `agents/` buckets removed.

**Skills**

- `insistir`: user-invoked (`disable-model-invocation`). Rewritten for Claude Code's implicit
  team (TeamCreate/TeamDelete were removed in 2.1.178, which had left the completion gate unable to
  fire): team mode (needs `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, interactive; Agent `name` +
  `subagent_type`) or subagent mode (teams off or `claude -p`). Run state keyed on
  `${CLAUDE_SESSION_ID}` (`~/.claude/insistir-state/<session>/`: `run.json`, `allowed_commands.txt`,
  `<key>.approved`); the TaskCompleted hook acts only when that dir exists. Reviewer Bash filter
  blocks `--fix`/`--write`/`-w`/`--allow-dirty` and `git branch` mutation, and no longer blocks
  other sessions on malformed input. Judge via `second-opinion` (args start with `judge`, decide by
  band, every judge finding in the summary). TODOs filed also when the round budget runs out;
  applied ones closed with the fixer's SHA. Workers commit `-- <paths>`. SKILL.md 506 → ~250 lines;
  new references `spawn-prompts.md`, `crew-fallback.md` (general-purpose crew for skills.sh
  installs), `edge-cases.md`, `deepen-plan.md`. Hook scripts moved into the skill.
- `goal-loop`: user-invoked; `SPEC.md` → `references/spec.md`; judge via `second-opinion` with the
  implementer kept blind to held-out checks.
- `remote-agents`: `remoto.sh` lives in the skill; the judge is the engine that did not write the
  work; host is `REMOTO_HOST` (default `jetson`),
  `REMOTO_FALLBACK_HOST`, `REMOTO_HOSTS`; `--help` exits 0; unreachable host reported as such;
  `spawn --safe` for Codex fixed (`--full-auto` no longer exists in codex-cli 0.156 → `--sandbox
  workspace-write`); hard-coded model names removed.
- `file-todos`, `compound-knowledge`: commands folded in; fallbacks when plugin agents or subagents
  are missing; resolve workers commit `-- <paths>`; credit EveryInc's compound-engineering plugin.
- `askcodex`: synced with the canonical skill in the askcodex repo (v0.1.0: prompting-text,
  prompting-images, transcription references), plus a not-for clause pointing critique requests at
  second-opinion (delta to port upstream).
- `metaprompt`: Claude lineup updated to Fable 5.1, Opus 5.5, Sonnet 5, Haiku 4.5 (checked against
  the live docs 2026-09-26); July sections labelled legacy.
- `agent-sdk-wizard`: model options Opus 5.5 ($4/$20) and Fable 5.1 ($10/$50) replace Opus 5 and
  Fable 5; argument becomes the step-2 proposal.
- `image-to-frontend`: moved to `creative/`; description rewritten; image steps call the `askcodex`
  skill instead of duplicating its flags; leftover deploy and MCP-era details removed.
- Every skill has `agents/openai.yaml`; no per-skill `version` fields.

**Repo**

- `AGENTS.md`: layout, invariants, how to write/add/release a skill (keeps the Code Review Rules);
  `.claude/CLAUDE.md` imports it (a root `CLAUDE.md` fails `claude plugin validate --strict`).
- `scripts/check.py` (catalog lint), `scripts/link-skills.sh` (symlink skills into
  `~/.claude/skills` and `~/.agents/skills`; `--force` moves a real dir to `skills-backup/`),
  `.github/workflows/check.yml` (lint, py_compile, shellcheck).
- Removed dev leftovers: root plan files, `goals/`, `todos/`, `docs/solutions/`, `docs/skills.md`.

## 0.3.0 (2026-09-26) — new skill `motion-design` (creative)

- **New category `creative/`**. First tenant: `skills/creative/motion-design`, the video
  counterpart of Anthropic's `frontend-design` skill. Its Definition of Done is the **pride test**:
  a video the person would post under their own name today, not one that merely renders.
- **Runs a production as a studio crew.** Every piece opens an `ORCHESTRATION.md` ledger (brief,
  definition of done, locked direction, crew and phase gates, beat sheet, sources, decisions,
  findings, render log, delivery) and fans divergent work out to parallel subagents: a writers'
  room with blind critics, style frames, music takes, one animator per scene on a frozen engine,
  and critique lenses checked by a skeptical verifier. Crew prompts and a scoring rubric ship as
  templates. It decides and reports instead of parking a run on a question.
- **Taste, written down.** Craft rules in frames and numbers (easing tokens, spring conversions,
  reading time, type floors at phone size, safe zones, beat math), a calibrated list of AI-slop
  tells in motion, the notes humans actually gave on past productions (no narrative UI, no
  transition menus, no fabricated ambience beds, native copy never translated), director's notes
  for pushing a cut, and tested one-line prompts that got people to share.
- **Stack references verified 2026-09-26**: HTML/GSAP/HyperFrames with a seek-and-screenshot
  renderer, Remotion 4.0.529 (license, official agent skills, determinism, rendering flags),
  p5.js 2 + p5.brush for the hand-drawn look, three.js r186 / WebGPU + TSL / Blender 5.2 headless,
  audio (ElevenLabs music plans in whole bars, TTS with timestamps, local ACE-Step and Qwen3-TTS,
  alignment, mixing), delivery specs per platform, and a radar of newer libraries with the
  commands to re-scan the awesome lists.
- **Ten tested scripts**: `render_frames.py` (deterministic HTML → MP4, BT.709-tagged),
  `contact_sheet.py`, `video_gates.py` (format, faststart, loudness, poster frame, frozen runs,
  periodic audio wobble, cuts vs the beat grid), `audio_check.py` (meter-driven −14 LUFS / −1.5 dBTP
  master), `beats.py`, `captions.py`, `sfx.py`, `poster_frame.py`, `export_social.py` (feed export,
  WhatsApp review copy under 180 MB, ProRes) and `blender_mg_render.py`. The gates were validated
  against past productions and caught real defects in them (true peak over −1 dBTP after AAC,
  full-range BT.601 tags, 4:4:4 exports, black first frames).
- Self-contained and portable: no machine paths, no keys, dependencies declared inline for `uv run`.

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

## Before the single-plugin reset: four plugins (July 2026)

Version numbers below belong to the old multi-plugin marketplace and restart at 0.1.0 above.

### Marketplace 0.4.2 (2026-07-18)

- **metaprompt 0.3.0 — four new harness deep-dive guides** (pi, Amp, eve, Vercel AI Gateway), each researched against live docs on 2026-07-18 with per-section `Source:` URLs:
  - `references/pi-harness.md` — minimal harness (4 tools, no MCP, no permission rails, `.pi/SYSTEM.md` full system-prompt replacement); subscription auth via `/login` OAuth — ChatGPT sub is OpenAI-endorsed; Claude sub bills per-token "extra usage" since April 2026.
  - `references/amp-harness.md` — threads/orbs/subagents, mode-based multi-model routing (low/medium/high/ultra — write prompts model-agnostically), full-auto default permissions, BYOK removed; ChatGPT sub linkable at `/settings/model-providers`, Claude sub linking thinly documented.
  - `references/eve-harness.md` — Vercel's agent framework ("an agent is a directory", `agent/instructions.md` as system prompt); no consumer-subscription path — API keys or AI Gateway only.
  - `references/ai-gateway-harness.md` — model slugs, routing/fallback/BYOK, per-agent backend config; Claude Max pass-through works only with Claude Code as client and is fragile + ToS gray area; no ChatGPT pass-through.
  - SKILL.md: harness routing table extended with the four harnesses plus a subscription-auth quick-reference matrix (never recommend token-sharing workarounds — Anthropic ToS Feb 2026, enforced April 2026).

### Marketplace 0.4.1 (2026-07-16)

- **remoto 0.2.0 — harness-agnostic engine/role policy**: Codex is always driven headless (`codex exec`, prompt on stdin — never the Codex MCP server), symmetric with `claude -p`; role (implementer/reviewer/judge) is orthogonal to engine.
  - Role matrix in the skill: orchestrator always Fable 5 (the local session); default implementer and judge codex `gpt-5.6-sol` at high reasoning; reviewer always the engine that did not author the work.
  - `remoto.sh spawn` gains `-r/--effort low|medium|high|xhigh` → Codex `model_reasoning_effort` (codex-only, rejected for claude); effort recorded in job `meta.env`.
  - New judge template in `prompt-templates.md` (scores goal fidelity, review rigor, fix completeness, evidence quality → PASS/FAIL) plus a universal no-background-remnants rule for headless workers (background children die with the process).

### Marketplace 0.4.0 (2026-07-16)

- **New plugin `remoto`** (Remote Agent Orchestration over SSH): spawn and manage headless `claude -p` / `codex exec` workers on a remote host (Jetson) from the local Claude Code session.
  - `scripts/remoto.sh` — file-based job runner over SSH: `hosts`, `spawn` (nohup/setsid, per-job dir under `~/.remoto/jobs/`), `ls`, `status`, `wait`, `logs`, `result` (parses claude stream-json / codex last-message), `kill` (process group), `push`/`pull` (rsync), `clean`.
  - `remote-agents` skill — orchestration playbook: probe → prepare workspace → self-contained prompts → parallel spawn → background wait → collect → cross-provider cross-review (claude work reviewed by codex and vice versa).
  - `references/prompt-templates.md` — metaprompt-engineered worker/reviewer/fixer templates (Claude: XML structuring, default-to-action, grounded claims; Codex/GPT-5: contradiction-free hard requirements, persistence) sharing a machine-collectable REPORT contract.
  - Commands `/remoto:run` and `/remoto:status`.

### Marketplace 0.3.0 (2026-07-12)

- **goal-loop becomes a software factory**: new Phase 0.5 (observability plan + dynamic instrument generation) grounded in a second literature deep-dive (The Verification Horizon arXiv:2606.26300, Verifier Engineering arXiv:2411.11504, Tool-Genesis arXiv:2603.05578, LATM arXiv:2305.17126, metamorphic-testing surveys):
  - New `references/factory-framework.md` — high-level framework: observable space, capability gap analysis, acquisition ladder (reuse → configure → compose → generate → escalate), interface-first instrument lifecycle, red-first calibration, registry/routing, maker/user separation, verifier–generator co-evolution, compounding libraries.
  - New `references/instrument-catalog.md` — problem-class → instrument routing table plus three planes: classic OSS stacks (from awesome-* repos and Better Stack guides, mid-2026), agent-native instruments (steipete-pattern sensors/actuators design grammar), and 2026 verifier constructions (rubric + interactive agentic judges, behavior monitors, held-out splits).
  - SKILL.md: loss calibration (evidence must fail red-first before epoch 1), evidence-dispute protocol (verifier owns evidence fixes), one-shottable-goal gate, `loops/<slug>/tools/` output, judge upgraded to the 7-behavior hacking taxonomy + declared-blind-spot probing.
  - New `SPEC.md` — formal contract: definitions, artifact schemas, phase pre/postconditions, 7 invariants (leak, red-first calibration, fresh implementer, oracle integrity, plateau stop, judge independence, verbatim failure log), conformance checks, and known limitations.

### Marketplace 0.2.0 (2026-07-12)

- **goal-loop rewritten from scratch** as loop engineering = gradient descent, built by an agent factory. Literature-grounded redesign (TextGrad 2406.07496, ProTeGi 2305.03495, SkillGrad 2605.27760, ADAS 2408.08435, SpecBench 2605.21384):
  - **Agent factory phase**: generates goal-specialized implementer/verifier/diagnoser/judge prompts into `loops/<slug>/agents/`, seeded by a cross-goal `loops/archive.md` (ADAS stepping stones).
  - **Backward pass**: a diagnoser converts failures into textual gradients and newly-passing checks into contrastive preserve-this signal; a momentum section accumulates recurring patterns across epochs.
  - **Visible/held-out evidence split**: implementer optimizes visible validation only; the judge runs hidden compositional checks and reports the hacking gap (SpecBench: agents saturate visible tests while failing composition).
  - **Adaptive learning rate + early stopping**: plateau shrinks edit scope, `--patience` (default 2) stops non-monotonic loops; flags now `--max-epochs`/`--patience`/`--judge`.
  - Replaced `references/goal-template.md` with `references/loop-template.md` and `references/factory-templates.md`.

### Marketplace 0.1.0 (2026-07-12)

- Initial release: **jaiskills** — Jairo's collection of Claude Code agent skills and plugins.
- **Plugin** `insistir` (Insistir Sin Desistir — Agents Checking Agents): multi-agent orchestration with cross-validation using Claude Code Agent Teams. Includes cross-provider Codex/GPT-5 judge, `/insistir:advisor` second opinions, goal loop (loop engineering), knowledge compounding (`docs/solutions/`), file-based TODO lifecycle, and plan deepening with parallel research agents.
