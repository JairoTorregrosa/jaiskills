# Prompting guides

You are choosing which guide to read before an askcodex call. Read the general guide for the kind
of output, then the guide for the model you will call. Read only what the call needs.

## General guides

| Output | Guide | Covers |
|---|---|---|
| Text and code (`ask`) | [prompting-text.md](prompting-text.md) | Brief shape, context, efforts, deliverable types, iteration |
| Images (`image create`, `image edit`) | [prompting-images.md](prompting-images.md) | Visual brief, photographs, illustrations, layouts, references, iteration |
| Transcripts (`transcribe`) | [transcription.md](transcription.md) | Audio preparation and transcript handling; the command takes no prompt |

## Model guides

Each one covers what the model is for, its verified catalog facts, effort choice, model-specific
prompting rules, a worked example, and what is still unverified. Checked 2026-09-27 (GPT-6.1 Sol and
the catalog changes: 2026-10-02).

| Model | Use it for | Guide |
|---|---|---|
| `gpt-6.1-sol` (the `ask` default) | Most work: coding, review, debugging, analysis, drafting | [model-gpt-6.1-sol.md](model-gpt-6.1-sol.md) |
| `gpt-6-astra` | The hardest or most consequential single deliverable | [model-gpt-6-astra.md](model-gpt-6-astra.md) |
| `gpt-6-luna` | Clear, repeatable extraction, classification, transformation | [model-gpt-6-luna.md](model-gpt-6-luna.md) |
| `gpt-daybreak-blue-latest` | Authorized defensive security work | [model-gpt-daybreak-blue-latest.md](model-gpt-daybreak-blue-latest.md) |
| `gpt-6-sol` | Reproducing an earlier GPT-6 Sol result (now "previous generation") | [model-gpt-6-sol.md](model-gpt-6-sol.md) |
| `gpt-5.6-sol` | Reproducing an earlier GPT-5.6 coding result | [model-gpt-5.6-sol.md](model-gpt-5.6-sol.md) |
| `gpt-5.6-terra` | Reproducing an earlier GPT-5.6 balanced result | [model-gpt-5.6-terra.md](model-gpt-5.6-terra.md) |
| `gpt-5.6-luna` | Reproducing an earlier GPT-5.6 fast result | [model-gpt-5.6-luna.md](model-gpt-5.6-luna.md) |
| `gpt-5.5` | Nothing new: it retires 2026-10-14; migrate | [model-gpt-5.5.md](model-gpt-5.5.md) |
| `gpt-image-2` (sent by `image create`/`edit`) | What the image backend controls, aspect, transparency, text, Images 2.5 status | [model-gpt-image-2.md](model-gpt-image-2.md) |

`gpt-reserve` and `codex-auto-review` are hidden in the catalog and have no guide. `gpt-reserve` is
Codex's "Luna Reserve", a fallback for selected accounts once ordinary usage runs out;
`codex-auto-review` is the model Codex uses to approve or deny agent actions. Both answered a
plain `ask` on 2026-09-27, but neither adds anything to a one-shot askcodex call that the listed
Luna models lack, and hidden slugs have no public contract. Do not pick them for `ask`.

For model listings, quota, authentication, and output handling, use [SKILL.md](../SKILL.md); those
commands take no prompt.
