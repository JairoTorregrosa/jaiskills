# Prompting GPT-6-Astra (`gpt-6-astra`) through askcodex

You are about to send one request to `gpt-6-astra` with `askcodex ask`. Astra is for the hardest single-shot deliverables: consequential reviews, difficult designs, and analysis with exacting requirements. For everyday coding and review, use [model-gpt-6.1-sol.md](model-gpt-6.1-sol.md). For extraction or format conversion with a known output shape, use [model-gpt-6-luna.md](model-gpt-6-luna.md).

## Context you must respect

- askcodex sends one text-only request to `/codex/responses`: no tools, files, browsing, memory, image input, or Codex base instructions. Everything the model needs goes in the prompt or `--instructions`.
- Astra is the costliest GPT-6 model. Its API list prices are 5x Sol's per token ([2], [9]). On AutomationBench, Sol at `xhigh` scored 33.2% against 30.3% for Astra at `low`, and Astra cost 3.9x as much per task ([9]). Subscription quota per model is not published; use API prices as the relative guide and send Sol-sized work to Sol.
- Astra refuses advanced cyber tasks such as proof-of-concept exploits, but it handles secure code review and patching ([3]). For authorized defensive work it refuses (vulnerability triage, malware analysis, detection engineering), use [model-gpt-daybreak-blue-latest.md](model-gpt-daybreak-blue-latest.md) ([13]).
- There is no follow-up turn. If the model answers with a clarifying question, the call ends without the deliverable.
- For images, use [model-gpt-image-2.md](model-gpt-image-2.md).

## Facts already verified (2026-09-27)

- Catalog (live, `client_version=0.157.1`): "Frontier intelligence for the most demanding work." Efforts through askcodex: `low`, `medium`, `high`, `xhigh`, `max` (catalog default `medium`; `ultra` is rejected with HTTP 400; `none` is rejected with HTTP 400 ([7])). Context window 272,000 tokens (catalog max 872,000). Input: text and image, but `ask` sends text only. Minimal Codex client version 0.153.0. Fast tier: "2x speed, increased usage". askcodex selects no tier, and responses report `service_tier: default` (observed 2026-09-27).
- askcodex always sends an effort (CLI default `medium`), so no catalog or product default applies. ChatGPT starts users on Astra "Light", which is `low` ([5]).
- Knowledge cutoff 2026-04-30 ([2]). No retirement announced ([5], [15]). The API page lists 1,050,000 context, 922,000 max input, and 128,000 max output ([2]), which differs from the catalog.
- OpenAI reports these Astra behaviors ([1]): it asks for clarification more often than earlier models; it follows longer instructions better but is more sensitive to instructions in context, so conflicting guidance can make it pause early; it favors lists, tables, and Markdown; and on small coding tasks it tests more broadly than needed.
- Astra "can be more tentative about how far to take a task". Boundary language written for older models: Astra "could take it too seriously and may stop work". Overly specific guidance "can now hinder results", and guidance that helps Sol or Luna "may overconstrain" Astra ([4]).
- Astra makes fewer factual errors than GPT-5.6 Sol, and the gain is largest at low reasoning settings ([8]).
- Codex sends Astra a 21,429-character system prompt, identical to Sol's. Permission and autonomy sections come first. A writing section follows with "Write in connected prose. Avoid section headings", a banned-phrase list, and a rule against "X, not Y" framing. askcodex sends none of it, and its tool, channel, and skill rules do not apply to a toolless call (Codex base instructions, 0.157.1).
- Codex sends `text.verbosity: "low"` ([10]). askcodex sends no `text` field, so the backend applies `medium`, the API default ([11]; observed 2026-09-27). With `low`, the same Astra answer fell from 629 to 556 output tokens and dropped its bullet list (observed 2026-09-27, one sample each).
- Probes (observed 2026-09-27, one sample each):
  - Exact-format JSONL at `low`: exact output in 5.0 s with 0 reasoning tokens, identical to Sol and Luna.
  - Bare "Can you write a function that deduplicates customer records?" at `medium`: a complete answer with stated assumptions in 24.0 s, 629 output tokens (112 reasoning), formatted with headings, bold text, and bullets.
- The API docs describe `reasoning.mode: "pro"` for GPT-6 ([14]). `/codex/responses` rejected it for `gpt-6-luna` with HTTP 400 (observed 2026-09-27).
- Conflict: the bundled Codex docs skill at 0.157.1 maps "faster/cheaper" to `gpt-5.6-luna` and "balanced" to `gpt-5.6-terra` ([12]). The live guide lists Astra, Sol, and Luna ([1]); the live guide wins.

## Do this

1. Choose the effort. Move up one level only when the answer shows a specific, named failure.
   - `low`: concise writing and adapting content while keeping facts and nuance ([6]); factual Q&A ([8]).
   - `medium`: an ambitious deliverable that needs broad context and a complete result ([6]).
   - `xhigh`: demanding analysis, or a complex deliverable with exacting requirements ([6]).
   - `max`: one hardest problem where depth matters more than time. "Most tasks do not need Max or Ultra" ([5]).
2. Write the brief. For the general brief shape, follow [prompting-text.md](prompting-text.md). Then add these Astra-specific parts:
   - Name the decisions that are yours and let Astra assume the rest: "If a detail is missing, choose a default, state it in one line, and finish." The probe proceeded without this line, but OpenAI reports Astra asks more often ([1]), so keep it. Carve out the facts the conclusion depends on: tell Astra to list those as missing evidence and withhold the conclusion instead of assuming them.
   - Define completion by listing every part of the deliverable ([4]).
   - Give goals, sources, templates, constraints, and checks; leave out step-by-step recipes ([4], [5]).
   - State format and length: "Plain paragraphs, no headings, at most 8 lines." For prose, paste OpenAI's excerpt: "Default to using clear, concise paragraphs, each developing one main idea" ([1]).
   - Name the tests you want ("at most 3 unit tests for the empty and duplicate cases") ([1]). Astra cannot run them.
   - To reproduce Codex's writing style, copy only the style lines of its prompt into `--instructions` (Codex base instructions, 0.157.1).
3. Run it:
   ```sh
   mkdir -p /tmp/askcodex
   cat > /tmp/askcodex/astra-brief.txt <<'EOF'
   Task: Decide go/no-go for this database migration before Friday's rollout.
   Context: [migration plan, schema diff, peak write rate, rollback script]
   Constraints: The rollout date and the 5-minute downtime budget are my decisions.
   If a fact the decision depends on is missing (peak write rate, rollback behavior, lock
   duration), do not assume it: answer "No decision" and list the missing evidence.
   For minor gaps, choose a default, state it in one line, and finish.
   Output: The decision in one sentence ("Go", "No-go" or "No decision"), then at most 5
   risks. For each risk give the trigger, impact, and mitigation. Plain paragraphs, no headings.
   Verification: Tie each risk to the line of the plan it comes from.
   EOF
   askcodex ask - --model gpt-6-astra --effort xhigh --json < /tmp/askcodex/astra-brief.txt > /tmp/askcodex/astra-review.json
   jq -r .result.text /tmp/askcodex/astra-review.json
   ```
4. Check the answer for these failure modes before you use it: a clarifying question where the deliverable should be; a first pass that stops short of the parts you listed; a decision that rests on an assumed fact instead of supplied evidence; assumptions stated at the top that contradict your context; Markdown structure you did not ask for; tests broader than you requested.

## Rules

- Do not send `--effort none` or `ultra`; both return HTTP 400.
- Do not reuse strong boundary language written for older models ("NEVER touch anything outside X without asking"). State the actual constraint ("Do not change the public API") ([4]).
- Do not let `--instructions` and the prompt disagree on format, length, or scope ([1]).
- Do not spend Astra on extraction, classification, or format conversion; Luna produced identical output in the probe (observed 2026-09-27).

## Report

Tell the user the model and effort used, where the answer was saved, and any limitation that affects it.

## Unverified

- [UNVERIFIED: which context limit `/codex/responses` enforces for one askcodex request — not probed]
- [UNVERIFIED: whether `reasoning.mode: "pro"` works for Astra — probed only on Luna]
- [UNVERIFIED: latency at `high`, `xhigh`, and `max` — not measured]
- [UNVERIFIED: how often Astra asks instead of delivering through askcodex — one probe]
- [UNVERIFIED: subscription quota cost per model — not published; API prices are only a proxy]

## Sources

[1]: https://developers.openai.com/api/docs/guides/latest-model "Using GPT-6", accessed 2026-09-27
[2]: https://developers.openai.com/api/docs/models/gpt-6-astra "GPT-6 Astra (model page)", accessed 2026-09-27
[3]: https://openai.com/index/gpt-6-astra/ "GPT-6 Astra: A new generation of intelligence", published 2026-09 (API release entry dated 2026-09-03 in [7])
[4]: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra "Rethinking skills and prompts for GPT-6 Astra", published 2026-09-11
[5]: https://learn.chatgpt.com/docs/models "Models", accessed 2026-09-27
[6]: https://learn.chatgpt.com/docs/model-selection "Model selection", accessed 2026-09-27
[7]: https://developers.openai.com/api/docs/changelog "Changelog", accessed 2026-09-27
[8]: https://deploymentsafety.openai.com/gpt-6-astra "GPT-6 Astra System Card", accessed 2026-09-27 (last updated 2026-09-22)
[9]: https://openai.com/index/introducing-gpt-6-sol-and-luna/ "Introducing GPT-6 Sol and Luna", published 2026-09-22
[10]: https://github.com/openai/codex/blob/rust-v0.157.1/codex-rs/core/src/client.rs "codex-rs/core/src/client.rs at rust-v0.157.1", published 2026-09-25
[11]: https://developers.openai.com/api/reference/resources/responses/methods/create "Create a response", accessed 2026-09-27
[12]: https://github.com/openai/codex/tree/rust-v0.157.1/codex-rs/skills/src/assets/samples/openai-docs/references "openai-docs skill references at rust-v0.157.1", published 2026-09-25
[13]: https://learn.chatgpt.com/docs/cyber-safety "Models and Trusted Access", accessed 2026-09-27
[14]: https://developers.openai.com/api/docs/guides/reasoning "Reasoning models", accessed 2026-09-27
[15]: https://developers.openai.com/api/docs/deprecations "Deprecations", accessed 2026-09-27
