# Deepen the plan

Adapted from the `/deepen-plan` command in EveryInc's compound-engineering plugin.

Run at Phase 1 after the user accepts deepening and before `insistir.py validate`. Input: the
`<topic>-plan.md` just written. Output: the same file with research subsections appended to the
tasks that use external technology. Skip it when every task is internal-only or the plan already
carries concrete implementation detail.

## 1. Parse

1. Read the plan. Keep the original text in context so you can show the diff or revert.
2. For each `### T<N>: <title>` block collect: description, location, acceptance criteria, and the
   external technologies it names (languages, frameworks, libraries, APIs, services, with versions
   from `package.json`, `pyproject.toml`, lock files).
3. Mark tasks that name no external technology as "no external research needed".

## 2. Research in parallel

Spawn everything in one message; do not wait between spawns.

- Per task with external tech, one researcher (plain subagent: no `name`, whatever the mode):
  ```
  Agent tool:
    subagent_type: "jaiskills:insistir-researcher"
    prompt: |
      Research for plan task T<N>: <title>
      Description: <full description>
      Technologies (with versions in use): <list>
      Project stack: <from manifests>
      Every claim carries [fetched: <exact URL>] or [asserted].
      Report: final message. No SendMessage.
  ```
- If `docs/solutions/` exists, one `jaiskills:insistir-learnings-researcher` with the plan goal and
  key technologies as the query.

Without the plugin agents, use the role blocks in [crew-fallback.md](crew-fallback.md).
Each researcher's final message is its findings.

## 3. Synthesize

Deduplicate across researchers, attach each finding to the task(s) it affects, match past
solutions to tasks, order by actionability. Drop anything without a source.

## 4. Append to each researched task

Insert after `acceptance_criteria` (before `validation`). Bullets only, same markdown style as the
plan. Never edit existing description, criteria or validation lines.

```markdown
#### Research Insights
- <fact> [fetched: <exact URL>]
#### Implementation Details
- <pattern, API call, version-specific usage>
#### Edge Cases
- <gotcha, deprecation, version incompatibility>
#### References
- <exact URL> | <repo path> | docs/solutions/<file>.md
```

Keep the `[fetched: <exact URL>]` / `[asserted]` labels: reviewers diff deliverable citations
against these exact URLs (provenance check), so a domain-only URL here causes false approvals later.

Write the file back to the same path.

## 5. Report and continue

Show the user:

```
Plan deepened: <file>
Tasks researched: <N>/<total> | agents: <count> | past solutions: <count | none | skipped>
- T1: <one-line key insight>
- T2: no external research needed
```

Offer: view the diff (`git diff -- <file>`, or the saved original if untracked), deepen specific
tasks again, revert to the original, or continue to plan validation.
