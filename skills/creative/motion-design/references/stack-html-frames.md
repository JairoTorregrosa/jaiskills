# Stack: HTML frames → deterministic video (author in HTML/CSS/SVG/Canvas, seek, screenshot, ffmpeg)

**Verified 2026-09-26** against npm, GitHub and live docs: HyperFrames **0.8.78** (released 2026-09-26, Apache-2.0, [repo](https://github.com/heygen-com/hyperframes)) · GSAP **3.15.0** ("Standard No Charge" license, every plugin free incl. commercial, [gsap.com/licensing](https://gsap.com/licensing/)) · anime.js **4.5.0** · Motion **13.4** (13.0.0 shipped 2026-08-05) · Motion Canvas **3.17.2** (last release 2024-12) · Revideo **0.11.0** (2026-07-10) · Theatre.js **0.7.2** (2024-05) · lottie-web **5.13.0** · dotlottie-web **0.80.0** · @rive-app/canvas **2.43.1** · p5 **2.3.4** · mediabunny **1.60.0** ([mp4-muxer is deprecated](https://github.com/Vanilagy/mp4-muxer) in its favour) · Playwright **1.63.0** (Chromium 153) · Puppeteer **25.12** · ffmpeg **9.0.2**. Anything marked **(tested)** was run for this doc on an Apple M1 Pro with `../examples/gsap-page.html` and `../scripts/render_frames.py`.

## 1. Pick this when

| Tool | Pick when | Seek handle | Status, Sep 2026 | Skip when |
|---|---|---|---|---|
| **HyperFrames** | You want a batteries-included HTML→MP4 CLI with lint, `check`, snapshots, audio/video tracks, captions, a catalog and 21 agent skills | Runtime seeks the paused GSAP timeline at `window.__timelines[id]`; adapters for Lottie, Three.js, anime.js, CSS, WAAPI, TypeGPU | Very active (daily releases), Node ≥ 22 + FFmpeg | You want one self-contained file and a renderer you fully control |
| **GSAP in the page + render_frames.py (§4)** | Kinetic type, SVG logo builds, designed motion graphics under ~1 min | `tl.seek(t)` on one paused master timeline | Active, all plugins free | Particles and simulation (use Canvas) |
| **anime.js v4** ([timeline](https://animejs.com/documentation/timeline)) | Smaller bundle; built-in `splitText`, `morphTo`, `createDrawable`, `createMotionPath`, `createLayout` (FLIP-style layout changes) | `tl.seek(ms)` plus `engine.pause()` (tested) | Active | You need MorphSVG-grade morphs |
| **Motion** ([animate docs](https://motion.dev/docs/animate)) | Porting an existing Motion UI animation | `controls.time = t`, then await two rAFs (tested) | Active (v13) | New timeline work: it is a UI library |
| **Canvas2D / p5.js (hand `render(t)`)** | Particles, generative art, brush looks, per-pixel work | Your own `render(t)`; p5 `noLoop()` + `redraw()` | p5 2.x active | Typography-heavy layouts (the DOM sets type better) |
| **Motion Canvas** ([repo](https://github.com/motion-canvas/motion-canvas)) | Only for legacy projects | Generator time, editor render | Dormant: no feature commits since 2025-02 | New projects (use Revideo) |
| **Revideo** ([repo](https://github.com/redotvideo/revideo)) | TypeScript explainers with generator scenes (`yield* waitFor(.5)`); headless `renderVideo()` with parallel workers | Generator timeline | Maintained by Midrender, 0.11.0 | You want plain HTML/CSS |
| **Theatre.js** ([docs](https://www.theatrejs.com/docs/latest/manual/sequences)) | A human keyframes in the studio UI, then you render | `sheet.sequence.position = t` | Stale since 2024 | Unattended agent work |
| **Lottie / dotLottie** ([dotlottie-web](https://github.com/LottieFiles/dotlottie-web)) | An After Effects or LottieFiles asset has to drop into a scene | `goToAndStop(ms)` / `setFrame(f)` | dotLottie (Rust/WASM) active; lottie-web slow | Authoring from scratch |
| **Rive** | A designer handed you a `.riv` with state machines | Low-level `advance(dt)` stepping only | Active | You need random-access seeking (state machines only step forward) |

Remotion (React, `useCurrentFrame()`) is covered in its own reference.

## 2. The time contract

Every scene is a pure function `render(t) → pixels`: the same `t` must give the same frame in any order, in any worker, on any run. Pin this API in every page:

```js
window.__meta  = { width: 1920, height: 1080, fps: 30, duration: 8 }; // renderer reads it; CLI flags override
window.__ready = build();            // Promise: fonts loaded, text split, timeline built and primed
window.__seek  = t => { /* set every visual for t seconds; may be async; idempotent; any order */ };
// The renderer injects window.__RENDER__ = true before any script runs, so the page skips its preview loop.
```

GSAP skeleton (the tested demo, trimmed):

```js
const mulberry32 = a => () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
Math.random = mulberry32(42);                      // before build: random staggers and plugins get seeded too
gsap.registerPlugin(SplitText, DrawSVGPlugin, MorphSVGPlugin, CustomEase, MotionPathPlugin);
gsap.ticker.lagSmoothing(0);
let tl;
async function build() {
  await Promise.all([document.fonts.load('800 172px "Inter Tight"'), document.fonts.load('500 30px JBM')]);
  await document.fonts.ready;                       // then split: SplitText measures real glyphs
  tl = gsap.timeline({ paused: true });              /* ...tweens at absolute positions... */
  tl.progress(1).progress(0);                        // prime: every tween records its start values now
}
window.__ready = build();
window.__seek = t => { Math.random = mulberry32(1e6 + Math.round(t * 1000)); tl.seek(t); drawFromProxies(t); };
if (!window.__RENDER__) __ready.then(() => { let t0 = null; gsap.ticker.add(s => { t0 ??= s; __seek((s - t0) % DUR); }); });
```

### Adapters: what goes inside `__seek(t)`

| Runtime | Body | Notes |
|---|---|---|
| GSAP | `tl.seek(t)` | [ticker](https://gsap.com/docs/v3/GSAP/gsap.ticker/), [updateRoot](https://gsap.com/docs/v3/GSAP/gsap.updateRoot%28%29/). `seek()` suppresses **all** callbacks, `onUpdate` included (checked in gsap.js 3.15). Do not draw in `onUpdate`: tween proxy objects and draw them after the seek. For code you don't control, `const tl = gsap.exportRoot(); tl.pause()`. Do not use `gsap.updateRoot(t)`: the root timeline has `autoRemoveChildren: true`, so it only plays forward |
| anime.js v4 | `tl.seek(t * 1000)` | `createTimeline({ autoplay: false })` and `engine.pause()` (tested: no drift). Time is in ms unless `engine.timeUnit = 's'` ([engine](https://animejs.com/documentation/engine)) |
| Motion | `a.time = t; await raf(); await raf()` | `a = animate(...); a.pause()`; sequences `animate([[el, kf, opts], ...])`. `raf = () => new Promise(requestAnimationFrame)`. Tested: without the rAF waits the DOM still shows the previous seek. Declarative React `<motion.div animate>` can't be seeked |
| CSS @keyframes / WAAPI | `ANIMS.forEach(a => { a.pause(); a.currentTime = t * 1000 })` | [getAnimations](https://developer.mozilla.org/en-US/docs/Web/API/Document/getAnimations). `const ANIMS = document.getAnimations()` **once**, after ready. `currentTime` includes the delay, and `@property` custom properties seek too (tested). A finished `fill: none` animation drops out of `getAnimations()` (tested), so re-querying each frame loses it |
| Scroll/view timelines | `scroller.scrollTop = f(t); await raf()` | [scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll-driven_animations). Scroll position is the clock. Tested: computed style lags one frame behind the scroll |
| lottie-web | `anim.goToAndStop(t * 1000, false)` | [lottie-web](https://github.com/airbnb/lottie-web). `lottie.loadAnimation({ autoplay: false, renderer: 'svg' })` |
| dotLottie | `dl.setFrame(Math.min(t / dl.duration, 1) * (dl.totalFrames - 1))` | `new DotLottie({ canvas, src, autoplay: false })`. `duration` is in **seconds** per the 0.80 typings; the docs page says ms |
| Rive | step `sm.advance(1/fps); artboard.advance(1/fps); artboard.draw(r)` | `@rive-app/canvas-advanced` ([low-level API](https://rive.app/docs/runtimes/web/low-level-api-usage)). If t goes backwards, rebuild and replay from 0. High-level `scrub()` is deprecated |
| Theatre.js | `sheet.sequence.position = t` | `getProject('P', { state: exportedJson })`, then `await project.ready` |
| p5.js | `T = t; randomSeed(k); noiseSeed(k); redraw()` | Call `noLoop()` and `pixelDensity(1)` in setup. Re-seed per element with a stable key (see below) |
| Three.js / WebGL | `uTime.value = t; mixer.setTime(t); renderer.render(scene, cam)` | Never use `THREE.Clock` or `performance.now()` |
| Canvas2D | `ctx.setTransform(1,0,0,1,0,0); ctx.globalAlpha = 1; draw(t)` | Reset all context state every frame (a minimal `renderAt(t)` renderer from a past production) |
| `<video>` inside | `v.currentTime = t; await new Promise(r => v.addEventListener('seeked', r, { once: true }))` | Better: let HyperFrames own the media, or pre-extract frames with ffmpeg and set `img.src`, then `await img.decode()` |

### Banned constructs

| Banned | Why | Use instead |
|---|---|---|
| rAF loops that advance state; `setTimeout`/`setInterval` choreography | Run on the wall clock, drop frames | State derived from `t` inside `__seek` |
| `Date.now()`, `performance.now()`, `THREE.Clock`, ticker time | Wall clock | `t` |
| CSS `transition:` | Created by a style change and runs on the wall clock, so its state depends on what happened before | `@keyframes` + WAAPI seek, or GSAP |
| Unseeded `Math.random`, `crypto.getRandomValues` | Different per run and per worker | mulberry32, re-seeded per seek from `t`; keyed seeds per element |
| `repeat: -1`, `infinite` without seeking | Infinite duration breaks `progress()` and length | `repeat: Math.max(0, Math.floor(dur / cycle) - 1)` |
| Side effects in `onStart`/`onComplete`/`onUpdate` | Suppressed on seek, or fire only going forward | Tween proxies; read them in `__seek` |
| GSAP ScrambleText, physics integrators, Rive state machines, particle `dt` stepping | Depend on history (tested: 3 seek orders gave 3 different scramble strings) | A closed-form `f(t)` (see `scrambleAt`, §5), or deterministic replay from 0 |
| Network at render time (Google Fonts CSS, CDN scripts, APIs) | Races and flakes | Vendor locally: npm packages, local woff2 |
| Hover, scroll, focus, input state | The renderer sends no input | Map `t` to the state explicitly |

**Randomness that stays still:** one global stream breaks when one element's draw count changes, because every later element then re-rolls (jitter). The music video's `boilSeed(key)` (stack-p5-brush.md) fixes this with FNV-1a over `key + '|' + boilFrame`, calling `randomSeed()` before each element, and holds drawings for `BOIL = 12` fps for hand-drawn "boil". anime.js has a seeded stagger: `stagger(40, { from: 'random', seed: 7 })`. GSAP's `stagger: { from: 'random' }` draws from `Math.random` at build time, so seed it before `build()`.

## 3. Capture approaches

| Approach | Captures | Deterministic | Use when |
|---|---|---|---|
| `__seek` + CDP `Page.captureScreenshot` (render_frames.py) | DOM, SVG, Canvas, WebGL (no `preserveDrawingBuffer` needed, tested) | Yes | Default |
| HyperFrames BeginFrame | Same; one atomic compositor frame via [`HeadlessExperimental.beginFrame`](https://chromedevtools.github.io/devtools-protocol/tot/HeadlessExperimental/) (needs chrome-headless-shell), falling back to screenshots | Yes | Using HyperFrames. Read the render summary's second line: `beginframe` vs `screenshot`, GPU mode |
| Playwright `page.clock` | Pages you can't edit: `install(time=0)` before `goto`, `pause_at(...)`, then `run_for(1000//fps)` per frame. Covers Date, timers, rAF (16 ms steps, tested), `performance.now` ([docs](https://playwright.dev/docs/clock)) | Forward-only | Legacy autoplay pages. It does **not** move CSS/WAAPI animations (tested), so add the `getAnimations()` seek |
| CDP [`Emulation.setVirtualTimePolicy`](https://chromedevtools.github.io/devtools-protocol/tot/Emulation/#method-setVirtualTimePolicy) | Experimental virtual-time budget (`advance`/`pause`/`pauseIfNetworkFetchesPending`) | Fragile | Don't adopt. [timecut](https://github.com/tungs/timecut)/timesnap (Puppeteer + in-page time overrides) have had no release since 2022 |
| In-page WebCodecs + mediabunny | Canvas/WebGL only: `new CanvasSource(canvas, { codec: 'avc', quality: QUALITY_HIGH })`, `await src.add(i/fps, 1/fps)`, `output.finalize()` ([docs](https://mediabunny.dev/guide/media-sources)) | Yes | No ffmpeg (in the user's browser), or big pure-canvas pieces |
| `canvas.toDataURL()` per frame | One canvas | Yes | Canvas-only scenes. WebGL gives black without `preserveDrawingBuffer: true` (tested); JS-side PNG encoding is slow |

Measured capture cost per frame on the demo (tested, M1 Pro, headless shell):

| Output | CDP JPEG q95 | CDP PNG + `optimizeForSpeed` | Playwright `page.screenshot()` PNG |
|---|---|---|---|
| 1280×720 (dsf 1) | 32 ms | 51 ms | 204 ms |
| 1920×1080 (dsf 1.5) | 51 ms | 123 ms | 489 ms |
| 2560×1440 (dsf 2) | 70 ms | 207 ms | 914 ms |

End to end, 90 frames at 720p: **4.1 s** wall with 1 worker (about 1.3 s of that is browser start), **2.9 s** with 3 workers.

## 4. Reference renderer: `scripts/render_frames.py` (tested)

Python + Playwright + ffmpeg, runnable directly (`scripts/render_frames.py`, or `uv run`) thanks to PEP 723 inline dependencies. It pipes JPEG (or PNG) frames into ffmpeg with `-f image2pipe`, converts with the BT.709 matrix and tags the stream, splits frame ranges across worker processes and concats the segments losslessly, and has contact sheets, stills, alpha output and audio muxing.

```bash
scripts/render_frames.py scene.html --out out/v01.mp4 --fps 30 --duration 6 --gpu      # add --workers 3 for >20 s pieces
scripts/render_frames.py scene.html --sheet 0,0.5,1,2,4 --out qa/sheet.png             # a:b = every frame in a:b
scripts/render_frames.py scene.html --stills 0 --scale 2 --out qa/stills/              # t=0 is the poster
scripts/render_frames.py scene.html --transparent --out overlay.mov                    # ProRes 4444 (.webm = VP9 alpha)
scripts/render_frames.py scene.html --range 12:15 --audio mix.wav --out qa/scene3.mp4   # audio cut to the same range
```

**Test results (2026-09-26):** `examples/gsap-page.html` is a 1280×720, 3 s GSAP 3.15 piece that exercises SplitText (masked chars, stagger from center then edges, CustomEase), DrawSVG, MorphSVG, MotionPath, a variable-font `fontWeight` tween and a seek-safe scramble. It rendered to `demo-720p.mp4`, and ffprobe reports `h264 High, 1280x720, yuv420p, 30/1, nb_frames=90, duration=3.000000, color bt709/bt709/bt709 tv`. The other modes passed too:
- `--workers 3`: min PSNR vs 1 worker is 49.6 dB (encoder-only differences). The file is 486 KB vs 260 KB, because each segment restarts the GOP and rate control, so use workers for renders over ~20 s.
- `--scale 1.5 --range 1:2`: 1920×1080, 30 frames.
- `--stills 0 --scale 2`: 2560×1440 PNG.
- `--transparent`: `.mov` gives ProRes 4444 `yuva444p12le` (15 MB for 3 s); `.webm` gives VP9 with `alpha_mode=1`. In both, a corner pixel has alpha 0 and the logo pixel is `D97757` at alpha 255.
- `--audio`: h264 + AAC, 3.000 s.
- `--sheet`: the cell labels match the page's own timecode on every cell, so no frame is stale.
- Colour: the `#D97757` swatch decodes to `216,119,87` (PNG capture) and `216,119,85` (JPEG q95). A naive `ffmpeg -pix_fmt yuv420p` decodes to **`225,127,83`** in BT.709 players.

**Kept from past productions, and what render_frames.py adds:** a minimal canvas renderer had `window.ready` (fonts, then `renderAt(0)`), sync `renderAt(t)`, a seeded Park–Miller RNG, a preview loop gated on `navigator.webdriver`, and canvas `toDataURL` PNG piped to ffmpeg (CRF 16, `slow`). The p5.brush music video's `render.mjs` had async `renderAt(t, type, q)`, an in-page `renderSheet` with `--crop` and `--crop-at` (a crop that follows a world point through the camera), `--strip a:b` (every frame), resumable atomic JPEG frames that workers pull from a shared queue, audio `-ss/-t` cut to the range, a per-platform ANGLE flag table, `gpu_probe.mjs`, `?render` to skip the dev UI, and `protocolTimeout: 0`. render_frames.py adds four things:
- DOM capture through the compositor, so any HTML works, not just one canvas.
- An explicit `__RENDER__` flag instead of the `navigator.webdriver` heuristic.
- Tagged BT.709 output.
- DPR supersampling done correctly.

For multi-minute or seconds-per-frame renders (p5.brush watercolour), use `--frames-dir DIR` instead of segments: frames are written one file each with an atomic rename, existing frames are skipped on the next run, and a crash loses one frame, not a segment.

## 5. GSAP recipes for motion graphics (all seek-safe; plugins are in the npm `gsap` package, `dist/*.min.js`)

- **Setup.** `gsap.registerPlugin(SplitText, MorphSVGPlugin, DrawSVGPlugin, Flip, CustomEase, CustomBounce, MotionPathPlugin)`, then `gsap.ticker.lagSmoothing(0)`. Build one `gsap.timeline({ paused: true })` with **absolute** positions (`tl.to(x, {...}, 1.25)`), then prime it with `tl.progress(1).progress(0)`.
- **Kinetic type, chars** ([SplitText](https://gsap.com/docs/v3/Plugins/SplitText/), rewritten in 3.13). Split after fonts load:
  `const s = SplitText.create("#title", { type: "chars,words", mask: "chars" });`
  `tl.from(s.chars, { yPercent: 110, duration: .6, ease: "snap", stagger: { each: .035, from: "center" } }, .2);`
  Staggers take `from: "center" | "edges" | "end" | "random" | index`, plus `grid: "auto"` and `axis: "x"` for 2D fields.
- **Line reveal.** `SplitText.create(p, { type: "lines", mask: "lines" })`, then `tl.from(s.lines, { yPercent: 100, stagger: .1 }, 0)` (tested: 3 lines, reversible). `autoSplit: true` re-splits on resize or font load; with it, return the animation from `onSplit`. For video, prefer a fixed viewport, fonts awaited before splitting, and `autoSplit: false`.
- **Word pops.** `tl.from(s.words, { scale: 0, rotation: () => gsap.utils.random(-12, 12), ease: "back.out(2.2)", stagger: .06 }, t)`. `utils.random` uses `Math.random`, which is seeded.
- **MorphSVG logo build** ([docs](https://gsap.com/docs/v3/Plugins/MorphSVGPlugin/)). `MorphSVGPlugin.convertToPath("circle, rect, polygon")`, then `tl.to("#mark", { morphSVG: { shape: "#final", shapeIndex: "auto", type: "rotational" }, duration: 1, ease: "expo.inOut" }, t)`. Build the logo from primitives: morph blobs into letterforms, stagger the parts, and finish on the exact brand path.
- **DrawSVG reveals** ([docs](https://gsap.com/docs/v3/Plugins/DrawSVGPlugin/)). Draw from the start: `tl.fromTo(path, { drawSVG: "0%" }, { drawSVG: "100%", duration: 1, ease: "power2.inOut" }, t)`. Grow from the centre: `{ drawSVG: "50% 50%" } → "0% 100%"`. Travelling dash: `tl.fromTo(path, { drawSVG: "0% 10%" }, { drawSVG: "90% 100%" }, t)`. Add `vector-effect="non-scaling-stroke"` when the SVG scales.
- **CustomEase / bounce.** `CustomEase.create("snap", "M0,0 C0.12,0 0.2,1.12 0.46,1.04 0.7,0.97 0.82,1 1,1")`. Then `CustomBounce.create("hop", { strength: .6, squash: 2 })` registers both `"hop"` and `"hop-squash"`: tween `y` with `hop` and `scaleY` with `hop-squash` over the same span (tested).
- **Flip layout transitions** ([docs](https://gsap.com/docs/v3/Plugins/Flip/)). Record the state, change the layout **at build time**, then nest the returned timeline:
  `const st = Flip.getState(".card"); grid.classList.add("row");`
  `tl.add(Flip.from(st, { duration: .8, ease: "power2.inOut", absolute: true, stagger: .04 }), 2)`
  Tested: the positions interpolate and reverse on seek. Never call Flip inside `__seek`.
- **Scramble / decode text.** GSAP ScrambleText is history-dependent (tested). Its chars `<>&` also show up as half-decoded HTML entities such as `lt;`. Use a pure helper instead:
  ```js
  const hash = (a, b) => { let h = Math.imul(a ^ 0x9E3779B9, 0x85EBCA6B) ^ Math.imul(b + 0x632BE5AB, 0xC2B2AE35); h ^= h >>> 15; return h >>> 0; };
  function scrambleAt(el, from, to, t, t0, dur, pool = "01/#*+=", hz = 24) { if (t < t0) return void (el.textContent = from);
    const n = Math.round(Math.min((t - t0) / dur, 1) * to.length), k = Math.floor(t * hz);
    el.textContent = to.slice(0, n) + [...to.slice(n)].map((c, i) => c === " " ? " " : pool[hash(i, k) % pool.length]).join(""); }
  ```
- **Counters.** `tl.to("#n", { innerText: 1250, snap: { innerText: 1 }, duration: 1.2, ease: "power1.out" }, t)` (tested). Use `font-variant-numeric: tabular-nums` so the digits don't wobble.
- **MotionPath object** ([docs](https://gsap.com/docs/v3/Plugins/MotionPathPlugin/)). `tl.to("#dot", { motionPath: { path: "#route", align: "#route", alignOrigin: [.5, .5], autoRotate: true }, duration: 1.4 }, t)`. `gsap.set` the object at the path start first, so frame 0 isn't at (0, 0).
- **Camera moves.** Move the world, not a camera. Tween a proxy along a curve and apply its inverse in `__seek` (tested; set `transform-origin` to the focus point):
  ```js
  const cam = { x: 0, y: 0, s: 1 };
  tl.to(cam, { motionPath: { path: [{x:0,y:0},{x:400,y:-100},{x:900,y:50}], curviness: 1.2 }, s: 1.5, duration: 2, ease: "power2.inOut" }, 0);
  // in __seek, after tl.seek(t):
  world.style.transform = `translate(${-cam.x}px, ${-cam.y}px) scale(${cam.s})`;
  ```
- **Variable-font axes.** `tl.to("#title", { fontWeight: 300, yoyo: true, repeat: 1 }, t)` (tested), or animate `"--wdth"` on an `@property`-registered property used in `font-variation-settings: "wdth" var(--wdth)`. Weight and width change glyph advances, so animate a whole centred line or give each char a fixed-width box, or neighbours will jitter.
- **Houdini [`@property`](https://developer.mozilla.org/en-US/docs/Web/CSS/@property).** `@property --p { syntax: '<number>'; inherits: false; initial-value: 0 }` makes custom properties interpolate: gradient stops, conic "progress rings", hue. GSAP tweens them via `tl.to(el, { "--p": 1 })`, and WAAPI seeks them (tested).
- **SVG morph without GSAP.** [flubber](https://github.com/veltman/flubber) 0.4.2 (unmaintained since 2022, still works): `const f = flubber.interpolate(a, b, { maxSegmentLength: 4 }); path.setAttribute("d", f(ease(p)))`. anime.js v4 has `morphTo(target)`.

## 6. Pitfalls and fixes

1. **FOUT or fallback font in frame 0** ([`FontFaceSet.load`](https://developer.mozilla.org/en-US/docs/Web/API/FontFaceSet/load)). `document.fonts.ready` can resolve before an unused face has started loading. Fix: `await document.fonts.load('800 172px "Face"')` for every face and weight, then `fonts.ready`. Use `font-display: block` and local woff2 files (tested).
2. **Text split before fonts load** measures the fallback metrics, so lines break in the wrong places. Split after step 1 and keep `autoSplit: false`.
3. **ES modules over `file://`** are blocked by CORS (tested: "Cross origin requests are only supported for... http, https"). Fix: `--allow-file-access-from-files` (render_frames.py sets it), a local `python3 -m http.server`, or UMD/IIFE builds.
4. **Colour shift.** ffmpeg's default RGB→YUV uses the BT.601 matrix and leaves the stream untagged, but players decode HD as BT.709: `#D97757` came out `225,127,83` (tested). Fix: `scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv`. The `-color_*` output flags alone left primaries and transfer `unknown` on ffmpeg 9 (tested).
5. **Chrome colour management.** A display profile leaks into captures. Launch with `--force-color-profile=srgb`.
6. **DPR ignored.** Raw CDP `Page.captureScreenshot` under Playwright returns **CSS-pixel** frames even with `device_scale_factor=2` (tested: 1280×720). Pass `clip: {x:0, y:0, width, height, scale: dsf}`. For 4K, author at 1920×1080 CSS with `--scale 2`: crisp text and SVG for about 4× the cost per frame.
7. **Headless GPU is off** ([Chrome headless](https://developer.chrome.com/docs/chromium/headless): the old mode ships only as `chrome-headless-shell` since Chrome 132). Playwright's default headless shell uses **SwiftShader** (software) WebGL; with `--use-angle=metal` it gets `ANGLE Metal Renderer: Apple M1 Pro`. New headless (`channel="chromium"`) uses Metal by default (tested). On Linux + NVIDIA use `--use-angle=vulkan` (render.mjs, gpu_probe.mjs). Always log `UNMASKED_RENDERER_WEBGL` once.
8. **WebGL readback.** `toDataURL`/`readPixels` in a later task returns black unless the context has `preserveDrawingBuffer: true`. CDP screenshots don't need it (tested).
9. **Not bit-exact across seek orders.** Chromium partially re-rasterises damaged tiles, so the same `t` reached from another order can differ by ≤5 levels on a few AA pixels (tested: 35 px, PSNR 89 dB). The same order is bit-identical run to run. Check determinism with a tolerance (PSNR > 50 dB), not md5.
10. **First render differs from a revisit.** MorphSVG converts to cubics and DrawSVG writes `480px, 0.1px`, so frame 0 differs after a jump. Prime with `tl.progress(1).progress(0)`.
11. **`from()`/`fromTo()`/`startAt` render immediately** at build time and can overwrite the poster state. Put later from-tweens on the same property with `immediateRender: false`, or use `.to()` + `startAt` after priming. Check frame 0 in a sheet.
12. **CSS `transform` plus a GSAP transform on the same node** fight each other (HyperFrames lint `gsap_css_transform_conflict`). Centre with flex/inset, and set start states in `fromTo` or with `xPercent`/`yPercent`.
13. **Transforms on inline elements** do nothing. Transformed elements must be `inline-block`/`block` with a real size. SplitText output already is.
14. **Subpixel jitter.** Slow drifts on text shimmer as the glyphs re-rasterise at subpixel offsets. Animate `transform` and `opacity` (not `left`/`top`), add `will-change: transform` for the move's duration (it promotes to a layer: smooth, slightly softer), or snap slow translations to whole device pixels: `modifiers: { x: gsap.utils.snap(1 / dsf), y: gsap.utils.snap(1 / dsf) }`.
15. **8-bit banding** in dark radial gradients gets worse after yuv420p. Overlay static grain (`feTurbulence` at opacity 0.04–0.08, or a noise PNG), keep CRF ≤ 18, and use `-tune grain` for heavy grain. Static grain is deterministic; seed animated grain from `t`.
16. **`backdrop-filter` / big `filter: blur()`** are the most expensive CSS features per frame; check the ms/frame in a quick `--range` test. Pre-blur to an image, blur a scaled-down layer, or bake with a canvas `ctx.filter`.
17. **Stray real-time motion between seek and capture.** A preview loop, the GSAP ticker driving a non-timeline tween, or CSS transitions can move pixels. Gate previews on `!window.__RENDER__`, put every tween in the master timeline, and ban `transition:`.
18. **Odd frame sizes.** libx264 with yuv420p needs even width and height (width × scale must come out even), so keep sizes even. Most social platforms want ≤ 3840×2160.
19. **Transparent capture renders black.** Both are required: `Emulation.setDefaultBackgroundColorOverride({a:0})` (or `omit_background`) **and** a transparent page (`html, body, #stage { background: transparent }`), PNG capture, and ProRes 4444 (`yuva444p10le`) or VP9 `yuva420p`. H.264 has no alpha.
20. **Worker seams.** Anything history-dependent (ScrambleText, physics, Rive SMs) comes out different at each worker's first frame. Make it closed-form or run 1 worker.
21. **Long pages time out.** Set Puppeteer `protocolTimeout: 0` (render.mjs), and in Playwright pass `timeout=0` to heavy `evaluate` waits. Watch `pageerror`: a thrown `__seek` otherwise just freezes frames.

## 7. Frame 0 = thumbnail

Most feeds and messengers (X, LinkedIn, WhatsApp, iMessage, Slack previews) show the **first decoded frame** as the poster before play, and most ignore MP4 cover-art atoms. So frame 0 must be a finished, legible, on-brand composition: the hero title set, the logo whole, the key visual in place. It must never be black, never a fade-in from nothing, never a half-split word.
- Author the poster state as the static HTML and CSS (the "visible end state" from HyperFrames' layout contract), then animate **away from and back to** it: exit at 0.15 s, rebuild by 0.6–1.2 s. The tested demo shows the complete title, logo, underline and subtitle at t=0, and the first motion starts at 0.15 s.
- Only `.to()` tweens with a positive start and `startAt` should move things away from the poster. Park path-driven objects at the path start (`gsap.set('#dot', {x, y})`). Prime the timeline.
- Fades live on the **last** frames, not the first. For loops, make the last frame flow into frame 0.
- Verify every render: `uv run render_frames.py scene.html --stills 0 --out stills/` (or `ffmpeg -i out.mp4 -frames:v 1 thumb.png`), then look at it next to a 12-cell `--sheet`. A 4-point check: legible at 20 % size, contrast, safe margins, no mid-motion blur.
- HyperFrames: make the first frame a composed state (clips with `data-start="0"`) and check it with `npx hyperframes snapshot --at 0`.

## 8. HyperFrames quick reference (v0.8.78)

`npx hyperframes init my-video && cd my-video && npx hyperframes preview` gives a Studio with live reload. The loop is `npx hyperframes check` (lint, runtime, layout, motion and contrast in one pass), then `npx hyperframes snapshot --at 1,2.5,4`, then `npx hyperframes render --quality draft|looks|delivery --output out.mp4`.
- **Composition.** Root `<div data-composition-id="launch" data-width="1920" data-height="1080" data-duration="6">`. Timed children take `class="clip"` + `data-start` + `data-duration` + `data-track-index` (the track index is a Studio lane, not z-order). Register one `gsap.timeline({ paused: true })` at `window.__timelines["launch"]` **after** an async build. The root `data-duration` fixes the length at compile time.
- **Render flags** ([reference](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes-cli/references/preview-render.md)). `--fps 24|30|60`. `--format mp4|webm|mov|gif|png-sequence|hls` (webm and mov keep alpha). `--resolution 4k` supersamples via `deviceScaleFactor`. `--crf` or `--video-bitrate`. `--workers auto` (about 256 MB of Chrome each). `--gpu` means hardware *encode* (VideoToolbox/NVENC). `--docker` gives reproducible renders. `--hdr`.
- **Rules its linter enforces** ([determinism rules](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes-core/references/determinism-rules.md)). No `repeat: -1` (use `floor`); no `Date.now`/`performance.now`/unseeded random; never tween `visibility`/`display`/`autoAlpha` on a `.clip`; every `<audio>` needs an `id`; no `crossorigin` on media; every named font needs an in-file `@font-face` to a local file.
- **Agent skills.** `npx skills add heygen-com/hyperframes` (interactive picker; the "Core Skills" group is enough) or `npx hyperframes skills update` (non-interactive core set). There are 21 published skills: a `/hyperframes` router, `/motion-graphics`, `/product-launch-video`, `/music-to-video`, `/hyperframes-core`, `/hyperframes-animation`, `/hyperframes-keyframes` and more ([README](https://github.com/heygen-com/hyperframes#skills)).
- **Porting.** A render_frames.py-style page ports easily: move `__seek` logic into the registered timeline, or write a frame adapter; `/remotion-to-hyperframes` handles Remotion sources.
