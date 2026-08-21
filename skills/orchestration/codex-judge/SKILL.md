---
name: codex-judge
user-invocable: false
description: >
  Cross-provider LLM judge using Codex (GPT-5) to evaluate implementations
  written by Claude. Internal skill invoked by the insistir lead during the
  review loop. Not user-facing.
---

# Codex Judge: Cross-Provider Verdict

Uses Codex (GPT-5) as an independent judge to evaluate Claude-written implementations, eliminating self-preference bias inherent in same-model review.

## Why Cross-Provider Judging

Self-preference bias is well-documented: models rate their own outputs 10-25% higher than warranted. GPT-5.x judging Claude's output is an ideal cross-provider setup — different training data, different reward models, different blind spots. The judge shares no internal assumptions with the implementer.

Reference: "Judging the Judges" (arXiv 2604.23178) — cross-model ensembles achieve higher separability and alignment with human rankings.

## What the Judge Sees

The judge receives ONLY:

| Input | Source |
|-------|--------|
| Task spec + acceptance criteria | Plan file |
| Git diff | `git diff` of the implementation |
| Reviewer findings (structured JSON) | Insistir reviewer agent |
| Check results (tests, typecheck, lint) | Reviewer's `checks` object |

**NEVER send the implementer's reasoning, chain-of-thought, or self-assessment.** The judge evaluates artifacts only — fresh context prevents sycophancy contamination.

## How to Invoke

```
mcp__codex__codex:
  prompt: <rendered judge-prompt from references/judge-prompt.md>
  sandbox: "read-only"
  approval-policy: "never"
  cwd: "<repo root>"
```

Parse the response as JSON matching the verdict schema. If JSON parsing fails, re-prompt once with: "Your previous response was not valid JSON. Return ONLY the verdict JSON, no markdown fencing." If it fails again, treat as degraded (see below).

## Verdict Schema

```json
{
  "verdict": "PASS | NEEDS_REVISION | REJECT",
  "confidence": 0.0-1.0,
  "criteria": {
    "correctness":      { "score": 1-5, "evidence": "...", "violations": [] },
    "security":         { "score": 1-5, "evidence": "...", "violations": [] },
    "maintainability":  { "score": 1-5, "evidence": "...", "violations": [] },
    "spec_compliance":  { "score": 1-5, "evidence": "...", "violations": [] }
  },
  "overall_score": 1-5,
  "rationale": "2-3 sentence summary",
  "remediation": [
    {
      "severity": "critical | major | minor",
      "description": "what is wrong",
      "suggestion": "how to fix",
      "file": "path",
      "line": 42
    }
  ]
}
```

## Dual-Threshold Gating

The lead uses the judge verdict alongside the reviewer verdict:

| Condition | Action |
|-----------|--------|
| `overall_score >= 4` AND no critical violations | **Auto-approve** — judge confirms quality |
| `overall_score <= 2` OR any critical violation | **Auto-revise** — spawn fixer immediately |
| Middle band (score 3, or major-only violations) | **Lead judgment** — reviewer verdict is tiebreaker |

Decision matrix when reviewer and judge disagree:

```
Reviewer APPROVED + Judge PASS         → APPROVED (consensus)
Reviewer APPROVED + Judge NEEDS_REVISION → Lead reviews judge's remediations;
                                           if credible, spawn fixer
Reviewer REVISE   + Judge PASS         → Unlikely; trust reviewer (closer to code)
Reviewer REVISE   + Judge NEEDS_REVISION → REVISE (consensus)
```

## When to Invoke the Judge

The lead invokes this skill:

1. **After the reviewer returns its verdict** — the judge sees reviewer findings as input
2. **Only for tasks marked as complex** (multi-file, cross-cutting, security-sensitive) or when the reviewer's verdict is borderline
3. **Not on trivial tasks** — single-file changes, config edits, or tasks where the reviewer gave a clear APPROVED with all checks passing

This keeps Codex API costs proportional to task complexity.

## Graceful Degradation

If `mcp__codex__codex` is unavailable (tool missing, MCP server down, auth failure, or timeout):

1. **Skip the judge step entirely** — do not block the pipeline
2. **Reviewer verdict stands as final** — the existing cross-review by a fresh Claude agent still provides independent validation
3. **Note in execution summary**: "Cross-provider judge unavailable — reviewer verdict used as sole gate"

Never fail the pipeline because the judge is unreachable. The judge is an enhancement, not a hard dependency.
