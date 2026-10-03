# Prompting GPT-6-Sol (`gpt-6-sol`) through askcodex

You are about to send one request to `gpt-6-sol` with `askcodex ask`. Since 2026-10-02 the catalog calls it "Previous generation workhorse model.": for new work use [model-gpt-6.1-sol.md](model-gpt-6.1-sol.md), and send GPT-6 Sol only to reproduce or compare an earlier result. It was the GPT-6 workhorse for coding, reviews, debugging, drafting, and analysis of supplied material. For the hardest or most consequential work, use [model-gpt-6-astra.md](model-gpt-6-astra.md). For clear, repeatable extraction or transformation, use [model-gpt-6-luna.md](model-gpt-6-luna.md).

## Context you must respect

- askcodex sends one text-only request to `/codex/responses`: no tools, files, browsing, memory, image input, or Codex base instructions. Everything the model needs goes in the prompt or `--instructions`.
- Sol answers an underspecified ask with clarifying questions (observed 2026-09-27), and askcodex has no follow-up turn. Always include the proceed-on-assumptions line from step 2.
- Luna's API price is 1/20 of Sol's per token ([3]). On AutomationBench, Astra at `low` cost 3.9x as much per task as Sol at `xhigh` and scored lower ([3]). Subscription quota per model is not published; use these ratios as the relative guide.
- To reproduce a previous-generation result, use [model-gpt-5.6-sol.md](model-gpt-5.6-sol.md). The catalog now calls it "Older coding model for complex work." (observed 2026-09-27).

## Facts already verified (2026-09-27)

- Catalog (live, `client_version=0.157.1`): "Workhorse model for coding and everyday work." Efforts through askcodex: `none`, `low`, `medium`, `high`, `xhigh`, `max` (catalog default `low`; `ultra` is rejected with HTTP 400; `none` is accepted). Context window 272,000 tokens (catalog max 872,000). Input: text and image, but `ask` sends text only. Minimal Codex client version 0.155.0. Fast tier: "2x speed, increased usage". askcodex selects no tier, and responses report `service_tier: default` (observed 2026-09-27).
- askcodex always sends an effort (CLI default `medium`), so no default applies. The sources disagree: the catalog default is `low`, and Codex's starting preset is "Sol Light" ([4]); ChatGPT guidance says start Sol at `medium` ([4]); the API default is `medium` ([10]).
- Knowledge cutoff 2026-04-20 ([2]). No retirement announced ([4], [12]). On paid plans, Sol replaces `gpt-5.5` in Codex when GPT-5.5 retires on 2026-10-14 ([4]). The API page lists 1,050,000 context, 922,000 max input, and 128,000 max output ([2]), which differs from the catalog.
- OpenAI positions Sol for "ambiguous, difficult, or high-value tasks" and adds: "For narrower tasks, define what done looks like to keep the work focused." ([4]).
- Launch data ([3]):
  - Sol makes "about half as many mistakes as its predecessor" on OpenAI's factuality evaluation.
  - On AutomationBench, Sol at `xhigh` scored 33.2% against 30.3% for Astra at `low`.
  - On DeepSWE 1.1, Sol at `max` scored 68.8%.
  - Sol gives "slightly shorter answers overall" with "fewer low-value details" than GPT-5.6 Sol.
- Sol's factual gains are largest "at very low latency and reasoning settings" ([7]).
- Update 2026-10-02 (`client_version=0.160.0`): description "Previous generation workhorse model.", catalog default `medium`, Fast tier "1.5x speed", and Codex now sends it an 18,992-character prompt without the "can you..." follow-through paragraph; the two bullets below describe 0.157.1 (observed 2026-10-02).
- Codex sends Sol exactly the same 21,429-character system prompt as Astra (Codex base instructions, 0.157.1). OpenAI presents its Astra prompts as a starting point "across the GPT-6 model family" ([1]).
- Codex's GPT-5.6 prompt told the model "Do not implement the fix unless the user asks". GPT-6 Sol's prompt drops that rule and treats "can you..." as a request to do the work (Codex base instructions, 0.157.1). askcodex sends neither prompt.
- Guidance that helps Sol or Luna "may overconstrain GPT-6 Astra" ([11]). This implies that explicit steps suit Sol.
- Codex sends `text.verbosity: "low"` ([8]). askcodex sends it only with `--verbosity` (0.3.0); without it the backend applies `medium`, the API default ([9]; observed 2026-09-27).
- Probes (observed 2026-09-27, one sample each):
  - Exact-format JSONL at `low`: exact output in 3.6 s with 0 reasoning tokens.
  - Bare "Can you write a function that deduplicates customer records?" at `medium`: three clarifying questions and no code, 115 output tokens in 13.3 s.
  - The same ask plus the proceed line in `--instructions`: a complete function with 500 output tokens (184 reasoning) in 10.7 s.
  - Astra and Luna answered the bare ask directly.
- The API docs describe `reasoning.mode: "pro"` for GPT-6 ([10]). `/codex/responses` rejected it for `gpt-6-luna` with HTTP 400 (observed 2026-09-27).
- An image-encoding bug in Sol and Luna was fixed on 2026-09-25 ([6]). It does not affect text-only `ask` calls.

## Do this

1. Choose the effort. Move up one level when a named issue remains.
   - `none`: classification or formatting that needs no reasoning, where latency matters ([10]).
   - `low`: focused writing and editing, fact-checking, short Q&A ([5]).
   - `medium`: everyday coding, and analysis that needs judgment and completeness ([4], [5]).
   - `high`: complex debugging and deep planning ([10]).
   - `xhigh`: deeper analysis, thorough verification, and careful review of documents, data, and code ([5]).
   - `max`: the hardest single problem, where depth matters more than time ([4]). If it still fails, switch to Astra instead of repeating.
2. Write the brief. For the general brief shape, follow [prompting-text.md](prompting-text.md). Then add these Sol-specific parts:
   - Put this line in `--instructions`: "If a detail is missing, choose a reasonable default, state it in one line, and deliver the complete result. Do not ask questions." (observed 2026-09-27). Always add the carve-out: "If code or a fact that the diagnosis, fix or conclusion depends on is missing, name it and withhold that part instead of guessing."
   - Say what done looks like, for example "the patch plus one regression test; no refactor" ([4]).
   - State the scope: diagnosis only, or diagnosis plus patch (Codex base instructions, 0.157.1).
   - Write out steps when the method matters; explicit guidance suits Sol ([11]).
   - Ask for exhaustive coverage explicitly when you need every item, because Sol trims low-value detail ([3]).
   - Match the verbosity of the result you reproduce: `--verbosity low` for a Codex result, because Codex sends `low` ([8]); no flag for an earlier askcodex result, which got the backend's `medium` ([9]). Keep hard length limits in the brief; verbosity is not a cap (observed 2026-10-02).
   - Supply facts newer than the 2026-04-20 cutoff ([2]).
   - For style excerpts, reuse the ones in [model-gpt-6-astra.md](model-gpt-6-astra.md) ([1]).
3. Run it:
   ```sh
   mkdir -p /tmp/askcodex
   cat > /tmp/askcodex/sol-brief.txt <<'EOF'
   Task: Find why test_refund_rounding fails and give a minimal fix.
   Context: [failing test output, refund.py, the diff of the last commit]
   Constraints: Keep the public function signatures. Python 3.12, no new dependencies.
   Output: The cause in two sentences, then a unified diff, then one test that fails
   before the fix and passes after it.
   Verification: Say which input from the test output your cause explains.
   EOF
   askcodex ask - --model gpt-6-sol --effort high \
     --instructions "If a detail is missing, choose a reasonable default, state it in one line, and deliver the complete result. Do not ask questions. If code or a fact that the diagnosis or fix depends on is missing, name it and withhold the diagnosis or patch instead of guessing." \
     --json < /tmp/askcodex/sol-brief.txt > /tmp/askcodex/sol-fix.json
   jq -r .result.text /tmp/askcodex/sol-fix.json
   ```
4. Check the answer for these failure modes before you use it: questions where the deliverable should be; a patch or diagnosis that relies on code you did not paste; a stated default that conflicts with your intent; a list you needed complete that was trimmed; work beyond the scope you defined as done.

## Rules

- Do not send a bare "Can you ..." ask without the proceed line.
- Do not send `--effort ultra`; it returns HTTP 400.
- Do not rerun `max` hoping for a different result; switch to Astra.
- Do not use Sol for bulk extraction or classification with a known schema; Luna costs 1/20 per token ([3]).

## Report

Tell the user the model and effort used, where the answer was saved, and any limitation that affects it.

## Unverified

- [UNVERIFIED: how often Sol asks instead of delivering, at other efforts and on other prompts — one probe at `medium`]
- [UNVERIFIED: which context limit `/codex/responses` enforces for one askcodex request — not probed]
- [UNVERIFIED: whether `reasoning.mode: "pro"` works for Sol — probed only on Luna]
- [UNVERIFIED: latency above `medium` — not measured]
- [UNVERIFIED: subscription quota cost per model — not published; API prices are only a proxy]

## Sources

[1]: https://developers.openai.com/api/docs/guides/latest-model "Using GPT-6", accessed 2026-09-27
[2]: https://developers.openai.com/api/docs/models/gpt-6-sol "GPT-6 Sol (model page)", accessed 2026-09-27
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
