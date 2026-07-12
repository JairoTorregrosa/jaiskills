---
name: resolve-todos
description: "Resolve approved TODOs in parallel using worker agents — one agent per TODO"
argument-hint: "[todo-ids...]"
disable-model-invocation: true
---

# Resolve Approved TODOs

Spawn parallel worker agents to resolve all `ready` TODOs. Each worker reads its assigned TODO, implements the recommended action, and marks it complete.

## Steps

### 1. Load Ready TODOs

Read all `todos/*-ready-*.md` files using Glob.

If an argument was provided (e.g., a specific ID like `003` or a pattern like `p1`), filter to only matching files.

If no ready TODOs found, tell the user: "No ready TODOs to resolve. Run `/insistir:triage` first to approve pending findings."

### 2. Parse Dependencies

For each ready TODO, read the `dependencies` field from YAML frontmatter. Dependencies reference other TODO IDs (e.g., `["001", "005"]`).

### 3. Group into Waves

Compute execution waves based on dependencies (same algorithm as plan wave computation):

- **Wave 1**: TODOs with no dependencies (or whose dependencies are already complete)
- **Wave 2**: TODOs that depend on Wave 1 items
- **Wave N**: TODOs that depend on Wave N-1 items

If circular dependencies are detected, report to the user and stop.

### 4. Execute Waves

For each wave, spawn **parallel `insistir:insistir-worker` agents** — one per TODO:

```
Task tool:
  name: "todo-resolver-{id}"
  subagent_type: "insistir:insistir-worker"
  prompt: |
    ## Context
    You are resolving a TODO from a review finding.

    ## Your Task
    Read the TODO file at: todos/{id}-ready-{priority}-{description}.md

    Implement the fix described in the **Recommended Action** section.
    Follow the **Acceptance Criteria** checklist — all items must pass.

    After implementation:
    1. Run any relevant validation (tests, typecheck, lint)
    2. Stage and commit with message: "fix: resolve todo {id} - {description}"
    3. Report completion to the lead via SendMessage
```

### 5. Mark Complete

After each worker completes and is shut down:

1. Rename the file from `ready` to `complete`:
   ```bash
   mv todos/{id}-ready-{priority}-{desc}.md todos/{id}-complete-{priority}-{desc}.md
   ```
2. Update the `status` field in YAML frontmatter from `ready` to `complete`
3. Update the `updated` date in frontmatter
4. Append to the **Work Log** section with what was done:
   ```
   ### YYYY-MM-DD
   - Resolved by worker agent
   - Changes: [files modified from worker's report]
   - Commit: [commit hash]
   ```

### 6. Protected Artifacts

Skip any TODOs that recommend deletion of `docs/plans/` or `docs/solutions/` directories. These are intentional pipeline artifacts.

For these TODOs:
1. Rename to `{id}-complete-{priority}-wont-fix-{description}.md`
2. Add to Work Log: "Skipped — recommends deleting pipeline artifacts (docs/plans/ or docs/solutions/). These directories are intentional and must be preserved."

### 7. Summary

After all waves complete, display resolution results:

```
## Resolution Summary

- Resolved: [N]
- Skipped (protected): [N]
- Failed: [N]

### Wave Details
| Wave | TODO | Worker | Status |
|------|------|--------|--------|
| 1    | 001  | todo-resolver-001 | complete |
| 1    | 003  | todo-resolver-003 | complete |
| 2    | 005  | todo-resolver-005 | complete |
```
