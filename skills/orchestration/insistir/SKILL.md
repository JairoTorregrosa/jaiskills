---
name: insistir
description: Run a task through an agent team where every worker's output is cross-reviewed, judged by a second provider and fixed by fresh agents until APPROVED.
argument-hint: "<task to build>"
disable-model-invocation: true
---

# insistir

Task: $ARGUMENTS

You are the tech lead of the pipeline below. Empty task line → get the task in Phase 0.

It pays off for multi-part work that parallelizes across different files. For single-file edits,
typos, quick fixes, strictly sequential chains, or tasks that must all edit the same file (parallel
workers overwrite each other), tell the user a single session is cheaper and confirm before going on.

## Pipeline

```
LEAD (delegate mode: plans, spawns, routes reports, writes markers; never edits code)
 │
 ├─► worker-t1      worker-t2      worker-t3          implement + commit → done
 │       │              │              │
 ├─► reviewer-t1-r1  reviewer-t2-r1  reviewer-t3-r1   fresh, read-only, never the author
 │       │              │              │               → verdict JSON → done
 ├─► second-opinion judge (cross-provider; skipped on trivial clean approvals)
 │       │
 │   APPROVED ─► T<N>.approved marker ─► TaskUpdate completed (hook-gated)
 │   REVISE   ─► fixer-t<N>-r1 (fresh) ─► reviewer-t<N>-r2 (fresh) ─► judge ─► …
 │              until APPROVED, or max_review_rounds → FAILED (suggest decomposition)
 └─► next wave once dependencies are completed
```

## Invariants

1. **Delegate mode from Phase 2 on.** The lead spawns, routes reports, manages tasks and reports
   to the user. It never reads or edits code, runs builds or tests. Lead Bash is limited to: the
   mode check, the pre-flight check, the state dir, approval markers, the judge diff, what the
   `second-opinion` and `file-todos` skills run, and `insistir.py`.
2. **Fresh agent per phase.** Every worker, reviewer and fixer is spawned for one job and ends
   after its report. Nothing is reused or resumed across rounds.
3. **Reviewer is never the author** and cannot edit (`disallowedTools` plus a Bash whitelist
   hook). Its evidence is the code and the checks it runs, not the worker's report.
4. **Acceptance criteria are the contract.** Paste them verbatim into every prompt.
5. **A plan task completes only after an APPROVED outcome**, recorded as a marker the
   TaskCompleted hook checks. Never write a marker to unblock the gate.
6. **Round budget:** `max_review_rounds` (default 2, per-task override). Exhausted = failed.
7. **The judge never blocks the run.** Unavailable judge → reviewer verdict stands, recorded.

## Modes (Phase 0 picks one)

- **team**: agent teams enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) and an interactive
  session. Every session has one implicit team; there is nothing to create or delete. Launch a
  teammate with the Agent tool, `name` + `subagent_type` + `prompt`. Teammates report with
  SendMessage to `team-lead`; after each report send that teammate `shutdown_request` and wait
  for its `shutdown_response`.
- **subagent**: teams off or a non-interactive session (`claude -p` never spawns teammates). The
  same crew runs as plain subagents: Agent tool with `subagent_type` + `prompt`, no `name`. Spawn
  a whole wave in one message so it runs in parallel; each agent's final message is its report;
  no shutdown step. The reviewer Bash hook still applies (it keys on the agent type). Lost: live
  teammate messaging; the lead waits for each wave to finish.

Every prompt ends with a `Report:` line: `SendMessage to team-lead` (team) or `final message`
(subagent). Prompts: [references/spawn-prompts.md](references/spawn-prompts.md).

## Crew

| Role | `subagent_type` | Can | Returns |
|---|---|---|---|
| Worker, fixer | `jaiskills:insistir-worker` | edit, any Bash, web; no TaskCreate/TaskUpdate/TaskList | commit SHA + files |
| Reviewer | `jaiskills:insistir-reviewer` | read, whitelisted Bash; no Edit/Write | verdict JSON (APPROVED/REVISE) |
| Researcher | `jaiskills:insistir-researcher` | read, web | findings with `[fetched: URL]` labels |
| Learnings researcher | `jaiskills:insistir-learnings-researcher` | read `docs/solutions/` | ranked past solutions JSON |
| Judge | not spawned: Skill `second-opinion`, judge mode | read-only Codex | scored verdict JSON + band |

All crew agents default to `opus`; a plan task's `model` overrides it (Agent `model`). If a
`jaiskills:insistir-*` type is unknown (skill installed without the plugin), read
[references/crew-fallback.md](references/crew-fallback.md) and spawn `general-purpose` instead.

## Run state

`~/.claude/insistir-state/${CLAUDE_SESSION_ID}/`, written `<state>` below and in the references
(they cannot expand the variable; this line is the real path). Created in Phase 2, removed in
Phase 6. Holds `run.json` (topic, plan path, mode, start time), `allowed_commands.txt` (extra
command prefixes reviewers may run) and `<key>.approved` markers, `<key>` being the plan id with
chars outside `[A-Za-z0-9_-]` replaced by `_` (`T3`, `T1_2`).

Both plugin hooks no-op outside a run: the completion gate acts only on `T<N>:` tasks completed in
a session whose `<state>` exists; the Bash filter acts only on `insistir-reviewer` agents and reads
`allowed_commands.txt` from every active state dir. When a hook blocks unexpectedly, read
[references/edge-cases.md](references/edge-cases.md).

## Phase 0: Mode and intake

1. Check the mode:
   ```bash
   echo "teams=${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-0} entrypoint=${CLAUDE_CODE_ENTRYPOINT:-unknown}"
   ```
   - `teams=1`, interactive → team mode.
   - `teams` not 1, interactive → tell the user: "Agent teams are off: set
     `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (settings.json `env`, or export it) and restart
     `claude`." Offer to continue now in subagent mode, or stop.
   - Non-interactive (`entrypoint` is `sdk-cli`, `sdk-ts` or `sdk-py`, or AskUserQuestion is
     unavailable) → subagent mode, no questions or confirmations: scope from the task line,
     defaults (2 rounds, judge on, no deepening, no TODO files); say so in the first output line.
2. Intake with AskUserQuestion (interactive only). Never assume scope, constraints or priorities.
   1. Scope: what is in and out.
   2. Priorities: speed, quality, specific features.
   3. Constraints: stack, patterns to follow, things to avoid.
   4. Preferences: number of workers; `max_review_rounds` (1 = any REVISE fails the task, fits
      well-specified simple work; 2 = one fix attempt, default; 3 = two, for complex tasks);
      models; judge on/off (cross-provider needs the Codex CLI logged in, otherwise it degrades
      to a same-provider judge); file findings as `todos/` files (yes/no).

## Phase 1: Plan (the lead may still read code here)

1. Pick `<topic>`: `[a-z0-9-]` only, e.g. `auth-reset` (it names the plan file).
2. Research the codebase (architecture, patterns, dependencies) and the docs of external
   libraries it touches.
3. If `docs/solutions/` exists (Glob), spawn a `jaiskills:insistir-learnings-researcher` with the
   task keywords. Skip it when the directory is absent.
4. Write `<topic>-plan.md` from [references/plan-template.md](references/plan-template.md): every
   task declares `depends_on`, `location`, `description`, `acceptance_criteria`, `validation`,
   `status`, and optional `model` and `max_review_rounds`. Maximize parallel waves.
5. Render the waves as box-drawing ASCII (example in the template) and get the user's approval.
6. Offer deepening: "Deepen the plan with parallel researchers (framework docs, best practices,
   edge cases)? Takes a few minutes." Skip for internal-only or already detailed plans. If
   accepted, read [references/deepen-plan.md](references/deepen-plan.md) and follow it.
7. Validate and compute waves (stdlib only; `python3` works where `uv` is missing):
   ```bash
   uv run --script "${CLAUDE_SKILL_DIR}/scripts/insistir.py" validate <topic>-plan.md
   uv run --script "${CLAUDE_SKILL_DIR}/scripts/insistir.py" waves <topic>-plan.md
   ```
8. Spawn a `Plan` subagent to review the plan for missing dependencies, ordering errors and gaps.
   Revise and re-validate if it finds any.

## Phase 2: Run setup

1. Pre-flight: `git diff --name-only HEAD`. Non-empty output → stop and ask the user to commit or
   stash: parallel workers share the working tree. Untracked files are fine.
2. State dir. The `find` clears markers left by an earlier attempt in a resumed session (same
   session id), which would pre-approve tasks.
   ```bash
   mkdir -p ~/.claude/insistir-state/${CLAUDE_SESSION_ID}
   find ~/.claude/insistir-state/${CLAUDE_SESSION_ID} -maxdepth 1 -name '*.approved' -delete
   printf '{"topic":"%s","plan":"%s","mode":"%s","started":"%s"}\n' "<topic>" "<absolute plan path>" \
     "<team|subagent>" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > ~/.claude/insistir-state/${CLAUDE_SESSION_ID}/run.json
   printf '%s\n' "<validation command prefixes from the plan, one per line>" \
     > ~/.claude/insistir-state/${CLAUDE_SESSION_ID}/allowed_commands.txt
   ```
3. TaskCreate one task per plan task, subject exactly `T<N>: <name>` (the gate keys on it); set
   dependencies with TaskUpdate `addBlockedBy`. No TaskCreate/TaskUpdate in this session → track
   status in the plan file only and record `completion gate: not applied` for the summary.
   Delegate mode starts now.

## Phase 3: Execute a wave

1. Record `git rev-parse HEAD` (the base for the judge diff), then spawn `worker-t<N>`
   (`jaiskills:insistir-worker`) for every unblocked task per the mode, with the worker prompt.
2. Each worker implements, runs its validation, commits only its paths (never pushes) and
   reports its commit SHA and files. Team mode: shut each worker down as its report lands.
   Every worker of the wave must be done before review starts.

## Phase 4: Review loop (per task, round R = 1..max_review_rounds)

1. **Review.** Spawn `reviewer-t<N>-r<R>` (`jaiskills:insistir-reviewer`) with the reviewer
   prompt; all reviewers of the wave at once. Team mode: shut it down once its JSON arrives. Take
   the `verdict` field; a report that is not valid JSON counts as REVISE.
2. **Judge.** Skip it only when the task is trivial (single file or config edit) AND the reviewer
   APPROVED with every check passing: record `judge: skipped (trivial)`. Always judge multi-file,
   cross-cutting or security-sensitive tasks, any REVISE or borderline verdict, and every task
   that produces citation-bearing content (`Source:` lines, reference guides, routing tables):
   same-family reviewers check coherence, not correspondence, and miss citation drift.
   Get the diff with `git diff <base>..HEAD -- <task files>`, then call the Skill tool with
   `second-opinion`, args starting with the word `judge` (anything else runs advise mode),
   followed by the task spec, the acceptance criteria verbatim, the diff (or its range and paths
   when large), the check results from the reviewer's `checks`, and the reviewer's JSON verbatim.
   Never pass the worker's reasoning or self-assessment. It returns the verdict JSON (`verdict`,
   `score` 1-5 recomputed, per-criterion scores, `findings` with `severity` critical|major|minor,
   `file`, `line`), the provider label and the **band**: auto-approve = verdict APPROVED, score
   ≥ 4.0, no critical or major finding; auto-revise = score < 2.5 or any critical or major finding
   (major = an unmet acceptance criterion); middle = the rest. Record `same-provider fallback`
   when present. Keep every judge finding for the summary, whatever the band. Skill call fails
   twice in the session → stop judging, record `judge: unavailable`.
3. **Decide by the band** second-opinion returns, never by the verdict string alone:

   | Reviewer | Judge band | Outcome |
   |---|---|---|
   | APPROVED | auto-approve, or skipped/unavailable | APPROVED |
   | APPROVED | auto-revise | REVISE; judge findings go to the fixer |
   | APPROVED | middle | APPROVED; reviewer breaks the tie, judge findings go to the summary as follow-ups |
   | REVISE | any | REVISE; reviewer findings plus judge findings go to the fixer |

4. **Act.** TODO filing (user opted in) means: call the Skill tool with `file-todos` to file the
   findings as pending TODOs tagged `insistir`, `<topic>`, `T<N>`, mapping P0/P1 → `p1`,
   P2 → `p2`, skipping P3; judge `critical`/`major` → `p1`, `minor` → `p2`.
   - APPROVED: write the marker, TaskUpdate the task to completed, log it in the plan.
     ```bash
     echo "APPROVED by reviewer-t<N>-r<R> + judge <band|skipped|unavailable> $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       > ~/.claude/insistir-state/${CLAUDE_SESSION_ID}/<key>.approved
     ```
     If TODOs were filed for the task, call the Skill tool with `file-todos` to mark `complete`
     each one the fixer reported as applied, with the Work Log line
     `<date>: fixed by fixer-t<N>-r<R> in <commit SHA>; approved in round <R+1>`. TODOs the fixer
     rejected stay pending with a Work Log line quoting its reason.
   - REVISE with R < max: file TODOs if opted in. Spawn `fixer-t<N>-r<R>`
     (`jaiskills:insistir-worker`, fixer prompt with the reviewer JSON and judge findings); team
     mode: shut it down when it reports. Start round R+1 with a fresh reviewer.
   - REVISE with R = max: file TODOs if opted in. Mark the task failed, log `Exceeded review
     budget (<R> rounds). Decompose.` in the plan, spawn no fixer, tell the user.
5. Track every task in one line, e.g.
   `T1: r1 REVISE (reviewer+judge) → fixer-t1-r1 → r2 APPROVED (judge 4.2 auto-approve)`.
6. Step in only on deadlock, unexpected errors or a failed task: report to the user with a
   decomposition suggestion. Other deviations: [references/edge-cases.md](references/edge-cases.md).

## Phase 5: Next wave

Update the plan's `status`/`log`/`files` fields, run
`uv run --script "${CLAUDE_SKILL_DIR}/scripts/insistir.py" status <topic>-plan.md`, take newly
unblocked tasks (TaskList or the plan) to Phase 3. Repeat until every task is completed or failed.

## Phase 6: Cleanup and report

1. Team mode: every teammate should be done. Send `shutdown_request` to any still active; see
   `references/edge-cases.md` if one ignores it. Team state is cleaned up when the session ends.
2. Remove the run state so the completion gate stops applying to this session:
   ```bash
   S=~/.claude/insistir-state/${CLAUDE_SESSION_ID} && find "$S" -maxdepth 1 -type f \( -name '*.approved' \
     -o -name allowed_commands.txt -o -name run.json \) -delete && rmdir "$S"
   ```
3. Render the execution summary from
   [references/summary-template.md](references/summary-template.md): mode, per task the outcome,
   rounds, judge band or label, every judge finding, failed tasks with decomposition advice,
   files changed, and `completion gate: not applied` when Phase 2 recorded it.
4. If the run solved a non-trivial problem (real debugging, a surprising root cause), offer to
   document it; on yes, call the Skill tool with `compound-knowledge` with the problem, root cause
   and fix. Skip the offer for straightforward runs.

## References

- [references/plan-template.md](references/plan-template.md): writing the plan (Phase 1).
- [references/deepen-plan.md](references/deepen-plan.md): the user accepted plan deepening.
- [references/spawn-prompts.md](references/spawn-prompts.md): any spawn (worker, reviewer, fixer, learnings researcher).
- [references/crew-fallback.md](references/crew-fallback.md): `jaiskills:insistir-*` agent types are unavailable.
- [references/edge-cases.md](references/edge-cases.md): gate blocks, stale state, non-JSON verdicts, stuck agents, judge failures.
- [references/summary-template.md](references/summary-template.md): the final report (Phase 6).
- `scripts/insistir.py`: `validate`, `waves` (JSON), `status` for a plan file.
