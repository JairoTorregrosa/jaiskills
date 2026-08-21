---
title: "Pi Harness Deep Dive"
last_verified: 2026-07-18
sources_verified: true
---

> **Verification note** — Every section was researched against live documentation on 2026-07-18. Source URLs are listed at the end of each section.

# Pi Harness Deep Dive

Pi is Mario Zechner's minimal, open-source terminal coding agent (`earendil-works/pi`, formerly `badlogic/pi-mono`; ~72k stars, v0.80.10 as of 2026-07-16). Philosophy: "If I don't need it, it won't be built" — ~1,000-token system prompt (vs Claude Code's 10k+), four core tools, no MCP, no permission rails ("always YOLO" — use containers for isolation), no hidden context injections, full observability, clean JSONL sessions. Layered TypeScript packages: `pi-ai` (multi-provider LLM API), `pi-agent-core` (loop), `pi-tui`, `pi-coding-agent` (CLI).

Do not confuse with `pi.ai` (Inflection) or the `oh-my-pi` fork.

Prompting implication: pi's minimal system prompt means a generated AGENTS.md carries MORE weight than in Claude Code — there is far less harness scaffolding to lean on, so spell out workflow conventions (planning, testing, commit habits) explicitly.

Source: https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
Source: https://github.com/badlogic/pi-mono

---

## 1. Instructions files

Pi concatenates context files from multiple locations, in order:

- **`AGENTS.md` and `CLAUDE.md`** — both conventions are read, from cwd, all parent directories, and `~/.pi/agent/`. If both exist, both load (watch for duplication/contradiction).
- **`.pi/SYSTEM.md`** (project) / `~/.pi/agent/SYSTEM.md` (global) — **replaces** the entire default system prompt. This is the metaprompt power-move unique to pi: you can own the whole system prompt.
- **`APPEND_SYSTEM.md`** — appends without replacing.
- Disable all context loading with `--no-context-files` / `-nc`.

Source: https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md
Source: https://pi.dev/docs/latest/quickstart

---

## 2. Skills, extensions, packages

- **Skills**: Markdown files following the Agent Skills standard; invoked via `/skill:name` or auto-loaded. Search paths: `~/.pi/agent/skills/`, `~/.agents/skills/`, `.pi/skills/`, `.agents/skills/` (cwd upward).
- **Extensions**: TypeScript modules (custom tools, commands, shortcuts, event handlers, UI) in `~/.pi/agent/extensions/`, `.pi/extensions/`, or installed packages. They execute arbitrary code — review before installing.
- **Packages**: `pi install npm:<pkg>` / git / HTTPS; manifest via a `"pi"` key in package.json. Project-local with `-l`.
- **No MCP by design** — expose capabilities as CLI tools with READMEs ("progressive disclosure") instead of MCP servers.

Source: https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md

---

## 3. Built-in tools (do not re-specify)

Four core tools: `read`, `write`, `edit` (exact `oldText` match), `bash` (synchronous only — no background bash; use tmux). Three optional read-only tools enabled via `--tools`: `grep`, `find`, `ls`. `--no-tools` disables all; extensions can add or replace tools.

Context management: auto-compaction near the limit (`compaction.enabled`, `reserveTokens` 16384, `keepRecentTokens` 20000 defaults), manual `/compact [prompt]`; full history stays in the session JSONL. Sessions are trees (`/tree`, `/fork`, `/clone`) in `~/.pi/agent/sessions/`.

Source: https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
Source: https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/settings.md

---

## 4. Config and models

Config is JSON: global `~/.pi/agent/settings.json`, project `.pi/settings.json` (merged over global), `auth.json` (OAuth tokens, 0600), `models.json` (custom providers), plus keybindings/themes/prompts dirs. Precedence: CLI args > project > global.

Providers (20+): subscription OAuth (Anthropic Claude Pro/Max, OpenAI ChatGPT Plus/Pro, GitHub Copilot) plus API-key providers (Anthropic, OpenAI, Google, Groq, OpenRouter, Ollama, vLLM, any OpenAI-compatible endpoint) over four API backends (OpenAI Completions/Responses, Anthropic Messages, Google Generative AI). Selection: `/model` (Ctrl+L), `--model <pattern>`, Ctrl+P cycles `enabledModels`. No hardcoded default — first run requires `/login` or an env key. Custom endpoints go in `models.json` (`baseUrl`, `api`, `models[]`). Cross-provider handoffs mid-session work but are lossy (thinking traces converted to `<thinking>` tags).

Source: https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/models.md
Source: https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/providers.md

---

## 5. Subscription auth

### Claude Pro/Max

Flow: `pi` → `/login` → "Claude Pro/Max" → browser OAuth → tokens in `~/.pi/agent/auth.json` (auto-refresh).

**Critical caveat (April 2026)**: Anthropic changed third-party billing — pi usage on a Claude sub now draws from **"extra usage" billed per token**, NOT your plan limits. Pi warns on login; you must enable and fund extra usage at claude.ai/settings/usage or requests fail with 400 `invalid_request_error`. So a Claude Max sub no longer gives pi "free" plan-limit usage.

Community workaround: the `pi-claude-auth` extension (`pi install npm:@pankajudhas81/pi-claude-auth`) reads Claude Code's own OAuth tokens (macOS Keychain / `~/.claude/.credentials.json`). **This violates Anthropic's ToS** (subscription tokens are restricted to official clients since Feb 2026, enforced since April 2026) and may break without notice — flag it, don't rely on it.

Fallback: `export ANTHROPIC_API_KEY=sk-ant-...` (API billing). Auth priority: `--api-key` > `auth.json` > env vars > `models.json` keys.

Source: https://github.com/earendil-works/pi/issues/3372
Source: https://pi.dev/docs/latest/providers
Source: https://pi.dev/packages/pi-claude-auth

### ChatGPT Plus/Pro

Flow: `/login` → "ChatGPT Plus/Pro (Codex Subscription)" → OpenAI device-code OAuth. **Officially endorsed by OpenAI ("Codex for OSS")** — no ToS friction, and models like `gpt-5.3-codex` are included in the subscription at no extra charge, subject to the plan's normal rate limits. This makes the ChatGPT sub the smoothest subscription path in pi.

Source: https://pi.dev/docs/latest/providers
Source: https://aiengineerguide.com/til/chatgpt-subscription-with-pi-coding-agent/

### GitHub Copilot (bonus)

`/login` → GitHub Copilot (github.com or GHE domain). If "model not supported," enable the model in VS Code Copilot Chat's picker first.

Source: https://pi.dev/docs/latest/providers

---

## 6. Install and gotchas

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent   # recommended
curl -fsSL https://pi.dev/install.sh | sh                          # alternative
```

Node 18+. The old package name `@mariozechner/pi-coding-agent` still resolves but is outdated. `--ignore-scripts` matters — dependency lifecycle scripts can break the install.

Gotchas: no permission checks at all (container it); no background bash; both AGENTS.md and CLAUDE.md load if present; Windows pnpm needs `pnpm approve-builds -g`; NixOS `pi install` needs a custom `npmCommand` in settings; `pi update --models` refreshes model lists.

Source: https://pi.dev/docs/latest/quickstart
Source: https://github.com/earendil-works/pi/issues/4399
