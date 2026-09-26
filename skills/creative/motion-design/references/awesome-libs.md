# Awesome libs for code-driven motion design and programmatic video

Verified 2026-09-26 against GitHub API; re-verify versions before pinning.

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

## 8. Data-viz animation
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [d3/d3](https://github.com/d3/d3) | Data-driven SVG/Canvas toolkit | Scales, shapes, interpolators to drive per-frame charts | 113.8k | 7.9.0 (2024) · push 2026-05-28 | ISC | standard |
| [observablehq/plot](https://github.com/observablehq/plot) | Concise grammar for charts | Clean charts to reveal step by step | 5.4k | v0.6.17 · 2025-02-14 | ISC | solid |
| [apache/echarts](https://github.com/apache/echarts) | Full chart library with built-in animation | Bar races and maps out of the box | 67.4k | 6.1.0 · 2026-05-19 | Apache-2.0 | standard |
| [vega/vega-lite](https://github.com/vega/vega-lite) | Declarative JSON chart grammar | Agent writes a JSON spec, renders SVG | 5.5k | v6.4.3 · 2026-04-24 | BSD-3-Clause | standard |
| [airbnb/visx](https://github.com/airbnb/visx) | React visualization primitives | Custom charts inside Remotion | 21.1k | v4.0.0 · 2026-06-11 | MIT | solid |
| [visgl/deck.gl](https://github.com/visgl/deck.gl) | GPU large-data visualization layers | Millions of points, arcs, hexbins | 14.6k | v9.4.0 · 2026-09-05 | MIT | standard |
| [maplibre/maplibre-gl-js](https://github.com/maplibre/maplibre-gl-js) | Open-source WebGL vector maps | Map flyovers/routes; Remotion maps skill; llms.txt | 11.7k | v6.11.2 · 2026-09-24 | BSD-3-Clause | standard |
| [CesiumGS/cesium](https://github.com/CesiumGS/cesium) | 3D globe, terrain, 3D tiles | Earth zoom-ins and flyovers | 15.8k | 1.145 · 2026-09-01 | Apache-2.0 | standard |
| [vasturiano/globe.gl](https://github.com/vasturiano/globe.gl) | three.js globe visualization component | Arcs/points on a globe in minutes | 3.2k | push 2026-08-22 | MIT | solid |
| [shuding/cobe](https://github.com/shuding/cobe) | 5 KB WebGL dotted globe | Brand-style spinning globe | 5.9k | 2.0.1 · 2026-03-19 | MIT | solid |
| [ChartGPU/ChartGPU](https://github.com/ChartGPU/ChartGPU) | WebGPU charting library | Huge animated series at 60 fps | 3.2k | v0.4.0 · 2026-08-03 | MIT | experimental |
| [SjoerdTilmans/sjvisualizer](https://github.com/SjoerdTilmans/sjvisualizer) | Python animated time-series charts (bar races) | Bar-chart-race exports | 240 | push 2026-09-09 | MIT | experimental |

## 9. Audio-reactive & audio tooling
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [librosa/librosa](https://github.com/librosa/librosa) | Python audio analysis (1.0) | Beats, onsets, RMS, spectra to JSON keyframes | 8.6k | 1.0.0 · 2026-08-11 | ISC | standard |
| [CPJKU/beat_this](https://github.com/CPJKU/beat_this) | State-of-the-art beat and downbeat tracker | Frame-exact cuts on beats and bars | 400 | v1.1.0 · 2026-04-14 | MIT | solid |
| [MTG/essentia](https://github.com/MTG/essentia) | C++/Python MIR: key, BPM, mood, onsets | Rich descriptors (AGPL) | 3.7k | push 2026-09-21 (rel 2014) | AGPL-3.0 | standard |
| [adefossez/demucs](https://github.com/adefossez/demucs) | Stem separation (maintained fork) | Drive visuals by drums/bass/vocals separately | 3.3k | push 2026-08-31 | MIT | standard |
| [nomadkaraoke/python-audio-separator](https://github.com/nomadkaraoke/python-audio-separator) | CLI/lib wrapping Demucs, MDX, RoFormer stem models | One-command stems | 1.4k | v0.47.0 · 2026-08-27 | MIT | solid |
| [katspaugh/wavesurfer.js](https://github.com/katspaugh/wavesurfer.js) | Waveform rendering and player | Audiogram waveforms | 10.4k | 8.0.1 · 2026-09-24 | BSD-3-Clause | standard |
| [bbc/audiowaveform](https://github.com/bbc/audiowaveform) | CLI waveform data/PNG generator | Precompute peaks JSON before render | 2.2k | 1.10.3 · 2025-08-20 | GPL-3.0 | solid |
| [Tonejs/Tone.js](https://github.com/Tonejs/Tone.js) | Web Audio synthesis and sequencing | Generate sound/sequences in the browser | 14.7k | 15.1.22 · 2026-07-12 | MIT | standard |
| [hvianna/audioMotion-analyzer](https://github.com/hvianna/audioMotion-analyzer) | High-resolution spectrum analyzer | Spectrum bars and radial visualizers (AGPL) | 953 | 4.5.4 · 2026-01-09 | AGPL-3.0 | solid |
| [jberg/butterchurn](https://github.com/jberg/butterchurn) | Milkdrop visualizer in WebGL | Classic psychedelic preset visuals | 2.0k | push 2026-04-20 | MIT | solid |
| [projectM-visualizer/projectm](https://github.com/projectM-visualizer/projectm) | Native Milkdrop-compatible visualization lib | Native preset rendering | 4.5k | v4.1.7 · 2026-07-14 | LGPL-2.1 | solid |
| [astrofox-io/astrofox](https://github.com/astrofox-io/astrofox) | Desktop app: audio to visualization video | No-code audio-reactive renders | 2.0k | v2.0.0 · 2026-08-28 | MIT | solid |
| [m-bain/whisperX](https://github.com/m-bain/whisperX) | Whisper + word-level alignment + diarization | Word-timed captions and lyrics | 24.3k | v3.8.6 · 2026-05-25 | BSD-2-Clause | standard |
| [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp) | C/C++ Whisper with Metal acceleration | Fast local transcripts; Remotion installer pkg | 53.9k | v1.9.4 · 2026-09-11 | MIT | standard |
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | CTranslate2 Whisper for Python | Fast ASR with timestamps | 25.6k | v1.2.1 · 2025-10-31 | MIT | standard |
| [MontrealCorpusTools/Montreal-Forced-Aligner](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner) | Forced alignment of known text to audio | Exact lyric/script word timings | 1.9k | v3.4.2 · 2026-08-20 | MIT | solid |
| [slhck/ffmpeg-normalize](https://github.com/slhck/ffmpeg-normalize) | EBU R128 loudness normalization via ffmpeg | Hit social loudness targets (about -14 LUFS) | 1.5k | v1.42.0 · 2026-09-02 | MIT | standard |
| [csteinmetz1/pyloudnorm](https://github.com/csteinmetz1/pyloudnorm) | Python loudness meter (ITU-R BS.1770) | Measure LUFS in QA | 783 | v0.2.0 · 2026-01-04 | MIT | solid |

## 10. Capture / encode / render
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [puppeteer/puppeteer](https://github.com/puppeteer/puppeteer) | Chrome/Firefox automation | Screenshot/screencast frame capture | 95.6k | 25.12.0 (npm) · 2026-09-23 | Apache-2.0 | standard |
| [microsoft/playwright](https://github.com/microsoft/playwright) | Cross-browser automation with video recording | Scripted product walkthrough footage | 96.7k | v1.63.0 · 2026-09-04 | Apache-2.0 | standard |
| [Vanilagy/mediabunny](https://github.com/Vanilagy/mediabunny) | Pure-TS media toolkit over WebCodecs (read/write/convert) | Encode MP4/WebM in browser or Node, no ffmpeg; llms.txt | 7.2k | v1.60.0 · 2026-09-25 | MPL-2.0 | standard (rising) |
| [dmnsgn/canvas-record](https://github.com/dmnsgn/canvas-record) | Record canvas to MP4/WebM/GIF (WebCodecs/WASM) | Frame-exact canvas export | 431 | 6.0.0 (npm) · 2026-09-17 | MIT | solid |
| [spite/ccapture.js](https://github.com/spite/ccapture.js) | Fixed-fps canvas capture by hijacking time (v2 revival) | Deterministic capture of real-time sketches | 3.8k | v2.0.0 · 2026-07-27 | MIT | solid |
| [alexey-pelykh/puppeteer-capture](https://github.com/alexey-pelykh/puppeteer-capture) | Puppeteer capture via BeginFrame (virtual time) | Frame-exact capture of arbitrary pages | 22 | 1.58.0 · 2026-08-07 | MIT | experimental |
| [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) | Encoder, muxer, filter graph | Final encode, concat, overlays, loudnorm, LUTs | 64.5k | push 2026-09-26 | LGPL/GPL | standard |
| [ffmpegwasm/ffmpeg.wasm](https://github.com/ffmpegwasm/ffmpeg.wasm) | FFmpeg compiled to WASM | Browser-side ops; slow for long renders | 17.8k | v12.15 · 2025-01-07 | MIT | solid (slow) |
| [seydx/node-av](https://github.com/seydx/node-av) | Native FFmpeg bindings for Node | Programmatic decode/encode without shelling out | 379 | v6.1.1 · 2026-07-06 | MIT | experimental |
| [PyAV-Org/PyAV](https://github.com/PyAV-Org/PyAV) | Pythonic FFmpeg bindings | Frame-level Python pipelines | 3.3k | v18.1.0 · 2026-08-12 | BSD-3-Clause | standard |
| [gpac/mp4box.js](https://github.com/gpac/mp4box.js) | MP4 parsing/muxing in JS | Inspect/fragment MP4 files | 2.5k | v2.4.1 · 2026-06-19 | BSD-3-Clause | solid |
| [WebAV-Tech/WebAV](https://github.com/WebAV-Tech/WebAV) | WebCodecs video-editing SDK | Browser compositing pipeline | 2.1k | push 2026-01-10 | MIT | experimental |
| [ImageOptim/gifski](https://github.com/ImageOptim/gifski) | Highest-quality GIF encoder | WhatsApp/Slack/README GIFs | 5.6k | 1.34.0 · 2025-07-13 | AGPL-3.0 | standard |
| [asciinema/agg](https://github.com/asciinema/agg) | asciinema recordings to GIF | Terminal GIFs | 1.7k | v1.9.0 · 2026-05-29 | GPL-3.0 | solid |
| [charmbracelet/freeze](https://github.com/charmbracelet/freeze) | Code/terminal output to PNG/SVG | Code stills for thumbnails | 4.9k | v0.2.2 · 2025-04-01 | MIT | solid |
| [CapSoftware/Cap](https://github.com/CapSoftware/Cap) | Open-source screen recorder (Loom alternative) | Raw product footage | 22.8k | v0.6.0 · 2026-09-15 | AGPL-3.0 (+MIT crates) | solid |
| [Breakthrough/PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | Scene-cut detection | Split and re-time footage | 5.2k | v0.7.1 · 2026-07-22 | BSD-3-Clause | standard |
| [WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor) | Auto-cuts silence and dead air | Tighten talking-head/demo footage | 5.4k | 31.6.0 · 2026-09-06 | Unlicense | solid |
| [Netflix/vmaf](https://github.com/Netflix/vmaf) | Perceptual video quality metric | QA encodes before posting | 5.5k | v3.2.1 · 2026-09-14 | BSD-2-Clause+Patent | standard |
| [lovell/sharp](https://github.com/lovell/sharp) | Fast Node image processing (libvips) | Resize/crop/convert assets and posters | 32.7k | v0.35.4 · 2026-08-26 | Apache-2.0 | standard |

## 11. Post: grading, grain, LUTs, upscaling, interpolation, matting
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [AcademySoftwareFoundation/OpenColorIO](https://github.com/AcademySoftwareFoundation/OpenColorIO) | Color management (ACES, OCIO configs) | Consistent color pipeline, LUT transforms | 2.1k | v2.5.2 · 2026-05-13 | BSD-3-Clause | standard |
| [colour-science/colour](https://github.com/colour-science/colour) | Python color science | Build/convert .cube LUTs, color math | 2.7k | v0.4.7 · 2025-12-06 | BSD-3-Clause | standard |
| [GreycLab/gmic](https://github.com/GreycLab/gmic) | 500+ image filters, CLI | Film looks and stylization per frame | 232 | v.4.0.5 · 2026-09-04 | CeCILL | solid |
| [ImageMagick/ImageMagick](https://github.com/ImageMagick/ImageMagick) | Image CLI toolkit with Hald CLUT support | Apply LUT looks to stills and frames | 17.5k | 7.1.2-31 · 2026-09-03 | ImageMagick | standard |
| [xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | GAN image/frame upscaler (+ ncnn-vulkan binary) | 4x upscale of stills/frames; frozen since 2024 but still default | 36.9k | push 2024-08-06 (rel 2022) | BSD-3-Clause | standard (stale) |
| [upscayl/upscayl](https://github.com/upscayl/upscayl) | Desktop/CLI AI image upscaler | Easy batch upscaling on a Mac | 49.9k | push 2026-09-15 (rel 2024) | AGPL-3.0 | solid |
| [k4yt3x/video2x](https://github.com/k4yt3x/video2x) | Video upscale + interpolation pipeline | One tool for super-res and frame interpolation | 21.8k | 6.4.0 · 2025-01-24 | AGPL-3.0 | solid |
| [OpenImagingLab/FlashVSR](https://github.com/OpenImagingLab/FlashVSR) | Diffusion-based streaming video super-resolution | Detail-rich upscale of AI clips | 1.9k | push 2026-09-01 | Apache-2.0 | experimental |
| [ByteDance-Seed/SeedVR](https://github.com/ByteDance-Seed/SeedVR) | SeedVR2 one-step video restoration/upscaling | Restore/upscale generated clips | 1.4k | push 2026-01-27 | Apache-2.0 | experimental |
| [hzwer/Practical-RIFE](https://github.com/hzwer/Practical-RIFE) | RIFE frame interpolation | 24 to 60 fps, smooth slow motion | 1.0k | push 2026-08-27 | MIT | standard |
| [georgmartius/vid.stab](https://github.com/georgmartius/vid.stab) | Video stabilization (ffmpeg vidstab filters) | Stabilize handheld B-roll | 961 | v1.1.2 · 2026-07-29 | LGPL-2.1+ | standard |
| [danielgatis/rembg](https://github.com/danielgatis/rembg) | Background removal CLI/lib | Cutouts for collage/parallax | 24.9k | v2.0.85 · 2026-09-20 | MIT | standard |
| [ZhengPeng7/BiRefNet](https://github.com/ZhengPeng7/BiRefNet) | High-resolution dichotomous segmentation | Hair-accurate mattes | 4.2k | push 2026-09-02 (rel 2024) | MIT | solid |
| [facebookresearch/sam3](https://github.com/facebookresearch/sam3) | SAM 3: promptable segmentation and tracking | Text-prompted video masks (text-behind-subject) | 11.8k | push 2026-09-18 | SAM License | solid |
| [pq-yang/MatAnyone](https://github.com/pq-yang/MatAnyone) | Consistent video matting | Clean alpha for people in footage | 1.6k | v1.0.0 · 2025-02-16 | S-Lab (NC) | solid |
| [mltframework/mlt](https://github.com/mltframework/mlt) | Multitrack engine behind Kdenlive/Shotcut (melt CLI) | Render XML timelines headless | 1.9k | v7.40.0 · 2026-06-25 | LGPL-2.1 | standard |
| [vapoursynth/vapoursynth](https://github.com/vapoursynth/vapoursynth) | Python frame-server for video filtering | Denoise/deband/resize chains | 2.1k | R80 · 2026-09-16 | LGPL-2.1 | solid |

## 12. AI-assist models (API / CLI / open weights)
| Name | What it is | Why an agent picks it for a shareable video | Stars | Last release / push | License | Maturity |
|---|---|---|---|---|---|---|
| [OpenAI Images (gpt-image-2.5-sunburst / -flare)](https://developers.openai.com/api/docs/guides/image-generation) | Image generate/edit; gpt-4o-mini-tts for voice | Sunburst for precise edits, Flare for fast gens; Sora 2 API shut down 2026-09-24 | API | API (docs 2026-09) | commercial | standard |
| [Gemini API (Nano Banana / Pro, Veo 3.1, Lyria 3.5)](https://ai.google.dev/gemini-api/docs) | Image, video, music, TTS (gemini-3.8-flash-tts) | Veo 3.1 clips with audio; Lyria RealTime; Omni Flash conversational edits; Imagen shut down | API | API (docs 2026-09) | commercial | standard |
| [Black Forest Labs (FLUX.2, FLUX 3)](https://docs.bfl.ai) | FLUX.2 images; FLUX 3 video with synced audio | Strong typography/brand images; official skills incl. FLUX 3 video | API | API (docs 2026-09) | commercial | standard |
| [Runway Dev API](https://docs.dev.runwayml.com) | Async video/image/audio generation endpoints | Official skills; task-poll API fits agents | API | API (docs 2026-09) | commercial | standard |
| [ElevenLabs (TTS v3, Music, SFX, Dubbing)](https://elevenlabs.io/docs) | Voice, music, sound effects, isolation, dubbing | One vendor for VO + score + SFX; skills + hosted MCP | API | API (docs 2026-09) | commercial | standard |
| [HeyGen API v3 (Video Agent, avatars)](https://docs.heygen.com) | Avatar/talking-head video generation | Presenter shots; official skills | API | API (docs 2026-09) | commercial | standard |
| [fal.ai / Replicate](https://fal.ai/docs) | Hosted gateways for open and closed media models | One key for many video/image/audio models; both publish skills | API | API | commercial | standard |
| [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Node-graph runtime for diffusion image/video/audio | Local reproducible workflows; comfy-skills | 135.1k | v0.37.0 · 2026-09-21 | GPL-3.0 | standard |
| [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) | Open text/image-to-video models | Local B-roll generation | 17.6k | push 2026-09-21 | Apache-2.0 | solid |
| [Lightricks/LTX-2](https://github.com/Lightricks/LTX-2) | Open audio+video generation model and trainer | Local clips with sound, LoRA training | 9.5k | v1.3.0 · 2026-08-26 | LTX-2 Community | solid |
| [Tencent-Hunyuan/HunyuanVideo-1.5](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5) | Lightweight open video generation model | Runs on consumer GPUs | 4.6k | push 2026-04-10 | Tencent Community | solid |
| [QwenLM/Qwen-Image](https://github.com/QwenLM/Qwen-Image) | Open image generation/editing model | Strong text rendering in images | 8.4k | push 2026-02-10 | Apache-2.0 | solid |
| [hexgrad/kokoro](https://github.com/hexgrad/kokoro) | 82M open TTS model | Free, fast local voice-over | 9.0k | push 2025-08-06 | Apache-2.0 | solid |
| [resemble-ai/chatterbox](https://github.com/resemble-ai/chatterbox) | Open TTS with emotion control and cloning | Expressive local VO | 26.6k | v0.1.2 · 2025-06-13 | MIT | solid |
| [index-tts/index-tts](https://github.com/index-tts/index-tts) | IndexTTS2 zero-shot TTS with duration control | Timed VO that fits a cut | 24.2k | v2.5.0 · 2026-08-13 | bilibili (custom) | solid |
| [microsoft/VibeVoice](https://github.com/microsoft/VibeVoice) | Open long-form multi-speaker voice AI | Podcast-style dialogues | 54.5k | push 2026-09-03 | MIT | solid |
| [SWivid/F5-TTS](https://github.com/SWivid/F5-TTS) | Flow-matching zero-shot TTS | Voice cloning locally | 15.3k | 1.1.22 · 2026-07-23 | MIT | solid |
| [ace-step/ACE-Step-1.5](https://github.com/ace-step/ACE-Step-1.5) | Open local music generation model | Royalty-free beds with lyrics locally | 12.9k | v0.1.8 · 2026-05-18 | MIT | solid |
| [multimodal-art-projection/YuE](https://github.com/multimodal-art-projection/YuE) | YuE2 open full-song generation | Songs with vocals from lyrics | 10.3k | yue2-v0.1.6 · 2026-09-09 | Apache-2.0 | experimental |
| [Stability-AI/stable-audio-tools](https://github.com/Stability-AI/stable-audio-tools) | Stable Audio training/inference code | Loops and SFX locally | 3.9k | push 2026-09-18 | MIT | solid |
| [hkchengrex/MMAudio](https://github.com/hkchengrex/MMAudio) | Video-to-audio (Foley) generation | Auto SFX matching on-screen motion | 2.3k | push 2026-02-23 (rel 2024) | MIT | solid |
| [Tencent-Hunyuan/HunyuanVideo-Foley](https://github.com/Tencent-Hunyuan/HunyuanVideo-Foley) | Text/video-to-audio Foley model | Synced SFX for generated clips | 1.1k | push 2025-09-28 | Tencent Community | experimental |
| [TMElyralab/MuseTalk](https://github.com/TMElyralab/MuseTalk) | Real-time lip-sync | Dub avatars/talking heads | 6.6k | push 2025-09-26 | MIT (code) | solid |
| [KlingAIResearch/LivePortrait](https://github.com/KlingAIResearch/LivePortrait) | Portrait animation from driving video | Animate a still face/mascot | 19.1k | push 2026-06-01 | MIT (code) | solid |

## 13. Agent skills & llms.txt available
Checked 2026-09-26: skills = `SKILL.md` files in the repo tree; llms.txt = HTTP 200 with a `text/plain` or `text/markdown` body. Install skills with [vercel-labs/skills](https://github.com/vercel-labs/skills) (`npx skills`, v1.7.0, 32.5k★) per the [agentskills.io](https://agentskills.io/home) spec; scan third-party skills with [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) (18.4k★) before installing.

| Library / vendor | Official skills (★ · push) | Install | llms.txt | Notes |
|---|---|---|---|---|
| Remotion | [remotion-dev/skills](https://github.com/remotion-dev/skills) (4.7k · 2026-09-25) | `npx skills add remotion-dev/skills` | https://www.remotion.dev/llms.txt | best-practices, create, markup, render, maps, captions, multimedia (Mediabunny), upgrade; monorepo also ships claude-code/codex plugins + MCP |
| HyperFrames | 21 skills in [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/tree/main/skills) | `npx skills add heygen-com/hyperframes` or `npx hyperframes skills update` | https://hyperframes.heygen.com/llms.txt | `/hyperframes` router; music-to-video, motion-graphics, faceless-explainer, product-launch-video, pr-to-video, media-use, remotion-to-hyperframes |
| GSAP | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) (15.7k · 2026-07-29) | `npx skills add https://github.com/greensock/gsap-skills` | https://gsap.com/llms.txt | core, timeline, plugins, utils, react, performance; Claude Code: `/plugin marketplace add greensock/gsap-skills` |
| Motion | none (motiondivision/ai-kit = Cursor plugin, 11★) | - | https://motion.dev/llms.txt | 62 KB, full API |
| three.js / R3F | none official; community [CloudAI-X/threejs-skills](https://github.com/CloudAI-X/threejs-skills) (3.4k, no license), [scottstts/Threejs-Awesome-Graphics-Agent-Skills](https://github.com/scottstts/Threejs-Awesome-Graphics-Agent-Skills) (856, MIT) | `npx skills add <repo>` | https://threejs.org/docs/llms.txt · https://r3f.docs.pmnd.rs/llms.txt | scottstts covers bloom, grading, procedural VFX, camera direction |
| PixiJS | [pixijs/pixijs-skills](https://github.com/pixijs/pixijs-skills) (337 · 2026-09-17) | `npx skills add pixijs/pixijs-skills` | https://pixijs.com/llms.txt | 26 skills incl. filters, particles, text, v8 migration |
| Babylon.js | none | - | https://doc.babylonjs.com/llms.txt | |
| PlayCanvas | [playcanvas/skills](https://github.com/playcanvas/skills) (24 · 2026-09-04) | `npx skills add playcanvas/skills` | https://developer.playcanvas.com/llms.txt | includes `verify-pixels` |
| Mediabunny | via Remotion `/remotion-multimedia` | - | https://mediabunny.dev/llms.txt | |
| Rive / LottieFiles | [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill) (1.8k, MIT; engine-agnostic principles) | `npx skills add LottieFiles/motion-design-skill` | https://rive.app/docs/llms.txt · https://developers.lottiefiles.com/llms.txt | |
| Paper Shaders · TypeGPU · Konva · MapLibre | none | - | https://shaders.paper.design/llms.txt · https://typegpu.com/llms.txt · https://konvajs.org/llms.txt · https://maplibre.org/llms.txt | |
| Remocn (Remotion shadcn registry) | [Remocn/remocn](https://github.com/Remocn/remocn) (1.5k, MIT) | `npx skills add Remocn/remocn` | - | copy-paste Remotion primitives: `npx shadcn@latest add @remocn/<name>` |
| Blender | official [Blender MCP Server](https://www.blender.org/lab/mcp-server/); community [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) (29.4k) | add-on + MCP config | - | headless alt: `blender -b file.blend -P script.py` |
| ElevenLabs | [elevenlabs/skills](https://github.com/elevenlabs/skills) (459 · 2026-09-25) | `npx skills add elevenlabs/skills` | https://elevenlabs.io/docs/llms.txt | TTS, music, SFX, isolator, dubbing; hosted MCP `https://api.elevenlabs.io/v1/mcp` (local elevenlabs-mcp archived) |
| HeyGen API | [heygen-com/skills](https://github.com/heygen-com/skills) (454) | `npx skills add heygen-com/skills` | https://docs.heygen.com/llms.txt | avatars, translate, video agent |
| Black Forest Labs | [black-forest-labs/skills](https://github.com/black-forest-labs/skills) (121 · 2026-09-09) | `npx skills add black-forest-labs/skills` | https://docs.bfl.ai/llms.txt | FLUX 3 video, keyframes, product ads, prompt doctor |
| Runway | [runwayml/skills](https://github.com/runwayml/skills) (70) | `npx skills add runwayml/skills` | https://docs.dev.runwayml.com/llms.txt | |
| fal · Replicate | [fal-ai-community/skills](https://github.com/fal-ai-community/skills) (247) · [replicate/skills](https://github.com/replicate/skills) (62) | `npx skills add <repo>` | https://fal.ai/docs/llms.txt · https://replicate.com/docs/llms.txt | model catalogs, prompting, routing |
| ComfyUI | [Comfy-Org/comfy-skills](https://github.com/Comfy-Org/comfy-skills) (207) | `npx skills add Comfy-Org/comfy-skills` | https://docs.comfy.org/llms.txt | Comfy Cloud generation |
| Gemini · OpenAI | [google-gemini/gemini-skills](https://github.com/google-gemini/gemini-skills) (4.2k; incl. gemini-omni-flash-api) · [openai/skills](https://github.com/openai/skills) (27.6k; imagegen, speech, transcribe) | `npx skills add <repo>` | https://ai.google.dev/gemini-api/docs/llms.txt · https://platform.openai.com/docs/llms.txt | |
| Anthropic · Hugging Face · Figma | [anthropics/skills](https://github.com/anthropics/skills) (178.5k; algorithmic-art, canvas-design, slack-gif-creator, frontend-design) · [huggingface/skills](https://github.com/huggingface/skills) (11.1k) · [figma/mcp-server-guide](https://github.com/figma/mcp-server-guide) (2.0k) | - | https://docs.anthropic.com/llms.txt | |

No llms.txt found (404 or HTML fallback): p5.js, D3, Manim, anime.js, Motion Canvas, Revideo, Tone.js, svg.js, Theatre.js, Pretext, Spark, Playwright, Puppeteer, FFmpeg, ECharts. Fetch their doc pages directly or lean on the skills above.

Community agent-video packs (study their workflows; do not depend on them): [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) (61.4k, AGPL, full agentic production), [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) (9.6k, cinematic product videos), [nolangz/pixel2motion](https://github.com/nolangz/pixel2motion) (2.3k, raster logo to SVG animation), [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) (2.1k), [Vincentwei1021/anything2explainer](https://github.com/Vincentwei1021/anything2explainer) (2.1k), [nexu-io/motion-anything](https://github.com/nexu-io/motion-anything) (822), [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills) (515, 50 skills), [Orkas-AI/Orkas-VideoStudio](https://github.com/Orkas-AI/Orkas-VideoStudio) (495), [snapcndev/snapcn](https://github.com/snapcndev/snapcn) (204, Remotion product-demo registry).

## Radar 2026 (rising / experimental, worth a test render)
1. **HTML-in-Canvas** ([WICG/html-in-canvas](https://github.com/WICG/html-in-canvas), 4.0k; Chromium flag `chrome://flags/#canvas-draw-element`): live DOM as a shader texture, so real UI text can melt, shatter or refract in product demos. [DavidHDev/canvas-ui](https://github.com/DavidHDev/canvas-ui) (4.7k, MIT + Commons Clause) ships 35 such effects.
2. **three.js WebGPURenderer + TSL** (r186): compute-shader particle morphs (logo -> 1M particles -> headline) at 4K. Examples: [verekia/tslfx](https://github.com/verekia/tslfx), basementstudio/shader-lab.
3. **TypeGPU 0.12**: typed WGSL compute sims keyed to the frame number, giving deterministic GPU simulations inside HyperFrames.
4. **Pretext** (@chenglou/pretext 0.0.9, 50.6k★): text that reflows around moving shapes every frame; per-line lyric layout in canvas.
5. **In-browser rendering**: Mediabunny + `@remotion/web-renderer` / `@remotion/webcodecs` mux MP4 client-side, so a shareable web toy can have an "export video" button with no server.
6. **Gaussian splats** (sparkjsdev/spark 2.2, [playcanvas/supersplat](https://github.com/playcanvas/supersplat) 10.3k): a phone capture of a real product or place becomes a photoreal fly-through inside a code-driven edit.
7. **[img2threejs](https://github.com/img2threejs/img2threejs)** (16.9k, v2.0.0 2026-09-06): reference photo -> procedural, animation-ready three.js model, so you get a product turntable with no 3D artist.
8. **DepthFlow 1.0**: any still (including AI images) -> 2.5D dolly/orbit shots. Replaces the Ken Burns effect.
9. **SAM 3 + MatAnyone**: text-prompted mattes for text-behind-subject titles over real footage.
10. **FlashVSR / SeedVR2**: diffusion upscaling of 480-720p AI clips to 1080x1920 for Reels without the mush.
11. **beat_this + demucs stems**: beat/downbeat grid plus per-stem envelopes, so cuts, flashes and scale pulses follow the song's structure.
12. **Structured generated scores**: Lyria 3.5 / Lyria RealTime, ElevenLabs Music, ACE-Step 1.5 (local), YuE2 give music that fits the edit length and has vocals when needed.
13. **FLUX 3 (video + synced audio) and Gemini Omni Flash (conversational video edits)**: API B-roll inserts and "change the sky" edits; both have official skills.
14. **Hand-made look**: tegaki + rough-notation + excalidraw-animate for whiteboard aesthetics that stand apart from glossy AI output.
15. **[cl0nazepamm/powershot-threejs](https://github.com/cl0nazepamm/powershot-threejs)** (63★): analog/digital camera emulation (grain, halation, lens) so 3D renders don't read as CG.

## Dropped or legacy (do not pick for new work)
- [theatre-js/theatre](https://github.com/theatre-js/theatre): no commits since 2024-04; @theatre/core 0.7.2 (2024-05). Use GSAP timelines or the Remotion/HyperFrames studios.
- vivus (rel 2021), flubber (2022), SplitType (2022), Splitting (2018), popmotion (push 2024-03), mojs (rel 2023), paper.js (rel 2021). Use GSAP DrawSVG/MorphSVG/SplitText (free), svg.js, opentype.js.
- tungs/timecut + timesnap (2022). Use ccapture.js v2, puppeteer-capture, or the Remotion/HyperFrames renderers.
- ARCHIVED: fluent-ffmpeg (2025-05; use ffmpeg CLI, node-av or Mediabunny), shiki-magic-move (-> `@shikijs/magic-move`), facebookresearch/demucs (-> adefossez/demucs), stable-ts (-> whisperX/MFA), google FILM (-> Practical-RIFE), dimforge/rapier.js (merged into dimforge/rapier; same npm names), elevenlabs-mcp (-> hosted MCP), strudel (moved to Codeberg), supertonic.
- Stale, with successors: coqui-ai/TTS (-> idiap fork, Kokoro, Chatterbox), RobustVideoMatting (-> MatAnyone), GaussianSplats3D (-> Spark), madmom/all-in-one (-> beat_this), meyda (2024) and essentia.js (npm 2022) (-> offline librosa/essentia to JSON), mixbox (stale + CC BY-NC; -> spectral.js).
- Shut-down APIs: OpenAI Sora 2 / Videos API (2026-09-24, no replacement); Google Imagen (use Nano Banana).

## Awesome lists and curated sources to re-scan
| List | ★ | Last push | Note |
|---|---|---|---|
| https://github.com/terkelg/awesome-creative-coding | 15.4k | 2026-07-21 | broadest creative-coding index |
| https://github.com/sergey-pimenov/awesome-web-animation | 1.6k | 2026-09-20 | web animation libs, GUI tools |
| https://github.com/mikbry/awesome-webgpu | 2.0k | 2026-09-10 | |
| https://github.com/AxiomeCG/awesome-threejs | 992 | 2026-07-28 | |
| https://github.com/sjfricke/awesome-webgl | 1.5k | 2026-04-02 | |
| https://github.com/vanrez-nez/awesome-glsl | 1.4k | 2023-08-21 | stale but still the best shader list (no live awesome-shaders exists) |
| https://github.com/camilleroux/awesome-generative-art | 120 | 2026-08-28 | kosmos/awesome-generative-art (1.8k) stale since 2024-06 |
| https://github.com/raphamorim/awesome-canvas | 1.9k | 2026-06-14 | |
| https://github.com/willianjusten/awesome-svg | 4.6k | 2026-07-16 | |
| https://github.com/willianjusten/awesome-audio-visualization | 5.1k | 2026-08-13 | |
| https://github.com/transitive-bullshit/awesome-ffmpeg | 1.2k | 2026-09-18 | + https://github.com/rendi-api/ffmpeg-cheatsheet (1.7k, 2026-04-29) |
| https://github.com/krzemienski/awesome-video | 1.9k | 2026-07-20 | streaming-heavy; encoders/players |
| https://github.com/LottieFiles/awesome-lottie | 329 | 2026-04-06 | |
| https://github.com/ManimCommunity/awesome-manim | 526 | 2026-09-08 | |
| https://github.com/agmmnn/awesome-blender | 7.4k | 2026-01-22 | |
| https://github.com/AlonzoLeeeooo/awesome-video-generation | 785 | 2026-09-24 | + https://github.com/showlab/Awesome-Video-Diffusion (5.8k, 2026-09-21) |
| https://github.com/Anil-matcha/awesome-ai-video-models | 196 | 2026-09-23 | API model roundup |
| https://github.com/ScreenKite/awesome-ai-video-editing | 36 | 2026-08-20 | |
| https://github.com/fliptheweb/motion-ui-design | 929 | 2026-05-15 | motion design resources |
| https://github.com/jasonwebb/morphogenesis-resources | 2.3k | 2026-09-10 | procedural growth (no live awesome-procedural-generation exists) |
| https://github.com/ellisonleao/magictools | 17.4k | 2026-09-26 | gamedev incl. procedural tools |
| https://github.com/VoltAgent/awesome-agent-skills | 34.9k | 2026-09-23 | + ComposioHQ/awesome-claude-skills (75.7k), hesreallyhim/awesome-claude-code (54.6k) |

No maintained list exists for awesome-remotion, awesome-p5js or awesome-motion-design (lucasmaiaesilva's is from 2015). Use instead: https://www.remotion.dev/showcase, https://www.remotion.dev/docs/resources, https://hyperframes.heygen.com/showcase, https://hyperframes.heygen.com/catalog/blocks/data-chart, https://p5js.org/libraries/, https://gl-transitions.com, https://skills.sh, https://github.com/trending?since=weekly, and https://github.com/topics/ + `motion-graphics`, `programmatic-video`, `remotion`, `webcodecs`, `tsl`, `webgpu`, `creative-coding`, `kinetic-typography`, `video-generation`, `agent-skills`.

## How to refresh this list
```bash
gh api rate_limit --jq '.resources | {core:.core.remaining, search:.search.remaining}'   # search = 30 req/min: sleep 2-3 s between searches
# 1. Discover lists and trending repos
gh search repos "awesome motion" --sort stars --limit 30 --json fullName,stargazersCount,pushedAt,description
gh search repos --topic motion-graphics --sort stars --limit 20 "pushed:>2026-03-01" \
  --json fullName,stargazersCount,pushedAt,description --jq '.[] | "\(.fullName)\t\(.stargazersCount)\t\(.pushedAt[:10])"'
# 2. Extract repo links from a list
gh api repos/terkelg/awesome-creative-coding/readme -H "Accept: application/vnd.github.raw" \
  | grep -oE 'github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+' | sed 's#github\.com/##; s#\.git$##' | sort -u > repos.txt
# 3. Verify one repo (releases/latest 404 = no GitHub releases, so check npm)
gh api repos/OWNER/REPO --jq '{stars:.stargazers_count,pushed:.pushed_at,license:.license.spdx_id,archived:.archived}'
gh api repos/OWNER/REPO/releases/latest --jq '{tag:.tag_name,date:.published_at}'
npm view PACKAGE version time.modified
gh api repos/OWNER/REPO/license --jq '.content|@base64d' | head -3        # when spdx_id = NOASSERTION
# 4. Batch-verify repos.txt: 40 repos per GraphQL call (~1 point each). bash 4+; dead repos are skipped (gh exits 1, jq still reads data)
mapfile -t R < <(sort -u repos.txt); for ((i=0;i<${#R[@]};i+=40)); do q="query{"; for ((j=i;j<i+40&&j<${#R[@]};j++)); do
  q+=" r$j: repository(owner:\"${R[$j]%%/*}\",name:\"${R[$j]#*/}\"){nameWithOwner stargazerCount pushedAt isArchived licenseInfo{spdxId} latestRelease{tagName publishedAt}}"; done
  gh api graphql -f query="$q}" 2>/dev/null | jq -r '.data[]|select(.)|[.nameWithOwner,.stargazerCount,.pushedAt[:10],.isArchived,.licenseInfo.spdxId,.latestRelease.tagName,.latestRelease.publishedAt[:10]]|@tsv'; done
# 5. Official skills and llms.txt
gh api "repos/OWNER/REPO/git/trees/HEAD?recursive=1" --jq '.tree[].path | select(endswith("SKILL.md"))'
curl -sL -o /dev/null -w '%{http_code} %{content_type}\n' https://DOCS_DOMAIN/llms.txt   # HTML body = SPA fallback, treat as absent
```
Keep/drop rule: drop if archived or no push in 18 months unless it is still the de-facto standard (mark it "stale"). Flag AGPL, NC and model-community licenses, and check vendor docs for shut-down APIs before pinning model IDs.
