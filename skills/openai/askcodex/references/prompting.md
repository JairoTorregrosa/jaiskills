# Prompting guide — GPT-5.x family and gpt-image vian askcodex

How to pick a model, an effort, and a prompt shape for each job. Claims marked
(inferred) have no published source; everything else traces to the sources at
the bottom. Cost figures are API-side prices — through askcodex they translate to
subscription quota and latency, not dollars, but the relative ordering holds.

## 1. Universal GPT-5.x prompting rules

- Structure prompts with labeled blocks (`<output_verbosity_spec>`,
  `<design_and_scope_constraints>`, `<uncertainty_and_ambiguity>`); put
  constraints early and reference them consistently.
- Control verbosity with concrete targets: "3–6 sentences or ≤5 bullets"; for
  multi-step work, "1 short overview paragraph then ≤5 bullets tagged
  What changed / Where / Risks". Compact bullets over narrative.
- Avoid contradictions: don't cap output length while implicitly demanding
  verbose deliberation; pin `--effort` explicitly instead of relying on
  defaults.
- Scope discipline: "Implement EXACTLY and ONLY what is requested"; forbid
  invented features/styling; "if ambiguous, choose the simplest valid
  interpretation."
- Ambiguity and hallucination: have the model ask 1–3 clarifying questions or
  present 2–3 interpretations; "set missing fields to null rather than
  guessing"; never fabricate figures or references.
- Long context (>10k tokens): outline relevant sections first, restate the
  constraints, anchor claims to named sections.
- When switching 5.x versions: change one variable at a time — swap the model
  with the prompt held identical, pin effort, compare, then tune.

## 2. Per-model notes

- **gpt-5.6-sol** — flagship. Best for hard multi-step agentic work,
  terminal/computer use, difficult debugging, architecture changes,
  long-horizon knowledge work. Efforts: high/xhigh for real work; max only for
  consequential tasks (steep diminishing returns); ultra runs parallel
  subagents at ~3x the cost for a small score gain. Low/medium wastes the
  tier (inferred). askcodex's default model.
- **gpt-5.6-terra** — mid tier; published takes disagree (either "the
  practical center of the lineup, near-Sol at less than half the cost" or "a
  dominated middle tier"). Reasonable single-model default at medium/high
  (inferred).
- **gpt-5.6-luna** — cheapest/fastest of the 5.6 line. Classification,
  extraction, reformatting, summaries, routine code edits, high-volume
  pipelines; avoid for long-context work (quality drops). low/medium usually
  suffices (inferred). No ultra.
- **gpt-daybreak-blue-latest** — a Sol variant calibrated for authorized
  defensive-security work (vuln discovery, secure code review, malware
  analysis, IR). Prompt it like Sol; pick it only for defensive-cyber tasks
  (inferred).
- **gpt-5.5** — frontier for agentic coding and computer use, more
  token-efficient than 5.4, faster first token. Good Sol alternative when 5.6
  quota is tight (inferred). Caps at xhigh.
- **gpt-5.4** — solid prior-gen generalist; pick when quota matters and
  luna's long-context weakness bites (inferred). Caps at xhigh.
- **gpt-5.4-mini** — no published guide; all inferred: budget/latency floor
  for simple Q&A, formatting, classification; keep effort low/medium and
  escalate models rather than pushing it to xhigh.

## 3. Per-use-case recipes

- **Quick one-shot Q&A**: luna or 5.4-mini, low effort; "Answer in ≤3
  sentences. If uncertain, say so." (inferred model choice)
- **Code generation/review**: sol or 5.5, high (xhigh for gnarly debugging).
  Include `<design_and_scope_constraints>`: exact scope, no invented
  tokens/colors/features; require a brief "What changed / Where / Risks"
  summary. Verify with tests/tools, not model self-confirmation.
- **Summarization / JSON extraction**: luna, low–medium. Give the schema,
  mark required vs optional, "null rather than guessing", stable IDs per
  document, and a final "re-scan the source for missed fields" instruction.
- **Long-context analysis**: sol or terra (not luna), high. Outline-first +
  constraint restatement + section-anchored citations.
- **Agentic/tool-ish tasks**: sol, high–xhigh. Crisp 1–2 sentence tool
  descriptions; define stop conditions; after writes, restate what changed
  and where; forbid scope expansion.
- **Creative writing**: terra or 5.5, medium (inferred). Specify voice, POV,
  length, and what to avoid; give a short sample of the target register;
  high effort adds little here (inferred).

## 4. Reasoning effort — decision table

| Task type | Effort |
|---|---|
| Classification, reformatting, simple Q&A | low |
| Standard summarization, extraction, routine edits | low–medium |
| Production coding, multi-step analysis | high |
| Hard debugging, difficult reasoning problems | xhigh |
| Consequential work where the last capability points matter | max |
| Correctness dwarfs budget; parallel search useful | ultra (sol/terra/daybreak only) |

Caveats: cost and latency scale dramatically with effort (a published
comparison ran the same task at ~70x the price between luna-low and sol-max);
diminishing returns accelerate above high; 5.5/5.4/5.4-mini top out at xhigh.
Treat effort as a purchasing decision, not a default.

## 5. Image prompting (gpt-image vian askcodex)

Backend limits override any published knob advice: one opaque PNG per call,
server-chosen size, no transparency/quality/aspect/batch parameters, edits
take up to 5 PNG references. Everything is steered through prompt text.

- **Structure**: scene/background → subject → key details → style/medium →
  lighting → composition/framing → constraints → intended use. Short labeled
  lines, not one long paragraph.
- Be concrete about materials, textures, medium ("photorealistic",
  "watercolor", "3D render"); specify viewpoint, framing, mood; for people,
  describe scale, body framing, gaze, interaction.
- **Text in images**: exact wording in "double quotes", font style/color/
  placement, demand verbatim rendering; keep on-image text short — small
  dense text is the weakest spot.
- **Edits with references**: index them explicitly ("Image 1: product photo…
  Image 2: style reference…") and say how they combine. Always include a
  preserve list ("keep face, logo, layout, background, camera angle exactly
  the same; change only X") and repeat it on every iteration — omitting it
  causes drift on faces, logos and text.
- Size is server-chosen: state desired framing in words ("wide landscape
  composition", "tight square portrait crop") and accept variance (inferred).
- Camera specs are interpreted as mood, not physics; character consistency
  needs the preserve list every round; no transparency — design for opaque
  backgrounds; iterate serially, changing one thing per edit (inferred
  workflow).

### Anti-"AI look": make photos read as real

The default gpt-image output screams AI: waxy poreless skin, teal-orange
grading, HDR-glossy even light, dead-centered symmetric composition, posed
subjects, sterile clutter-free scenes. Real photos are full of small
failures — blown highlights, tilted horizons, missed focus, ugly light.
Steer against every telltale with positive description (there is no
negative-prompt knob):

- **Camera/film language — the highest-impact fix.** "shot on a 35mm lens
  at f/2", "ISO 1600, natural film grain visible", "shot on iPhone 15
  Pro", "Kodak Gold 200, fine grain". Skip the most-memed stocks (Portra
  400, Cinestill 800T) — they've become their own AI tell. Specs are
  interpreted as intent, not physics.
- **Imperfect, concrete light** instead of "beautiful lighting": "harsh
  direct on-camera flash, hotspot on faces, background falling to
  near-black", "flat overcast daylight, muted cool color", "mixed warm
  streetlight and cool fluorescent", "slightly underexposed available
  light".
- **Name the palette** ("muted earth tones", "faded warmth",
  "monochromatic") so the model can't default to teal-orange.
- **Candid composition**: "off-center framing, slightly tilted horizon,
  cropped at the edge, subject looking away mid-laugh, unposed, slight
  motion blur"; name a genre — "documentary photojournalism", "candid
  amateur snapshot".
- **Texture and imperfection**: "visible pores and fine lines, uneven skin
  tone, flyaway hairs, fabric weave visible, dust on the lens, chromatic
  aberration at contrast edges, halation around lights".
- **Mundane context** grounds the scene: "crumbs on the counter, tangled
  charger cable, damp pavement, ordinary everyday people".
- **Never write** the quality-worship words: "stunning", "8k",
  "ultra-detailed", "hyper-realistic", "masterpiece", "cinematic",
  "perfect", "flawless", "beautiful lighting" — they summon the glossy
  aesthetic. Phrase avoidance affirmatively: not "no plastic skin" but
  "visible pores and natural skin texture".
- **Reference PNGs are the strongest anchor**: attach a real photograph
  and state the relationship — "match the color palette, grain, and
  lighting of image 1; new subject: …".

Before → after: "Stunning ultra-realistic 8k portrait, perfect lighting,
masterpiece" → "Candid amateur flash snapshot, harsh direct on-camera
flash, hotspot on the faces, background falling into near-black, slight
motion blur, framing a little tilted, unposed".

## 6. Sources

- OpenAI Cookbook — GPT-5.x prompting guide (gpt-5-2_prompting_guide.ipynb)
- OpenAI Cookbook — image-gen models prompting guide
- developers.openai.com — daybreak-blue-latest model page
- simonw.substack.com — "The new GPT-5.6 family: Luna, Terra…"
- vellum.ai — "GPT-5.6 Sol, Terra, Luna explained"
- gist.github.com/IgorWarzocha — GPT-5.6 model-selection guide
- miraflow.ai — "How to make AI images look like real photos: prompt tricks"
- hedra.com — "Make AI images look like real photos: prompting"
- datalab.flitto.com — "This orange-and-teal color bias shouts AI-generated"

No published guide exists for gpt-5.4-mini or slug-specific prompting for
gpt-5.4/5.5/daybreak; family guidance is applied there and marked (inferred).
