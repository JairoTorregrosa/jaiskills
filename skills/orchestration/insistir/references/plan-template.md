# Plan template

Read when writing `<topic>-plan.md` (Phase 1; `<topic>` is `[a-z0-9-]` only). `scripts/insistir.py validate` requires, per task:
`depends_on`, `location`, `description`, `acceptance_criteria`, `validation`, `status`
(`pending|in_progress|completed|failed`). Task headings are `### T<N>: <name>`; the shared task
subject must match (`T<N>: <name>`) or the completion gate will not apply. Optional per task:
`model` (`sonnet` for single-component or copy edits, `opus` for state machines, cross-file
refactors, complex logic) and `max_review_rounds`.

```markdown
# [Topic] Plan

## Goal
[1-2 sentence description of what we're building]

## Constraints
- [Tech stack, patterns, risks]

## Config
- **max_review_rounds**: 2

## Tasks

### T1: [Task Name]
- **depends_on**: []
- **location**: [file paths]
- **description**: [what to implement]
- **acceptance_criteria**: [list of criteria]
- **validation**: [how to verify]
- **status**: pending
- **model**: [optional: sonnet/opus override for worker/reviewer]
- **log**:
- **files**:

### T2: [Task Name]
- **depends_on**: [T1]
- **location**: [file paths]
- **description**: [what to implement]
- **acceptance_criteria**: [list of criteria]
- **validation**: [how to verify]
- **status**: pending
- **log**:
- **files**:

## Dependency Graph
T1 → T2 → T3
     ↘ T4 ↗

## Parallel Execution Waves
| Wave | Tasks | Depends On |
|------|-------|------------|
| 1    | T1    | -          |
| 2    | T2, T3| T1         |
| 3    | T4    | T2, T3     |
```

## Render for the user

Show waves and dependencies with box-drawing characters before asking for confirmation:

```
Wave 1 (parallel)              Wave 2 (parallel)              Wave 3
┌────────────┐ ┌────────────┐  ┌────────────┐ ┌────────────┐  ┌────────────┐
│ T1: Create │ │ T2: Install│  │ T3: Repo   │ │ T4: Service│  │ T5: API    │
│ DB Schema  │ │ Packages   │──│ Layer      │ │ Layer      │──│ Endpoints  │
└────────────┘ └────────────┘  └────────────┘ └────────────┘  └────────────┘
       │              │               ▲              ▲               ▲
       └──────────────┴───────────────┘              │               │
                                      └──────────────┴───────────────┘
```
