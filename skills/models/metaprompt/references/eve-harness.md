---
title: "Eve Harness Deep Dive"
last_verified: 2026-07-18
sources_verified: true
---

> **Verification note** — Every section was researched against live documentation on 2026-07-18. Source URLs are listed at the end of each section.

# Eve Harness Deep Dive (Vercel)

Eve is Vercel's open-source, filesystem-first TypeScript framework for durable backend AI agents ("the Next.js for agents"), launched June 2026 (Apache-2.0, `vercel/eve`, public beta — `eve@0.25.1` as of 2026-07-17). Unlike Claude Code or Codex, eve is **not itself a coding agent** — it is the framework you use to *build* agents. A metaprompt targeting eve is therefore usually the content of `agent/instructions.md` (the agent's system prompt) plus optional skill files.

Do not confuse with `scaling-group/eve` (an evolutionary ensemble research framework) — unrelated.

Source: https://vercel.com/blog/introducing-eve
Source: https://github.com/vercel/eve

---

## 1. Architecture ("an agent is a directory")

Each file's location in the tree defines its role — no registry or wiring:

```
my-agent/
  agent/
    agent.ts              # Model + runtime config (defineAgent)
    instructions.md       # System prompt — ALWAYS loaded
    tools/                # One .ts file per tool (app runtime, full process.env)
    skills/               # On-demand procedures (Markdown files or SKILL.md dirs)
    subagents/            # Child agents with own tools/config
    channels/             # HTTP, Slack, Discord, Teams, Telegram, Twilio, GitHub, Linear
    connections/          # MCP servers / OpenAPI integrations
    sandbox/              # Sandbox config (sandbox.ts)
    schedules/            # Cron jobs
```

Pillars: **durable execution** (sessions checkpoint every step via the Workflow SDK; agents park at zero compute while waiting for approvals and resume exactly), **sandboxed compute** (Docker/microsandbox locally, Vercel Sandbox in production), **human-in-the-loop** (tools declare `needsApproval`), multi-channel delivery, and OpenTelemetry observability.

Source: https://vercel.com/blog/introducing-eve
Source: https://eve.dev/docs/introduction
Source: https://vercel.com/docs/eve/concepts

---

## 2. Where the generated prompt goes

- **`agent/instructions.md`** — plain Markdown, always-on system prompt. This is eve's equivalent of CLAUDE.md/AGENTS.md; eve does **not** read those files.
- **Skills** — progressive disclosure via a SKILL.md convention: either a flat `agent/skills/forecast.md` or a packaged directory `agent/skills/research/SKILL.md` (+ `references/`). The frontmatter `description` is the routing hint; the model loads skills on demand through a framework-owned `load_skill` tool. Put always-needed rules in `instructions.md`; put long procedures in skills.
- **`agent/agent.ts`** — runtime config:

```typescript
import { defineAgent } from "eve";
export default defineAgent({
  model: "anthropic/claude-sonnet-5",   // gateway slug, or an AI SDK model object
  // limits: { maxSubagentDepth }, compaction, provider options
});
```

Source: https://eve.dev/docs/getting-started
Source: https://eve.dev/docs/skills

---

## 3. Built-in tools (do not re-specify)

The default harness provides: `read_file`, `write_file`, `bash` (all targeting the **sandbox**, not the app runtime), a web-access tool, and a built-in `agent` delegation tool (delegates to a copy of the agent or to declared subagents). Built-ins can be overridden or disabled via Default Harness configuration. Custom tools in `agent/tools/` run in the app runtime with full `process.env`.

A generated `instructions.md` should reference these tools by behavior ("run the tests with bash"), never re-define them.

Source: https://eve.dev/docs/tools
Source: https://vercel.com/docs/eve/concepts

---

## 4. Model support

- **Gateway slugs** (default path): `"anthropic/claude-opus-4.8"`, `"openai/gpt-5.4-mini"`, etc., resolved through **Vercel AI Gateway** (see `ai-gateway-harness.md`). On Vercel deployments auth is automatic via OIDC; locally set `AI_GATEWAY_API_KEY`.
- **Direct provider**: install the AI SDK package and pass a model object — `anthropic("claude-opus-4-8")` with `ANTHROPIC_API_KEY`, `openai("gpt-5.5")` with `OPENAI_API_KEY`.
- Scaffold default: `anthropic/claude-sonnet-5` (some docs show `openai/gpt-5.4-mini`). The dev TUI `/model` command guides credential setup.

Source: https://vercel.com/docs/ai-gateway/models-and-providers
Source: https://eve.dev/docs/getting-started

---

## 5. Subscription auth (Claude Pro/Max, ChatGPT Plus/Pro)

**Eve cannot run on consumer subscriptions. Both provider paths incur metered pay-per-token billing** — authenticated locally via API keys, or via OIDC on Vercel deployments (which still bills gateway credits, not a subscription).

- **Claude Pro/Max**: not supported. Eve makes server-side API calls via AI Gateway or `ANTHROPIC_API_KEY`. Anthropic's consumer ToS restricts Pro/Max OAuth tokens to Claude Code/claude.ai (see `pi-harness.md` §5 and `ai-gateway-harness.md` §3 for the sourced policy detail). AI Gateway's Claude-Max pass-through applies **only to Claude Code as the client**, not to eve agents. Use a key from console.anthropic.com.
- **ChatGPT Plus/Pro**: eve exposes no ChatGPT-subscription auth path — its OpenAI integration is `OPENAI_API_KEY` (platform.openai.com, billed separately from any ChatGPT plan).
- **Gotcha (Claude Code specifically, per the Vercel guide below)**: if `ANTHROPIC_API_KEY` is set in the environment, Claude Code uses it silently in preference to OAuth/`ANTHROPIC_AUTH_TOKEN` — relevant when eve development and Claude Code share a shell environment.

Practical pattern for a subscription-only budget: build/test the *prompt* inside Claude Code or Codex CLI (covered by the subs), and reserve eve for deployment where API billing is accepted.

Source: https://vercel.com/docs/ai-gateway/coding-agents/claude-code
Source: https://vercel.com/changelog/claude-code-max-via-ai-gateway-available-now-for-claude-code

---

## 6. Install, commands, gotchas

```bash
npx eve@latest init my-agent     # new project (requires Node 24+)
eve dev      # local dev TUI — auto-reaps Docker sandbox containers
eve build    # compile to .eve/
eve start    # serve built output (does NOT clean up sandbox containers)
eve eval     # run test suites
eve channels add <platform>
```

Gotchas as of 0.25.x:

- Public beta — APIs and docs still shifting; breaking changes landed in 0.23.0 (built-in agent tool became root-only) and 0.24.0 (`experimental_workflow(options)` replaces `ExperimentalWorkflow`; `maxSubagents` moved to the Workflow tool definition).
- Subagent recursion capped at 3 levels by default (`limits.maxSubagentDepth`); at the cap eve stops advertising subagent tools.
- Local sandbox features require Docker or microsandbox; without one, sandbox-backed built-ins fail.
- Self-hosted Postgres: `@workflow/world-postgres@4.2.0` (npm `latest`) is incompatible and fails runs mid-execution.
- Gateway slugs without `AI_GATEWAY_API_KEY` locally → dev TUI flags missing credentials.

Source: https://github.com/vercel/eve/releases
Source: https://vercel.com/docs/eve
