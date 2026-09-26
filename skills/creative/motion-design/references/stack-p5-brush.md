# p5.js 2 + p5.brush: the hand-made look

Verified 2026-09-26: p5 **2.3.4** (LGPL-2.1), p5.brush **2.2.3** (MIT, https://github.com/acamposuribe/p5.brush).
Patterns below come from a 64 s animated cumbia lyric video (1,536 frames, six scene animators in parallel)
built on the MIT starter kit https://github.com/JohnHeibel/ClaudeAnimationBase, which wraps p5.brush
for character animation and headless rendering. Read the kit's animation guide before a character piece.

## When to pick it

- Watercolor, ink, pencil, hatching, paper: a piece that should feel drawn by a person, not generated.
- Character animation with personality (a mascot, a crew, a crowd) where squash, stretch, arcs and boil
  carry the charm.
- Generative data-art where each mark is a real data point and texture comes from the medium.

Skip it for crisp UI, data charts with exact values, or photoreal work. It's GPU-bound and slower than
DOM or plain canvas: budget ~150–450 ms per frame for a busy scene at 1080p.

## Setup

Two builds (README, "Two builds"):

| | p5 build (`p5.brush`) | Standalone (`p5.brush/standalone`) |
|---|---|---|
| Needs | p5.js 2.x + `createCanvas(w, h, WEBGL)` | WebGL2 only; `brush.createCanvas(w, h)` |
| Seeding | p5 `randomSeed()` / `noiseSeed()` | `brush.seed()` / `brush.noiseSeed()` |
| Frame flush | automatic at the end of `draw()` | `brush.render()` at the end of each frame |

Core calls: `brush.scaleBrushes(k)` for built-in brushes at video size, `brush.set(name, color, weight)`,
`brush.fill(color, opacity)` with `brush.fillBleed()` / `brush.fillTexture()` for watercolor,
`brush.wash()` for flat color, `brush.hatch(dist, angle)`, then `brush.line/rect/circle/arc/polygon` or
`beginShape`. Custom brushes via `brush.add()` (the online Brush Maker generates the code); vector
fields via `brush.field()` / `brush.addField()` bend strokes organically. In ES-module setups use p5
instance mode and call `brush.instance(p)` first.

Wrap the library in two or three house functions (`paint(points, {wash|fill, ink, sw, bleed, tex, hatch})`,
`inkLine()`, `glow()`) and never call plain p5 shapes, so every mark shares the medium.

## Frame-pure architecture

p5's `draw()` loop is a real-time clock. Turn it off and draw from `t`:

```js
let T = 0, loaded;
window.__meta = {width: 1920, height: 1080, fps: 24, duration: 64};
window.__ready = new Promise(r => (loaded = r));   // resolve after fonts and assets (see the font gate below)
function setup() { createCanvas(1920, 1080, WEBGL); pixelDensity(1); noLoop(); fontsReady.then(loaded); }
function draw() { drawWorld(T); composite(T); }     // composite = paper grain + type onto the visible canvas
window.__seek = async t => { T = t; await redraw(); };  // redraw() runs draw() once; await it in p5 2.x
```

`scripts/render_frames.py page.html --gpu --out out/v01.mp4` then seeks and screenshots every frame. The
starter kit's own `render.mjs` uses the equivalent `window.ready` + `renderAt(t)` → `toDataURL` contract
with resumable frame files; either works.

- **Seed per element, per boil frame.** Linework re-draws ("boils") 12 times a second. Reseed before
  every separate element so one moving element doesn't shift the random stream of everything after it:
  ```js
  const BOIL = 12, boilN = t => Math.floor(t * BOIL);
  const boilSeed = (key, t) => { let h = 2166136261;
    for (const c of key + '|' + boilN(t)) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
    randomSeed(h >>> 0); noiseSeed(h >>> 0); };   // boilSeed('bg-hill', t) before drawing the hill
  ```
  Stable per-object traits (skin, hat, dance phase) come from `hash(i)`, never `Math.random()`.
- **Animate on twos** where it helps the hand-made feel: `onTwos = t => Math.floor(t * 12 + 1e-6) / 12`.
- **Timing comes from data.** A generated `lyrics_data.js` / cue sheet holds every line, word and beat;
  scenes read `SONG.lines[i].start`, never copied numbers. Swapping a take is rerunning two scripts.
- **Shots register absolute ranges** (`shots([[t0, fn], …])`), one file per scene, so parallel animators
  own disjoint time and files.

## Texture: paper, grain, boil

- Paint a paper layer under everything (soft radial stains + short fibre strokes), and composite a static
  grain + radial vignette over the finished frame with `multiply`, so pigment and even crisp type sit
  *in* the paper:
  ```js
  c.drawImage(sceneCanvas, 0, 0); drawLetters(c);
  c.globalCompositeOperation = 'multiply'; c.drawImage(grainCanvas, 0, 0);
  c.globalCompositeOperation = 'source-over';
  ```
- Light is additive (`glow()`), not pigment: watercolor mixing turns yellow-on-blue green.
- No pure black or white; ink and cream from the palette.
- An orange body on an orange ground needs a cream halo or offset stroke to separate.

## Character acting

- One literal, funny, paintable image per line of script or lyric. The gag must read with the sound off.
- Act with body, eyes and emotes. If the character design has no mouth, don't lip-sync.
- Helpers that earned their keep (all pure functions of `t`):
  ```js
  const seg = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));
  const spring = (t, t0, k = 6, w = 18) => t < t0 ? 0 : Math.exp(-k * (t - t0)) * Math.sin(w * (t - t0));
  const arcPt = (p0, p1, h, k) => [lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k) - h * 4 * k * (1 - k)];
  function jump(t, t0, t1, h = 3) {                 // crouch, stretch on the arc, squash-land and settle
    if (t < t0 - 0.12) return {dy: 0, sq: 0};
    if (t < t0) return {dy: 0, sq: 0.18 * ease(seg(t, t0 - 0.12, t0))};
    if (t < t1) { const k = (t - t0) / (t1 - t0); return {dy: -h * 4 * k * (1 - k), sq: -0.16 * Math.abs(1 - 2 * k)}; }
    const a = t - t1; return {dy: 0, sq: 0.22 * Math.exp(-8 * a) * Math.cos(20 * a)};
  }
  ```
- Thrown props travel on `arcPt` and land on a beat; costume changes are mode switches with a flash on
  the downbeat.
- Crowds: give neighbours different skin, clothing, hair, dance style and beat phase (`crowdMember(i)`),
  and mirror the lead hand per seed, or the crowd reads as clones.
- Attach props through rig hooks (`armR: (u, sw) => flag(u, sw, t)`); un-rotate the model matrix so a
  pole stays upright at any arm angle.

## Beat sync

```js
const bpOf = t => (t - OFF) / BEAT, beatN = t => Math.floor(bpOf(t)), frac = x => x - Math.floor(x);
const pulse = (t, k = 6) => Math.exp(-frac(bpOf(t)) * k);                 // 1 on the beat, decays
const bAt = t => OFF + Math.round((t - OFF) / BEAT) * BEAT;               // snap a hit to the grid
const stepX = (t, t0, x0, step, n) => {                                    // one eased step per beat
  const b = Math.min(n, Math.max(0, bpOf(t) - bpOf(t0))), i = Math.floor(b); return x0 + step * (i + ease(b - i)); };
```

Landings, slaps, stomps, flashes and cuts all go through `bAt()`. End cards build one element per beat,
then hold. Get `BEAT` and `OFF` from `scripts/beats.py`, not from the prompt's BPM.

## Transitions

Hard cuts on the beat or on action are the default. When a seam needs a transition, it must be
motivated by the content, and each scene owns one half so parallel animators join cleanly:

```js
// outgoing shot, last 0.3 s:  if (lt > dur - 0.3) wipe((lt - (dur - 0.3)) / 0.6);   // p 0 → 0.5 covers
// incoming shot, first 0.3 s: if (lt < 0.3) wipe(0.5 + lt / 0.6);                  // p 0.5 → 1 uncovers
// cut at p = 0.5 under full cover; draw in screen space after the camera ends
```

Motivated examples from the music video: a leap off frame right continuing mid-leap from the left (cut on
action), a close-up whose pose matches the next scene's opening (match cut), an iris closing onto the face
the next scene is about, a whip smear led by a thrown prop. A brush wipe used at every seam is a menu, not a
decision.

## Type in a hand-drawn world

- Lyrics or captions over a drawn world: painted paper-cut underlays with ragged edges, crisp type on top,
  a sub-pixel per-boil offset (`typeBoil`) so the type belongs, all under the paper grain.
- Pick a style by meaning: karaoke for sung lines (ghost unsung words at 30%, fill each word with a clip
  rect as it's sung, a 7% bump over 0.24 s), a terminal card for commands, a diff card for before/after
  jokes, a title plate for the brand line (opaque impact frame at scale 1.7 easing to 1, no fade-in).
- Compute contrast for every text/underlay pair; a low-contrast brand color (orange on cream, 2.9:1)
  becomes an underline under ink type, never the type itself.
- Reserve screen bands for words in the storyboard and keep action out of them; assert per frame that
  text boxes don't intersect character boxes. Pre-split long lines in the data instead of trusting wrap.
- **Font gate:** never capture a frame with a fallback face.
  ```js
  const fontsReady = Promise.all(SPECS.map(s => document.fonts.load(s, 'AaÁñ¿¡')));
  let core = false, fonts = false;
  Object.defineProperty(window, 'ready', {configurable: true, get: () => core && fonts, set: v => { core = v; }});
  fontsReady.finally(() => { fonts = true; });     // the kit's renderer waits for window.ready === true
  ```
  With `render_frames.py`, resolve `window.__ready` only after `fontsReady` instead.
- Vector logos: draw them from their SVG paths. A PNG loaded from `file://` taints the canvas and breaks
  `toDataURL`.

## Rendering

- Capture on the GPU (`render_frames.py --gpu` = ANGLE on Metal; SwiftShader is the silent headless
  default and much slower). The capture loop, flags and trade-offs are in
  [stack-html-frames.md](stack-html-frames.md).
- p5.brush is GPU-bound: extra worker tabs in one Chrome don't help. Two separate processes on disjoint
  ranges gave 1.3–1.6×; three sometimes, more caused page-load timeouts. Stagger launches 1–2 s, run them
  in tmux, and render finished scenes first while the last scene is still being animated.
- Make the frame writer resumable (skip existing frames, write `.tmp` then rename) and finish with a pass
  that fills gaps. Delete old frames before a full render whenever duration or fps changed.
- Measure per-element cost in bench loops (a character ~26–64 ms, 110 confetti ~84 ms) and keep a scene
  budget (≤450 ms/frame) so the render fits the deadline.
- JPEG frames (q ≈ 0.94) are faster to write but encode as full-range BT.601 (`yuvj420p`): convert on
  export (`scripts/export_social.py` does it). Pad audio to the video length before muxing; `-shortest`
  truncates.

## Pitfalls

| Symptom | Fix |
|---|---|
| Strokes collapse to a dot under camera zoom | Draw around the shape's own center, not far from the origin |
| Outlines get fat in close-ups | Scale stroke weight down with zoom |
| An unrelated OffscreenCanvas error | A `NaN` in a point list; validate points |
| Held prop drawn behind the hat brim | Draw it from the rig's draw hook with the arm transform |
| Everything jitters when one element moves | Missing per-element `boilSeed(key, t)` |
| Frame 0 is blank paper (fade-up) | Frame 0 is the poster: `scripts/poster_frame.py`, or design the first frame |
| Render needs the network | Local fonts and assets only; a Google Fonts link can stall headless capture |
| Brand logo painted as scenery by an animator | Put "no product logos" in the shared rules; grep scene code before the final render |
| Concept frames drift off-model | Generate a model sheet first, pass it as reference, crop labels; use frames only as palette/composition guides |
