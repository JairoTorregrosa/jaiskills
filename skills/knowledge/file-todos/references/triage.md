# Triage mode: decide on pending TODOs

Decision-making only. **Do not write or change code during triage**; implementation is resolve mode ([resolve.md](resolve.md)).

## 1. Load pending TODOs

Glob `todos/*-pending-*.md`. If the request carries a filter (an ID like `003`, a priority like `p1`, a tag or a word from the description), keep only matching files.

None found → tell the user "No pending TODOs to triage." and offer to file some from review findings. Stop.

## 2. Sort

1. `p1` (Critical)
2. `p2` (Important)
3. `p3` (Nice-to-have)

Within a priority, ascending ID.

## 3. Present each TODO

One card per TODO, one at a time:

```
--- Finding [N] of [M] ---

[P1 CRITICAL | P2 IMPORTANT | P3 NICE-TO-HAVE]

Title: [TODO heading]
Tags: [frontmatter tags]
Location: [file:line references from Findings]
Problem: [first 2-3 sentences of Problem Statement]
Proposed Solution: [recommended option, else the first option]
Effort: [effort of that option]
Dependencies: [dependency IDs, or none]
```

## 4. Ask for a decision

Ask with the harness's question tool (Claude Code: AskUserQuestion); without one, ask in chat and wait for the answer. Options:

- **Approve**: accept for implementation.
- **Skip**: delete the TODO; not worth fixing or not actionable.
- **Modify**: the user changes priority, description or solution, then it is approved.

**Approve**
1. Write the chosen option into **Recommended Action** (the proposed option unless the user picked another).
2. Rename `todos/{id}-pending-{priority}-{desc}.md` → `todos/{id}-ready-{priority}-{desc}.md` (`git mv` if tracked).
3. Frontmatter: `status: ready`, `updated: <today>`.

**Skip**
1. `rm todos/{id}-pending-{priority}-{desc}.md` (`git rm` if tracked).

**Modify**
1. Ask what to change (priority, recommended action, description, acceptance criteria).
2. Apply the edits to the file. A priority change also changes the filename segment.
3. Continue exactly as Approve.

After each decision print `Finding [N] of [M] triaged`.

## 5. Summary

```
## Triage summary

- Approved: [N] (ready for implementation)
- Skipped: [N] (removed)
- Modified: [N] (adjusted and approved)
- Total effort: [sum of approved effort estimates]

### Approved by priority
- P1 Critical: [count]
- P2 Important: [count]
- P3 Nice-to-have: [count]
```

## 6. Next steps

Offer:
- Resolve mode now for the approved items ([resolve.md](resolve.md)); it spawns parallel workers that edit and commit, so it runs only on the user's yes.
- Or commit the triage decisions: `git add todos/ && git commit -m "chore: triage review findings"`.
