---
name: image-to-frontend
description: This skill should be used when the user asks to "image to frontend", "build this UI", "make me a landing page", "design and ship this site", "generate a mockup", "turn this screenshot into code", or hands over a product brief or reference image and wants a working React or HTML page. Also covers single-shot app screenshots (desktop + mobile pairs), logo and hero illustration generation, photorealistic compositing, and identity-preserving image edits via the askcodex CLI gpt-image path (no API key required; uses `codex login` credentials).
version: 0.1.0
---

# Image → Frontend (gpt-image via askcodex)

End-to-end workflow: brief → 4 visual variants → chosen variant → detailed build spec → real frontend code → iterate to pixel-close. Powered by the `askcodex` CLI (`askcodex image create` / `askcodex image edit`) from the [askcodex](https://github.com/JairoTorregrosa/askcodex) repo. **No API key needed** — askcodex reuses the credentials `codex login` already stored.

GI2 is genuinely strong: photorealistic web/mobile app screenshots, accurate text rendering, world knowledge, identity preservation across edits. But ~3 in 4 attempts fail to closely replicate a complex reference without strategy. Follow the steps; do not shortcut.

## Step 1 — Brief

Collect from the user (or draft and confirm):

- Business / product name and one-line pitch
- Audience and tone (expert + grounded? playful? minimal?)
- Primary CTAs (book a call, sign up, try demo)
- Aesthetic preferences, palette, vibe references
- Type (SaaS dashboard, marketplace landing, personal site, mobile app, infographic)
- Existing brand assets, icons, color tokens (paths)

Ambiguity is fine in step 2 — it surfaces options. Explicit direction massively improves variant quality.

## Step 2 — Generate 4 stylistic variants

Fire **4 `askcodex image create` commands in parallel** (background Bash calls in one message), each with a distinct visual direction (e.g. editorial-serif, bento grid, glass-morphism, brutalist-mono). Same brief, different style. Save to `mockups/v1.png` … `mockups/v4.png`.

Use the prompt template in `examples/variant-prompt.md` as the quoted prompt: `askcodex image create "<prompt>" -o mockups/v1.png`. Verify outputs with `file mockups/v*.png`. Read each PNG with the Read tool to view, then show the variants to the user.

## Step 3 — Image → detailed build spec

Once the user picks a variant, **do not jump straight to "build it."** Generate a meticulous build spec from the chosen image. Pass the PNG to a strong code/vision model and ask it to enumerate:

- Layout regions and grid structure
- Spacing scale (px values for gaps, padding, max-widths)
- Font family (display + body), weights, approximate sizes
- Color stops, gradients (with hex), accent uses
- Container widths, border radii, shadows
- Icon set / icon style
- Hover/active/focus states (inferred)
- Responsive breakpoints — what reflows at <1024 / <720 / <480
- Copy snippets exactly as rendered

Read the spec; **add anything the image omits but the page needs** (footer, legal links, secondary CTAs, mobile nav, 404, loading states).

## Step 4 — Build, with the image fed back into context

Pass BOTH the spec AND the original PNG into the implementation step. Instruct:

> Build the frontend exactly as outlined. While building, regularly refer back to the original image to check the work. Loop: build → diff against image → fix discrepancies → repeat. Carefully match spacing, font, icons, logos, layout, and text. Execution over speed. Accuracy over efficiency. Make sure it works on mobile.

The image-in-context is the load-bearing part — without it, output drifts.

## Step 5 — Annotate & iterate

The first build will not be pixel-perfect. Expect ~5–10 follow-ups for spacing, font, SVGs, copy fit. Best practice:

- Run the dev server and view the page in a browser.
- If a browser annotation tool is available (e.g. the `agent-browser` skill), highlight specific elements and **batch all fixes into one prompt** rather than trickling them.
- Each round should be visibly closer; if not, prompts are ambiguous — be more concrete (px values, hex codes, exact copy).

## Step 6 — Personalize and extend

Once the visual style locks, the same model also generates: logos, hero illustrations, product shots, supporting imagery, infographics, slide artifacts — separate `askcodex image create` / `askcodex image edit` calls. Keep style consistent by passing the chosen `v{N}.png` as a reference (`askcodex image edit "..." -i mockups/v{N}.png -o out.png`) and saying *"use the same style/palette/typography as the input image."* For motion, hand stills off to an image-to-video tool.

## Hard rules (askcodex specifics)

- **One askcodex call = one opaque PNG, size chosen by the backend.** There are no size/quality/transparency/batch flags. Do not ask for "4 variants in one call" — fire 4 calls in parallel instead, and put composition (landscape desktop viewport, mobile portrait framing) in the prompt wording.
- **Parallelize**: 6–8 concurrent `askcodex image create` processes are safe.
- **Usage cap**: on "usage limit" errors, check `askcodex usage` and wait for the reset before retrying.
- **Edit references must be PNG** (magic-byte checked, max 5, passed with `-i`).
- **Always pass an explicit `-o` path**. Verify with `file path.png`.
- **Read PNGs early** with the Read tool — catch style drift at variant #1, not at image #28.

## Additional Resources

### Reference Files

- **`references/prompt-engineering.md`** — phrasing rules across structure, text rendering, photorealism, composition, constraints/preserve-lists, multi-image inputs, and iteration.
- **`references/sizing.md`** — how sizing works under askcodex (server-chosen) and composition guidance.
- **`references/use-cases.md`** — secondary use case (batch desktop+mobile mockup pairs across many ideas) plus tertiary use cases: logos, ads, edits/try-on, style transfer, character consistency, in-image translation, product mockups on plain backgrounds.

### Examples

- **`examples/variant-prompt.md`** — Step 2 per-variant prompt template (4 parallel calls).
- **`examples/batch-pair-prompt.md`** — desktop + mobile pair template for the secondary batch case.
- **`examples/mvp-handoff-prompt.md`** — inline prompt to hand off a single idea's clean-MVP frontend implementation (mockup PNGs + brief → one deployable page). Built for the batch case where many ideas each need their own MVP page.
