---
title: "Same-family LLM reviewers approve provenance drift that a cross-provider judge catches"
date: 2026-07-16
category: "logic-errors"
tags:
  - "cross-provider-judge"
  - "provenance"
  - "citation-drift"
  - "llm-review"
  - "insistir"
  - "metaprompt"
  - "cross-file-consistency"
  - "coherence-vs-correspondence"
severity: "high"
status: "validated"
---

## Problem

**What happened**: While building the metaprompt plugin 0.2.0 reference guides with the insistir pipeline (Claude workers → Claude adversarial reviewers → Codex/GPT-5 judge), Claude reviewers APPROVED tasks T1 and T5 with ~20 automated checks passing each (including `source_urls_valid: PASS`), yet the cross-provider Codex judge found: (T1) `Source:` lines citing generic `developers.openai.com/docs/...` paths instead of the actually-fetched `/api/docs/...` factbase URLs, plus 3 unsupported comparative performance claims; (T5) a worked example asserting Opus 4.8 adaptive thinking is on-by-default when the guide it routes to says opt-in, a routing table claiming broader model coverage than the reference file's declared `covers:`, and a categorical "strip sandbox/permission config" rule contradicting the Codex harness guide.

Verification cut both ways: fixers re-fetching sources confirmed the suspected-fabricated "Project Glasswing" as REAL (on anthropic.com/news/claude-fable-5-mythos-5), while the researcher's "file-based memory boosts Fable 5 3x more than Opus 4.8" claim was NOT on the cited page and was removed.

**How detected**: Cross-provider adversarial judge (Codex/GPT-5, `mcp__codex__codex` read-only) instructed to demand file:line evidence and cross-check every claim against the plan's `research_insights` factbase. An earlier goal-loop on the same plugin was rejected by the same judge for the same class of issue (citation trustworthiness).

**Impact**: Without the judge, authoritative reference guides for downstream prompt generation would have shipped with plausible-but-wrong citations, fabricated comparative claims presented as sourced facts, an inverted model default, overclaimed routing coverage, and a rule that strips security constraints from generated prompts.

## Root Cause

**Why it happened**: Same-family reviewers validate **coherence** (does this read as plausible, well-structured, thematically aligned with the factbase?) rather than **correspondence** (does this exact URL/claim match what was actually fetched or written in the sibling file?). A thematically-correct generic URL passes coherence review perfectly — the instruction "verify this URL" triggers the same plausibility heuristic that generated the wrong URL in the first place. For T5, the SKILL.md worker inferred defaults and routing scope from general knowledge instead of reading the file it was routing to, and the reviewer checked SKILL.md in isolation without diffing it against `claude-models.md`'s `covers:` frontmatter.

**Code references**:
- `todos/001-complete-p1-t1-source-provenance.md` — generic vs fetched URL drift
- `todos/002-complete-p1-t1-unsupported-claims.md` — 3 unsupported comparative claims
- `todos/005-complete-p1-t5-internal-consistency.md` — 3 cross-file contradictions
- `todos/003-complete-p1-t2-project-glasswing.md` — suspected fabrication confirmed real by re-fetch
- Fix commits: `6cfa40f`, `342ed16` (T1), `3c5d84b` (T2), `8d77612` (T5)

## Solution

**What fixed it**:
1. Judge prompt demanding file:line evidence + exact cross-check against the plan factbase (not domain plausibility).
2. Fixers instructed to WebFetch every disputed claim before keep/remove — prevented both false retentions (3x memory) and false removals (Project Glasswing).
3. Claim-level `Source:` lines (URL per claim/section, not per file).
4. Routing tables narrowed to match the reference file's `covers:` frontmatter exactly.

**Code changes**:

Before (SKILL.md worked example):
```
Adaptive thinking is on by default for Opus 4.8 — no thinking budget needed
```

After:
```
Adaptive thinking is OFF by default on Opus 4.8 — enable explicitly with
thinking: {type: "adaptive"}; budget_tokens returns 400
```

**Key insight**: A cross-provider judge breaks the blind spot not because it is smarter but because it operates from a different prior distribution — it doesn't share the writer/reviewer tendency to fill gaps with the same plausible defaults. Same-family reviewers need **mechanized** correspondence checks (exact URL diff against a fetched-URL log, `covers:` frontmatter vs routing-table diff), not prose instructions to "verify sources."

## Prevention

**How to prevent recurrence**:
- Reviewer prompts for documentation tasks must diff every `Source:` URL against the plan factbase EXACTLY (path-level); domain-only match = FAIL.
- When a file routes to other files (SKILL.md routing tables), the reviewer must read each target's `covers:`/coverage declarations and flag scope overclaims.
- Label factbase claims `[fetched: <exact URL>]` vs `[asserted]`; workers may not promote `[asserted]` claims without re-fetching.
- Researchers must cite the exact page fetched per claim — directory-level URLs are insufficient.
- NEVER skip the cross-provider judge for documentation/provenance-critical tasks; "single-file change" does not mean trivial when the file is a citation-bearing reference.

**Tests to add**:
- Source-URL drift checker: every `Source:` URL in `plugins/*/skills/*/references/*.md` must appear verbatim in the corresponding plan factbase.
- Routing-vs-coverage check: models in SKILL.md routing tables ⊆ target file's `covers:` frontmatter.
- Sections-without-Source check: any `##` section with factual claims but no `Source:` line is a provenance gap.
- Frontmatter completeness: references must carry `last_verified:` + `sources_verified:` (warn-only until retrofitted).

**Monitoring**:
- `last_verified` staleness warning (30 days default; 14 for pricing/deprecation-heavy pages).
- Track judge skip rate per task type; >50% skips on documentation tasks means the "trivial" carve-out is too broad.
- Log fixer re-fetch outcomes (confirmed vs disproved) as a researcher-reliability signal.

## Related

- Same failure surface elsewhere: goal-loop SKILL.md arXiv citations (unaudited claim↔paper mapping); goal-loop grep-keyword evidence commands (structural, not provenance checks); `plugins/remoto` reference files and insistir's own references lack `last_verified` frontmatter; solution files themselves compound across sessions — a fabricated claim here would amplify via the learnings researcher.
- Session artifacts: `metaprompt-guides-plan.md`, `goals/metaprompt-skill-goal.md`, commits `fe76a94`…`6e21b6f`.
