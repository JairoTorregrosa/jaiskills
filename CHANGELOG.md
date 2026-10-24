# Changelog

## 1.5.6 (2026-10-24): managed-agents-wizard explains the Session trace

- `scripts/trazas.py <session_id>`: the session as a timeline next to the Console. It shows each
  model request with its duration and tokens (new, from cache, written), each tool call with the
  permission that let it run and a short input and result, messages, confirmations, errors and the
  stop reason, plus a header with billed time against open time, cost against the cap, and cache
  use. The first time each event type appears, one Spanish line explains it. `--breve` and
  `--json` are available. It is read-only and free.
- `references/trazas.md` tells the agent to walk every test trace with the person and map each
  block to the ficha row that made it possible (tool and permission, Procedure, stop_reason). It
  then compares the run with the design and asks, with `AskUserQuestion`, for one change per run.
- `probar.py` uses `agents/<agent>/kickoff.md` when the spec has no `events`, and `"dry_run": true`
  appends "Dry run.", so the test and the Deployment share one kickoff. It also prints the
  `trazas.py` command after every run.
- Validated with a demo agent (`web-health`, Sonnet 5.5 `low`). Run 1 cost USD 0.02. Then one
  prompt line changed, the agent went to v2, and the next run cost USD 0.01; the prompt prefix was
  still in the cache.

## 1.5.5 (2026-10-24): managed-agents-wizard is event-agnostic

- Removed `references/taller.md` and every reference to a specific workshop (agenda times, credits
  QR, Claude Desktop setup, venue). The skill keeps the general path: design, one budgeted test
  Session, iterate with the Console trace, schedule; a smaller first version when time or a
  credential is short; clean-up with `AskUserQuestion` when the person is done. The learning mode
  is now called **Guiado**.
- States that `AskUserQuestion` is the wizard's tool in the coding agent, talking to the person who
  builds; it never goes into the Managed Agent's prompt, tools or kickoff.

## 1.5.4 (2026-10-24): managed-agents-wizard follows the workshop deck

- `references/taller.md`: the deck's agenda (Diseña 10:15, Prueba 10:45, Itera 11:10, Programa
  11:35) mapped to wizard steps, credits and Claude Desktop, the Console tab, a smaller first
  version when time runs out, and clean-up with `AskUserQuestion` (archiving an Agent archives
  its Deployments).
- Same story as the slides: `always_ask` in unattended runs is fine when a `session.status_idled`
  webhook answers it by rule; cost = tokens + USD 10 per 1,000 searches + USD 0.08 per
  session-hour running; `budget_reached` resumes only by raising the budget; cron jitter up to 9
  minutes, no backfill, auto-pause on unrecoverable errors; `networking` always explicit (API
  default is `unrestricted`); `allowed_hosts` also limits web tools; cloud sandbox specs.
- Preflight checks `uv` and `jq`; debugging keeps the Session open in the Console.

## 1.5.3 (2026-10-24): managed-agents-wizard starts with a message kickoff

- The default kickoff is `user.message`, with the "done" check in the system prompt's Goal. An
  outcome (`user.define_outcome` + rubric) is an explicit choice in `AskUserQuestion`, proposed
  after one or two runs show what a good result looks like: it adds a grader and up to
  `max_iterations` rounds, and a rubric written before real outputs tends to fail good work.
  Catalog designs, previews, the ficha and the test template follow the new default.

## 1.5.2 (2026-10-24): managed-agents-wizard shows the whole agent

- `references/ficha.md`: one card with every layer of the agent (model and effort, trigger,
  kickoff and rubric, cost cap, system prompt in full, tools, MCP tools, skills, environment and
  hosts, memory and its access, files, credentials, the human gate, what was left out), each with
  its exact value, the file it lives in, and the reason in this job. Shown before files are
  written, after every change, and in the final report; kept in the agent's README.
- Every choice, confirmation and go-ahead goes through `AskUserQuestion` with previews that show
  the exact value each option writes: the diagnosis playback, settled decisions (proposal first),
  a batch for the layers nobody asked about, the ficha, `ant apply`, and go-live. Plain text stays
  for open facts only. Up to 4 independent questions per call.

## 1.5.1 (2026-10-24): managed-agents-wizard diagnoses, then designs big

- `references/diagnostico.md`: five facts (trigger, input, output, action, cost of error) before
  any design; a table that turns a domain ("un agente financiero") into a first loop; what the
  agent may do alone; ambitious defaults (real source, gated real action, memory, trigger, rubric).
- `references/catalogo-ideas.md`: 13 families from 147 real answers to "¿Qué agente quieres
  construir?" (La Salle workshop registrations, no personal data), each with a full design.
- `references/skills.md`: find and vet published skills (Anthropic knowledge-work plugins, vendor
  skills, the skills.sh search API) before writing a custom one.
- `references/conectores.md`: table of official remote MCP servers probed on 2026-10-24, the
  OAuth-app prerequisites, and the HTTP fallback for services with none.
- `references/system-prompt.md`: prompt, custom tools and rubric designed as one contract, with
  rules from the current prompting guides for Opus, Sonnet and Haiku 5.5.
- `references/docs.md`: index of the official pages (prompting guides added); audit fixes from a prompt-audit pass.
- Fixes from two simulated workshop runs (a vague "Financiero" idea and a contractor-document
  auditor), each played to `ant apply --dry-run` with a role-played participant:
  - unattended runs never use `always_ask` or approval tools that wait; the gate is a draft in the
    agent's own space; catalog designs updated to match;
  - Gmail MCP cannot download attachments: statements enter through Drive or uploads; encrypted
    PDFs must arrive unlocked (`credenciales.md` § Inside the sandbox);
  - `vault_ids: [./vault.yaml]` and `{path, access}` memory resources resolve in one apply
    (checked with `--dry-run -v`); `ensamblar.py` now fails on a file without `file_id` or a
    placeholder left in `vault_ids`/`resources`;
  - patterns for N entities in one Deployment, late inputs over a run window, fixed uploads,
    reference data, third-party personal data, where the person reads the result;
  - step 1 starts from the registration answer; decisions the diagnosis settled become proposals;
    preflight reads org and token expiry; model advice keyed to the cost of an error; test budget
    USD 5 (Sonnet) to 20 (Opus `high`); workshop credits and the Claude Desktop setup in preflight.
- Third simulated run (Meta Ads agency, 9 clients): Meta MCP accepts a System User token as
  `static_bearer` (read-only by scope, verified in Meta's docs); prefer vendor bearer tokens over
  OAuth in a workshop; credentials load after the apply that creates the vault; `probar.py` mounts
  memory stores `read_only` unless the spec says otherwise; read-only reference data refreshed
  with `memories update`; `-v` prints `resources` as sensitive.

## 1.5.0 (2026-10-24): managed-agents-wizard

- New `models/managed-agents-wizard`: idea → Claude Managed Agents agent that runs on its own,
  debugging included. Explains Agent, Environment, Session, Deployment, vault, memory store and
  outcome at the step that needs each one; six illustrated AskUserQuestion decisions (trigger,
  kickoff, model, write permissions, subagents, network); system prompts in Simplified Technical
  English with a self-critique checklist; MCP connector search (vendor docs, then the official MCP
  Registry); vault credentials loaded with `read -rs` so secrets never reach the chat.
- Every agent is one folder with one concern per file (`model.yaml`, `system_prompt.md`,
  `tools.yaml`, `mcp.yaml`, `skills.yaml`, `environment.yaml`, `schedule.yaml`, `kickoff.md`,
  `rubric.md`, `files.yaml`, `memory/`, `tests/`); `scripts/ensamblar.py` builds the `agent.md`
  and `deployment-*.yaml` that `ant apply` reads (`--check` for CI). Templates carry a `.tmpl`
  suffix so `ant apply` never picks them up.
- `scripts/probar.py` runs one capped test session (denies paused calls, answers custom tools from
  fixtures, downloads only real outputs); `scripts/inspeccionar.py` reports why a session stopped,
  what failed, what was denied and what it cost. `references/debugging.md` maps each symptom to its
  fix. Archetypes, costs and gotchas come from 11 agents and 13 test sessions run on 2026-10-24.

## 1.4.0 (2026-10-02): askcodex 0.3.0, a tool for the agent calling it

- `askcodex` re-synced from askcodex v0.3.0 (JairoTorregrosa/askcodex#14, #15, #16) plus #17,
  whose extraction example now defines its fields and null policy: `--schema FILE` for answers to parse (strict rules, `.result.json`, re-checked
  locally), `--verbosity`, `image create|edit --background transparent|opaque` with the saved
  file's real `width`, `height` and `alpha_channel`, `models --no-refresh` for a short listing
  (the raw backend response is now opt-in with `--backend`), and a table from `error.backend` to
  the next step (`invalid_json_schema`, unsupported effort or model, policy blocks such as
  `cyber_policy`, `incomplete_details`, rate limits). The Luna batch examples use `--schema`.
- `second-opinion`: `ask_codex.sh -o DIR < DIR/prompt.md` no longer truncates the prompt before
  reading it (stdin is copied first, then moved into place).
- `scripts/sync-askcodex.py` replaces the manual rsync-and-patch re-sync of the askcodex mirror. It
  refuses a dirty `skill/`, reports the synced commit and `git describe`, and exits 1 before
  touching anything when the upstream wording its delta replaces has moved.

## 1.3.0 (2026-10-02): askcodex 0.2.0 release and GPT-6.1 Sol

- `askcodex` re-synced from the released askcodex v0.2.0 (JairoTorregrosa/askcodex#13): Codex
  0.160.0 brought `gpt-6.1-sol`, now the CLI default and the "Most work" row; new
  `model-gpt-6.1-sol.md` (efforts, `none` rejected, proceed line with the missing-evidence
  carve-out, Free/Go conflict); `gpt-6-sol` marked previous generation; the GPT-5.5 migration
  points to `gpt-6.1-sol`. The catalog hides a model below the client version that knows it even
  when its `minimal_client_version` is lower, so the skill trusts the live catalog over its list.

## 1.2.0 (2026-09-27): askcodex for GPT-6

- `askcodex` re-synced from askcodex 0.2.0 (JairoTorregrosa/askcodex#3 to #12): the CLI now lists the
  GPT-6 models (its old `client_version` hid them), defaults to `gpt-6-sol`, and drops the
  `ultra` effort the backend rejects. New references: one prompting guide per model
  (`model-gpt-6-astra.md`, `-sol`, `-luna`, `model-gpt-5.6-sol.md`, `-terra`, `-luna`,
  `model-gpt-daybreak-blue-latest.md`, `model-gpt-5.5.md`, `model-gpt-image-2.md`), sourced to
  OpenAI docs and live probes dated 2026-09-27. Image guidance corrected: the prompt sets the
  aspect and can get a transparent background.
- The mirror's English triggers and background-job wording are now upstream; the only local delta
  is the not-for clause pointing to second-opinion.
- AGENTS.md: skills and references are written the way you brief a subagent.

## 1.1.0 (2026-09-27): GPT as advisor and adversarial reviewer

- `second-opinion` gains two modes. **review** runs Codex's built-in reviewer (`codex exec review`
  on `uncommitted`, `base:<ref>` or `commit:<sha>`). **adversarial** tries to break confidence in a
  change with [references/adversarial-prompt.md](skills/orchestration/second-opinion/references/adversarial-prompt.md)
  and a forced JSON schema (verdict ship/needs-attention/no-ship, findings with scenario, evidence,
  file:line range, confidence); one run or 2-3 parallel lenses (correctness and data, security and
  boundaries, failure and concurrency, design assumptions); Claude verifies every finding
  (confirmed / plausible / rejected) and recomputes the verdict from confirmed findings only.
  Procedure in `references/adversarial.md`. Tested on gpt-6-astra: native review 28 s,
  two parallel adversarial lenses 44-51 s, end-to-end via `/jaiskills:second-opinion adversarial` 142 s.
- Codex advises, reviews and judges; it never implements. `ask_codex.sh` forces read-only on every
  path (the user's Codex config may set `danger-full-access`), and closes the ways around the
  sandbox: `--ignore-rules` (an execpolicy allow rule like `bash -ic` runs unsandboxed),
  `--disable hooks` + `notify=[]` + `CMUX_CODEX_HOOKS_DISABLED=1` (hooks run outside the sandbox),
  `review_model` pinned for native review (it outranks `-m`). It disables Codex memories, defaults
  the model to `gpt-6-astra` when Codex's catalog lists it (`SECOND_OPINION_MODEL`, `-m`) and the
  effort to `high` (`SECOND_OPINION_EFFORT`, `-e`; configs may default to `low`), adds `--review`,
  and retries once when parallel runs lose the `~/.codex` SQLite lock race.
- Follow-ups resume by explicit session id (`--resume last` races with parallel runs).
- Dogfooded: two adversarial gpt-6-astra passes over this change found the rules, hooks,
  review-target and review_model gaps above; all fixed and re-tested.
- AGENTS.md: Codex never implements in second-opinion, insistir or goal-loop; `mcp-server` was
  removed from codex-cli in 0.154.

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
