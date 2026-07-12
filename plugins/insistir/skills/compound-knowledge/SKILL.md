---
name: compound-knowledge
description: >
  Document a solved problem to compound team knowledge. Triggered by phrases
  like "that worked", "it's fixed", "problem solved", or explicitly via the
  /insistir:compound command. Orchestrates parallel sub-agents to analyze the
  problem, extract the solution, and suggest prevention — then assembles a
  single searchable solution file in docs/solutions/.
---

## Compound Knowledge Skill

Capture a solved problem as searchable documentation so the team never solves the same problem twice.

**Only ONE file gets written — the final documentation.** All sub-agents return text only.

### Categories

Solutions are organized into these categories (used as subdirectories under `docs/solutions/`):

- `build-errors`
- `test-failures`
- `runtime-errors`
- `performance-issues`
- `database-issues`
- `security-issues`
- `ui-bugs`
- `integration-issues`
- `logic-errors`

### Filename Convention

`docs/solutions/<category>/YYYY-MM-DD-<kebab-description>.md`

Example: `docs/solutions/runtime-errors/2026-02-13-null-pointer-in-auth-middleware.md`

### Solution Template

Use the template at [solution-template.md](references/solution-template.md) for the final file format.

---

## Orchestration: 3 Phases

### Phase 1: Parallel Information Gathering (3 sub-agents via Task tool)

Spawn these three sub-agents in parallel using the Task tool. Each receives the conversation context about the solved problem and returns structured text. **None of these sub-agents write files.**

#### 1a. Context Analyzer

Prompt: Analyze the conversation and codebase context to extract:
- **Problem type**: Which category from the list above best fits
- **Affected area**: Files, modules, or systems involved
- **Severity**: low / medium / high / critical
- **How detected**: How the problem surfaced (test failure, user report, monitoring alert, etc.)
- **Impact**: What was broken or degraded

Return as structured text.

#### 1b. Solution Extractor

Prompt: Analyze the conversation and code changes to extract:
- **Root cause**: Why the problem happened (1-2 paragraphs)
- **Code references**: Specific files and lines involved
- **What fixed it**: The actual changes made (before/after snippets)
- **Key insight**: The non-obvious realization that led to the fix

Return as structured text.

#### 1c. Prevention Strategist

Prompt: Based on the problem and solution, determine:
- **How to prevent recurrence**: Specific practices, checks, or guards
- **Tests to add**: What test cases would catch this in the future
- **Monitoring**: Any alerts or checks that should exist
- **Related patterns**: Similar problems that might exist elsewhere

Return as structured text.

### Phase 2: Assembly (sequential)

The orchestrator (you) assembles the outputs from all three sub-agents into a single solution file:

1. Read the [solution-template.md](references/solution-template.md) for the expected format
2. Determine the category from the Context Analyzer's output
3. Generate the filename: `YYYY-MM-DD-<kebab-description>.md` using today's date
4. Create the directory `docs/solutions/<category>/` if it doesn't exist
5. Write the single assembled file at `docs/solutions/<category>/<filename>.md`
6. Fill in all YAML frontmatter fields and all sections from the sub-agent outputs

**This is the only file write in the entire skill.**

### Phase 3: Optional Review

After writing the file, offer the user a specialized review based on the category:

- **security-issues**: "Want me to check if this security fix needs broader application?"
- **performance-issues**: "Want me to verify the performance improvement with benchmarks?"
- **build-errors / test-failures**: "Want me to run the test suite to confirm the fix holds?"
- **Other categories**: "Want me to search for similar patterns elsewhere in the codebase?"

Only proceed with the review if the user confirms.

---

## Rules

- Sub-agents return TEXT only — they do not write files
- Only ONE file gets written — the final documentation in `docs/solutions/<category>/`
- Always use the solution template format
- Always confirm the category with the user if ambiguous
- Tag with relevant keywords for future searchability
