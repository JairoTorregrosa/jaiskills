# jaiskills

My agent skills for Claude Code, shipped as **one plugin**: agents checking agents, verification-first orchestration, model-aware prompting, and OpenAI tooling from the terminal.

These skills exist to fix failure modes I kept hitting with coding agents. Each one is small, composable, and earns its place by closing a specific gap.

## Install (30 seconds)

```
/plugin marketplace add JairoTorregrosa/jaiskills
/plugin install jaiskills@jaiskills
```

Or load locally for development:

```bash
claude --plugin-dir /path/to/jaiskills
```

> **Migrating from ≤0.4.x?** This repo used to publish four separate plugins (`insistir`, `metaprompt`, `constatar`, `remoto`). They are now one plugin, `jaiskills`. Uninstall the old ones and install `jaiskills@jaiskills`; every skill and command came along.

## Why these skills exist

### #1: The agent says it's done — and it isn't

Self-reported success is the most expensive lie in agentic coding.

- **`insistir`** (`/insistir <task>`) — multi-agent orchestration where every worker's output is cross-reviewed by a *different* agent in an adversarial loop. Tasks cannot be marked complete without a reviewer's APPROVED verdict (enforced by hook). The name is the point: fix, review, judge — insist until verified.
- **`constatar-plan`** / **`constatar-verify`** (`/constatar-run`, `/constatar-verify`, `/constatar-audit`) — verification-first orchestration through the [constatar](https://github.com/JairoTorregrosa/constatar) Rust engine: plans with a 6-rung evidence ladder, grounded verdicts, resumable journals.

### #2: One model grades its own homework

Same-model review inherits the same blind spots.

- **`codex-judge`** — a cross-provider judge (Codex/GPT-5) scores each review verdict on a weighted rubric and gates auto-approve/auto-revise. The judge never sees implementer reasoning — only diff and verdict — preventing anchoring. Degrades gracefully when Codex is unavailable.
- **`/advisor`** — an independent second opinion from a different-provider model on your plan, diff, or question.

### #3: The loop plateaus, or worse, games the test

- **`goal-loop`** (`/goal <goal>`) — loop engineering as gradient descent: an agent factory generates goal-specialized agents, then forward → loss → textual gradient → update, with momentum and early stopping. Evidence is split into visible checks (the implementer's target) and **held-out checks the implementer never sees**; a positive gap between them is treated as reward hacking and yields NOT MET.

### #4: Lessons evaporate between sessions

- **`compound-knowledge`** (`/compound`) — captures solved problems as searchable docs in `docs/solutions/`; a learnings-researcher agent feeds them into future planning.
- **`file-todos`** (`/triage`, `/resolve-todos`) — review findings become markdown files with a file-name-driven lifecycle (`pending → ready → complete`), triaged one by one, then fixed by parallel workers.

### #5: The prompt wasn't built for the model that runs it

- **`metaprompt`** (`/metaprompt`) — takes a goal, a target model, and a target harness, and produces a complete prompt engineered for that combination, from researched per-model/per-harness guides (Claude, GPT-5.x/Codex; Claude Code, Codex CLI, pi, Amp, and more).

### #6: Your laptop is the bottleneck

- **`remote-agents`** (`/remoto-run`, `/remoto-status`) — orchestrate headless `claude -p` / `codex exec` workers on a remote SSH host. File-based job state, jobs survive disconnects, results collected and cross-reviewed across providers. Requires SSH key auth to the host and `claude`/`codex` logged in there.

### #7: You want OpenAI's models from the terminal — or an image turned into a real page

- **`askcodex`** — use GPT-5.x and image models from the CLI with the [askcodex](https://github.com/JairoTorregrosa/askcodex) binary: one-shot text, image create/edit, models, quota. No API key; it reuses `codex login` credentials. (Canonical copy lives in the askcodex repo; this one tracks it.)
- **`image-to-frontend`** — brief → 4 visual variants → build spec → real React/HTML page, iterated to pixel-close. Image generation runs through askcodex.

## Skills

| Category | Skill | One line |
|---|---|---|
| orchestration | `insistir` | Cross-validated multi-agent pipeline; APPROVED-gated completion |
| orchestration | `constatar-plan` / `constatar-verify` | Verification-first plans and grounded verdicts via the constatar engine |
| orchestration | `goal-loop` | Goal descent with agent factory, textual gradients, anti-reward-hacking judge |
| orchestration | `codex-judge` | Cross-provider review scoring with dual-threshold gating |
| orchestration | `remote-agents` | Headless agent fleets over SSH |
| prompting | `metaprompt` | Model- and harness-specific prompt generation |
| knowledge | `compound-knowledge` | Solved problems → searchable solution docs |
| knowledge | `file-todos` | File-based TODO lifecycle for review findings |
| openai | `askcodex` | OpenAI models as a CLI (text, images, quota) |
| openai | `image-to-frontend` | Reference image or brief → working frontend |

Agents (`insistir-worker`, `insistir-reviewer`, `insistir-researcher`, `insistir-learnings-researcher`), hooks (completion gate, reviewer Bash whitelist), the bundled Codex MCP config, and the `remoto.sh` / `insistir.py` scripts ship in the same plugin. Full inventory in [docs/skills.md](docs/skills.md).

## How insistir works

```
      ┌──────────────────────────────────────────────┐
      │         TECH LEAD (delegate mode only)        │
      │   Coordinates, delegates, synthesizes.        │
      │   NEVER implements, edits files, or builds.   │
      └───┬──────────────┬──────────────┬────────────┘
          │              │              │
   ┌──────▼──┐    ┌──────▼──┐    ┌──────▼──┐
   │Worker A │    │Worker B │    │Worker C │    IMPLEMENT
   └────┬────┘    └────┬────┘    └────┬────┘
        │              │              │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │Review B │    │Review C │    │Review A │    CROSS-REVIEW
   │→ REVISE │    │→APPROVE │    │→ REVISE │    (read-only reviewers)
   └────┬────┘    └─────────┘    └────┬────┘
        │                             │
   ┌────▼─────────────────────────────▼────┐
   │        CODEX JUDGE (optional)         │    CROSS-PROVIDER VERDICT
   └────┬─────────────────────────────┬────┘
        │                             │
   ┌────▼────┐                   ┌────▼────┐
   │Fixer A  │                   │Fixer C  │    FIX (fresh agents)
   └────┬────┘                   └────┬────┘
   ┌────▼────┐                   ┌────▼────┐
   │Review B'│                   │Review A'│    RE-REVIEW → APPROVE
   └─────────┘                   └─────────┘
```

Fresh agents per phase, read-only reviewers, iterative convergence until APPROVED or budget exhausted.

## Requirements

- Claude Code 1.0.33+
- Python 3.10+ (hook scripts)
- Optional: [OpenAI Codex CLI](https://github.com/openai/codex) — enables `/advisor`, the cross-provider judge, and the askcodex-backed skills
- Optional: the [constatar](https://github.com/JairoTorregrosa/constatar) engine — for the constatar skills

## License

MIT
