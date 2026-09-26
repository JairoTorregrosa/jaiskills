---
name: remote-agents
description: "Orchestrate headless Claude Code (`claude -p`) and Codex (`codex exec`) workers on a remote Linux SSH host (default `jetson`, override with REMOTO_HOST) from the local session: probe hosts, spawn jobs, wait, collect results, cross-review across providers, report fleet status. Use when work should run on a remote box (its GPU, files, environment) while this session coordinates: 'run this on the jetson', 'spawn remote agents', 'remote swarm', 'status of the remote jobs', 'córrelo en el jetson', 'lanza agentes remotos', 'cómo van los jobs remotos'. Also for checking or collecting jobs spawned earlier. NOT for local-only work or local subagents, and NOT usable without an SSH host that has key auth and a logged-in claude or codex."
argument-hint: "<task> [--host <ssh-host>] [--engine codex|claude|both] [--dir <remote workdir>] | status [job-id ...]"
---

You are the **orchestrator** in the local session. Workers are headless `claude -p` / `codex exec` processes on a remote SSH host. Never implement remotely yourself: spawn jobs, poll, collect, synthesize.

Request: $ARGUMENTS

## Runner and host

Every mechanic goes through one script in this skill's directory:

```bash
REMOTO="${CLAUDE_SKILL_DIR}/scripts/remoto.sh"   # other harnesses: absolute path of scripts/remoto.sh beside this SKILL.md
```

Host selection (environment; prefix any call, e.g. `REMOTO_HOST=gpu-box $REMOTO ls`):

| Variable | Effect | Default |
|---|---|---|
| `REMOTO_HOST` | Host every command targets | `jetson` (Jairo's Jetson) |
| `REMOTO_FALLBACK_HOST` | Second host `hosts` probes; retarget to it with `REMOTO_HOST=<it>` when the primary is DOWN | `jetson-ts` (Tailscale route) when `REMOTO_HOST` is unset, none otherwise |
| `REMOTO_HOSTS` | Explicit list for `hosts` | `$REMOTO_HOST $REMOTO_FALLBACK_HOST` |

A host is anything `ssh <host>` resolves (ssh config alias, `user@ip`, Tailscale name). The host must be Linux with key-based SSH (BatchMode, no prompts), bash, `setsid`, python3, and `claude` and/or `codex` logged in on PATH. Local side needs only ssh and rsync. Job state lives on the host in `~/.remoto/jobs/<id>/`, so jobs survive disconnects and are visible to every session.

## Arguments

Parse `$ARGUMENTS`; when empty (model-invoked), read the same fields from the user's latest message:

- `status [job-id ...]`, or a question about existing jobs → **Status mode** below. Do not spawn.
- `--host <h>` → prefix every call with `REMOTO_HOST=<h>`.
- `--engine codex|claude|both` → implementer engine (default `codex`). `both`: one implementer per engine on separate clones/worktrees, compare the two REPORTs, pick one, cross-review it with the other engine.
- `--dir <path>` → remote workdir. Quote tildes (`'~/code/x'`) so they expand on the host; the script refuses local-home paths.
- The rest is the task. No task and no status question → ask for the task.

## Engines and roles

Both engines are driven the same way: headless CLI, prompt on stdin, answer as final message, never through an MCP server. Role is orthogonal to engine; only the prompt changes.

| Role | Who | Spawn flags |
|---|---|---|
| Orchestrator | This session. Never delegated. | — |
| Implementer (default) | Codex at high reasoning | `-e codex -r high` |
| Implementer (alt: user asks for Claude, or `--engine claude`) | Claude Code headless | `-e claude` |
| Reviewer | The engine that did NOT write the work | per engine above |
| Judge (final verdict on a review loop) | The engine that did NOT write the work, so the author's provider never grades itself (default Codex implementer → Claude judge) | `-e claude`, or `-e codex -r high` when Claude implemented |

Models: omit `-m` and the host CLI uses its own configured default (`model` in the host's `~/.codex/config.toml`; Claude Code's model setting on the host). That config is the single place the current defaults live; change it there, not in prompts. Pass `-m <name>` only when the user names a model or the task needs a specific one. `hosts` prints each CLI's version.

`-r/--effort low|medium|high|xhigh` maps to Codex `model_reasoning_effort`; it is codex-only (headless claude has no effort flag; the script rejects it).

## CLI quick reference

| Command | Purpose |
|---|---|
| `$REMOTO hosts` | Probe hosts: UP/DOWN, CLI versions, load; first line names the target |
| `$REMOTO spawn -e claude\|codex -d <remote-dir> [-m model] [-r effort] [-n name] [--safe] -` | Launch a worker, prompt on stdin. Prints the job id |
| `$REMOTO ls` / `status <id>...` | Fleet / job state: RUNNING, DONE, FAILED(rc), DEAD, MISSING |
| `$REMOTO wait [-t secs] <id>...` | Block until all finish (poll 15 s, default timeout 7200). Exit 0 all DONE, 1 any failed, 124 timeout |
| `$REMOTO logs [-f] <id>` | Tail stderr + stdout |
| `$REMOTO result <id>` | Final answer (claude: parsed from stream-json; codex: last message) |
| `$REMOTO kill <id>` / `clean` | Kill the process group / delete finished job dirs |
| `$REMOTO push <local> <remote>` / `pull <remote> <local>` | rsync payloads and artifacts (mind trailing slashes) |
| `$REMOTO help` | Usage |

## Status mode

1. `$REMOTO hosts`.
2. Job ids given: `$REMOTO status <ids>`, then `$REMOTO result <id>` for each DONE. No ids: `$REMOTO ls` for the whole fleet.
3. For each FAILED or DEAD job, `$REMOTO logs <id>`.
4. Report: running, finished (with the REPORT status line of each result), failed (with the log tail that explains it).

## Orchestration workflow

1. **Probe.** `$REMOTO hosts`. Primary DOWN → retarget with `REMOTO_HOST=<fallback>`. All DOWN → stop and tell the user which hosts were tried.
2. **Prepare the remote workspace.** Every job needs an existing remote directory: check with `ssh <host> 'ls <dir>'`, clone the repo on the host, or `$REMOTO push`. Parallel workers on the same repo get **separate clones or worktrees**; remote workers cannot coordinate with each other.
3. **Write worker prompts.** Workers have zero context from this conversation; every prompt is self-contained. Read [references/prompt-templates.md](references/prompt-templates.md) before writing the first prompt and build from its engine-specific template. Keep its REPORT contract so results are machine-collectable.
4. **Spawn.** Pipe the prompt on stdin (never inline-quote a multi-line prompt):
   ```bash
   $REMOTO spawn -e codex -r high -d '~/code/project' -n api-worker - <<'PROMPT'
   ...full self-contained prompt...
   PROMPT
   ```
   Spawn independent jobs back to back in one shell call; capture every printed job id.
5. **Wait without blocking the user.** Run `$REMOTO wait <ids>` in the background (Claude Code: Bash with `run_in_background: true`) and keep doing local work. Jobs can take many minutes; spot-check long ones with `logs`.
6. **Collect.** Per job: `status`, then `result <id>`, then read the REPORT block. FAILED or DEAD → read `logs <id>` before deciding to respawn. Never retry silently.
7. **Cross-review (nontrivial work).** Spawn a fresh reviewer on the *other* engine over the worker's uncommitted diff in the same workdir (reviewer template). Findings → fixer job → re-review, max 2 rounds. High-stakes changes: close with a **judge** job (judge template) that scores the review loop instead of re-reviewing the code.
8. **Verify and deliver.** `$REMOTO pull` artifacts if needed, run or inspect what came back, then report: what ran on which host, results, failures, remote paths. `$REMOTO clean` once the user is done with the batch.

## Rules

- **Self-contained prompts.** The top failure mode is a prompt that references context the worker cannot see. Include repo path, task, constraints, verification commands, and the REPORT contract.
- **One job = one task.** Split multiple deliverables into parallel jobs.
- **Permissions.** Default is full bypass (claude `--dangerously-skip-permissions`, codex `--dangerously-bypass-approvals-and-sandbox`): use only on a host you own that holds nothing you cannot lose. Pass `--safe` when the task only edits files (claude `acceptEdits`, codex `--sandbox workspace-write`).
- **Do not kill what you did not spawn.** `ls` shows every job on the host, including other sessions'.
- **Ground the report.** A job succeeded only after DONE status *and* a result whose REPORT says success; DONE with an error-shaped result is a failure.
- **No background remnants.** Headless processes die with their background children. Every worker prompt says: "Do all polling/waiting synchronously; do not leave background tasks running; your final message must contain all evidence." A result that says "waiting for background tasks" is incomplete: verify the work directly or respawn.
