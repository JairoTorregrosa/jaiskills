# Prompting GPT-5.6 Terra (`gpt-5.6-terra`) through askcodex

You are about to send one request to `gpt-5.6-terra` with `askcodex ask`. Use it for routine coding, review, drafting, and summarizing or consolidating long pasted material at close to Sol quality. For hard math, security or novel reasoning, use [model-gpt-5.6-sol.md](model-gpt-5.6-sol.md) or [model-gpt-6.1-sol.md](model-gpt-6.1-sol.md). For short extraction and classification, use [model-gpt-5.6-luna.md](model-gpt-5.6-luna.md).

## Context you must respect

- askcodex sends one text-only request to `/codex/responses`: no tools, files, browsing, memory, image input, or Codex base instructions. Everything the model needs goes in the prompt or `--instructions`.
- Terra is the middle tier of GPT-5.6. The GPT-6 family has only Astra, Sol and Luna ([7]), so no GPT-6 model is a direct swap. OpenAI's own docs skill still says to "retain Terra for balanced work" when migrating to GPT-6 Astra ([8]).
- OpenAI publishes no Terra-specific prompting guide. Its GPT-5.6 guide covers "GPT-5.6 Sol or the GPT-5.6 family" ([2]), and Codex gives Terra the same base prompt as Sol, byte for byte (Codex base instructions, 0.157.1). Apply the Sol brief rules and the deltas below.

## Facts already verified (2026-09-27)

- Catalog (live, `client_version=0.157.1`): "Older balanced model for straightforward work.". Efforts through askcodex: `none`, `low`, `medium`, `high`, `xhigh`, `max`. The catalog default is `medium`; `ultra` is rejected with HTTP 400, and `none` works (observed 2026-09-27). Context window 272,000 tokens (catalog max 872,000). Input: text and image, but `ask` sends text only. Minimal Codex client 0.144.0. The "Fast" tier is not reachable: askcodex sends no `service_tier`. No retirement is announced.
- The API page describes it as balancing intelligence and cost, corresponding "to the mini model tier used in earlier GPT-5 families". Knowledge cutoff: Feb 16, 2026 ([3]).
- OpenAI calls Terra "a lower-cost model with performance competitive with GPT‑5.5" ([1]).
- Close to Sol on coding ([1]):
  - SWE-Bench Pro 63.4% (Sol 64.6%).
  - Terminal-Bench 2.1 87.4% (Sol 88.8%).
  - DeepSWE 69.6% (Sol 72.7%).
- Well behind Sol on harder tasks ([1]):
  - FrontierMath Tier 4: 68.3% vs 83%.
  - SEC-Bench Pro: 57.7% vs 71.2%.
  - OSWorld 2.0: 50.2% vs 62.6%.
  - ARC-AGI-3: 0.8% vs 7.78%.
- Strong on long inputs: 8-needle MRCR at 256K-512K tokens scores 89.6%, vs 91.5% for Sol and 41.3% for Luna ([1]).
- Codex's default model for memory consolidation is `gpt-5.6-terra`; memory extraction uses Luna ([5]).
- OpenAI's system card: "larger models tend to perform better than smaller models on factuality" ([6]).
- With more reasoning effort, Terra and Luna "can often perform similar to GPT‑5.4 and 5.5" ([4]).
- Probe, `--effort none`: exact JSONL from a 3-line log in 3.3 s (observed 2026-09-27).
- Probe, `--effort medium`, a Python function with 2 planted bugs: the same 5 findings as Sol, with a correct `finally: conn.close()` fix. 33.9 s, 1,745 output tokens (observed 2026-09-27).
- The backend applied `text.verbosity: "medium"` when askcodex omitted it (observed 2026-09-27). askcodex 0.3.0 sends Codex's `low` with `--verbosity low`, which shapes length but is no cap (see step 2 of [model-gpt-5.6-sol.md](model-gpt-5.6-sol.md)).

## Do this

1. Choose the effort:
   - Format conversion or classification: `none`.
   - Short Q&A: `low`.
   - Summaries of long pasted material, routine code review or explanation, drafting: `medium`.
   - Multi-step analysis: `high`.
   - For a bounded task that falls short, try `high` or `xhigh` before switching to Sol ([4]).
   - For hard math, security or novel reasoning, switch to Sol rather than reaching for `max`. The benchmark gap above is 13-15 points.
2. Write the brief. Follow [prompting-text.md](prompting-text.md) for the general shape and step 2 of [model-gpt-5.6-sol.md](model-gpt-5.6-sol.md) for the GPT-5.6 rules: lean brief, layer of work, explicit length and format. Then add:
   - Supply the facts the answer depends on. Do not rely on recall; smaller models are less factual ([6]).
   - For long inputs, paste the whole source and ask for conclusions tied to named sections. Terra holds up at 256K-512K where Luna does not ([1]), but keep the total under the 272,000-token window.
   - For summaries and consolidation, list what must survive: "Keep all required facts, decisions, caveats, and next steps. Trim introductions, repetition, generic reassurance, and optional background first." ([2])
3. Run it:
   ```sh
   mkdir -p /tmp/askcodex
   askcodex ask - --model gpt-5.6-terra --effort medium --json \
     < /tmp/askcodex/incident-notes.txt > /tmp/askcodex/terra-incident-summary.json
   jq -r .result.text /tmp/askcodex/terra-incident-summary.json
   ```
   Example `incident-notes.txt`:
   ```text
   Goal: one consolidated incident summary for the on-call handoff.
   Context: [paste the Slack export, the timeline doc, and the postmortem draft, with credentials,
   customer data, personal details and internal hostnames redacted]
   Keep: every decision with its owner, every ticket ID, open questions, and the current mitigation.
   Output: at most 25 lines: Status, Timeline (UTC), Decisions, Open questions. Cite the source section for each decision.
   Stop rule: if two sources conflict, list both with their sections instead of choosing.
   ```
4. Check the answer before you use it:
   - Items from the middle of a long input are missing.
   - A fact appears that no pasted source supports.
   - A math, proof or security conclusion. Verify it, or rerun on Sol.

## Rules

- Do not use it for the hardest reasoning or for security analysis where Sol scores 13-15 points higher ([1]).
- Do not hand it tiny classification jobs at `medium` or above. Use `none` or `low`, or Luna.
- Do not set `max` as a default ([2]).
- Do not compare it with Sol or Luna by `reasoning_tokens`. See Unverified.

## Report

Tell the user the model and effort used, where the answer was saved, and any limitation that affects it, such as a long input that was only partly covered.

## Unverified

- [UNVERIFIED: whether `/codex/responses` accepts a single input above 272,000 tokens, up to the catalog max of 872,000. The API page lists 1,050,000 ([3]); not probed.]
- [UNVERIFIED: how Terra's subscription quota cost compares with Sol's. API prices differ ($2 vs $4 per million input tokens ([3])), but the subscription meter is not documented.]
- [UNVERIFIED: why the four GPT-5.6-family slugs each reported exactly 1,034 reasoning tokens on the same brief, although their answers differed (observed 2026-09-27).]
- The Notion claim that agents built on GPT-5.5 "perform just as well on Terra for half the cost" is a customer quote in [1], not an OpenAI measurement.

## Sources

[1]: https://openai.com/index/gpt-5-6/ "GPT-5.6: Frontier intelligence that scales with your ambition", published 2026-07-09
[2]: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6.md "Prompting guidance for GPT-5.6 Sol", accessed 2026-09-27
[3]: https://developers.openai.com/api/docs/models/gpt-5.6-terra "GPT-5.6 Terra (model page)", accessed 2026-09-27
[4]: https://openai.com/index/builders-guide-to-gpt-5-6/ "The builder's guide to GPT-5.6", published 2026-08-13
[5]: https://github.com/openai/codex/blob/rust-v0.157.1/codex-rs/model-provider/src/provider.rs "model-provider default task models", tag rust-v0.157.1, accessed 2026-09-27
[6]: https://deploymentsafety.openai.com/gpt-5-6 "GPT-5.6 System Card (Hallucinations section)", accessed 2026-09-27
[7]: https://developers.openai.com/api/docs/guides/latest-model.md "Using GPT-6", accessed 2026-09-27
[8]: https://github.com/openai/codex/blob/rust-v0.157.1/codex-rs/skills/src/assets/samples/openai-docs/references/upgrading-to-gpt-6-astra.md "OpenAI Docs skill: upgrading-to-gpt-6-astra.md", tag rust-v0.157.1, accessed 2026-09-27
