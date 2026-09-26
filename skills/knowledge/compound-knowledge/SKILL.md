---
name: compound-knowledge
description: >
  Document a solved problem as one searchable file in the project's
  docs/solutions/<category>/ so future sessions (and insistir's learnings
  researcher) find it instead of re-solving it. Three parallel read-only
  subagents extract context, root cause and fix, and prevention; you write the
  single file. Use right after a non-trivial fix is confirmed: "that worked",
  "it's fixed", "problem solved", "document this fix", "write up the solution",
  "compound this", "ya funcionó", "quedó arreglado", "documenta la solución".
  NOT for trivial fixes (typos, obvious one-liners), problems still unresolved
  (keep debugging first), or general docs, READMEs and changelogs.
argument-hint: "[problem summary]"
---

# Compound knowledge

Capture a solved problem as searchable documentation so nobody solves it twice. Adapted from EveryInc's compound-engineering plugin (https://github.com/EveryInc/compound-engineering-plugin).

Problem to document: $ARGUMENTS

If that is empty, document the most recently solved problem in this conversation. If nothing was actually fixed and verified, stop and say so; do not document a guess.

**Exactly ONE file gets written: the final solution doc.** Subagents return text only.

## Convention (per project)

`docs/solutions/` at the project root is the knowledge store. insistir's learnings researcher greps it during planning, so keep paths, frontmatter and tags exactly as below.

Categories (subdirectories of `docs/solutions/`):

- `build-errors`
- `test-failures`
- `runtime-errors`
- `performance-issues`
- `database-issues`
- `security-issues`
- `ui-bugs`
- `integration-issues`
- `logic-errors`

Filename: `docs/solutions/<category>/YYYY-MM-DD-<kebab-description>.md`
Example: `docs/solutions/runtime-errors/2026-02-13-null-pointer-in-auth-middleware.md`

File format: [references/solution-template.md](references/solution-template.md).

## Phase 1: parallel gathering (3 read-only subagents)

Spawn the three in one message so they run in parallel (Claude Code: Agent tool, general-purpose type). Give each the problem summary, the relevant conversation excerpts (error messages, commands, diffs) and the files touched; they have no conversation history. Each returns structured text and writes nothing. No subagent support in this harness: do the three analyses yourself, in order.

### 1a. Context analyzer

Extract from the conversation and codebase:
- **Problem type**: best-fitting category from the list above
- **Affected area**: files, modules, systems
- **Severity**: low / medium / high / critical
- **How detected**: test failure, user report, monitoring alert, etc.
- **Impact**: what was broken or degraded

### 1b. Solution extractor

Extract from the conversation and code changes:
- **Root cause**: why it happened (1-2 paragraphs)
- **Code references**: files and lines involved
- **What fixed it**: the actual changes (before/after snippets)
- **Key insight**: the non-obvious realization that led to the fix

### 1c. Prevention strategist

Determine from the problem and solution:
- **Prevent recurrence**: practices, checks, guards
- **Tests to add**: cases that would catch it next time
- **Monitoring**: alerts or checks that should exist
- **Related patterns**: similar problems that may exist elsewhere

## Phase 2: assembly (you, sequential)

1. Read [references/solution-template.md](references/solution-template.md).
2. Take the category from the context analyzer. Ambiguous between two categories → ask the user.
3. Grep `docs/solutions/` for the key error string and symptom. A doc with the same root cause exists → update that file (refine sections, add to Related) instead of creating a duplicate.
4. Otherwise name the file `YYYY-MM-DD-<kebab-description>.md` with today's date and create `docs/solutions/<category>/` if missing.
5. Write the single file: every frontmatter field and every section filled from the subagent outputs. Tags carry the searchable keywords (error names, libraries, symptoms). `status: draft` unless the fix was verified by a test or reproduction in this session, then `validated`.

This is the only file write in the skill.

## Phase 3: optional follow-up

After writing, offer one follow-up by category and proceed only if the user confirms:

- `security-issues`: check whether the fix needs broader application.
- `performance-issues`: verify the improvement with a benchmark.
- `build-errors` / `test-failures`: run the test suite to confirm the fix holds.
- Other categories: search the codebase for the same pattern elsewhere.

## Rules

- Subagents return TEXT only; they never write files.
- One file per solved problem, always in the template format.
- Ground every claim in the conversation or the code; mark anything unverified as such in the doc.
- No secrets, tokens or personal data in the doc: redact them from logs and snippets.
