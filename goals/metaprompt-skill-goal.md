---
slug: metaprompt-skill
created: 2026-07-16
status: met  # in-progress | met | exhausted
budget: 5
iterations_used: 2
judge: codex
---

# Goal: Standalone metaprompting skill (goal + model + harness → complete prompt)

## Desired End State

A new standalone plugin `metaprompt` exists in this marketplace repo at `plugins/metaprompt/`, registered in `.claude-plugin/marketplace.json`. Its skill takes three user inputs — (1) a short objective/goal, (2) a target model, (3) a target harness — and produces a complete, ready-to-use prompt engineered for that model+harness combination using the latest published metaprompting/prompt-engineering techniques for each model.

Concretely:

- `plugins/metaprompt/.claude-plugin/plugin.json` — valid plugin manifest.
- `plugins/metaprompt/skills/metaprompt/SKILL.md` — skill with valid frontmatter (`name`, `description` with trigger phrases), documenting the three inputs (goal, target model, harness) and the output (a complete prompt), plus the generation workflow.
- `plugins/metaprompt/commands/metaprompt.md` — slash command entry point.
- `plugins/metaprompt/skills/metaprompt/references/` — per-model technique reference files covering at minimum: Anthropic Claude models (Fable/Opus/Sonnet/Haiku) and OpenAI GPT-5.x/Codex models; optionally Gemini. Each reference file must contain REAL researched techniques (researched via web search during implementation, not invented) with source URLs, covering model-specific prompting guidance (e.g., Claude XML-tags/system-prompt conventions, GPT-5 verbosity/reasoning-effort steering, harness differences: Claude Code vs Codex CLI vs chat/API).
- The skill instructs a runtime freshness step: web-search for updated guidance when the target model is newer than the reference file's `last_verified` date.
- Marketplace `.claude-plugin/marketplace.json` includes the `metaprompt` plugin entry and remains valid JSON.

## Evidence

| # | Command | Expected | Last Result |
|---|---------|----------|-------------|
| 1 | `python3 -m json.tool plugins/metaprompt/.claude-plugin/plugin.json` | exits 0 | — |
| 2 | `python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && grep -q '"metaprompt"' .claude-plugin/marketplace.json` | exits 0 | — |
| 3 | `head -20 plugins/metaprompt/skills/metaprompt/SKILL.md \| grep -q '^name: metaprompt' && head -30 plugins/metaprompt/skills/metaprompt/SKILL.md \| grep -qi 'description'` | exits 0 | — |
| 4 | `grep -qiE 'target model' plugins/metaprompt/skills/metaprompt/SKILL.md && grep -qiE 'harness' plugins/metaprompt/skills/metaprompt/SKILL.md && grep -qiE 'complete prompt\|full prompt\|ready-to-use prompt' plugins/metaprompt/skills/metaprompt/SKILL.md` | exits 0 | — |
| 5 | `ls plugins/metaprompt/skills/metaprompt/references/*.md \| wc -l` | >= 2 | — |
| 6 | `grep -rliE 'claude\|anthropic' plugins/metaprompt/skills/metaprompt/references/ \| head -1 && grep -rliE 'gpt-5\|codex\|openai' plugins/metaprompt/skills/metaprompt/references/ \| head -1` | both non-empty (exits 0) | — |
| 7 | `grep -rhoE 'https?://[^ )>"]+' plugins/metaprompt/skills/metaprompt/references/ \| sort -u \| wc -l` | >= 5 distinct source URLs | — |
| 8 | `test -f plugins/metaprompt/commands/metaprompt.md` | exits 0 | — |
| 9 | `grep -rqi 'last_verified' plugins/metaprompt/skills/metaprompt/references/ && grep -qiE 'web.?search\|freshness\|newer than' plugins/metaprompt/skills/metaprompt/SKILL.md` | exits 0 | — |

## Constraints

- Do NOT modify anything under `plugins/insistir/` (there are uncommitted changes there — leave them untouched).
- Do NOT commit — leave changes in the working tree.
- Reference techniques must come from real, current sources found via web search (Anthropic docs, OpenAI docs/cookbook, reputable 2025–2026 posts) — no fabricated citations or made-up URLs.
- All skill/reference content written in English.
- `.claude-plugin/marketplace.json` must remain valid JSON; only ADD the new plugin entry, don't alter the existing `insistir` entry.

## Iteration Log

### Iteration 1

- **Attempt summary:** Fresh implementer researched Anthropic/OpenAI prompting guides (6 primary sources), created plugin.json, commands/metaprompt.md, SKILL.md, references/claude-models.md (10 sections, 8 URLs), references/openai-models.md (12 sections, 7 URLs), added metaprompt entry to marketplace.json.
- **Evidence results:** all 9 commands PASS (verified by orchestrator).
- **Judge verdict:** NOT MET (Codex GPT-5)
- **Judge reason (verbatim):** insistir marketplace entry changed 0.1.0→0.3.0 (NOTE: orchestrator verified this modification pre-existed the session — false positive, judge diffed against HEAD not pre-session working tree); reference files show "fabricated freshness" signals — claims about Claude Fable 5 / Mythos 5 / Opus 4.7-4.8 / Sonnet 5 attributed to a purported `prompting-claude-fable-5` page without claim-level support; broad sections reuse a single generic URL for many precise assertions.
- **Carry-forward for iteration 2:** (a) verify every cited URL actually resolves by fetching it, remove/replace dead ones; (b) add claim-level inline citations per section; (c) do not touch marketplace.json insistir entry (pre-existing modification, leave as-is).

### Iteration 2

- **Attempt summary:** Fresh implementer fetched all 8 cited URLs (all HTTP 200; two redirects replaced with canonical targets: code.claude.com/docs/en/skills, learn.chatgpt.com/docs/agent-configuration/agents-md); restructured references to claim-level `Source:` lines per section; rewrote openai-models.md §6 ("Metaprompting with GPT-5" → "Prompt optimization") removing the unverified "GPT-5 can optimize its own prompts" claim; added `sources_verified: true` + verification notes; no insistir files touched.
- **Evidence results:** all 9 commands PASS (re-verified by orchestrator; 8 distinct URLs).
- **Judge verdict:** MET (Codex GPT-5)
- **Judge reason (verbatim, abridged):** "The goal is genuinely met. The plugin is standalone and structurally complete... SKILL.md explicitly collects goal/model/harness, asks rather than silently defaulting required inputs, maps model families, performs a runtime freshness search for uncovered or newer models... assembles a full paste-ready prompt, and self-reviews it... Both reference files are substantial rather than keyword-stuffed... official-source URLs directly under every numbered claim section... No new commit is present."
