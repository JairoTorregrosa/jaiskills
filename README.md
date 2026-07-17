# jaiskills

A collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) agent skills and plugins.

## insistir — Insistir Sin Desistir

A plugin for multi-agent orchestration with cross-validation. Every agent's work is reviewed by a different agent in an iterative adversarial loop, optionally judged by a cross-provider LLM (Codex/GPT-5). The name is the point: the pipeline insists — fix, review, judge — until the work is verified, never settling short.

## Install

1. Add the marketplace:

```
/plugin marketplace add JairoTorregrosa/jaiskills
```

2. Install the plugin:

```
/plugin install insistir@jaiskills
```

Or load locally for development:

```bash
claude --plugin-dir /path/to/insistir
```

## Usage

```
/insistir Build a REST API with auth, CRUD endpoints, and tests
```

The plugin orchestrates the full lifecycle:

```
Intake → Plan* → Create Team → [Execute Wave → Cross-Review Loop† → Judge‡] → Cleanup§

  * Optional: search past solutions, deepen plan with research agents
  † REVISE findings persisted as TODO files for lifecycle tracking
  ‡ Optional: Codex/GPT-5 cross-provider judge scores the review verdict
  § Optional: compound learnings into docs/solutions/
```

## How It Works

```
      ┌──────────────────────────────────────────────┐
      │         TECH LEAD (delegate mode only)        │
      │   Coordinates, delegates, synthesizes.        │
      │   NEVER implements, edits files, or builds.   │
      └───┬──────────────┬──────────────┬────────────┘
          │              │              │
   ┌──────▼──┐    ┌──────▼──┐    ┌──────▼──┐
   │Worker A │    │Worker B │    │Worker C │    IMPLEMENT
   │implement│    │implement│    │implement│
   │  commit │    │  commit │    │  commit │
   └────┬────┘    └────┬────┘    └────┬────┘
        ✕              ✕              ✕         SHUTDOWN workers
        │              │              │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │Review B │    │Review C │    │Review A │    CROSS-REVIEW
   │→ REVISE │    │→APPROVE │    │→ REVISE │
   └────┬────┘    └─────────┘    └────┬────┘
        │                             │
   ┌────▼─────────────────────────────▼────┐
   │        CODEX JUDGE (optional)         │    CROSS-PROVIDER VERDICT
   │  Scores review quality 1-5, flags     │    (graceful degradation:
   │  critical issues, auto-approve/revise │     skipped if unavailable)
   └────┬─────────────────────────────┬────┘
        ✕                             ✕         SHUTDOWN reviewers
        │                             │
   ┌────▼────┐                   ┌────▼────┐
   │Fixer A  │                   │Fixer C  │    FIX (fresh agents)
   └────┬────┘                   └────┬────┘
        ✕                             ✕
   ┌────▼────┐                   ┌────▼────┐
   │Review B'│                   │Review A'│    RE-REVIEW
   │→APPROVE │                   │→APPROVE │    (fresh context)
   └─────────┘                   └─────────┘
```

**Key principles:**
- Fresh agents for each phase — no context pollution across rounds
- Reviewers are read-only (cannot edit files) with whitelisted Bash commands
- Tasks need reviewer APPROVED verdict before they can be marked complete (enforced by hook)
- Iterative convergence: fix-review cycles until APPROVED or budget exhausted
- Cross-provider judge eliminates single-model bias (optional, degrades gracefully)

## Codex as Advisor & Cross-Provider Judge

Insistir integrates OpenAI's Codex CLI (GPT-5) as an independent second opinion via the bundled `.mcp.json` MCP server configuration.

### `/insistir:advisor`

Get an independent perspective from a different-provider model on your plan, diff, or a specific question:

```
/insistir:advisor Should we use a queue here or is polling sufficient?
/insistir:advisor          (defaults to reviewing the current plan/diff)
```

The advisor gathers relevant context (plan, diff, recent errors), sends it to Codex with a read-only sandbox, and returns a dual-perspective summary (Codex opinion + Claude synthesis). Follow-up questions reuse the same Codex thread for continuity.

### Cross-Provider Judge in the Review Loop

During Phase 4 (adversarial review), the lead can invoke a Codex judge to score the reviewer's verdict on a 1-5 rubric (Correctness 40%, Spec compliance 20%, Security 20%, Maintainability 20%). Decision matrix:

| Score | Critical issues? | Action |
|-------|-----------------|--------|
| >= 4  | No              | Auto-approve |
| <= 2  | Any             | Auto-revise with judge remediation items |
| 3     | —               | Lead judgment, reviewer as tiebreaker |

The judge never sees implementer reasoning — only the code diff and review verdict — preventing anchoring bias.

### Requirements and Degradation

- **Requires**: OpenAI Codex CLI installed and authenticated (`codex` command available in PATH)
- **Graceful degradation**: If Codex is unavailable (not installed, auth expired, 2 consecutive errors), the pipeline skips the judge step and the reviewer's verdict stands alone. The advisor command falls back to a Claude subagent.

## Goal Loop (Loop Engineering)

Gradient descent for goals: an agent factory generates goal-specialized agents, then the loop runs forward → loss → backward → update until the goal is provably met. Grounded in TextGrad/ProTeGi (textual gradients), SkillGrad (diagnoser/momentum/patcher, contrastive diagnosis, early stopping), ADAS (meta-agent + design archive), and SpecBench (visible/held-out evidence split against reward hacking).

### `/insistir:goal`

```
/insistir:goal Reduce p95 latency below 200ms on the /search endpoint --max-epochs 6 --patience 2
```

**Goal Contract (guided intake)** — Objective and end state, a loss function of observable evidence **partitioned into visible validation** (the implementer's optimization target) **and held-out compositional checks** (judge-only — never shown to the implementer), constraints, epoch budget, and an initial edit scope (the learning rate). Unverifiable goals are rejected upfront.

**Agent Factory** — Before looping, a meta-step generates four goal-specialized agent prompts into `loops/<slug>/agents/` (implementer, verifier, diagnoser, judge), seeded by `loops/archive.md` and `docs/solutions/` — designs compound across goals, ADAS-style.

**Descent Loop** — Each epoch: a fresh implementer (forward pass) acts on the gradient log and momentum; evidence commands compute the loss; a diagnoser converts failures into textual gradients and newly-passing checks into contrastive "preserve this" signal; momentum accumulates recurring patterns; plateau shrinks the edit scope and eventually early-stops (textual optimization is non-monotonic).

**Anti-Reward-Hacking Judge** — When visible evidence is green, the judge (Codex by default, Claude fallback) runs the held-out checks and reports the **hacking gap** (visible minus held-out pass rate). A positive gap with green visible evidence is presumptive gaming — deleted tests, hardcoded values, lookup-table memorization, feature isolation — and yields NOT MET.

## Knowledge Compounding

Solved problems are captured as searchable documentation in `docs/solutions/`. When planning new work, a learnings-researcher agent searches past solutions so workers benefit from prior experience.

- `/insistir:compound` — Document a solved problem with parallel sub-agents (context analyzer, solution extractor, prevention strategist)
- Solution files use YAML frontmatter with category, tags, severity, and status for searchable filtering

## File-based TODO Lifecycle

Review findings are tracked as standalone markdown files in `todos/` with a file-name-driven lifecycle:

```
{id}-pending-{priority}-{description}.md  →  {id}-ready-...  →  {id}-complete-...
         (from review)                        (triaged)           (resolved)
```

- `/insistir:triage` — Present pending TODOs one by one for user decision (approve, skip, modify). Uses haiku model for cost efficiency.
- `/insistir:resolve-todos` — Spawn parallel worker agents (one per ready TODO) to fix and commit

## Plan Deepening

Enrich plans with external research before execution. Parallel researcher agents look up framework documentation, best practices, and edge cases.

- `/insistir:deepen-plan <plan-file>` — Parse plan sections, spawn researchers per section, enhance with Research Insights, Implementation Details, Edge Cases, and References

## Components

| Component | Type | Description |
|-----------|------|-------------|
| `insistir` | Skill | Main orchestration pipeline (intake, plan, execute, cross-review, judge, cleanup) |
| `codex-judge` | Skill | Cross-provider LLM judge — scores review verdicts via Codex/GPT-5, dual-threshold gating |
| `goal-loop` | Skill | Loop engineering as gradient descent: agent factory, textual gradients, momentum, held-out evidence, anti-reward-hacking judge |
| `compound-knowledge` | Skill | Orchestrates parallel sub-agents to capture solved problems as documentation |
| `file-todos` | Skill | Defines TODO format, lifecycle, and management operations |
| `insistir-worker` | Agent | Implements tasks or applies review fixes, commits, reports to lead |
| `insistir-reviewer` | Agent | Cross-reviews work with structured APPROVED/REVISE verdicts (read-only) |
| `insistir-learnings-researcher` | Agent | Searches `docs/solutions/` for relevant past solutions (read-only, opus) |
| `insistir-researcher` | Agent | Researches best practices, framework docs, and codebase patterns (read-only, opus) |
| `compound` | Command | Trigger compound-knowledge skill to document a solved problem |
| `advisor` | Command | Get a second opinion from Codex/GPT-5 on plan, diff, or a question |
| `goal` | Command | Loop-engineering goal loop: implement, verify, judge, iterate |
| `triage` | Command | Present pending TODOs one by one for user triage decisions |
| `resolve-todos` | Command | Spawn parallel agents to fix ready TODOs |
| `deepen-plan` | Command | Enrich a plan file with external research via parallel researchers |
| `TaskCompleted` | Hook | Blocks task completion without review approval marker |
| `PreToolUse(Bash)` | Hook | Whitelists read-only commands for reviewer agents (generalized, team-configurable) |
| `.mcp.json` | Config | Bundles Codex MCP server into the plugin for advisor/judge features |
| `insistir.py` | Script | Plan validator CLI (validate, waves, status) |

## remoto — Remote Agent Orchestration over SSH

Orchestrate headless Claude Code and Codex agents on a remote SSH host (e.g. a Jetson) from your Mac. The local session is the lead: it spawns `claude -p` / `codex exec` jobs over SSH, polls file-based job state, collects results, and cross-reviews across providers. Jobs survive disconnects (`nohup setsid`, state under `~/.remoto/jobs/<id>/` on the host).

```
/plugin install remoto@jaiskills

/remoto:run Migrate the sensor pipeline to async — implement with claude, cross-review with codex
/remoto:status
```

| Component | Type | Description |
|-----------|------|-------------|
| `remote-agents` | Skill | Orchestration playbook: probe, prepare workspace, spawn, wait, collect, cross-review |
| `prompt-templates` | Reference | Metaprompt-engineered worker/reviewer/fixer templates per model family |
| `remoto.sh` | Script | SSH job runner: hosts, spawn, ls, status, wait, logs, result, kill, push, pull, clean |
| `run` / `status` | Commands | `/remoto:run <task>`, `/remoto:status [job ...]` |

Requires: SSH key auth to the host (`Host jetson` in `~/.ssh/config`), `claude` and `codex` logged in on the remote, `rsync` for push/pull.

## Requirements

- Claude Code 1.0.33+
- Python 3.10+ (for hook scripts)
- Optional: [OpenAI Codex CLI](https://github.com/openai/codex) — enables `/insistir:advisor` and cross-provider judge features

## License

MIT
