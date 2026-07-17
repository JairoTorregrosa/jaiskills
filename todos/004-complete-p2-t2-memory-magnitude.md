---
id: 004
status: pending
priority: p2
task: T2
source: reviewer-t2-r1 round 1
created: 2026-07-16
---

# T2: Memory section omits quantitative comparison

`claude-models.md` Memory section (~209-213) says Fable 5 "performs particularly well"
with file-based memory but drops the factbase's quantitative claim: file-based memory
improved Fable 5 three times more than Opus 4.8.

**Fix:** add the relative magnitude with its source (prompting-claude-fable-5 page).
