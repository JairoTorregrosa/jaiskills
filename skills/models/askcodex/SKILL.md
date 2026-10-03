---
name: askcodex
description: >-
  Use the askcodex CLI to get text and code from OpenAI models (GPT-6 Astra, Sol, Luna and
  older), generate or edit images, transcribe audio, and inspect available models, subscription
  usage, or authentication. Trigger for requests such as "ask GPT", "make an image",
  "pregúntale a GPT", "genera una imagen", "edita esta foto", "transcribe este audio",
  "qué modelos tengo", or "cuánta cuota queda", and for bounded one-shot tasks (draft, summarize,
  classify or extract into schema-checked JSON, generate an asset) worth a second model's
  answer. Not for critiquing repo work, plans or diffs: use second-opinion, which reads the repo.
---

# askcodex

You have the `askcodex` CLI. It sends one request to an OpenAI model through the user's
ChatGPT/Codex subscription and returns a text answer, an image, or a transcript. Turn the user's
request into a complete brief, run one focused call, check the result against the brief, and hand
the user the useful output with its saved path.

Canonical copy: `skill/` in https://github.com/JairoTorregrosa/askcodex (this is a mirror; change
it there, then re-sync). Local delta: the description's not-for clause points to second-opinion.

## Context you must respect

- This skill describes askcodex 0.3.0 or later. Check `askcodex --version` once per session. 0.2.x
  has no `--schema`, `--verbosity` or `--background`, prints the ~700 KB raw catalog inside
  `models --json`, and gives errors without `error.backend`; 0.1.x also hides the GPT-6 models.
  If it is older, tell the user to update instead of working around it: in an askcodex checkout,
  `git pull && ./install.sh`; without one, download the latest release binary from
  https://github.com/JairoTorregrosa/askcodex/releases (verify `SHA256SUMS`), or clone it and run
  `./install.sh` (needs Rust 1.88+).
- Every call is one-shot and stateless. `ask` sends only the prompt and optional `--instructions`:
  the model gets no tools, files, browsing, repository, or earlier conversation. A file path in a
  prompt is just text; paste the contents instead.
- Everything in a prompt, a reference image or an audio file leaves the machine for OpenAI's
  backend. Before you paste logs, exports, code or documents, always remove credentials, tokens,
  keys and passwords, even when the user supplied them for the task: replace them with
  placeholders. Also remove personal or customer data the task does not need; if the task needs
  it, or you cannot tell, ask the user first.
- Every call spends the user's subscription quota. GPT-6 Astra is the most expensive model.
- A second model's answer is input to your work. Verify its facts, review its code, and look at
  its images before you report success.
- askcodex uses the credentials `codex login` saved to `~/.codex/auth.json`; it reads no API key.
  Never print credentials.

## Facts already verified (2026-10-02)

- `askcodex models --no-refresh` lists what the account can use, with each model's description,
  Codex's default effort and any retirement date. On 2026-10-02:
  `gpt-6.1-sol`, `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`,
  `gpt-5.6-luna`, `gpt-daybreak-blue-latest`, `gpt-5.5` (retires 2026-10-14), and the hidden
  `gpt-reserve` and `codex-auto-review`. All take text; `ask` sends text only. OpenAI ships models
  every few days: trust the live catalog over this list.
- `ask` defaults to `gpt-6.1-sol` at `medium`. The catalog lists it for every plan; if a plan
  refuses it with a model-availability error (OpenAI's Codex docs have offered Free and Go only
  Luna), pass `--model gpt-6-luna`. askcodex never switches models on its own.
- `--effort` takes `low`, `medium`, `high`, `xhigh`, `max`, or `none`. The catalog also lists
  `ultra`, which is Codex's multi-agent mode; the backend rejects it. A level a model does not take
  fails with HTTP 400 (`none` on `gpt-6-astra` and `gpt-6.1-sol`; `gpt-6-sol` and `gpt-6-luna`
  accept it although the catalog omits it).
- `--verbosity low|medium|high` sets answer length and detail. Unset, the backend answers at
  `medium`; Codex itself asks for `low`. On the same prompt `low` used 240 output tokens and `high`
  513.
- `--schema FILE` makes the backend enforce a JSON Schema in strict mode, even against a prompt that
  asks for prose. Strict rules: every property in `required`, `"additionalProperties": false` on
  every object, and an optional value adds `"null"` to its own type (`["string","null"]`,
  `["integer","null"]`; an `enum` must list `null` too). A schema that breaks them fails before
  generation with `error.backend.code: "invalid_json_schema"` and a message naming the key. With
  `--json`, `.result.json` is the parsed answer. askcodex re-checks its structure against the
  schema, so an answer that does not parse or does not match is a `response_invalid` failure, never
  a result.
- `image create` and `image edit` return one PNG per call of about 1.57 megapixels; the prompt sets
  the aspect ratio. `--background transparent` or `opaque` forces the background (both honored);
  unset, the prompt decides. The result reports the file's real `width`, `height` and
  `alpha_channel`. There is no model, size, quality, format, or count flag, because the backend
  ignores those fields.
- `transcribe` takes a WAV file up to 25 MiB and has no model or language selector.

## Do this

1. Pick the command and read its guide before you write the prompt:

   | Result | Command | Read first |
   |---|---|---|
   | Answer, analysis, writing, code, or review | `askcodex ask "prompt" --model <slug> --effort <level>` (add `--verbosity low` for a concise answer) | [prompting-text.md](references/prompting-text.md) and the model's guide below |
   | Classification or extraction you will parse | `askcodex ask - --schema /tmp/askcodex/<name>.schema.json --json < brief.txt`, then read `.result.json` | Same as above |
   | New image | `askcodex image create "prompt" -o /tmp/askcodex/<name>-v1.png` (add `--background transparent` for a cutout) | [prompting-images.md](references/prompting-images.md) and [model-gpt-image-2.md](references/model-gpt-image-2.md) |
   | Image edit from one to five PNG references | `askcodex image edit "prompt" -i ref.png -o /tmp/askcodex/<name>-v2.png` | Same as a new image |
   | Audio transcript | `askcodex transcribe recording.wav` | [transcription.md](references/transcription.md) |
   | Which models exist, their default effort, what retires | `askcodex models --no-refresh` (a short list with descriptions) | Nothing; no prompt is involved |
   | Quota, account, auth status | `askcodex usage` / `whoami` / `auth status`, each with `--json --no-refresh` | Nothing |

2. For `ask`, pick the model and read its guide:

   | The task | Model | Guide |
   |---|---|---|
   | Most work: coding, review, debugging, analysis, drafting | `gpt-6.1-sol` (default) | [model-gpt-6.1-sol.md](references/model-gpt-6.1-sol.md) |
   | The hardest or most consequential single deliverable | `gpt-6-astra` | [model-gpt-6-astra.md](references/model-gpt-6-astra.md) |
   | Clear, repeatable extraction, classification, or transformation | `gpt-6-luna` | [model-gpt-6-luna.md](references/model-gpt-6-luna.md) |
   | Authorized defensive security work | `gpt-daybreak-blue-latest` | [model-gpt-daybreak-blue-latest.md](references/model-gpt-daybreak-blue-latest.md) |
   | Reproducing a GPT-6 Sol result | `gpt-6-sol` | [model-gpt-6-sol.md](references/model-gpt-6-sol.md) |
   | Reproducing a GPT-5.6 result | `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` | [sol](references/model-gpt-5.6-sol.md), [terra](references/model-gpt-5.6-terra.md), [luna](references/model-gpt-5.6-luna.md) |
   | Anything on `gpt-5.5` | move to `gpt-6.1-sol` (`gpt-6-luna` if the plan refuses it) | [model-gpt-5.5.md](references/model-gpt-5.5.md) |

   [prompting.md](references/prompting.md) indexes every guide. Pin `--model` and `--effort`
   whenever you compare outputs or need to reproduce one.
3. Write a complete brief: the deliverable, its audience, the constraints, what "done" means, the
   source material itself, what must stay unchanged, and the output format.
4. Run one focused request. Create `/tmp/askcodex/` first and give every artifact a descriptive
   name with a version suffix, so an edit never overwrites a useful result. For a long-running job,
   run it in the background or in tmux and save its output to a file.
5. Inspect the result against the brief. Make the next request about one specific observed problem,
   and keep the last useful version.

## Handle the output

- Images: always pass `-o /tmp/askcodex/<name>-vN.png`. With `--json`, `.result.width`,
  `.result.height` and `.result.alpha_channel` come from the saved file; `alpha_channel: true`
  only says transparency is possible, so look at the image before you call it a cutout.
- Long text answers: `--json > /tmp/askcodex/<name>.json`, then
  `jq -r .result.text /tmp/askcodex/<name>.json`. Keep large JSON and image payloads out of the
  conversation.
- `--json`, `--events`, and `--no-refresh` are global flags and work after the subcommand.
- Semantic `--json` success output is `{schema_version:1,command,result}`. Read `.result`. Do not
  pass `--backend` (it adds the raw backend response, ~700 KB for `models`) unless the user is
  debugging the protocol.
- `ask --json` gives one final envelope with `.result.model`, `.result.effort`,
  `.result.verbosity`, `.result.text`, `.result.usage` (possibly null), and `.result.json` with
  `--schema`. The catalog is at `.result.models` (slug, description, default_reasoning_level,
  upgrade); quota windows are at `.result.rate_limit`.
- `--events` prints newline-delimited JSON: `ask` sends `text_delta` events and one final `result`
  event on success; other commands send their result. Check the exit status: partial text is not
  success. Do not combine `--events` with `--json`.
- `transcribe` prints the text, or `.result.text` with `--json`.
- Stdin prompts (`-`) and `raw --body -` accept up to 16 MiB of UTF-8. File inputs must be regular
  files (symlinks to them work; devices and FIFOs do not). `image edit` accepts up to five PNG
  references totaling 25 MiB; renaming a JPEG to `.png` does not convert it, and the CLI checks the
  file signature. These caps are client memory limits, not server limits.
- `raw <METHOD> <PATH> --body '<JSON>'` is for a backend operation the user explicitly needs. It
  accepts only the backend origin, leaves JSON and stream bytes unwrapped, and does not support
  `--events`.
- `reference` prints the CLI reference locally, without credentials or network.

## Rules

- On a nonzero exit, report the error and fix its cause before another attempt. Do not loop,
  fabricate a result, or silently switch models.
- With `--json` or `--events`, a failure prints `{schema_version:1,error:{code,message,
  http_status?,backend?}}` on stderr and no success result. Never turn a partial stream into a
  completed answer. `error.backend` carries the backend's own reason, filtered: only `code`,
  `type`, `param`, `message`, `detail` and `error` (or `incomplete_details.reason`), each cut to
  400 bytes. When it is absent or reads as cut off, tell the user the full cause could not be read
  instead of guessing. Act on it:

  | The diagnostic says | Cause | Next step |
  |---|---|---|
  | `backend.code: "unsupported_value"`, `backend.param: "reasoning.effort"` | The model does not take that effort | Pick a level from the model's guide and retry once |
  | `backend.code: "invalid_json_schema"` | The `--schema` file breaks a strict rule | Fix the key the message names; no answer was generated |
  | `backend.detail: "... not supported when using Codex with a ChatGPT account."` | Unknown slug, or a model this plan cannot use | Check `askcodex models`; ask the user before using another model |
  | `backend.code: "cyber_policy"` or another policy code | A safety classifier blocked the request | Report it; do not reword the request to get around it |
  | `backend.incomplete_details` | The answer was cut short | Report it; narrow the task or ask for less output, then retry once |
  | `code: "rate_limited"` (HTTP 429) | Quota or rate limit | Check `askcodex usage --json --no-refresh` and tell the user |
- Use `--no-refresh` for read-only account and auth checks. `askcodex auth refresh` rotates the
  credentials and rewrites the auth file; run it only when the user asks for a refresh.
- Write into a project directory only when the user asks for that destination.

## Report

Tell the user the command you ran, the outcome, the artifact path if one was saved, and any
limitation that affects the result. For `ask`, add the model and effort. For an image, give the
file's real dimensions and never name a serving model: the backend does not report one. Show an
image when the user needs to judge it visually.

## Install

The binary is `~/.local/bin/askcodex`. From a checkout, `./install.sh` installs it without
touching credentials; `--skills agents`, `--skills claude`, or `--skills all` also installs this
skill, and `--check-auth` checks credentials without refreshing. See
[the repository](https://github.com/JairoTorregrosa/askcodex) and the
[generated command reference](https://github.com/JairoTorregrosa/askcodex/blob/main/docs/COMMANDS.md).
