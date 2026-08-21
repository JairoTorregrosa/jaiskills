---
name: file-todos
description: >
  File-based TODO lifecycle for tracking review findings, managing technical debt, and
  organizing work items. Each TODO is a standalone markdown file with YAML frontmatter,
  named by convention: {id}-{status}-{priority}-{description}.md. Status transitions
  drive the lifecycle: pending (created from review) -> ready (triaged and approved) ->
  complete (resolved). Use when: (1) review findings need persistent tracking beyond
  a single session, (2) technical debt should be cataloged with solutions, (3) work
  items need triage before implementation. Do NOT use for: (1) simple one-off fixes
  that can be done immediately, (2) tasks already tracked in an external issue tracker.
---

# File-based TODO Lifecycle

Track review findings and work items as individual markdown files in `todos/`. Each file captures the full context — problem, evidence, proposed solutions, and work log — so any agent can pick it up and resolve it independently.

## Naming Convention

```
{id}-{status}-{priority}-{description}.md
```

| Segment       | Format                       | Example                    |
|---------------|------------------------------|----------------------------|
| `id`          | 3-digit zero-padded          | `001`, `042`, `100`        |
| `status`      | One of: pending, ready, complete | `pending`              |
| `priority`    | One of: p1, p2, p3           | `p1`                       |
| `description` | kebab-case, max 50 chars     | `missing-auth-middleware`  |

Full example: `001-pending-p1-missing-auth-middleware.md`

## Statuses

| Status    | Meaning                                                              |
|-----------|----------------------------------------------------------------------|
| `pending` | Created from review findings. Needs triage — no decision made yet.   |
| `ready`   | Approved by user during triage. Ready to be worked on.               |
| `complete`| Work finished. Issue resolved and verified.                          |

## Priorities

| Priority | Level       | When to use                                                     |
|----------|-------------|-----------------------------------------------------------------|
| `p1`     | Critical    | Blocks merge, security/data issues, crashes                     |
| `p2`     | Important   | Should fix — performance, architecture, reliability concerns    |
| `p3`     | Nice-to-have| Cleanup, minor improvements, documentation                     |

## Operations

### Create a TODO

Find the highest existing ID in `todos/` and increment by 1. Start at `001` if the directory is empty.

Use the **Write** tool to create the file at `todos/{id}-pending-{priority}-{description}.md` using the template in [references/todo-template.md](references/todo-template.md).

### List TODOs

Use **Glob** to find TODOs by status:

- All pending: `todos/*-pending-*.md`
- All ready: `todos/*-ready-*.md`
- All complete: `todos/*-complete-*.md`
- All p1 critical: `todos/*-*-p1-*.md`

### Update Status

Rename the file via **Bash** `mv` to change the status segment:

```bash
mv todos/001-pending-p1-missing-auth.md todos/001-ready-p1-missing-auth.md
```

Also update the `status` field in the YAML frontmatter to match.

### Delete a TODO

Remove the file via **Bash** `rm`:

```bash
rm todos/001-pending-p3-minor-cleanup.md
```

## Auto-ID

When creating a new TODO, determine the next ID:

1. Glob `todos/[0-9][0-9][0-9]-*.md` to find all existing TODOs
2. Extract the numeric prefix from each filename
3. Take the maximum and add 1
4. If no files exist, start at `001`
5. Zero-pad to 3 digits

## Template

See [references/todo-template.md](references/todo-template.md) for the full TODO file structure.
