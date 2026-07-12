---
name: insistir
description: >
  Agents Checking Agents — multi-agent orchestration with cross-validation using Claude Code Agent Teams
  and a cross-provider Codex/GPT-5 judge for bias-free final verdicts.
  Fresh agents for each phase — no agent reuse. Each worker/reviewer/fixer is spawned, does its work,
  and is shut down. The review loop iterates until the reviewer APPROVES or max rounds are reached.
  The lead operates in delegate mode: coordinates only, never implements.
  Use when: (1) user says /insistir, (2) complex tasks that benefit from parallel execution with
  quality gates, (3) "agents checking agents", "multi-agent", "swarm", or "orchestrate".
  Do NOT use for: (1) simple single-file changes, (2) sequential tasks with tight dependencies,
  (3) quick bug fixes or typos, (4) tasks where coordination overhead exceeds the benefit.
  Full pipeline: intake → plan → spawn team → [execute wave → adversarial review → codex judge] → cleanup.
---

# Insistir: Agents Checking Agents

Multi-agent orchestration where **every agent's work is reviewed by a different agent** in an **iterative adversarial loop** — the reviewer either APPROVES or sends back for REVISION, with fresh context each round.

Uses Claude Code Agent Teams — each teammate is a full independent Claude Code session with its own context window, communicating via messages and a shared task list.

## Adversarial Cooperation Model

Based on dialectical autocoding research: a structured coach/player feedback loop where the reviewer (coach) independently validates against requirements, catching the implementer's (player's) blind spots and false confidence. Key principles:

1. **Fresh context each round** — each reviewer spawn starts clean, avoiding context pollution
2. **Requirements contract** — acceptance criteria are the single source of truth, not the worker's self-assessment
3. **Iterative convergence** — multiple review rounds systematically close the delta between implementation and requirements
4. **Turn limits as complexity signal** — if max rounds exhaust without approval, the task is likely too complex and should be decomposed
5. **Cross-provider judgment** — a different model family (Codex/GPT-5) issues the final verdict, eliminating self-preference bias

## Custom Agents (bundled in this plugin)

| Agent | Role | Tools | Model |
|-------|------|-------|-------|
| `insistir:insistir-worker` | Implement task or apply review fixes, commit, report to lead, shut down | Read, Edit, Write, Bash, Glob, Grep, WebFetch, WebSearch, SendMessage, TaskGet (disallowed: TaskUpdate, TaskCreate, TaskList) | opus |
| `insistir:insistir-reviewer` | Cross-review with APPROVE/REVISE verdict, run verification commands | Read, Glob, Grep, Bash (whitelisted), SendMessage, TaskGet | opus |
| `insistir:insistir-learnings-researcher` | Search docs/solutions/ for relevant past solutions (read-only) | Read, Glob, Grep, SendMessage | opus |
| `insistir:insistir-researcher` | Research best practices and framework docs (read-only + web) | Read, Glob, Grep, WebFetch, WebSearch, SendMessage | opus |

Workers can edit files and run any commands. Reviewers **cannot edit** (`disallowedTools: Edit, Write`) but can run whitelisted read-only verification commands (tests, typecheck, lint) via a `PreToolUse` Bash filter hook.

> **LLM Judge (Codex/GPT-5)**: Not a teammate agent. The lead calls `mcp__codex__codex` directly with `sandbox: "read-only"` to obtain a cross-provider verdict. No agent is spawned — the tool call returns a JSON verdict inline.

## When NOT to Use

- Single-file edits or trivial changes — use a single session
- Sequential tasks where each step depends on the previous — use subagents
- Same-file edits by multiple agents — causes overwrites
- Quick bug fixes, typos, config changes — overhead isn't worth it

## Example Triggers

```
/insistir Build a full authentication system with login, signup, password reset, and tests
/insistir Refactor the payment module — split into separate services with cross-review
/insistir Create a dashboard with API endpoints, React components, and E2E tests
```

## Core Pattern

```
      ┌──────────────────────────────────────────────┐
      │         TECH LEAD (delegate mode only)        │
      │   Coordinates, delegates, synthesizes.        │
      │   NEVER implements, edits files, or builds.   │
      └───┬──────────────┬──────────────┬────────────┘
          │              │              │
   ┌──────▼──┐    ┌──────▼──┐    ┌──────▼──┐
   │Worker A │    │Worker B │    │Worker C │    IMPLEMENT
   │implement│    │implement│    │implement│
   │  commit │    │  commit │    │  commit │
   └────┬────┘    └────┬────┘    └────┬────┘
        ✕              ✕              ✕         SHUTDOWN workers
        │              │              │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │Review B │    │Review C │    │Review A │    CROSS-REVIEW (round 1)
   │→ REVISE │    │→APPROVE │    │→ REVISE │    findings → lead
   └────┬────┘    └─────────┘    └────┬────┘
        ✕                             ✕         SHUTDOWN reviewers
        │                             │
   ┌────▼────┐                   ┌────▼────┐
   │Fixer A  │                   │Fixer C  │    FIX (new agents)
   │  fixes  │                   │  fixes  │
   │  commit │                   │  commit │
   └────┬────┘                   └────┬────┘
        ✕                             ✕         SHUTDOWN fixers
        │                             │
   ┌────▼────┐                   ┌────▼────┐
   │Review B'│                   │Review A'│    CROSS-REVIEW (round 2)
   │→APPROVE │                   │→APPROVE │    fresh context, no pollution
   └─────────┘                   └─────────┘
        ✕                             ✕         SHUTDOWN reviewers
```

## Pipeline

```
Intake → Plan → Create Team → [Execute Wave → Iterative Cross-Review Loop] → Cleanup
```

---

## Phase 0: Intake (MANDATORY)

**ALWAYS start here.** Before any research or planning, use AskUserQuestion to understand:

1. **Scope**: What exactly should be built? What's in/out of scope?
2. **Priorities**: What matters most — speed, quality, specific features?
3. **Constraints**: Tech stack, patterns to follow, things to avoid?
4. **Preferences**: How many agents? Max review rounds? Model preferences?

**Available enhancements** (mention to user):
- **Knowledge search**: Past solutions in `docs/solutions/` are searched automatically during planning. If the team has solved similar problems before, those learnings feed into task descriptions.
- **Plan deepening**: After plan creation, `/insistir:deepen-plan` can enrich tasks with external research (framework docs, best practices, edge cases) via parallel researcher agents.
- **TODO tracking**: Review findings (P1/P2) are persisted as todo files in `todos/` for lifecycle tracking, even after fixers resolve them.
- **Cross-provider judge**: Codex/GPT-5 as independent final verdict; requires Codex CLI logged in; can be disabled.

**Review round trade-offs** (explain to user when asking):
- **1 round**: No second chance — any REVISE verdict = task failure. Good for well-specified simple tasks.
- **2 rounds** (default): One chance to fix review findings. Good balance of quality vs speed.
- **3 rounds**: Two fix attempts. For complex tasks where first pass might miss nuances.

Do NOT skip this phase. Do NOT assume scope, constraints, or priorities.

---

## Phase 1: Plan

### 1.1 Research
- Investigate codebase: architecture, patterns, existing implementations, dependencies
- Fetch docs for external libraries/frameworks via web search

### 1.1.5 Search Past Solutions

Before creating the plan, check whether `docs/solutions/` exists in the project (Glob). If it does not exist, skip this step — do not spawn a researcher just to report an empty directory. If it exists, spawn a `insistir:insistir-learnings-researcher` agent with the task summary as a query:

```
Task tool:
  subagent_type: "insistir:insistir-learnings-researcher"
  prompt: |
    Search docs/solutions/ for past solutions relevant to: [task summary keywords]
    Return structured findings: which solutions are relevant, key patterns, pitfalls to avoid.
```

If relevant solutions are found, include them in task descriptions when spawning workers (Phase 3) so implementers benefit from prior learnings.

### 1.2 Create Dependency-Aware Plan

Each task declares explicit dependencies for maximum parallelization. Save to `<topic>-plan.md` using the template in [references/plan-template.md](references/plan-template.md).

Optional per-task fields for advanced control:
- **model**: Override model for worker/reviewer. For trivial tasks (single-component changes, adding one element, copy edits), set `model: sonnet` to reduce cost. Reserve `opus` for tasks involving state machine changes, cross-file refactoring, or complex logic.
- **max_review_rounds**: Override default max rounds for this specific task

### 1.3 Display Plan as ASCII Art

**ALWAYS** render the plan visually to the user using box-drawing characters showing waves and dependencies:

```
Wave 1 (parallel)              Wave 2 (parallel)              Wave 3
┌────────────┐ ┌────────────┐  ┌────────────┐ ┌────────────┐  ┌────────────┐
│ T1: Create │ │ T2: Install│  │ T3: Repo   │ │ T4: Service│  │ T5: API    │
│ DB Schema  │ │ Packages   │──│ Layer      │ │ Layer      │──│ Endpoints  │
│ [backend]  │ │ [config]   │  │ [backend]  │ │ [backend]  │  │ [backend]  │
└────────────┘ └────────────┘  └────────────┘ └────────────┘  └────────────┘
       │              │               ▲              ▲               ▲
       └──────────────┴───────────────┘              │               │
                                      └──────────────┴───────────────┘
```

Show this to the user and confirm before proceeding.

### 1.3.5 Deepen Plan (Optional)

After displaying the plan, offer to run `/insistir:deepen-plan` to enrich tasks with external research:

> "Would you like to deepen this plan with external research? This spawns parallel researcher agents to look up framework docs, best practices, and edge cases for each task that references external technologies. Takes a few minutes but can improve implementation quality."

If the user accepts, run:
```
/insistir:deepen-plan <topic>-plan.md
```

This is optional and should be skipped if:
- The user declines or wants to proceed quickly
- Tasks are purely internal (no external frameworks/APIs)
- The plan is already well-specified with clear implementation details

### 1.4 Validate Plan

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/insistir/scripts/insistir.py validate <topic>-plan.md
python ${CLAUDE_PLUGIN_ROOT}/skills/insistir/scripts/insistir.py waves <topic>-plan.md
```

### 1.5 Plan Review
Spawn a Plan subagent to review for missing dependencies, ordering issues, gaps. Revise if needed.

---

## Phase 2: Create Agent Team

### 2.1 Pre-Flight Check

**MANDATORY** before creating the team. Verify the working tree is clean:

```bash
git diff --name-only HEAD
```

If the output is non-empty (tracked files have modifications), STOP and tell the user:
> "The working tree has uncommitted tracked changes. Please commit or stash them before starting a insistir session. Uncommitted changes in the shared working tree will interfere with parallel workers."

Untracked files (`??` in `git status --porcelain`) are acceptable — they don't cause merge conflicts between parallel workers. Only modified tracked files require commit/stash.

Do NOT proceed to team creation with modified tracked files.

### 2.2 Create Team

```
TeamCreate: team_name="insistir-<topic>", description="<task summary>"
```

### 2.3 Enter Delegate Mode

**CRITICAL**: The lead MUST operate in delegate mode. The lead NEVER:
- Reads code files
- Edits or writes files
- Runs builds or tests
- Implements anything

The lead ONLY:
- Spawns teammates (Task tool)
- Sends messages (SendMessage)
- Manages tasks (TaskCreate, TaskUpdate, TaskList)
- Synthesizes results and reports to user

Operate in a delegation-only capacity: never use file/code tools directly — spawn teammates for all implementation, review, and verification work. (The only lead Bash exceptions are the state-directory setup, the approval marker, and the judge diff.)

### 2.4 Initialize State Directory

The lead creates the external state directory for hook approval markers:
```bash
mkdir -p ~/.claude/insistir-state/insistir-<topic>
```

The lead also writes the plan's validation command prefixes to the allowed-commands whitelist so reviewers can run them:
```bash
printf '%s\n' "<validation command prefixes from the plan, one per line>" > ~/.claude/insistir-state/insistir-<topic>/allowed_commands.txt
```

### 2.5 Create Shared Tasks

Use **TaskCreate** for each plan task. Set dependencies with **TaskUpdate** `addBlockedBy`. Assign to workers with `owner`.

---

## Phase 3: Execute Wave

### 3.1 Spawn Workers

For each unblocked task, spawn a worker using the **bundled insistir-worker agent**:

```
Task tool:
  name: "worker-t1"
  team_name: "insistir-<topic>"
  subagent_type: "insistir:insistir-worker"
  prompt: |
    ## Context
    - Plan file: [path to <topic>-plan.md]
    - Overview: [relevant goals from plan]
    - Completed dependencies: [list]
    - Constraints: [risks from plan]

    ## Your Task
    **Task [ID]: [Name]**
    Location: [file paths]
    Description: [full description]
    Acceptance Criteria: [list from plan]
    Validation: [tests or verification steps]
```

**i18n scoping** (if the task touches translation files): Add to the prompt: "i18n scope: only add/modify keys in the `[namespace]` namespace of translation files (e.g., en.json, es.json). Do NOT touch keys in other namespaces."

> **Note on project-level quality hooks**: If the project has stop hooks (e.g., typecheck, lint), they may fire on the lead's turn and report errors from workers' in-progress code. This is expected noise during parallel execution — ignore until all workers in the current wave have completed and been shut down.

### 3.2 Workers Implement, Commit, Report

Workers implement their task, commit, and message the lead with completion status. They then go idle.

### 3.3 Shutdown Workers

After receiving each worker's completion message, immediately send `shutdown_request` to the worker:

```
SendMessage type="shutdown_request" recipient="worker-t1" content="Implementation received. Shutting down."
```

Wait for `shutdown_response` (approve) before proceeding. All workers must be shut down before starting cross-review.

---

## Phase 4: Iterative Adversarial Review + Cross-Provider Judge

This is the core of the skill. The review loop **iterates until APPROVED or max rounds reached**. Each phase uses fresh agents — no agent is ever reused. After each reviewer verdict, a cross-provider LLM judge (Codex/GPT-5) provides an independent second opinion.

### 4.1 Spawn Reviewers (Round N)

For each completed task, spawn a reviewer using the **bundled insistir-reviewer agent**:

```
Task tool:
  name: "reviewer-t1-r1"
  team_name: "insistir-<topic>"
  subagent_type: "insistir:insistir-reviewer"
  prompt: |
    ## Task Under Review
    **Task [ID]: [Name]**
    - Plan file: [path to <topic>-plan.md]
    - Description: [task description from plan]
    - Acceptance Criteria: [from plan]
    - Files Modified: [from worker's output]
    - Review Round: [N] of [max_review_rounds]

    ## Output
    Send your findings as raw JSON (no code fences, no prose) via SendMessage to: [lead-name]
    Use summary: "T[ID] review: [your verdict]"
```

Launch ALL reviewers in parallel. The reviewer sends structured JSON findings directly to the lead.

### 4.2 Shutdown Reviewers

After receiving each reviewer's findings message, immediately send `shutdown_request` to the reviewer. Wait for `shutdown_response` before processing the verdict.

> **Parsing note**: Extract the `verdict` field from the reviewer's JSON message. If the message is not valid JSON, treat it as REVISE and include the raw message in the fixer prompt for context.

### 4.3 Judge Verdict (Cross-Provider)

**When to invoke** (matches the codex-judge skill): skip the judge when the task is trivial (single-file change, config edit) AND the reviewer gave a clear APPROVED with all checks passing — record `"judge: skipped (trivial)"` for the summary. Invoke the judge for complex tasks (multi-file, cross-cutting, security-sensitive) or whenever the reviewer verdict is REVISE or borderline.

After receiving reviewer findings, the lead obtains an independent verdict from Codex/GPT-5:

1. **Gather diff** via Bash (allowed lead Bash exception, like the approval marker):
   ```bash
   git diff <base-commit>..HEAD -- <task-files>
   ```

2. **Load the judge prompt template** from `${CLAUDE_PLUGIN_ROOT}/skills/codex-judge/references/judge-prompt.md`. Fill placeholders:
   - `{{TASK_SPEC}}` — task description from the plan
   - `{{ACCEPTANCE_CRITERIA}}` — acceptance criteria list from the plan
   - `{{DIFF}}` — the git diff output
   - `{{REVIEWER_FINDINGS}}` — the reviewer's JSON findings
   - `{{CHECK_RESULTS}}` — verification command outputs from the reviewer's `checks` object

3. **Call the Codex MCP tool**:
   ```
   mcp__codex__codex:
     prompt: [filled judge prompt]
     sandbox: "read-only"
     approval-policy: "never"
   ```

4. **Parse the JSON verdict** from the response. Full schema in `${CLAUDE_PLUGIN_ROOT}/skills/codex-judge/SKILL.md`; the fields the lead uses:
   ```json
   {
     "verdict": "PASS" | "NEEDS_REVISION" | "REJECT",
     "overall_score": 1-5,
     "rationale": "...",
     "remediation": [ { "severity": "critical|major|minor", "description": "...", "suggestion": "...", "file": "...", "line": 1 } ]
   }
   ```
   A "critical violation" means any `remediation` item with `severity: "critical"`.

### 4.4 Decision Matrix

Combine reviewer and judge verdicts to determine the task outcome:

The dual-threshold score bands are the single source of truth; the judge's `verdict` string is advisory:

| Reviewer | Judge score band | Outcome |
|----------|------------------|---------|
| APPROVED | >= 4 AND no critical violations | **APPROVED** — task passes |
| APPROVED | <= 2 OR any critical violation | **REVISE** — use judge `remediation` items as findings for fixer |
| APPROVED | = 3, no criticals (middle band) | **APPROVED** — reviewer verdict is the tiebreaker; carry judge `remediation` into the summary as follow-up notes |
| REVISE | any | **REVISE** — union of reviewer findings + judge `remediation` (appended to fixer prompt) |

### 4.5 Graceful Degradation

If the `mcp__codex__codex` tool is unavailable (connection error, auth failure) or errors on two consecutive attempts within the session:
- **Skip the judge** for the remainder of the session
- Reviewer verdict stands alone (original behavior)
- Record `"judge: unavailable"` in the execution summary

Do NOT block the pipeline waiting for judge recovery.

### 4.6 Process Verdicts

**If outcome = APPROVED:**
- The lead writes the approval marker via Bash (the only Bash the lead runs besides diff/judge — required by the TaskCompleted hook).
  **Important**: sanitize the task_id to `[a-zA-Z0-9_-]` only (replace other chars with `_`) so the filename matches what the hook expects:
  ```bash
  mkdir -p ~/.claude/insistir-state/insistir-<topic> && \
  echo "APPROVED by [reviewer-name] + judge round [N] $(date -u +%Y-%m-%dT%H:%M:%SZ)" > ~/.claude/insistir-state/insistir-<topic>/[sanitized_task_id].approved
  ```
- Mark task complete. (The TaskCompleted hook verifies the marker exists.)

**If outcome = REVISE and round < max_review_rounds:**
- **Persist P0–P2 findings as TODO files** in `todos/` using the file-todos naming convention (`{id}-pending-{priority}-{description}.md`). This creates a persistent record of significant findings even if the fixer resolves them, enabling lifecycle tracking across sessions. Skip P3 (nice-to-have). Priorities follow the reviewer's scale: P0 blocking, P1 urgent, P2 normal, P3 low.
- Spawn a **new fixer agent** with the findings embedded in its prompt:
  ```
  Task tool:
    name: "fixer-t1-r1"
    team_name: "insistir-<topic>"
    subagent_type: "insistir:insistir-worker"
    prompt: |
      ## Context
      - Plan file: [path to <topic>-plan.md]
      - Overview: [relevant goals from plan]
      - Constraints: [risks from plan]

      ## Your Task
      **Task [ID]: [Name]**
      Acceptance Criteria: [list from plan]

      ## Review Findings (Round [N])
      [paste the full findings JSON from the reviewer]

      ## Judge Remediation Items
      [paste judge remediation items if present]

      Fix all P0/P1 findings and any FAIL items in the requirements checklist.
      Address judge remediation items. Use your judgment on P2/P3 findings.
  ```
- After receiving the fixer's completion message, immediately send `shutdown_request` to the fixer.
- Spawn a **fresh reviewer** (`reviewer-t1-r2`) — increment round in name.
- The fresh reviewer re-evaluates from scratch against acceptance criteria.
- This avoids context pollution — the new reviewer has no memory of previous rounds.

**If outcome = REVISE and round >= max_review_rounds:**
- Mark task as `failed` with note: "Exceeded review budget ([N] rounds). Consider decomposing into smaller tasks."
- Log the failure reason in the plan file. No fixer is spawned.

### 4.7 Lead Tracks Review Rounds

The lead maintains a mental model of each task's review state:
```
T1: round 1/2 → REVISE (reviewer+judge) → fixer-t1-r1 → round 2/2 → APPROVED (reviewer+judge) ✓
T2: round 1/2 → APPROVED (reviewer+judge) ✓
T3: round 1/2 → REVISE → fixer-t3-r1 → round 2/2 → REVISE → FAILED (max rounds)
```

### 4.8 Lead Intervenes Only If Needed

The lead only steps in if:
- Deadlock or unexpected errors → lead escalates to user
- Task fails max rounds → lead reports to user with decomposition suggestion

---

## Phase 5: Repeat

1. Use **TaskUpdate** to mark completed/failed tasks
2. Run `python ${CLAUDE_PLUGIN_ROOT}/skills/insistir/scripts/insistir.py status <topic>-plan.md` to check progress
3. Check **TaskList** for newly unblocked tasks
4. Spawn next wave of workers → iterative cross-review → repeat
5. Continue until all tasks complete or fail

---

## Phase 6: Cleanup

All agents should already be shut down at this point (each was shut down after finishing its work).

1. **Safety net**: If any agents are unexpectedly still active, send `shutdown_request` to each remaining teammate. Wait up to **10 seconds** for `shutdown_response`. If a teammate does not respond:
   - Send ONE more `shutdown_request` with explicit content: "All work is done. Please shut down immediately."
   - Wait another 10 seconds. If still no response, proceed with force cleanup — remove team/task directories file-by-file (avoid `rm -rf` on home paths as security hooks may block it):
     ```bash
     rm ~/.claude/teams/insistir-<topic>/*.json 2>/dev/null; rmdir ~/.claude/teams/insistir-<topic> 2>/dev/null
     rm ~/.claude/tasks/insistir-<topic>/*.json 2>/dev/null; rmdir ~/.claude/tasks/insistir-<topic> 2>/dev/null
     ```
   - Do NOT loop indefinitely waiting for unresponsive agents.
2. **TeamDelete** to remove team resources (if agents responded and team still exists)
3. Remove state directory:
   ```bash
   rm ~/.claude/insistir-state/insistir-<topic>/*.approved 2>/dev/null
   rmdir ~/.claude/insistir-state/insistir-<topic> 2>/dev/null
   ```
4. **You MUST render the execution summary before finishing.** Use the template in [references/summary-template.md](references/summary-template.md). Show which tasks passed/failed, how many review rounds each took, what files were changed, and per-task judge verdicts (or `"judge: unavailable"` if the judge was skipped).
5. **Offer to compound learnings.** After the summary, check if the session involved solving a non-trivial problem worth documenting. If so, offer:

   > "Did the team solve a non-trivial problem worth documenting? I can run `/insistir:compound` to capture the solution in `docs/solutions/` for future sessions to learn from."

   If the user accepts, run `/insistir:compound` with a summary of the key problem and solution. Skip this offer if all tasks were straightforward or if no significant debugging/problem-solving occurred.

---

## Resources

- **Plan template**: [references/plan-template.md](references/plan-template.md) — task structure with required fields
- **Summary template**: [references/summary-template.md](references/summary-template.md) — execution report format
- **Plan CLI**: `scripts/insistir.py` — validate plans, compute waves, check status
