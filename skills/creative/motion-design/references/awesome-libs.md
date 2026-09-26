# Awesome libs for code-driven motion design and programmatic video

Verified 2026-09-26 against GitHub API; re-verify versions before pinning.

Part 1 of 2: default picks and sections 1–7 (frameworks, tweens, type, vector, canvas and brushes, 3D, particles). Part 2, [awesome-radar.md](awesome-radar.md), has data-viz, audio, capture and encode, post, AI-assist models, agent skills, the 2026 radar, dropped libraries, the awesome lists to re-scan and how to refresh.

Stars = GitHub stargazers on 2026-09-26. "Last release / push": latest GitHub release; `(npm)` when GitHub has no releases; `push DATE (rel YYYY)` when the last release is older than 2025. Maturity: **standard** = de-facto default; **solid** = maintained and production-usable; **experimental** = new, 0.x or small community. Watch licenses: Remotion (paid for companies >3 staff), AGPL (DepthFlow, essentia, hydra, audioMotion, video2x, upscayl, gifski, Cap), GPL-3.0 (typed.js v3), NC/community model licenses (MatAnyone, LYGIA, LTX-2, Hunyuan, IndexTTS).

## Default picks by job
- HTML-first agent pipeline, any genre: a plain page with `window.__seek(t)` + GSAP, rendered by `scripts/render_frames.py`, for one-offs; **HyperFrames** + GSAP (+ Lottie/Three/TypeGPU adapters) when you want a framework with lint, snapshots and agent skills. React team, data-driven variants or existing Remotion code: **Remotion** (+ `@remotion/*` packages). Decision matrix: [stack-selection.md](stack-selection.md).
- Math/technical explainer: **Manim (Community)**. Narrated vector diagrams: Revideo (active) over Motion Canvas (dormant).
- Terminal/dev demo: **VHS**, `@shikijs/magic-move`, Code Hike. Product UI walkthrough: Playwright capture + Remotion/HyperFrames overlay.
- Generative/data-art: p5.js (+ p5.brush, spectral.js) or three.js/TSL; export with canvas-record, ccapture.js v2 or Mediabunny.
- Music video: librosa/beat_this beat grid + demucs stems -> JSON keyframes -> any renderer; loudness via ffmpeg-normalize.
- Final encode/QA: FFmpeg (H.264 yuv420p, +faststart) via `scripts/export_social.py`, `scripts/video_gates.py` for the mechanical gates, gifski for GIF, VMAF for encode quality.

## 1. Programmatic video frameworks
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | HTML/CSS + seekable animations to deterministic MP4, agent-first CLI | Agent writes plain HTML+GSAP/Lottie/Three; 21 official skills; lint, snapshot, render, Lambda/Cloud Run | 53.3k | v0.8.78 · 2026-09-26 | Apache-2.0 | solid (0.x, daily releases) |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | React components rendered frame-by-frame to MP4/WebM | Largest ecosystem: transitions, captions, light-leaks, motion-blur, noise, Lottie/Rive/Three/Skia/GSAP pkgs, web-renderer | 60.6k | v4.0.529 · 2026-09-25 | Remotion Lic. (paid >3 staff) | standard |
| [midrender/revideo](https://github.com/midrender/revideo) | TypeScript generator scenes with headless render API | Code-first 2D scenes + React player; active under Midrender | 4.1k | 0.11.0 (npm) · 2026-07-10 | MIT | solid |
| [motion-canvas/motion-canvas](https://github.com/motion-canvas/motion-canvas) | TS generators + editor for voice-over-synced vector explainers | Great timing model for narrated diagrams; no feature work since 2025-02 | 19.2k | push 2026-07-02 (rel 2024) | MIT | solid (dormant) |
| [ManimCommunity/manim](https://github.com/ManimCommunity/manim) | Python engine for math/technical explainer animation | LaTeX, graphs, geometry morphs; best STEM explainer look | 41.1k | v0.21.0 · 2026-08-10 | MIT | standard |
| [3b1b/manim](https://github.com/3b1b/manim) | ManimGL, Grant Sanderson's OpenGL fork | Faster interactive preview; VideoMobject/Sprite added 2026-09 | 94.3k | push 2026-09-09 (rel 2024) | MIT | solid |
| [nexu-io/html-video](https://github.com/nexu-io/html-video) | Single-file HTML video templates rendered to MP4 locally | Ready templates (NYT chart, glitch title, light-leak) an agent fills | 4.6k | push 2026-06-21 | Apache-2.0 | experimental |
| [Zulko/moviepy](https://github.com/Zulko/moviepy) | Python clip compositing/editing on top of ffmpeg | Quick Python assembly of clips, text, audio | 14.9k | v2.2.1 · 2025-05-21 | MIT | solid |
| [mifi/editly](https://github.com/mifi/editly) | Declarative JSON5 spec to edited video (ffmpeg + GL transitions) | Slideshows/montages from a spec; slow maintenance | 5.5k | v0.15.0-rc.1 · 2025-01-19 | MIT | solid (slow) |
| [charmbracelet/vhs](https://github.com/charmbracelet/vhs) | Scripted terminal sessions (.tape) to GIF/MP4 | Deterministic CLI demos for dev products | 21.0k | v0.12.1 · 2026-09-24 | MIT | standard |

## 2. Timeline / tween engines
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [greensock/GSAP](https://github.com/greensock/GSAP) | Timeline/tween engine; all plugins now free (SplitText, MorphSVG, DrawSVG) | Seekable timelines = frame-exact renders; official skills + llms.txt | 28.6k | 3.15.0 (npm) · 2026-04-13 | GSAP Std (free) | standard |
| [motiondivision/motion](https://github.com/motiondivision/motion) | Motion (ex Framer Motion) for JS/React: springs, layout, WAAPI | Spring physics + layout animation in React scenes; llms.txt | 33.7k | 13.4.4 (npm) · 2026-09-25 | MIT | standard |
| [juliangarnier/anime](https://github.com/juliangarnier/anime) | Anime.js v4: timelines, SVG, stagger, text utils | Lightweight MIT alternative to GSAP; HyperFrames adapter | 73.1k | v4.5.0 · 2026-06-22 | MIT | standard |
| [pmndrs/react-spring](https://github.com/pmndrs/react-spring) | Spring-physics animation for React and R3F | Natural motion without hand-tuned easing | 29.2k | v10.1.2 · 2026-06-24 | MIT | solid |
| [tweenjs/tween.js](https://github.com/tweenjs/tween.js) | Minimal tweening engine (three.js classic) | Tiny deterministic tweens inside canvas/three loops | 10.1k | MIT | custom | solid |
| [gre/bezier-easing](https://github.com/gre/bezier-easing) | cubic-bezier easing function implementation | Reproduce CSS/After Effects curves in frame math | 1.8k | v3.1.0 · 2026-09-05 | MIT | solid |

## 3. Text & typography motion
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [chenglou/pretext](https://github.com/chenglou/pretext) | DOM-free multiline text measurement and layout | Per-line kinetic type in canvas/WebGL/SVG without reflow, any script | 50.6k | 0.0.9 (npm) · 2026-09-07 | MIT | solid (new, 0.0.x) |
| [gkurt/tegaki](https://github.com/gkurt/tegaki) | Handwriting animation for any font | Handwritten titles and signature reveals | 3.1k | 0.22.2 · 2026-09-23 | MIT | solid |
| [opentypejs/opentype.js](https://github.com/opentypejs/opentype.js) | Parse fonts, glyphs to SVG paths, variable fonts | Draw-on/morph glyph outlines, text on path | 5.0k | 2.0.0 · 2026-05-06 | MIT | standard |
| [harfbuzz/harfbuzzjs](https://github.com/harfbuzz/harfbuzzjs) | HarfBuzz text shaping in WASM | Correct Arabic/Devanagari/ligatures for glyph-level animation | 286 | v1.6.2 · 2026-09-21 | MIT | solid |
| [vercel/satori](https://github.com/vercel/satori) | JSX/HTML+CSS to SVG without a browser | Fast title cards, thumbnails, cover frames server-side | 14.0k | 0.33.5 · 2026-09-22 | MPL-2.0 | standard |
| [kane50613/takumi](https://github.com/kane50613/takumi) | Rust renderer: JSX/HTML/CSS to image or PDF | Faster satori alternative for stills and posters | 3.0k | 2.14.0 · 2026-09-15 | Apache-2.0 | solid |
| [protectwise/troika](https://github.com/protectwise/troika) | troika-three-text: SDF text for three.js | Crisp 3D kinetic type in WebGL scenes | 2.0k | push 2026-07-24 | MIT | solid |
| [barvian/number-flow](https://github.com/barvian/number-flow) | Animated digit-rolling number component | Stat hits and counters in explainers | 7.7k | 0.6.2 · 2026-07-18 | MIT | solid |
| [mattboldt/typed.js](https://github.com/mattboldt/typed.js) | Typewriter text effect | Typing hooks, fake-terminal captions | 16.3k | GPL-3.0 (v3) | custom | solid |
| [shikijs/shiki](https://github.com/shikijs/shiki) | Syntax highlighter; @shikijs/magic-move animates code diffs | Code-transition shots for dev demos (magic-move moved here) | 13.8k | v4.4.3 · 2026-08-10 | MIT | standard |
| [code-hike/codehike](https://github.com/code-hike/codehike) | Markdown + React annotated code walkthroughs | Code explainers; Remotion has a Code Hike template | 5.4k | 1.1.0 · 2026-03-17 | MIT | solid |
| [fontsource/fontsource](https://github.com/fontsource/fontsource) | Open fonts as self-hosted npm packages | Deterministic fonts in headless renders (no network) | 6.1k | core-v0.5.1 · 2026-09-23 | MIT | standard |

## 4. SVG / vector, Lottie & Rive
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [svgdotjs/svg.js](https://github.com/svgdotjs/svg.js) | Lightweight SVG manipulation and animation | Programmatic SVG scenes with a seekable runner | 11.8k | 3.2.6 · 2026-07-17 | MIT | solid |
| [rough-stuff/rough](https://github.com/rough-stuff/rough) | Hand-drawn sketchy rendering (canvas/SVG) | Whiteboard explainer look; stable, low churn | 21.2k | push 2024-07-28 (rel 2019) | MIT | standard (stable) |
| [rough-stuff/rough-notation](https://github.com/rough-stuff/rough-notation) | Animated hand-drawn underline/circle/highlight marks | Emphasis on text/UI; Remotion ships a wrapper | 9.7k | push 2024-03-18 | MIT | solid (stable) |
| [steveruizok/perfect-freehand](https://github.com/steveruizok/perfect-freehand) | Pressure-sensitive freehand stroke outlines | Organic drawn-on lines and signatures | 5.7k | v1.2.3 · 2026-02-01 | MIT | solid |
| [dai-shi/excalidraw-animate](https://github.com/dai-shi/excalidraw-animate) | Animate Excalidraw drawings stroke by stroke | Diagram draw-on explainers from .excalidraw files | 2.1k | push 2026-09-10 | MIT | solid |
| [visioncortex/vtracer](https://github.com/visioncortex/vtracer) | Color raster-to-SVG vectorizer | Turn logos/AI images into animatable paths | 7.1k | 1.0.0-alpha.4 · 2026-08-29 | MIT | solid |
| [svg/svgo](https://github.com/svg/svgo) | SVG optimizer (CLI/Node) | Clean paths and ids before animating | 22.7k | v4.1.0 · 2026-08-24 | MIT | standard |
| [linebender/resvg](https://github.com/linebender/resvg) | Fast SVG-to-PNG renderer (Rust, CLI, JS) | Rasterize SVG frames without a browser | 4.1k | v0.48.1 · 2026-08-02 | Apache-2.0 | standard |
| [iconify/iconify](https://github.com/iconify/iconify) | 200k+ open icons behind one API/CLI | Any icon set on demand for explainers | 6.3k | push 2026-09-25 | MIT | standard |
| [pqoqubbw/icons](https://github.com/pqoqubbw/icons) | Animated Lucide-style icons (Motion) | Ready micro-animated icons for UI demos | 8.1k | push 2026-08-22 | MIT | solid |
| [airbnb/lottie-web](https://github.com/airbnb/lottie-web) | After Effects Lottie JSON player (SVG/canvas) | Huge asset ecosystem; maintenance mode | 32.1k | 5.13.0 (npm) · 2025-05-21 | MIT | standard (maint.) |
| [LottieFiles/dotlottie-web](https://github.com/LottieFiles/dotlottie-web) | Rust/WASM Lottie and .lottie player, themes, state machines | Faster, frame-seekable modern Lottie player | 886 | 0.80.0 · 2026-08-28 | MIT | standard |
| [thorvg/thorvg](https://github.com/thorvg/thorvg) | C++ vector engine rendering SVG and Lottie (CPU/GPU/WASM) | Headless/native Lottie rendering | 1.8k | v1.1.2 · 2026-09-18 | MIT | solid |
| [ed-asriyan/lottie-converter](https://github.com/ed-asriyan/lottie-converter) | Lottie/.lottie/TGS to GIF, WebM, APNG | Export Lottie straight to shareable files | 1.0k | v1.2.0 · 2026-02-02 | MIT | solid |
| [rive-app/rive-wasm](https://github.com/rive-app/rive-wasm) | Rive runtime (WASM/JS) with state machines | Interactive vector characters; @remotion/rive exists | 970 | 2.43.1 · 2026-09-23 | MIT | standard |
| [GraphiteEditor/Graphite](https://github.com/GraphiteEditor/Graphite) | Node-based procedural vector/raster editor | Procedural vector art; watch for headless render | 27.4k | push 2026-09-26 | Apache-2.0 | experimental (alpha) |

## 5. Canvas / 2D creative coding & brushes
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [processing/p5.js](https://github.com/processing/p5.js) | Browser creative coding (v2.x) | Largest sketch corpus; generative art in minutes | 24.1k | v2.3.4 · 2026-09-25 | LGPL-2.1 | standard |
| [q5js/q5.js](https://github.com/q5js/q5.js) | p5-compatible API with WebGPU renderer | Same sketches, much faster heavy particle scenes | 422 | 4.7.0 · 2026-05-17 | LGPL-3.0 | experimental |
| [pixijs/pixijs](https://github.com/pixijs/pixijs) | Fast 2D WebGL/WebGPU renderer | Thousands of sprites + filters; official skills + llms.txt | 48.2k | v8.21.0 · 2026-09-17 | MIT | standard |
| [konvajs/konva](https://github.com/konvajs/konva) | Canvas 2D scene graph with tweens | Structured 2D scenes; llms.txt | 14.8k | 10.7.0 · 2026-09-23 | MIT | standard |
| [fabricjs/fabric.js](https://github.com/fabricjs/fabric.js) | Canvas object model with SVG import/export | Load SVG artwork and manipulate objects | 31.5k | v740 · 2026-05-18 | MIT | standard |
| [jonobr1/two.js](https://github.com/jonobr1/two.js) | Renderer-agnostic 2D API (SVG/Canvas/WebGL) | One scene, output as SVG or canvas | 8.7k | v0.8.24 · 2026-08-29 | MIT | solid |
| [williamngan/pts](https://github.com/williamngan/pts) | Creative coding and visualization library | Geometric/data-art compositions | 5.3k | v1.0.1 · 2026-09-19 | Apache-2.0 | solid |
| [mattdesl/canvas-sketch](https://github.com/mattdesl/canvas-sketch) | Generative art framework with frame export | Built-in MP4/GIF/PNG-sequence export | 5.3k | 0.7.8 (npm) · 2026-05-26 | MIT | solid |
| [raphaelameaume/fragment](https://github.com/raphaelameaume/fragment) | Modern creative-coding toolkit (Vite, live params, capture) | Sketch and record in one tool | 939 | v0.2.15 · 2026-07-01 | MIT | experimental |
| [acamposuribe/p5.brush](https://github.com/acamposuribe/p5.brush) | Natural brushes, hatching, watercolor fills for p5 | Painterly hand-made look for generative pieces | 931 | v2.2.2 · 2026-08-25 | MIT | solid |
| [rvanwijnen/spectral.js](https://github.com/rvanwijnen/spectral.js) | Kubelka-Munk paint-like color mixing | Pigment gradients instead of muddy RGB | 1.2k | 3.0.0 · 2025-04-25 | MIT | solid |
| [hydra-synth/hydra](https://github.com/hydra-synth/hydra) | Live-coding video synth (chained GLSL) | VJ-style feedback textures for music videos | 2.7k | push 2026-04-25 | AGPL-3.0 | solid |
| [css-doodle/css-doodle](https://github.com/css-doodle/css-doodle) | Web component for generative CSS patterns | Pattern backgrounds in HTML-based renders | 6.0k | v0.53.0 · 2026-09-25 | MIT | solid |
| [google/skia](https://github.com/google/skia) | Skia 2D engine; CanvasKit WASM; Skottie Lottie player | Pro-grade paths/shaders; @remotion/skia | 11.0k | push 2026-09-26 | BSD-3-Clause | standard |
| [linebender/vello](https://github.com/linebender/vello) | GPU-compute 2D vector renderer (Rust) | Huge vector scenes at GPU speed, native pipelines | 4.4k | v0.10.0 · 2026-08-14 | Apache-2.0 | experimental |
| [nannou-org/nannou](https://github.com/nannou-org/nannou) | Rust creative-coding framework | Native high-performance generative renders | 6.8k | v0.20.0 · 2026-06-22 | MIT/Apache-2.0 | solid |
| [openframeworks/openFrameworks](https://github.com/openframeworks/openFrameworks) | C++ creative-coding toolkit | Native heavy simulations and installs | 10.4k | nightly · 2026-09-26 | MIT | standard |
| [tixl3d/tixl](https://github.com/tixl3d/tixl) | Open realtime motion-graphics tool (node-based) | TouchDesigner-style realtime MG, open source | 5.1k | v4.2.1 · 2026-08-04 | MIT | solid |

## 6. 3D / WebGPU / shaders
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [mrdoob/three.js](https://github.com/mrdoob/three.js) | 3D library; WebGPURenderer + TSL node shaders | Default web 3D; llms.txt; r18x ships WebGPU path | 115.9k | r186 · 2026-09-24 | MIT | standard |
| [pmndrs/react-three-fiber](https://github.com/pmndrs/react-three-fiber) | React renderer for three.js | Declarative 3D inside Remotion (@remotion/three); llms.txt | 32.5k | v9.8.1 · 2026-09-24 | MIT | standard |
| [pmndrs/drei](https://github.com/pmndrs/drei) | R3F helpers: text, environments, cameras, effects | Ready environments, Text3D, float, sparkles | 9.9k | v10.7.9 · 2026-09-25 | MIT | standard |
| [pmndrs/postprocessing](https://github.com/pmndrs/postprocessing) | three.js post FX: bloom, DOF, noise, LUT | Cinematic finish on 3D shots | 2.9k | v6.39.5 · 2026-09-09 | Zlib | standard |
| [BabylonJS/Babylon.js](https://github.com/BabylonJS/Babylon.js) | Full 3D engine, WebGL/WebGPU, node materials | PBR + node editor; llms.txt | 26.1k | 9.28.0 · 2026-09-24 | Apache-2.0 | standard |
| [playcanvas/engine](https://github.com/playcanvas/engine) | WebGL/WebGPU runtime with Gaussian-splat support | Splats + glTF; official skills + llms.txt | 16.9k | v2.22.4 · 2026-09-23 | MIT | standard |
| [software-mansion/TypeGPU](https://github.com/software-mansion/TypeGPU) | Type-safe WebGPU/WGSL from TypeScript | Typed compute sims; HyperFrames adapter; llms.txt | 3.2k | v0.12.6 · 2026-09-25 | MIT | solid |
| [patriciogonzalezvivo/lygia](https://github.com/patriciogonzalezvivo/lygia) | Shader function library (GLSL/HLSL/WGSL/Metal) | Noise, SDF, color, blur by include | 3.4k | 1.4.1 · 2026-02-07 | Prosperity 3.0 (NC; paid commercial) | standard |
| [patriciogonzalezvivo/glslViewer](https://github.com/patriciogonzalezvivo/glslViewer) | CLI GLSL sandbox with headless frame export | Render a fragment shader to PNG sequence from shell | 5.3k | 3.5.2 · 2026-02-07 | BSD-3-Clause | solid |
| [paper-design/shaders](https://github.com/paper-design/shaders) | Zero-dependency shader components (mesh gradient, grain, dither) | Premium background loops in one line; llms.txt | 3.5k | 0.0.81 (npm) · 2026-09-17 | Apache-2.0 | solid |
| [ruucm/shadergradient](https://github.com/ruucm/shadergradient) | Animated 3D gradient backgrounds | Brand-opener backdrops | 2.6k | push 2026-09-23 | none stated | solid |
| [basementstudio/shader-lab](https://github.com/basementstudio/shader-lab) | Shader layer editor + React runtime (WebGPU) | Stack/animate shader layers as post | 689 | push 2026-09-24 | Apache-2.0 | experimental |
| [fand/vfx-js](https://github.com/fand/vfx-js) | WebGL effects on DOM elements (glitch, RGB shift) | One-line glitch/chromatic hits on HTML text | 1.1k | 1.1.0 · 2026-06-08 | MIT | solid |
| [gl-transitions/gl-transitions](https://github.com/gl-transitions/gl-transitions) | Open GLSL scene-transition collection | 100+ transitions; used by editly/ffmpeg pipelines | 2.1k | 1.71.0 (npm) · 2026-06-22 | MIT | standard |
| [BrokenSource/DepthFlow](https://github.com/BrokenSource/DepthFlow) | Image to 2.5D depth-parallax video | Camera moves on stills and AI images | 1.5k | v1.0.1 · 2026-08-25 | AGPL-3.0 | solid |
| [sparkjsdev/spark](https://github.com/sparkjsdev/spark) | Gaussian-splat renderer for three.js | Photoreal 3D captures inside web scenes | 3.7k | v2.2.0 · 2026-09-11 | MIT | solid |
| [gkjohnson/three-gpu-pathtracer](https://github.com/gkjohnson/three-gpu-pathtracer) | Path tracing for three.js | Photoreal product turntables | 1.8k | v0.0.24 · 2026-02-21 | MIT | solid |
| [blender/blender](https://github.com/blender/blender) | Scriptable 3D suite (bpy), Cycles/EEVEE, geometry nodes | Photoreal/stylized 3D headless; official MCP server | 20.5k | push 2026-09-26 | GPL-2.0+ | standard |
| [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | Community MCP to drive Blender from an LLM | Agent-built scenes when official MCP is unavailable | 29.4k | push 2026-09-25 | MIT | solid |

## 7. Particles / physics / simulation
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [tsparticles/tsparticles](https://github.com/tsparticles/tsparticles) | Configurable particles, confetti, fireworks | JSON presets for instant effects | 9.0k | v4.4.0 · 2026-08-31 | MIT | standard |
| [catdad/canvas-confetti](https://github.com/catdad/canvas-confetti) | Tiny confetti bursts | Celebration hits | 12.8k | 1.9.4 · 2025-10-25 | ISC | standard |
| [Alchemist0823/three.quarks](https://github.com/Alchemist0823/three.quarks) | VFX/particle system for three.js | Sparks, smoke, magic in 3D | 1.0k | push 2026-05-21 | MIT | solid |
| [creativelifeform/three-nebula](https://github.com/creativelifeform/three-nebula) | JSON-defined particle engine for three.js | Editor-authored 3D particle systems | 1.2k | v13.3.0 · 2026-09-19 | MIT | solid |
| [liabru/matter-js](https://github.com/liabru/matter-js) | 2D rigid-body physics | Falling/stacking logos, playful kinetic type | 18.4k | 0.20.0 (2024) · push 2026-09-24 | MIT | standard |
| [piqnt/planck.js](https://github.com/piqnt/planck.js) | Box2D port for JavaScript | Stable 2D physics | 5.3k | push 2026-09-22 | MIT | solid |
| [dimforge/rapier](https://github.com/dimforge/rapier) | 2D/3D physics (Rust, WASM builds @dimforge/rapier*) | Deterministic physics = reproducible frame renders | 5.8k | 0.21.0 (npm) · 2026-09-25 | Apache-2.0 | standard |
| [jrouwe/JoltPhysics.js](https://github.com/jrouwe/JoltPhysics.js) | Jolt physics compiled to WASM | Heavy 3D rigid-body scenes | 573 | 1.1.0 · 2026-07-11 | MIT | solid |
| [PavelDoGreat/WebGL-Fluid-Simulation](https://github.com/PavelDoGreat/WebGL-Fluid-Simulation) | GPU fluid simulation | Ink/smoke backgrounds; frozen since 2024-11 | 16.7k | push 2024-11-12 | MIT | solid (stale) |
| [jwagner/simplex-noise.js](https://github.com/jwagner/simplex-noise.js) | Fast seedable simplex noise | Organic drift and flow fields | 1.8k | push 2024-07-26 (rel 2024) | MIT | standard (stable) |
| [Auburn/FastNoiseLite](https://github.com/Auburn/FastNoiseLite) | Noise library incl. GLSL/HLSL/JS | Identical noise on CPU and shader | 3.5k | push 2026-06-21 (rel 2024) | MIT | standard |
| [anvaka/fieldplay](https://github.com/anvaka/fieldplay) | Vector-field particle explorer (GLSL) | Flow-field visuals | 1.3k | push 2026-09-23 | MIT | solid |
| [mapbox/webgl-wind](https://github.com/mapbox/webgl-wind) | WebGL wind particle visualization | Flow maps for data stories | 1.1k | push 2026-08-06 | ISC | solid |

