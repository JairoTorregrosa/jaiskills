# Prompting Daybreak Blue (`gpt-daybreak-blue-latest`) through askcodex

You are about to send one request to `gpt-daybreak-blue-latest` with `askcodex ask`. Use it only for authorized defensive security work: secure code review, vulnerability triage, detection engineering, incident response analysis, or patch validation. For general coding, use [model-gpt-6-sol.md](model-gpt-6-sol.md). Its catalog entry mirrors [model-gpt-5.6-sol.md](model-gpt-5.6-sol.md), the non-alias flagship.

## Context you must respect

- askcodex sends one text-only request to `/codex/responses`: no tools, files, browsing, memory, image input, or Codex base instructions. Everything the model needs goes in the prompt or `--instructions`.
- This slug is an alias inside OpenAI Daybreak, its Trusted Access for Cyber program. Daybreak Blue gives reduced refusals "for verified defensive work in authorized environments" ([1]).
- Use it only on systems the user owns or is explicitly authorized to test or analyze. Never use it for customer-facing, third-party or downstream product traffic ([1]).
- The alias "follows updates to the Blue alias's underlying model" ([2]). The model behind it can change without the slug changing.
- Daybreak approval does not grant Zero Data Retention ([1]). Treat what you paste as retained.
- Codex's sandbox and auto-review safeguards for Daybreak ([3]) do not apply here, because askcodex runs no tools. You are the control that keeps the request in scope.

## Facts already verified (2026-09-27)

- Catalog (live, `client_version=0.157.1`): "Latest frontier agentic coding model for broad defensive cybersecurity work.", display name "Daybreak Blue".
  - `model_specialty: "cyber"`. The only access program listed is `daybreak_blue`. No Fast tier.
  - Efforts through askcodex: `none`, `low`, `medium`, `high`, `xhigh`, `max`. The catalog default is `low`; `ultra` is rejected with HTTP 400, and `none` works (observed 2026-09-27).
  - Context window 272,000 tokens (catalog max 872,000). Input: text and image, but `ask` sends text only. Minimal Codex client 0.144.0.
- Apart from name, description, specialty, speed tier, access programs and priority, its catalog entry matches `gpt-5.6-sol` field for field. Codex sends it the same base prompt as the GPT-5.6 family (Codex base instructions, 0.157.1).
- On Amazon Bedrock, the Daybreak Blue model ID is `openai.gpt-daybreak-blue-5.6-sol` ([1]).
- When the request omits `access_programs`, the alias selects `daybreak_blue`, and "The request fails if the required access is missing" (API behavior, [2]).
- On an account with Daybreak Blue enabled, the response reported `access_programs.cyber: "daybreak_blue"` and `model: "gpt-daybreak-blue-latest"`. The alias was not resolved to an underlying model (observed 2026-09-27).
- The same account got `daybreak_blue` automatically on `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` and `gpt-5.5` (observed 2026-09-27).
- Blue does not unlock offensive work. GPT-5.6 Sol under Daybreak Blue completed 2.0% of requests in OpenAI's "Advanced Cybersecurity Completion Rate" eval, which covers exploit chains, authentication bypass and privilege escalation. GPT-5.6-Cyber, a Daybreak Red model, completed 95.0% ([3]). Red models are not in this catalog.
- OpenAI's example of a Blue task: "Review the approved lab repository for authentication weaknesses, rank findings by evidence and impact, and propose patches without accessing external systems." ([4])
- Safeguards still apply. Blocked requests return error code `cyber_policy`, which can arrive mid-stream ([5]). askcodex reports this as `stream_failed`, with the code inside the message.
- Individual Daybreak users must have Advanced Account Security and FIDO2 hardware keys by Oct 1, 2026 to keep access ([1]).
- Probe, `--effort none`: exact JSONL from a 3-line log in 6.4 s (observed 2026-09-27).
- Probe, `--effort medium`, a Python function with an SQL injection and an off-by-one bug: it found both plus 3 real defects and closed the connection correctly in its fix. 40.7 s, 1,731 output tokens (observed 2026-09-27).

## Do this

1. Confirm scope. Before you write the brief, confirm that the user owns or is authorized to assess the target, and that the deliverable is defensive. If either is unclear, ask the user instead of calling the model ([1]).
2. Choose the effort:
   - Explain a vulnerability class, triage one finding, or draft a detection rule: `low`, the catalog default.
   - Secure review of one pasted function or diff: `medium`.
   - A threat model or a review spanning several components: `high`.
   - Use `xhigh`, then `max`, only when a concrete gap remains after you improve the brief.
3. Write the brief. Follow [prompting-text.md](prompting-text.md) for the general shape and step 2 of [model-gpt-5.6-sol.md](model-gpt-5.6-sol.md) for the GPT-5.6 rules. Then add:
   - Open with the authorization and scope in one or two lines: whose system it is, what is in scope, and the defensive outcome. This mirrors OpenAI's Blue example ([4]).
   - Ask for defensive deliverables: findings ranked by evidence and impact, the fix, detection logic, and validation steps.
   - Omit exploit detail that the defensive outcome does not need. OpenAI: "focus on a defensive outcome, such as identifying, preventing, or remediating a security issue. Omit exploit details that are not necessary to that outcome." ([6])
   - Redact secrets, tokens, customer data and internal hostnames from pasted code and logs ([1]).
4. Run it:
   ```sh
   mkdir -p /tmp/askcodex
   askcodex ask - --model gpt-daybreak-blue-latest --effort medium --json \
     < /tmp/askcodex/authz-review.txt > /tmp/askcodex/daybreak-authz-review.json
   jq -r .result.text /tmp/askcodex/daybreak-authz-review.json
   ```
   Example `authz-review.txt`:
   ```text
   Scope: our own internal billing service; I am on its security team and this review is authorized.
   Goal: find authorization flaws in the handlers below before release.
   Context: [paste the route handlers and the auth middleware, secrets redacted]
   Output: findings ranked by evidence and impact, each with the line, the attacker precondition, the impact, and a patch; then the tests that would prove each patch. An empty list is allowed.
   Do not write working exploit code; describe the trigger in one line.
   If code a finding depends on is missing, name the missing file instead of guessing.
   ```
5. Check the answer before you use it:
   - Whether each finding is reachable in the code you pasted.
   - Whether each patch closes the finding without breaking the documented behavior.
   - Any exploit detail beyond what you asked for.
   - A `stream_failed` exit with `cyber_policy` in the message. That is a block, not an answer.

## Rules

- Do not use it on systems outside the user's ownership or explicit authorization, or for anyone else's traffic ([1]).
- Do not ask it for exploit development, proof-of-concept weaponization, or production pentesting. Blue refuses most of that ([3]), and that work requires Daybreak Red.
- Do not reword a blocked request to get around the block. "Changing the wording does not change whether a request is allowed" ([6]). Narrow it to the defensive outcome, or report the block.
- Do not assume the model behind the alias stayed the same between runs. Record the date with the result ([2]).

## Report

Tell the user the model and effort used, where the answer was saved, and any limitation that affects it. Name any safety block. State that the answer came from a Daybreak alias whose underlying model can change.

## Unverified

- [UNVERIFIED: which model the alias serves today. The Bedrock ID and the catalog point to GPT-5.6 Sol ([1]), but OpenAI's API example pairs Daybreak Blue with `gpt-6-sol` ([2]), and the response echoed only the alias.]
- [UNVERIFIED: what this backend returns to an account without Daybreak Blue. The API fails the request ([2]); not probed on this backend.]
- [UNVERIFIED: this alias's knowledge cutoff. GPT-5.6 Sol's is Feb 16, 2026, if that is the underlying model.]
- Conflict on the hardware-key deadline: OpenAI's August posts say September 1, 2026 ([3]); the current help article says Oct 1, 2026 ([1]). The help article is newer.
- Conflict on defaults: Codex's app keeps the Daybreak toggle off by default ([1]), but askcodex omits `access_programs`, and the backend then applied `daybreak_blue` on every GPT-5.x model probed (observed 2026-09-27).

## Sources

[1]: https://help.openai.com/en/articles/20001258-openai-daybreak-trusted-access-for-cyber-overview "OpenAI Daybreak - Trusted Access for Cyber Overview", accessed 2026-09-27
[2]: https://developers.openai.com/api/docs/guides/daybreak "Use Daybreak in the Responses API", accessed 2026-09-27
[3]: https://openai.com/index/expanding-daybreak-as-the-cyber-defense-window-narrows/ "Expanding Daybreak as the Cyber Defense Window Narrows", published 2026-08-10
[4]: https://learn.chatgpt.com/docs/cyber-safety "Models and Trusted Access", accessed 2026-09-27
[5]: https://developers.openai.com/api/docs/guides/safety-checks/cybersecurity "Cybersecurity checks", accessed 2026-09-27
[6]: https://help.openai.com/en/articles/20001326 "Additional safety checks for biological and cybersecurity requests in ChatGPT, Codex, and the API", accessed 2026-09-27
