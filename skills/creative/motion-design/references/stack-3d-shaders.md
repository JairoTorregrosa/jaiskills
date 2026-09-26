# 3D, GPU, shaders and Blender for short videos

Verified 2026-09-26 against GitHub releases, npm dist-tags, library source and official docs. Tests ran on an M1 Pro
under macOS 27.
- three.js **r186** (2026-09-24; npm `three@0.186.1`). R3F **9.8.1** (v10 is at `10.0.0-alpha.5`, WebGPU-first:
  https://github.com/pmndrs/react-three-fiber/releases).
  drei **10.7.9** (11 is alpha). `@react-three/postprocessing` **3.1.2** / `postprocessing` **6.39.5** are WebGL only.
  `postprocessing` v7 is still a beta pinned to three <0.184.
- Remotion **4.0.529**. `@remotion/three` ships `<ThreeCanvas>` plus `<ThreeWebGPUCanvas>` (added in 4.0.503).
- Splats: Spark **2.2.0** (`@sparkjsdev/spark`, three ≥0.180, WebGL2), three r186 `GaussianSplat` addon, PlayCanvas
  engine **2.22.4**, SuperSplat **3.4.2** and `@playcanvas/splat-transform` **3.6.6**. Stale: GaussianSplats3D 0.4.7 (last
  release Jan 2025), gsplat.js 1.2.9 (Jul 2025) and `@lumaai/luma-web` 0.2.2 (last publish Mar 2024).
- Blender **5.2.1 LTS** (tested locally; notes https://developer.blender.org/docs/release_notes/5.2/). Blender Lab MCP
  **v1.0.0** (https://projects.blender.org/lab/blender_mcp). ffmpeg **9.0.2**.

Tested and working: a Remotion `<ThreeWebGPUCanvas>` scene that combines a TSL compute kernel, 60k sprites, domain
warp, bloom and IGN dither (template in `../examples/remotion-webgpu-tsl-scene.tsx`). Blender EEVEE and Cycles-Metal headless renders
(skeleton in `../scripts/blender_mg_render.py`).

---

## 1. When 3D earns its place (and when it is a distraction)

**Use 3D when depth carries meaning**: data with a real third axis, or thousands of items that must regroup (particles
morphing between layouts); an object the viewer needs to turn around; parallax that sells scale (city, map, network); a
reveal 2D cannot stage (fly-through, pull-out to the whole).
**Skip it** when the message is one sentence plus a number (kinetic type wins), when the 3D only adds a slow logo orbit,
when you can't light and grade it (unlit defaults look cheap next to flat design), when it needs >2 s of spin-up before
the first idea lands, or when the feed shows it 360 px wide (fine detail turns to mush after the platform re-encode).

Rule of thumb: 3D should hold at most 1–2 hero shots per 30 s video. The type and the numbers stay 2D overlays, pinned
to 3D points with `project()` (see §5).

| Need | Pick | Why |
|---|---|---|
| Frame-exact 3D inside a Remotion edit with type/audio | **Remotion + `@remotion/three`** (`<ThreeCanvas>` WebGL, or `<ThreeWebGPUCanvas>` for TSL/compute) | Same timeline and props. Frame-driven. Concurrency-safe (verified byte-identical across tabs) |
| Custom shader or particle look, full control, no React | **three.js r186** plus a manual frame-step harness (Playwright) | Least overhead. You own capture |
| Declarative scenes, drei helpers, GLTF models | **R3F 9.8 + drei 10** (inside Remotion for video) | Ecosystem. Beware helpers that read the clock (§9) |
| Photoreal product, cloth, glass, GI, true motion blur/DOF | **Blender 5.2 headless** (EEVEE for speed, Cycles for glass/caustics) | Offline quality. PNG sequence goes into the edit |
| Procedural mograph (arrays, audio-reactive, text templates) | **Blender Geometry Nodes** (5.2 adds a *Sample Sound Frequencies* node; 5.1 exposes *String to Curves* inputs as sockets; https://developer.blender.org/docs/release_notes/5.2/geometry_nodes/) | Node-driven, deterministic per frame |
| 2D line art in 3D space (hand-drawn arrows, write-ons) | **Blender Grease Pencil v3** | Build modifier gives write-ons |
| Real captured place or object with a camera move | **Gaussian splats** (three `GaussianSplat` or Spark 2) | Photoreal at low cost. Keep moves slow (§2.4) |

---

## 2. Stack reference

### 2.1 three.js r186: WebGPURenderer, TSL, compute, post
- `import * as THREE from 'three/webgpu'` and `import {...} from 'three/tsl'`. `WebGPURenderer` falls back to a WebGL2
  backend automatically; `forceWebGL: true` forces the fallback. The manual still calls the renderer "experimental",
  though much more mature than before (https://threejs.org/manual/#en/webgpurenderer). `ShaderMaterial`,
  `onBeforeCompile` and `EffectComposer` do **not** work with it. Port them to node materials, TSL and `RenderPipeline`.
- Init is async: call `await renderer.init()` before your first manual `render()` or `compute()`. Offline or
  deterministic capture: `await renderer.renderAsync(scene, cam)`, then `await device.queue.onSubmittedWorkDone()`.
  Readback: `await renderer.readRenderTargetPixelsAsync(rt, 0, 0, w, h)`.
- `PostProcessing` was **renamed to `RenderPipeline` in r183** (the old name warns). `Clock` was replaced by `Timer`
  (r183, https://github.com/mrdoob/three.js/releases/tag/r183). r186 added `SunLight` (cascaded shadows), a native `GaussianSplat`, `DirectRenderPipeline` and the TSL Guide
  (https://github.com/mrdoob/three.js/releases/tag/r186).
- TSL basics. Node materials (`MeshStandardNodeMaterial`, `MeshBasicNodeMaterial`, `SpriteNodeMaterial`) expose these
  slots: `colorNode`, `positionNode`, `opacityNode`, `emissiveNode`, `scaleNode`. Wrap functions in `Fn(() => …)`. Use
  `uniform(v)` for per-frame values (set `.value`). Noise helpers: `mx_fractal_noise_float(p, octaves)`,
  `mx_noise_float`, `mx_worley_noise_float`, `hash(i)`, `interleavedGradientNoise(px)`. Pixel position:
  `screenCoordinate`; `screenUV` for UVs. For raw shader code, use `wgslFn`/`glslFn`.
- Compute particles: `const pos = instancedArray(N, 'vec3')`, then
  `Fn(() => { pos.element(instanceIndex).assign(...) })().compute(N)`. Run it per frame with `renderer.compute(k)`.
  Draw with `new THREE.Sprite(spriteNodeMaterial)`, `sprite.count = N`, `material.positionNode = pos.toAttribute()`,
  `opacityNode = shapeCircle()` (https://threejs.org/examples/webgpu_compute_particles.html). Tested at 60k sprites.
- Post (TSL display nodes in `three/addons/tsl/display/`, entry `pass(scene, cam)`): `bloom(node, strength, radius,
  threshold)`, `dof(color, pass.getViewZNode(), focusDist, focalLen, bokehScale)`, `motionBlur(color, velocityTex,
  int(samples))` with `pass.setMRT(mrt({output, velocity}))`, `film(node, intensity, uvNode)`,
  `chromaticAberration(node, strength, center, scale)`, `lut3D(node, lut, size, i)`, plus FXAA/SMAA/TRAA, GTAO, SSR,
  SSGI, `LensflareNode`, `GodraysNode`.
- **The TSL `time` / `deltaTime` nodes and the default `oscSine()` read `performance.now()`.** `FilmNode` seeds its noise
  with `time`. Never use any of them for video: pass your own `uniform(frame / fps)` and feed `film()` a frame-seeded
  `uvNode`. Test result: the same frame rendered twice with `time` produced different SHA-1s; with `uniform(frame/fps)`
  the SHA-1s matched.
- GLTF: `GLTFLoader` plus `DRACOLoader`/`KTX2Loader`/`MeshoptDecoder`. Animations: never `mixer.update(delta)`; call
  `mixer.setTime(frame / fps)` every frame. Loading goes inside `delayRender` or Suspense (`@remotion/three` wraps
  Suspense).
- Color management: textures holding color get `tex.colorSpace = THREE.SRGBColorSpace`; data maps stay
  `NoColorSpace`. Keep `renderer.outputColorSpace = SRGBColorSpace`. Constants: `NeutralToneMapping` (7),
  `AgXToneMapping` (6), `ACESFilmicToneMapping` (4). three's default is `NoToneMapping`. R3F defaults to ACES, and
  `flat` switches it to None. Choice guidance is in §7.
- WebGL canvas capture: `gl={{preserveDrawingBuffer: true}}` whenever anything reads the canvas outside the render task
  (`toDataURL`, `drawImage`, screenshots). WebGPU has no such flag. Capture via Remotion's `<ThreeWebGPUCanvas>` (it
  awaits `onSubmittedWorkDone`) or read back a render target.

### 2.2 R3F 9 / drei / postprocessing (and in Remotion)
- R3F WebGPU: `gl={async (props) => { const r = new THREE.WebGPURenderer(props); await r.init(); return r }}`, plus
  `extend(THREE)` for node-material JSX (https://r3f.docs.pmnd.rs/api/canvas#webgpu). 9.8 configures roots
  synchronously and gates rendering on async renderers.
- **Frame→time, never clock→time.** Compute every animated value from `useCurrentFrame()` (Remotion) or your own frame
  counter. `useFrame((s, delta) => …)` may only *render* (priority ≥ 1). It must never advance state.
- During a render, `<ThreeCanvas>` forces `frameloop="never"` and calls `advance()` once per frame. If you update a
  texture asynchronously, call `advance(performance.now())` yourself, not `invalidate()`
  (https://www.remotion.dev/docs/three-canvas). Inside the canvas use `<Sequence layout="none">`.
- `<ThreeWebGPUCanvas>` (import from `@remotion/three/webgpu`) needs three ≥0.167, R3F ≥9 and React 19. It accepts
  every `ThreeCanvas` prop except `gl` (https://www.remotion.dev/docs/three-webgpu-canvas). Remotion 4 needs `--gl=angle`.
  The docs say ANGLE becomes the default in Remotion 5, which is not released yet. Tested: headless Chrome on macOS with
  `--gl=angle` ran the **real WebGPU backend**, not the fallback. The pattern that worked:
  ```tsx
  sim.uT.value = frame / fps; post.uFrame.value = frame;            // in render body: pure
  useFrame(() => { renderer.compute(sim.kernel); post.pipeline.render(); }, 1); // priority 1 = you render
  ```
- WebGL post in Remotion: build the `postprocessing` `EffectComposer` **synchronously** in `useMemo` (the JSX
  `<EffectComposer>` creates it in an effect, so the first captured frame per tab can miss post). Render it in
  `useFrame(…, 1)` and hold a `delayRender` until that callback has run for the current frame. Proven in the data documentary's particle engine.
- Video textures: `useOffthreadVideoTexture()` gives the exact frame during rendering.
- These drei helpers read `clock`/`delta`/`Math.random` and are not deterministic in renders: `Float`, `Sparkles`, `Stars`,
  `CameraShake`, `Cloud`, `MeshDistortMaterial`, `MeshWobbleMaterial`. Also `useAnimations`, which calls
  `mixer.update(delta)`. Re-implement them from frame, or seed and drive their props.

### 2.3 Remotion GPU checklist
Put `Config.setChromiumOpenGlRenderer('angle')` in `remotion.config.ts`. Log the unmasked renderer once per tab: you want
"ANGLE Metal", not SwiftShader. the data documentary measured 80 ms/frame with ANGLE against 170 ms/frame with swangle.
`npx remotion gpu` inspects support (https://www.remotion.dev/docs/cli/gpu). For concurrency, benchmark 4–6 on M-series chips: Chrome capture is the floor, and
the GPU work is only a few ms.

### 2.4 Gaussian splats: usable for video, with conditions
- **three r186 `GaussianSplat`** (`three/addons/objects/GaussianSplat.js`; loaders `GaussianSplatPLYLoader`,
  `SPLATLoader`, `KSPLATLoader`, glTF extension with SH). Needs `WebGPURenderer` (the WebGL2 fallback is OK). It runs a
  GPU counting sort in `onBeforeRender`, so each render comes out sorted with no async lag. Best fit for Remotion
  `<ThreeWebGPUCanvas>`.
- **Spark 2.2** (World Labs, WebGL2 `WebGLRenderer`). Loads `.ply/.spz/.sog/.splat/.ksplat/.rad`, supports LoD streaming,
  and provides "dyno" shader effects. Its sort runs in workers, which is asynchronous. For offline frames call
  `await spark.update({scene})` before rendering, or wire `onDirty` to hold a `delayRender`. Disable paged/LoD streaming
  (load the whole file) so every tab sees the same splats (https://sparkjs.dev/docs/spark-renderer/).
- PlayCanvas and SuperSplat handle editing and cleanup. `splat-transform` converts PLY ↔ SOG/SPZ/compressed PLY
  (https://github.com/playcanvas/splat-transform).
- Video rules: keep camera moves slow (less than about 5° or 0.3 m of change per frame). Stay inside the captured
  viewpoints, because splats smear off-axis. Give a clean background plate or fog to hide floaters. Crop tight.
  `@lumaai/luma-web` has had no publish since March 2024; don't build on it.

---

## 3. Deterministic rendering rules (GPU scenes)
1. **Every pixel is a pure function of `frame`.** Set `t = frame / fps`; all uniforms, camera state and post seeds derive
   from it. Wall-clock time must never enter: no `Date`, no `performance.now()` math, no `Clock`/`Timer`, no TSL `time`,
   no R3F `delta`.
2. **Seeded randomness only.** Use a hash of `(index, salt)` (lowbias32, PCG) or a seeded stream such as mulberry32,
   run once at module scope. In shaders, `hash(instanceIndex)` works; do not hash anything time-derived that isn't
   `frame`. Ban `Math.random()` in lint.
3. **Prefer stateless simulation**: `pos = f(p0, t)`, meaning closed-form paths, noise offsets and curl displacement.
   Any frame renders in any order, in any tab. Tested: frame 30 from a 4-tab sequence render was byte-identical to a
   standalone still.
4. **If you need state** (true advection, springs, collisions): use a fixed `dt = 1/fps` (or 1/(fps·k) substeps).
   Either (a) **bake**: pre-simulate to a cache (Float32Array per frame, a texture atlas, or Alembic/VDB/point cache in
   Blender) and sample it by frame; or (b) **pre-roll**: each tab re-simulates from frame 0 up to its first frame
   before capture. Cache per tab with memoization. Never integrate with the real frame delta.
5. **Temporal effects need history.** Velocity-buffer motion blur, TRAA/TAA and temporal denoisers break on each tab's
   first frame and on seeks. Render frame−1 silently first, or use sub-frame accumulation (`<CameraMotionBlur>`,
   https://www.remotion.dev/docs/motion-blur/camera-motion-blur; Blender motion blur), or skip them.
6. **Hold the capture until the GPU is done**: `delayRender` → render this frame → `continueRender`. For WebGPU, await
   `onSubmittedWorkDone`. Frame 0 and each tab's first frame are where post and loaders go missing.
7. **Stable identities**: layouts, masks and keyframe arrays live at module scope or in `useMemo`. New arrays every
   frame defeat caches and re-upload buffers.
8. **Verify**: render the same frame twice as stills, and once inside a concurrent render. Then compare
   `shasum`/`magick compare -metric AE` and expect 0. Sanity check that frame N and N+1 differ.

---

## 4. Camera language for 3D motion graphics
- **One move per shot.** Push-in, pull-out, lateral truck, or an arc of at most about 30°. Hold 8–15 frames at each end.
  Combine moves only across a cut.
- **Lenses.** 35–50 mm is neutral. 70–135 mm flattens and makes graphic compositions (the data documentary uses fov 30°).
  18–24 mm is dramatic and distorts type, so avoid it on text. In three, set the aspect first, then call
  `camera.setFocalLength(mm)`. `filmGauge` (35) covers the *longer* side, like Blender's Sensor Fit *Auto*, so "50 mm"
  frames the same in both tools and in 9:16.
- **Dolly vs zoom.** Dolly (move the camera) creates parallax and feels physical; zoom (change fov) flattens and feels
  like surveillance. A dolly-zoom (move in while widening fov, keeping the subject size) is a one-time trick.
- **Parallax layers.** Put 3–5 depth planes (background noise, mid particles, foreground bokeh specks) at geometric
  distances such as 1×, 2×, 4×. A 5–10 % lateral truck then reads as depth without any orbit.
- **Easing.** Use in-out cubic or quint for moves, plus a long "settle" at the landing (for example
  `1-(1-t)^4`). Never linear, except continuous drift. Evaluate the ease on the CPU from frame. For shader-side
  per-particle easing, upload a 64-sample LUT and interpolate (the data documentary's `easeLut`/`sampleLut`), so CPU labels and
  GPU particles agree exactly.
- **Orbits**: interpolate yaw/pitch/radius around the target (shortest yaw), never lerp positions (the data documentary's camera module).
- **Rack focus**: animate the focus distance between two subjects over 12–20 frames with an ease, keeping aperture
  constant. In Blender set `cam.data.dof.focus_object` or keyframe `focus_distance`; in three use `dof()` with a
  uniform focus.
- **Handheld**: seeded noise (`@remotion/noise` `noise2D(seed, t*0.35, 0)`) at 0.5–2 % of frame height. Never random.
- **Motion budget**: keep a point's travel under about 3 % of frame width per frame at 30 fps, or add motion blur
  (180° shutter). Beyond that, H.264 at social bitrates smears or strobes.

---

## 5. Particle systems that look premium
- **Count.** 20k–100k reads as "substance"; the data documentary uses 58,184 (one per data point). Below 5k, make each particle
  meaningful and larger.
- **Size attenuation** in pixels: `px = size * pxPerUnit / depth`, where
  `pxPerUnit = bufferH / (2·tan(fov/2))`. **Floor it**: below about 1.25 px, fade alpha by `(px/min)^2` instead of
  shrinking. This kills sub-pixel shimmer and crawl after encoding.
- **Sprite profile.** Draw a crisp disc with a 1 px AA edge while small. Ramp to a soft `(1-x²)²` bump above about
  2–9 px, with a gain of about 1.7 to keep energy constant.
- **Blending.** Output *premultiplied* color with blend `ONE, ONE_MINUS_SRC_ALPHA`, and write
  `alpha·(1-additive)`: one uniform then morphs from normal "over" (0) to glow (1). Pure additive whitens every pile;
  keep it at 0.1–0.3 for dense clusters. `depthWrite:false`. With additive or premultiplied soft sprites you can skip
  depth sorting. Sort only for opaque-ish alpha "over", or use `alphaToCoverage` for hard dots.
- **Color.** Ramp through a perceptual palette (OKLab/OKLCH lerp on the CPU into per-particle attributes). Keep colors in
  linear space inside the shader, and remember that small linear numbers look big in sRGB. Accent at most one hue;
  push the rest toward ink or neutral.
- **Depth cues.** Fog as an alpha falloff (`mix(1, fogMin, smoothstep(near, far, depth))`). For DOF, grow the sprite by
  the circle of confusion `coc = aperture·|d−focus|/d·pxPerUnit/focus`, draw `sqrt(px²+coc²)` px, and scale alpha by
  `px²/drawn²` (energy conservation = real bokeh). Check `ALIASED_POINT_SIZE_RANGE` if you use `gl.POINTS`.
- **Morph between layouts** (the data documentary's engine pattern: keyframed layouts + a particle shader):
  - Each layout is a pure `compute(data, viewport) → {position, color, size, alpha}` Float32Array set, memoized per
    (layout id, viewport).
  - The keyframe list says which pair (A→B, progress) is active at a frame. Transitions may not overlap (validated).
  - Upload A and B as attributes (`aPosA/aPosB/...`, shared `BufferAttribute`s so a revisit never re-uploads). The
    vertex shader blends them.
  - Per-particle stagger: `t = clamp((progress − delay·spread)/(1−spread))`, with delays from random, sweep or role
    order.
  - Flight, not lerp: `bump = 4e(1−e)` adds an arc (`arcDir·arc·bump`), a swirl around an axis, and noise scatter
    mid-flight, all zero at both ends so layouts land exactly.
  - Deterministic drift: two octaves of simplex `noiseVec(pos·freq + t·speed)` at amplitude ≤0.02 world units while at
    rest (≤0.002 on pixel grids, to avoid moiré).
  - Highlight: dim and desaturate outside a mask, and pulse inside it with `0.5−0.5cos(2π(t·f − phase))`.
- **Labels on particles**: project world points to composition pixels with the *same* camera state (the data documentary
  `project()`), so HTML type stays glued to 3D.
- **Compute path (WebGPU)**: a storage buffer plus a stateless kernel `pos[i] = f(hash(i), t)`, re-run every frame.
  Tested at 60k sprites, 640×360 × 60 frames in 4.8 s wall on M1 Pro with concurrency 4.

---

## 6. Shader recipe cookbook
GLSL unless marked. `uFrame` is the integer frame and `uT = frame/fps`. Put grain and dither **last**, in display space.

**SDF shape with pixel-exact AA** (any scale, any zoom)
```glsl
float sdRoundBox(vec2 p, vec2 b, float r){ vec2 q=abs(p)-b+r; return length(max(q,0.))+min(max(q.x,q.y),0.)-r; }
float d = sdRoundBox(p, vec2(.4,.2), .06);
float a = clamp(.5 - d / fwidth(d), 0., 1.);          // coverage; animate b/r for morphs
float ring = clamp(.5 - (abs(d) - uStroke) / fwidth(d), 0., 1.); // outline, animate uStroke
```
**MSDF text** (msdf-atlas-gen atlas). Weight and glow animate by moving the threshold:
```glsl
float median(vec3 s){ return max(min(s.r,s.g), min(max(s.r,s.g), s.b)); }
float sd = median(texture(uAtlas, vUv).rgb) - .5 + uGrow;   // uGrow>0 = bolder
float alpha = clamp(sd / fwidth(sd) + .5, 0., 1.);
float glow = smoothstep(-.25, 0., sd) * .35;                 // soft halo from the same field
```
(WebGL R3F: drei `<Text>`/troika gives SDF text for free. WebGPU: sample the MSDF in a TSL node material, or use
`TextGeometry` meshes.)

**Domain-warped noise backdrop** (IQ warp). TSL, tested:
```js
const p = uv().mul(3.0);
const q = vec2(mx_fractal_noise_float(p.add(uT.mul(0.05))), mx_fractal_noise_float(p.add(vec2(5.2, 1.3))));
const f = mx_fractal_noise_float(p.add(q.mul(4.0)), 4);
bgMat.colorNode = mix(color('#05060a'), color('#3a1a4a'), smoothstep(-0.3, 0.7, f));
```
**Curl-noise flow** (divergence-free, so particles swirl without clumping). Use it statelessly as
`p0 + curl(p0*k + uT*s)*amp`, or integrate from a bake with a fixed dt:
```glsl
vec3 curl(vec3 p){ const float e=.1; vec3 dx=vec3(e,0,0), dy=vec3(0,e,0), dz=vec3(0,0,e);
  vec3 px=noiseVec(p+dx)-noiseVec(p-dx), py=noiseVec(p+dy)-noiseVec(p-dy), pz=noiseVec(p+dz)-noiseVec(p-dz);
  return vec3(py.z-pz.y, pz.x-px.z, px.y-py.x) / (2.*e); }
```
**Dither against banding** (interleaved gradient noise, rotated per frame; TSL has `interleavedGradientNoise`):
```glsl
float ign(vec2 px){ return fract(52.9829189 * fract(dot(px, vec2(.06711056, .00583715)))); }
col += (ign(gl_FragCoord.xy + float(uFrame) * 5.588238) - .5) / 255.;   // last op, sRGB 0..1
```
TSL form (tested): `vec4(renderOutput(lit).rgb.add(interleavedGradientNoise(screenCoordinate.xy.add(uFrame.mul(5.588238))).sub(.5).mul(2.5/255)),1)`,
with `pipeline.outputColorTransform = false`.

**Film grain** (frame-seeded, lattice of at least 2 px, weighted toward the shadows; condensed from the data documentary
`FinishEffect`):
```glsl
vec2 g = floor(gl_FragCoord.xy / uGrainPx) + vec2(mod(uFrame,997.)*13.17, mod(uFrame,991.)*7.31);
float n = hash12(g) - .5;                              // any good 2D hash
vec3 p = sqrt(max(col, 0.));                           // perceptual space: grain shows in shadows
p += n * uGrain * (1. - .55 * smoothstep(.2, .9, dot(p, vec3(.333))));
col = p * p;                                           // uGrain ~0.03-0.04
```
**Chromatic aberration** (radial, subtle, off on pixel-fine grids):
```glsl
vec2 c = uv - .5; vec2 off = c * dot(c, c) * 4. * uCA;              // uCA <= .002 at the corners
col = vec3(texture(tIn, uv + off).r, texture(tIn, uv).g, texture(tIn, uv - off).b);
```
**Vignette** (aspect-correct):
```glsl
float r = length((uv - .5) * vec2(uAspect, 1.));
col *= 1. - uVig * smoothstep(.35, 1.05, r);                        // uVig .3-.45
```
**Halftone** (45° screen, dot radius from luminance):
```glsl
float lum = dot(col, vec3(.2126, .7152, .0722));
vec2 cell = fract(mat2(.7071,-.7071,.7071,.7071) * gl_FragCoord.xy / uCell) - .5;
float d = length(cell) - .7 * sqrt(1. - lum);
col = mix(uPaper, uInk, clamp(.5 - d / fwidth(d), 0., 1.));
```
**Tasteful bloom**: bloom *only emissive*, strength 0.2–0.6, threshold near HDR white (piles and sparks only). TSL:
```js
scenePass.setMRT(mrt({ output, emissive }));
pipeline.outputNode = scenePass.getTextureNode('output').add(bloom(scenePass.getTextureNode('emissive'), 0.45, 0.3, 0));
```
A test with additive sprites and threshold 0.15 turned the whole background purple-grey. Moving the threshold to 0.7
and strength to 0.35 fixed it.

**Glitch, sparingly**: trigger it from the timeline (`uGlitch` keyed 0→1→0 over 3–6 frames on a cut or beat), never
continuously.
```glsl
float row = floor(uv.y * 24.), slot = floor(float(uFrame) / 2.);
float sh = (hash12(vec2(row, slot)) - .5) * .06 * uGlitch;
vec2 u2 = uv + vec2(sh, 0.);
col = vec3(texture(tIn, u2 + vec2(.004*uGlitch,0)).r, texture(tIn, u2).g, texture(tIn, u2 - vec2(.004*uGlitch,0)).b);
```

---

## 7. Lighting and look
- **Tone mapping** (tested in Blender 5.2 on the same frame with a saturated orange emissive title):
  - *Khronos PBR Neutral* kept the authored hue and deep blacks. **Default for brand-color motion graphics.** three:
    `NeutralToneMapping`; Blender view: `'Khronos PBR Neutral'`.
  - *AgX* (Blender default, three `AgXToneMapping`) rolled the orange off to peach and lifted the blacks. Use it for
    photoreal or bloom-heavy scenes where graceful highlight desaturation matters. Author emissive at lower strength.
  - *Standard/None* clipped and skewed orange to yellow. Use it only for flat, unlit graphics that never exceed 1.0.
  - *ACES* (three `ACESFilmicToneMapping`, R3F's default; Blender 5 adds ACES 1.3/2.0 views) came out darker and more
    contrasty, with hue skews. Pick it only to match an ACES pipeline.
  - **Match across tools**: if Blender shots intercut with three.js shots, use the same operator on both sides.
    Neutral↔Neutral is easiest.
- **Lighting recipe**: warm key from 45° high, cool rim from behind-opposite at 1.5× the key, a dark world at 0.3–1.0
  strength, and emissive accents carrying the brand color. Studio floor: dark, roughness 0.3–0.5, so it catches a
  reflection.
- **Where to grade**: do it in-shader or in-engine when the grade must react to the scene (vignette, haze, highlight
  shoulder, per-shot looks animated by frame). Use an ffmpeg `lut3d=file.cube` for one global look across mixed sources
  (Blender + three + screen captures), applied once at the final encode. Don't double-grade.
- **Banding after H.264** (dark gradients band at 8-bit). Defenses, in order: (1) render 16-bit PNG (Blender
  `color_depth='16'`) or HalfFloat buffers; (2) dither when going to 8-bit (IGN in-shader, or ffmpeg
  `scale=…:sws_dither=ed`); (3) grain at ≥2 px scale (per-pixel grain is eaten by the encoder and doubles bitrate, as
  the data documentary measured); (4) encode with `-tune grain -x264-params aq-mode=3` (more bits in darks), CRF 16–18 for
  masters. Platforms re-encode anyway: upload the master.
- **Tag color correctly** (tested with ffmpeg 9): a PNG sequence encode inherits `color_trc=iec61966-2-1` (sRGB) even with
  `-color_trc bt709`. Force the tags with
  `-vf "scale=out_color_matrix=bt709:out_range=tv:sws_dither=ed,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"`.

---

## 8. Blender headless pipeline (tested: Blender 5.2.1 LTS, M1 Pro, Metal)
**Invoke**: `blender -b --factory-startup --python-exit-code 1 -P script.py -- --engine eevee --frames 90 --res 1920x1080`.
Parse arguments after `--`. `--factory-startup` isolates you from user add-ons and prefs (reproducible). A `.blend` can
come first: `blender -b scene.blend -P script.py -- …`. The full tested skeleton is `../scripts/blender_mg_render.py`:
it builds a scene from nothing, adds a GN wave grid, a GP v3 write-on and an eased camera, renders resumably and logs
timings.

**5.x API facts** (verified by probing 5.2; https://developer.blender.org/docs/release_notes/5.0/python_api/):
- Engine ids are `'BLENDER_EEVEE'`, `'CYCLES'` and `'BLENDER_WORKBENCH'`. `BLENDER_EEVEE_NEXT` is gone since 5.0.
- **`Action.fcurves` no longer exists** (slotted actions). Keyframes go through
  `anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves`.
- `scene.node_tree` was removed; use `scene.compositing_node_group`. `material/world/scene.use_nodes` are deprecated,
  since trees always exist.
- View transforms: `Standard, ACES 1.3, ACES 2.0, Khronos PBR Neutral, AgX, Filmic, Filmic Log, False Color, Raw`. AgX
  looks go from `'AgX - Punchy'` to `'AgX - Very Low Contrast'`.
- Motion blur lives at `scene.render.use_motion_blur` / `motion_blur_shutter` for both engines.
- Grease Pencil v3 data is `bpy.data.grease_pencils` (legacy annotations moved to `bpy.data.annotations`).

```python
# excerpt: cam, title, OUT come from the full script (scripts/blender_mg_render.py)
import bpy, os, sys; from bpy_extras import anim_utils
engine = (sys.argv[sys.argv.index("--")+1:] or ["eevee"])[0]   # simplified; the full script uses argparse
sc = bpy.context.scene; r = sc.render
def ease_keys(obj, interp="BEZIER", easing="AUTO"):          # 5.x-safe easing
    ad = obj.animation_data
    for fc in anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves:
        for k in fc.keyframe_points:
            k.interpolation, k.easing = interp, easing        # BEZIER auto-clamped = ease in/out; SINE/EXPO + EASE_IN_OUT
            k.handle_left_type = k.handle_right_type = "AUTO_CLAMPED"
cam.location = (0.6,-9,1.6); cam.keyframe_insert("location", frame=1)
cam.location = (0.2,-6.5,1.3); cam.keyframe_insert("location", frame=90); ease_keys(cam)
cam.data.dof.use_dof = True; cam.data.dof.focus_object = title; cam.data.dof.aperture_fstop = 2.8
r.use_motion_blur = True; r.motion_blur_shutter = 0.5                      # 180 degrees
sc.view_settings.view_transform = "Khronos PBR Neutral"                     # or "AgX" + look
r.image_settings.file_format, r.image_settings.color_depth = "PNG", "16"
if engine == "cycles":
    p = bpy.context.preferences.addons["cycles"].preferences
    p.compute_device_type = "METAL"; p.get_devices()          # OPTIX/CUDA/HIP off Apple (the full script probes)
    for d in p.devices: d.use = d.type == "METAL"
    c = sc.cycles; r.engine = "CYCLES"; c.device = "GPU"; c.samples = 128
    c.use_adaptive_sampling, c.adaptive_threshold = True, 0.03
    c.use_denoising, c.denoiser, c.denoising_use_gpu = True, "OPENIMAGEDENOISE", True
    c.denoising_input_passes = "RGB_ALBEDO_NORMAL"; c.use_animated_seed = True
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces = 6, 2, 2; r.use_persistent_data = True
else:
    r.engine = "BLENDER_EEVEE"; e = sc.eevee
    e.taa_render_samples = 64; e.use_raytracing = True; e.ray_tracing_method = "SCREEN"; e.use_fast_gi = True
for f in range(sc.frame_start, sc.frame_end + 1):                          # resumable loop
    out = f"{OUT}/{f:04d}.png"
    if os.path.exists(out): continue
    sc.frame_set(f); r.filepath = out; bpy.ops.render.render(write_still=True)
```
- **Follow Path**: `fp = cam.constraints.new('FOLLOW_PATH'); fp.use_fixed_location = True`, then keyframe
  `'constraints["Follow Path"].offset_factor'`, and put `TRACK_TO` last in the stack. Offsets are fractions of the curve
  length, start wherever the curve starts, and cannot wrap past 0 or 1. Probe the positions first; the test needed the
  circle rotated 90° to center the arc on the front.
- **Geometry Nodes from Python**: `ng = bpy.data.node_groups.new(n,'GeometryNodeTree')`, then
  `ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')` (and one for OUTPUT). Nodes:
  `GeometryNodeMeshGrid`, `GeometryNodeInputSceneTime` (a pure function of the frame), `GeometryNodeSetPosition`,
  `GeometryNodeInstanceOnPoints`. Attach with `obj.modifiers.new('GN','NODES').node_group = ng`. 5.2 also lets empties
  carry GN modifiers.
- **Grease Pencil v3 write-on**: `gpd = bpy.data.grease_pencils.new('Ink')`, `layer.frames.new(1).drawing`,
  `drawing.add_strokes([n])`, set `points[i].position/radius`. The material needs
  `bpy.data.materials.create_gpencil_data(m)`. Add a `GREASE_PENCIL_BUILD` modifier with `frame_start`/`length`.
  **Close loops with a duplicate end point, not `cyclic=True`**: a cyclic stroke draws a chord during the build (seen in
  the test).
- **EEVEE vs Cycles**: EEVEE for mograph, emissive, stylized looks and anything on a deadline. Its 5.2 overhaul improved
  screen-space raytracing; some scenes render darker than in 5.1, so re-check exposure
  (https://developer.blender.org/docs/release_notes/5.2/eevee/). Cycles for glass, caustics,
  true GI and complex DOF. On Apple Silicon use Metal GPU only.
- **Measured budget** (M1 Pro, scene: text, GN 784 instances, GP, DOF, motion blur):

| Engine / settings | 480×270 per frame | 1920×1080 per frame | 10 s @30 fps at 1080p |
|---|---|---|---|
| EEVEE, 32 → 64 TAA samples | 0.34 s | 2.8 s | ≈ 14 min |
| Cycles Metal, 32 → 128 spp, adaptive 0.03, OIDN GPU | 0.55 s | 20 s | ≈ 1.7 h |

  First-frame overheads: EEVEE shader compile takes 1–4 s. **The first Cycles run after install compiles Metal kernels
  (140 s, once per Blender version).** Budget rule: render a 25 % proof of 3 frames (start, middle, end) first. Scale
  the per-frame time by the pixel ratio, then decide. Halve samples before halving resolution.
- **PNG → video**: see the `setparams` command in §7. For alpha, use `film_transparent=True` with RGBA PNG, then
  `-c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le` (or VP9 `yuva420p`) for the Remotion overlay. Render the
  **exact frame count** the edit needs, plus transition handles. Never retime with `setpts`/`fps` (drops and duplicates
  frames = judder).
- **Blender MCP** (Blender Lab v1.0.0, when configured as an MCP server): `execute_blender_code_for_cli(blend_file, code)`
  runs Python in `blender --background` on a .blend and returns whatever you assign to `result` (verified on the test
  scene). The interactive tools (`execute_blender_code`, `get_objects_summary`, `render_viewport_to_path`,
  `render_thumbnail_to_path`, screenshots) need the GUI running with the add-on. `search_api_docs` and
  `search_manual_docs` query the bundled 5.x docs: use them before guessing an API. Keep final renders in a CLI script
  (resumable, logged), not in MCP calls.

---

## 9. Pitfalls and fixes
1. **The same frame renders differently twice.** Cause: TSL `time`/`deltaTime`/`oscSine()`, `FilmNode`, R3F `delta`, drei
   `Float`/`Sparkles`/`Stars`/`CameraShake`/`Cloud`, `mixer.update(delta)`. Fix: `uniform(frame/fps)`,
   `mixer.setTime(t)`, re-implement the helpers from frame.
2. **Blank or black canvas in a Remotion render.** Cause: missing `--gl=angle` (Remotion 4), or SwiftShader. Fix: set it in
   config, log the unmasked renderer, run `npx remotion gpu`.
3. **The first frame of each tab lacks post, or a model hasn't loaded.** Fix: build the composer synchronously, hold a
   `delayRender` until the render callback has run for this frame, and load inside Suspense or `delayRender`.
4. **Grey instead of ink black with the WebGL composer.** Cause: `gl.setClearColor` gets converted to sRGB, then encoded
   again. Fix: set `scene.background = new Color(...)` (the data documentary).
5. **`PostProcessing` deprecation warning / `EffectComposer` doesn't work on WebGPU.** Fix: use `RenderPipeline` plus TSL
   nodes. `@react-three/postprocessing` works with WebGL only.
6. **Double tone mapping or washed-out output.** Fix: with `renderOutput()` in the chain, set
   `pipeline.outputColorTransform = false`. With the `postprocessing` library, set `renderer.toneMapping = NoToneMapping`
   (R3F `flat`) and tone-map in the last effect.
7. **Brand colors shift hue.** Cause: ACES skews hues, AgX desaturates highlights. Fix: Neutral tone mapping, or
   lower emissive strength.
8. **Additive piles blow out to white, bloom hazes the whole frame.** Fix: additive at 0.1–0.3 via the premultiplied
   blend trick, bloom threshold near white, and bloom only emissive (MRT).
9. **Sub-pixel particles shimmer or crawl after encoding.** Fix: a minimum on-screen size of about 1.25 px that fades
   alpha instead of shrinking, whole-pixel grid pitch, no camera move over pixel lattices.
10. **Chromatic aberration tints fine dot grids.** Fix: CA = 0 by default; enable it only on soft, out-of-focus shots,
    at 0.001–0.002.
11. **Grain triples bitrate and render time.** Cause: per-pixel grain is x264 entropy. Fix: a lattice of 2 px or more,
    amplitude about 0.035 in sqrt space, `-tune grain`, CRF 18–20 for uploads.
12. **Banding in dark gradients.** Fix: 16-bit or half-float intermediates, IGN dither as the last op, error-diffusion
    `sws_dither=ed`, `aq-mode=3`.
13. **Wrong transfer tag in the MP4** (`iec61966-2-1`). Fix: `setparams=color_trc=bt709…` in `-vf`.
14. **Velocity motion blur or TRAA is wrong on each tab's first frame.** Fix: pre-roll frame−1, use sub-frame
    accumulation (`<CameraMotionBlur samples={5–10}>`), or skip temporal effects.
15. **Splats pop, sort late, or differ between tabs.** Fix: three `GaussianSplat` (synchronous GPU sort), or Spark
    with `await spark.update({scene})` and LoD paging off. Keep camera moves slow.
16. **Blender 5 script fails on `action.fcurves`, `scene.node_tree` or `BLENDER_EEVEE_NEXT`.** Fix: channelbag API,
    `compositing_node_group`, `BLENDER_EEVEE`.
17. **The first Cycles render hangs for minutes.** Cause: Metal kernel compile, once per version. Fix: warm up with a
    1-frame 64×64 render before timing or budgeting.
18. **Euler flips or wobble when keyframing `rotation_euler` from `to_track_quat`.** Fix: a `TRACK_TO` constraint on
    an animated target empty. Keyframe positions, not rotations.
19. **A Grease Pencil build draws a straight chord.** Fix: no `cyclic`; close with a duplicate end point.
20. **Shots judder in the edit.** Cause: CGI retimed with `setpts`/`fps`. Fix: render the exact frame count with
    handles, or re-render at the new length.
21. **Moiré on regular grids during camera moves.** Fix: hold the camera frontal at rest on lattices, drift ≤0.002,
    or add a hint of DOF and grain.
22. **`<Sequence>` inside `<ThreeCanvas>` throws.** Fix: `layout="none"`.

---

## 10. Past productions: what to reuse, what to fix
**A 60 s data documentary** (R3F in Remotion, 58k particles, WebGL `ShaderMaterial` +
`postprocessing`). **Keep**: the pure frame→state pipeline and hashed PRNG; the layout morph engine (stagger,
arc/swirl/scatter bumps, shared CPU/GPU easing LUT for pinned labels); pixel-aware sprite math (minimum size, CoC DOF,
energy conservation); the premultiplied additive↔over uniform; frame-seeded sqrt-space grain that doubles as dither;
the highlight shoulder; the synchronous composer with a delayRender guard; measured concurrency; and the byte-identical
determinism test . **Gaps vs 2026 practice**: not portable to WebGPU/TSL (a new engine should
target `<ThreeWebGPUCanvas>`); no motion blur, so fast swirls rely on easing to avoid strobing; `gl.POINTS` has a size
cap, so very large bokeh can clip; layout computation costs about 0.5 s of CPU per tab on the first frame.

**A metro-system trailer** (Blender 5.2 asset kit + three.js app + 30 s trailer). **Keep**:
`--factory-startup` builds whose GLBs came out SHA-256 identical across two clean builds ;
per-asset triangle budgets checked on import; resumable per-frame rendering with a saved `.blend` plus `metadata.json`
(source hashes) per shot; one slow move per shot (two-key drifts over 90 frames at 48 mm); EEVEE at 16 TAA samples with
AO-only fast GI for speed; frozen, manually stepped app capture (`freeze` + `step(1/30)`). **Fix**: Blender shots use
**AgX** while the three.js app uses **ACESFilmic**, and they intercut in one trailer (match the operators); clips were
retimed with `setpts` + `fps=30` (render exact durations); capture went through q94 JPEG screenshots before H.264
(double lossy; use PNG or canvas readback); camera rotation was keyframed from `to_track_quat` Eulers (prefer a
`TRACK_TO` target); 8-bit PNGs and encodes not tagged BT.709 (use 16-bit plus `setparams`).
