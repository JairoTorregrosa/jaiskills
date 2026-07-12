# Compound Patterns Integration Plan

## Goal

Adopt three key patterns from the compound-engineering plugin into insistir: knowledge compounding (docs/solutions/), file-based TODO lifecycle (todos/), and plan deepening with parallel research agents. Extend the existing plugin with new agents, skills, commands, and templates.

## Constraints

- **Tech stack**: Python scripts (no external deps), Markdown agents/skills/commands with YAML frontmatter
- **Patterns**: Follow existing insistir conventions (agent frontmatter structure, hook patterns, script style)
- **Risks**: New commands must not collide with built-in Claude Code commands; new skills must follow progressive disclosure; agent tools must be minimal (principle of least privilege)
- **Naming**: All new commands prefixed with plugin name via directory structure (auto-prefixed as `insistir:*`)

## Config

- **max_review_rounds**: 2

---

## Tasks

### T1: Knowledge Compounding System

- **depends_on**: none
- **location**: `plugins/insistir/agents/insistir-learnings-researcher.md`, `plugins/insistir/skills/compound-knowledge/SKILL.md`, `plugins/insistir/skills/compound-knowledge/references/solution-template.md`, `plugins/insistir/commands/compound.md`
- **description**: Create a knowledge compounding system that captures solved problems as searchable documentation. Includes: (1) A learnings-researcher agent (model: sonnet, read-only) that searches docs/solutions/ for past solutions relevant to a query using grep-first strategy with parallel keyword searches including synonyms. (2) A compound-knowledge skill that orchestrates parallel sub-agents to gather context about a solved problem, then assembles a single solution file. The skill should define 3 parallel information-gathering phases (context analyzer, solution extractor, prevention strategist) where sub-agents return TEXT only and only the orchestrator writes the file. (3) A solution-template.md reference with YAML frontmatter (title, date, category, tags, severity, status) and sections (Problem, Root Cause, Solution, Prevention, Related). (4) A compound command that triggers the skill. Categories: build-errors, test-failures, runtime-errors, performance-issues, database-issues, security-issues, ui-bugs, integration-issues, logic-errors.
- **acceptance_criteria**:
  - Learnings-researcher agent has frontmatter with model: sonnet, allowed tools: Read, Glob, Grep, SendMessage, and disallowed tools: Edit, Write, Bash
  - Learnings-researcher uses grep-first strategy: parallel keyword searches (including synonyms) to pre-filter before reading files
  - Compound-knowledge SKILL.md defines 3 parallel sub-agent phases that return text only
  - SKILL.md explicitly states "Only ONE file gets written - the final documentation"
  - Solution template has valid YAML frontmatter with all required fields
  - Solution template has all required sections: Problem, Root Cause, Solution, Prevention, Related
  - Compound command has proper YAML frontmatter (name, description, argument-hint)
  - Command routes to the compound-knowledge skill with $ARGUMENTS
  - Category list matches: build-errors, test-failures, runtime-errors, performance-issues, database-issues, security-issues, ui-bugs, integration-issues, logic-errors
- **validation**: `python plugins/insistir/skills/insistir/scripts/insistir.py validate compound-patterns-plan.md`
- **status**: pending

### T2: File-based TODO Lifecycle

- **depends_on**: none
- **location**: `plugins/insistir/skills/file-todos/SKILL.md`, `plugins/insistir/skills/file-todos/references/todo-template.md`, `plugins/insistir/commands/triage.md`, `plugins/insistir/commands/resolve-todos.md`
- **description**: Create a file-based TODO management system for tracking review findings through their lifecycle. Includes: (1) A file-todos skill defining the TODO format, lifecycle, and management operations. TODOs live in todos/ with naming convention {id}-{status}-{priority}-{description}.md. Statuses: pending (from review), ready (approved in triage), complete (resolved). Priorities: p1 (critical, blocks merge), p2 (important, should fix), p3 (nice-to-have). (2) A todo-template.md reference with YAML frontmatter (status, priority, issue_id, tags, dependencies) and sections (Problem Statement, Findings, Proposed Solutions, Recommended Action, Acceptance Criteria, Work Log). (3) A triage command that presents pending todos one by one for user decision (approve->ready, skip->delete, modify). The triage command MUST set model to haiku in frontmatter for cost efficiency and MUST include the rule "DO NOT CODE ANYTHING DURING TRIAGE." (4) A resolve-todos command that reads ready todos, spawns parallel worker agents (one per todo), each fixes and commits, then marks complete by renaming file.
- **acceptance_criteria**:
  - file-todos SKILL.md defines naming convention: {id}-{status}-{priority}-{description}.md
  - SKILL.md defines all 3 statuses (pending, ready, complete) and 3 priorities (p1, p2, p3)
  - Todo template has YAML frontmatter with: status, priority, issue_id, tags, dependencies
  - Todo template has all sections: Problem Statement, Findings, Proposed Solutions, Recommended Action, Acceptance Criteria, Work Log
  - Triage command frontmatter includes `model: haiku` for cost efficiency
  - Triage command contains explicit rule: "DO NOT CODE ANYTHING DURING TRIAGE"
  - Triage command presents todos one-by-one with severity/description and offers approve/skip/modify
  - Resolve-todos command spawns parallel agents (one per ready todo)
  - Resolve-todos command renames files from ready to complete after resolution
- **validation**: `python plugins/insistir/skills/insistir/scripts/insistir.py validate compound-patterns-plan.md`
- **status**: pending

### T3: Research and Plan Deepening System

- **depends_on**: none
- **location**: `plugins/insistir/agents/insistir-researcher.md`, `plugins/insistir/commands/deepen-plan.md`
- **description**: Create a research system for enhancing plans with external knowledge. Includes: (1) A insistir-researcher agent (model: sonnet, read-only + web access) that researches best practices, framework documentation, and codebase patterns. Tools: Read, Glob, Grep, WebFetch, WebSearch, SendMessage. Disallowed: Edit, Write. The agent should follow the compound-engineering pattern: check available skills/docs first, do mandatory deprecation checks for external APIs, then online research if needed. Returns structured findings as text to the lead. (2) A deepen-plan command that takes a plan file path, parses its sections, spawns parallel researcher agents (one per section that references external tech/frameworks), optionally searches docs/solutions/ for relevant past solutions, and enhances each section with Research Insights, Implementation Details, Edge Cases, and References. The command should use disable-model-invocation: true since it orchestrates sub-agents.
- **acceptance_criteria**:
  - Researcher agent has frontmatter with model: sonnet, color defined
  - Researcher agent allowed tools: Read, Glob, Grep, WebFetch, WebSearch, SendMessage
  - Researcher agent disallowed tools include: Edit, Write
  - Researcher agent instructions prioritize: skills/docs first -> deprecation check -> online research
  - Researcher agent returns structured text findings (not files)
  - Deepen-plan command has proper YAML frontmatter with name, description, argument-hint
  - Deepen-plan command has disable-model-invocation: true
  - Command parses plan sections and spawns parallel researchers per section
  - Command enhances sections with: Research Insights, Implementation Details, Edge Cases, References
  - Command offers post-enhancement options (view diff, start work, deepen further)
- **validation**: `python plugins/insistir/skills/insistir/scripts/insistir.py validate compound-patterns-plan.md`
- **status**: pending

### T4: Integration into Main Insistir Skill

- **depends_on**: T1, T2, T3
- **location**: `plugins/insistir/skills/insistir/SKILL.md`
- **description**: Wire all new components into the main insistir orchestration skill. Changes: (1) Phase 1 (Plan) - Add step 1.1.5 "Search Past Solutions" that spawns insistir-learnings-researcher to search docs/solutions/ for relevant past problems before creating the plan. Include findings in task descriptions when spawning workers. (2) Phase 1 (Plan) - Add optional step 1.3.5 "Deepen Plan" that offers to run /insistir:deepen-plan on the generated plan before proceeding to execution. (3) Phase 4 (Cross-Review) - When reviewer sends REVISE findings, also create todo files in todos/ using the file-todos naming convention for any P1/P2 findings. This creates a persistent record even if the fixer resolves them. (4) Phase 6 (Cleanup) - After displaying the execution summary, offer to run /insistir:compound to document significant learnings from the session. Add a check: "Did the team solve a non-trivial problem worth documenting?" (5) Update the Phase 0 Intake to mention the new capabilities (knowledge search, plan deepening, todo tracking). IMPORTANT: Read the CURRENT SKILL.md from the repo (not cache) before editing, as it contains v0.2.0 fixes not yet in cache.
- **acceptance_criteria**:
  - Phase 1 includes a learnings search step that spawns insistir-learnings-researcher
  - Phase 1 includes optional deepen-plan step with user confirmation
  - Phase 4 creates todo files for P1/P2 findings during REVISE processing
  - Phase 6 offers /insistir:compound after execution summary
  - Phase 0 mentions new capabilities (knowledge search, plan deepening, todo tracking)
  - All existing functionality preserved (no regressions in the 7-phase pipeline)
  - New steps use consistent formatting with existing SKILL.md style
  - References to new agents/skills use correct plugin-qualified names (insistir:*)
- **validation**: `python plugins/insistir/skills/insistir/scripts/insistir.py validate compound-patterns-plan.md`
- **status**: pending

### T5: Plugin Metadata and Documentation Updates

- **depends_on**: T1, T2, T3
- **location**: `plugins/insistir/.claude-plugin/plugin.json`, `README.md`, `CHANGELOG.md`
- **description**: Update all plugin metadata and documentation to reflect the new components. (1) plugin.json - Update description to reflect new component counts (4 agents, 4 commands, 3 skills). Keep version at 1.0.0 since these are unreleased changes that will be bumped together. (2) README.md - Add new sections describing: Knowledge Compounding (what it is, how docs/solutions/ works, the compound command), File-based TODO Lifecycle (the lifecycle diagram, triage and resolve commands), Plan Deepening (the research system, deepen-plan command). Update the component table to include all new agents, commands, and skills with descriptions. Update the pipeline diagram to show the new optional stages. (3) CHANGELOG.md - Add a new v1.1.0 entry (unreleased) documenting all additions: new agents (learnings-researcher, researcher), new skills (compound-knowledge, file-todos), new commands (compound, triage, resolve-todos, deepen-plan), and integration changes to the main SKILL.md.
- **acceptance_criteria**:
  - plugin.json description mentions correct component counts (4 agents, 4 commands, 3 skills)
  - README.md has sections for Knowledge Compounding, File-based TODO Lifecycle, Plan Deepening
  - README.md component table lists ALL agents, commands, and skills (old and new)
  - README.md pipeline diagram shows new optional stages
  - CHANGELOG.md has v1.1.0 (Unreleased) entry with all additions categorized
  - CHANGELOG.md follows Keep a Changelog format (Added, Changed sections)
  - All markdown renders correctly (no broken links, consistent formatting)
- **validation**: `python plugins/insistir/skills/insistir/scripts/insistir.py validate compound-patterns-plan.md`
- **status**: pending

---

## Dependency Graph

```
T1 (Knowledge Compounding) ──────┐
                                  ├──→ T4 (SKILL.md Integration)
T2 (File-based TODOs) ───────────┤
                                  ├──→ T5 (Metadata & Docs)
T3 (Research & Deepening) ────────┘
```

## Parallel Execution Waves

| Wave | Tasks | Workers | Description |
|------|-------|---------|-------------|
| 1    | T1, T2, T3 | 3 | Foundation: all new components built in parallel |
| 2    | T4, T5 | 2 | Integration: wire into main skill + update docs |
