---
name: deepen-plan
description: "Enhance a plan with parallel research agents for each section"
argument-hint: "<plan-file>"
disable-model-invocation: true
---

Enhance a plan file with research insights by spawning parallel research agents.

## Step 1: Locate the Plan File

If `$ARGUMENTS` specifies a path, use it. Otherwise, find the most recent `*-plan.md` file in the current working directory using Glob.

Read the plan file. If it cannot be found or read, report the error and stop.

Save the original content for later diffing.

## Step 2: Parse Plan Structure

Parse the plan file to extract:

1. **Task sections**: Each `### T<N>: <title>` block with its description, location, acceptance criteria
2. **Technologies**: For each task, identify external technologies, frameworks, libraries, or APIs mentioned (e.g., "Python", "TypeScript", "React", "PostgreSQL", "Claude API")
3. **Internal references**: File paths and internal patterns mentioned in each task

Build a list of `(task_id, task_title, task_description, technologies[])` tuples.

## Step 3: Optional Past Solutions Search

If `docs/solutions/` exists in the project:

Spawn a `insistir:insistir-learnings-researcher` agent via the Task tool with a query summarizing the plan's overall goal and key technologies. This searches for relevant past solutions that could inform the plan.

This runs in parallel with Step 4.

## Step 4: Spawn Parallel Researchers

For each task section that references at least one external technology, framework, or library:

Spawn a `insistir:insistir-researcher` agent via the Task tool. Each researcher receives:

- The task title and full description
- The specific technologies to research for that task
- The project's tech stack context (from package.json, tsconfig.json, etc.)
- Instruction to send findings back to you (the orchestrator) via SendMessage

Spawn all researchers in parallel — do NOT wait for one to finish before starting the next.

Skip tasks that only reference internal codebase patterns with no external dependencies.

## Step 5: Collect All Findings

Wait for all spawned agents (researchers + optional learnings researcher) to send their findings via SendMessage.

For each agent, after receiving findings, send a `shutdown_request` to terminate it.

## Step 6: Synthesize Findings

Process all collected findings:

1. **Deduplicate**: Merge overlapping findings across researchers
2. **Group by task**: Associate each finding with the task section(s) it applies to
3. **Cross-reference**: If the learnings researcher found relevant past solutions, match them to tasks
4. **Prioritize**: Order findings by relevance and actionability

## Step 7: Enhance Plan Sections

For each task section that received research findings, append these subsections after the existing acceptance criteria (and before validation if present):

### Research Insights
Key findings relevant to this task from the research phase. Bullet list of specific, factual findings with sources.

### Implementation Details
Specific patterns, API usage, version-specific code examples, and recommended approaches.

### Edge Cases
Gotchas, version compatibility issues, deprecation warnings, known bugs, and things to watch out for.

### References
URLs to official docs, relevant file paths in the codebase, and links to past solutions.

**Formatting rules:**
- Use the same indentation and markdown style as the existing plan
- Do NOT modify existing content (description, acceptance criteria, validation)
- Only append the new subsections
- Keep each subsection concise — bullet points, not paragraphs

## Step 8: Write Enhanced Plan

Write the enhanced plan back to the original file path.

## Step 9: Present Summary

Display a summary of what was enhanced:

```
## Plan Deepening Complete

**Plan**: <filename>
**Tasks researched**: <N> of <total>
**Research agents spawned**: <count>
**Past solutions found**: <count or "none" or "skipped (no docs/solutions/)">

### Enhancements by Task

- **T1: <title>**: <1-line summary of key insight>
- **T3: <title>**: <1-line summary of key insight>
- (tasks without external tech are listed as "No external research needed")
```

## Step 10: Post-Enhancement Options

Present the user with options via conversation:

1. **View the diff**: Show `git diff` of the changes made to the plan file
2. **Start working**: Suggest running the main orchestration skill (`/insistir`) or proceed to execution
3. **Deepen further**: Re-run on specific sections that need more research
4. **Revert changes**: Restore the original plan content from the saved copy
