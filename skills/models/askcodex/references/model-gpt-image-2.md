# Prompting GPT Image 2 (`gpt-image-2`) through askcodex

You are about to generate or edit one image with `askcodex image create` or `askcodex image edit`. The subscription backend chooses the model, size and quality and ignores what askcodex sends for them. You control the prompt, up to 5 PNG references and, since askcodex 0.3.0, the background.

## Context you must respect

- **What you control:** the prompt, up to 5 PNG references (25 MiB total, a client cap), and `--background transparent|opaque`.
  - askcodex has no model, size, quality, format or n flags, because the backend ignores those fields.
  - `--background` sends the backend's `background` field, which it honors both ways (observed 2026-10-02). Unset, the prompt decides, as before 0.3.0.
- **What this file covers:** only rules specific to this model and backend. For the general visual brief (labeled sections, composition, photos, illustrations, layouts, iteration), follow [prompting-images.md](prompting-images.md).
- **If the user asks for Images 2.5:** `gpt-image-2.5-flare` and `gpt-image-2.5-sunburst` are API models [6][7][8].
  - Tell the user askcodex cannot select an image model, and a model name sent with `askcodex raw` is ignored too (observed 2026-09-27).
  - The backend may already be serving Images 2.5 [6].
  - A guaranteed model, `xhigh`/`max` quality, an exact size, `n>1` or masks all require the OpenAI Image API with an API key and API billing [3][12]. That is outside askcodex; offer it, and never fake it.

## Facts already verified (2026-09-27; `--background`: 2026-10-02)

Checked against codex rust-v0.157.1 source, live calls, and the sources below.

**Backend behavior**
- askcodex sends `{prompt, model: "gpt-image-2"}`, plus `images[]` for `image edit` and `background` when `--background` is given. Codex rust-v0.157.1 and rust-v0.159.0-alpha.9 hardcode the same model string (observed 2026-09-27); Codex rust-v0.160.0 always sends `background` (observed 2026-10-02).
- The result reports what the saved file holds: `width`, `height` and `alpha_channel` read from the PNG header, plus the `background` the backend reported. Human output adds a line such as `  pixels 1254x1254, alpha channel yes, backend background transparent`; with `--json` the same facts are `.result.width`, `.result.height`, `.result.alpha_channel` and `.result.background` (askcodex 0.3.0).
- The model field is ignored. The same prompt sent with `gpt-image-2.5-flare` and with `zz-not-a-model` returned identical envelopes: 1370×1148, `quality: "low"`, 429 output image tokens (observed 2026-09-27).
- Size is a fixed budget of about 1.57 MP: 1,572,516–1,573,352 px across 9 outputs from 2026-08-07 to 2026-09-27 (observed 2026-09-27). The prompt shapes the aspect:

| Prompt wording | Output |
|---|---|
| "Vertical 9:16 portrait composition", placed first (2026-09-26) or last (2026-09-27) | 941×1672 |
| "wide 16:9 landscape film frame" (edits, 2026-09-24) | 1672×941 |
| Square subject, such as a 3×3 grid (2026-09-23) | 1254×1254 |
| No aspect stated | The model's choice: 1448×1086, 1370×1148, 1254×1254 |

- Edges are not multiples of 16, so the API `size` grid (1024x1536, 2K, 4K) cannot be reached. Quality is fixed: opaque results report `quality: "low"`, and sending `quality: "auto"` changed nothing (observed 2026-09-27).
- **Transparency:**
  - `background: "transparent"` returned alpha even for a neutral prompt: "A red ceramic mug, product photo, centered." gave RGBA 1254×1254 with 42.4% of pixels at alpha 0, and `image create --background transparent` with another neutral prompt gave RGBA 1254×1254 with 66.3% at alpha 0, a clean cutout (observed 2026-10-02, one call each). An earlier raw call returned RGBA, `quality: "medium"` and 2,058 image tokens in 41 s (observed 2026-09-27).
  - `background: "opaque"` overrides the prompt: a prompt asking for "a fully transparent background (PNG cutout, no backdrop)" came back RGB, `quality: "low"` (observed 2026-10-02, one call).
  - `image edit --background opaque` with a transparent cutout as the reference returned an RGB scene with the same subject (observed 2026-10-02, one call).
  - Without `--background`: a prompt asking for a transparent background returned RGBA with 52.5% of pixels at alpha 0 (1 of 1 call), and prompts without that request return opaque RGB (observed 2026-09-27).
- Cutout quality, prompt-only cutout: subject pixels sat at alpha 240–254 rather than 255, soft shadows were semi-transparent, and one edge had a faint color fringe (observed 2026-09-27).
- Every PNG carries a C2PA manifest (`softwareAgent` "ChatGPT", version "gpt-image"; observed 2026-09-27) and an invisible SynthID watermark [10].
- Time and quota: observed latency was 16–41 s (2026-09-27), and complex prompts can take up to 2 minutes [3]. Image calls use included Codex limits about 3–5× faster than ordinary turns [12].

**Model strengths and weaknesses**
- **Strong:**
  - Text rendering with crisp lettering [1]. "CAFÉ ABIERTO", accent included, rendered exactly (observed 2026-09-27).
  - Photorealism, identity preservation in edits, infographics, diagrams, multi-panel layouts, style transfer, and world knowledge ("Bethel, New York, August 1969" produces Woodstock) [1].
- **References:** every input image is processed at high fidelity automatically, and there is no `input_fidelity` setting [3][4].
- **Weak:**
  - Small or dense text, detailed infographics, close-up portraits and identity-sensitive edits. For these, OpenAI recommends `medium` or `high` quality [1]; askcodex results come back `low` (observed 2026-09-27).
  - Exact text placement, a recurring character staying consistent across separate generations, and exact element placement in layout-sensitive compositions [3].
  - Repeated edits can still change details you asked to preserve [2].
  - Transparency for gpt-image-2 is labelled "preview" [1][2].
- **Masks and reference limits:** API masking is prompt-guided and does not follow exact shapes. Codex caps edits at 5 references (`MAX_EDIT_IMAGES`); the API accepts 16 (Codex imagegen skill, 0.157.1).

**Images 2.5**
- Launched 2026-09-08 [6], succeeding Images 2.0 (gpt-image-2, released 2026-04-21) [4][5].
- **Flare** (`gpt-image-2.5-flare`): the fastest model, for everyday generation [7]. The announcement says higher quality than gpt-image-2 at 50% lower latency [6]; the prompting guide calls the quality "comparable to GPT Image 2" [2].
- **Sunburst** (`gpt-image-2.5-sunburst`): the most capable model, for work where editing precision matters most, with longer generation times [6][8].
- Both add `xhigh` and `max` quality and support transparency [3]. Both cost the same per token as gpt-image-2: $8 per 1M image input tokens, $30 per 1M image output tokens [9].
- OpenAI disagrees with itself about what Codex serves:
  - The announcement says Images 2.5 rolled out to Codex users on all tiers [6].
  - The Codex image-generation page says `gpt-image-2` [11].
  - The C2PA manifest says only "gpt-image" (observed 2026-09-27).

## Do this

1. **Decide create or edit, then the aspect.**
   - Use `image create` for a new image and `image edit` to preserve or transform an existing PNG.
   - References given only for style or subject make a generation with references, not an edit of Image 1 (Codex imagegen skill, 0.157.1).
   - Put the aspect ratio in words at the very start of the prompt, for example "Vertical 9:16 portrait composition." It worked both first and last (observed 2026-09-27).
   - Never give pixel sizes.
2. **Write the brief.** For the general visual brief, follow [prompting-images.md](prompting-images.md). Then apply these model rules:
   - **Order:** scene/backdrop → subject → key details → constraints → intended use (Codex imagegen skill, 0.157.1).
   - **Augmentation:** normalize a detailed user prompt without embellishing it. For a generic prompt, add only framing, intended use or practical layout (Codex imagegen skill, 0.157.1).
   - **Photographs:** write "photorealistic" or "real photograph". Camera specs work only as loose cues for the look [1].
   - **Moody scenes:** for wide, cinematic, low-light, rainy or neon scenes, specify scale, atmosphere and color. Otherwise the model trades mood for surface realism [1].
   - **People:** state framing, gaze and hands, for example "full body visible, feet included", "looking down at the open book, not at the camera", "hands naturally gripping the handlebars" [1].
   - **Text:**
     - Quote the copy, say how many times it appears ("render the tagline exactly once"), and add "no other text" [2].
     - Spell uncommon names letter by letter [1].
     - Keep in-image copy to one or two short lines; results are `low` quality (observed 2026-09-27), while OpenAI recommends `medium` or `high` for small text [1]. Put dense typography in a design tool.
   - **Cutouts:** pass `--background transparent`; it returned alpha even for a neutral prompt (observed 2026-10-02). Still write "isolated on a fully transparent background" and exclude scenery, solid backdrops, checkerboards and unwanted shadows [1]: the flag makes the background transparent, the wording keeps the subject clean to cut around.
   - **Opaque deliverables:** pass `--background opaque` when the image must have no alpha (a scene, a photo, a social or print asset), even if the prompt mentions transparency; it overrode such a prompt (observed 2026-10-02). With neither, the prompt decides.
   - **Real places and history:** name the place and the date [2].
3. **For edits, add:**
   - **Roles:** label every image by index and role (Codex imagegen skill, 0.157.1). Because every reference is read at high fidelity [3], give each one a narrow role, such as "use Image 2's palette and texture only" [2].
   - **Identity:** lock face, body shape, pose, hair and expression. Change only the named element, and require realistic fit plus matching light and shadows [1].
   - **Compositing:** say what moves where ("the dog from Image 2, right next to the woman in Image 1"). Match lighting, perspective and scale, and keep the base framing [1].
   - **Transparency:** the flag is per call. In every edit of a cutout, pass `--background transparent` again and repeat "preserve the transparent background" [1]. To place a cutout in a scene, pass `--background opaque`: that edit returned an RGB scene with the same subject (observed 2026-10-02).
   - **Aspect:** restate the aspect ratio in every edit. Nineteen 16:9 edits returned 1672×941 (observed 2026-09-24).
   - **Masks:** askcodex has none. If an area must stay pixel-identical, composite the approved edit into the original locally [2].
4. **Run it:**
   ```sh
   mkdir -p /tmp/askcodex
   askcodex image create 'Vertical 9:16 portrait composition. Sticker illustration for a café window: a steaming white coffee cup above a ribbon banner. Render "CAFÉ ABIERTO" exactly once on the banner in bold rounded letters; no other text. Thick white die-cut border. Isolated on a fully transparent background: no scenery, no solid backdrop, no checkerboard.' --background transparent -o /tmp/askcodex/cafe-sticker-v1.png
   askcodex image edit 'Vertical 9:16 portrait composition. Image 1 is the edit target. Change only the banner color to deep teal. Keep the cup, steam, die-cut border, the text "CAFÉ ABIERTO" and its letterforms unchanged. Preserve the transparent background.' --background transparent -i /tmp/askcodex/cafe-sticker-v1.png -o /tmp/askcodex/cafe-sticker-v2.png
   ```
   A near-identical create without the flag returned 941×1672 with alpha and exact text (observed 2026-09-27). The flag was verified on other prompts (observed 2026-10-02); this edit was not run.
5. **Inspect before you report.**
   - **Size:** read the `pixels WxH, alpha channel yes|no` line askcodex prints after the save, or `.result.width`, `.result.height` and `.result.alpha_channel` with `--json`. They come from the saved file's header; you need no `file` command. Expect about 1.57 MP at the requested aspect, and re-check on every call because these are dated backend observations.
   - **Transparency:** `alpha channel yes` proves only that the file can carry transparency, not that the background is transparent. Look at the image and confirm the background is truly see-through; a drawn checkerboard is not transparency [2]. Check edges, shadows and fringes.
   - **Text:** check every letter, accent and number of the in-image text.
   - **Preservation:** check that preserved elements and identity survived the edit, and check clothing and props in historical scenes [2].
   - **Blocked requests:** OpenAI checks prompts, input images and outputs [10]. If a request is blocked, report the block to the user; with `--json`, quote the backend's reason from `error.backend`. Do not reword it to get around the block or silently drop the blocked element. If a narrower version that is clearly allowed still meets the user's goal, propose it, and run it only with their agreement, saying what changed.

## Rules

- Do not put model names, "4K" or "high quality" in the prompt to raise resolution or quality. The backend ignores those fields (observed 2026-09-27).
- Do not add characters, props, brands, slogans or palettes the user did not imply (Codex imagegen skill, 0.157.1).
- Do not tell the user which model produced the image.
- Do not promise transparency, an exact size or exact text before you have looked at the result. `background: "transparent"` returned alpha in 3 of 3 calls (one through `--background`), transparency from the prompt alone in 1 of 1.
- Set the background with `--background`, not `askcodex raw`. Do not use `askcodex raw` to send a model name unless the user explicitly asks for a backend call.
- Never claim a generated image is not AI-made. It carries C2PA metadata and SynthID [10].

## Report

Tell the user the file path, the actual dimensions and alpha channel askcodex reported, what you checked (aspect, alpha, text, preserved elements), any requirement the image does not meet (missing alpha, inexact size, text errors) and any finishing step still needed (upscale, crop, composite). If they asked for Flare or Sunburst, say askcodex could not select it.

## Unverified

- [UNVERIFIED: which model serves askcodex. The model field is ignored, C2PA says only "gpt-image", and [6] and [11] disagree.]
- [UNVERIFIED: that every prompt-only transparency request returns alpha. Only 1 call was made.]
- [UNVERIFIED: that `--background transparent` always returns a clean cutout. 3 calls returned alpha; one was inspected as clean.]
- [UNVERIFIED: `image edit --background transparent`. Only an opaque edit of a cutout was run (observed 2026-10-02).]
- [UNVERIFIED: whether words like "4K" or "high quality" change the output. Not tested.]
- [UNVERIFIED: that the prompt alone set the aspect in the 2026-09-24 edits. One reference was already 16:9.]
- [UNVERIFIED: how askcodex reports a safety block. Never provoked.]
- [UNVERIFIED: that the pixel budget, aspect behavior and `low` quality persist. These are dated backend observations that can change without notice.]

## Sources

- [1]: https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide "GPT Image Generation Models Prompting Guide", published 2026-04-21 (transparency section added 2026-08-20)
- [2]: https://developers.openai.com/api/docs/guides/image-prompting "Image prompting" (GPT Image 2.5 guide and GPT Image 2 tab), accessed 2026-09-27
- [3]: https://developers.openai.com/api/docs/guides/image-generation "Image generation", accessed 2026-09-27
- [4]: https://developers.openai.com/api/docs/models/gpt-image-2 "GPT-Image-2" (snapshot `gpt-image-2-2026-04-21`), accessed 2026-09-27
- [5]: https://openai.com/index/introducing-chatgpt-images-2-0/ "Introducing ChatGPT Images 2.0", published 2026-04-21 (now points to 2.5)
- [6]: https://openai.com/index/introducing-chatgpt-images-2-5/ "Introducing ChatGPT Images 2.5", published 2026-09-08
- [7]: https://developers.openai.com/api/docs/models/gpt-image-2.5-flare "GPT-Image-2.5 Flare", accessed 2026-09-27
- [8]: https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst "GPT-Image-2.5 Sunburst", accessed 2026-09-27
- [9]: https://developers.openai.com/api/docs/pricing#image-generation "Pricing: image generation", accessed 2026-09-27
- [10]: https://deploymentsafety.openai.com/chatgpt-images-2-5 "ChatGPT Images 2.5 System Card", published 2026-09-08
- [11]: https://learn.chatgpt.com/docs/image-generation "Image generation" (Codex surfaces), accessed 2026-09-27
- [12]: https://learn.chatgpt.com/docs/pricing#image-generation-usage-limits "How does image generation count toward usage limits?", accessed 2026-09-27
- Codex imagegen skill, 0.157.1: https://github.com/openai/codex/tree/rust-v0.157.1/codex-rs/skills/src/assets/samples/imagegen (`SKILL.md`, `references/prompting.md`, `references/image-api.md`), accessed 2026-09-27
