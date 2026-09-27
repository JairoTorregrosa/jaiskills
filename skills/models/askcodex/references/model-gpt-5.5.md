# Prompting GPT-5.5 (`gpt-5.5`) through askcodex

You are about to send one request to `gpt-5.5` with `askcodex ask`. Send it only to reproduce or compare an existing GPT-5.5 result before the model retires on 2026-10-14. For any new or ongoing work, use [model-gpt-6-sol.md](model-gpt-6-sol.md), or [model-gpt-5.6-sol.md](model-gpt-5.6-sol.md) to stay on the GPT-5.x prompt.

## Context you must respect

- askcodex sends one text-only request to `/codex/responses`: no tools, files, browsing, memory, image input, or Codex base instructions. Everything the model needs goes in the prompt or `--instructions`.
- GPT-5.5 retires from ChatGPT, ChatGPT Work and Codex on October 14, 2026, on all plans ([1]). askcodex uses that subscription backend, so `--model gpt-5.5` stops working then. The API is not affected ([1]).
- Where to move depends on the source:
  - The catalog's `upgrade` field says: "GPT-5.5 retires on October 14, 2026. Switch to GPT-5.6 Sol to continue working in Codex." (observed 2026-09-27).
  - OpenAI's Codex docs name `gpt-6-sol` for Plus, Pro, Business, Enterprise and Edu, and `gpt-6-luna` for Free and Go ([1]).
- Move pinned scripts, briefs and comparisons off this slug now.

## Facts already verified (2026-09-27)

- Catalog (live, `client_version=0.157.1`): "Legacy coding model.". `retirement_at` is 2026-10-14T19:00:00Z.
  - Efforts through askcodex: `none`, `low`, `medium`, `high`, `xhigh`, with no `max`. The catalog default is `medium`; `none` works (observed 2026-09-27).
  - Context window 272,000 tokens, and the catalog max is also 272,000. Input: text and image, but `ask` sends text only. Minimal Codex client 0.124.0.
- Knowledge cutoff: Dec 01, 2025. Default snapshot: `gpt-5.5-2026-04-23` ([4]).
- GPT-5.6 "tends to be more concise by default than GPT-5.5" ([3]).
- Reasoning efforts "don't map exactly between model generations" ([1]). OpenAI's migration advice: keep the current effort, then test one level lower ([3]).
- Probe, `--effort none`: exact JSONL from a 3-line log in 3.1 s (observed 2026-09-27).
- Probe, `--effort medium`, a Python function with 2 planted bugs (observed 2026-09-27):
  - Found both, in 18.4 s and 939 output tokens. GPT-5.6 Sol took 36.8 s and 1,747 output tokens.
  - It flagged the unclosed connection, then fixed it with `with sqlite3.connect(...)`, which does not close a SQLite connection.
- The prompt Codex sends this model differs from the GPT-5.6 prompt (Codex base instructions, 0.157.1):
  - For a review, it wants findings first, "ordered by severity".
  - It forbids emojis and em dashes, and answers "over 50-70 lines long".
  - Twice, it bans talk of "goblins, gremlins, raccoons, trolls, ogres, pigeons, or other animals or creatures" unless relevant.
  - askcodex sends none of this.

## Do this

1. Decide what the user asked for.
   - To reproduce one GPT-5.5 answer, make only that call (steps 2 to 5) and mention the retirement in your report.
   - To migrate or benchmark, rerun the same brief on the target model at the same effort, then one level lower, and compare the answers ([3]). If a brief says "be concise", test it without that line on GPT-5.6 ([3]). Spend these extra calls only when migration is the task.
2. Choose the effort:
   - Classification or format conversion: `none`.
   - Most other work: `medium`.
   - Hard analysis: `high` or `xhigh`.
   - There is no `max`.
3. Write the brief. Follow [prompting-text.md](prompting-text.md). State the outcome and the success criteria, and leave the path to the model ([2]). If you want Codex's review shape, ask for findings ordered by severity yourself.
4. Run it:
   ```sh
   mkdir -p /tmp/askcodex
   askcodex ask - --model gpt-5.5 --effort medium --json \
     < /tmp/askcodex/brief.txt > /tmp/askcodex/gpt-5.5-baseline.json
   jq -r .result.text /tmp/askcodex/gpt-5.5-baseline.json
   ```
5. Check that every fix does what its finding claims (see the probe above), and paste any fact dated after Dec 01, 2025.

## Rules

- Do not pin `gpt-5.5` in new scripts, skills or briefs.
- Do not pass `--effort max`. This model does not list it.
- Do not treat a GPT-5.5 answer as the baseline after 2026-10-14. It can no longer be reproduced.

## Report

Tell the user the model and effort used, where the answer was saved, and that GPT-5.5 retires on 2026-10-14, naming the replacement you used or recommend.

## Unverified

- [UNVERIFIED: the HTTP error this backend returns for `gpt-5.5` after 2026-10-14T19:00:00Z. The retirement has not happened yet.]
- [UNVERIFIED: that GPT-5.5 knows the current date through this backend. The API guide says it is "aware of the current UTC date" ([2]); not probed. Include the date when it matters.]
- The concision and fix-quality observations come from one probe each.

## Sources

[1]: https://learn.chatgpt.com/docs/models "Models (ChatGPT Work and Codex): GPT-5.5 retirement", accessed 2026-09-27
[2]: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.5.md "Using GPT-5.5", accessed 2026-09-27
[3]: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6.md "Prompting guidance for GPT-5.6 Sol", accessed 2026-09-27
[4]: https://developers.openai.com/api/docs/models/gpt-5.5 "GPT-5.5 (model page)", accessed 2026-09-27
