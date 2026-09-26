# Spawn prompts

Read when spawning any crew agent. Fill every `<...>`; paste plan text verbatim, never paraphrase
acceptance criteria. `<state>` is the run state dir named in SKILL.md.

How to spawn (Agent tool):

- Team mode: `name: "<agent name below>"`, `subagent_type`, `prompt`, optional `model`. The
  `name` is what makes it a teammate of the session's implicit team.
- Subagent mode: `subagent_type`, `prompt`, optional `model`; no `name`. Put every spawn of a wave
  in one message so they run in parallel.
- Add `model: <sonnet|opus>` when the plan task sets one.
- Without the plugin agents, swap `subagent_type` per [crew-fallback.md](crew-fallback.md).

Last line of every prompt, by mode:

- Team: `Report: SendMessage to team-lead, then approve the shutdown_request.`
- Subagent: `Report: final message. No SendMessage.`

## Learnings researcher (Phase 1, only if `docs/solutions/` exists)

Always a plain subagent (no `name`), whatever the mode.

```
subagent_type: "jaiskills:insistir-learnings-researcher"
prompt: |
  Search docs/solutions/ for past solutions relevant to: <task summary keywords>
  Return: relevant solutions, key patterns, pitfalls to avoid.
  Report: final message. No SendMessage.
```

Paste relevant hits into the matching worker prompts under `Prior learnings`.

## Worker (Phase 3)

```
name: "worker-t<N>"                      # team mode only
subagent_type: "jaiskills:insistir-worker"
prompt: |
  ## Context
  - Plan file: <absolute path to <topic>-plan.md>
  - Goal: <plan goal>
  - Completed dependencies: <T-ids and one line each>
  - Constraints: <plan constraints and risks>
  - Prior learnings: <learnings-researcher hits, or "none">
  - Other workers run in parallel in this working tree: commit only your paths.

  ## Your Task
  **T<N>: <name>**
  Location: <paths>
  Description: <verbatim>
  Acceptance criteria: <verbatim list>
  Validation: <verbatim commands>
  <research subsections from plan deepening, if present>

  Report: <by mode>
```

Touching translation files: add `i18n scope: only add or modify keys in the <namespace>
namespace of <files>. Do not touch keys in other namespaces.`

## Reviewer (Phase 4, fresh every round)

```
name: "reviewer-t<N>-r<R>"               # team mode only
subagent_type: "jaiskills:insistir-reviewer"
prompt: |
  ## Task Under Review
  **T<N>: <name>**
  - Plan file: <absolute path>
  - Description: <verbatim>
  - Acceptance criteria: <verbatim list>
  - Validation: <verbatim commands>
  - Files modified: <from the worker or fixer report>
  - Base commit: <HEAD recorded before the wave>
  - Review round: <R> of <max_review_rounds>

  ## Output
  Your verdict as raw JSON only (no fences, no prose), summary "T<N> review: <APPROVED|REVISE>".
  Report: <by mode>
```

Never include the worker's self-assessment or an earlier round's verdict: the reviewer re-checks
everything from the acceptance criteria.

## Fixer (Phase 4, REVISE with rounds left)

```
name: "fixer-t<N>-r<R>"                  # team mode only
subagent_type: "jaiskills:insistir-worker"
prompt: |
  ## Context
  - Plan file: <absolute path>
  - Goal: <plan goal>
  - Constraints: <plan constraints>
  - Other agents may run in parallel in this working tree: commit only your paths.

  ## Your Task
  **T<N>: <name>**
  Acceptance criteria: <verbatim list>
  Validation: <verbatim commands>

  ## Review Findings (Round <R>)
  <full reviewer JSON, or the raw report if it was not valid JSON>

  ## Judge Findings
  <judge findings with severity and file:line, or "none">

  Fix every P0/P1 finding, every FAIL in requirements_checklist, and every critical or major
  judge finding. Use judgment on P2/P3 and minor judge findings. Report each finding as applied
  or rejected (with the reason), plus your commit SHA.
  Report: <by mode>
```
