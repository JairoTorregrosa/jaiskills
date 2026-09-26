# Choosing the stack

Pick the stack after the direction is locked (phase 3), from what the *piece* needs, not from habit.
Versions and licenses verified 2026-09-26; libraries move fast, so check the current release and docs
(`llms.txt`, official agent skills) before writing code. The catalogue of alternatives is in
[awesome-libs.md](awesome-libs.md).

## 1. Decision matrix

| The piece needs | Pick | Reference |
|---|---|---|
| Kinetic type, UI, diagrams, a one-off piece authored as a web page | **HTML/CSS/SVG/Canvas + GSAP**, rendered with `scripts/render_frames.py` | [stack-html-frames.md](stack-html-frames.md) |
| The same, for a company of 4+ people, with a framework and agent skills | **HyperFrames** (Apache-2.0, pre-1.0: pin it) | [stack-html-frames.md](stack-html-frames.md) §8 |
| Data- or prop-driven video, many variants or aspects from one codebase, VO/caption/beat sync, footage | **Remotion** (license: free for ≤ 3 people) | [stack-remotion.md](stack-remotion.md) |
| Hand-drawn, watercolor, ink, character animation, generative data-art | **p5.js 2 + p5.brush** | [stack-p5-brush.md](stack-p5-brush.md) |
| Particles, abstract 3D, product spins in the browser | **three.js (WebGL, or WebGPU + TSL)**, alone or via `@remotion/three` | [stack-3d-shaders.md](stack-3d-shaders.md) |
| Real light, materials, physics, hero 3D shots, alpha passes | **Blender 5.x headless** → PNG/EXR sequence → composite | [stack-3d-shaders.md](stack-3d-shaders.md) §8 |
| Equations, graphs, algorithm explainers | **Manim CE** (restyle it; the default look is recognizable), composite elsewhere | awesome-libs.md |
| Designer-supplied vector animation | **Lottie/dotLottie** or **Rive**, frame-driven playback | stack-remotion.md §3 |
| Quote cards, code plates, end-card stills | **Typst** or HTML stills, animated as layers | awesome-libs.md |
| Terminal or CLI demos | **vhs** tapes (deterministic), real screen captures for real UI | awesome-libs.md |

Mixed pipelines are normal: Blender passes composited under Remotion type; a p5 world with an HTML
title layer; Manim equations inside a GSAP page. Keep **one** timing source (the cue sheet) that every
layer reads.

Small pieces don't need a framework: a single HTML page with `window.__seek(t)` and the renderer is the
fastest path from idea to MP4. Reach for Remotion when you need its media timeline, variants or
`<Player>`, not by default.

## 2. The time contract (every stack)

Every pixel is a pure function of `(t or frame, fps, seed, props)`. Renders run in parallel and out of
order, so anything on a wall clock flickers or drifts.

| Banned during capture | Use instead |
|---|---|
| `requestAnimationFrame` loops, p5 `draw()` looping, R3F `useFrame` clocks, `THREE.Clock`/`Timer` deltas, TSL `time` | Derive from `t`: `useCurrentFrame()`, `__seek(t)`, `renderAt(t)` |
| CSS transitions/animations, Tailwind `animate-*`, autoplaying GSAP/anime timelines | Paused timelines + `seek(t)`; WAAPI `currentTime` |
| `Math.random()`, `Date.now()`, `performance.now()` | Seeded PRNG keyed by element and time (`hash(i)`, `boilSeed(key, t)`) |
| Integrating state frame to frame (`x += v`) | Closed form `pos = f(seed, t)`, or bake the simulation offline to per-frame data |
| Live `<video>` seeking, `AnalyserNode` | Pre-extracted frames or frame-exact media components; audio features precomputed to JSON |
| System fonts, network fonts, lazy images | Bundled font files + an explicit fonts/assets gate before the first capture |

Test it: render one frame as a still and inside a parallel render, then compare with a tolerance
(Chromium anti-aliasing can differ by a few levels across seek orders; md5 is too strict).

## 3. Licenses (tell the human when it matters)

| Tool | License | Watch for |
|---|---|---|
| Remotion | Source-available | Free for individuals, orgs ≤ 3 people, non-profits; Company License above (v5 will count contractors) |
| HyperFrames | Apache-2.0 | Pre-1.0, daily releases |
| GSAP 3.15 | Standard "no charge" (Webflow) | All plugins free incl. commercial; not OSI; can't build a Webflow competitor |
| anime.js 4 | MIT | v3 snippets from memory are wrong |
| three.js / R3F / drei | MIT | `postprocessing` (Zlib) is WebGL-only |
| p5.js / p5.brush | LGPL-2.1 / MIT | |
| Blender | GPL | Your renders are yours |
| Manim CE | MIT | Needs LaTeX for `MathTex` |
| Fonts | Varies | Brand fonts are often not redistributable: keep them out of public repos |

## 4. GPU in headless capture

Headless Chrome defaults to SwiftShader (CPU): WebGL is ~2× slower and WebGPU has no adapter.

- Remotion: `--gl=angle` (or `Config.setChromiumOpenGlRenderer('angle')`; `chromiumOptions: {gl: 'angle'}`
  in Node APIs). ANGLE leaks memory on long renders: split with `--frames` and concatenate.
- Playwright/Puppeteer on macOS: `--use-angle=metal` (`render_frames.py --gpu`); Linux servers: Vulkan/EGL
  if there's a GPU, otherwise SwiftShader.
- WebGPU and WebCodecs need a secure context: serve from `http://localhost`, not `about:blank`.
- Log the unmasked WebGL renderer once per tab; you want "ANGLE Metal", not SwiftShader.
- GPU-bound renderers (p5.brush, heavy WebGL) don't scale with tabs in one browser; use separate
  processes on disjoint frame ranges.

## 5. Check the machine before planning

```bash
ffmpeg -hide_banner -filters | grep -E ' (drawtext|subtitles|ass|zscale|libplacebo) '   # missing = render type in the scene
ffmpeg -hide_banner -encoders | grep -E 'aac_at|libx264|prores_ks|libsvtav1'
blender --version 2>/dev/null | head -1          # engine id is BLENDER_EEVEE on 5.x
node --version; npx --yes remotion versions 2>/dev/null | tail -3
uv --version                                      # scripts here are PEP 723 (`uv run --script`)
```

Homebrew's ffmpeg build ships without `drawtext`, `subtitles`/`ass`, `zscale` and `libplacebo`: draw all
type in the renderer (better anyway: brand fonts, animation, one timing source). Don't reinstall
ffmpeg without asking.

Budget the machine: a 16 GB laptop can't run a local music model, Blender and a 6-tab browser render at
once. Long jobs go in tmux or a queue, never the foreground; renders of finished ranges start while
other scenes are still being built.

## 6. Avoid for rendered output

- **Motion (framer-motion), react-spring**: real-time springs; rewrite with the stack's own spring.
- **Theatre.js** (dormant since 2024), **Spline** runtime (owns its clock; treat exports as footage),
  **timecut/timesnap** (unmaintained since 2022), **Motion Canvas** for agents (no headless render;
  Revideo is the headless fork).
- **Chrome BeginFrame deterministic mode** on macOS: crashes; Linux headless shell only.
- **OpenAI Sora API**: removed 2026-09-24.

## 7. Generative AI as an ingredient

Helps: textures, backplates, skies, stylized plates the code then animates (parallax, masks), model
sheets and concept frames as palette/composition guides, 1–3 s inserts.
Cheapens: realistic people, faces, hands, lip-sync; product UI (use real captures or code); any text
or logo (always set in code); an obvious 8-second-clip cadence; mixed model looks in one piece;
generated audio left in the clip.

- Images: OpenAI `gpt-image-2.5-sunburst` (edits) / `-flare` (fast) take custom sizes (edges multiple
  of 16, ratio 1:3–3:1) and transparent backgrounds. Subscription-backed image CLIs return one opaque
  PNG at a server-chosen size; state the aspect in the prompt's first words ("Vertical 9:16…") and
  upscale, or key out a flat chroma background for cut-outs.
- Video: Veo 3.1 (4/6/8 s clips; files deleted after 2 days, download at once), Gemini Omni Flash,
  Kling 3.0, Runway as an aggregator. Normalize every clip to the project fps, size and color before
  compositing; mute its audio and own the mix.
- Log model, prompt, seed or operation id per asset in `provenance.json`; generation isn't deterministic.
- Disclose when a viewer could mistake it for real (delivery.md §10).

## 8. Experimental edge (worth a test render, with a fallback shot)

| Technique | Maturity | Condition |
|---|---|---|
| Variable-font axis animation (`font-variation-settings` per frame) | Stable | Local font files |
| SDF/MSDF text in WebGL (troika) | Stable | Block the frame until typesetting finishes (async worker) |
| Precomputed audio-reactive visuals | Stable | Features in JSON keyed by frame |
| WebGPU + TSL compute particles | Usable with care | Closed-form particles; drive every uniform from the frame |
| HyperFrames | Usable with care | Pin the version; macOS uses screenshot capture, not BeginFrame |
| Gaussian splats (three r186 built-in, Spark 2) | Experimental | Slow camera, wait for the sort each frame, no streaming LoD |
| View Transitions / scroll-driven CSS rendered to video | Experimental | Pause animations and set `currentTime` per frame; not in Remotion |
