---
id: 001
status: pending
priority: p1
task: T1
source: codex-judge round 1 (NEEDS_REVISION, score 3)
created: 2026-07-16
---

# T1: Source lines use generic URLs instead of factbase URLs

Judge (Codex/GPT-5) found several `Source:` lines in the GPT-5.6 sections of
`plugins/metaprompt/skills/metaprompt/references/openai-models.md` citing generic
`developers.openai.com/docs/...` paths instead of the model-specific
`/api/docs/models/gpt-5.6-{sol,terra,luna}` and `/api/docs/guides/...` URLs that were
actually fetched for the plan factbase (metaprompt-guides-plan.md T1 research_insights).

**Fix:** normalize every Source line to the exact verified URL supporting that section.
Assigned to fixer-t1-r1.
