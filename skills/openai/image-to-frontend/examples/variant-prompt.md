# Per-variant prompt template (Step 2 of image-to-frontend workflow)

Fire 4 of these in parallel, each with a different `Style direction`:
`askcodex image create "<prompt>" -o mockups/v1.png` … `-o mockups/v4.png`.

```
Business: "{name}" — {one-line pitch}.
Audience: {audience}. Tone: {tone}.
Primary CTA (verbatim, ALL CAPS in image): "{cta}".

Style direction for THIS variant: {editorial-serif | bento-grid | glass-morphism | brutalist-mono | <other>}.
Palette: {colors}. Accent: {hex}.

Render a landscape desktop-viewport landing-page hero + 2-3 sections below
(features, social proof, CTA). Describe it as if the product
already exists — real interface, not a Figma sketch. Photorealistic
deployed-site look. Use real interface elements: nav bar with 4
tabs, hero with headline + sub + CTA, feature row, footer.

Constraints:
- Keep on-image text to short headlines and labels (5-8 words max)
- No fake browser chrome, no watermarks, no logos other than "{name}"
- Clean typography, polished spacing, no decorative clutter

Save to: /abs/path/mockups/v{N}.png
Print absolute path.
```
