The solution template below defines the format for all files in `docs/solutions/`.

```markdown
---
title: "<Descriptive title of the problem and solution>"
date: YYYY-MM-DD
category: "<one of: build-errors, test-failures, runtime-errors, performance-issues, database-issues, security-issues, ui-bugs, integration-issues, logic-errors>"
tags:
  - "<keyword1>"
  - "<keyword2>"
  - "<keyword3>"
severity: "<low|medium|high|critical>"
status: "<draft|validated>"
---

## Problem

**What happened**: <Clear description of the problem>

**How detected**: <How the problem was discovered — test failure, user report, monitoring, etc.>

**Impact**: <What was broken or degraded, who was affected>

## Root Cause

**Why it happened**: <Technical explanation of the underlying cause>

**Code references**:
- `path/to/file.ts:42` — <what this code was doing wrong>
- `path/to/other.ts:17` — <related problematic code>

## Solution

**What fixed it**: <Summary of the fix approach>

**Code changes**:

Before:
\`\`\`
<code that was broken>
\`\`\`

After:
\`\`\`
<code that fixed it>
\`\`\`

**Key insight**: <The non-obvious realization that led to the fix>

## Prevention

**How to prevent recurrence**:
- <Specific practice, check, or guard>
- <Another prevention measure>

**Tests to add**:
- <Test case description>
- <Another test case>

**Monitoring**:
- <Alert or check that should exist>

## Related

- <Link to issue/PR>
- <Link to related solution docs>
- <Link to external resources>
```
