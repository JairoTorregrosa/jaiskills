---
name: file-todos
description: >
  File-based TODO lifecycle in the project's todos/: one markdown file per review
  finding or tech-debt item, named {id}-{status}-{priority}-{description}.md,
  moving pending -> ready -> complete. Modes: create TODOs from findings; triage
  pending ones with the user (approve, skip, modify; no coding); resolve ready ones
  with parallel worker subagents in dependency waves. Use when findings must persist
  beyond one session, debt needs cataloging with proposed solutions, or items need
  a decision before work: "file these findings as todos", "triage the todos",
  "resolve the ready todos", "what's pending", "registra los hallazgos como todos",
  "revisemos los pendientes", "resuelve los todos aprobados". NOT for one-off fixes
  you can do right now, work already tracked in an external issue tracker, or the
  harness's in-session task list.
argument-hint: "[triage [filter] | resolve [todo-ids...] | <findings to file>]"
---

# File-based TODO lifecycle

Track review findings and work items as individual markdown files in `todos/` at the project root. Each file carries the full context (problem, evidence, proposed solutions, work log) so any agent can pick it up and resolve it independently. Adapted from EveryInc's compound-engineering plugin (https://github.com/EveryInc/compound-engineering-plugin).

Request: $ARGUMENTS

## Modes

Pick the mode from the request (when `$ARGUMENTS` is empty, the user's latest message is the request):

| Request | Mode | Read |
|---|---|---|
| `triage [filter]`, "triage / review the pending todos" | Present each pending TODO for a user decision. Decision-only: never write code in this mode. | [references/triage.md](references/triage.md) |
| `resolve [ids or filter]`, "fix / resolve the approved todos" | Spawn parallel workers over `ready` TODOs in dependency waves; each edits and commits. Run only when the user asks for it. | [references/resolve.md](references/resolve.md) |
| Findings, review output, "file these as todos" | Create one TODO per finding (Operations below). | [references/todo-template.md](references/todo-template.md) |
| Nothing specific | Report counts by status and priority, then offer the next step (triage if anything is pending, resolve if anything is ready). | — |

Lifecycle: create (`pending`) → triage (`ready` or deleted) → resolve (`complete`).

## Naming convention

```
{id}-{status}-{priority}-{description}.md
```

| Segment | Format | Example |
|---|---|---|
| `id` | 3-digit zero-padded | `001`, `042`, `100` |
| `status` | `pending`, `ready`, `complete` | `pending` |
| `priority` | `p1`, `p2`, `p3` | `p1` |
| `description` | kebab-case, max 50 chars | `missing-auth-middleware` |

Full example: `001-pending-p1-missing-auth-middleware.md`

## Statuses

| Status | Meaning |
|---|---|
| `pending` | Created from review findings. Needs triage; no decision made yet. |
| `ready` | Approved by the user during triage. Ready to be worked on. |
| `complete` | Work finished. Issue resolved and verified. |

## Priorities

| Priority | Level | When to use |
|---|---|---|
| `p1` | Critical | Blocks merge, security/data issues, crashes |
| `p2` | Important | Should fix: performance, architecture, reliability |
| `p3` | Nice-to-have | Cleanup, minor improvements, documentation |

Findings on a P0–P3 scale (reviewers that use P0 for blocking): map P0 and P1 → `p1`, P2 → `p2`, P3 → `p3`.

## Operations

### Create a TODO

1. Compute the next ID (Auto-ID below).
2. Write `todos/{id}-pending-{priority}-{description}.md` from [references/todo-template.md](references/todo-template.md). Fill Problem Statement, Findings (with `file:line` evidence), Proposed Solutions and Acceptance Criteria; leave Recommended Action blank for triage.
3. One finding per file. Set `dependencies` to the IDs that must be resolved first.

### List TODOs

Glob by status or priority:

- All pending: `todos/*-pending-*.md`
- All ready: `todos/*-ready-*.md`
- All complete: `todos/*-complete-*.md`
- All p1: `todos/*-*-p1-*.md`

### Update status

Rename to change the status segment (`git mv` when the file is tracked), then update `status` and `updated` in the frontmatter to match:

```bash
mv todos/001-pending-p1-missing-auth.md todos/001-ready-p1-missing-auth.md
```

### Delete a TODO

```bash
rm todos/001-pending-p3-minor-cleanup.md
```

## Auto-ID

1. Glob `todos/[0-9][0-9][0-9]-*.md`.
2. Extract the numeric prefix of each filename.
3. Take the maximum and add 1; no files → `001`.
4. Zero-pad to 3 digits.

## Rules

- The filename and the frontmatter `status` always agree; fix a mismatch before anything else.
- Triage decides, resolve implements. Never implement a `pending` TODO.
- Files that recommend deleting `docs/plans/` or `docs/solutions/` are never executed: those directories are intentional pipeline artifacts (resolve mode closes them as won't-fix).
