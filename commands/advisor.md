---
description: Get a second opinion from Codex (GPT-5) on your current plan, diff, or a specific question.
argument-hint: "[question or topic — defaults to reviewing the current plan/diff]"
---

# Codex Advisor

Get an independent second opinion from a different-provider model (Codex/GPT-5) to challenge assumptions, identify risks, and surface alternative approaches.

## Process

### 1. Gather Context

Determine what to send for review, in priority order:

1. **User provided a question** → use that question as-is
2. **Active plan file exists** (`*-plan.md` in cwd) → read and summarize the plan
3. **Uncommitted changes exist** → run `git diff` to capture the current diff
4. **None of the above** → stop and tell the user: "Nothing to review — provide a question, create a plan, or make some changes first." Do NOT call Codex with an empty context.

Compose a context block from the above. Keep it under 12,000 characters — truncate diffs to the most significant files if needed.

### 2. Call Codex

Invoke the `mcp__codex__codex` tool:

```
mcp__codex__codex:
  prompt: |
    You are an adversarial advisor reviewing work by a different AI model.
    Your job: challenge assumptions, identify risks, suggest alternatives.
    Do NOT be sycophantic. Disagree where warranted. Be specific and cite evidence.

    ## Context
    {{CONTEXT}}

    ## Instructions
    1. Identify the 2-3 riskiest assumptions or decisions
    2. For each, explain what could go wrong and suggest an alternative
    3. Note anything missing that should have been considered
    4. Give an overall confidence assessment (high/medium/low) for the approach
  sandbox: "read-only"
  approval-policy: "never"
  cwd: "<project root — use git rev-parse --show-toplevel>"
```

### 3. Extract Thread ID

The response includes a `threadId` in `structuredContent`. Store it for the session — if the user asks follow-up questions, use `mcp__codex__codex-reply` with that `threadId` instead of starting a new session.

### 4. Present Results

Format the output as:

```
## Codex (GPT-5) says:

[Codex's response, lightly reformatted for readability]

## Claude's reconciliation:

- **Agree**: [points where Claude concurs with Codex's assessment]
- **Disagree**: [points where Claude has contrary evidence or reasoning]
- **Recommend**: [synthesized recommendation incorporating both perspectives]
```

### 5. Follow-up

If the user asks a follow-up question about the same topic, use `mcp__codex__codex-reply` with the stored `threadId` to continue the conversation thread. Present the response in the same dual-perspective format.

## Graceful Degradation

If `mcp__codex__codex` is unavailable (tool not found, MCP server not running, or call errors):

1. Tell the user: "Codex MCP server is not available. This requires the Codex CLI to be installed and authenticated (`codex login` or OPENAI_API_KEY set)."
2. Offer: "I can run the same adversarial-advisor analysis using a fresh Claude subagent instead. Want me to proceed?"
3. If accepted, spawn a subagent with the same adversarial prompt. Label the output as "Claude subagent" instead of "Codex (GPT-5)".

Never fail silently. Always inform the user which provider produced the advisory opinion.
