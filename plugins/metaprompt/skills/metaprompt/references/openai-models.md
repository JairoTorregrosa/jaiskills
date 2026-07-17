---
title: OpenAI GPT-5.6 / GPT-5 / Codex Models — Prompt Engineering Reference
last_verified: 2026-07-16
sources_verified: true
covers: GPT-5.6 (Sol, Terra, Luna), GPT-5, GPT-5.1, GPT-5.2, GPT-5.3, Codex (GPT-5.1-Codex-Max, GPT-5.3-Codex)
---

> **Verification:** All URLs listed below were fetched and content-verified on 2026-07-16. Each section's Source line points to the specific page supporting that section's claims.

# GPT-5.6 Family (GA 2026-07-09)

The GPT-5.6 family comprises three tiers — Sol, Terra, and Luna — with 1,050,000-token context, 128K output, and a February 2026 knowledge cutoff. All accept text and image input and produce text output. No fine-tuning, audio, or video support on any tier.

## Model Selection Table

| Model | ID | Alias | Input $/MTok | Output $/MTok | Best For |
|---|---|---|---|---|---|
| Sol | `gpt-5.6-sol` | `gpt-5.6` | $5 | $30 | Hardest coding, agents, research — frontier intelligence |
| Terra | `gpt-5.6-terra` | — | $2.50 | $15 | Default baseline for agent workflows — balanced cost/quality |
| Luna | `gpt-5.6-luna` | — | $1 | $6 | High-volume with reliable grading — cost-sensitive workloads |

**Long-context surcharge:** Inputs exceeding 272K tokens are billed at 2x input rate and 1.5x output rate. Prompt cache writes cost 1.25x base input; cache reads save 90%.

**Selection guidance:** Start with Terra for most agent and workflow tasks. Use Sol only for problems that demonstrably need frontier intelligence (complex multi-step reasoning, hard coding, deep research). Luna at `xhigh` effort can match or beat Sol at `medium` effort at a fraction of the cost — always benchmark your actual workload before defaulting to Sol.

Source: https://developers.openai.com/api/docs/models/gpt-5.6-sol
Source: https://developers.openai.com/api/docs/models/gpt-5.6-terra
Source: https://developers.openai.com/api/docs/models/gpt-5.6-luna
Source: https://sebastianraschka.com/blog/2026/gpt-5-6-configurations.html

## GPT-5.6 Sol

Flagship model for the hardest professional problems. Use `gpt-5.6-sol` (or the alias `gpt-5.6`) when the task demands frontier reasoning: complex multi-file code generation, multi-step research synthesis, or agent orchestration with high-stakes decisions. Pair with `reasoning.mode: pro` for maximum intelligence when latency is acceptable.

Source: https://developers.openai.com/api/docs/models/gpt-5.6-sol
Source: https://simonwillison.net/2026/Jul/9/gpt-5-6/

## GPT-5.6 Terra

Balanced intelligence and cost. Terra is the recommended default for agent workflows, structured data processing, and production pipelines where Sol's ceiling is unnecessary. Its price-to-performance ratio makes it the natural starting point for new projects — move to Sol only if Terra measurably underperforms on your eval suite.

Source: https://developers.openai.com/api/docs/models/gpt-5.6-terra

## GPT-5.6 Luna

Optimized for high-volume, cost-sensitive workloads: classification, extraction, grading, routing, and subagent tiers. Luna at `xhigh` effort can outperform Sol at `medium` on coding benchmarks while costing substantially less — consult the Artificial Analysis Coding Agent Index for current comparisons.

Source: https://developers.openai.com/api/docs/models/gpt-5.6-luna
Source: https://sebastianraschka.com/blog/2026/gpt-5-6-configurations.html

## GPT-5.6 API Parameters

### reasoning.effort (6 levels)

Controls how deeply the model reasons before answering. GPT-5.6 supports six levels:

| Level | When to Use |
|---|---|
| `none` | Latency-critical tasks with no reasoning benefit (simple classification, format conversion) |
| `low` | Tool-use orchestration, light planning, straightforward coding |
| `medium` | Default for most workloads — balanced quality and latency |
| `high` | Complex debugging, deep planning, quality over latency |
| `xhigh` | Deep research, asynchronous workflows requiring maximum depth |
| `max` | Hardest quality-first workloads — reserve for problems that justify the cost |

Source: https://developers.openai.com/api/docs/guides/reasoning

### reasoning.mode

Independent of effort. Two modes:

- **`standard`** (default): Normal execution path.
- **`pro`**: Applies more model work before returning a single aggregated answer. Increases token usage and cost. Best for complex optimization, high-value coding, or deep analysis where quality matters more than latency.

Mode and effort are orthogonal — you can combine `low` effort with `pro` mode or `max` effort with `standard` mode.

Source: https://developers.openai.com/api/docs/guides/reasoning

### reasoning.context

Controls reasoning persistence across multi-turn conversations:

- **`auto`** (default): Model determines behavior.
- **`all_turns`**: Renders compatible reasoning from earlier turns into the next sample. Use when task goals remain stable; provide `previous_response_id`.
- **`current_turn`**: Reasoning available only within the active turn. Use when earlier reasoning is no longer relevant.

Source: https://developers.openai.com/api/docs/guides/reasoning

### text.verbosity

Sets the default detail level of the final answer:

- **`low`**: Terse, direct output.
- **`medium`**: Balanced detail.
- **`high`**: Expanded explanations.

GPT-5.6 is more concise by default than GPT-5.5. Legacy "be brief" prompt instructions may now over-correct — use this parameter instead of prompt text to control verbosity.

Source: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6

### Image detail: `original`

GPT-5.6 supports `detail: "original"` for image inputs, preserving full resolution without downscaling. Use this for higher-fidelity analysis of full-resolution images where fine details matter, such as reading small text, inspecting UI elements, or analyzing technical diagrams.

Source: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6

## GPT-5.6 Prompting Rules

GPT-5.6 rewards leaner, more precise prompts. These rules supersede older GPT-5.x prompt patterns where they conflict.

### State each instruction exactly once

Internal testing showed that removing duplicated instructions improved eval scores by 10-15% and reduced tokens by 41-66%. GPT-5.6 actively penalizes redundancy — repeating a rule for emphasis degrades performance rather than reinforcing it.

Source: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6

### Specify concrete behaviors, not vague adjectives

Replace "be thorough" with measurable instructions: "Check all files matching `*.test.ts` before declaring the fix complete." Replace "be concise" with the `text.verbosity` parameter. Vague tone adjectives waste reasoning tokens without guiding behavior.

Source: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6

### Define autonomy boundaries

Explicitly state what the model may do without confirmation and what requires approval:
- **Autonomous:** File reads, test runs, in-scope local edits, information gathering.
- **Requires confirmation:** External writes, destructive actions, purchases, material scope expansion.

Without these boundaries, GPT-5.6 may either over-ask (slowing workflows) or over-act (taking unreviewed actions).

Source: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6

### Control verbosity via parameter, not prompt

Use `text.verbosity` instead of prompt-based brevity instructions (see the `text.verbosity` section above for details and rationale).

Source: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6

## Programmatic Tool Calling (PTC)

PTC lets the model write JavaScript to orchestrate tool calls in an isolated runtime. Reserve it for bounded, data-heavy workflows where the model needs to filter, join, rank, or aggregate results across multiple tool calls. Parallel calls alone do not justify PTC — use it when the orchestration logic itself is complex enough that imperative code is clearer than a sequence of declarative tool invocations.

The multi-agent "ultra" mode is beta. Keep a single-agent fallback path in production.

Source: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6

## Prompt Cache Breakpoints

GPT-5.6 supports explicit prompt cache breakpoints — prefix markers that tell the API where cacheable content ends. Cached prefixes have a minimum 30-minute lifetime. Structure system prompts with stable content first (instructions, reference data) and variable content last (user query, conversation history) to maximize cache hits.

Source: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6

## Migration from GPT-5.x to GPT-5.6

1. **Effort baseline:** Keep your current GPT-5.5/5.4 effort level as the starting baseline, then benchmark one level lower.
2. **Verbosity cleanup:** Remove prompt-level brevity instructions; use `text.verbosity` instead.
3. **Deduplicate instructions:** Audit for repeated rules and collapse them. The 10-15% eval improvement from deduplication is effectively free.
4. **Test `reasoning.mode: pro`:** For your hardest tasks, compare `pro` mode against higher effort levels.
5. **Review autonomy prompts:** GPT-5.6's improved instruction-following requires explicit autonomy boundaries. Add clear statements of what the model may do without confirmation and what requires approval.

Source: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6

## Codex Integration with GPT-5.6

Use `codex -m gpt-5.6-sol` to run Codex CLI with the Sol model. In `config.toml`, set `model = "gpt-5.6"` to make it the default. Cloud tasks cannot change the default model at runtime — it must be set in configuration before the task starts.

Source: https://learn.chatgpt.com/docs/models

## Gotchas

- No fine-tuning available on any GPT-5.6 tier.
- No audio or video input/output support.
- Long-context surcharge (>272K tokens) can double effective input cost — monitor token counts in agent loops.
- SWE-Bench Pro: Sol 64.6% vs Claude Fable 5 80% — evaluate on your actual codebase, not benchmarks alone.

Source: https://simonwillison.net/2026/Jul/9/gpt-5-6/

---

# GPT-5.x Prompt Engineering Techniques

Sourced from OpenAI's official cookbook, prompting guides, and Codex documentation. These techniques apply across the GPT-5 family and remain valid for GPT-5.6 unless superseded by the sections above.

## 1. Reasoning effort (GPT-5.x)

The `reasoning_effort` parameter controls how deeply the model thinks. Options range from minimal to high, with medium as default.
- **High:** Use for complex multi-step tasks, code generation, analysis.
- **Medium:** Default for most tasks.
- **Low:** Use for simple classification, formatting, or quick lookups to reduce latency.

Higher reasoning effort increases exploration depth but also cost and latency. GPT-5.6 extends this to six named levels (see above).

Source: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide

## 2. Verbosity steering (GPT-5.x)

GPT-5 has a `verbosity` API parameter influencing final answer length (distinct from thinking length). Can be set globally or overridden with natural language instructions for specific contexts — e.g., "high verbosity for coding tools only."

For concise output, set low verbosity and reinforce with: "Lead with the answer. Supporting detail comes after."

Note: GPT-5.6 uses `text.verbosity` and is more concise by default — legacy brevity prompts may over-correct.

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
