# Remotion: stack reference

Verified 2026-09-26 against remotion.dev docs (Remotion v4.0.529, released 2026-09-25). v4 ships a patch
every few days; v5.0 is in preparation (PR #3750) and NOT released. Before coding, pull current docs:
https://www.remotion.dev/llms.txt. Append `.md` to any docs URL (e.g. https://www.remotion.dev/docs/spring.md) or send
`Accept: text/markdown`.

**License: source-available, not MIT.** Sources: https://www.remotion.dev/docs/license/faq and
https://github.com/remotion-dev/remotion/blob/main/LICENSE.md
- Free for: individuals (commercial use included), for-profit orgs with **3 people or fewer**, non-profits, and evaluation.
- Orgs of 4+ people need a Company License. "Creators" costs $25/month per person who writes Remotion code, by hand or with a
  coding agent. "Automators" costs $0.01 per render with a $100/month minimum. It applies to orgs that own code that
  programmatically calls `renderMedia/renderStill/renderFrames`, Lambda, Cloud Run, Vercel or web rendering, scripts
  `npx remotion render`, or embeds `<Player>`. With both plans the combined minimum is $100/month. Enterprise has a $500
  minimum. Features are identical across all tiers. Buy at https://remotion.pro/license.
- Forbidden: a service that renders Remotion code uploaded by its users. Allowed: rendering Remotion code your service
  generated with AI. Agency delivering only MP4s: only the agency headcount counts.
- The v5 license (not live yet) counts contractors toward headcount. If the user's team has 4+ people, tell them.

## 0. Official agent skills (read them; don't duplicate them)
Install: `npx skills add remotion-dev/skills`, or `npx remotion skills add` inside a project. `create-video` also offers to add
them. Repo: https://github.com/remotion-dev/skills (mirror of `packages/skills`; SKILL.md `version: 4.0.529`).
Docs: https://www.remotion.dev/docs/ai/skills. The Remotion MCP is deprecated in favor of skills.
Router `remotion-best-practices` loads: `remotion-create`, `-markup` (≈30 rule files), `-render`, `-studio`, `-captions`,
`-maps` (Mapbox/MapLibre/MapTiler/Cesium), `-multimedia` (Mediabunny), `-interactivity`, `-saas`, `-docs`, `-upgrade`.
What they insist on (verified in the files):
- Drive everything with `useCurrentFrame()` + `interpolate()`. CSS `transition`/`animation` and Tailwind `animate-*` "will not
  render correctly". Favorite eases: `Easing.bezier(0.16, 1, 0.3, 1)` and `Easing.spring({damping: 200})`.
- Keep `interpolate()` inline in `style`, and use the individual `scale`/`translate`/`rotate` CSS properties instead of
  `transform` strings. This keeps keyframes editable in Studio; wrap elements in `Interactive.Div` (4.0.475+) with a hard-coded `name`.
- Use media from `@remotion/media` (`<Video>`, `<Audio>`), `<CanvasImage>` (stills that accept `effects`) and `<AnimatedImage>` (GIF/APNG/WebP).
- "Always premount any `<Sequence>`" (`premountFor={fps}`). Put each substantial scene in its own file, register it as its own
  `<Composition>` inside a `<Folder>` (a "connected composition"), and chain scenes with `<TransitionSeries>`.
- Add packages with `npx remotion add <pkg>` so versions match. Render only when the user asks. For visual checks use
  `npx remotion render <id> out/frames --frames=0,30,90 --image-format=png`.
- `video-layout.md`: one focal point per scene. Safe area at 1080 px width: at least 80 px from the sides and 100 px from
  top and bottom. Headlines at least 84 px, supporting text at least 44 px; scale with width.
- Voiceover recipe: ElevenLabs TTS per scene, then `calculateMetadata` measures each clip and sums the durations.
  Captions: whisper.cpp → `Caption[]` JSON → `createTikTokStyleCaptions`. SFX: `@remotion/sfx` plus `https://remotion.media/*.wav`.

## 1. When to pick Remotion
- **Remotion**: TSX/React, data- or prop-driven videos, many variants and aspect ratios from one codebase, VO/caption/beat sync,
  frame-exact footage, programmatic or cloud renders, an embeddable `<Player>`. Cost: headless Chrome captures every frame
  (≈40–100 ms/frame/tab), plus the license at 4+ people.
- **HTML frames / GSAP page**: a one-off animation that already exists as a web page and needs no media timeline. Inside Remotion,
  use `@remotion/gsap` instead of a hand-rolled capture loop.
- **Motion Canvas**: MIT, generator timelines, strong for vector/code/LaTeX explainers; weaker for footage, audio mixing and cloud renders.
- **Blender**: real 3D lighting, physics, photoreal materials. Render passes there, then composite type and captions in
  Remotion with `<Video>`.

## 2. Project setup
```bash
npx create-video@latest --yes --blank my-video   # bun: `bun create video` (scripts use `remotionb` = Bun runtime)
cd my-video && npm i
npx remotion skills add                          # official agent skills
npm run dev                                      # = remotion studio → http://localhost:3000/<composition-id>
npx remotion add @remotion/transitions @remotion/media @remotion/google-fonts zod   # same version as core
npx remotion studio --no-open                    # agents: long-running; prints URL
```
Requirements: Node ≥16 (v5 will need ≥22) or Bun ≥1.0.3, and macOS 15+ (https://www.remotion.dev/docs). The 4.0.52x blank
template ships Tailwind v4 and `Config.setRspack(true)`. Tested: `--no-tailwind` is ignored because minimist parses it as
`tailwind=false`, so delete `@remotion/tailwind-v4` and `enableTailwind` by hand if you don't want them.
Pin **every** `remotion`/`@remotion/*` package to the **same exact version** (no `^`). Check with `npx remotion versions`
and upgrade with `npx remotion upgrade`.

Layout:
```
src/index.ts          registerRoot(RemotionRoot)
src/Root.tsx          <Composition>/<Still> list, <Folder name="Scenes"> with one composition per scene
src/scenes/*.tsx      one component per scene (scene-local frames)
src/lib/theme.ts      fonts (loadFont at module scope), palette, type scale in units of min(w,h)/100
src/lib/timing.ts     fps, scene lengths, transition lengths, beat/VO cue helpers
public/               assets → staticFile('audio/vo.mp3'). Keep public/ next to package.json
remotion.config.ts    CLI + Studio defaults ONLY. Not applied to @remotion/renderer APIs
```
`<Composition id component durationInFrames fps width height defaultProps schema calculateMetadata/>`
(https://www.remotion.dev/docs/composition). Ids use letters, numbers and `-`. Keep width and height even for
h264/yuv420p. Use `<Still>` for single images and `<Folder>` for grouping.
- **zod props**: `schema={z.object({...})}` (top level must be `z.object`). Studio then shows editable controls; use
  `zColor()` from `@remotion/zod-types` for colors. Render-time override: `--props='{"title":"Hi"}'` or `--props=props.json`.
- **calculateMetadata** (https://www.remotion.dev/docs/calculate-metadata): async `({props, abortSignal}) => ({durationInFrames,
  width, height, fps, props, defaultOutName, defaultCodec, defaultPixelFormat, defaultVideoImageFormat})`. Use it to size the
  composition to VO or footage. Measure durations with Mediabunny (`new Input({formats: ALL_FORMATS, source: new
  UrlSource(staticFile(f))}).computeDuration()`); `getAudioDurationInSeconds()` is deprecated. Precompute once, never per frame.
- **staticFile('x.png')**: the only way to reference `public/`. Since v4 it URL-encodes the path, so never pre-encode.
  Remote URLs work but must allow CORS for `@remotion/media` and `<CanvasImage>`.
- **Fonts** (https://www.remotion.dev/docs/fonts): `import {loadFont} from '@remotion/google-fonts/Inter'; const {fontFamily,
  waitUntilDone} = loadFont('normal', {weights: ['400','800'], subsets: ['latin']})`. Call it at module scope; it
  auto-blocks rendering until loaded. List only the weights and subsets you use (`latin-ext` for names).
  Local fonts: `loadFont({family, url: staticFile('F.woff2'), weight})` from `@remotion/fonts`. Hand-rolled `FontFace` needs
  `delayRender`/`continueRender`. Never rely on system-installed fonts: other machines and Lambda silently fall back.
- **Async data** (https://www.remotion.dev/docs/use-delay-render): `const {delayRender, continueRender, cancelRender} =
  useDelayRender(); const [h] = useState(() => delayRender('Loading captions'))`. Call `continueRender(h)` after the fetch and
  `cancelRender(err)` in catch. The default timeout is 30 s (`--timeout`, `Config.setDelayRenderTimeoutInMilliseconds`,
  per-call `timeoutInMilliseconds`). Always add a label. Prefer the hook over global `delayRender()`.

## 3. Animation core (all from `remotion`)
- `useCurrentFrame()` is **local** inside any `<Sequence>`/`Series`/`TransitionSeries` (starts at 0). `useVideoConfig()` →
  `{fps, width, height, durationInFrames}`. Write timings as `n * fps`, never raw frames scattered in code.
- `interpolate(input, inRange, outRange, opts)` (https://www.remotion.dev/docs/interpolate): extrapolation defaults to **extend**.
  Pass `{extrapolateLeft:'clamp', extrapolateRight:'clamp'}` for opacity, volume and anything bounded. Recent options:
  per-segment `easing: [e1, e2, …]` (4.0.462), CSS string outputs (`'0px 0px'→'100px 50px'`, `'20deg'`) (4.0.472), numeric
  tuples (4.0.473), `posterize: 3` for a stepped/stop-motion feel (4.0.470), `output: 'perceptual-scale'` for scale so the
  visible area changes linearly (4.0.490). Colors: `interpolateColors(frame, [0,30], ['#000','#f40'])`.
- `spring({frame, fps, config:{mass=1, damping=10, stiffness=100, overshootClamping}, from, to, delay, durationInFrames,
  reverse})` (https://www.remotion.dev/docs/spring). Recipes: `damping: 200` gives a smooth push with no bounce (settles in
  ≈23 frames at 30 fps); `damping: 12–15` bounces playfully; `mass` 0.5 is snappier; `durationInFrames` stretches the spring to
  an exact length; `delay: i * 3` staggers. Get settle time with `measureSpring({fps, config})`. Map the 0→1 spring through
  `interpolate` for pixels.
- `Easing` (https://www.remotion.dev/docs/easing): `bezier(x1,y1,x2,y2)`, `in/out/inOut(e)`, `quad, cubic, sin, circle, exp,
  back(), elastic(), bounce`, and `Easing.spring({damping, allowTail})` (4.0.476) for spring feel inside `interpolate` segments.
- `<Sequence from durationInFrames layout="none"|"absolute-fill" premountFor name>` (https://www.remotion.dev/docs/sequence).
  Newer props: `trimBefore` (4.0.482), `loop`, `playbackRate` (4.0.528), `freeze={n}` (4.0.476), `cropLeft/Right/Top/Bottom`
  (4.0.500), `width/height` (nests another composition's size). Media and many components accept `from`/`durationInFrames`
  directly (4.0.446+).
- `<Series>` + `<Series.Sequence durationInFrames offset={-15}>` (a negative offset overlaps). `<Loop durationInFrames times>`
  plus `Loop.useLoop()`. `<Freeze frame>` or `<Sequence freeze>` holds a frame.
- `@remotion/transitions` (https://www.remotion.dev/docs/transitions/transitionseries): `<TransitionSeries>` with
  `.Sequence`, `.Transition presentation timing`, and `.Overlay durationInFrames offset` (4.0.415; lays an effect over the cut
  without shortening). Total length = sum of scenes − sum of transitions, via `timing.getDurationInFrames({fps})`. Timing:
  `linearTiming({durationInFrames, easing})` or `springTiming({config:{damping:200}, durationInFrames})`.
  - Work everywhere: `fade()`, `slide({direction:'from-right'})`, `wipe()`, `flip()`, `clockWipe()`, `iris()`,
    `pushCut()` (4.0.500), `none()`. Import each from `@remotion/transitions/<name>`.
  - HTML-in-canvas: `dissolve, ripple, crossZoom, filmBurn, bookFlip, crosswarp, dreamyZoom, linearBlur, swap, zoomBlur,
    zoomInOut, blurSlide`. They render out of the box (Remotion's bundled Chrome has the flag, 4.0.455+). Studio preview needs
    Chrome ≥149 with `chrome://flags/#canvas-draw-element`. WebGL ones need `--gl=angle`.
  - The entering scene's local frame 0 is the **start** of the transition. Entrance animations play while the scene slides
    in, so delay them by the transition length if they should read after the cut (seen in the test render below).
- `@remotion/paths`: `evolvePath(p, d)` → `{strokeDasharray, strokeDashoffset}` (line draw-on), `getLength`,
  `getPointAtLength`, `getTangentAtLength` (move along a path), `interpolatePath(t, a, b)` (morph), `warpPath`, `cutPath`,
  `scalePath`, `translatePath`, `reversePath`, `getBoundingBox`, `normalizePath`.
- `@remotion/shapes`: `<Rect|Circle|Ellipse|Triangle|Star|Polygon|Pie progress|Heart|Arrow|Callout|Spark>` components plus
  `makeX()`, which returns an SVG path to animate with `@remotion/paths`.
- `@remotion/noise`: `noise2D/3D/4D(seed, x, y, …)` → −1..1, deterministic per seed. Use `frame/fps*speed` as one axis for
  organic drift and `noise3D('cloud-x', x, y, t)` for fields.
- `@remotion/motion-blur` (https://www.remotion.dev/docs/motion-blur-guide): `<HtmlInCanvasMotionBlur width height samples=8
  shutterAngle=180>` (4.0.529, best; never nest HTML-in-canvas). `<CameraMotionBlur shutterAngle={180} samples={5–10}>`
  (children absolutely positioned; shifts colors and opacity, so keep samples low). `<Trail layers lagInFrames trailOpacity>`
  gives stylized echoes, not a camera look.
- `@remotion/layout-utils`: `measureText({text, fontFamily, fontSize, fontWeight, letterSpacing})` → `{width, height}`,
  `fitText({text, withinWidth, fontFamily, fontWeight})` → `{fontSize}` (cap it with `Math.min`), `fitTextOnNLines`,
  `fillTextBox`. Call them only after `waitUntilDone()` of the font, otherwise you measure the fallback font.
- `@remotion/animated-emoji`: `<AnimatedEmoji emoji="fire"/>` (Noto animated emoji, CC BY 4.0; self-host via `calculateSrc`).
- `@remotion/lottie`: `<Lottie animationData={json} loop playbackRate direction/>`. Load remote JSON behind `delayRender`.
  `getLottieMetadata()` gives the duration for `calculateMetadata`. After Effects → Bodymovin JSON.
- `@remotion/rive`: `<RemotionRiveCanvas src artboard animation fit alignment onLoad/>` (seeks with the frame).
- `@remotion/gsap` (4.0.517): `const scope = useGsapTimeline<HTMLDivElement>(({timeline, selector}) => {timeline.from(
  selector('[data-t]'), {y:40, opacity:0, duration:.8, ease:'power3.out'})}, {dependencies:[x]})` then `<AbsoluteFill
  ref={scope}>`. The timeline is paused and seeked to the frame. Install `gsap` as a peer dependency.
- `@remotion/three` (https://www.remotion.dev/docs/three): `<ThreeCanvas width height>` (required props). Animate from
  `useCurrentFrame()`. Never animate with R3F `useFrame` clocks/deltas, `THREE.Clock` or shader `time` uniforms that advance
  on their own. Use `<Sequence layout="none">` inside the canvas. `<ThreeWebGPUCanvas>` supports TSL. Textures:
  `useOffthreadVideoTexture()` or the `@remotion/media` video-texture snippet. Render with `--gl=angle`, and pass
  `chromiumOptions: {gl: 'angle'}` to SSR APIs.
- `@remotion/effects` (WebGL2, `effects={[blur({radius:8}), lut(...), chromaticAberration(...)]}` on `<Video>`, `<Solid>`,
  `<CanvasImage>`, `<HtmlInCanvas>`), custom `createEffect()`, and `<HtmlInCanvas onPaint>` for DOM→canvas post-processing
  (https://www.remotion.dev/docs/html-in-canvas). The old light-leak and starburst packages are deprecated; they now live in
  `@remotion/effects`. Also `@remotion/rough-notation` (hand-drawn highlights) and `@remotion/mac-cursors`.

## 4. Media and captions
- **Video**: `<Video>` from `@remotion/media` is the default (https://www.remotion.dev/docs/video-tags). It uses
  Mediabunny/WebCodecs, is frame-exact, fastest, downloads partially, loops, and runs client-side. It needs CORS.
  `playbackRate` shifts the pitch. Unsupported codecs fall back to `<OffthreadVideo>` (Rust+FFmpeg extractor: H.265, AV1,
  ProRes render, AVI; downloads the whole file first, so big remote files hit the delayRender timeout).
  `<Html5Video>` (the old `remotion` `<Video>`) is not frame-exact; avoid it for renders. Props: `trimBefore`, `trimAfter`,
  `from`, `volume`, `muted`, `loop`, `objectFit`, `style`. ProRes preview needs the extra decoder
  (https://www.remotion.dev/docs/videos/prores). Transparent source: VP8/VP9 WebM with alpha or ProRes 4444
  (https://www.remotion.dev/docs/transparent-videos).
- **Audio**: `<Audio>` from `@remotion/media` (§7). Legacy `<Html5Audio>` still works.
- **Images**: `<Img>` (waits for load) or `<CanvasImage>` (effects, needs CORS). Never CSS `background-image`/`mask-image`
  for assets, because nothing waits for them (https://www.remotion.dev/docs/flickering).
- **Captions** (https://www.remotion.dev/docs/captions): the `Caption` type is `{text, startMs, endMs, timestampMs,
  confidence}`. Local transcription: `@remotion/install-whisper-cpp` (`installWhisperCpp({to, version:'1.5.5'})`,
  `downloadWhisperModel({model:'medium.en', folder})`, `transcribe({inputPath: 16 kHz wav, tokenLevelTimestamps: true})`, then
  `toCaptions()`). Convert audio first: `ffmpeg -i in.mp3 -ar 16000 in.wav`. In-browser: prefer `@remotion/whisper-webgpu`,
  because `@remotion/whisper-web` is experimental and needs COOP/COEP. Display with `createTikTokStyleCaptions({captions,
  combineTokensWithinMilliseconds: 1200, breakOnSilenceAfterMilliseconds})` → pages, then highlight the active token by
  `startMs`. Other helpers: `parseSrt`/`serializeSrt` and `ensureMaxCharactersPerLine`. Load JSON with `useDelayRender`.
- **Audio viz** (`@remotion/media-utils`): `useWindowedAudioData({src, frame, fps, windowInSeconds: 30})` →
  `{audioData, dataOffsetInSeconds}`, then `visualizeAudio({fps, frame, audioData, numberOfSamples: 128|256 (power of 2),
  optimizeFor:'speed', dataOffsetInSeconds})` → 0..1 bins (bass first, highs last). Bass pulse: average `bins.slice(0,32)`.
  Also `visualizeAudioWaveform` + `createSmoothSvgPath` for oscilloscopes and `getWaveformPortion` for bars. Map through dB
  (`20*log10(v)` over −100..−30) or the lows swamp everything. Pass `frame` down from the parent instead of calling
  `useCurrentFrame()` in children inside offset Sequences.

## 5. Determinism: every pixel must be a pure function of the frame
Remotion renders frames out of order across parallel tabs (https://www.remotion.dev/docs/flickering). Rules:
1. No `Math.random()`. Use `random('seed-'+i)` from `remotion`, or a hash PRNG keyed by index and salt. Seed noise.
2. No CSS transitions, `@keyframes`, Tailwind `animate-*`, `requestAnimationFrame`, `setTimeout`/`setInterval`, `Date.now()`,
   `performance.now()`, video/audio `currentTime` reads, or state accumulated from previous frames (`x += v` in an effect).
3. Simulations such as physics or particles: either use closed-form f(frame), or **bake** the simulation to JSON offline and
   index it by frame (the Matter.js approach in https://www.remotion.dev/docs/third-party).
4. Third-party libraries: GSAP → `@remotion/gsap`; Lottie/Rive → their packages; anime.js → paused timeline + `seek(frame/fps*1000)`;
   CSS animations → `animation-play-state: paused` + negative `animation-delay: -${frame/fps}s`; Framer Motion and
   react-spring → no integration, rewrite with `interpolate`/`spring`.
5. Canvas 2D/WebGL: redraw fully each frame from `frame` inside `useLayoutEffect`. If drawing is async (textures,
   composer), hold the frame with `delayRender` and release it after the draw call.
6. Everything async (fonts, JSON, images) must block through `loadFont`/`useDelayRender`/Remotion media tags.
7. Keep memoized inputs (layouts, arrays, masks) identity-stable at module scope or in `useMemo`.
Test it: render the same frame as a still and inside a concurrent render, then compare them
(`magick compare -metric AE a.png b.png null:` should print 0). Do not "fix" flicker with `--concurrency=1`: that hides the bug
and blocks Lambda.

## 6. Rendering
`npx remotion render [entry] <comp-id> [out]` (https://www.remotion.dev/docs/cli/render). Flags that matter:
| flag | use |
|---|---|
| `--codec=h264` (default) `h265 vp8 vp9 av1 prores gif` | h264 for social; `prores --prores-profile=4444` for NLE/alpha |
| `--crf=18` | h264 range 1–51, default 18; 16 for masters with fine detail, 20–23 for upload drafts. Not allowed with HW accel |
| `--x264-preset=veryfast` | drafts (≈30% faster on the data documentary); default `medium`; `slow` for final masters |
| `--pixel-format=yuv420p` | default, universally playable; `yuva420p` (VP8/9 alpha), `yuva444p10le` (ProRes 4444) |
| `--color-space=bt709` | **set it** in v4: the default is `default` = bt601, which shifts colors on HD. bt709 becomes the default in v5 |
| `--image-format=jpeg` + `--jpeg-quality=95` | default jpeg (faster); `png` for alpha or exact color; `--sequence` for image frames |
| `--concurrency=6` or `50%` | tabs in parallel; benchmark it (below) |
| `--gl=angle` | GPU for WebGL/three/effects/HTML-in-canvas. See the GPU notes below |
| `--frames=0-59` / `--frames=0,30,90` | range → one video; list → PNG frames (4.0.502+). Ranges combine: `0,30-59,90-` |
| `--scale=0.5` | half-res drafts; `2` for crisp 4K from a 1080 comp (vector content re-rasterizes) |
| `--every-nth-frame=2` | **GIF only**; not a video draft tool |
| `--audio-bitrate=320k` (default) `--audio-codec=aac` `--muted` `--enforce-audio-track` | audio |
| `--props=props.json` `--timeout=120000` `--log=verbose` | props; slow frames; see browser `console.log` |
| `--hardware-acceleration=if-possible` | macOS VideoToolbox (ProRes, h264, h265); use `--video-bitrate` instead of `--crf` |
Put defaults in `remotion.config.ts` (`Config.setChromiumOpenGlRenderer('angle')`, `setCodec`, `setCrf`, `setPixelFormat`,
`setColorSpace('bt709')`, `setConcurrency`, `setDelayRenderTimeoutInMilliseconds`). The Node APIs ignore that file, so pass
the options explicitly there.
- **Stills and contact sheets**: `npx remotion still <id> out.png --frame=45 --scale=0.5` for thumbnails. For many frames,
  bundle once and loop (fast): `const serveUrl = await bundle({entryPoint}); const browser = await openBrowser('chrome',
  {chromiumOptions:{gl:'angle'}}); const composition = await selectComposition({serveUrl, id, inputProps,
  puppeteerInstance: browser}); await renderStill({serveUrl, composition, frame, output, imageFormat:'png',
  puppeteerInstance: browser})`, then `ffmpeg … tile=5x2` or `magick montage` (pass `-font` explicitly on macOS).
- **Programmatic**: `@remotion/bundler` `bundle()` → `@remotion/renderer` `selectComposition()` → `renderMedia({composition,
  serveUrl, codec, outputLocation, inputProps, crf, x264Preset, colorSpace:'bt709', chromiumOptions:{gl:'angle'},
  onProgress})` (https://www.remotion.dev/docs/renderer/render-media). `getVideoMetadata()` is deprecated; use Mediabunny.
- **Benchmark**: `npx remotion benchmark src/index.ts <id> --concurrencies=2,4,6,8 --runs=2 --frames=0-149`. Concurrency
  usually saturates well below the core count. The data documentary on an M1 Pro (10 cores): best 6, 52 ms/frame; 8 was slower.
- **GPU (--gl)** (https://www.remotion.dev/docs/gl-options): v4 default `null` (Chrome decides; headless usually means CPU).
  On macOS use `angle` (Metal) for any WebGL. `swangle` is the CPU fallback: works everywhere, ≈2× slower on a WebGL scene
  (80 vs 170 ms/frame measured). `egl`/`angle-egl`/`vulkan` target Linux GPU servers. v5 makes `angle` the default.
  Known issues: `angle` leaks memory on long renders, so split them with `--frames` and concatenate; GitHub Actions runners
  have no GPU.
- **Cloud**: Lambda (`@remotion/lambda`) is fastest and splits frames across functions; `swangle` only, no GPU, no AV1, output
  ≤≈5 GB. `@remotion/vercel` (`renderMediaOnVercel`). Cloud Run is "Alpha, not actively developed". Client-side
  `@remotion/web-renderer` (`renderMediaOnWeb`) works with `@remotion/media`, not `<OffthreadVideo>`. All of these count as
  Automators renders under the license.
- **Transparent output**: `--image-format=png --pixel-format=yuva420p --codec=vp8|vp9` (.webm, browsers) or
  `--image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444` (.mov, editors).

## 7. Audio in Remotion
- `<Audio src={staticFile('music.mp3')} volume={0.6} trimBefore={2*fps} trimAfter={10*fps} from={fps} loop playbackRate
  toneFrequency muted/>` (https://www.remotion.dev/docs/media/audio). Layer multiple `<Audio>` for music, VO and SFX. A
  `from`/`<Sequence from>` wrapper places a clip; `trimBefore` skips into the file (in frames).
- **Volume curves**: pass a function, `volume={(f) => interpolate(f, [0, fps, dur-1.5*fps, dur], [0, 1, 1, 0], CLAMP)}`.
  `f` is **frames since this audio started**, not the composition frame. Negative values are illegal, so clamp. Keep values
  in 0–1 and fix loudness in the files (stems near -18 LUFS; master the final mix with `scripts/audio_check.py --normalize`). The callback form draws a curve in Studio and is
  faster than re-rendering a numeric prop.
- **Ducking under VO**: precompute a per-frame gain array once in `useMemo` from VO word timings (merge words into phrases,
  bridging pauses <1 s; attack ≈0.35 s before speech, release ≈0.9 s; duck by a dB factor such as `gain = base *
  duckTo**env`, where env is a smoothstep 0..1), then `volume={(f) => gains[Math.min(f, gains.length-1)]}`. Aim for music
  about 9–10 dB under the voice (the data documentary's soundtrack component).
- **VO alignment → animation cues**: store word timings as JSON (`{words:[{text,start,end,line}]}` from WhisperX/ElevenLabs
  timestamps/whisper.cpp tokens). Expose `cue(line, word) → frame = Math.round(start*fps)` and **throw** if the word is
  missing, so a re-voiced take fails loudly instead of desyncing. Land key visual changes 0–2 frames before the word, never after.
- **Beats**: detect beats offline (aubio, librosa, or a known BPM grid: `i*60/bpm + offset`) into `beats.json`. Drive
  accents with a decaying pulse `exp(-(t - lastBeat)*k)` computed from the **global** frame, with the reactive layer
  outside scene Sequences, or pass the global frame down. Snap scene lengths to beat multiples
  (`Math.round(n*60/bpm*fps)`), so cuts and transitions land on beats. Live reactivity uses `visualizeAudio` bass bins (§4).
- SFX: `<Sequence from={cueFrame} durationInFrames={n} layout="none"><Audio src=… volume={…}/></Sequence>`. Normalize SFX
  loudness per file first; peaky clicks and long risers differ by tens of LUFS.
- Pitch (`toneFrequency`): the docs table (https://www.remotion.dev/docs/video-tags) marks it supported for `@remotion/media`,
  but the official skill says it only applies to server renders. Check the render, not the Studio preview.

## 8. Pitfalls → fixes
1. Fallback font in the first frames or a random frame → `loadFont()` at module scope. Measure text only after
   `waitUntilDone()`. Never use system font names without loading them.
2. `interpolate` without clamp overshoots: opacity >1, negative volume (throws), text flying off-screen → clamp both sides.
3. Flicker or jitter in the render but not in Studio → nondeterminism (§5): Math.random, CSS animation, accumulated state,
   `useFrame` clock.
4. `delayRender() … not cleared after 28000ms` → a missing `continueRender`, a blocked network, or a heavy three/WebGL first
   frame (shader compile, big JSON) → label the handles and raise `--timeout`/per-call `timeoutInMilliseconds`. Cache
   parsed data per tab.
5. Big remote video with `<OffthreadVideo>` times out while downloading → use `@remotion/media` `<Video>` (partial reads)
   or copy the file into `public/`.
6. `<Html5Video>` stutters or drifts → switch to `@remotion/media` `<Video>`. H.265, AV1 or ProRes sources fall back to
   OffthreadVideo automatically.
7. CORS errors with `@remotion/media` or `<CanvasImage>` on remote assets → serve with CORS headers, or download to `public/`.
8. Colors look washed or shifted after encoding → `--color-space=bt709` (v4 default is bt601). Use PNG frames for
   color-critical work. Expect some banding on subtle gradients in yuv420p: add a little grain or noise dither, or deliver
   ProRes 4444.
9. Chroma bleed on thin saturated text in yuv420p (4:2:0 halves color resolution) → thicker strokes, less saturated small
   text, or render at `--scale=2` and downscale.
10. Three.js scene black or crawling on CPU → `--gl=angle`, plus `chromiumOptions.gl` in SSR APIs. Set the background via
    `scene.background`, not `gl.setClearColor` (a linear/sRGB double conversion turns the ink grey). With
    postprocessing, render the composer yourself and hold `delayRender` until it has drawn this frame.
11. Multiple scenes each mounting a `<ThreeCanvas>` → WebGL context churn and a slow first frame per tab. Keep **one**
    persistent canvas for the whole film and drive its state per scene.
12. `<Sequence>` inside `<ThreeCanvas>` crashes (it adds a div) → `layout="none"`.
13. Scene pops in with a blank or late asset → `premountFor={fps}` on Sequences and TransitionSeries sequences
    (media also has `premountFor`, 4.0.495+).
14. Composition shorter than expected with transitions → total = Σ scenes − Σ transitions. Compute it, never hard-code it.
15. Studio preview stutters but the render is fine → lower preview quality or use scale; preview speed says nothing about
    the render. Check real output with `--frames` renders and stills.
16. `--every-nth-frame` on mp4 fails → it's GIF-only. For drafts use `--scale=0.5 --x264-preset=veryfast --frames=a-b`.
17. HTML-in-canvas effects or transitions blank in Studio → Chrome ≥149 plus the `#canvas-draw-element` flag.
    Renders need nothing; WebGL ones need `--gl=angle`.
18. Version mismatch errors (`remotion` vs `@remotion/*`) → exact pins, all one version, `npx remotion versions`.
    npm cooldown policies (e.g. min-release-age) reject a just-published version that `create-video` pinned → pin
    everything to the newest release older than the cooldown (tested: 4.0.529 → 4.0.526). If `npx remotion add` fails on npm
    policy flags, run `npm i --save-exact @remotion/x@<same version>`.
19. `remotion.config.ts` settings "ignored" in scripts → the config file is CLI/Studio-only; pass the options to
    `renderMedia`/`renderStill`.
20. Long renders on `angle` crash near the end (GPU memory leak) → split into `--frames` chunks and concat with
    `ffmpeg -f concat -c copy`; also try `--concurrency` lower.
21. Moiré or shimmer on dense 1–4 px grids when the camera moves → whole-pixel pitch, no sub-pixel drift, and no chromatic
    aberration on fine lattices.
22. Grain or noise inflates bitrate and x264 time → keep grain subtle (size ≥2 px), use CRF 18–20 for uploads, and
    `veryfast` for previews.
23. Browser `console.log` invisible during render → `--log=verbose` (or `console.warn`).

## 9. Lessons from past productions
**A 60 s data documentary** (Remotion 4.0.526 + R3F 9.7 + postprocessing; 58k-particle data film, 1800 frames, 4:5 + 16:9).
Worth copying:
- Exact-pinned, same-version `@remotion/*`. `remotion.config.ts` sets `angle`, jpeg 95, h264 CRF 16, yuv420p, **bt709**,
  concurrency 6 (benchmarked), delayRender timeout 120 s, and `setOverwriteOutput(true)`.
- One component serves two aspect ratios: two `<Composition>`s share it, a unit `u = min(w,h)/100` scales type, and a
  `useLayout()` safe area positions it. A zod schema (`lang`, `captions`, `showSafeArea`, `musicVolume`) enables Studio
  toggles. Lab compositions for engine proofs sit in a `<Folder>`.
- Fonts: `@remotion/google-fonts` at module scope with limited weights and `latin-ext`, loaded by importing `theme.ts` in Root.
- Data and VO alignment load through `useDelayRender` with labels and a per-tab cache. Hash PRNG (`hash32`, `rand01(i,
  salt)`), `@remotion/noise` seeded by strings, no `Math.random`. Determinism **proven**: still vs a 6-tab render → 0 px
  diff, identical SHA-1.
- One persistent `<ThreeCanvas>` for all 1800 frames, `flat`, `preserveDrawingBuffer`, `dpr` = render scale. A frame guard
  (`delayRender` in `useLayoutEffect`, released after the composer draws) protects each tab's first frame.
- `scripts/stills.mjs`: one bundle + one browser → dozens of stills in seconds for contact sheets. Scene reviews use
  `--frames=a-b --x264-preset=veryfast`.
- Audio: a per-frame music gain array (fades, phrase-merged dB ducking, section boosts), a per-file SFX LUFS/true-peak
  normalization table, a VO stem hash-named after the alignment so a stale mix never plays, and `ctx.cue(line, word)` that
  throws on missing words.
Diverges from current official guidance:
- Uses legacy `Html5Audio`; the recommendation for new code is `<Audio>` from `@remotion/media`.
- Uses R3F `useFrame(cb, 1)` as a **render callback** to drive the composer. It is safe only because it ignores
  clock and delta; the official skill forbids `useFrame`, so document the exception if you copy it.
- Overlays animate `transform` template strings and no `Interactive.*`, so Studio can't edit keyframes (render output is fine).
  No `premountFor`. Scene lengths are hard-coded to 1800 instead of derived via `calculateMetadata` (fine for a fixed 60 s cut).
- Symlinked `public/data` and `public/audio` need a prepare script. `getStaticFiles()` moves to `@remotion/studio` in v5.
- Uses its own canvas `measureText` instead of `@remotion/layout-utils`.
**A 40 s conference proof of concept** (4.0.468, 5 data-driven scenes from JSON): good spring use
(`damping 190`, no bounce), deterministic pulse `sin(frame/28)`, `staticFile` + `<Img>`. Weak points: `^4.0.0` caret ranges,
fonts named (`Inter`, `JetBrains Mono`) but never loaded (silent fallback on other machines), hard cuts via plain
`<Sequence>`, no premount, `transform` strings, no audio.

## 10. Minimal working example (tested plumbing, not a design reference)
It proves the mechanics (fonts, springs, transitions, a beat grid, audio curves); its frame 0 is
not a poster and its slide transition is the kind of default the house taste avoids. Kinetic title
with staggered spring words, a spring-timed slide transition, a dot pulsing on a 120 BPM beat grid from
`beats.json`, and music with a fade curve. Setup: `npx remotion add @remotion/transitions @remotion/media
@remotion/google-fonts`, `public/beat.wav`, `src/beats.json` = `{"bpm":120,"beats":[0,0.5,1,1.5,2,2.5]}`.
```tsx
// src/Kinetic.tsx
import {Audio} from '@remotion/media';
import {loadFont} from '@remotion/google-fonts/Anton';
import {springTiming, TransitionSeries} from '@remotion/transitions';
import {slide} from '@remotion/transitions/slide';
import {AbsoluteFill, Easing, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import beatMap from './beats.json'; // {bpm, beats: seconds[]} from a beat tracker / VO aligner

// Blocks rendering until the font files are loaded (no fallback-font flash).
const {fontFamily} = loadFont('normal', {weights: ['400'], subsets: ['latin']});
const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const SCENE = 48;
export const TRANSITION = 14;

// 1 on each beat, decaying to 0: a pure function of the frame, so any tab renders it identically.
const beatPulse = (frame: number, fps: number) => {
  const t = frame / fps;
  const past = beatMap.beats.filter((b) => b <= t);
  return past.length === 0 ? 0 : Math.exp(-(t - past[past.length - 1]) * 9);
};

const Word: React.FC<{text: string; index: number}> = ({text, index}) => {
  const frame = useCurrentFrame(); // local to the enclosing TransitionSeries.Sequence
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, delay: index * 4, config: {damping: 200}});
  return (
    <span style={{display: 'inline-block', marginRight: '0.22em', opacity: enter,
      translate: `0 ${interpolate(enter, [0, 1], [90, 0])}px`}}>
      {text}
    </span>
  );
};

const Title: React.FC<{text: string; bg: string}> = ({text, bg}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{backgroundColor: bg, justifyContent: 'center', alignItems: 'center'}}>
      <div style={{fontFamily, fontSize: 150, lineHeight: 0.95, color: '#F4F1EA', textAlign: 'center',
        textTransform: 'uppercase', padding: 100,
        scale: interpolate(frame, [0, 1.5 * fps], [1.12, 1], {...CLAMP, easing: Easing.bezier(0.16, 1, 0.3, 1)})}}>
        {text.split(' ').map((w, i) => <Word key={i} text={w} index={i} />)}
      </div>
    </AbsoluteFill>
  );
};

// Lives OUTSIDE the TransitionSeries, so useCurrentFrame() is the global frame = audio time.
const BeatDot: React.FC = () => {
  const p = beatPulse(useCurrentFrame(), useVideoConfig().fps);
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 150}}>
      <div style={{width: 64, height: 64, borderRadius: 32, backgroundColor: '#FF5A36',
        scale: 1 + 0.7 * p, opacity: 0.45 + 0.55 * p}} />
    </AbsoluteFill>
  );
};

export const Kinetic: React.FC = () => {
  const {fps, durationInFrames} = useVideoConfig();
  return (
    <AbsoluteFill>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={SCENE} premountFor={fps}>
          <Title text="Make it move" bg="#101014" />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({direction: 'from-right'})}
          timing={springTiming({config: {damping: 200}, durationInFrames: TRANSITION})} />
        <TransitionSeries.Sequence durationInFrames={SCENE} premountFor={fps}>
          <Title text="On the beat" bg="#1B2CC1" />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <BeatDot />
      <Audio src={staticFile('beat.wav')}
        volume={(f) => interpolate(f, [0, 6, durationInFrames - 12, durationInFrames], [0, 1, 1, 0], CLAMP)} />
    </AbsoluteFill>
  );
};
// Root.tsx: <Composition id="Kinetic" component={Kinetic} fps={30} width={1080} height={1350}
//   durationInFrames={SCENE * 2 - TRANSITION} />  (transitions overlap: 48 + 48 - 14 = 82)
```
Verified 2026-09-26 in a scratch project (create-video blank, Remotion 4.0.526, Node 26, macOS 27). `tsc --noEmit`
is clean. `npx remotion render Kinetic out/kinetic-2s.mp4 --frames=0-59 --scale=0.4 --x264-preset=veryfast
--color-space=bt709 --concurrency=4` finished in 9.2 s wall time: h264 432×540, yuv420p, bt709, 60 frames, 30 fps, plus
AAC 48 kHz stereo audio. Frames checked: the dot peaks at frame 30 (beat at 1.0 s), the slide pushes scene A out over
frames 34–48, and the words stagger in. `render --frames=0,30,59 --image-format=png` and `still --frame=45` also work.
