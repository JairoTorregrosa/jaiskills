# Images with askcodex

Use `image create` for a new image and `image edit` to preserve or transform
an existing image. The strongest controls available in these commands are
the prompt and, for edits, the reference PNGs.

## Choose the starting point

| Need | Workflow |
|---|---|
| Explore a new visual concept | Create an image from a clear brief |
| Preserve a person, product, composition, or visual identity | Edit with a relevant reference |
| Correct one defect in an otherwise useful result | Edit the last useful version with one focused change |
| Combine content and style from different images | Edit with numbered references and an explicit role for each |
| Produce several variants | Make separate calls; keep the brief fixed except for the variable being explored |

Save each version to a distinct PNG path under `/tmp/askcodex/`.
The CLI accepts up to five PNG references with `-i`, totaling at most 25 MiB.
This is a client memory cap, not a backend limit. References must be regular
files; symlinks to regular files are supported. Devices and FIFOs are rejected.

## Write a visual brief

Describe the visible result in short labeled sections:

```text
Use: [Where this image will appear and who will see it.]
Subject: [Main subject, action, and important identifying details.]
Setting: [Background, environment, and supporting objects.]
Composition: [Viewpoint, framing, hierarchy, and empty space.]
Style: [Photograph, illustration, painting, 3D render, or other medium.]
Light and color: [Concrete lighting and palette.]
Text: [Exact wording in double quotes, placement, and treatment; or no text.]
Preserve: [Elements that must remain unchanged when editing.]
Change: [The specific requested edit.]
```

Include only relevant sections. Resolve contradictory instructions before
calling the model. Describe materials, spatial relationships, and intended
use rather than relying on words such as "stunning" or "high quality."

Framing belongs in the prompt, but it does not guarantee file dimensions.
The CLI has no size, quality, transparency, format, batch, or image-model
selector. Observed backend responses contain one opaque PNG at server-selected
dimensions. Inspect the result; do not promise an exact resolution or transparency.

## Adapt to the visual product

### Photographs

Specify the kind of photograph, viewpoint, light, subject behavior, and
environment. Use concrete camera language as a visual cue rather than a
guarantee of physical camera settings.

For a candid look, useful cues include off-center framing, mixed ambient
light, visible skin or fabric texture, ordinary clutter, and slight motion.
Choose the cues that fit the scene; do not add every imperfection by default.

Example brief:

```text
Use: Editorial photograph for a neighborhood bakery story.
Subject: A baker placing a fresh loaf on a flour-dusted wooden counter.
Composition: Eye-level, candid framing, hands and loaf clearly visible.
Light and color: Soft morning window light, warm wood, muted cream tones.
Style: Documentary photograph with natural fabric and skin texture.
Text: No text.
```

### Illustrations and assets

Name the medium, silhouette, palette, line treatment, detail level, and
background. Say how the asset will be used so the composition fits its role.
For a small icon, prioritize a clear silhouette and few details. For a slide
illustration, specify which area should remain clear for a title.

If the final deliverable requires alpha transparency or exact dimensions,
identify that requirement before generation and plan an appropriate finishing
step. A request in the prompt is not proof that the exported PNG meets it.

### Layouts and text

Describe the hierarchy and relative positions: title above image, product on
the right, empty copy area on the left. Put exact text in double quotes and
specify its placement, size relationship, and color.

Keep copy concise when the use case allows. Inspect every letter, number,
label, and alignment in the generated result. Correct a specific error with
an edit instead of regenerating a composition that already works.

## Create and edit

Create the output directory, then generate:

```sh
mkdir -p /tmp/askcodex
askcodex image create "Editorial watercolor illustration of a small neighborhood bakery. Warm cream and muted blue palette, simple ink outlines, storefront on the right, clear space on the left for a slide title. No text." -o /tmp/askcodex/bakery-v1.png
```

Inspect the image before choosing the next edit:

```sh
askcodex image edit "Change only the blue awning to muted terracotta. Preserve the storefront, composition, linework, background, and empty space on the left. No text." -i /tmp/askcodex/bakery-v1.png -o /tmp/askcodex/bakery-v2.png
```

For multiple references, state their roles in the same order as `-i`:

```text
Image 1: The product. Preserve its shape, proportions, and label.
Image 2: The style reference. Use its palette and lighting.
Create a new product composition using Image 1 as the subject.
Keep the product label unchanged; do not copy objects from Image 2.
```

Use real PNG files; renaming another format does not convert it. Pass the
prior output explicitly for each edit. Repeat the preserve list so each call
contains the context it needs.

## Inspect and iterate

Check the subject, composition, exact text, reference fidelity, requested
change, and preserved elements. Also inspect actual dimensions and alpha
when they matter to delivery.

Keep the last useful version. Change one thing at a time when diagnosing a
problem. For broad exploration, make separate variants with a named difference
such as lighting or viewpoint. Queue calls that may take minutes.

These are prompting heuristics, not guaranteed model behavior. Evaluate the
actual image and finish only when it meets the user's brief.

## Model context — 2026-09-08

OpenAI's Images 2.5 succeeds Images 2.0 / `gpt-image-2`. Its public API offers
`gpt-image-2.5-flare` for most applications and `gpt-image-2.5-sunburst` for
finer control across edits. `gpt-image-2` remains available at lower API token
rates. Those API choices do not add an image-model selector to askcodex.
Do not translate API prices or latency claims into a promise about this CLI.

Source: [OpenAI's Images 2.5 announcement](https://openai.com/index/introducing-chatgpt-images-2-5/).
