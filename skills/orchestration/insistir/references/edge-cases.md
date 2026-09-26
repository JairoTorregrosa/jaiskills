# Edge cases

Read when something in the run deviates from the happy path in SKILL.md. `<state>` is the run
state dir named in SKILL.md (`~/.claude/insistir-state/<session id>/`).

## Completion gate blocks a task you believe is approved

The TaskCompleted hook allows a plan task (`T<N>: ...` subject) completed in this session only
when `<state>/<key>.approved` exists, `<key>` being the plan id with every char outside
`[A-Za-z0-9_-]` replaced by `_` (`T3`, `T1_2` for `T1.2`). Check in order: the subject starts with
`T<N>:`; the marker path uses this session's id; the marker filename. The hook's stderr prints the
exact command. Never write a marker to get past the gate without an APPROVED outcome.

## Stale state

- Resumed session (same session id): `<state>` may still hold markers from an earlier attempt.
  Phase 2 deletes `*.approved` before creating tasks; never skip that.
- Crashed runs leave `~/.claude/insistir-state/<other id>/` dirs behind. They cannot gate this
  session, but the reviewer Bash filter reads every `allowed_commands.txt`, so stale dirs widen
  the whitelist. List them with their `run.json` (topic, plan, start time) and offer the user to
  delete the ones not running now: `find <dir> -maxdepth 1 -type f \( -name '*.approved' -o -name
  allowed_commands.txt -o -name run.json \) -delete && rmdir <dir>` (no bare `*.approved` glob:
  zsh aborts on an unmatched glob).

## Agent teams unavailable mid-run

A named Agent spawn fails, or teammates never report: agent teams are off or the session is not
interactive. Switch the rest of the run to subagent mode (SKILL.md, Modes), record it in
`run.json` and the summary, and continue from the current wave.

## Reviewer report is not valid JSON

Treat it as REVISE. Pass the raw report to the fixer under `Review Findings`. Two non-JSON
reports in a row for the same task: tell the user; do not loop.

## Reviewer cannot run a validation command

The Bash filter blocks anything outside its whitelist and the `allowed_commands.txt` files, and
blocks write flags (`--fix`, `--write`, formatter `-w`, `--allow-dirty`, git branch mutation).
If the plan's validation command was not seeded, append its prefix to
`<state>/allowed_commands.txt` (prefixes starting with `rm`, `curl`, `wget`, `bash`, `sh `,
`python -c`, `sudo` and similar are ignored by the hook) and spawn a fresh reviewer for the same
round. A validation command that needs a write flag is not a verification command: ask the user.

## Worker commit collisions

Parallel workers share one index. Workers commit with `git commit -m "…" -- <paths>`, so a
commit carries only its own paths. An `index.lock` error means another agent was mid-commit:
the worker retries after a few seconds. A worker report whose commit lists another task's files
→ tell the user before reviewing; do not let the next reviewer judge mixed commits.

## Worker reports it is blocked or failed

Do not spawn a reviewer for unfinished work. End the worker (team mode: `shutdown_request`),
then either spawn a fresh worker with the blocker added to the prompt (same round), or mark the
task failed and ask the user. Two blocked workers on one task: stop and decompose with the user.

## Project stop hooks fire during a wave

Project-level hooks (typecheck, lint on Stop) may report errors from workers' in-progress code
on the lead's turn. Ignore them until every worker in the wave has reported.

## Judge problems

`second-opinion` retries malformed or vacuous verdicts and falls back to a same-provider judge on
its own. If the Skill tool call itself fails twice in the session (skill not installed, repeated
errors), stop calling it, let reviewer verdicts stand alone, and record `judge: unavailable` per
task. Never wait on judge recovery. Args not starting with `judge` run advise mode instead: the
output then has no band; rerun with `judge` first.

## Round budget exhausted

REVISE at `round == max_review_rounds`: file TODOs if the user opted in, mark the task failed,
write `Exceeded review budget (<N> rounds). Decompose.` in the plan task's `log`, spawn no fixer.
Dependent tasks stay blocked; ask the user whether to decompose now or stop the run.

## Deadlock

No crew agent active, tasks still pending, nothing unblocked (circular or failed dependency):
report the task graph state to the user and stop spawning.

## Teammate ignores shutdown (team mode)

Send one more `shutdown_request` with "All work is done. Shut down now." and wait about 10
seconds. Still alive: tell the user its name and continue; team state is removed when the session
ends. Never loop waiting on an unresponsive agent.
