# Prompting GPT-6-Luna (`gpt-6-luna`) through askcodex

You are about to send one request to `gpt-6-luna` with `askcodex ask`. Luna is the fastest and cheapest GPT-6 model, for clear, repeatable work whose correct output you can specify exactly: extraction, classification, transformation, and structured summaries. When the task is ambiguous or needs judgment, use [model-gpt-6-sol.md](model-gpt-6-sol.md). For the hardest work, use [model-gpt-6-astra.md](model-gpt-6-astra.md).

## Context you must respect

- askcodex sends one text-only request to `/codex/responses`: no tools, files, browsing, memory, image input, or Codex base instructions. Everything the model needs goes in the prompt or `--instructions`.
- Luna fills gaps in a loose brief with its own policy (observed 2026-09-27). Spell out every rule the output must follow.
- Luna's API price is 1/20 of Sol's per token ([3]), which makes it the default for many parallel or repeated calls. Subscription quota per model is not published; use API prices as the relative guide.
- To reproduce a previous-generation result, use [model-gpt-5.6-luna.md](model-gpt-5.6-luna.md).

## Facts already verified (2026-09-27)

- Catalog (live, `client_version=0.157.1`): "Fast and affordable model for easier tasks." Efforts through askcodex: `none`, `low`, `medium`, `high`, `xhigh`, `max` (catalog default `medium`). `ultra` is not in Luna's catalog ([4]), and the backend rejects it with HTTP 400. `none` is accepted. Context window 272,000 tokens (catalog max 872,000). Input: text and image, but `ask` sends text only. Minimal Codex client version 0.155.0. Fast tier: "1.5x speed". askcodex selects no tier, and responses report `service_tier: default` (observed 2026-09-27).
- askcodex always sends an effort (CLI default `medium`), so no default applies. The sources disagree: the catalog default is `medium`; ChatGPT guidance says start Luna at `high`, and Codex has a "Luna High" preset ([4]); the API default is `medium` ([10]).
- Knowledge cutoff 2026-05-18, the latest of the three GPT-6 models ([2]). No retirement announced ([4], [12]). Codex names Luna as the replacement for `gpt-5.4-mini` (retired 2026-08-31) and for `gpt-5.5` on Free and Go plans (retiring 2026-10-14) ([4]). The API page lists 1,050,000 context, 922,000 max input, and 128,000 max output ([2]), which differs from the catalog.
- OpenAI positions Luna for specific, high-volume tasks "when you know what a good result looks like", including summarization, extraction, and focused coding ([4]).
- Launch data ([3]): at higher effort, Luna matches GPT-5.6 Sol's factuality "at about a hundredth its cost". On DeepSWE 1.1, Luna at `max` scored 66.6%.
- Luna's factual gain over GPT-5.6 Luna is largest at low effort ([7]).
- OpenAI has no Luna-specific prompting guide. Its GPT-6 prompts address behavior observed with Astra, and OpenAI says to evaluate them with the chosen model ([1]). Guidance that helps Sol or Luna "may overconstrain GPT-6 Astra" ([11]). This implies that explicit steps suit Luna.
- Codex sends Luna its own system prompt, shorter than Astra's and Sol's (18,044 vs 21,429 characters). Its personality section comes first and describes "a simple, clear communicator". It tells Luna to "minimize cognitive load" and not to assume the reader "will decode or fill in missing steps".
- Luna's prompt omits Astra and Sol's "Write in connected prose. Avoid section headings" rule and the paragraph that treats "can you..." requests as instructions to act. It tells Luna "Do not add or run tests unless the user asks", while Astra and Sol are told to run appropriate tests. askcodex sends none of this (Codex base instructions, 0.157.1).
- Codex sends `text.verbosity: "low"` ([8]). askcodex sends no `text` field, so the backend applied `medium`, the API default ([9]; observed 2026-09-27).
- Probes (observed 2026-09-27, one sample each):
  - Exact-format JSONL at `low`: exact output in 3.6 s with 0 reasoning tokens.
  - "Reply with exactly: OK" at `low`: 1.5 s.
  - Bare "Can you write a function that deduplicates customer records?" at `medium`: 19.3 s and 557 output tokens (247 reasoning). Luna delivered code with stated assumptions but merged fields from later duplicates, a policy nobody asked for. Astra kept the first record in 24.0 s (112 reasoning). Sol, given a proceed line, finished in 10.7 s (184 reasoning).
- The API docs describe `reasoning.mode: "pro"` for GPT-6 ([10]). `/codex/responses` rejected it for Luna with HTTP 400: "`reasoning.mode` is not supported with this model." (observed 2026-09-27).
- An image-encoding bug in Sol and Luna was fixed on 2026-09-25 ([6]). It does not affect text-only `ask` calls.

## Do this

1. Choose the effort. Move up one level when a field or rule is missed.
   - `none`: classification or formatting that needs no reasoning, where latency matters ([10]).
   - `low`: fine-grained edits, well-scoped problems, and simple extraction ([5]).
   - `medium`: drafting from a clear brief, and coordinated updates to supplied work ([5]).
   - `high`: any task that needs some judgment ([4]), and fact-dependent answers ([3]).
   - `xhigh`: problems with clear constraints that require prioritizing ([5]).
   - `max`: the hardest well-specified coding problem ([3]). If it still fails, switch to Sol.
2. Write the brief. For the general brief shape, follow [prompting-text.md](prompting-text.md). Then add these Luna-specific parts:
   - Specify the output exactly: schema, key order, allowed values, null policy, and one example line ([4]; observed 2026-09-27).
   - State every policy the model would otherwise choose, such as keeping the first record or merging duplicates (observed 2026-09-27).
   - Write out the steps when order matters ([11]).
   - Name the tests you want, if any; otherwise expect none (Codex base instructions, 0.157.1).
   - For Codex-like style, paste Luna's own lines into `--instructions`: "a simple, clear communicator" and "minimize cognitive load" (Codex base instructions, 0.157.1).
   - Cap the length in the brief, because the backend uses `medium` verbosity ([8], [9]).
   - Supply facts newer than the 2026-05-18 cutoff ([2]).
3. Run it:
   ```sh
   mkdir -p /tmp/askcodex
   cat > /tmp/askcodex/luna-brief.txt <<'EOF'
   Convert each support ticket below to one JSON object per line with exactly these
   keys in this order: "id" (string), "product" (one of "app", "api", "billing", or
   null), "severity" (integer 1-3, 1 = outage, or null), "summary" (at most 12 words).
   Copy each ticket's id exactly as given, in input order. Use null for product or
   severity when the ticket does not state it; never guess.
   Output only the JSON lines: no code fence, no prose, no blank lines.
   Example: {"id":"T-17","product":"api","severity":2,"summary":"Webhook retries stop after first failure"}

   Tickets (each starts with its id, e.g. "T-17:"):
   [paste tickets]
   EOF
   askcodex ask - --model gpt-6-luna --effort low --json < /tmp/askcodex/luna-brief.txt > /tmp/askcodex/luna-tickets.json
   jq -j .result.text /tmp/askcodex/luna-tickets.json > /tmp/askcodex/luna-tickets.jsonl   # -j adds no newline
   IDS='["T-17","T-18","T-19"]'   # the ids of the tickets you pasted, in order
   jq -Rse --argjson ids "$IDS" 'rtrimstr("\n") | split("\n")
     | map(try fromjson catch null | .id?) == $ids and all(.[];
     (try fromjson catch null) as $o | ($o | type) == "object" and ($o |
       keys_unsorted == ["id","product","severity","summary"]
       and (.id | type == "string" and length > 0)
       and (.product == null or (.product | IN("app","api","billing")))
       and (.severity == null or (.severity | IN(1,2,3)))
       and (.summary | type == "string" and (split(" ") | map(select(length > 0)) | length) <= 12)))' \
     /tmp/askcodex/luna-tickets.jsonl
   ```
   The command checks structure only: exactly one JSON object per physical line, one line per
   pasted ticket with its id in order, and every key, enum, range and length rule. `false` means a
   missing, extra, blank, pretty-printed or merged line, an invented or reordered id, or a broken
   rule. `true` is not proof that the values are right: step 4 still compares each product,
   severity and summary with its ticket. Paste only tickets that carry an id; ask the user for
   missing ids first.
4. Check the answer for these failure modes before you use it, comparing each value with its source ticket (a sample for large batches, saying how many you checked): lines that do not parse or break the schema; fields, merges, or behaviors you did not ask for; guessed values where the source is silent and you asked for null.

## Rules

- Do not give Luna an ambiguous task; route it to Sol ([4]).
- Do not leave a policy decision to Luna; state it (observed 2026-09-27).
- Do not use `medium` or higher for latency-sensitive transforms; use `low` or `none`. Luna is not reliably faster at `medium` (observed 2026-09-27).
- Do not send `--effort ultra`; it returns HTTP 400.

## Report

Tell the user the model and effort used, where the answer was saved, and any limitation that affects it.

## Unverified

- [UNVERIFIED: which context limit `/codex/responses` enforces for one askcodex request — not probed]
- [UNVERIFIED: latency above `medium` — not measured]
- [UNVERIFIED: how often Luna invents a policy on loose briefs — one probe]
- [UNVERIFIED: subscription quota cost per model — not published; API prices are only a proxy]

## Sources

[1]: https://developers.openai.com/api/docs/guides/latest-model "Using GPT-6", accessed 2026-09-27
[2]: https://developers.openai.com/api/docs/models/gpt-6-luna "GPT-6 Luna (model page)", accessed 2026-09-27
[3]: https://openai.com/index/introducing-gpt-6-sol-and-luna/ "Introducing GPT-6 Sol and Luna", published 2026-09-22
[4]: https://learn.chatgpt.com/docs/models "Models", accessed 2026-09-27
[5]: https://learn.chatgpt.com/docs/model-selection "Model selection", accessed 2026-09-27
[6]: https://developers.openai.com/api/docs/changelog "Changelog", accessed 2026-09-27
[7]: https://deploymentsafety.openai.com/gpt-6-astra "GPT-6 Astra System Card (Sol and Luna appendix)", accessed 2026-09-27 (appendix added 2026-09-22)
[8]: https://github.com/openai/codex/blob/rust-v0.157.1/codex-rs/core/src/client.rs "codex-rs/core/src/client.rs at rust-v0.157.1", published 2026-09-25
[9]: https://developers.openai.com/api/reference/resources/responses/methods/create "Create a response", accessed 2026-09-27
[10]: https://developers.openai.com/api/docs/guides/reasoning "Reasoning models", accessed 2026-09-27
[11]: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra "Rethinking skills and prompts for GPT-6 Astra", published 2026-09-11
[12]: https://developers.openai.com/api/docs/deprecations "Deprecations", accessed 2026-09-27
