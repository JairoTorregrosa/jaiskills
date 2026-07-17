---
title: Anthropic Claude Models — Prompt Engineering Reference
last_verified: 2026-07-16
sources_verified: true
covers: Claude Fable 5, Claude Mythos 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, Claude Sonnet 4.6, Claude Haiku 4.5
---

> **Verification:** All URLs listed below were fetched and content-verified on 2026-07-16. Each section's Source line points to the specific page supporting that section's claims.

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

- **Claude Fable 5 and Mythos 5:** Thinking is always on and adaptive — no budget parameter. Raw chain of thought is never returned. For readable reasoning, request `thinking: {type: "adaptive", display: "summarized"}`.
- **Claude Opus 4.6–4.8 and Sonnet 4.6:** Use `thinking: {type: "adaptive"}` — Claude dynamically decides when and how much to think.
- Use `<thinking>` tags inside few-shot examples to show Claude the reasoning pattern; it will generalize.
- Prefer general instructions ("think thoroughly") over prescriptive step-by-step plans — the model's own reasoning often outperforms hand-written steps.
- Do NOT instruct Claude to reproduce its reasoning in the response text — this can trigger `reasoning_extraction` refusals on Fable 5.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

## 6. Claude Fable 5 specific techniques

- **Effort levels:** Use `effort` parameter as the primary control. `high` is the default for most tasks; `xhigh` for the most capability-sensitive workloads; `medium`/`low` for routine work. Lower effort on Fable 5 often exceeds `xhigh` on prior models.
- **Strong instruction following:** A brief instruction replaces enumerating each behavior. Example: a short brevity instruction is as effective as listing each verbosity pattern.
- **Longer turns:** Individual requests on hard tasks can run for many minutes. Adjust client timeouts and streaming, consider async checking.
- **Prevent overplanning:** "When you have enough information to act, act. Do not re-derive facts already established in the conversation."
- **Ground progress claims:** "Before reporting progress, audit each claim against a tool result from this session."
- **State boundaries explicitly:** Define what Claude should and should not do to prevent unrequested actions.
- **Parallel subagents:** Fable 5 dispatches subagents more readily. "Delegate independent subtasks to subagents and keep working while they run."
- **Memory systems:** Fable 5 performs well with a place to record and reference lessons from previous runs.

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
