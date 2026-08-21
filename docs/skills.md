# jaiskills — full component inventory

One plugin. Skills live under `skills/<category>/<skill>/SKILL.md`; commands, agents, hooks, and scripts are plugin-level.

## Skills

| Path | What it does |
|---|---|
| `skills/orchestration/insistir` | Main orchestration pipeline: intake, plan, execute, cross-review, judge, cleanup |
| `skills/orchestration/constatar-plan` | Author verification-first plans for the constatar engine |
| `skills/orchestration/constatar-verify` | Grounded verdicts through constatar's 6-rung evidence ladder |
| `skills/orchestration/goal-loop` | Loop engineering as gradient descent: agent factory, textual gradients, momentum, held-out evidence, anti-reward-hacking judge |
| `skills/orchestration/codex-judge` | Cross-provider LLM judge — scores review verdicts via Codex/GPT-5, dual-threshold gating |
| `skills/orchestration/remote-agents` | Headless agent fleets over SSH: probe, prepare, spawn, wait, collect, cross-review |
| `skills/prompting/metaprompt` | Generate complete prompts engineered for a specific model + harness |
| `skills/knowledge/compound-knowledge` | Capture solved problems as searchable documentation in `docs/solutions/` |
| `skills/knowledge/file-todos` | File-based TODO format, lifecycle, and management operations |
| `skills/openai/askcodex` | OpenAI GPT-5.x and image models as a CLI (text, images, quota) — canonical copy in the [askcodex repo](https://github.com/JairoTorregrosa/askcodex) |
| `skills/openai/image-to-frontend` | Reference image or brief → variants → build spec → working frontend, via askcodex |

## Commands

| Command | Does |
|---|---|
| `/insistir` (skill trigger) | Run the full insistir pipeline |
| `/advisor` | Second opinion from Codex/GPT-5 on plan, diff, or a question |
| `/goal` | Goal-loop descent: implement, verify, judge, iterate |
| `/compound` | Document a solved problem |
| `/triage` | Present pending TODOs one by one for user decisions |
| `/resolve-todos` | Parallel workers fix ready TODOs |
| `/deepen-plan` | Enrich a plan file with external research |
| `/metaprompt` | Generate a model/harness-specific prompt |
| `/constatar-run` | Drive a constatar plan end to end |
| `/constatar-verify` | Verify claims through the evidence ladder |
| `/constatar-audit` | Audit a constatar journal |
| `/remoto-run` | Spawn a remote headless agent job |
| `/remoto-status` | Check remote job state |

## Agents, hooks, config, scripts

| Component | Type | Does |
|---|---|---|
| `agents/insistir-worker.md` | Agent | Implements tasks or applies review fixes, commits, reports to lead |
| `agents/insistir-reviewer.md` | Agent | Cross-reviews with APPROVED/REVISE verdicts (read-only) |
| `agents/insistir-learnings-researcher.md` | Agent | Searches `docs/solutions/` for relevant past solutions |
| `agents/insistir-researcher.md` | Agent | Researches best practices, framework docs, codebase patterns |
| `hooks/hooks.json` + `task_completed.py` | Hook | Blocks task completion without review approval marker |
| `hooks/reviewer_bash_filter.py` | Hook | Whitelists read-only Bash for reviewer agents |
| `.mcp.json` | Config | Bundles the Codex MCP server for advisor/judge features |
| `scripts/remoto.sh` | Script | SSH job runner: spawn, status, wait, logs, result, kill, push, pull |
| `skills/orchestration/insistir/scripts/insistir.py` | Script | Plan validator CLI (validate, waves, status) |
| `references/constatar/` | Reference | Constatar engine reference material used by its commands |
