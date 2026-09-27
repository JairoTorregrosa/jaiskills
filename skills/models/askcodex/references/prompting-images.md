# Images with askcodex

You are about to turn a user's request into one PNG with `askcodex image create` or
`askcodex image edit`. You control the prompt and, for edits, up to five reference PNGs; the
backend decides everything else. Write a visual brief, generate, inspect the file, and iterate on
one observed problem at a time.

## Context you must respect

- One PNG per call. There is no size, quality, transparency, format, count, or model flag, because
  the backend ignores those fields.
- Model-specific rules (aspect, transparency, text limits, what to say about Images 2.5) are in
  [model-gpt-image-2.md](model-gpt-image-2.md). Read it with this file.
- `-i` takes up to five PNG references totaling 25 MiB (a client memory cap). References must be
  real PNG files: renaming another format does not convert it. Symlinks to regular files work;
  devices and FIFOs are rejected.
- A request in the prompt does not prove the PNG meets it. Inspect every result.

## Facts already verified (2026-09-27)

- The backend returns a fixed budget of about 1.57 megapixels shaped to the aspect you state:
  941×1672 for 9:16, 1672×941 for 16:9, 1254×1254 for square (observed 2026-09-23 to 2026-09-27).
  Exact pixel sizes are not reachable.
- A prompt that asks for a transparent background has returned a PNG with real alpha; a prompt
  that does not returns an opaque PNG (observed 2026-09-27, one call each).
- The model field askcodex sends (`gpt-image-2`) is ignored: a nonsense model name returned the
  same result. OpenAI says ChatGPT Images 2.5 reached Codex users on 2026-09-08, while its Codex
  image page still says `gpt-image-2`; which model serves askcodex is unverified. The API models
  `gpt-image-2.5-flare` and `gpt-image-2.5-sunburst` cannot be selected here, and their per-token
  API rates equal gpt-image-2's. Do not turn API prices, quality levels, or latency claims into
  promises about this CLI.
  Sources: [Images 2.5 announcement](https://openai.com/index/introducing-chatgpt-images-2-5/),
  [Codex image generation](https://learn.chatgpt.com/docs/image-generation),
  [API pricing](https://developers.openai.com/api/docs/pricing#image-generation).

## Do this

1. Choose the starting point:

   | Need | Workflow |
   |---|---|
   | Explore a new visual concept | Create from a clear brief |
   | Preserve a person, product, composition, or visual identity | Edit with a relevant reference |
   | Fix one defect in an otherwise useful result | Edit the last useful version with one focused change |
   | Combine content and style from different images | Edit with numbered references and an explicit role for each |
   | Several variants | Separate calls; keep the brief fixed except the variable you are exploring |

2. Write the visual brief in short labeled sections, keeping only the relevant ones:

   ```text
   Use: [Where this image will appear and who will see it.]
   Subject: [Main subject, action, and important identifying details.]
   Setting: [Background, environment, and supporting objects.]
   Composition: [Aspect ratio in words, viewpoint, framing, hierarchy, and empty space.]
   Style: [Photograph, illustration, painting, 3D render, or other medium.]
   Light and color: [Concrete lighting and palette.]
   Text: [Exact wording in double quotes, placement, and treatment; or no text.]
   Preserve: [Elements that must remain unchanged when editing.]
   Change: [The specific requested edit.]
   ```

   State the aspect ratio in words at the start, for example "Vertical 9:16 portrait
   composition." Resolve contradictions before the call. Describe materials, spatial
   relationships, and the intended use instead of words like "stunning" or "high quality".
3. Adapt the brief to the product:
   - **Photographs.** Name the kind of photograph, viewpoint, light, subject behavior, and setting.
     Camera language is a visual cue, not a guarantee of physical settings. For a candid look,
     pick the cues that fit: off-center framing, mixed ambient light, visible skin or fabric
     texture, ordinary clutter, slight motion. Do not add every imperfection by default.

     ```text
     Use: Editorial photograph for a neighborhood bakery story.
     Subject: A baker placing a fresh loaf on a flour-dusted wooden counter.
     Composition: Horizontal 3:2, eye-level, candid framing, hands and loaf clearly visible.
     Light and color: Soft morning window light, warm wood, muted cream tones.
     Style: Documentary photograph with natural fabric and skin texture.
     Text: No text.
     ```

   - **Illustrations and assets.** Name the medium, silhouette, palette, line treatment, detail
     level, and background, and say how the asset will be used. A small icon needs a clear
     silhouette and few details; a slide illustration needs a stated clear area for the title.
     For a cutout, ask for the subject isolated on a fully transparent background, with no
     scenery, solid backdrop, checkerboard, or shadow; then confirm the alpha is real and keep a
     chroma-key or cutout step ready as the fallback. For exact dimensions, plan a crop or resize
     after generation.
   - **Layouts and text.** Describe the hierarchy and relative positions: title above the image,
     product on the right, empty copy area on the left. Put exact text in double quotes with its
     placement, size relationship, and color. Keep copy short.
4. Run it. Create the output directory, then generate:

   ```sh
   mkdir -p /tmp/askcodex
   askcodex image create "Horizontal 16:9 composition. Editorial watercolor illustration of a small neighborhood bakery. Warm cream and muted blue palette, simple ink outlines, storefront on the right, clear space on the left for a slide title. No text." -o /tmp/askcodex/bakery-v1.png
   ```

   Inspect it, then edit one thing:

   ```sh
   askcodex image edit "Horizontal 16:9 composition. Change only the blue awning to muted terracotta. Preserve the storefront, composition, linework, background, and empty space on the left. No text." -i /tmp/askcodex/bakery-v1.png -o /tmp/askcodex/bakery-v2.png
   ```

   With several references, state their roles in the same order as `-i`:

   ```text
   Image 1: The product. Preserve its shape, proportions, and label.
   Image 2: The style reference. Use its palette and lighting.
   Create a new product composition using Image 1 as the subject.
   Keep the product label unchanged; do not copy objects from Image 2.
   ```

   Pass the previous output explicitly for each edit, and repeat the aspect and the preserve list:
   every call must carry its own context. Run calls that may take minutes in the background or in
   tmux.
5. Inspect: the subject, composition, every letter and number of the text, reference fidelity,
   the requested change, and the preserved elements. Check the real dimensions and whether the PNG
   has an alpha channel with `file <file>` (macOS and Linux) when they matter for delivery; look at
   the image to confirm the transparency is real. Correct a
   text error with an edit instead of regenerating a composition that works.

## Rules

- Change one thing at a time when diagnosing a problem; keep the last useful version.
- For broad exploration, make separate variants with a named difference, such as lighting or
  viewpoint.
- Do not promise an exact resolution, transparency, or exact text before you have checked the file.

## Report

Tell the user the file path, the actual dimensions, what you checked, and any requirement the image
does not meet (missing alpha, inexact size, text errors), plus any finishing step still needed.
Show the image when the user needs to judge it.
