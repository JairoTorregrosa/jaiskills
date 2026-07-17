---
title: Claude Code Harness — Prompt Engineering Reference
last_verified: 2026-07-16
sources_verified: true
covers: Built-in tools, Skills, Subagents, Hooks, MCP, CLAUDE.md, Permission modes, Plan mode, Headless/Agent SDK
---

> **Verification:** All URLs listed below were fetched and content-verified on 2026-07-16. Each section's Source line points to the specific page supporting that section's claims.

# Claude Code Harness Deep Dive

This guide explains how a generated prompt, CLAUDE.md, or SKILL.md should interact with the Claude Code harness. The harness provides a rich tool surface, orchestration primitives, and configuration layers. Understanding what the harness already provides is the single most important principle: **never re-specify built-in tools in prompts**.

---

## 1. Built-in Tool Surface

Claude Code provides a fixed set of tools that are always available. These are injected by the harness itself — prompts must never redefine or re-describe them.

### Available tools

| Category | Tools |
|----------|-------|
| File operations | `Read`, `Write`, `Edit`, `Glob`, `Grep` |
| Execution | `Bash`, `Monitor` |
| Web | `WebSearch`, `WebFetch` |
| Orchestration | `Agent`, `SendMessage`, `Task*` (TaskCreate, TaskGet, TaskList, TaskStop, TaskUpdate) |
| User interaction | `AskUserQuestion` |
| Skills | `Skill` |
| Artifacts | `Artifact` |
| Scheduling | `Cron*`, `ScheduleWakeup` |
| Notebooks | `NotebookEdit` |
| Plan mode | `ExitPlanMode` |
| Worktrees | `EnterWorktree`, `ExitWorktree` |

### Rule #1: Never re-specify built-in tools

The tool names above are the exact strings used in permission rules, subagent `tools` lists, and hook matchers. A generated prompt or CLAUDE.md should reference tools by these names for configuration but must never include tool descriptions or parameter schemas — the harness injects those.

```markdown
<!-- BAD — re-specifies built-in tool -->
Use the Read tool to read files. It accepts a file_path parameter...

<!-- GOOD — references tool by name for behavioral guidance only -->
Prefer Read over `cat` for viewing file contents.
```

Source: https://docs.claude.ai/en/tools-reference

---

## 2. Skills (Progressive Disclosure)

Skills are packaged instruction sets loaded on demand via the `Skill` tool. They enable progressive disclosure: heavy instructions stay out of context until needed.

### SKILL.md structure

A skill lives in a directory containing `SKILL.md` (under 500 lines) plus an optional `references/` subdirectory for supplemental material. The SKILL.md frontmatter controls when and how the skill loads.

### Key frontmatter fields

```yaml
---
name: deploy
description: "Deploy the app to production via Railway CLI" # max 1,536 chars
when_to_use: "When the user asks to deploy, push to prod, or ship"
context: fork          # run in a forked context (optional)
allowed-tools:         # single-turn grant — clears on next user message
  - Bash(railway deploy)
  - Bash(railway logs)
paths:                 # only trigger when working in these globs
  - "apps/web/**"
  - "infra/**"
disable-model-invocation: true  # for side-effectful skills (runs commands, not reasoning)
---
```

### Dynamic injection and substitutions

Skills can inject dynamic content using shell commands with `!` backtick syntax, and reference arguments or their own directory:

```markdown
## Current deployment status
!`railway status 2>/dev/null || echo "Not connected"`

## Configuration
Load the config from `${CLAUDE_SKILL_DIR}/references/deploy-config.md`.

The user requested: $ARGUMENTS
```

### Compaction behavior

Skill content persists in context for the entire session. During compaction, the harness preserves approximately 5K tokens per skill, with a 25K total budget across all loaded skills. Design skills to front-load the most critical instructions.

### Description budget

The `description` field is capped at 1,536 characters. This description is what the model reads to decide whether to invoke the skill, so it must be precise and trigger-rich.

Source: https://docs.claude.ai/en/skills

---

## 3. Subagents

Subagents are spawned via the `Agent` tool. The body of the agent definition IS the agent's entire system prompt — subagents do not inherit the Claude Code system prompt.

### Frontmatter configuration

```yaml
---
name: linter
model: haiku
tools:
  - Read
  - Grep
  - Bash(eslint)
disallowedTools:
  - Write
  - Edit
permissionMode: auto
maxTurns: 10
skills:
  - code-review
mcpServers:
  - github
memory: false
background: true
effort: medium
isolation: worktree
---

You are a linting agent. Run eslint on all changed files and report issues.
Do not fix anything — only report.
```

### Key principles

- **Body = system prompt.** Everything below the frontmatter is the agent's entire instruction set. Brief the agent like a colleague who just walked into the room.
- **Forks inherit context.** Using `subagent_type: "fork"` gives the child your full conversation history — use a directive prompt, not a re-briefing.
- **Nesting depth.** Subagents can nest up to 5 levels deep.
- **Explore/Plan agents skip CLAUDE.md.** These built-in agent types do not load the project's CLAUDE.md, so they operate from clean instructions.
- **Plugin agents' limitations.** Hooks, mcpServers, and permissionMode declared in plugin agent definitions are silently ignored by the harness.

### Fork vs. fresh agent

```markdown
<!-- Fork: inherits context, directive-style prompt -->
Agent({
  subagent_type: "fork",
  prompt: "Check whether the migration in db/0042.sql is safe under concurrent writes. Report in under 200 words."
})

<!-- Fresh agent: needs full context in the prompt -->
Agent({
  subagent_type: "general-purpose",
  prompt: "We have a 50M-row users table. Review db/0042.sql which adds a NOT NULL column with a backfill default. Is the backfill safe under concurrent writes? Check for lock escalation and long-running transactions."
})
```

Source: https://docs.claude.ai/en/sub-agents

---

## 4. Hooks (Deterministic Automation)

Hooks are event-driven handlers that fire on specific harness events. The critical distinction: **CLAUDE.md is advisory (the model may ignore it); hooks are deterministic (the harness always executes them).**

### Decision rule

If something must happen every single time — use a hook. If it's guidance the model should usually follow — use CLAUDE.md.

### Event surface

The harness exposes approximately 28 hook events. Key categories:

| Event | Use case |
|-------|----------|
| `PreToolUse` | Deny, allow, or modify tool input before execution |
| `PostToolUse` | React to tool output (logging, validation) |
| `Stop` | Block turn end (can fire up to 8 consecutive times) |
| `Notification` | Side-channel alerts |
| `SessionStart` / `SessionEnd` | Setup/teardown |

### Handler types

Hooks support five handler types: `command`, `http`, `mcp_tool`, `prompt`, and `agent`.

### Exit code 2: blocking

A hook handler that exits with code 2 blocks the operation. The handler's stderr is fed back to Claude as an error message.

```jsonc
// .claude/settings.json — hook that blocks commits without a ticket reference
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "command": "bash -c 'echo \"$TOOL_INPUT\" | grep -qE \"[A-Z]+-[0-9]+\" || (echo \"Commit message must include a ticket reference (e.g. PROJ-123)\" >&2; exit 2)'"
      }
    ]
  }
}
```

### CLAUDE.md example referencing hooks

```markdown
<!-- In CLAUDE.md — explaining what hooks enforce so the model understands constraints -->
## Automated enforcement (hooks)
- All commits are checked for ticket references (PROJ-NNN) by a PreToolUse hook.
  If your commit message lacks one, the hook will block it — include the ticket number.
- The Stop hook runs `npm test` before ending any coding turn. If tests fail,
  you will be asked to fix them before completing.
```

Source: https://docs.claude.ai/en/hooks

---

## 5. MCP (Model Context Protocol)

MCP extends Claude Code's tool surface with external servers. Configuration lives in `.mcp.json` files at three scopes.

### Scopes

| Scope | File location | Use case |
|-------|---------------|----------|
| Local | `.mcp.json` (gitignored) | Developer-specific servers |
| Project | `.mcp.json` (committed) | Shared team servers |
| User | `~/.claude/.mcp.json` | Cross-project servers |

### Tool naming convention

MCP tools follow the pattern `mcp__<server>__<tool>`. This naming is used in permission rules and subagent tool lists:

```yaml
# In a subagent definition — granting access to a specific MCP tool
tools:
  - mcp__github__create_pull_request
  - mcp__github__list_issues
```

### Deferred tools and ToolSearch

Many MCP tools are deferred — their schemas are not loaded until explicitly requested. Before calling a deferred tool, use `ToolSearch` to load its schema:

```
ToolSearch({ query: "select:mcp__github__create_pull_request,mcp__github__list_issues" })
```

Batch all needed tools into one `ToolSearch` call to avoid unnecessary round-trips.

### Claude Code as MCP server

Claude Code can itself serve as an MCP server via `claude mcp serve`, exposing its capabilities to other MCP clients.

Source: https://docs.claude.ai/en/mcp

---

## 6. CLAUDE.md and Memory

CLAUDE.md files are the primary way to inject project-specific instructions. They form a hierarchy that is concatenated (not overridden) at load time.

### Hierarchy

```
Managed (org-level)
  └─ User (~/.claude/CLAUDE.md)
      └─ Project (.claude/CLAUDE.md or CLAUDE.md at repo root)
          └─ Local (.claude/CLAUDE.local.md — gitignored)
              └─ Nested (subdirectory CLAUDE.md files)
```

All levels are concatenated. Later entries do not override earlier ones — they add to them.

### Best practices (under 200 lines)

Target under 200 lines for the project-root CLAUDE.md. Content it should include:

- **DO:** Commands Claude cannot guess (custom build steps, test runners, deployment flows), style conventions that differ from defaults, project-specific gotchas, environment setup quirks.
- **DON'T:** Information readable from the code itself, generic advice ("write clean code"), tool descriptions the harness already provides.

```markdown
<!-- Example CLAUDE.md -->
# Project: Acme API

## Build & Test
- `make build` compiles all services
- `make test-unit` runs unit tests (< 2 min)
- `make test-integration` requires Docker running

## Conventions
- All API handlers go in `internal/handlers/` with `_handler.go` suffix
- Use `slog` for logging, never `fmt.Print` in production code
- Error types must implement `APIError` interface from `pkg/errors`

## Gotchas
- The CI uses Go 1.23; do not use 1.24 features
- `make lint` runs golangci-lint with `.golangci.yml` — fix all issues before committing
```

### @import

CLAUDE.md supports `@import` directives for pulling in external files, with a maximum of 4 hops.

### Rules directory

`.claude/rules/*.md` files provide scoped rules. Each can have `paths:` frontmatter to limit when it applies:

```markdown
---
paths:
  - "apps/frontend/**"
---

Use React Server Components by default. Only add "use client" when the component needs browser APIs or state.
```

### Compaction behavior

The project-root CLAUDE.md survives compaction and is re-injected. Nested CLAUDE.md files from subdirectories do not re-inject after compaction — put critical instructions at the root level.

Source: https://docs.claude.ai/en/memory

---

## 7. Permission Modes and Rules

Claude Code's permission system controls which tools and commands can execute without user confirmation.

### Permission modes

| Mode | Behavior |
|------|----------|
| `ask` | Prompt user for every tool call (default) |
| `auto` | Allow listed tools without prompting |
| `trust` | Allow all tools without prompting |
| `deny` | Block specific tools entirely |

### Settings precedence

Settings follow: managed > CLI flags > local > project > user. However, permission rules **merge** across all scopes — they are not overridden. A `deny` rule at any scope wins over `allow` at any other scope.

### Permission rule format

```jsonc
// .claude/settings.json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(npm test)",
      "Bash(npm run lint)",
      "mcp__github__list_issues"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force*)"
    ]
  }
}
```

Tool names in permission rules must match the exact built-in tool names or MCP tool naming pattern (`mcp__<server>__<tool>`). Bash permissions use glob patterns on the command string.

### Subagent permission modes

Subagents can declare their own `permissionMode` in frontmatter. Plugin-defined agents have their `permissionMode` silently ignored — this is a known harness limitation.

Source: https://docs.claude.ai/en/settings

---

## 8. Plan Mode

Plan mode restricts the model to read-only operations — it can explore the codebase and reason about an approach but cannot write, edit, or execute side effects. The model exits plan mode via the `ExitPlanMode` tool when ready to implement.

### When to use plan mode in prompts

Prompts that involve multi-step architectural decisions benefit from instructing the model to plan first:

```markdown
## Workflow
1. Enter plan mode. Read the codebase and propose an implementation plan.
2. Wait for user approval of the plan.
3. Exit plan mode and implement the approved plan.
```

### Plan mode and subagents

The built-in `Plan` agent type automatically operates in plan mode. It has access to all read-only tools but cannot use `Edit`, `Write`, or `NotebookEdit`. Similarly, the `Explore` agent type is read-only and skips CLAUDE.md loading entirely.

Source: https://docs.claude.ai/en/tools-reference

---

## 9. Headless Mode and Agent SDK

Claude Code can run non-interactively for CI/CD pipelines, automated workflows, and custom agent systems.

### Headless CLI

```bash
# Run a prompt non-interactively with JSON output
claude -p "Analyze this codebase for security issues" --output-format json

# Pipe input
echo "Fix the failing test in tests/auth.test.ts" | claude -p --output-format json
```

### Agent SDK

The Agent SDK (Python and TypeScript) provides programmatic access to Claude Code's capabilities:

```python
from claude_code import query

result = await query(
    prompt="Review the PR diff and report issues",
    options={
        "model": "claude-fable-5",
        "permission_mode": "auto",
        "allowed_tools": ["Read", "Grep", "Bash(git diff*)"],
    }
)
```

Hooks can be registered as callbacks in the SDK, giving full programmatic control over the hook lifecycle.

### Key considerations for prompts

- Headless mode has no interactive user — prompts must not include `AskUserQuestion` calls.
- Permission mode should be set to `auto` or `trust` with appropriate allow-lists.
- Output format (`json`) enables structured parsing of results.
- The SDK's `query()` function accepts the same tool and permission configuration as the CLI.

Source: https://docs.claude.ai/en/agent-sdk

---

## 10. Prompt Engineering Rules for the Harness

### What a well-engineered prompt should do

1. **Reference tools by name, never re-describe them.** The harness injects tool schemas. Prompts should only mention tools to constrain behavior ("use `Edit` instead of `Write` for existing files") or grant permissions.

2. **Use skills for progressive disclosure.** Heavy reference material belongs in skill `references/` directories, not inlined in CLAUDE.md. Load it on demand.

3. **Put deterministic requirements in hooks, not instructions.** If a lint check must run before every commit, configure a `PreToolUse` hook on `Bash(git commit*)` — don't rely on "always run lint before committing" in CLAUDE.md.

4. **Scope rules with paths.** Use `.claude/rules/*.md` with `paths:` frontmatter or skill `paths:` to avoid loading irrelevant instructions.

5. **Design for compaction.** Root CLAUDE.md survives compaction; nested files and long skill bodies get truncated. Front-load critical instructions.

6. **Brief subagents completely.** The agent body is the entire system prompt. Include all context the agent needs — it has no access to your CLAUDE.md or conversation history (unless forked).

7. **Batch ToolSearch calls.** When working with deferred MCP tools, load all needed schemas in a single `ToolSearch` call.

Source: https://docs.claude.ai/en/tools-reference, https://docs.claude.ai/en/memory, https://docs.claude.ai/en/hooks
