# Prompting GPT-5.6 Sol (`gpt-5.6-sol`) through askcodex

You are about to send one request to `gpt-5.6-sol` with `askcodex ask`. Use it for hard reviews and analysis when you want a GPT-5.6 answer or a second opinion from a different generation than GPT-6. For new work with no reason to stay on 5.6, use [model-gpt-6-sol.md](model-gpt-6-sol.md). For the hardest problems, use [model-gpt-6-astra.md](model-gpt-6-astra.md).

## Context you must respect

- askcodex sends one text-only request to `/codex/responses`: no tools, files, browsing, memory, image input, or Codex base instructions. Everything the model needs goes in the prompt or `--instructions`.
- The catalog now calls this model "older", but it is the replacement Codex names for `gpt-5.5`, which retires 2026-10-14. Expect callers migrating from `gpt-5.5` to land here.
- The prompt Codex normally sends this model is not sent by askcodex. Nothing tells the model how long to write, how to format, or whether to rewrite code unless you say so.
- Security topics can trip real-time classifiers. On accounts with Daybreak Blue, the backend loosens this automatically. On other accounts, standard safeguards apply.

## Facts already verified (2026-09-27)

- Catalog (live, `client_version=0.157.1`): "Older coding model for complex work.". Efforts through askcodex: `none`, `low`, `medium`, `high`, `xhigh`, `max`. The catalog default is `low`; askcodex sends `medium` unless you pass `--effort`. `ultra` is rejected with HTTP 400, and `none` works (observed 2026-09-27). Context window 272,000 tokens (catalog max 872,000). Input: text and image, but `ask` sends text only. Minimal Codex client 0.144.0. A "Fast" tier exists, but askcodex sends no `service_tier`, and responses report `default` (observed 2026-09-27).
- Knowledge cutoff: Feb 16, 2026 ([4]).
- The backend applied `text.verbosity: "medium"` when askcodex omitted it (observed 2026-09-27). Codex asks for `low` (catalog `default_verbosity`).
- It leads its siblings on hard reasoning ([1]):
  - FrontierMath Tier 4: 83%, vs 68.3% for Terra and 58.5% for Luna.
  - SEC-Bench Pro: 71.2%, vs 57.7% and 48.9%.
  - On routine coding the gap is small: SWE-Bench Pro 64.6%, vs 63.4% for Terra.
- On Agents' Last Exam, Sol at `low` beat GPT-5.5 at `high` with the same harness ([5]).
- With leaner system prompts on internal coding-agent evals, OpenAI measured 10-15% higher scores and 41-66% fewer tokens ([2]).
- GPT-5.6 is more concise than GPT-5.5 by default ([2]).
- OpenAI describes GPT-6 Sol as having "stronger factual reliability and clearer communication than GPT-5.6 Sol" ([6]).
- Probe, `--effort none`: exact JSONL from a 3-line log in 4.1 s, with 128 input and 107 output tokens (observed 2026-09-27).
- Probe, `--effort medium`, a Python function with 2 planted bugs: it found both plus 3 real ones and closed the connection correctly in its fix. 36.8 s, 1,747 output tokens (observed 2026-09-27).
- Real-time cyber and biology classifiers can hold the stream for several seconds or block a request ([3]). Codex treats a `cyber_policy` failure as final ([7]). askcodex reports it as `stream_failed`, with the backend code only inside the message.

## Do this

1. Choose the effort:
   - Format conversion, classification, exact-schema extraction: `none`.
   - Short Q&A, explanation, focused rewrite: `low`.
   - Review or debugging of one pasted function or diff: `medium`.
   - Multi-component design or security review: `high`.
   - Move up one level only when a named issue stays unresolved after you fix the brief. Before raising effort, look for a missing success criterion or stop rule ([2]).
   - Use `xhigh`, and then `max`, only for the hardest quality-first problem. Keep `max` only if it wins on that same brief. OpenAI: "Reserve max for the hardest quality-first workloads" ([2]).
2. Write the brief. For the general brief shape, follow [prompting-text.md](prompting-text.md). Then:
   - Keep it lean. State each rule once and drop examples that do not change behavior ([2]).
   - Use ALWAYS, NEVER and must only for true invariants such as required fields or forbidden changes. For judgment calls, give a decision rule ([2]).
   - Name the layer of work. For "review", "diagnose" or "explain", say to report and not rewrite. For "fix", ask for the full corrected code. OpenAI scopes autonomy by these request types ([2]), and so does the prompt Codex sends this model: "Diagnose: determine the cause and explain it. Do not implement the fix unless the user asks" (Codex base instructions, 0.157.1).
   - Set length and format explicitly. Give the word or line budget and say what a short answer must keep, for example: "Lead with the conclusion. Include the evidence needed to support it, any material caveat, and the next action." ([2]). Codex normally tells it to "Use the minimum formatting appropriate" (Codex base instructions, 0.157.1). Without that prompt, name the shape you want: table, JSON or prose.
   - For edits, say what stays fixed: "Preserve the requested artifact, length, structure, genre, and factual claims first." ([2])
   - For grounded answers, say to cite only the supplied sources, label inference, and report missing evidence. Missing evidence is not a factual "no" ([2]).
   - Paste every fact dated after Feb 16, 2026 ([4]).
   - In a follow-up that pushes back, include the counter-evidence. Codex steers this model to answer objections "with concrete evidence and diligent reasoning rather than unsubstantiated deference" (Codex base instructions, 0.157.1).
3. Run it:
   ```sh
   mkdir -p /tmp/askcodex
   askcodex ask - --model gpt-5.6-sol --effort medium \
     --instructions "Review only: report defects, do not rewrite unrelated code. State each finding once." \
     --json < /tmp/askcodex/retry-review.txt > /tmp/askcodex/sol-retry-review.json
   jq -r .result.text /tmp/askcodex/sol-retry-review.json
   ```
   Example `retry-review.txt`:
   ```text
   Goal: decide whether this retry wrapper for payment captures is safe to merge.
   Context: [paste the diff, the capture client, and the caller]
   Success criteria: each finding names the line, the trigger, the impact, and a one-line fix.
   Output: numbered findings, highest impact first, then "Merge: yes/no" with one reason. An empty list is allowed.
   Stop rule: if the pasted code omits something you need, name the missing file instead of guessing.
   ```
4. Check the answer before you use it:
   - It rewrote code when you asked for review.
   - It stated facts after its cutoff that you did not supply.
   - Its fix does what its finding claims. Run the code yourself.
   - The answer ended as `stream_failed` with `cyber_policy` in the message. Do not present the partial stream as an answer.

## Rules

- Do not use it for bulk extraction or classification; use [model-gpt-5.6-luna.md](model-gpt-5.6-luna.md). Do not use it for long routine inputs where near-Sol quality is enough; use [model-gpt-5.6-terra.md](model-gpt-5.6-terra.md).
- Do not write "be concise" alone, and do not repeat the same rule in `--instructions` and the prompt ([2]).
- Do not set `max` as a default ([2]).
- Do not retry or reword a `cyber_policy` block to get around it. Report the block; if a narrower defensive version still meets the user's goal, propose it and run it only with their agreement, saying what changed.
- Do not compare this model with its siblings by `reasoning_tokens`. See Unverified.

## Report

Tell the user the model and effort used, where the answer was saved, and any limitation that affects it. Name a safety block or a truncated stream explicitly.

## Unverified

- [UNVERIFIED: whether `/codex/responses` accepts a single input above 272,000 tokens, up to the catalog max of 872,000. Not probed. The API model page lists 1,050,000 ([4]), but the catalog governs askcodex.]
- [UNVERIFIED: pro mode (`reasoning.mode: "pro"`) and the API alias `gpt-5.6` on this backend. askcodex cannot send the mode, and the alias is not in the catalog.]
- Conflict: the API defaults this model to `medium` effort ([3]); Codex defaults it to `low`.
- [UNVERIFIED: why the four GPT-5.6-family slugs each reported exactly 1,034 reasoning tokens on the same brief, although their answers differed (observed 2026-09-27).]
- Wall times come from single probes run 5 at a time. They are not benchmarks.

## Sources

[1]: https://openai.com/index/gpt-5-6/ "GPT-5.6: Frontier intelligence that scales with your ambition", published 2026-07-09
[2]: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6.md "Prompting guidance for GPT-5.6 Sol", accessed 2026-09-27
[3]: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.6.md "Using GPT-5.6", accessed 2026-09-27
[4]: https://developers.openai.com/api/docs/models/gpt-5.6-sol "GPT-5.6 Sol (model page)", accessed 2026-09-27
[5]: https://openai.com/index/builders-guide-to-gpt-5-6/ "The builder's guide to GPT-5.6", published 2026-08-13
[6]: https://learn.chatgpt.com/docs/models "Models (ChatGPT Work and Codex)", accessed 2026-09-27
[7]: https://github.com/openai/codex/blob/rust-v0.157.1/codex-rs/codex-api/src/sse/responses.rs "codex-api SSE handling (cyber_policy)", tag rust-v0.157.1, accessed 2026-09-27
