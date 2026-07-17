---
title: OpenAI GPT-5 / Codex Models — Prompt Engineering Reference
last_verified: 2026-07-16
sources_verified: true
covers: GPT-5, GPT-5.1, GPT-5.2, GPT-5.3, Codex (GPT-5.1-Codex-Max, GPT-5.3-Codex)
---

> **Verification:** All URLs listed below were fetched and content-verified on 2026-07-16. Each section's Source line points to the specific page supporting that section's claims.

# GPT-5 Prompt Engineering Techniques

Sourced from OpenAI's official cookbook, prompting guides, and Codex documentation. Apply these techniques when generating prompts for any GPT-5 family model.

## 1. Reasoning effort

The `reasoning_effort` parameter controls how deeply the model thinks. Options range from minimal to high, with medium as default.
- **High:** Use for complex multi-step tasks, code generation, analysis.
- **Medium:** Default for most tasks.
- **Low:** Use for simple classification, formatting, or quick lookups to reduce latency.

Higher reasoning effort increases exploration depth but also cost and latency. Unlike Claude's effort levels, this is a single parameter rather than named tiers.

Source: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide

## 2. Verbosity steering

GPT-5 has a `verbosity` API parameter influencing final answer length (distinct from thinking length). Can be set globally or overridden with natural language instructions for specific contexts — e.g., "high verbosity for coding tools only."

For concise output, set low verbosity and reinforce with: "Lead with the answer. Supporting detail comes after."

Source: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide

## 3. Agentic eagerness control

Steers the balance between model autonomy and explicit guidance:
- **Reduce eagerness:** Lower reasoning effort + define clear exploration criteria + explicit stop conditions.
- **Increase eagerness:** Higher reasoning effort + persistence instructions: "Keep going until the user's query is completely resolved."

Source: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide

## 4. Tool preambles

Instruct the model to provide upfront plans and progress updates during tool execution:

```
Always begin by rephrasing the user's goal in your own words, then outline a structured plan before executing tool calls.
```

This improves user comprehension of agent workflows and grounds the model's actions.

Source: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide

## 5. Instruction hierarchy and contradiction avoidance

GPT-5's surgical precision in following directives makes contradictions particularly damaging. "Poorly-constructed prompts containing contradictory or vague instructions can be more damaging to GPT-5" — contradictions waste reasoning tokens as the model tries to reconcile conflicting directives.

**Critical rule:** Before finalizing a GPT-5 prompt, review for internal contradictions. Remove soft permissions that undermine constraints (e.g., "prefer stdlib" + "use external packages if simpler" creates a decision fork).

Source: https://developers.openai.com/cookbook/examples/gpt-5/prompt-optimization-cookbook

## 6. Prompt optimization

OpenAI provides a **GPT-5 Prompt Optimizer** in the Playground that automatically refines prompts. Per the documentation: "The goal of the Prompt Optimizer is to give your prompt the best practices and formatting most effective for our models." Use it to:
1. Remove contradictory instructions.
2. Add missing format specifications.
3. Align few-shot examples with the prompt's stated rules.

You can also ask GPT-5 itself to review a prompt and suggest improvements -- a useful manual complement to the Playground tool.

Source: https://developers.openai.com/cookbook/examples/gpt-5/prompt-optimization-cookbook

## 7. Structured XML specifications

GPT-5 also benefits from XML tags for organizing complex instructions, similar to Claude:

```xml
<context_gathering>Instructions for how to gather context</context_gathering>
<tool_preambles>Instructions for tool use communication</tool_preambles>
<output_format>Expected output structure</output_format>
```

Source: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide

## 8. GPT-5.2 specific improvements

GPT-5.2 improves on GPT-5:
- Better token efficiency on medium-to-complex tasks.
- Cleaner formatting with less unnecessary verbosity.
- Clear gains in structured reasoning, tool grounding, and multimodal understanding.
- Designed for enterprise and agentic workloads.

Prompting strategy should focus on evaluability, strict output formats (JSON schemas), negative constraints ("Do not..."), and XML scaffolding for agents.

Source: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-2_prompting_guide

## 9. Codex CLI / AGENTS.md specifics

AGENTS.md is the persistent instruction file for OpenAI's Codex CLI — the equivalent of Claude Code's CLAUDE.md.

**File discovery and merging:**
- Files named `AGENTS.md` are automatically discovered from `~/.codex/` and repo directories.
- Codex concatenates files root-to-leaf, with later (deeper) directories overriding earlier ones.
- Each file appears as a separate user-role message prefixed with `# AGENTS.md instructions for <directory>`.

**Best practices:**
- A short, accurate AGENTS.md beats a long vague one.
- Remove rules vague enough that Codex might not know what to do with them.
- Use the starter prompt (GPT-5.1-Codex-Max) as a base, then make tactical additions.
- Emphasize "bias to action" over planning: "Once the user gives a direction, proactively gather context, plan, implement, test, and refine without waiting for additional prompts."

**Parallel tool batching:**
- "If you need multiple files, read them together" using parallel tool calls. Never read files sequentially unless the next file's location depends on previous results.

**Plan tool usage:**
- Skip planning for straightforward tasks (~25% of the time).
- When planning, update plans after completing sub-tasks and mark all items as Done/Blocked/Cancelled.

Source: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
Source: https://learn.chatgpt.com/docs/agent-configuration/agents-md

## 10. Codex code quality instructions

Effective patterns for Codex coding prompts:
- "Optimize for correctness, clarity, and reliability over speed; avoid risky shortcuts, speculative changes, and messy hacks."
- Follow existing codebase patterns, helpers, naming, and formatting.
- Avoid broad try/catch blocks; propagate or surface errors explicitly.
- No silent failures or early returns without logging.

**Frontend-specific:** "Avoid collapsing into 'AI slop' or safe, average-looking layouts. Aim for interfaces that feel intentional, bold, and a bit surprising."

Source: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

## 11. Mid-turn communication (GPT-5.3+)

**Preambles:** Short, human-readable progress updates (1-2 sentences) sent alongside tool calls. Aim for updates every 1-3 execution steps.

**Phase parameter:** Preserve `phase` metadata (null, "commentary", or "final_answer") on assistant items — required for GPT-5.3-Codex to prevent early stopping.

Source: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

## 12. Prompt optimization workflow

OpenAI's recommended optimization process:
1. Identify contradictory signals in the prompt.
2. Use the Playground Optimizer for automatic refinement.
3. Replace ambiguous guidance with "hard requirements" — exact algorithms, data structures, memory bounds.
4. For retrieval tasks, establish "behavioral priorities" ranking grounding over helpfulness.
5. Define clear "refusal policies" for out-of-scope queries.

Source: https://developers.openai.com/cookbook/examples/gpt-5/prompt-optimization-cookbook
