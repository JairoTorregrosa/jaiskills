---
name: askcodex
description: >-
  Use OpenAI's GPT-5.x and image models from the command line with the `askcodex` binary: ask or
  complete text, generate or edit images, list models, check quota/plan. Trigger whenever the user
  wants an OpenAI model from the terminal — "pregúntale a gpt-5", "haz una imagen", "qué modelos
  tengo", "cuánta cuota me queda", "quién soy" — or when a quick one-shot task (summarize,
  classify, draft, generate an asset) is worth delegating to an OpenAI model. Auth is already on
  the machine; there is nothing to configure. Read this file completely before running anything:
  the flags, output locations and gotchas are below, and references/prompting.md carries the
  per-model, per-use-case prompting guide.
---

# askcodex — OpenAI models as a CLI

The binary lives at `~/.local/bin/askcodex`. If it is missing, clone
<https://github.com/JairoTorregrosa/askcodex> and run `./install.sh`. It authenticates with the
credentials `codex login` already stored — if they are missing, askcodex says so; tell the user to run
`codex login`.

## Intent → command

| The user wants | Run |
|---|---|
| ask GPT-5 / complete text | `askcodex ask "prompt" [--model <slug>] [--effort low\|medium\|high\|xhigh\|max\|ultra]` |
| make an image of X | `askcodex image create "X" -o /tmp/askcodex/x.png` |
| edit / restyle this image | `askcodex image edit "change ..." -i ref.png -o /tmp/askcodex/x-edited.png` |
| which models are available | `askcodex models` |
| how much quota / rate-limited? | `askcodex usage` |
| who am I / which plan | `askcodex whoami` |
| is the auth still valid | `askcodex auth status --no-refresh` |
| refresh the auth token | `askcodex auth refresh` |
| any other backend endpoint | `askcodex raw GET /codex/... [--body '{…}'] [--stream]` |

Two global flags, accepted anywhere on the command line, including after the deepest subcommand:

- `--json` — exactly one JSON document on stdout, nothing else.
- `--no-refresh` — the command will not rewrite the auth file. Use it for read-only checks.

## Prompting

Before writing a prompt — picking a model, choosing a reasoning effort, or phrasing an image
prompt — read [references/prompting.md](references/prompting.md). It has the per-model notes
(which slug for which job), per-use-case recipes (one-shot Q&A, codegen, extraction, long
context, creative), an effort decision table, and the image-prompt structure that works.

## Outputs go to /tmp/askcodex/

Save every artifact under `/tmp/askcodex/` (`mkdir -p /tmp/askcodex` first) instead of the working
directory, so large outputs never flood the conversation and stay recoverable by path:

- Images: `-o /tmp/askcodex/<descriptive-name>.png`, then report the path (and send the file if the
  user should see it).
- Answers you expect to be long: `askcodex ask "..." --json > /tmp/askcodex/<name>.json` — read back just
  the parts you need (`jq -r .text`). Short answers can stream to stdout normally.
- Raw endpoint dumps: `askcodex raw ... > /tmp/askcodex/<name>.json`.

Never write artifacts into a git repository's tree unless the user asked for the file there.

## Gotchas

- **Images: one opaque PNG per call, size chosen by the backend.** There are no size, quality,
  transparency, format, or batch flags — the backend ignores those parameters, so askcodex does not
  offer them. Don't promise a transparent logo or a specific resolution; if the user needs that,
  askcodex is the wrong path.
- **`image edit` references must be PNG**, max 5, passed with `-i`. askcodex checks the magic bytes
  locally and refuses a JPEG-renamed-to-.png before spending a billed request.
- **`askcodex ask` streams**; the prompt may be `-` to read stdin to EOF. Under `--json` nothing
  prints until the stream completes, then one `{"model","effort","text","usage"}` document —
  `usage` carries the backend's token counts (or `null` if it sent none). Pick `--model` from
  `askcodex models` slugs; the default is `gpt-5.6-sol` at `medium` effort.
- **`askcodex models --json` prints the whole `{"models": [...]}` envelope**, not the bare array —
  read `.models` if you want the list.
- **`askcodex auth refresh` rotates the real auth token** and rewrites the auth file. Run it when the
  user asks for it, not as a routine step; "is the auth valid?" is
  `askcodex auth status --no-refresh`.
- **`raw` only talks to the backend's own origin.** A path like `/codex/usage` or a full URL on
  that origin; anything else is refused at parse time — that's expected behavior, not a bug to
  work around.
- **Errors are final.** askcodex prints `askcodex: error: <message>` on stderr and exits non-zero. Report
  the message as-is instead of retrying in a loop.
