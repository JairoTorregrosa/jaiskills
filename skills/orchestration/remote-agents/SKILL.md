---
name: remote-agents
description: "Orchestrate headless Claude Code and Codex agents on a remote SSH host (Jetson) from this Mac. Use when: (1) user says /jaiskills:remoto-run or /jaiskills:remoto-status, (2) 'remote agents', 'spawn on the jetson', 'run this on the jetson', 'remote swarm', (3) work should execute on the remote box (its GPU, its files, its environment) while this session coordinates. Do NOT use for local-only tasks or when the remote host is unreachable."
---

You are the **orchestrator** on macOS. Workers are headless `claude -p` / `codex exec` processes on a remote SSH host (default `jetson`; Tailscale fallback `jetson-ts`). Both CLIs are already logged in on the remote. You never implement remotely yourself — you spawn jobs, poll, collect results, and synthesize.

## Engines and roles (harness-agnostic)

Both engines are invoked the same way: headless CLI, prompt on stdin, answer as final message — **never** via the Codex MCP server or any other harness-specific channel. Role is orthogonal to engine: any engine can be implementer, reviewer, or judge; only the prompt changes. Model policy:

| Role | Engine / model | Spawn flags |
|---|---|---|
| Orchestrator | Fable 5 — this session, always. Never delegated. | — |
| Implementer (default) | Codex `gpt-5.6-sol` at high reasoning | `-e codex -m gpt-5.6-sol -r high` |
| Implementer (alt, when the user asks for claude) | Claude Code headless | `-e claude [-m opus]` |
| Reviewer | The engine that did NOT write the work | per engine above |
| Judge (final verdict on a review loop) | Codex `gpt-5.6-sol -r high` — cross-provider bias-free | `-e codex -m gpt-5.6-sol -r high` |

`-r/--effort` maps to Codex `model_reasoning_effort`; it is codex-only (claude headless has no effort flag — the script rejects it).

All mechanics go through one script:

```bash
REMOTO="${CLAUDE_PLUGIN_ROOT}/scripts/remoto.sh"
```

## CLI quick reference

| Command | Purpose |
|---|---|
| `$REMOTO hosts` | Probe hosts (up/down, CLI versions, load) |
| `$REMOTO spawn -e claude\|codex -d <remote-dir> [-m model] [-r effort] [-n name] [--safe] -` | Launch worker, prompt on stdin. Prints job id |
| `$REMOTO ls` / `status <id>...` | Fleet / job state: RUNNING, DONE, FAILED(rc), DEAD |
| `$REMOTO wait [-t secs] <id>...` | Block until all finish (poll 15s). Exit 0 all DONE, 1 any failed, 124 timeout |
| `$REMOTO logs [-f] <id>` | Tail stderr + stdout |
| `$REMOTO result <id>` | Final answer (claude: parsed from stream-json; codex: last message) |
| `$REMOTO kill <id>` / `clean` | Kill process group / delete finished job dirs |
| `$REMOTO push <local> <remote>` / `pull <remote> <local>` | rsync payloads and artifacts |

Target a different host per invocation with `REMOTO_HOST=jetson-ts $REMOTO ...`.

## Orchestration workflow

1. **Probe.** `$REMOTO hosts`. If the primary is DOWN, try `REMOTO_HOST=jetson-ts`; if both are down, stop and tell the user.
2. **Prepare the remote workspace.** Every job needs an existing remote directory: verify with `ssh jetson 'ls <dir>'`, clone a repo remotely, or `$REMOTO push`. Give parallel workers that touch the same repo **separate clones or worktrees** — remote workers cannot coordinate with each other.
3. **Write worker prompts.** Remote workers have zero context from this conversation — each prompt must be fully self-contained. Build it from `references/prompt-templates.md` (model-specific templates; read it before writing your first prompt). Always keep the template's REPORT contract so results are machine-collectable.
4. **Spawn.** Pipe the prompt via stdin (never inline-quote a multi-line prompt):
   ```bash
   $REMOTO spawn -e claude -d ~/code/proyecto -n api-worker - <<'PROMPT'
   ...full self-contained prompt...
   PROMPT
   ```
   Spawn independent jobs back-to-back in one Bash call; capture each printed job id. Default implementer is `codex -m gpt-5.6-sol -r high`; reviewers always the other engine; judge codex (see role matrix above).
5. **Wait without blocking the user.** Run `$REMOTO wait <ids>` via Bash with `run_in_background: true`, then continue any local work. Remote jobs can take many minutes. Spot-check long jobs with `logs`.
6. **Collect.** For each job: `status`, then `result <id>`, and read the REPORT block. If FAILED or DEAD, get `logs <id>` before deciding to respawn — never silently retry.
7. **Cross-review (recommended for nontrivial work).** Spawn a fresh reviewer on the *other* engine over the worker's diff (`git -C <dir> diff` output embedded in the reviewer prompt, or the reviewer runs it itself in the same workdir). Reviewer template is in the references. Iterate: findings → fixer job → re-review, max 2 rounds. For high-stakes changes, close with a **judge** job (codex `gpt-5.6-sol -r high`, judge template) that scores the final review verdict instead of re-reviewing the code.
8. **Verify and deliver.** Pull artifacts with `$REMOTO pull` if needed, run/inspect what came back, then report to the user: what ran where, results, failures, and remote paths. `$REMOTO clean` when the user is done with the batch.

## Rules

- **Self-contained prompts.** The #1 failure mode is a prompt that references context the remote model can't see. Include: repo path, task, constraints, verification commands, and the REPORT contract.
- **One job = one task.** Don't pack multiple deliverables into a single worker; spawn parallel jobs instead.
- **Permissions default.** Jobs run with permissions bypassed (it's Jairo's own Jetson). Use `--safe` when the task only edits files and shouldn't run arbitrary commands.
- **Don't kill what you didn't spawn.** `ls` shows all jobs on the host, including ones from other sessions.
- **Ground your report.** Only claim a job succeeded after seeing its DONE status *and* its result/REPORT — a DONE exit with an error-shaped result is a failure.
- **No background remnants.** Headless processes die with their background children: every worker prompt must say "do all polling/waiting synchronously; do not leave background tasks running; your final message must contain all evidence." A worker whose final message says "waiting for background tasks" produced an incomplete result — verify its work directly or respawn.
