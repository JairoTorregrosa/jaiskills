# Execution summary template

Read at Phase 6. Render it before finishing, even when tasks failed. `Judge` is the band and
score, suffixed `(same-provider fallback)` when second-opinion could not reach Codex, or
`skipped (trivial)` / `unavailable`. List every judge finding, whatever the band.

```markdown
# Execution Summary

## Tasks: [N] total | [done] completed | [failed] failed | [issues] review findings
Mode: [team | subagent] | Completion gate: [applied | not applied (reason)] | TODOs: [filed N, closed N | off]

### Wave [N]
| Task | Worker | Reviewers | Rounds | Judge | Outcome | Findings |
|------|--------|-----------|--------|-------|---------|----------|
| T1 | worker-t1 | reviewer-t1-r1 | 1 | skipped (trivial) | APPROVED | 0 |
| T2 | worker-t2 | reviewer-t2-r1, -r2 | 2 | auto-approve 4.5 | APPROVED | 3 (2 fixed) |
| T3 | worker-t3 | reviewer-t3-r1, -r2 | 2 | auto-revise 2.1 | FAILED | 4 (decompose) |

### Cross-Review Stats
- Reviewed: [N] | First-pass APPROVED: [N] | Required revision: [N] | Failed (max rounds): [N]
- Total review rounds: [N] | Avg rounds per task: [N]

### Issues Caught by Reviewers
- T2 R1: [Issue found by reviewer] → [Fix applied in R1]
- T2 R2: [Re-review confirmed fix] → APPROVED

### Failed Tasks (exceeded review budget)
- T3: [reason, suggested decomposition]

### Judge Findings (all bands)
- T[N] R[R] [critical|major|minor] [file:line]: [claim] → [fixed in <sha> | follow-up | rejected: reason]

## Files Modified
[list of all files changed across all waves]

## Team Composition
- Lead: [you]
- Workers: [list]
- Fixers: [list, if any review rounds required revision]
- Reviewers: [list] (fresh per round)
```
