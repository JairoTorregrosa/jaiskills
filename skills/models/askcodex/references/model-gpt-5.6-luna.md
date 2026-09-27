# Prompting GPT-5.6 Luna (`gpt-5.6-luna`) through askcodex

You are about to send one request to `gpt-5.6-luna` with `askcodex ask`. Use it for one bounded job with a checkable answer: a label, a title, a field extraction, a format conversion, or a short snippet review. For long inputs, use [model-gpt-5.6-terra.md](model-gpt-5.6-terra.md). For hard reasoning, use [model-gpt-5.6-sol.md](model-gpt-5.6-sol.md) or [model-gpt-6-sol.md](model-gpt-6-sol.md). For the newer small model, use [model-gpt-6-luna.md](model-gpt-6-luna.md).

## Context you must respect

- askcodex sends one text-only request to `/codex/responses`: no tools, files, browsing, memory, image input, or Codex base instructions. Everything the model needs goes in the prompt or `--instructions`.
- Luna is the smallest GPT-5.6 tier. Its weak spots are long inputs and hard reasoning, not routine code.
- OpenAI publishes no Luna-specific prompting guide. Its GPT-5.6 guide covers the family ([2]), and Codex gives Luna the same base prompt as Sol (Codex base instructions, 0.157.1). Apply the Sol brief rules and the deltas below.

## Facts already verified (2026-09-27)

- Catalog (live, `client_version=0.157.1`): "Older fast and efficient model.". Efforts through askcodex: `none`, `low`, `medium`, `high`, `xhigh`, `max`. The catalog default is `medium`, and the catalog lists no `ultra` for this model; `none` works (observed 2026-09-27). Context window 272,000 tokens (catalog max 872,000). Input: text and image, but `ask` sends text only. Minimal Codex client 0.144.0. No retirement is announced.
- The API page places it in "the nano model tier used in earlier GPT-5 families", for "cost-sensitive, high-volume workloads". Knowledge cutoff: Feb 16, 2026 ([3]).
- OpenAI's migration map sends "classification, extraction, routing, high-volume, or strict-latency" work to Luna ([4]).
- Codex itself uses `gpt-5.6-luna` for these jobs ([5]):
  - Thread titles, at `low` effort.
  - The Guardian v2 scorer, described in the code as "One tool-less Luna classification request".
  - Memory extraction.
  - Approval review under API-key sign-in.
- Routine coding is close to the larger tiers ([1]): SWE-Bench Pro 62.7% (Sol 64.6%), Terminal-Bench 2.1 84.7%.
- Long inputs and hard reasoning fall off ([1]):
  - 8-needle MRCR at 256K-512K tokens: 41.3%, vs 89.6% for Terra.
  - GraphWalks BFS 1M: 51.2%.
  - FrontierMath Tier 4: 58.5%.
  - ExploitGym: 12.4%.
  - Big Finance Bench: 36%, vs 51% for Terra.
- At `xhigh`, Luna scored 84.04% on BrowseComp, against 84.36% for GPT-5.5 at `xhigh` ([6]). OpenAI: with more reasoning effort, Luna and Terra "can often perform similar to GPT‑5.4 and 5.5" ([6]).
- OpenAI's system card: "larger models tend to perform better than smaller models on factuality" ([7]).
- Probe, `--effort none`: exact JSONL from a 3-line log in 3.3 s, 107 output tokens (observed 2026-09-27).
- Probe, `--effort medium`, a Python function with 2 planted bugs: the same 5 findings as Sol, with a correct `finally: conn.close()` fix. 32.4 s against Sol's 36.8 s, 1,725 output tokens (observed 2026-09-27). Wall time was not clearly shorter than Sol's.

## Do this

1. Choose the effort:
   - Labels, titles, routing, format conversion: `none`.
   - Extraction into a given schema: `low`. Codex's own title call uses `low` ([5]).
   - Review of a short snippet, or a structured summary of a short text: `medium`, the catalog default.
   - When a bounded task falls short, raise to `high`, then `xhigh`, before you switch models ([6]).
   - When the input is large, or the task needs proofs, novel algorithms or security depth, switch to Terra or Sol instead of raising effort ([1]).
2. Write the brief. Follow [prompting-text.md](prompting-text.md) for the general shape and step 2 of [model-gpt-5.6-sol.md](model-gpt-5.6-sol.md) for the GPT-5.6 rules. Then add:
   - Give exactly one job with an answer you can check: a closed label set, an exact schema, or pass/fail criteria. This is the work OpenAI routes to Luna ([4]) and runs on Luna inside Codex ([5]).
   - Keep the input short. Split a large corpus into separate calls, and merge the results on Terra or in code. Long-input retrieval is Luna's weakest measured area ([1]).
   - Paste the facts the answer depends on, and ask it to answer only from them. Smaller models are less factual ([7]).
   - Name the exact output and nothing else, for example "Reply with the label only." A strict JSONL conversion came back exact at `none` (observed 2026-09-27).
3. Run it:
   ```sh
   mkdir -p /tmp/askcodex
   askcodex ask - --model gpt-5.6-luna --effort low \
     --instructions "Classify each input line. Labels: auth_failure, timeout, disk_full, other. Output JSON Lines {\"line\":n,\"label\":\"...\"} only." \
     --json < /tmp/askcodex/error-lines.txt > /tmp/askcodex/luna-labels.json
   jq -r .result.text /tmp/askcodex/luna-labels.json
   ```
   `error-lines.txt` holds the numbered log lines, pasted in full with secrets and personal data redacted.
4. Check the answer before you use it:
   - Labels outside the set, extra keys, dropped lines, or lines merged together. Count the lines against the input.
   - A fact that the input does not contain.
   - A confident conclusion on a hard reasoning or security question. Rerun that on Terra or Sol.

## Rules

- Do not give it inputs in the hundreds of thousands of tokens. Use Terra ([1]).
- Do not use it for math proofs, exploit analysis or finance modeling where it trails Terra by 10 or more points ([1]).
- Do not pick it for speed through askcodex without measuring. The probes showed no clear wall-time gain over Sol (observed 2026-09-27).
- Do not switch models silently after a weak answer. Report the result and name the next model you would try.

## Report

Tell the user the model and effort used, where the answer was saved, and any limitation that affects it, such as a split input or a count mismatch.

## Unverified

- [UNVERIFIED: Luna's usable context on this backend. The catalog says 272,000 tokens (max 872,000). The API model page says 1,050,000 ([3]), and OpenAI's migration guide says "Luna has a smaller 400K context" ([4]). The sources conflict, and none was probed.]
- [UNVERIFIED: how Luna's subscription quota cost compares with Sol's. API input price is $0.20 vs $4 per million tokens ([3]), but the subscription meter is not documented.]
- [UNVERIFIED: why the four GPT-5.6-family slugs each reported exactly 1,034 reasoning tokens on the same brief (observed 2026-09-27).]
- OpenAI's advice for the Luna tier to start at `high` effort is written for GPT-6 Luna, not for this model ([8]).

## Sources

[1]: https://openai.com/index/gpt-5-6/ "GPT-5.6: Frontier intelligence that scales with your ambition", published 2026-07-09
[2]: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6.md "Prompting guidance for GPT-5.6 Sol", accessed 2026-09-27
[3]: https://developers.openai.com/api/docs/models/gpt-5.6-luna "GPT-5.6 Luna (model page)", accessed 2026-09-27
[4]: https://developers.openai.com/api/docs/guides/upgrading-to-gpt-5p6-sol.md "Upgrading to GPT-5.6 Sol", accessed 2026-09-27
[5]: https://github.com/openai/codex/tree/rust-v0.157.1/codex-rs "openai/codex: model-provider/src/provider.rs, tui/src/app/thread_title.rs, ext/guardian-v2/src/async_scorer/sampler.rs", tag rust-v0.157.1, accessed 2026-09-27
[6]: https://openai.com/index/builders-guide-to-gpt-5-6/ "The builder's guide to GPT-5.6", published 2026-08-13
[7]: https://deploymentsafety.openai.com/gpt-5-6 "GPT-5.6 System Card (Hallucinations section)", accessed 2026-09-27
[8]: https://learn.chatgpt.com/docs/models "Models (ChatGPT Work and Codex)", accessed 2026-09-27
