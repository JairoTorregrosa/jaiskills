---
name: askcodex
description: >-
  Use the askcodex CLI to get text and code from OpenAI models, generate or edit
  images, transcribe audio, and inspect available models, subscription usage, or authentication.
  Trigger for requests such as "ask GPT", "make an image", "pregúntale a GPT", "genera una imagen",
  "edita esta foto", "transcribe este audio", "qué modelos tengo", or "cuánta cuota queda", and for
  bounded one-shot tasks (draft, summarize, classify, generate an asset) worth a second model's
  answer. Not for critiquing repo work, plans or diffs: use second-opinion, which reads the repo.
---

# askcodex

Use `askcodex` to turn a concrete brief into a text answer, code, image, or audio transcript.
Choose the command, supply the context it needs, inspect the result, and return
the useful output with its saved path.

Canonical copy: `skill/` in https://github.com/JairoTorregrosa/askcodex (this is a mirror; change it there, then re-sync). Local deltas to port upstream: the description's English triggers and not-for clause, and step 4's background-job wording.

## Choose the workflow

| Intended result | Command | Read before prompting |
|---|---|---|
| Answer, analysis, extraction, writing, code, or review | `askcodex ask "prompt" --model <slug> --effort <level>` | [Text and code](references/prompting-text.md) |
| New image | `askcodex image create "prompt" -o /tmp/askcodex/image-v1.png` | [Images](references/prompting-images.md) |
| Edit using one or more images | `askcodex image edit "prompt" -i reference.png -o /tmp/askcodex/image-v2.png` | [Images](references/prompting-images.md) |
| Audio transcript | `askcodex transcribe recording.wav` | [Transcription](references/transcription.md) |
| Available text/agent models | `askcodex models --json --no-refresh` | No prompting guide needed |
| Subscription usage | `askcodex usage --json --no-refresh` | No prompting guide needed |
| Account and plan | `askcodex whoami --no-refresh` | No prompting guide needed |
| Authentication status | `askcodex auth status --no-refresh` | No prompting guide needed |

[Prompting by product](references/prompting.md) is the reference index.
Read only the guide relevant to the requested output.

## Work from a complete brief

1. Identify the deliverable, audience, constraints, and definition of success.
2. Supply the source material the model needs. Include text explicitly; attach
   image references with `-i` for image edits.
3. Specify the output format and what must remain unchanged.
4. Run one focused request. For a long-running job, run it in the background
   or in tmux and save its output to a file.
5. Inspect the result against the brief. Make the next request about a specific
   observed problem; preserve the last useful version.

Treat a second model's answer as input to your work. Verify factual claims,
review generated code, and inspect generated images before reporting success.

## Save and return results

Create `/tmp/askcodex/` before writing artifacts. Use descriptive names and
version suffixes so edits do not overwrite a useful result.

- Images: always pass `-o /tmp/askcodex/<name>-v1.png`.
- Long text answers: use `--json > /tmp/askcodex/<name>.json`; read the answer
  with `jq -r .result.text /tmp/askcodex/<name>.json`.
- Keep large JSON documents and image payloads out of the conversation.
- Report the outcome, any material limitation, and the artifact path. Display
  the image when the user needs to assess it visually.
- Write into a project directory when the user requests that destination.

## Use the command surface accurately

- `--json`, `--events`, and `--no-refresh` are global flags and work after subcommands.
- Semantic `--json` success output is `{schema_version:1,command,result,backend?}`.
  Read `.result` for the command result; optional `.backend` contains the original
  response and may change independently of the askcodex schema.
- `ask` streams text normally. With `--json`, one final envelope contains
  `.result.model`, `.result.effort`, `.result.text`, and `.result.usage` (possibly null).
- Read the catalog at `.result.models` and usage windows at `.result.rate_limit`.
- `--events` emits newline-delimited JSON: `ask` sends `text_delta` events and
  one final `result` event on success. Other semantic commands emit their result.
  Check the exit status; partial text is not success. Do not combine with `--json`.
- `transcribe` returns text or `.result.text` in JSON mode. It accepts WAV files
  up to a 25 MiB client limit, with no model or language selector.
- Stdin prompts and `raw --body -` accept up to 16 MiB of UTF-8 text. File inputs
  must be regular files; symlinks to regular files work, devices and FIFOs do not.
  These size caps are client memory policies, not server limits.
- `reference` generates the CLI reference locally without credentials or network.
- `ask` accepts `--model`, `--effort`, and `--instructions`. Use the available
  model catalog to choose a slug and a supported effort.
- `image create` and `image edit` have no model, size, quality, transparency,
  output-format, or batch selector. Plan for one PNG per call and inspect its
  actual dimensions. Do not promise transparent output or an exact resolution.
- `image edit` accepts up to five PNG references totaling at most 25 MiB.
  Renaming a JPEG to `.png`
  does not convert it; the CLI checks the file signature.
- `raw` is for an explicitly needed backend operation:
  `askcodex raw <METHOD> <PATH> --body '<JSON>'`. It accepts only the configured
  backend origin. Its JSON and stream bytes remain unwrapped; `--events` is
  unsupported. Use the regular commands for the workflows above.

## Authentication and errors

The executable is `~/.local/bin/askcodex`. It uses credentials already stored
by `codex login` with file credential storage. In a checkout, `./install.sh`
installs the binary without requiring authentication. `./install.sh --skills agents` installs the cross-agent skill; use
`claude` for Claude Code or `all` for both destinations. `./install.sh --check-auth` explicitly checks credentials without
refreshing. See [the repository](https://github.com/JairoTorregrosa/askcodex)
for installation and the [generated command reference](https://github.com/JairoTorregrosa/askcodex/blob/main/docs/COMMANDS.md).

Use `--no-refresh` for read-only account and authentication checks.
`askcodex auth refresh` rotates credentials and rewrites the auth file; use it
when the user requests a refresh. Never print credentials.

With `--json` or `--events`, failures put a structured error on stderr:
`{schema_version:1,error:{code,message}}`. No final success result is emitted.
Never turn a partial stream into a completed answer.

On a nonzero exit, report the error and resolve its cause before another
attempt. Do not loop, fabricate a result, or silently switch models.
