# Secondary and tertiary use cases

## Secondary — batch single mockups (desktop + mobile per idea)

When the user wants one mockup pair (desktop + mobile) per idea across many ideas, skip the full 6-step workflow and fire one askcodex call per idea. See `examples/batch-pair-prompt.md` for the prompt template.

## Tertiary use cases

- **Logo generation**: ask for clean vector-like shapes, strong silhouette, balanced negative space, scalable; flat design, plain background, generous padding. Fire `n=4` (or 4 parallel calls) for variations.
- **Ads**: write the prompt as a creative brief (brand, audience, scene, exact tagline in quotes), let GI2 make taste-driven decisions inside those bounds.
- **Edits / try-on / object removal**: lock identity (face, body, pose, expression), allow changes only to specified elements, demand realistic fit/lighting/shadow integration.
- **Style transfer**: name what stays (palette, texture, brushwork) vs. what changes (subject). Keep background and framing constraints explicit.
- **Character consistency** (children's books, multi-page art): generate a reusable "character anchor" image first, then `images.edit`-style follow-ups passing that anchor in to advance scenes while preserving appearance.
- **Translation in images**: "translate text to X, do not change any other aspect of the image" — preserve typography, placement, hierarchy.
- **Product mockups on plain backgrounds**: ask for crisp silhouette, no halos/fringing, light polishing only, subtle contact shadow; preserve label legibility and product geometry exactly.
