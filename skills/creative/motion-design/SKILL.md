---
name: motion-design
description: >
  Direct and produce code-driven videos that a person is proud to share: motion graphics, series
  openers, music and lyric videos, paper and data explainers, product demos, social clips. Runs
  end to end as a studio crew of parallel subagents coordinated through an ORCHESTRATION.md file:
  brief, writers' room, style frames, music/VO/SFX, deterministic render, critique loop, social
  exports. Use when the user says "make a video", "motion graphics", "animate this", "an opening
  for my series", "intro animada", "hazme un video", "video musical", "lyric video", "explainer
  de 60 s", "video para LinkedIn / Reels / TikTok", "kinetic typography", "render an MP4",
  "anima este paper / estos datos", or wants an existing video to look less generic. Not for
  static images or slide decks.
version: 0.1.0
---

# Motion Design

Approach every video as the creative director of a small motion studio whose work gets
forwarded. The client has already seen the template version of this video — fade-up titles,
stock whooshes, a logo at the end — and is paying for a point of view: one idea, one image
people remember, sound that was designed, and craft they can feel in the timing.

The Definition of Done is the **pride test**: the human would post this under their own name
today, without apologizing for anything, and it is better than the last video they shipped.
"It renders" is the floor, not the goal.

## Non-negotiables

1. **Open the orchestration file first.** Copy [templates/ORCHESTRATION.md](templates/ORCHESTRATION.md)
   to the project root and fill §1 Brief and §2 Definition of Done before writing any code. It is
   the single source of truth for every agent, the ledger of decisions, sources and findings,
   and what you re-read after a context compaction. Update it at every phase gate.
2. **Run it as a crew, in parallel.** Divergent work (drafts, style frames, music takes,
   scenes, critique lenses) goes to parallel subagents launched in one message, each pointed at
   `ORCHESTRATION.md` and given one output path. Prompts: [templates/crew-prompts.md](templates/crew-prompts.md).
   Playbook: [references/orchestration.md](references/orchestration.md).
3. **Look at every render, and measure it.** A render nobody looked at is not progress. Every
   iteration: a contact sheet for pacing, motion strips for easing and sync, stills for type
   (`scripts/contact_sheet.py`), and the mechanical gates for format, loudness, frame 0, frozen
   runs and cuts on the beat (`scripts/video_gates.py`). Taste is judged by independent critics,
   not by the builder ([references/qa-critique.md](references/qa-critique.md)).
4. **Frame 0 is the poster; the hook lands in 1.5 s.** Feeds and chats preview the first frame:
   design it as the thumbnail, never black, white or half-built (`scripts/poster_frame.py` fixes a
   fade-in). The premise reads in the first 1.5 s with the sound off, and the best material is in
   the first 5 s, because that is where the viewer and the person who commissioned it decide.
5. **Truth on screen.** Every number, name and claim traces to data or a source recorded in the
   ledger; a fact-check pass runs before final. Parody of a brand is fine; its real logo is not.
6. **Native voice.** Copy, lyrics and VO are written in the audience's language and register
   from scratch — never translated, never hype.
7. **Decide, don't block.** Make the reasonable call, log it in §7, keep going. Ask the human
   only at a genuine taste fork (which song take, which concept), with a recommended default,
   and keep building the default while waiting. Never leave a long run parked on a question.
8. **Ship the whole package.** Masters per aspect, feed exports, a WhatsApp review copy under
   180 MB (`scripts/export_social.py`), `.srt`, covers, title, post copy in the human's voice, a
   "how it was made" note, provenance of every generated asset, and known issues stated plainly
   ([references/delivery.md](references/delivery.md)).

## Ground it in the subject and the person

Distinct pieces come from specifics. Before concepting, collect: what the subject's world looks,
sounds and talks like (its vernacular, objects, textures, music genres); what you know about the
human from memory and context (their work, community, obsessions, in-jokes); the real assets
and data you can use (logos they own, mascots, logs, eval results, screenshots). A Colombian
developer community gets a cumbia with local slang, not a synthwave montage; an eval paper gets
its real per-question results as the visual material, not generic "AI" particles; a personal
opener borrows a format the audience instantly recognizes (a streaming-series cold open, an anime
OP) and fills it with true details. Build with real content from the first frame.

## The production

| Phase | What happens | Gate |
|---|---|---|
| 0 Intake | Fill §1–2; pick format, aspect, duration, language, stack | Brief fits on one screen |
| 1 Research | Facts with sources, reference pieces and the device each uses, the subject's vernacular | `research/` written |
| 2 Writers' room | 3–5 divergent drafts in parallel → 3 blind critics with the rubric → merge | One script, every line illustratable |
| 3 Direction | 3 style frames, tokens, motion language, anti-list — reviewed against the calibration list below | §3 locked |
| 4 Sound | Music/VO first when they lead; beat grid (`scripts/beats.py`) and word timings into `cues.json` | Take chosen, cues exported |
| 5 Animatic | Beat sheet timed to audio, rough render | Contact sheet reads as a story |
| 6 Build | One animator agent per scene on a shared engine and tokens | Each scene ships a sheet + strip |
| 7 Assemble | Full render, mix, master (`scripts/audio_check.py --normalize`) | `out/vNN.mp4` plays end to end; `video_gates.py` passes |
| 8 Critique loop | 3–5 lenses in parallel → skeptical verifier per finding → fix → re-render | No open P0/P1; pride test passes |
| 9 Deliver | Exports, captions, poster, post copy | §10 complete |

Keep a shippable cut at all times: once phase 7 produces `v01`, every later change must leave a
better playable file, so a deadline never finds you with nothing.

## Principles of motion people share

**One idea, one image.** Say the idea in a sentence before designing. Decide the single frame
people will screenshot, build toward it, and give it a hold. Spend boldness in one place; keep
everything around it disciplined.

**Hook with the sound off.** Most feeds autoplay muted. The first 1.5 s must carry the premise
visually: a strong shape, a surprising line of type, motion that starts mid-action. No logo
stings, no slow fade from black.

**Timing is the craft.** Holds are where meaning lands; cut them and nothing reads. Give on-screen
text enough time to be read twice by a slow reader (rules in [references/craft.md](references/craft.md)). Vary shot
length with the music's phrasing; escalate toward the payoff, then breathe.

**A motion vocabulary, not effects.** Pick two or three easings for the whole piece (a snappy
entrance, a soft settle, one expressive overshoot) and name them as tokens. Hard cuts on the beat
or on action are the default transition; add one signature move tied to the concept (a match cut
on a shape, a data morph, a brush wipe in a painted piece), never a menu of wipes, slides and
circle reveals. Things that enter together are staggered; things that stop have follow-through;
big moves anticipate.

**Sync is felt.** Put cuts and hits on beats and transients (within a frame), key text to word
timestamps, let big moves resolve on downbeats. Derive every cue from the audio (`cues.json`),
never by eyeballing.

**Type is image, and every word earns its place.** Few words, set large, in a typeface chosen for
this subject (not the default sans). Break lines by meaning. Kinetic type acts out what the words
say. No narrative UI (kickers, step numbers, chips, progress bars, verdict labels): show the number
in a widget or cut the text. The story reads with the sound off; spoken pieces get designed
captions unless the picture already carries the words, and always ship an `.srt`.

**Texture beats sterility.** Grain, dither, paper, brush boil or film response make code-made
frames feel made by hand and hide H.264 banding in gradients. Keep it subtle and consistent.

**Camera with intent.** One motivated move per shot; parallax and depth of field over spinning
3D. Every move should answer "what do I want the viewer to look at now?"

**Sound is half the video.** Music chosen for the subject's culture and energy arc, voice that
sounds like a person, SFX that are sparse and specific. Mix it: music ducks under voice, the
final beat resolves on the button, the master sits at −14 LUFS with true peak ≤ −1 dBTP after the
AAC encode. Never synthesize a continuous ambience bed: a periodic wobble made viewers nauseous.

**Remove one accessory.** Before rendering the final, cut the effect you are proudest of for
its own sake. If the piece doesn't miss it, it was decoration.

## Calibration: what AI-made motion clusters around

Every one of these is legitimate for some brief, but they appear regardless of subject, so in a
piece they read as defaults, not choices. Where the brief leaves an axis free, don't spend it here:

1. Every element fading in while sliding up 20–40 px, all with the same ease-in-out and duration.
2. A dark background with floating bokeh, random particles or a slow gradient mesh as filler.
3. Generic "tech" HUD overlays, scanlines, lens flares, fake window chrome with traffic-light dots;
   a different wipe, slide or glitch transition on every cut.
4. Centered title plus smaller subtitle plus accent gradient, then a logo fade-out as the ending.
5. A stock whoosh on every movement, and music that never changes energy.
6. On-screen text that narrates what the picture already shows; narrative UI (kickers, "01 / 04",
   chips, progress bars); captions in one long line.
7. Numbers counting up from zero with no source, charts that animate but explain nothing.
8. Emoji, confetti or sparkle bursts as a stand-in for a payoff.
9. Robotic, evenly paced VO; copy full of "revolucionar", "el futuro es hoy", "unlock", "seamless".
10. Everything moving at once; nothing ever holds still long enough to be read.

The longer list, with fixes, is in [references/craft.md](references/craft.md). Write the piece's own anti-list in
§3 of the orchestration file.

## Push for taste

Run these director's notes on every contact sheet, and teach the human to use them:

- What is the one frame people will screenshot? Is it on screen long enough?
- If I muted it, would the first 1.5 s still make me stop?
- Which moment would a stranger describe to a friend? If none, the idea is too safe.
- Where does it look like a template? Replace that default with something from the subject's world.
- What can I cut? Shorter almost always wins; remove one accessory.
- Is every hit on the beat? Is every hold long enough to read twice?
- Is this better than the last video this person shipped?

When the human says it looks "AI slop", "genérico", or asks for "más sabor", they mean too safe,
too hedged and too generic — not "add effects". Respond with more specificity (their world, their
jokes, their data), a bolder single idea and stronger opinion, and fewer disclaimers.
Paste-able prompts that ask any agent for better work are in [references/prompting.md](references/prompting.md).

## Pick the stack

| Brief | Default stack | Reference |
|---|---|---|
| Kinetic type, openers, UI parodies, lyric videos, most 15–30 s pieces | HTML/CSS/SVG + GSAP (or HyperFrames), rendered frame by frame | [stack-html-frames.md](references/stack-html-frames.md) |
| Data or paper explainers, React teams, captions from alignment, long pieces | Remotion (+ `@remotion/three` for GPU scenes) | [stack-remotion.md](references/stack-remotion.md) |
| Hand-painted, illustrated, character animation | p5.js + p5.brush on a time-pure engine | [stack-p5-brush.md](references/stack-p5-brush.md) |
| Particles, data-art, 3D product or place, cinematic camera | three.js (WebGPU/TSL) or Blender headless | [stack-3d-shaders.md](references/stack-3d-shaders.md) |
| Anything else, or unsure | Read the decision matrix | [stack-selection.md](references/stack-selection.md) |

Whatever the stack, every frame is a pure function of time (`render(t)`): no wall clock, no
unseeded randomness, no free-running animation loops. That is what makes renders reproducible,
parallelizable by frame range, and fixable one shot at a time.

For newer and experimental libraries — and how to re-scan the awesome lists for what shipped
this month — see [references/awesome-libs.md](references/awesome-libs.md). Allow one experiment per piece, where it
serves the idea, and keep a proven fallback for that shot.

## Scripts

| Script | Does |
|---|---|
| `scripts/render_frames.py` | Deterministic HTML → MP4: seeks `window.__seek(t)` per frame in headless Chromium (`--gpu` for Metal), BT.709-tagged encode; ranges, supersampling, workers, sheets, stills, alpha |
| `scripts/contact_sheet.py` | Contact sheet of any video (frame-0 and flat-frame checks), motion strips for a time range, full-res stills |
| `scripts/video_gates.py` | Mechanical gates: format, faststart, decode, loudness, poster frame, frozen runs, periodic audio wobble, cuts vs the beat grid |
| `scripts/audio_check.py` | Integrated LUFS, range and true peak against targets; `--normalize` masters to −14 LUFS / −1.5 dBTP with an oversampled limiter |
| `scripts/beats.py` | Constant beat grid, downbeats and onsets from a song → `--cues` JSON |
| `scripts/captions.py` | Word timings → phrase-aware SRT cards within reading speed |
| `scripts/sfx.py` | Seeded procedural accents in numpy: whoosh, hit, riser, ta-dum, glitch, click, blip, pop, swell, braam |
| `scripts/poster_frame.py` | Stamp a designed or chosen poster over the first frames without shifting sync |
| `scripts/export_social.py` | Feed export (BT.709, faststart), WhatsApp review copy under a size budget, ProRes for editors |
| `scripts/blender_mg_render.py` | Headless Blender 5.x skeleton: scene from code, eased camera, resumable PNG frames |

Paths such as `scripts/…`, `references/…` and `templates/…` are relative to this skill's
directory, not the user's project; pass absolute paths when briefing subagents. All scripts need
`ffmpeg`/`ffprobe`; those with dependencies declare them inline (PEP 723) and run with `uv run`,
the rest use only the standard library. Working starting points live in `examples/`
(`gsap-page.html` implements the render contract; `remotion-webgpu-tsl-scene.tsx` is a deterministic
WebGPU scene).

## References

| File | Read when |
|---|---|
| [orchestration.md](references/orchestration.md) | Starting any production; running the crew, gates, human checkpoints, overnight runs |
| [craft.md](references/craft.md) | Designing and critiquing: timing, easing, rhythm, type, color, camera, the long slop list |
| [story.md](references/story.md) | Writing hooks, beat sheets for 15/30/60/90 s, lyrics, VO scripts |
| [stack-selection.md](references/stack-selection.md) | Choosing the stack; local toolbox check |
| [stack-html-frames.md](references/stack-html-frames.md) | HTML/GSAP/HyperFrames/anime.js pieces and the frame renderer |
| [stack-remotion.md](references/stack-remotion.md) | Remotion projects |
| [stack-p5-brush.md](references/stack-p5-brush.md) | Painted or character-animated pieces |
| [stack-3d-shaders.md](references/stack-3d-shaders.md) | three.js, R3F, WebGPU/TSL, shaders, Blender |
| [audio.md](references/audio.md) | Music, VO, SFX, alignment, cue sheets, mixing |
| [delivery.md](references/delivery.md) | Platform specs, safe zones, captions, exports |
| [qa-critique.md](references/qa-critique.md) | Running the critique loop and the fact-check |
| [awesome-libs.md](references/awesome-libs.md) | Newest libraries, experimental radar, how to refresh the list |
| [prompting.md](references/prompting.md) | Asking for better work; community one-liners |
| [case-studies.md](references/case-studies.md) | Lessons from past productions: what worked, what cost hours |
