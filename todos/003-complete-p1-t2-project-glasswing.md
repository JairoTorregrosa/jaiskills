---
id: 003
status: pending
priority: p1
task: T2
source: reviewer-t2-r1 round 1 (APPROVED with P1)
created: 2026-07-16
---

# T2: Verify "Project Glasswing" claim for Mythos 5 availability

`claude-models.md` line ~149 says Mythos 5 is invitation-only through "Project
Glasswing". The name is not in the plan's T2 research_insights (though it DID appear in
the original researcher-t2 report sourced from anthropic.com/news/claude-fable-5-mythos-5,
so it may be genuine).

**Fix:** WebFetch the announcement URL; keep the name only if the page confirms it,
otherwise say "invitation-only" without the program name.
