---
title: "Codex Harness Deep Dive"
last_verified: 2026-07-16
sources_verified: true
---

> **Verification note** — Every section was researched against live Codex documentation on 2026-07-16. Source URLs are listed at the end of each section. If a section lacks a clickable URL, the claim originates from the plan's pre-verified research insights (marked "plan-insight") and should be re-checked on the next refresh.

# Codex Harness Deep Dive

This guide describes how a generated prompt or AGENTS.md should exploit the Codex harness — OpenAI's agentic coding environment (CLI, cloud, and IDE). Use it when the metaprompt's target harness is Codex.

---

## 1. AGENTS.md

AGENTS.md is the primary way to give Codex project-level instructions. It is the Codex equivalent of Claude Code's CLAUDE.md.

### Discovery order

Codex builds its instruction chain by walking directories from global scope down to the current working directory:

1. **Global** (`~/.codex/`): checks `AGENTS.override.md` first, then `AGENTS.md`.
2. **Git root to CWD**: at every directory level, checks `AGENTS.override.md`, then `AGENTS.md`, then any names listed in `project_doc_fallback_filenames`.

The search stops at the current working directory. Empty files are skipped.

### Merge behavior

Files are concatenated root-to-leaf. Later (closer-to-CWD) content overrides earlier guidance. Use `AGENTS.override.md` at any directory level to surgically replace the base `AGENTS.md` at that level without deleting it.

### Size cap

The combined instruction payload is capped at **32 KiB** (`project_doc_max_bytes` in config.toml). Exceeding it silently truncates.

### What belongs in AGENTS.md

- Project context a model cannot infer from the code alone.
- Exact test and lint commands (`npm test`, `pytest -x`).
- Coding conventions, naming rules, import ordering.
- Dependency policy (e.g., "do not add new npm packages without asking").
- Per-directory overrides for service-specific rules (API key rotation, framework idioms).

### Debugging

Run `codex --print-instructions` to inspect the merged instruction chain. You can also configure alternate fallback filenames via `project_doc_fallback_filenames` in config.toml, and use `CODEX_HOME` for profile isolation (e.g., CI automation accounts).

### Example: AGENTS.md excerpt

```markdown
# Project: acme-api

## Stack
TypeScript 5.8, Express 5, PostgreSQL 16, Drizzle ORM.

## Commands
- Test: `npm test` (runs vitest)
- Lint: `npm run lint` (eslint + prettier)
- Type-check: `npx tsc --noEmit`

## Conventions
- All new endpoints go in `src/routes/` with a co-located `*.test.ts` file.
- Use Drizzle schema migrations — never raw SQL in application code.
- Prefer `zod` for request validation; do not add `joi`.

## Per-directory: src/workers/
Background jobs use BullMQ. Each worker file exports a default
`Processor` function. Always include a dead-letter-queue config.
```

Source: https://learn.chatgpt.com/docs/agent-configuration/agents-md

---

## 2. Sandbox Modes

Codex enforces three sandbox levels controlling filesystem and network access:

| Mode | Filesystem | Network | Use case |
|------|-----------|---------|----------|
| `read-only` | Read only | Blocked | Inspection, code review |
| `workspace-write` (default) | Write within project | Blocked | Normal development |
| `danger-full-access` | Unrestricted | Unrestricted | When full access is intentionally desired |

### Platform implementation

- **macOS**: native Seatbelt framework — no extra setup.
- **Linux / WSL2**: `bubblewrap` (bwrap) + seccomp. Install bwrap via your distro's package manager, especially on AppArmor-restricted systems (Ubuntu 24.04+).

### Protected paths

Even at `danger-full-access`, `.git`, `.agents`, and `.codex` directories remain read-only.

### Configuration

Set in config.toml:

```toml
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
writable_roots = ["/home/user/project"]
```

Source: https://learn.chatgpt.com/docs/sandboxing

---

## 3. Approval Policies

Four approval modes control when Codex must pause for human (or AI) authorization:

### Modes

1. **on-request** (default) — asks approval for edits outside the workspace or network-requiring commands. Recommended for version-controlled projects.
2. **never** (`--ask-for-approval never`) — no approval prompts; sandbox still enforced. Use for CI/CD.
3. **untrusted** (`--ask-for-approval untrusted`) — only known-safe read operations run automatically; everything else requires approval.
4. **granular** — fine-grained per-category control (sandbox approvals, execution policy, MCP prompts, permission requests, skill scripts) via config.toml.

### Auto-review (AI reviewer)

Setting `approvals_reviewer = "auto_review"` routes eligible approval requests through an AI reviewer instead of surfacing them to the user. The reviewer checks for:

- Data exfiltration risks.
- Credential probing.
- Persistent security weakening.
- Destructive or irreversible actions.

Actions are classified low / medium / high / critical. Low and medium proceed when policy allows; critical is always denied.

```toml
approval_policy = "on-request"
approvals_reviewer = "auto_review"

[auto_review]
policy = "your_custom_policy_text"
```

Source: https://learn.chatgpt.com/docs/agent-approvals-security

---

## 4. CLI: exec, resume, and key flags

### Non-interactive mode

`codex exec` runs Codex without interactive prompts — designed for CI/CD pipelines and scripted workflows.

### Session resume

`codex resume` reopens a previous session from SQLite-backed local state, letting you continue where you left off.

### Key flags

| Flag | Purpose |
|------|---------|
| `-m <model>` | Select model and reasoning effort (e.g., `-m gpt-5.6-sol`) |
| `--image` | Attach screenshots or diagrams to the first prompt |
| `--search` | Enable live web search for current documentation |
| `--sandbox <mode>` | Override sandbox mode |
| `--ask-for-approval <mode>` | Set approval policy |
| `--print-instructions` | Debug merged AGENTS.md chain |

Source: https://learn.chatgpt.com/docs/cli

---

## 5. config.toml

The main configuration file lives at `~/.codex/config.toml` (or `$CODEX_HOME/config.toml`).

### Essential settings

```toml
model = "gpt-5.5"
model_reasoning_effort = "high"    # minimal | low | medium | high | xhigh
model_verbosity = "medium"         # low | medium | high (GPT-5+ Responses API)
model_context_window = 200000
model_auto_compact_token_limit = 150000

sandbox_mode = "workspace-write"
approval_policy = "on-request"
approvals_reviewer = "auto_review"
```

### Profiles

Store named profiles as `~/.codex/<profile-name>.config.toml`. Select at launch with `--profile <name>`. Machine-level provider and authentication settings cannot be overridden by project-scoped configs.

### Permissions

Named permission profiles support inheritance via `extends`:

```toml
[permissions.my-profile]
extends = ":workspace"   # built-in: :read-only, :workspace

[permissions.my-profile.filesystem]
"/home/user/project" = "write"
"/etc" = "deny"

[permissions.my-profile.network]
domains = { "api.example.com" = "allow", "*.internal.corp" = "allow", "*" = "deny" }
```

Deny rules take precedence on conflicts. Wildcards: `*.example.com` (one level), `**.example.com` (recursive).

Source: https://learn.chatgpt.com/docs/config-file/config-reference

---

## 6. MCP (Model Context Protocol)

Codex supports MCP in both client and server modes.

### Client mode

Configure MCP servers in config.toml with two transport types:

**STDIO servers:**
```toml
[mcp_servers.my-server]
command = "npx"
args = ["-y", "@acme/mcp-server"]
env = { API_KEY_VAR = "ACME_API_KEY" }
startup_timeout_sec = 10
tool_timeout_sec = 60
default_tools_approval_mode = "auto"  # auto | prompt | writes | approve
```

**Streamable HTTP servers:**
```toml
[mcp_servers.remote-server]
url = "https://mcp.example.com/v1"
bearer_token_env_var = "MCP_TOKEN"
startup_timeout_sec = 10
tool_timeout_sec = 60
```

Tool approval can be set per-server (`default_tools_approval_mode`) or per-tool with overrides. If an identity mismatch is detected between the configured and actual server identity, the server is silently disabled as a security measure.

### Server mode

`codex mcp-server` exposes Codex itself as an MCP server, providing two tools:

- **`codex(prompt, threadId?)`** — send a task to a Codex agent. Returns a `threadId` for follow-up.
- **`codex-reply(threadId, message)`** — continue a conversation on an existing thread.

This enables multi-agent delegation: an outer orchestrator (another Codex instance, Claude Code, or any MCP client) can spawn and manage Codex sub-tasks via standard MCP calls.

Source: https://learn.chatgpt.com/docs/config-file/config-reference (MCP section), plan-insight (server mode details from learn.chatgpt.com/docs pre-verified research)

---

## 7. Plan Tool Discipline

Codex uses `update_plan` to track task progress with statuses: `pending`, `in_progress`, `completed`.

### Rules for generated prompts

- **Skip planning for trivial tasks** — roughly the easiest 25% of requests do not benefit from a plan.
- **Close all items before finishing** — every plan item must end as Done, Blocked (with reason and a targeted question), or Cancelled. Never leave items in `in_progress`.
- **Keep plans actionable** — each item should map to a concrete step, not a vague goal.

Source: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

---

## 8. Parallel Tool Batching

Codex supports `multi_tool_use.parallel` to batch independent tool calls into a single round-trip.

### Pattern

1. Plan all needed reads upfront.
2. Issue one parallel batch with every read/list/search call.
3. Analyze results together.
4. Repeat if new reads emerge.

The prompting guide is explicit: "Always maximize parallelism. Never read files one-by-one unless logically unavoidable."

Source: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

---

## 9. Phase Metadata (GPT-5.3+)

The Responses API includes a `phase` field on assistant output items:

- `null` — default.
- `"commentary"` — preamble-style thinking-aloud content.
- `"final_answer"` — the closeout message delivered to the user.

**Dropping the `phase` parameter when replaying conversation history degrades performance significantly.** Generated prompts and tool harnesses that replay Codex conversations must preserve this metadata across requests.

Source: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

---

## 10. Preamble Pattern

Codex expects a short acknowledgement before diving into tool calls:

1. **Acknowledge** the request in one sentence.
2. **State a 1–2 sentence plan** of what you will do.
3. **Update** with 1–2 sentences at milestones — every 1–3 execution steps (minimum every 6 steps or 10 tool calls).
4. Share outcomes, next steps, and open questions without log-style labels or status headers.

Source: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

---

## 11. Personalities

Codex supports two personality modes that a prompt can request:

- **Friendly** — warm, partner-oriented tone. Uses "we/let's" language, affirms progress, emphasizes collaboration and ownership.
- **Pragmatic** — terse, direct delivery. Higher actionable-information-per-token ratio, fewer social flourishes. Better for latency-sensitive or CI contexts.

Source: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

---

## 12. File Reference Format

Use inline backtick paths with optional line and column numbers:

- `src/app.ts:42` — file and line.
- `src/app.ts:42:5` — file, line, and column (1-based).

Avoid URI schemes like `file://` or `vscode://`. Each reference should be standalone and clickable in Codex's UI.

Source: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

---

## 13. Git Safety Prohibitions

Generated prompts should instruct the model to:

- **Never** use `git reset --hard`, `git checkout --`, or other destructive commands unless the user explicitly requests them.
- **Never** revert unrelated user changes found in touched files.
- If unrelated changes exist, read them carefully and work around them.
- Prefer `apply_patch` (the model is specifically trained for this diff format) over manual file writes.

Source: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

---

## 14. Codex Cloud: Two-Phase Runtime

Codex cloud tasks run in a two-phase container:

### Setup phase (online, secrets available)

- Full internet access for installing dependencies.
- Environment secrets are accessible.
- Package managers (npm, pip, poetry, etc.) resolve automatically.
- Custom bash setup scripts can run.

### Agent phase (offline, secrets stripped)

- Internet access is off by default (configurable).
- **Secrets are removed** before the agent phase starts.
- Regular environment variables persist, but `export` commands from setup do not carry over — use `~/.bashrc` instead.

### Container caching

Cached containers persist up to 12 hours. Cache invalidates when setup scripts, maintenance scripts, environment variables, or secrets change. Manual reset is available from the environment settings page.

Source: https://learn.chatgpt.com/docs/environments/cloud-environment

---

## 15. Model Notes

| Surface | Default model | Notes |
|---------|--------------|-------|
| Codex CLI / IDE / Cloud | GPT-5.5 | Current default across all surfaces |
| gpt-5-codex | — | 400K context, $1.25/$10 per MTok (plan-insight) |
| GPT-5.6 | Via `-m gpt-5.6-sol` (or `terra`/`luna`) | Available in CLI; cloud tasks cannot change the default model |

### Selection guidance

- **Sol** — hardest coding, agents, research, cybersecurity.
- **Terra** — everyday tasks, performance competitive with GPT-5.5 at lower cost.
- **Luna** — high-volume extraction, classification, transformation.

In config.toml, set `model = "gpt-5.6-sol"` (or any variant). Adjust `model_reasoning_effort` to match task complexity — Medium balances speed and depth for standard work.

Source: https://learn.chatgpt.com/docs/models

---

## Quick Reference for Prompt Authors

When generating a prompt targeting the Codex harness:

1. **Do not re-specify built-in tools** — the harness provides them. Reference them by behavior, not by tool name.
2. **Include an AGENTS.md section** in your deliverable if the prompt is project-scoped.
3. **Instruct parallel batching** — "read all needed files in one parallel batch before analyzing."
4. **Preserve `phase` metadata** in any conversation-replay logic.
5. **Set personality** (friendly or pragmatic) to match the use case.
6. **Specify sandbox mode and approval policy** when the task has security constraints.
7. **Use the preamble pattern** — acknowledge, plan, then execute.
8. **Reference files as** `path/to/file.ts:line` — no URI schemes.
