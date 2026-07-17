---
id: 005
status: pending
priority: p1
task: T5
source: codex-judge round 1 (NEEDS_REVISION, score 3)
created: 2026-07-16
---

# T5: SKILL.md internal-consistency issues vs reference guides

Three majors from the cross-provider judge on commit 56f2ec5:

1. Worked example (SKILL.md:91) says Opus 4.8 adaptive thinking is on by default;
   claude-models.md says it is OPT-IN (off by default).
2. Routing table (SKILL.md:19-20) claims coverage for Opus 4.1 and all Sonnet 4.x,
   broader than claude-models.md's declared coverage (Opus 4.6-4.8, Sonnet 4.6/5).
3. Workflow step (SKILL.md:43) unconditionally strips sandbox/permission config from
   generated prompts, contradicting codex-harness.md's rule to specify sandbox mode +
   approval policy when the task has security constraints.

**Fix:** assigned to fixer-t5-r1.
