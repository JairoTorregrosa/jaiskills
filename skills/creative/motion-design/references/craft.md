# Craft and taste: motion design for code-driven video

Load this when planning tokens, building scenes, or critiquing a cut. Every rule is a default you can
break *on purpose for this brief*. Never break one because you forgot it. Source tags like [HEER] are
listed at the end. "Derived" marks our own arithmetic built on a cited base.

## 0. Units and the video-vs-UI gap

- Think in frames. At 30 fps, 1 f = 33.3 ms. At 60 fps, 1 f = 16.7 ms. 24 fps reads as cinema, 30 is the
  social default, and 60 suits screen recordings and fast UI demos. Store durations as seconds and
  convert with `Math.round(s * fps)` so the piece re-times cleanly when fps changes.
- UI motion guidance answers user input, so it is fast: Carbon uses 70–700 ms, M3 50–1000 ms, and
  Kowalski keeps UI under 300 ms [CARBON][M3-TOK][EMIL]. In video the motion *is* the content and the
  viewer can't replay it. Make anything the viewer must read or track **1.5–2× UI length**, and keep
  exits UI-fast (derived).
- Duration grows with the distance or area covered. Small moves are short and full-frame moves are
  long [M3-ED][CARBON]. Carbon's duration scale is non-linear, so a move that goes twice as far takes
  less than twice as long [CARBON].

| Job (30 fps) | Frames | ms | Basis |
|---|---|---|---|
| Micro accent (tick, highlight, color change) | 3–6 | 100–200 | Carbon fast/moderate 70–150 ms |
| Small entrance (label, icon, chip) | 10–15 | 330–500 | M3 emphasized-decelerate enter 400 ms |
| Large or full-frame entrance, scene transform | 15–24 | 500–800 | M3 long 500 ms, extra-long 700–1000 ms |
| Data transition, per stage | 24–30 | 800–1000 | Heer & Robertson: ~1 s per stage |
| Exit (leaves for good) | 6–10 | 200–330 | M3 emphasized-accelerate 200 ms; exits need less attention |
| Hold after a reveal ("the breath") | ≥30 | ≥1000 | §2 |

**On-screen reading time.** Subtitle guidance is 160–180 wpm, which is 0.33–0.375 s per word, with a
floor of about 0.3 s per word (4 words ≈ 1.2 s) [BBC]. Each caption stays up for at least 5/6 s and at
most 7 s, at ≤20 characters per second for adults [NETFLIX]. Adults read plain text silently at about
238 wpm [BRYSBAERT], but video viewers are also watching the picture, so budget at subtitle rate.
- Rule (derived): `holdFrames ≥ fps × (max(0.83, 0.35 × words) + 0.4)`. The +0.4 s covers finding the
  text. Start counting when the text **stops moving**, not when it starts entering. 1–2 words ≈ 37 f,
  5 words ≈ 65 f, 10 words ≈ 117 f @30. If a block needs more than 3 s, split it into beats.

## 1. The principles, translated for code

### Easing vocabulary
Choose the curve by what the element does relative to the frame [M3-ED][CARBON][EMIL].

| Role | Curve | Values (CSS cubic-bezier) |
|---|---|---|
| Enter (appear, arrive) | decelerate / ease-out | M3 emphasized-decelerate `(0.05, 0.7, 0.1, 1)` · Carbon entrance-expressive `(0, 0, 0.3, 1)` · Kowalski strong `(0.23, 1, 0.32, 1)` |
| Exit for good | accelerate / ease-in | M3 emphasized-accelerate `(0.3, 0, 0.8, 0.15)` · Carbon exit-expressive `(0.4, 0.14, 1, 1)` |
| Move A→B on screen, or exit that may come back | ease-in-out | M3 standard `(0.2, 0, 0, 1)` · Carbon standard-expressive `(0.4, 0.14, 0.3, 1)` · Kowalski `(0.77, 0, 0.175, 1)` |
| Calm or utility element | productive | Carbon standard-productive `(0.2, 0, 0.38, 0.9)` |
| Continuous or mechanical motion | linear | Clock hands, marquees, progress fills, slow ambient drift, time mapped to x |

- An exit that ends at full speed says "gone for good". One that slows to a stop just off-frame says
  "can come back" [M3-ED][CARBON].
- Never use ease-in on an entrance. It starts slow at the exact moment the viewer is watching [EMIL].
  Linear position on a discrete move reads as robotic: "strictly linear movement appears unnatural"
  [CARBON].
- **What reads as expensive:** a fast take-off and a long, soft landing, with 60–70% of the travel in
  the first third of the time. M3 describes this as "snappy take offs and very soft landings" [M3-ED].
  The M3 emphasized curve is an Android path. On web, M3's own fallback is standard `(0.2, 0, 0, 1)`
  [M3-ED][M3-TOK].
- **Build a system, not a default.** Define 3 curves (enter, exit, move) and 1–2 springs as named
  tokens, and signal hierarchy through *duration, distance and stagger*. "Related movements have a
  unified relationship" [CARBON]. The same curve for the same *role* is a system. The same curve and
  duration on every element regardless of mass or role is a slop tell (§8).

### Springs (overshoot, done with numbers)
- Springs apply to *spatial* properties (position, scale, rotation, size), which may overshoot.
  *Effects* (opacity, color) must use a critically damped spring (ζ = 1) or a curve, and never
  overshoot [M3-PHYS].
- M3 moved to springs in May 2025 and no longer maintains the easing-and-duration system [M3-ED].
- Conversion math: ζ is the damping ratio, k the stiffness, m the mass. A damping *coefficient*
  (Remotion's `damping`) = `2·ζ·√(k·m)`. Overshoot = `e^(−πζ/√(1−ζ²))`. Time to settle within 2% ≈
  `4/(ζ·√(k/m))` s.

| Token | ζ / k | Remotion `{mass:1, damping, stiffness}` | Overshoot | Settle |
|---|---|---|---|---|
| M3 expressive fast spatial | 0.6 / 800 | damping 33.9, stiffness 800 | 9.5% | 0.24 s |
| M3 expressive default spatial | 0.8 / 380 | damping 31.2, stiffness 380 | 1.5% | 0.26 s |
| M3 expressive slow spatial | 0.8 / 200 | damping 22.6, stiffness 200 | 1.5% | 0.35 s |
| M3 standard default spatial | 0.9 / 700 | damping 47.6, stiffness 700 | 0.2% | 0.17 s |
| Video hero move (derived) | 0.7 / 120 | damping 15.3, stiffness 120 | 4.6% | 0.52 s |
| **Remotion default** | 0.5 / 100 | damping 10, stiffness 100 | **16.3%** | 0.80 s |

Token values are from [M3-COMPOSE] and the Remotion defaults are from [REMOTION]. Remotion's default
bounces 16%, so always set `damping` explicitly.

- **Overshoot budget:** 0% for serious or productive work (Carbon rules out easing that "suggest[s]
  bounce, stretch, or sudden stops" [CARBON]). 1–5% for expressive premium. 8–12% for playful accents.
  Above 15% looks like a toy, so use it only when the brand is a toy. Overshoot the one hero element,
  never the whole frame.

### Anticipation
- Put a small counter-move before a big move: 3–6 f backward by 3–8% of the travel, or scale to
  0.96–0.98 before growing. Anticipation lets you "queue your audience's expectations" [SOM-ANT]. Heer &
  Robertson cite anticipation and staging as ways to direct attention [HEER].
- The motion-graphics form of anticipation is a setup: a line, highlight or camera drift lands where
  the next thing will appear 4–8 f before it appears. A J-cut is anticipation in sound (§2).
- Spend anticipation on the hero move of each scene. When everything anticipates, it becomes a tic.

### Follow-through and overlapping action
- Children lag their parents. School of Motion staggers a chain "one frame each", and uses two frames
  when the object should feel softer [SOM-FT].
- Stagger sibling groups by 2–4 f @30 (60–130 ms). For UI, Kowalski uses 30–80 ms [EMIL]. Cap the
  total spread at about 15 f however many items there are: `stagger = min(3f, 15f/(n−1))` (derived).
- Stagger outward from the cause, whether that's the origin of the action, reading order or the
  direction of motion. Never stagger in random order.
- Secondary parts settle 2–6 f after the main body: underline after word, label after bar, shadow
  after object.
- Offset properties within one element: opacity reaches 100% by about 40% of the move, and scale lags
  position by 1–2 f. Starting and stopping all properties on the same frame looks mechanical.

### Squash and stretch: use restraint
- In brand, type and UI motion, keep non-uniform scale within ±3–8%, preserve area
  (`scaleX·scaleY ≈ 1`), and apply it only on impacts or very fast moves.
- Never squash letterforms or logos. For fast moves, use motion blur instead: a 180° shutter, meaning
  blur across half the frame interval.

### Arcs
- Organic things travel on arcs, while UI and mechanical things travel straight. For an arc, ease x
  and y differently or animate along a path.
- Keep data marks on straight paths. Translation and expand/contract are easier to follow than
  rotation [HEER].

### Secondary action
- Allow one supporting motion per primary, at ≤25% of the primary's amplitude and lower contrast, for
  example a background moving at ¼ speed or a caption tick. If it competes for the eye, cut it.

### Staging and hierarchy: one focal point per moment
- For every shot, decide where the eye is at its first frame and where it must be at its last. Move
  only the thing you want looked at, and hold everything else still or dimmed. Aim for 1 primary and
  at most 1 secondary motion at a time.
- Across a cut, place the next focal point near where the eye already is ("eye-trace") [MURCH].
- Group elements that change the same way ("common fate"), minimize occlusion, and stage complex
  changes as simple steps [HEER].

### Exaggeration and solid drawing
- Exaggerate the one idea: a bigger hero number, a longer hero move, a harder stop. Keep everything
  else calm. Spend boldness in one place [FD].
- "Solid drawing" in code means **solid layout on every frame, not just keyframes**. Mid-transition
  frames must still hold the grid, margins and type scale. Intermediate states should "remain valid
  data graphics" [HEER]. Check frames at 25%, 50% and 75% of every transition (§9).
- Weight comes from timing. Heavy objects start slowly and barely overshoot. Light objects start fast
  and overshoot more.

## 2. Rhythm and editing

- **Murch's rule of six**, in priority order: emotion 51%, story 23%, rhythm 10%, eye-trace 7%, 2D
  plane 5%, 3D space 4%. When you can't satisfy all six, sacrifice from the bottom, because "emotion is
  worth more than all five of the things underneath it" [MURCH]. Cut when the *feeling* is complete,
  not when the animation is.
- **Shot length.** The average Hollywood shot fell from about 12 s in the 1950s to under 4 s in the
  2000s [CUTTING]. Short social video runs faster and must vary: a metronomic scene length (every
  scene exactly 3 s) is a tell.

| Format | Beats/shots | Typical shot | Notes (derived from the above + §7) |
|---|---|---|---|
| 15 s opener or ad | 4–7 | 1.5–3 s | Hook ≤2 s, one idea, button in the last 1.5–2 s |
| 30 s | 8–14 | 1.5–3.5 s | One turn at around 40–50% |
| 60 s explainer | 12–25 scenes | 2.5–6 s | Longer holds for reading; each mechanism step gets its own scene |
| 60–90 s music video | 20–60 | 1–8 bars | Cut on downbeats; change scenes on 4- or 8-bar phrases |

- **Beat maths.** `framesPerBeat = fps × 60 / BPM`. At 120 BPM and 30 fps that's 15 f per beat and 60 f
  per 4/4 bar. For BPMs that don't divide evenly (128 BPM = 14.06 f), compute each cut as
  `round(n × fps × 60 / BPM)` from zero. Summing rounded beats drifts off the music.
- **Cut on action.** Cut 1–3 f into a movement so the motion hides the cut [SB-CUTS]. In graphics,
  whatever leaves shot A keeps its direction into shot B.
- **J and L cuts.** In a J-cut the sound of B starts before its picture; in an L-cut the sound of A
  carries over B [SB-CUTS]. Pre-lap audio 6–12 f to pull the viewer forward. Let music or a line tail
  0.5–1.5 s to let a feeling linger.
- **Match cuts and graphic matches** carry shape, position or color across a cut [SB-CUTS]. In code
  they're cheap: morph circle A into circle B, or carry a line through. Make it the piece's signature
  transition once or twice and use hard cuts everywhere else. "I used to have to convince my junior
  animators to just use a cut" [GRANDIN].
- **Sound sync.** Viewers detect audio leading picture by about 45 ms and audio lagging by about
  125 ms; acceptability limits are about +90/−185 ms [ITU1359]. Land hits within ±1 f @30. If you
  must err, let sound trail by a frame rather than lead.
- **Hold for payoff.** After a reveal, keep nothing else moving for ≥1–1.5 s. Let the music thin out
  or drop. "Maybe we just need to stop and not animate anything here and make the music really good"
  [GRANDIN].
- **Escalation.** Sketch an energy curve (0–10) per beat. Each beat should be bigger, closer, faster or
  more surprising than the last, peaking at about 75–85% of runtime. Contrast *in time* (fast vs.
  still, loud vs. silent, dense vs. empty) is what gives a piece rhythm.
- **End on a button.** The last beat is a punch: an image, line or sound that closes the loop opened by
  the hook, held 1.5–2.5 s, followed by one clear action. For social, consider making the last frame
  match the first for a seamless loop.

## 3. Typography in motion

**Size floors at phone viewing size** (derived from Apple's 17 pt default and 11 pt minimum text
[HIG-TYPE], and BBC caption line heights [BBC]). A 1080-px-wide frame shown about 390–430 pt wide on a
phone gives 1 pt ≈ 2.5–2.8 px. A 1920-px-wide 16:9 frame letterboxed on a portrait phone gives 1 pt ≈
4.9 px.

| Canvas | Floor (source line, legal) | Body / caption | Headline | Hero word or number |
|---|---|---|---|---|
| 1080×1920 (9:16) | 32 px | 48–64 px (BBC: line height 3.9–4.5% of height ≈ 75–86 px) | 80–120 px | 140–260 px |
| 1080×1350 (4:5) | 32 px | 48–60 px | 76–110 px | 130–220 px |
| 1920×1080 (16:9), mobile-first | 54 px | 64–84 px (BBC: line height 7–8% ≈ 76–86 px) | 96–140 px | 160–280 px |
| 1920×1080, desktop or TV only | 36 px | 48–60 px | 72–110 px | 140–240 px |

- **Words per beat.** One idea per text beat, ≤7 words for social (about 2 s at subtitle rate). A single
  block is ≤2 lines for headlines. Captions are ≤2 lines at 16:9 and ≤3 at 9:16, ≤42 characters per
  line [NETFLIX], and about 25 characters per line across 90% of a 9:16 frame [BBC]. Anything longer
  becomes a sequence.
- **Break lines by meaning.** Break at punctuation. Don't split an article from its noun, a
  preposition from its phrase, or a name [BBC]. Every line should survive being read alone.
- **Weights.** Moving display type usually wants 600–900. Keep body text on video at ≥500. Thin weights
  and hairline serifs shimmer and break up under H.264 at small sizes, so keep hairlines ≥60 px.
- **Tracking.** Tighten large display type by −1 to −3%. Loosen small labels by +2–5%. Animating
  tracking as the effect ("tracking-in") is a template move unless the meaning is expansion.
- **Designed vs. templated kinetic type.** Designed type moves *as the meaning*: "grow" scales,
  "split" divides, "stop" stops hard. Reveals follow the stroke direction or the voiceover syllables,
  and type interacts with the image (occlusion, depth, masking by an object). Saul Bass treated type
  and symbol as "simple, direct ideas" [BASS] and invented "a new type of kinetic typography" for
  Hitchcock [AOTT]. Templated type uses per-letter fade-ups on every line, typewriter effects for
  non-computer content, per-letter bounce, 3D flips per word, and random-order letter reveals.
- Text becomes legible 0–3 f before the voiceover says it, or exactly with it. Never after.
- Use tabular (monospaced) figures for any number that animates so digits don't jitter. Land count-ups
  on the exact final value and hold.
- **Caption style.** Sentence case, a plate at 60–75% dim or a 1–2 px shadow or stroke, and the same
  position throughout. At 9:16, sit captions in the lower third but above the platform UI (§4), and
  never over mouths, faces or on-screen text [BBC].

## 4. Composition and camera

- **Vertical 9:16 safe zones.**
  - Meta, unified Reels and Stories since March 2026: keep text and logos out of the top 14% (≈270 px),
    the bottom 35% (≈670 px) and 6% (≈65 px) on each side [META-SAFE].
  - TikTok: 108 px top, 320 px bottom, 60 px left, 120 px right [TT-SAFE].
  - Cross-platform box (derived): x 65–960, y 270–1250. Place hero text in the upper-middle band, not
    the bottom third.
- **Vertical composition.** Center-weighted, vertically stacked. Put faces and eyes at about the upper
  third, since UI and captions own the bottom. Treat the rule of thirds as a vertical-axis tool here.
  BBC also puts 9:16 captions higher because "faces are generally in the top half" [BBC].
- **16:9.** Thirds, lead room in the direction of motion, and text inside the central 90% vertically
  and 75% horizontally (BBC's caption region) [BBC]. **4:5**: keep text inside the central 90%.
- **Depth without 3D.**
  - Parallax: speeds roughly ∝ 1/distance, e.g. foreground 1.0, midground 0.5, background 0.15–0.25.
  - Scale change as things approach.
  - Background blur: 4–12 px at 1080.
  - Atmospheric falloff: farther layers lose contrast and saturation.
- **One camera move per shot, and it must be motivated.** Follow the subject, reveal information, or
  express feeling: a push-in means intensity or intimacy, a pull-out means context or isolation.
  Don't stack zoom, rotate and pan.
- Avoid rotating the whole world and give the viewer a stationary frame of reference. Avoid sustained
  large oscillation, especially near 0.2 Hz [HIG-MOTION].
- A constant slow Ken Burns zoom on every shot, or simulator-smooth floating, reads as synthetic. The
  "flight simulator" camera is a known AI tell [OPUS].

## 5. Color and texture

- **Palette of 3–5 named colors:** ground, ink, 1–2 supports, and 1 accent covering ≤10% of the frame
  (60-30-10) [LOTTIE]. Put the accent only on the focal element; when the accent moves, attention
  moves.
- **Check value, not hue.** Look at every key frame in grayscale. When two saturated colors share a
  value they "buzz", and hierarchy vanishes [SOM-COLOR]. The focal element should be the
  highest-contrast thing in the frame. Text contrast floors are in §10.
- **Take the palette from the subject:** materials, place, era, packaging, the product's own UI, logo
  history. Not from "tech".
- Avoid synthetic over-saturation. Over-saturated reds, teals and yellows ("video game color grade")
  are a documented AI tell [OPUS].
- **Banding.** 8-bit 4:2:0 H.264, which is what platforms serve, bands on smooth gradients, especially
  dark ones.
  - Render in high precision.
  - Add fine monochrome grain at 1–3% amplitude, weighted to midtones and absent from pure blacks and
    whites, so the platform re-encode doesn't turn it into blocks [GRAIN].
  - Upload at high bitrate.
  - Or design around it: fewer large dark gradients.
- Texture should come from the subject (paper, halftone, film, fabric), not from a generic noise
  overlay laid over everything.

## 6. Data and explanation animation

- **Object constancy.** A mark that stands for Ohio stays Ohio through every transition. Key marks by
  identity, and handle enter, update and exit explicitly. Tracking moving marks uses "preattentive
  processing of motion rather than sequential scanning of labels" [BOSTOCK].
- **Congruence** [HEER]:
  - Intermediate frames should be valid charts.
  - The same operation looks the same everywhere.
  - Never reuse a mark for a different datum.
  - Different operations must look different.
- **Apprehension** [HEER]:
  - Group marks that change together.
  - Minimize occlusion.
  - Use slow-in/slow-out for predictability.
  - Prefer translation to rotation.
  - Stage complex changes, allowing about 1 s per stage.
- **One change at a time.** Rescale the axis first, then change values [HEER]. Keep gridlines through a
  rescale and fade them only after everything settles [HEER].
- **Don't over-stage.** Heavily multi-staged transitions increased error, and "most subjects laughed
  upon first viewing" [HEER]. Simple staging wins.
- **Numbers must be traceable.** Put a source line on screen or on the end card, legible at the floor
  size (§3). Don't count up from 0 when 0 means nothing. Hold the final number.
- **Annotate, don't decorate.** Label marks directly. Highlight by dimming the rest to 30–40%, not with
  glow, and draw arrows only to things that matter.
- **Explanation (3Blue1Brown).**
  - Concrete before abstract [SOME][3B1B].
  - Visuals first, then name the idea [3B1B].
  - Make "clear to the reader/viewer within the first 30 seconds why they should care" [SOME].
  - Make it *memorable*, something that will "make the piece easy to remember even several months
    later" [SOME].
  - Morph the formula or shape the viewer already holds into the new one. That's object constancy for
    symbols, as in Manim's matching-shape transforms.

## 7. Hooks and story

- "Audience involvement with a film should begin with its first frame" [BASS]. **Frame 0 is the
  thumbnail.** It must be a composed, legible still that states the promise: no black, no fade-in, no
  logo.
- The evidence on the opening seconds:
  - TikTok reports that over 63% of its top-CTR ads show the key message within 3 s [TIKTOK].
  - MrBeast's production guide calls the first minute "the most important" because it proves the
    title and thumbnail promise [MRBEAST].
  - 3Blue1Brown gives 30 s to motivate [SOME].
  - Scale the principle to your length: **promise in ≤2 s, proof by 20% of runtime.**
- **Hook patterns for 0–2 s.** Pick one and make it specific to the subject:
  1. Payoff first, then "here's how".
  2. An impossible or contrast image.
  3. A claim with a specific number.
  4. Start mid-action, already moving.
  5. A pattern interrupt: unexpected scale, silence, or a hard cut in the first second.
  6. A direct question the video answers.
- **Tension and release.** Open a loop (a question, an unfinished shape, a countdown, a partial
  reveal) and close it on the payoff frame. That frame is the one image people remember. Design it
  first.
- **Know, feel, do.** Start every piece with "what do we want people to know? … how do we want them to
  feel …? … what do we want them to do next?" [GRANDIN].
- **Make the ordinary extraordinary.** Bass looked at an everyday object with "unrelenting examination"
  [BASS]. That's a strong strategy for product and explainer work.

**Beat sheets** (derived):
- **15 s:** hook 0–2 · setup 2–5 · turn 5–10 · payoff 10–13 · button 13–15.
- **30 s:** hook 0–2 · problem 2–7 · turn 7–12 · three proof beats 12–24 · payoff 24–27 · button 27–30.
- **60 s explainer:** hook 0–3 · why care 3–10 · mechanism in three steps 10–40 · proof or number
  40–50 · payoff image 50–56 · button/CTA 56–60.
- **60–90 s music:** 4–8 bar intro motif · verse (establish) · chorus = peak visual idea · bridge =
  change of palette or space · final chorus bigger · button on the last hit.

## 8. Calibrated AI-slop tells in motion

For calibration, auto-generated motion currently clusters around these traits. All of them are
legitimate for *some* brief. Where the brief asks for one, follow the brief. Where it leaves the axis
free, don't spend that freedom on a default. If you'd land on the same choice for any similar prompt,
it's a default, not a decision [FD].

1. **Uniform entrance.** Every element fades in and slides up 20–40 px over about 0.5 s with CSS-ish
   ease-out, staggered 0.1 s, regardless of role or mass. frontend-design flags fade-and-slide-up
   entrances as the generic default [FD].
2. **One ease, one duration everywhere,** or library defaults left alone. Remotion's default spring
   bounces 16% on everything. Nothing has weight.
3. **The default scene:** a centered headline plus a smaller subtitle over a gradient. Three "feature
   cards" pop in one by one. Icon-and-label grids. A big number with a small label and a gradient
   accent.
4. **Neon-on-near-black "tech" look:** cyan, magenta or purple gradients, glowing orbs, bokeh, particle
   fields, grid floors and lens flares as filler. Glassmorphism panels. Over-saturated grades [OPUS].
5. **HUD chrome that means nothing:** scanlines, crosshairs, hex grids, fake code rain, random
   readouts.
6. **Transition inflation:** glitch, RGB-split, whip-pan or zoom-blur on every cut, or a different
   transition per cut. Meanwhile the piece needed hard cuts [GRANDIN].
7. **Sound on autopilot:** a stock whoosh on every move, a riser before every reveal, a music bed at
   constant energy from first frame to last, no silence anywhere, hits a few frames off.
8. **Redundant text:** on-screen words repeat what the picture or voiceover already says. Headline,
   caption and VO triple-state the same line.
9. **Template kinetic type:** per-letter bounce, typewriter, tracking-in, word-by-word pop captions in
   yellow or green with emoji. One word per line recolored for "emphasis".
10. **Celebration kit:** confetti, sparkles, check-mark bursts, 3D emoji, ✨. The "AI" motifs too:
    sparkle icons, gradient mesh blobs, neural-net lines, glowing brains.
11. **Counting everything:** every number counts up from zero, and progress rings appear with no data
    behind them.
12. **Robotic voiceover:** a "TTS plateau" cadence with no ramps, pauses or breaths [OPUS]. Picture cut
    on sentence boundaries instead of meaning.
13. **Unmotivated camera:** a slow push or drift on every shot, simulator-smooth floating [OPUS], and
    moves that reveal nothing.
14. **Perpetual motion:** no holds, idle elements that wiggle, nothing ever still. Stillness is what
    makes motion readable.
15. **Metronome pacing:** every scene the same length, cuts on neither beat nor emotion, a flat energy
    curve.
16. **Decaying ending:** a logo fade on black with a tagline, "Thanks for watching", or the energy
    simply running out instead of landing a button.
17. **Generic subject:** the video could be about any product. Nothing comes from the subject's own
    materials, vernacular or data. "Sameness" is the core complaint about slop [ARTLIST].

### 8b. House taste: what humans rejected in the productions behind this skill

These came back as notes from the person commissioning the video. Treat them as settled unless the
brief explicitly asks otherwise.

- **Narrative UI.** Kickers, step numbers ("01 / 04"), chips, progress bars, "(reference)" labels,
  verdict stamps that tell the viewer what to think. Replace text with a widget that *shows* the
  number, or delete it. "Widgets over text" was the note that turned one explainer around.
- **Transition menus.** Circle reveals, wipes, slides and noise dissolves chosen per cut read as a
  slideshow template. Hard cuts on the beat or on action, plus one signature match cut, is the house
  default.
- **The default "dark tech" stack.** Near-black ground + grid + glow + dust particles + vignette,
  all at once. Any one of these can be right; all five together are the stock AI look. Pick the
  ground from the subject.
- **Fake app chrome.** Window cards with traffic-light dots, fake terminals around text that isn't
  code, emoji used as icons.
- **Ken Burns judder.** A slow zoom on a still that snaps to whole pixels every few frames. Supersample
  the source (≥2× the output size) and move it in the renderer with sub-pixel sampling, or don't move it.
- **Fabricated ambience.** A synthesized "room tone" or pad that rises and falls periodically made
  viewers physically uncomfortable. Use real recordings, the music itself, or silence.
  `video_gates.py` flags periodic wobble.
- **Translated copy.** Spanish (or any language) that reads as a translation from English: calques,
  English word order, "impulsado por". Write natively in the audience's register.
- **Patch narrative and voice relays.** VO that narrates the latest fix, or three voices taking turns.
  One narrator, told from the viewer's side.
- **Periodic ornament.** Anything that pulses on a fixed period with no musical or narrative reason
  (a glowing dot, a breathing logo). Motion answers a question or it stays still.

## 9. How to push for taste

**Director's notes.** Apply these to your own cut, or the user can paste them.
- "What is the one image people will remember? Show me that frame." Then build toward it.
- "What should they know, feel and do?" [GRANDIN]
- "Where is the eye on the first and last frame of this shot?"
- "Remove one accessory" [FD]: delete one effect, transition, sound effect or layer per scene, then
  check whether anything was lost. Ordinary Folk cut a single dot on a single frame and the shot
  "somehow feels a little bit more cohesive" [OFOLK].
- "Make the hold longer." Give the payoff 1 more second with nothing moving.
- "Just use a cut." [GRANDIN]
- "Stop animating here and make the music good." [GRANDIN]
- "What would Saul Bass cut?" One symbol, "simple, direct ideas", the ordinary made extraordinary
  [BASS].
- "Is this motion answering a question? If not, still it." Don't add "motion for the sake of adding
  motion" [HIG-MOTION].
- "Pause on any mid-transition frame: is it still a good poster?"
- "Mute it: does it still work? Close your eyes: does the sound alone carry the arc?"
- "Could this be about any other product? Then find the subject's vernacular."
- "Which details matter most?" Knowing that is the skill, not polishing every frame equally [OFOLK].
- "Is beat N+1 bigger than beat N?" "Does the last beat call back the first?"
- "Spend it where it's seen." MrBeast: "I want money spent to be shown on camera" [MRBEAST]. Put craft
  effort into the frames people actually look at.

**How to ask for better work** (a brief card to request from the user, or fill in yourself and
confirm):
`Subject & real content · Audience · Platform + aspect + length · The one memorable image · Know/feel/do ·
2 references + what to take from each (not "make it like X") · Palette/type anchors from the brand ·
Sound: music energy arc, VO or not · Must avoid · What "proud to share" means to you`

**Contact-sheet self-critique.** Render stills at 1 frame per second, plus the first and last frame and
frames at 25%, 50% and 75% of every transition. Downscale a copy to 360 px wide to simulate the phone.
Check:
- [ ] Frame 0 works as a thumbnail and states the promise (§7).
- [ ] Every sheet frame has one focal point, and it's the highest-contrast element (grayscale check).
- [ ] At 360 px wide, all text is readable and respects the §3 floors and the §4 safe-zone overlay.
- [ ] Mid-transition frames hold the grid (§1). Nothing is clipped, overlapping or half-legible.
- [ ] Palette ≤5 colors with the accent only on focal elements. No banding in gradients.
- [ ] Holds meet the reading formula (§0), and the payoff holds ≥1 s with nothing else moving.
- [ ] The energy curve rises with contrast in time, and the piece ends on a button.
- [ ] Each §8 tell present has a written reason tied to the brief.
- [ ] The §10 floor passes.

## 10. Accessibility floor (non-negotiable)

- **Flashes.** Nothing flashes more than 3 times in any 1 s window unless it's below the general and
  red flash thresholds [WCAG231].
  - The threshold area is 341×256 CSS px, about a 10° field. Evaluate at the largest size the video
    will play, which means full screen [WCAG231].
  - Saturated-red transitions are stricter [WCAG231].
  - Glitch strobes, bright/dark cut alternations and flicker effects all count.
  - Practical rule: never alternate large bright and dark frames more than 3 times per second.
- **Patterns.** More than 5 light-dark stripe pairs covering a large area (Ofcom flags risk above 25%
  of the screen) must not oscillate, flicker or reverse contrast. Smooth one-way flow is exempt
  [OFCOM].
- **Vestibular.** Avoid rotating the whole frame, sustained oscillation near 0.2 Hz, and fast
  full-frame zooms. Keep a stable reference [HIG-MOTION].
- **Captions for all speech.** Many viewers watch muted, so the *story* must read with the sound off.
  How to deliver the words is a design decision, logged in `ORCHESTRATION.md` §7:
  - VO-led social pieces: designed, burned-in captions are the default, styled as part of the piece
    (not the yellow word-pop template, §8).
  - When the picture already carries the meaning with widgets and a few designed words, humans have
    asked to remove burned-in captions entirely. Honor that; ship a sidecar `.srt` instead.
  - Always ship the `.srt` for platform CC. If captions are burned in, warn that turning CC on shows
    the words twice.
  - Lyric videos: the designed lyrics are the captions.
  - Rate: 160–180 wpm, ≥0.3 s per word [BBC]. Duration: 5/6 s to 7 s each [NETFLIX].
  - ≤42 characters per line [NETFLIX]. ≤2 lines at 16:9 and ≤3 at 9:16 [BBC].
  - Break lines by meaning, and never cover mouths, faces or on-screen text [BBC].
- **Contrast.** Text is ≥4.5:1 against its background, or ≥3:1 for large text, on **every frame it's
  on screen**, including over moving footage. Add a plate or shadow if it drops [WCAG143].
- **Never carry meaning by sound alone or color alone.** Pair color coding with labels and shape
  [HIG-MOTION].
- **Reading time** follows §0. If the text must stay up longer than 7 s, split it.

## Sources
- [M3-ED] Material 3, *Easing and duration: Applying* — https://m3.material.io/styles/motion/easing-and-duration/applying-easing-and-duration
- [M3-TOK] Material Components Android, *Motion* (token values) — https://github.com/material-components/material-components-android/blob/master/docs/theming/Motion.md
- [M3-PHYS] Material 3, *Motion physics system* — https://m3.material.io/styles/motion/overview/how-it-works
- [M3-COMPOSE] AndroidX `ExpressiveMotionTokens.kt` / `StandardMotionTokens.kt` — https://github.com/androidx/androidx/tree/androidx-main/compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens
- [CARBON] IBM Carbon, *Motion* — https://carbondesignsystem.com/elements/motion/overview/
- [HIG-MOTION] Apple HIG, *Motion* — https://developer.apple.com/design/human-interface-guidelines/motion
- [HIG-TYPE] Apple HIG, *Typography* — https://developer.apple.com/design/human-interface-guidelines/typography
- [EMIL] Emil Kowalski, *Animation Standards* — https://github.com/emilkowalski/skills/blob/main/skills/review-animations/STANDARDS.md
- [REMOTION] Remotion `spring()` docs — https://www.remotion.dev/docs/spring
- [SOM-FT] School of Motion, *Follow-Through in After Effects* — https://www.schoolofmotion.com/blog/animation-tricks-follow-through-after-effects
- [SOM-ANT] School of Motion, *Anticipation* — https://www.schoolofmotion.com/blog/anticipation-principle-quick-tip
- [SOM-COLOR] School of Motion, *Basic Color Theory Tips* — https://schoolofmotion.com/blog/color-theory-after-effects
- [GRANDIN] Jay Grandin (Giant Ant) on SoM podcast — https://schoolofmotion.com/blog/jay-grandin-podcast-interview
- [OFOLK] Ordinary Folk on SoM podcast — https://schoolofmotion.com/blog/ordinary-folk-podcast
- [MURCH] W. Murch, *In the Blink of an Eye* (2001), rule of six via StudioBinder — https://www.studiobinder.com/blog/walter-murch-rule-of-six/
- [CUTTING] J. Cutting, shot-length research — https://flowingdata.com/2014/09/22/evolution-of-movies/
- [SB-CUTS] StudioBinder, *Types of editing transitions* — https://www.studiobinder.com/blog/types-of-editing-transitions-in-film/
- [BASS] Saul Bass interview (1977), The Academy — https://medium.com/art-science/saul-bass-on-his-approach-to-designing-movie-title-sequences-47fd537c457b
- [AOTT] Art of the Title, *Saul Bass* — https://www.artofthetitle.com/designer/saul-bass/
- [HEER] Heer & Robertson, *Animated Transitions in Statistical Data Graphics* (InfoVis 2007) — https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf
- [BOSTOCK] M. Bostock, *Object Constancy* — https://bost.ocks.org/mike/constancy/
- [SOME] 3Blue1Brown, *Summer of Math Exposition* — https://www.3blue1brown.com/blog/some1/
- [3B1B] Grant Sanderson quotes, compiled — https://www.antoinebuteau.com/lessons-from-grant-sanderson/
- [BBC] BBC Subtitle Guidelines — https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/
- [NETFLIX] Netflix Timed Text Style Guide (English USA; General Requirements) — https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977 · https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617
- [BRYSBAERT] Brysbaert (2019), *How many words do we read per minute?* — https://www.sciencedirect.com/science/article/abs/pii/S0749596X19300786
- [ITU1359] ITU-R BT.1359-1, sound/vision timing — https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-1-199811-I!!PDF-E.pdf
- [WCAG231] W3C, *Understanding SC 2.3.1* — https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html
- [WCAG143] W3C, *Understanding SC 1.4.3 Contrast (Minimum)* — https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- [OFCOM] Ofcom Broadcast Code guidance, Section 2 (flashing images & regular patterns) — https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/broadcast-guidance/programme-guidance/broadcast-code-guidance/section-2-guidance-notes.pdf
- [META-SAFE] Meta unified 9:16 safe zone (Mar 2026), summarized — https://blog.adnabu.com/meta-ads/meta-safe-zones/
- [TT-SAFE] TikTok / Reels safe zones — https://www.ignitesocialmedia.com/content-creation/what-are-the-safe-zones-for-tiktoks-and-instagram-reels/
- [TIKTOK] TikTok, *9 Creative Tips* (63% stat as widely cited) — https://ads.tiktok.com/business/library/Auction_Ads_Creative_Tips.pdf
- [MRBEAST] *How to succeed in MrBeast production*, via S. Willison — https://simonwillison.net/2024/Sep/15/how-to-succeed-in-mrbeast-production/
- [OPUS] OpusClip, *AI Slop: 12 Tells* — https://www.opus.pro/blog/ai-slop-aesthetic-12-tells
- [ARTLIST] Artlist, *What is AI slop* — https://artlist.io/blog/what-is-ai-slop-and-why-it-matters-for-video-creators/
- [GRAIN] G. Harkawik, *How to add grain to online video* — https://www.garretharkawik.com/how-to-add-grain-to-online-video
- [LOTTIE] LottieFiles, *Color theory for motion design* (60-30-10) — https://lottiefiles.com/blog/tips-and-tutorials/color-theory-for-motion-design
- [FD] Anthropic `frontend-design` skill (calibration list, "remove one accessory", "spend boldness in one place")
