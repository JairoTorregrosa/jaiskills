# Resolve mode: implement ready TODOs with parallel workers

Run only when the user asks: workers edit code and commit. One worker per TODO, grouped into dependency waves.

## 1. Load ready TODOs

Glob `todos/*-ready-*.md`. If the request carries IDs or a filter (`003`, `p1`, a tag), keep only matching files.

None found → tell the user "No ready TODOs to resolve." and offer triage mode ([triage.md](triage.md)) if anything is pending. Stop.

## 2. Close protected TODOs first

A TODO whose Recommended Action deletes `docs/plans/` or `docs/solutions/` is never executed; those directories are intentional pipeline artifacts. For each:

1. Rename to `todos/{id}-complete-{priority}-wont-fix-{description}.md`; frontmatter `status: complete`, `updated: <today>`.
2. Append to Work Log: "Skipped: recommends deleting pipeline artifacts (docs/plans/ or docs/solutions/). These directories are intentional and must be preserved."

## 3. Build waves

Read `dependencies` from each frontmatter (IDs like `["001", "005"]`).

- A dependency that is `complete` is satisfied.
- A dependency that is `pending`, missing, or outside the selected set blocks the TODO: report it and leave it `ready`.
- **Wave 1**: TODOs with all dependencies satisfied. **Wave N**: TODOs whose dependencies are all in waves < N.
- A cycle → report the IDs involved and stop.
- Two TODOs in the same wave whose Findings or Recommended Action touch the same file → move the higher ID to the next wave. Workers share one working tree; parallel edits to one file collide.

## 4. Run each wave

Spawn one worker per TODO in the wave, all in one message so they run in parallel. Wait for the whole wave before starting the next.

Worker type: `subagent_type: "jaiskills:insistir-worker"` (a plugin agent). When that type is not available (skills.sh or other non-plugin installs ship no plugin agents), spawn a general-purpose subagent with the same brief. No subagent support at all → resolve the TODOs yourself, one at a time, following the same brief.

Brief (fill the braces; the worker has no conversation history):

```
name: todo-resolver-{id}
subagent_type: jaiskills:insistir-worker
prompt: |
  ## Context
  You are resolving one TODO filed from a review finding. Other workers are
  resolving other TODOs in this same working tree at the same time.

  ## Task
  Read todos/{id}-ready-{priority}-{description}.md.
  Implement the Recommended Action. Every Acceptance Criteria item must pass.
  Touch only the files this TODO needs. Do not edit the TODO file itself.

  ## Finish
  1. Run the relevant validation (tests, typecheck, lint) and fix failures.
  2. Commit only your files, by path, so parallel workers never commit each
     other's staged changes: git add <paths> && git commit -m "fix: resolve todo
     {id} - {description}" -- <paths>. Never git add -A or ., never push.
     On a git index.lock error, wait a few seconds and retry.
  3. Report: files changed, commit hash, validation commands with their
     results, and any acceptance criterion you could not meet. If you run in
     a team, send this to the lead with SendMessage; otherwise it is your
     final message.
```

## 5. Record the outcome

Per worker, after its report:

**Success** (commit exists, validation passed, every criterion met):
1. Rename `ready` → `complete` (`git mv` if tracked); frontmatter `status: complete`, `updated: <today>`.
2. Append to Work Log:
   ```
   ### YYYY-MM-DD
   - Resolved by worker agent
   - Changes: [files from the worker's report]
   - Commit: [hash]
   ```

**Failure or partial**: leave it `ready`, append a dated Work Log entry with what failed and the evidence, and count it as failed. Dependents in later waves are now blocked: skip them and say so.

Verify before marking complete: the commit hash exists (`git log -1 <hash>`) and touches the claimed files. A report without a commit is a failure.

## 6. Summary

```
## Resolution summary

- Resolved: [N]
- Skipped (protected): [N]
- Blocked (dependencies): [N]
- Failed: [N]

### Wave details
| Wave | TODO | Worker | Status |
|------|------|--------|--------|
| 1    | 001  | todo-resolver-001 | complete |
| 1    | 003  | todo-resolver-003 | complete |
| 2    | 005  | todo-resolver-005 | failed   |
```
