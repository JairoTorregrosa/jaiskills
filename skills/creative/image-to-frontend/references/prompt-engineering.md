# Prompt-engineering rules for image generation (askcodex)

Apply these throughout any image generation, regardless of artifact type.

## Structure

- **Order matters**: background/scene → subject → key details → constraints. For complex prompts use line-broken sections, not one paragraph.
- **State the artifact**: "landing-page hero", "mobile app UI in iPhone frame", "1-pager infographic", "ad creative" — the artifact name sets the model's polish mode.
- **Describe the product as if it exists.** Avoid "concept art" / "design exploration" language for UI work.

## Text in images

- **Put literal copy in quotes or ALL CAPS.** Specify font style, weight, color, placement.
- **Spell tricky words letter-by-letter** for brand names, uncommon spellings.
- **Keep on-image text short.** Long sentences come out garbled — use 5–8 word labels and numbers.
- For dense text (infographics, slides, multi-font layouts), inspect every word and fix errors with a focused `askcodex image edit`; there is no quality setting to raise.

## Photorealism

- Use the word **"photorealistic"** explicitly. Adjacent triggers: "real photograph", "professional photography", "iPhone photo", "shot on 35mm film".
- Photography language for composition (lens, framing, lighting): "50mm lens, eye-level, soft coastal daylight, shallow DoF, subtle film grain". Use these for *look and composition*, not literal physical simulation — camera specs are interpreted loosely.
- Ask for real texture: pores, wrinkles, fabric wear, imperfections. Avoid "cinematic" / "movie poster" language unless that is the goal.

## Composition

- **Framing/viewpoint**: close-up, wide, top-down, eye-level, low-angle.
- **Lighting/mood**: soft diffuse, golden hour, high-contrast, overcast.
- **Layout placement**: "logo top-right", "subject centered with negative space on left".
- For people: scale, body framing ("full body, feet included"), gaze ("looking down at the book, not at the camera"), hand-object interaction.

## Constraints (what changes vs. what must NOT)

- State exclusions: "no watermark", "no extra text", "no logos/trademarks".
- For edits: "change only X" + "keep everything else the same". Repeat the preserve list every iteration to fight drift.
- For surgical edits, also preserve: saturation, contrast, layout, arrows, labels, camera angle, surrounding objects.

## Multi-image inputs

- Reference each by index + role: *"Image 1: product photo. Image 2: style reference. Apply Image 2's palette and brushwork to Image 1."*
- For compositing, be explicit about what moves where: *"place the dog from Image 2 next to the woman in Image 1; match Image 1's lighting and shadows."*

## Iteration

- Start with a clean base prompt. Refine with **small, single-change follow-ups** ("warmer lighting", "remove the extra tree", "restore original background").
- Use shorthand like "same style as before" / "the subject" — but re-specify critical details if they start drifting.
