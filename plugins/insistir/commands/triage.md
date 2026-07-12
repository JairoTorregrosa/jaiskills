---
name: triage
description: "Triage review findings one by one — present pending TODOs for user decision (approve, skip, modify)"
model: haiku
argument-hint: "[filter]"
---

# Triage Pending TODOs

**DO NOT CODE ANYTHING DURING TRIAGE. This command is for decision-making only. Implementation happens in `/insistir:resolve-todos`.**

## Steps

### 1. Load Pending TODOs

Read all `todos/*-pending-*.md` files using Glob.

If an argument was provided (e.g., a specific ID like `003` or a pattern like `p1`), filter to only matching files.

If no pending TODOs found, tell the user: "No pending TODOs to triage. Create some from review findings first."

### 2. Sort by Priority

Order the pending TODOs for presentation:
1. **p1** (Critical) first
2. **p2** (Important) second
3. **p3** (Nice-to-have) last

Within the same priority, sort by ID (ascending).

### 3. Present Each TODO

For each pending TODO, display a summary card:

```
--- Finding [N] of [M] ---

[P1 CRITICAL | P2 IMPORTANT | P3 NICE-TO-HAVE]

Title: [title from the TODO heading]
Tags: [tags from frontmatter]
Location: [file:line references from Findings section]
Problem: [first 2-3 sentences of Problem Statement]
Proposed Solution: [summary of recommended option or first option]
Effort: [effort estimate from proposed solution]
Dependencies: [dependency IDs if any]
```

### 4. User Decision

Use **AskUserQuestion** for each TODO with these options:

- **Approve**: Accept this finding for implementation
- **Skip**: Remove this TODO — not worth fixing or not actionable
- **Modify**: Let the user provide changes (priority, description, solution) before approving

#### On Approve:
1. Rename the file from `pending` to `ready`:
   ```bash
   mv todos/{id}-pending-{priority}-{desc}.md todos/{id}-ready-{priority}-{desc}.md
   ```
2. Update the `status` field in YAML frontmatter from `pending` to `ready`
3. Update the `updated` date in YAML frontmatter

#### On Skip:
1. Delete the TODO file:
   ```bash
   rm todos/{id}-pending-{priority}-{desc}.md
   ```

#### On Modify:
1. Ask the user what to change (priority, recommended action, description, etc.)
2. Apply the modifications to the file content
3. Then rename from `pending` to `ready` (same as Approve)
4. Update `status` and `updated` fields in frontmatter

### 5. Track Progress

After each decision, show: `"Finding [N] of [M] triaged"`

### 6. Summary

After all TODOs are processed, display:

```
## Triage Summary

- Approved: [N] (ready for implementation)
- Skipped: [N] (removed)
- Modified: [N] (adjusted and approved)
- Total effort estimate: [sum of effort estimates from approved TODOs]

### Approved TODOs by Priority
- P1 Critical: [count]
- P2 Important: [count]
- P3 Nice-to-have: [count]
```

### 7. Next Steps

Suggest:
- Run `/insistir:resolve-todos` to fix approved items with parallel worker agents
- Or commit the triage decisions: `git add todos/ && git commit -m "chore: triage review findings"`
