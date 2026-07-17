# Metaprompt Frontier Guides Plan

## Goal
Expand the `metaprompt` plugin's reference guides to cover all frontier models (Claude: Fable/Mythos 5, Opus 4.x, Sonnet, Haiku; OpenAI: GPT-5.6 Sol/Terra/Luna, GPT-5.x, Codex) and add two dedicated harness deep-dive guides (Claude Code tools, Codex tools) so generated prompts exploit each harness correctly.

## Constraints
- All technique claims must be grounded in sources actually fetched via WebFetch/WebSearch — no fabricated citations. Each section ends with a `Source:` line. Frontmatter: `last_verified: 2026-07-16`, `sources_verified: true`.
- GPT-5.6 family (Sol/Terra/Luna) went GA 2026-07-09 — primary sources: openai.com/index/previewing-gpt-5-6-sol, help.openai.com article 20001325, developers.openai.com docs/cookbook.
- Do NOT modify anything under `plugins/insistir/` or `plugins/remoto/`.
- English content. Keep the existing metaprompt evidence invariants passing: SKILL.md frontmatter `name: metaprompt`, mentions of "target model"/"harness"/"complete prompt", freshness/web-search instruction, `last_verified` in references, valid plugin.json.
- Workers each own distinct files — no overlapping edits. Only T5 touches SKILL.md/plugin.json.

## Config
- **max_review_rounds**: 2

## Tasks

### T1: OpenAI frontier models guide (GPT-5.6 Sol/Terra/Luna + GPT-5.x/Codex)
- **depends_on**: []
- **location**: plugins/metaprompt/skills/metaprompt/references/openai-models.md
- **description**: Research (web) and extend the OpenAI guide with the GPT-5.6 family — Sol (flagship, hardest problems), Terra (balanced), Luna (fast/cheap) — model-selection guidance, pricing tiers, prompting differences vs GPT-5.x, any new parameters or migration notes from OpenAI docs/cookbook; keep and refresh the existing GPT-5.x sections.
- **acceptance_criteria**: File mentions Sol, Terra, and Luna with per-model prompting guidance and a selection table; every new section has a `Source:` line with a URL actually fetched; frontmatter keeps `last_verified`/`sources_verified`; existing verified sections preserved unless superseded.
- **research_insights**:
  - Model IDs: `gpt-5.6-sol` (alias `gpt-5.6`), `gpt-5.6-terra`, `gpt-5.6-luna`. GA 2026-07-09, cutoff Feb 2026, 1,050,000-token context / 128k output, text+image in, text out. Pricing/1M: Sol $5/$30, Terra $2.50/$15, Luna $1/$6; >272K input tokens billed 2x input / 1.5x output; cache writes 1.25x, reads −90%. (developers.openai.com/api/docs/models/gpt-5.6-sol|terra|luna)
  - `reasoning.effort` has SIX levels: none/low/medium(default)/high/xhigh/max. New `reasoning.mode: standard|pro` (pro = more model work, single aggregated answer) independent of effort. New `reasoning.context: auto|all_turns|current_turn`. (developers.openai.com/api/docs/guides/reasoning, .../latest-model)
  - `text.verbosity: low|medium|high` — GPT-5.6 is MORE concise by default than 5.5; legacy "be brief" prompt rules now over-correct; use the parameter, not prompt text. (developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6)
  - Instruction-duplication penalty: stating each rule exactly once improved evals 10-15% and cut tokens 41-66%. Leaner prompts win; avoid vague tone adjectives — specify concrete behaviors; define autonomy boundaries (in-scope local changes without pausing; confirmation for external writes/destructive/purchases).
  - Programmatic Tool Calling (PTC): model writes JS to orchestrate tool calls in isolated runtime — reserve for bounded data-heavy workflows (filter/join/rank/aggregate); parallel calls alone do NOT justify it. Multi-agent "ultra" is beta — keep single-agent fallback. Prompt cache breakpoints: explicit prefix marking, 30-min minimum lifetime.
  - Selection: Sol = hardest coding/agents/research; Terra = default baseline for agent workflows; Luna = high-volume with reliable grader. Luna at xhigh effort can beat Sol at medium at lower cost (sebastianraschka.com/blog/2026/gpt-5-6-configurations.html). Migration: keep current effort as baseline then compare one level LOWER. Codex: `codex -m gpt-5.6-sol`, config.toml `model = "gpt-5.6"`; cloud tasks can't change default model (learn.chatgpt.com/docs/models).
  - Gotchas: no fine-tuning on any tier; no audio/video; SWE-Bench Pro: Sol 64.6% vs Claude Fable 5 80% (simonwillison.net/2026/Jul/9/gpt-5-6/).
- **validation**: `grep -ci 'sol' plugins/metaprompt/skills/metaprompt/references/openai-models.md` >= 3; `grep -qi 'terra' ...openai-models.md && grep -qi 'luna' ...openai-models.md`; `grep -c 'Source:' ...openai-models.md` >= 8
- **status**: complete
- **log**:
- **files**:

### T2: Claude frontier models guide (Fable/Mythos 5, Opus 4.x, Sonnet, Haiku)
- **depends_on**: []
- **location**: plugins/metaprompt/skills/metaprompt/references/claude-models.md
- **description**: Research (web, platform.claude.com) and extend the Claude guide with per-model guidance: Claude 5 family (Fable 5, Mythos 5), Opus 4.x, Sonnet (latest), Haiku 4.5 — effort/adaptive-thinking steering, model selection, differences in instruction-following across tiers; refresh existing sections against live docs.
- **acceptance_criteria**: File has per-model sections for Fable 5, Opus, Sonnet, Haiku with concrete prompting differences; every section has a `Source:` line with a fetched URL; frontmatter keeps `last_verified`/`sources_verified`.
- **research_insights**:
  - Lineup: Fable 5 (`claude-fable-5`, $10/$50/MTok, 1M ctx, 128k out, adaptive thinking ALWAYS on); Mythos 5 (same model, invitation-only); Opus 4.8 (`claude-opus-4-8`, $5/$25, thinking OFF unless `thinking:{type:"adaptive"}`); Sonnet 5 (`claude-sonnet-5`, $3/$15, intro $2/$10 until Aug 31 2026, adaptive ON by default); Haiku 4.5 ($1/$5, 200k ctx, legacy `budget_tokens` extended thinking only, NO effort param). Opus 4.1 retires Aug 5, 2026. (platform.claude.com/docs/en/docs/about-claude/models/overview)
  - Effort param levels low/medium/high(default)/xhigh/max via `output_config:{effort}`; Sonnet 5 medium ≈ Sonnet 4.6 high. Thinking `display` defaults to "omitted" on Fable 5/Opus 4.8/4.7/Sonnet 5 — set "summarized" to see it. Non-default temperature/top_p/top_k → 400 on Fable 5/Opus 4.7+/Sonnet 5. Prefilling last assistant turn removed from 4.6+ (400). (platform.claude.com effort + adaptive-thinking pages)
  - Fable 5 specifics: longer turns (adjust timeouts/streaming); brief instructions beat enumerated lists; ground progress claims against tool results; state action boundaries explicitly (takes unrequested actions); dispatches parallel subagents readily; file-based memory boosts it 3x more than Opus 4.8; `reasoning_extraction`-style prompts ("echo your reasoning") trigger classifier fallback to Opus 4.8; safety classifiers may block benign cyber/bio asks — configure fallback; avoid surfacing token countdowns ("You have ample context remaining"). (platform.claude.com .../prompting-claude-fable-5)
  - Opus 4.8: favors reasoning over tool calls (raise effort for more tool use); more literal at low effort; fewer subagents by default; design defaults cream/serif/terracotta — specify alternatives; "report every issue" pattern for review harnesses. Sonnet 5: more agentic + self-verification loops; new tokenizer ~30% more tokens (raise max_tokens); `computer_20251124` tool. Haiku 4.5: classification/high-volume/subagent tier. (per-model prompting pages)
  - Batch API `output-300k-2026-03-24` beta = 300k output on Opus 4.6+/Sonnet. Fable 5 was suspended Jun 12–30 2026 (export controls), redeployed Jul 1 with stricter classifier (anthropic.com/news/redeploying-fable-5).
- **validation**: `grep -qi 'fable' plugins/metaprompt/skills/metaprompt/references/claude-models.md && grep -qi 'haiku' ...claude-models.md && grep -qi 'sonnet' ...claude-models.md`; `grep -c 'Source:' ...claude-models.md` >= 8
- **status**: complete
- **log**:
- **files**:

### T3: Claude Code harness deep dive
- **depends_on**: []
- **location**: plugins/metaprompt/skills/metaprompt/references/claude-code-harness.md
- **description**: New guide (researched from code.claude.com docs): Claude Code's tool surface and how a generated prompt/CLAUDE.md/skill should exploit it — built-in tools (Read/Edit/Bash/Glob/Grep/WebFetch), subagents (Task), skills & progressive disclosure, slash commands, hooks, MCP, plan mode, permission modes, CLAUDE.md conventions, headless/SDK. For each capability: what it is, when the prompt should reference it, and an example prompt snippet.
- **acceptance_criteria**: Covers at minimum: subagents, skills, hooks, MCP, CLAUDE.md, plan mode, permission modes; each section has `Source:` line with fetched URL; includes >= 3 example prompt snippets; frontmatter has `last_verified: 2026-07-16` and `sources_verified: true`.
- **research_insights**:
  - Tool surface (code.claude.com/docs/en/tools-reference): file (Read/Write/Edit/Glob/Grep), Bash+Monitor, Web(Search/Fetch), orchestration (Agent/SendMessage/Task*), AskUserQuestion, Skill, Artifact, plan-mode tools, worktrees, Cron/ScheduleWakeup, NotebookEdit. Tool names are the exact strings for permission rules, subagent tool lists, hook matchers. Generated prompts must NOT re-specify built-in tools — harness provides them.
  - Skills (code.claude.com/docs/en/skills): SKILL.md <500 lines + progressive disclosure via linked references/; frontmatter incl. `description`, `when_to_use`, `context: fork`, `allowed-tools` (single-turn grant, clears on next user msg), `paths:` glob scoping, `disable-model-invocation: true` for side-effectful skills; dynamic injection with !`command`; `$ARGUMENTS`/`${CLAUDE_SKILL_DIR}` substitutions; skill content persists in context all session (compaction carries 5K/skill, 25K total); description budget 1,536 chars.
  - Subagents (docs/en/sub-agents): body = ENTIRE system prompt (no Claude Code system prompt); frontmatter tools/disallowedTools/model/permissionMode/maxTurns/skills/mcpServers/memory/background/effort/isolation; forks inherit full context; nesting depth 5; Explore/Plan skip CLAUDE.md; plugin agents' hooks/mcpServers/permissionMode silently ignored.
  - Hooks (docs/en/hooks): ~28 events; handler types command/http/mcp_tool/prompt/agent; exit 2 = block + stderr to Claude; PreToolUse can deny/allow/modify input; Stop can block turn end (max 8 consecutive); CLAUDE.md is advisory, hooks are deterministic — "must happen every time" → hook, not prompt.
  - MCP (docs/en/mcp): .mcp.json scopes local/project/user; `mcp__<server>__<tool>` naming; deferred tools need ToolSearch first; `claude mcp serve` exposes Claude Code as MCP server.
  - CLAUDE.md/memory (docs/en/memory): hierarchy managed→user→project→local, concatenated not overridden; `@import` (4 hops); `.claude/rules/*.md` with paths: frontmatter; target <200 lines; DO: commands Claude can't guess, style deltas, gotchas; DON'T: things readable from code, generic advice; project-root CLAUDE.md survives compaction, nested ones don't re-inject.
  - Settings/permissions (docs/en/settings): precedence managed>CLI>local>project>user, but permission rules MERGE across scopes (deny anywhere wins); permission modes ask/auto/trust/deny. Agent SDK (docs/en/agent-sdk): Python/TS `query()`, hooks as callbacks, headless `claude -p` with `--output-format json`.
- **validation**: `test -f plugins/metaprompt/skills/metaprompt/references/claude-code-harness.md`; `grep -c 'Source:' ...claude-code-harness.md` >= 6; `grep -qi 'subagent' ...claude-code-harness.md && grep -qi 'hook' ... && grep -qi 'mcp' ...`
- **status**: complete
- **log**:
- **files**:

### T4: Codex harness deep dive
- **depends_on**: []
- **location**: plugins/metaprompt/skills/metaprompt/references/codex-harness.md
- **description**: New guide (researched from developers.openai.com / learn.chatgpt.com): Codex CLI & Codex cloud tool surface — AGENTS.md discovery/merging, plan tool, sandbox modes (read-only/workspace-write/full-access), approval policies, exec/non-interactive mode, MCP support, tool preambles, parallel tool batching, Codex-specific prompting. For each capability: what it is, when the prompt should reference it, and an example prompt snippet.
- **acceptance_criteria**: Covers at minimum: AGENTS.md, plan tool, sandbox modes, approval policies, MCP; each section has `Source:` line with fetched URL; >= 3 example prompt snippets; frontmatter has `last_verified: 2026-07-16` and `sources_verified: true`.
- **research_insights**:
  - AGENTS.md (learn.chatgpt.com/docs/agent-configuration/agents-md): discovery global (~/.codex/AGENTS.override.md→AGENTS.md) then git-root→CWD, per-dir override→AGENTS.md→fallbacks; concatenated root-to-leaf, later overrides earlier; 32 KiB combined cap (`project_doc_max_bytes`); `--print-instructions` debugs merge. Content: project context, exact test/lint commands, conventions, dependency policy, per-directory overrides.
  - Sandbox (learn.chatgpt.com/docs/sandboxing): read-only / workspace-write / danger-full-access; macOS Seatbelt, Linux bwrap+seccomp; `.git`, `.agents`, `.codex` read-only even at full access. Approval policies (docs/agent-approvals-security): on-request / never / untrusted / granular; `approvals_reviewer = "auto_review"` = AI reviewer for exfiltration/credential/destructive checks.
  - CLI: `codex exec` for CI/non-interactive, `codex resume` (SQLite state), flags --image/--search/--sandbox/--ask-for-approval. config.toml (docs/config-file/config-reference): model, `model_reasoning_effort` (minimal|low|medium|high|xhigh), profiles with permissions.extends/filesystem/network.domains.
  - MCP: client mode via config.toml (STDIO + streamable HTTP, `default_tools_approval_mode`, timeouts); server mode `codex mcp-server` exposing codex()/codex-reply() with threadId — enables multi-agent delegation. Identity mismatch silently disables a server.
  - Prompting mechanics (developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide): plan tool `update_plan` (skip for trivial tasks, close all items Done/Blocked/Cancelled); parallel tool batching via `multi_tool_use.parallel` (decide all reads upfront); `phase` param ("commentary"/"final_answer") on GPT-5.3+ — dropping it degrades performance significantly; preamble pattern (ack + 1-2 sentence plan, update every 1-3 steps); personalities friendly/pragmatic; file refs `src/app.ts:42`; prefer apply_patch; prohibit destructive git.
  - Cloud (learn.chatgpt.com/docs/environments/cloud-environment.md): two-phase — setup (network+secrets) then agent (offline, secrets stripped); `export` doesn't persist between phases (use ~/.bashrc); 12h container cache. GPT-5-Codex model: 400K ctx, $1.25/$10; current surfaces run GPT-5.5; GPT-5.6 available via `codex -m gpt-5.6-*`.
- **validation**: `test -f plugins/metaprompt/skills/metaprompt/references/codex-harness.md`; `grep -c 'Source:' ...codex-harness.md` >= 5; `grep -qi 'AGENTS.md' ...codex-harness.md && grep -qi 'sandbox' ...`
- **status**: complete
- **log**:
- **files**:

### T5: Rewire SKILL.md routing + version bump
- **depends_on**: [T1, T2, T3, T4]
- **location**: plugins/metaprompt/skills/metaprompt/SKILL.md, plugins/metaprompt/.claude-plugin/plugin.json
- **description**: Update SKILL.md: model→reference-file routing table including GPT-5.6 Sol/Terra/Luna and Claude tiers; harness→reference-file routing (claude-code-harness.md, codex-harness.md); update workflow to load BOTH the model guide and the harness guide; keep freshness step and worked example consistent. Bump plugin.json version to 0.2.0.
- **acceptance_criteria**: SKILL.md routes every covered model to its file and both harnesses to their new files; still mentions "target model", "harness", "complete prompt", and the freshness web-search step; plugin.json valid with version 0.2.0.
- **validation**: `grep -qi 'claude-code-harness' plugins/metaprompt/skills/metaprompt/SKILL.md && grep -qi 'codex-harness' ...SKILL.md && grep -qiE 'sol|terra|luna' ...SKILL.md`; `python3 -m json.tool plugins/metaprompt/.claude-plugin/plugin.json`; `grep -q '"0.2.0"' plugins/metaprompt/.claude-plugin/plugin.json`
- **status**: complete
- **log**:
- **files**:

## Dependency Graph
T1 ─┐
T2 ─┼→ T5
T3 ─┤
T4 ─┘

## Parallel Execution Waves
| Wave | Tasks | Depends On |
|------|-------|------------|
| 1    | T1, T2, T3, T4 | - |
| 2    | T5    | T1, T2, T3, T4 |
