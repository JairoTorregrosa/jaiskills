---
title: "Amp Harness Deep Dive"
last_verified: 2026-07-18
sources_verified: true
---

> **Verification note** — Every section was researched against live documentation on 2026-07-18. Source URLs are listed at the end of each section. Amp is in "Research Preview" and ships changes weekly — re-verify billing/mode details before relying on them.

# Amp Harness Deep Dive (Sourcegraph)

Amp is Sourcegraph's multi-model agentic coding tool (CLI/TUI, VS Code/Cursor/Windsurf/JetBrains/Neovim/Zed extensions, web at ampcode.com). Core concepts: **threads** (persistent, shareable conversation containers, `@T-<id>` references), **orbs** (remote execution machines — close your laptop, resume anywhere), **runners** (headless `amp --no-tui --runner-id <id>`), **subagents** (up to 7 parallel workers; inter-agent messaging since 2026-07-17), and the **oracle** (built-in second-opinion reasoning model).

Key difference vs Claude Code/Codex: **no model picker** — Amp routes among frontier models automatically per mode/task; you influence routing by prompt framing and mode selection, not model names. Threads live on Sourcegraph servers (no local-only mode).

Source: https://ampcode.com/manual
Source: https://ampcode.com/chronicle

---

## 1. Instructions files

- **`AGENTS.md`** is the standard (also reads legacy `AGENT.md` and `CLAUDE.md` for compatibility).
- Locations, all auto-included: cwd + parents up to `$HOME`; subtree AGENTS.md files when the agent reads into subdirectories; `~/.config/amp/AGENTS.md` and `~/.config/AGENTS.md`; system-wide `/etc/ampcode/AGENTS.md` (Linux) / `/Library/Application Support/ampcode/AGENTS.md` (macOS).
- **Glob-scoped instructions** via YAML frontmatter (`globs: ['**/*.ts']`) — a metaprompt can target file types, not just directories.
- **@-mentions**: `@path/file.md` (globs like `@doc/*.md` supported) pull other files in.
- Amp can auto-generate AGENTS.md from `.cursorrules`, `.windsurfrules`, `CLAUDE.md`, `.github/copilot-instructions.md`, etc.

Source: https://ampcode.com/news/AGENT.md
Source: https://ampcode.com/manual

---

## 2. Config, skills, permissions, MCP

- **Settings** (JSON/JSONC, `amp.` prefix): user `~/.config/amp/settings.json`, workspace `.amp/settings.json`, enterprise managed-settings paths.
- **Skills**: `SKILL.md` files with `name`/`description` frontmatter; search precedence `~/.config/agents/skills/`, `~/.agents/skills/`, `~/.config/amp/skills/`, project `.agents/skills/`, legacy `.claude/skills/`. Skills can bundle MCP servers via `mcp.json` — tools stay hidden until the skill loads.
- **Custom commands**: `.agents/commands/`. **Custom review checks**: `.agents/checks/` (Markdown + frontmatter, inherit to subdirectories).
- **Permissions**: default is **full-auto — Amp does not ask before tool calls**. Guardrails via `amp.permissions` rules (first match wins; actions `allow`/`ask`/`reject`/`delegate` to an external program via exit codes), with per-tool parameter matching (`{"tool": "Bash", "matches": {"cmd": "*git commit*"}, "action": "ask"}`) and `mcp__*` wildcards. CLI: `amp permissions edit|add|test`. A generated prompt that assumes an approval gate (like Claude Code's) is wrong here — state destructive-action policy in AGENTS.md or ship a permissions block.
- **MCP**: full local + remote (HTTP/SSE) support via `amp.mcpServers`, OAuth for remote servers, workspace servers need `amp mcp approve <name>`.
- **Plugins**: TypeScript in `.amp/plugins/*.ts` — events (`tool.call` can allow/reject/modify/synthesize), custom tools, commands, even custom agent modes (`amp.experimental.registerAgentMode`).

Source: https://ampcode.com/manual
Source: https://ampcode.com/permissions
Source: https://ampcode.com/news/tool-level-permissions

---

## 3. Built-in tools (do not re-specify)

`Bash`, `Read`, `Grep` (ripgrep), `Glob`, `create_file`, `edit_file`, `undo_edit`, `get_diagnostics`, `read_web_page`, `web_search`, `read_mcp_resource`, `Task` (spawn subagents), `todo_read`/`todo_write`, `Finder`, `Oracle`. Enumerate the live set with `amp tools list`.

System-level subagents (not user-invocable): Librarian (cross-repo GitHub search, GPT-5.6 Sol), Painter (GPT Image 2), Review (GPT-5.5), Search (GPT-5.6 Terra), Read Thread (GLM-5.2).

Source: https://ampcode.com/manual/appendix
Source: https://ampcode.com/modes

---

## 4. Models and modes

Mode system (since 2026-07-09; old names smart/deep/rush/large deprecated), selected with `Ctrl+S`:

| Mode | Agent model | Oracle model | Use |
|---|---|---|---|
| `low` | GLM-5.2 | GPT-5.6 Sol | fast, cheap, small tasks |
| `medium` | GPT-5.6 Sol | GPT-5.6 Sol | default |
| `high` | GPT-5.6 Sol | Claude Fable 5 | hard tasks |
| `ultra` | Claude Fable 5 | GPT-5.6 Sol | most capable, open-ended |

Utility models: Gemini 3 Flash (media), Claude Haiku 4.5 (thread titles), GPT-5.6 Sol (context summarization). A metaprompt for Amp should be written model-agnostically (it may execute on GLM, GPT, or Claude depending on mode) and instead recommend the mode.

Source: https://ampcode.com/modes
Source: https://ampcode.com/chronicle

---

## 5. Billing and subscriptions

**BYOK was explicitly removed** ("No More BYOK") — you cannot bring raw API keys. Replaced by "customer-managed model provider connections": linking consumer subscriptions at `/settings/model-providers`.

Billing options (subscriptions launched 2026-07-18):

| Plan | Cost | Includes |
|---|---|---|
| Free tier | $0 | Amp Tab autocomplete, core agent, thread sharing, no token caps; free-tier data may feed analytics |
| Pay-as-you-go | min $5 credits | provider rates at zero markup; credits pool per workspace, expire after 1yr inactivity |
| Megawatt | $20/mo | low+medium modes, 750h small orbs, $20 usage, subscription linking |
| Gigawatt | $200/mo | all modes, 1,000h large orbs, $200 usage |
| Enterprise | +50% rates, $1,000 min | regional BYO-provider endpoints on request |

**ChatGPT Plus/Pro sub**: explicitly supported — link it at `/settings/model-providers` for cheaper/more GPT-5.6 usage ("link your ChatGPT subscription for more GPT-5.6 usage"). X Premium+/SuperGrok linkable too.

**Claude Pro/Max sub**: partial/less documented — a secondary source (yixscout comparison, below) states Amp supports Claude via your Max/Pro subscription, but the prominently documented first-party path is ChatGPT. Verify in `/settings/model-providers` before promising it; assume Claude usage otherwise bills through Amp credits.

Community proxy workarounds (BYOKEY, CLIProxyAPI, vibeproxy) turn consumer subs into API endpoints for Amp — these likely violate provider ToS (Anthropic explicitly since Feb 2026); flag, don't recommend.

CLI auth: access token from `/settings/security#access-token`, or `AMP_API_KEY` env var for non-interactive use.

Source: https://ampcode.com/news/no-more-byok
Source: https://ampcode.com/news/subscriptions
Source: https://ampcode.com/manual
Source: https://yixscout.com/compare/amp-code-vs-claude-code

---

## 6. Install and gotchas

```bash
curl -fsSL https://ampcode.com/install.sh | bash        # recommended
brew install ampcode/tap/ampcode
npm install -g @ampcode/cli                             # legacy path — Amp now ships as a Bun single-file executable
```

Package renamed from `@sourcegraph/amp` to `@ampcode/cli`; old aliases removed 2026-06-15 (`npm uninstall -g @sourcegraph/amp` first).

Gotchas: all threads stored server-side (privacy consideration for regulated code); default full-auto tool execution; subagent dependency tracking "not infallible" on tightly coupled code; mode-name scripts written before July 9 need updating; MCP workspace servers need explicit approval; Research Preview — expect churn.

Source: https://ampcode.com/news/npm-package-changes
Source: https://ampcode.com/manual
