---
title: Anthropic Claude Models — Prompt Engineering Reference
last_verified: 2026-07-16
lineup_verified: 2026-09-26
sources_verified: true
covers: Claude Fable 5.1, Claude Opus 5.5, Claude Sonnet 5, Claude Haiku 4.5 (lineup, effort, gotchas); per-model prompting guides for Claude Fable 5, Claude Mythos 5, Claude Opus 4.8, Claude Sonnet 5, Claude Haiku 4.5
---

> **Verification:** Sections marked "verified 2026-09-26" (lineup table, effort levels, the lineup-related migration gotchas) were re-fetched on 2026-09-26. Everything else was fetched and content-verified on 2026-07-16 and describes models up to Fable 5 / Opus 4.8 / Sonnet 5. Each section's Source line points to the page supporting its claims.
>
> **Current lineup (2026-09-26):** Claude Fable 5.1 (`claude-fable-5-1`), Claude Opus 5.5 (`claude-opus-5-5`), Claude Sonnet 5 (`claude-sonnet-5`), Claude Haiku 4.5 (`claude-haiku-4-5-20251001`). Anthropic's default starting point is Opus 5.5; Fable 5.1 is for demanding reasoning and long-horizon agentic work. This file has no dedicated prompting section for Fable 5.1 or Opus 5.5 yet: before targeting either, read https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1 or https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5 (SKILL.md workflow step 2), then use the Fable 5 / Opus 4.8 sections below as background.

# Claude Prompt Engineering Techniques

Sourced from Anthropic's official documentation and primary guides. Apply these techniques when generating prompts for any Claude model.

## 1. XML tag structuring

XML tags are the single highest-impact structuring method for Claude. Use descriptive, consistent tag names to separate instructions, context, examples, and variable inputs. Claude is trained to recognize XML tags as structural markers.

```xml
<instructions>Your task description here</instructions>
<context>Background information</context>
<examples>
  <example>
    <input>Sample input</input>
    <output>Expected output</output>
  </example>
</examples>
```

Best practices:
- Nest tags when content has natural hierarchy (`<documents><document index="1">...</document></documents>`).
- Use tags to wrap few-shot examples so Claude distinguishes them from instructions.
- For long documents, place them at the top of the prompt inside XML tags, with the query below.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

## 2. System prompt conventions

- Use the system prompt for role, behavioral constraints, and output format.
- Be explicit: "Claude responds well to clear, explicit instructions." Think of Claude as a brilliant new employee who lacks context on your norms.
- Give Claude a role in the system prompt: even a single sentence ("You are a helpful coding assistant specializing in Python") focuses behavior.
- Provide context/motivation behind instructions — explain *why*, not just *what*.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

## 3. Prefilling (models before Claude 4.6)

Prefilling (providing a partial assistant message for Claude to continue from) is no longer supported on the last assistant turn for Claude 4.6+ models. Migration paths:
- **Output format control:** Use Structured Outputs or direct instructions instead.
- **Eliminating preambles:** Use "Respond directly without preamble" in the system prompt.
- **Continuations:** Move continuation context to the user message.

For older models (pre-4.6), prefilling remains available and useful for steering format.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

## 4. Long-context tips

- Place long documents at the top of the prompt, above instructions and queries. Queries at the end improve response quality by up to 30%.
- Wrap each document in `<document index="N"><source>...</source><document_content>...</document_content></document>` tags.
- Ask Claude to quote relevant parts before answering — this grounds responses and reduces hallucination.
- Structure for prompt caching: static content first (system instructions, examples, tool definitions), variable content last. Caching can cut costs by 90% and latency by 85%.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

## 5. Extended thinking / adaptive thinking

- **Claude Fable 5.1, Opus 5.5, Fable 5 and Mythos 5:** Thinking is always on and adaptive — no budget parameter; `thinking: {type: "disabled"}` is rejected. Raw chain of thought is never returned. For readable reasoning, request `thinking: {type: "adaptive", display: "summarized"}`. (Fable 5.1 / Opus 5.5 part verified 2026-09-26: https://platform.claude.com/docs/en/build-with-claude/thinking)
- **Claude Opus 4.6–4.8 and Sonnet 4.6:** Use `thinking: {type: "adaptive"}` — Claude dynamically decides when and how much to think.
- Use `<thinking>` tags inside few-shot examples to show Claude the reasoning pattern; it will generalize.
- Prefer general instructions ("think thoroughly") over prescriptive step-by-step plans — the model's own reasoning often outperforms hand-written steps.
- Do NOT instruct Claude to reproduce its reasoning in the response text — this can trigger `reasoning_extraction` refusals on Fable 5.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

## 6. Claude Fable 5 specific techniques

Key behavioral shifts: effort-level control, stronger instruction following, longer turns, parallel subagents, and file-based memory as a stronger lever than on prior models. See the detailed [Claude Fable 5](#claude-fable-5) section below for full guidance, prompt templates, and per-behavior source links.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

## 7. Agentic / tool-use prompting

- Be explicit about taking action: "Change this function" not "Can you suggest changes?"
- To make Claude proactive by default: wrap instructions in `<default_to_action>` tags.
- To make Claude conservative: wrap in `<do_not_act_before_instructions>` tags.
- Optimize parallel tool calling: Claude runs independent tool calls in parallel by default. Boost with `<use_parallel_tool_calls>` instructions.
- After completing tool use, instruct Claude to summarize work done if visibility is needed.
- For long async agents, create a `send_to_user` tool for verbatim mid-task updates.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

## 8. Claude Code (CLAUDE.md / skills) specifics

- CLAUDE.md is the persistent instruction file for Claude Code — placed at repo root or `~/.claude/CLAUDE.md` for global instructions.
- Skills are reusable instruction packages with YAML frontmatter (`name`, `description` with trigger phrases) and imperative instruction body.
- In Claude Code prompts, omit what the harness already injects: tool definitions, git context, file tree. Focus on behavioral instructions, constraints, and workflow.
- Use progressive disclosure: concise SKILL.md with details in `references/` files.
- Claude Code supports slash commands via `commands/*.md` that invoke skills with `$ARGUMENTS`.

Source: https://code.claude.com/docs/en/skills

## 9. Output and formatting control

- Tell Claude what to do instead of what not to do: "Write in flowing prose paragraphs" rather than "Do not use markdown."
- Use XML format indicators: "Write in `<prose>` tags."
- Match prompt style to desired output style — removing markdown from the prompt reduces markdown in the output.
- Claude's latest models default to LaTeX for math; add explicit plain-text instructions if unwanted.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

## 10. Few-shot / multishot prompting

- Start with one example (one-shot). Add more only if output doesn't match.
- 3-5 examples for best results.
- Wrap in `<example>` / `<examples>` tags.
- Make examples relevant, diverse, and cover edge cases.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

---

# Current Claude Model Lineup and Selection

## Model comparison table (verified 2026-09-26)

If unsure, start with Opus 5.5. Use Fable 5.1 for demanding reasoning and long-horizon agentic work, or when evals on Opus 5.5 at higher effort still fall short.

| Feature | Claude Fable 5.1 | Claude Opus 5.5 | Claude Sonnet 5 | Claude Haiku 4.5 |
|---|---|---|---|---|
| **Model ID** | `claude-fable-5-1` | `claude-opus-5-5` | `claude-sonnet-5` | `claude-haiku-4-5-20251001` (alias `claude-haiku-4-5`) |
| **Pricing (input/output MTok)** | $10 / $50 | $4 / $20 | $2 / $10 | $1 / $5 |
| **Context window** | 1M tokens | 1M tokens | 1M tokens | 200k tokens |
| **Max output** | 128k tokens | 128k tokens | 128k tokens | 64k tokens |
| **Thinking** | Adaptive, always on (`disabled` returns 400) | Adaptive, always on (`disabled` returns 400 at every effort) | Adaptive, on by default (can disable) | Extended (`budget_tokens`) only |
| **Extended thinking (budget_tokens)** | Not accepted | Not accepted | Not accepted | Supported |
| **Effort parameter** | low / medium / high / xhigh / max | low / medium / high / xhigh / max | low / medium / high / xhigh / max | Not supported |
| **Effort default** | high | **medium** | high | N/A |
| **Sampling params (temperature, top_p, top_k)** | Non-default values return 400 | Non-default values return 400 | Non-default values return 400 | Accepted |
| **Prefilling** | Not possible (thinking always on) | Not possible (thinking always on) | Not supported (400 error) | Supported |
| **Forced `tool_choice` (`any` / `tool`)** | 400 error — use `auto` + strict tools or structured outputs | 400 error — use `auto` + strict tools or structured outputs | Supported | Supported only with thinking off (incompatible with extended thinking) |
| **Thinking display default** | omitted | omitted | omitted | N/A (extended thinking) |
| **Reliable knowledge cutoff** | Jun 2026 | Jun 2026 | Jan 2026 | Feb 2025 |
| **Best for** | Demanding reasoning, long-horizon agentic work | Long-running agentic coding and knowledge work (default choice) | Speed + intelligence balance | Fastest; classification, high-volume, subagents |

Claude Mythos 5.1 (`claude-mythos-5-1`) shares Fable 5.1's specifications and pricing and is invitation-only through Project Glasswing.

Legacy models, still available: Claude Fable 5, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Opus 4.5, Claude Sonnet 4.6, Claude Sonnet 4.5. Claude Mythos 5 is still active for Glasswing participants. Claude Opus 4.1 was retired on August 5, 2026.

Source: https://platform.claude.com/docs/en/about-claude/models/overview , https://platform.claude.com/docs/en/models/fable-5-1/overview , https://platform.claude.com/docs/en/models/opus-5-5/overview , https://platform.claude.com/docs/en/build-with-claude/thinking , https://platform.claude.com/docs/en/about-claude/model-deprecations

Mythos 5 background (verified 2026-07-16): Claude Mythos 5 (`claude-mythos-5`) shares Fable 5's specs and pricing and is invitation-only through Project Glasswing, a collaboration with the US government deploying Mythos-class models to cyberdefenders and infrastructure providers; it is the same underlying model as Fable 5 with certain safety safeguards lifted. Source: https://www.anthropic.com/news/claude-fable-5-mythos-5

---

# Per-Model Prompting Guides

## Claude Fable 5

> Legacy model (verified 2026-07-16). Claude Fable 5.1 (`claude-fable-5-1`) succeeded it on 2026-09-01 as Anthropic's most capable widely released model; the guidance below was written for Fable 5 and has not been re-checked against Fable 5.1.

Claude Fable 5 was Anthropic's most capable widely released model at the time of writing. It excels at long-horizon autonomy, first-shot correctness on complex problems, vision, enterprise workflows, code review, navigating ambiguity, and parallel delegation. The following behavioral differences from prior models require prompt or scaffolding updates.

### Adaptive thinking is always on

Thinking is always on and adaptive on Fable 5. You cannot pass `thinking: {type: "disabled"}` or `thinking: {type: "enabled", budget_tokens: N}` — both return a 400 error. The raw chain of thought is never returned. To get readable reasoning, set `thinking: {type: "adaptive", display: "summarized"}`. Without the explicit `display: "summarized"`, thinking blocks are returned with an empty `thinking` field (the default is `"omitted"`).

Use the `effort` parameter as the primary control for thinking depth. At `high` (default) and above, Fable 5 almost always thinks deeply. At `medium` and `low`, it may skip thinking for simpler problems. Lower effort on Fable 5 still performs well and often exceeds `xhigh` on prior models.

Source: https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking

### Longer turns

Individual requests on hard tasks can run for many minutes at higher effort settings. Autonomous runs can extend for hours. Adjust client timeouts, streaming, and user-facing progress indicators before migrating. Consider restructuring harnesses to check on runs asynchronously rather than blocking.

To prevent overplanning when a task is ambiguous, add to the system prompt:

> When you have enough information to act, act. Do not re-derive facts already established in the conversation, re-litigate a decision the user has already made, or narrate options you will not pursue in user-facing messages.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

### Brief instructions beat enumerated lists

Instruction-following is improved enough that a brief instruction replaces enumerating each behavior. A short brevity instruction is as effective as listing each verbosity pattern. Similarly, a concise checkpoint instruction replaces listing every case where the model should stop.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

### Ground progress claims

On long autonomous runs, instruct Fable 5 to audit progress against actual tool results. This nearly eliminates fabricated status reports:

> Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

### Action boundaries

Fable 5 can occasionally take unrequested actions (drafting an email when none was asked for, creating defensive git-branch backups). Define explicit constraints on what it should and should not do:

> When the user is describing a problem or asking a question rather than requesting a change, report your findings and stop. Don't apply a fix until they ask for one.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

### Parallel subagents

Fable 5 dispatches parallel subagents more readily than prior models. Provide explicit guidance about when delegation is appropriate, and prefer asynchronous communication between orchestrator and subagents over blocking.

> Delegate independent subtasks to subagents and keep working while they run. Intervene if a subagent goes off track or is missing relevant context.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

### File-based memory

Persistent file-based memory is a stronger lever on Fable 5 than on prior models. Fable 5 performs particularly well when it can record lessons from previous runs and reference them in later sessions. Provide a place to write notes (as simple as a Markdown file). To bootstrap a memory system from existing history, have Fable 5 review past sessions and extract core themes.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

### Reasoning extraction classifier fallback

Prompts, skills, or harness instructions that tell the model to echo, transcribe, or explain its internal reasoning as response text can trigger the `reasoning_extraction` refusal category on Fable 5, causing elevated fallbacks to Opus 4.8. Audit existing skills and system prompts for show-your-thinking instructions when migrating. If your application needs reasoning visibility, read the structured thinking blocks from adaptive thinking instead.

Source: https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback

### Safety classifier fallback routing

Fable 5 runs safety classifiers targeting offensive cybersecurity techniques, biology/life sciences content, competing AI model development (`frontier_llm`), and reasoning extraction. Benign work in these domains may also trigger refusals. When a classifier fires, the response returns `stop_reason: "refusal"` with a `stop_details.category` field.

To re-route declined requests automatically, use either server-side fallback (beta `fallbacks` parameter) or client-side SDK middleware. Both auto-retry on a fallback model like Opus 4.8:

```python
response = client.beta.messages.create(
    model="claude-fable-5",
    fallbacks=[{"model": "claude-opus-4-8"}],
    betas=["server-side-fallback-2026-06-01"],
    messages=[...]
)
```

Source: https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback

### Context-countdown avoidance

In very long sessions, Fable 5 can occasionally suggest a new session or offer to summarize. This is most often triggered when the harness shows a remaining-token countdown. Avoid surfacing explicit context-budget counts. If the harness must show them, add a reassurance:

> You have ample context remaining. Do not stop, summarize, or suggest a new session on account of context limits. Continue the work.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

---

## Claude Opus 4.8

> Legacy model (verified 2026-07-16). The Opus line has moved on to Claude Opus 5 and then Claude Opus 5.5 (`claude-opus-5-5`, released 2026-09-22), which is now the recommended default. The guidance below was written for Opus 4.8; Opus 5.5 differs at least in that thinking is always on and effort defaults to `medium`.

Claude Opus 4.8 was Anthropic's recommended model for complex agentic coding and enterprise work at the time of writing. It shares most behavioral patterns with Opus 4.7 but with improved bug-finding, vision, and memory.

### Opt-in adaptive thinking

On Opus 4.8, thinking is off by default. You must explicitly set `thinking: {type: "adaptive"}` to enable it. Manual `thinking: {type: "enabled", budget_tokens: N}` is rejected with a 400 error. Start with `xhigh` effort for coding and agentic use cases, and use a minimum of `high` for intelligence-sensitive work.

When adaptive thinking is enabled but the model thinks more often than needed (common with large system prompts), add:

> Thinking adds latency and should only be used when it will meaningfully improve answer quality — typically for problems that require multistep reasoning. When in doubt, respond directly.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8

### Reasoning over tools at low effort

Opus 4.8 tends to favor reasoning over tool calls. This produces better results in most cases, but increasing the effort setting is a useful lever to increase tool usage. `high` or `xhigh` effort settings show substantially more tool usage in agentic search and coding.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8

### Literalness

Opus 4.8 interprets prompts literally and explicitly, particularly at lower effort levels. It does not silently generalize an instruction from one item to another and does not infer requests you didn't make. If you need it to apply an instruction broadly, state the scope explicitly ("Apply this formatting to every section, not just the first one").

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8

### Design defaults (cream/serif/terracotta)

Opus 4.8 has a consistent default house style for frontend work: warm cream/off-white backgrounds (~`#F4F1EA`), serif display type (Georgia, Fraunces, Playfair), italic word-accents, and a terracotta/amber accent. This reads well for editorial or portfolio briefs but feels off for dashboards, dev tools, or enterprise apps.

Two approaches work reliably:
1. **Specify a concrete alternative** with explicit color palette, typography, and layout specs.
2. **Have the model propose options before building:** "Before building, propose 4 distinct visual directions tailored to this brief (bg hex / accent hex / typeface — one-line rationale). Ask the user to pick one."

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8

### Report-every-issue review pattern

Opus 4.8 has higher bug-finding recall and precision than prior models. However, when review prompts say "only report high-severity issues" or "be conservative," Opus 4.8 follows that instruction more faithfully — it may find more bugs but report fewer. For review harnesses, use:

> Report every issue you find, including ones you are uncertain about or consider low-severity. Do not filter for importance or confidence at this stage. Your goal here is coverage.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8

### Subagent spawning

Opus 4.8 spawns fewer subagents by default compared to Fable 5. This is steerable through prompting; give explicit guidance about when subagents are desirable.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8

---

## Claude Sonnet 5

Claude Sonnet 5 is the best combination of speed and intelligence. It has particular strengths in coding and agentic tasks and performs well on existing Sonnet 4.6 prompts with minimal tuning.

### Adaptive thinking on by default

Unlike Opus 4.8 where thinking is off by default, Sonnet 5 has adaptive thinking on by default. Requests without a `thinking` field run with adaptive thinking. To turn it off entirely, pass `thinking: {type: "disabled"}`. Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) returns a 400 error.

Because `max_tokens` is a hard limit on total output (thinking plus response text), revisit it for workloads that ran without thinking on Sonnet 4.6.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

### More agentic and self-verifying

Sonnet 5 is more agentic than Sonnet 4.6 by default and will reach for tools and run self-verification loops more readily. With thinking disabled, the model is less likely to reach for tools — if you rely on tool calls with thinking off, add an explicit nudge in the system prompt.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

### New tokenizer produces ~30% more tokens

Sonnet 5 uses the tokenizer introduced with Opus 4.7. The same text produces roughly 30% more tokens than models before Opus 4.7. This affects `usage` fields, context window capacity, and `max_tokens` limits. Limits tuned for Sonnet 4.6 may truncate equivalent output on Sonnet 5. Re-run token counting against the new model.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

### Computer use

Sonnet 5 supports the `computer_20251124` tool version. Computer use works across resolutions up to 2576px / 3.75MP. Internal testing shows 1080p provides a good balance of performance and cost; 720p or 1366x768 for cost-sensitive workloads.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

### Cross-model effort mapping

As a rough cross-model mapping when migrating: Sonnet 5 at `medium` is comparable in intelligence to Sonnet 4.6 at `high`, and Sonnet 5 at `high` is comparable to Sonnet 4.6 at `max`. When benchmarking, match by observed thinking length rather than effort name.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

### Sampling parameters not accepted

Setting `temperature`, `top_p`, or `top_k` to a non-default value returns a 400 error on Sonnet 5. Remove these parameters when migrating. Use system-prompt instructions to guide tone and variety instead.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

---

## Claude Haiku 4.5

Claude Haiku 4.5 is the fastest model with near-frontier intelligence, optimized for classification, high-volume pipelines, and cost-sensitive subagent tasks.

### Legacy extended thinking only

Haiku 4.5 uses manual extended thinking with `budget_tokens` (`thinking: {type: "enabled", budget_tokens: N}`). It does not support adaptive thinking or the effort parameter. It has a 200k context window and 64k max output.

### No effort parameter

The `effort` parameter is not supported on Haiku 4.5. To control thinking depth, use `budget_tokens` directly.

### Prefilling and sampling still available

Unlike the Claude 4.6+ models, Haiku 4.5 still supports prefilling on the last assistant turn and accepts non-default `temperature`, `top_p`, and `top_k` values.

### Best-for tier

Use Haiku 4.5 for:
- Classification and routing tasks
- High-volume batch processing
- Subagent workloads where speed matters most
- Budget-sensitive pipelines
- Tasks where near-frontier intelligence at the lowest cost is the priority

Source: https://platform.claude.com/docs/en/docs/about-claude/models/overview

---

# Effort Parameter Levels (verified 2026-09-26)

The effort parameter controls how many tokens Claude spends when responding, available on all current models except Haiku 4.5. Set it via `output_config: {effort: "level"}`. Setting effort to the model's default is identical to omitting it.

| Level | Description | Typical use case |
|---|---|---|
| `max` | Absolute maximum capability, no constraints on token spending | Deepest possible reasoning and most thorough analysis |
| `xhigh` | Extended capability for long-horizon work (Fable 5.1, Mythos 5.1, Fable 5, Mythos 5, Opus 5.5, Opus 5, Opus 4.8, Opus 4.7, Sonnet 5) | Long-running agentic and coding tasks (30+ minutes) |
| `high` | Default on every effort-capable model except Opus 5.5 | Complex reasoning, difficult coding, agentic tasks |
| `medium` | Balanced, moderate token savings. Default on Opus 5.5 | Cost-sensitive agentic work needing speed/cost/perf balance |
| `low` | Most efficient, significant token savings | Simple tasks, subagents, latency-sensitive workloads |

### Per-model effort recommendations

- **Fable 5.1:** Start with `high` (default). Step up to `xhigh` or `max` for the most capability-sensitive agentic and coding work; step down to `medium` or `low` for routine or latency-sensitive work once evals show quality holds. Supports per-message effort changes (beta), which preserve the prompt cache.
- **Opus 5.5:** Default is `medium`, one level below Opus 5 and earlier Opus models, so a request that omits `effort` runs lower than it did on Opus 5. Thinking is always on, so effort is the primary control for reasoning depth and cost. Run an effort sweep on your own evals instead of carrying settings over. Supports per-message effort changes (beta).
- **Fable 5:** Start with `high` (default). Use `xhigh` for capability-sensitive workloads. Lower levels still often exceed `xhigh` on prior models.
- **Opus 4.8:** Start with `xhigh` for coding/agentic. Use `high` minimum for intelligence-sensitive. Effort is likely more important for this model than for any prior Opus.
- **Sonnet 5:** Start with `high` (default). Use `xhigh` for hardest coding/agentic. Sonnet 5 at `medium` is comparable to Sonnet 4.6 at `high`.
- **Haiku 4.5:** Not supported — use `budget_tokens` instead.

At `high`, `xhigh`, and `max` effort, set a large `max_tokens` (start at 64k and tune) to leave room for thinking and tool calls.

Source: https://platform.claude.com/docs/en/build-with-claude/effort

---

# Migration Gotchas

## Prefill removal (Claude 4.6+)

Prefilling the last assistant message returns a 400 error on all models from Claude Opus 4.6 onward (including Fable 5, Opus 4.8, and Sonnet 5). Use structured outputs, system prompt instructions, or `output_config.format` instead.

Source: https://platform.claude.com/docs/en/about-claude/models/migration-guide

## Non-default temperature/top_p/top_k return 400

Setting `temperature`, `top_p`, or `top_k` to non-default values returns a 400 error on Claude Opus 4.7 and every later model (Opus 4.8, Opus 5, Opus 5.5, Sonnet 5, Fable 5, Fable 5.1). Remove these parameters entirely; use prompting to guide behavior. The Python SDK v1.0+ removes them, so passing them raises `TypeError`. (verified 2026-09-26)

Source: https://platform.claude.com/docs/en/about-claude/model-deprecations

## Thinking display defaults to "omitted"

On Fable 5.1, Fable 5, Opus 5.5, Opus 5, Opus 4.8, Opus 4.7, and Sonnet 5 (list verified 2026-09-26), thinking blocks default to `display: "omitted"` — the `thinking` field is empty unless you explicitly set `display: "summarized"`. This is a silent change from Opus 4.6 and Sonnet 4.6 where the default was `"summarized"`.

Source: https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking

## budget_tokens deprecation

Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) is rejected with a 400 error on Opus 4.7, Opus 4.8, Sonnet 5, Fable 5, and every later model (Opus 5, Opus 5.5, Fable 5.1; verified 2026-09-26). It is deprecated on Opus 4.6 and Sonnet 4.6 (still functional but will be removed). Use adaptive thinking with the effort parameter instead.

Source: https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking

## Opus 4.1 retired

Claude Opus 4.1 (`claude-opus-4-1-20250805`) was retired on August 5, 2026; requests to it fail. Anthropic's listed replacement is `claude-opus-4-8`; for new prompts target `claude-opus-5-5`. (verified 2026-09-26)

Source: https://platform.claude.com/docs/en/about-claude/model-deprecations

## 300k-output batch beta

On the Message Batches API, Claude Opus 5.5, Opus 5, Sonnet 5, Opus 4.8, Opus 4.7, Opus 4.6, and Sonnet 4.6 support up to 300k output tokens by using the `output-300k-2026-03-24` beta header. (verified 2026-09-26)

Source: https://platform.claude.com/docs/en/about-claude/models/overview

## Forced tool use rejected (Fable 5.1, Opus 5.5)

Claude Opus 5.5, Fable 5.1, and Mythos 5.1 reject `tool_choice: {"type": "any"}` and `{"type": "tool", ...}` on every request with a 400 error. Use `tool_choice: {"type": "auto"}` plus a prompt instruction naming the tool, strict tool use, or structured outputs. Do not generate prompts or harness configs that rely on forced tool calls for these models. (verified 2026-09-26)

Source: https://platform.claude.com/docs/en/build-with-claude/thinking

## New tokenizer (+30% tokens)

Claude Opus 4.7, Opus 4.8, Fable 5, and Sonnet 5 use a newer tokenizer. The same text produces roughly 30% more tokens compared to models before Opus 4.7. Re-run token counting; do not reuse counts from older models.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

## Adaptive thinking on by default (Sonnet 5)

Unlike Opus 4.8 where thinking is off by default, Sonnet 5 has adaptive thinking on by default. Requests without a `thinking` field incur thinking tokens. To disable, pass `thinking: {type: "disabled"}`.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

## Fable 5 data retention

Fable 5 and Mythos 5 require 30-day minimum data retention. They are not available under zero data retention (ZDR) arrangements. Organizations with ZDR must contact Anthropic to adjust configuration or use Opus 4.8 instead.

Source: https://platform.claude.com/docs/en/about-claude/models/migration-guide
