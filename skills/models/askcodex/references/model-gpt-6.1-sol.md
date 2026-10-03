# Prompting GPT-6.1-Sol (`gpt-6.1-sol`) through askcodex

You are about to send one request to `gpt-6.1-sol` with `askcodex ask`. GPT-6.1 Sol is the current workhorse: coding, reviews, debugging, drafting, analysis of supplied material, and complex work where Astra's cost is not justified. OpenAI positions it as "near-Astra performance for complex work at a lower cost" ([2]). For the hardest or most consequential deliverable, use [model-gpt-6-astra.md](model-gpt-6-astra.md). For clear, repeatable extraction or transformation, use [model-gpt-6-luna.md](model-gpt-6-luna.md). To reproduce an earlier GPT-6 Sol result, use [model-gpt-6-sol.md](model-gpt-6-sol.md).

## Context you must respect

- askcodex sends one text-only request to `/codex/responses`: no tools, files, browsing, memory, image input, or Codex base instructions. Everything the model needs goes in the prompt or `--instructions`.
- askcodex 0.2.0 and later default `ask` to `gpt-6.1-sol` and report Codex client 0.160.0. The catalog lists this model only from `client_version` 0.159.0, although its minimum is 0.153.0, so an older askcodex does not show it in `models`; `ask --model gpt-6.1-sol` still works there (observed 2026-10-02). Pin `--model` when you compare outputs.
- Like GPT-6 Sol, it answers an underspecified ask with clarifying questions, and askcodex has no follow-up turn (observed 2026-10-02). Always include the proceed line from step 2.
- Cost: API prices are $2 input, $0.10 cached input, and $10 output per 1M tokens. Astra's input and output cost 5x as much, and Luna's cost 1/20 as much ([1]). Codex credit rates match GPT-6 Sol for input and output (50 and 250 credits per 1M tokens) and halve cached input (2.5 against 5). Astra costs 250 and 1,250 credits, Luna 2.5 and 12.5 ([7]). OpenAI's Plus estimate is 15–160 local messages per five hours, against 15–150 for GPT-6 Sol, 5–45 for Astra and 350–3,000 for Luna ([7]).
- OpenAI treats it as Critical in cybersecurity and gives it Astra's safeguard stack ([5]). Its catalog access programs are `standard` only; `gpt-6-sol` also lists `daybreak_blue` (observed 2026-10-02). For authorized defensive security work, use [model-gpt-daybreak-blue-latest.md](model-gpt-daybreak-blue-latest.md).

## Facts already verified (2026-10-02)

- Catalog (live, `client_version=0.160.0`): "Latest workhorse model for coding and everyday work." Priority 1, ahead of `gpt-6-astra`. Efforts through askcodex: `low`, `medium`, `high`, `xhigh`, `max` (catalog default `low`). `ultra` is Codex's multi-agent mode and returns HTTP 400. Context window 272,000 tokens (catalog max 872,000). Input: text and image, but `ask` sends text only. Fast tier: "2x speed, increased usage"; askcodex selects no tier. The catalog's prompt to Codex users: "Try it on complex work for near-Astra performance at a lower cost." (observed 2026-10-02).
- `--effort none` returns HTTP 400: "'none' is not supported with the 'gpt-6.1-sol' model" (observed 2026-10-02). GPT-6 Sol accepts `none`; the docs say to use `low` instead ([4]).
- `gpt-6-sol` is now "Previous generation workhorse model.", with catalog default `medium`. The `gpt-5.5` upgrade target is now `gpt-6.1-sol` (observed 2026-10-02). Conflict: OpenAI's GPT-5.5 retirement section still names `gpt-6-sol` ([3]). The live catalog wins.
- API model page: knowledge cutoff 2026-04-30 (GPT-6 Sol: 2026-04-20 ([9])). Context 1,050,000 tokens, max output 128,000, efforts `low` to `max` with `medium` as the default ([2]). These limits differ from the catalog. Launched 2026-09-29 ([1], [8]).
- Plans: the catalog lists every plan, including `free` and `go` (observed 2026-10-02). OpenAI says "Free and Go are not included at launch". Enterprise and Edu keep it off until an administrator enables it ([3], [7]).
- Launch data ([1]):
  - On DeepSWE v1.1 it matches Astra at about one-fifth of the cost. It also beats GPT-6 Sol's best score by 6.4 points "at a lower reasoning effort and cost".
  - On AutomationBench at `medium`, it scores 4.8 points above GPT-6 Sol at the same setting.
  - Its factual-error share fell from 11.4% to 7.7% at low effort, the largest gain over GPT-6 Sol. Across settings it stays within 1.9 points of Astra.
  - Astra still leads Terminal-Bench Science (68.1%), and OpenAI says to use Astra "for the most difficult scientific research tasks".
- Conflict: the system card finds that GPT-6.1 Sol and GPT-6 Sol "achieve similarly low hallucination rates" on user-flagged cases ([5]). Verify facts either way.
- ChatGPT guidance: "Reasoning efforts don't map exactly between model generations. Try a familiar task at a lower setting and adjust based on the result." ([3]). askcodex always sends an effort (CLI default `medium`), so no catalog or API default applies.
- Codex base instructions, 0.160.0: Codex sends this model a 21,769-character prompt. It is Astra's 21,420-character prompt plus one paragraph against "unnecessary apologies and self-blame". Compared with GPT-6 Sol's 18,992-character prompt, it adds:
  - OpenAI's follow-through paragraph ([4]): treat "can you..." as a request to do the work and "Do not stop at acknowledging capability (e.g. "Yes…")".
  - Astra's writing section: "Write in connected prose. Avoid section headings", main point first, and paragraphs over lists.
  - It drops GPT-6 Sol's rule that a user's correction means "fix the issue".
  - askcodex sends none of this. The tool, channel, approval and skill rules do not apply to a toolless call.
- Codex sends `text.verbosity: "low"`, the catalog `default_verbosity`. askcodex sends it only with `--verbosity` (0.3.0); without it the backend answers at `medium`. The same prompt returned 240 output tokens at `low` and 513 at `high` (observed 2026-10-02).
- Probes (observed 2026-10-02, one sample each, wall time including CLI startup; GPT-6 Sol figures are from [model-gpt-6-sol.md](model-gpt-6-sol.md), 2026-09-27):
  - Bare "Can you write a function that deduplicates customer records?" at `medium`: the answer opened with "Yes.", then asked three questions and gave no code. 315 output tokens (211 reasoning) in 17.0 s. GPT-6 Sol also asked three questions.
  - The same ask with the proceed line in `--instructions`: a one-line default, then a complete Python function with an example. 557 output tokens (137 reasoning) in 20.7 s, with a `###` heading and bold text nobody asked for.
  - The same again with `--verbosity low` (askcodex 0.3.0): no heading and no bold text, 391 visible answer tokens against 420 at `medium`. Reasoning rose to 235 tokens, so total output was 626, in 24.6 s.
  - Exact-format JSONL from a 3-line log at `low` (prompt rebuilt; the 2026-09-27 text was not saved): exact output, 0 reasoning tokens, 96 output tokens, 7.1 s.
- Conflict: the Codex docs skill bundled at 0.160.0 does not mention GPT-6.1 Sol, and the 0.159.0 and 0.160.0 release notes do not mention it either ([10]). The live guide lists it ([4]); the live guide wins.

## Do this

1. Choose the effort. If you know a task from GPT-6 Sol, start one level lower ([1], [3]). Move up one level when a named issue remains.
   - `low`: well-scoped tasks ([3]), exact-format conversion (observed 2026-10-02), and factual Q&A, where its factual gain is largest ([1]).
   - `medium`: "Complex technical work and coordinated deliverables you expect to revise" ([6]). Use it for everyday coding and review.
   - `high`: "difficult work with multiple steps, sources, or tradeoffs" ([3]), such as complex debugging.
   - `xhigh`: "Polished deliverables, connected visual systems, and decisions built from conflicting evidence" ([6]).
   - `max`: the hardest single problem, where depth matters more than speed ([3]). If it still fails, switch to Astra instead of repeating ([1]).
2. Write the brief. For the general brief shape, follow [prompting-text.md](prompting-text.md). Then add these parts for 6.1 Sol:
   - Put this line in `--instructions`: "If a detail is missing, choose a reasonable default, state it in one line, and deliver the complete result. Do not ask questions." (observed 2026-10-02). Always add the carve-out: "If code or a fact that the diagnosis, fix or conclusion depends on is missing, name it and withhold that part instead of guessing." OpenAI's longer version of the proceed line is the follow-through paragraph that Codex adds for this model ([4]; Codex base instructions, 0.160.0).
   - Say what done looks like and state the scope: diagnosis only, or diagnosis plus patch.
   - Pass `--verbosity low`: at the default `medium` it added a heading and bold text, at `low` neither (observed 2026-10-02, one sample each). Still state the format and any hard length limit, for example "Plain paragraphs, no headings, at most 10 lines."; verbosity is not a cap. For prose, paste OpenAI's excerpt: "Default to using clear, concise paragraphs, each developing one main idea" ([4]).
   - When a script will parse the answer, pass `--schema FILE` and read `.result.json`. The worked schema is in [model-gpt-6-luna.md](model-gpt-6-luna.md); it was verified live on the Luna models only (observed 2026-10-02).
   - Supply any fact newer than the 2026-04-30 cutoff ([2]).
3. Run it:
   ```sh
   mkdir -p /tmp/askcodex
   cat > /tmp/askcodex/sol61-brief.txt <<'EOF'
   Task: Review this diff for defects before it merges.
   Context: [the diff, the functions it calls, the intended behavior; secrets replaced by placeholders]
   Constraints: Report defects only: no style, naming or refactor comments.
   Output: At most 6 findings, highest impact first. For each, give the location, the input or
   sequence that triggers it, what the user sees, and a minimal fix. Plain paragraphs, no headings.
   If you find no defect, say so in one line.
   Verification: Quote the diff line each finding comes from.
   EOF
   askcodex ask - --model gpt-6.1-sol --effort medium --verbosity low \
     --instructions "If a detail is missing, choose a reasonable default, state it in one line, and deliver the complete result. Do not ask questions. If code or a fact that a finding or fix depends on is missing, name it and withhold that finding instead of guessing." \
     --json < /tmp/askcodex/sol61-brief.txt > /tmp/askcodex/sol61-review.json
   jq -r .result.text /tmp/askcodex/sol61-review.json
   ```
4. Before you use the answer, check it for these failure modes: "Yes." or questions where the deliverable should be; a finding or patch that relies on code you did not paste; a stated default that conflicts with your intent; headings, bold text or lists you did not ask for; work beyond the scope you set; a claim that tests pass.

## Rules

- Do not send a bare "Can you ..." ask without the proceed line.
- Do not send `--effort none` or `ultra`; both return HTTP 400. Change `none` to `low` in scripts moved from GPT-6 Sol.
- Do not rerun `max` hoping for a different result; switch to Astra.
- Do not use 6.1 Sol for bulk extraction or classification with a known schema; Luna costs 1/20 per token ([1], [7]).
- Replace credentials with placeholders before sending. Send personal data only with the user's consent.
- Do not reword a blocked request to get around the block. Report it. If a narrower defensive version still meets the user's goal, propose it and run it only with the user's agreement.

## Report

Tell the user the model and effort used, where the answer was saved, and any limitation that affects it. Name any safety block explicitly.

## Unverified

- [UNVERIFIED: whether Free and Go accounts can call it — the catalog lists them and the docs exclude them; no such account was probed]
- [UNVERIFIED: how often it asks instead of delivering at other efforts and on other prompts — one probe at `medium`]
- [UNVERIFIED: whether its cyber safeguards block defensive requests that GPT-6 Sol answered — not probed]
- [UNVERIFIED: which context limit `/codex/responses` enforces for one askcodex request — not probed]
- [UNVERIFIED: whether `reasoning.mode: "pro"` works — not probed]
- [UNVERIFIED: latency above `medium` — not measured]
- [UNVERIFIED: how much of the included quota an askcodex call uses — OpenAI publishes credit rates and message estimates for Codex, and included usage has "different multipliers" ([7])]

## Sources

[1]: https://openai.com/index/introducing-gpt-6-1-sol/ "Introducing GPT-6.1 Sol", published 2026-09-29
[2]: https://developers.openai.com/api/docs/models/gpt-6.1-sol "GPT-6.1 Sol (model page)", accessed 2026-10-02
[3]: https://learn.chatgpt.com/docs/models "Models", accessed 2026-10-02
[4]: https://developers.openai.com/api/docs/guides/latest-model "Using GPT-6", accessed 2026-10-02
[5]: https://deploymentsafety.openai.com/gpt-6-1-sol "Addendum to GPT-6 Astra System Card: GPT-6.1 Sol", published 2026-09-29
[6]: https://learn.chatgpt.com/docs/model-selection "Model selection", accessed 2026-10-02
[7]: https://learn.chatgpt.com/docs/pricing "Pricing", accessed 2026-10-02
[8]: https://developers.openai.com/api/docs/changelog "Changelog", accessed 2026-10-02
[9]: https://developers.openai.com/api/docs/models/gpt-6-sol "GPT-6 Sol (model page)", accessed 2026-10-02
[10]: https://github.com/openai/codex/tree/rust-v0.160.0/codex-rs/skills/src/assets/samples/openai-docs/references "openai-docs skill references at rust-v0.160.0", published 2026-10-01
