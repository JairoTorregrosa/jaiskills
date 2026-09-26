# Case studies: what shipped, what worked, what cost hours

Post-mortems of the productions this skill was distilled from (September 2026), each made end
to end by coding agents. Read the one closest to your brief before planning; the "cost" lines are
the expensive mistakes not to repeat.

---

## 1. Community music video — "Vente pa'l parche" (64 s, 16:9 master + 4:5, 1:1)

**Brief:** a one-minute animated music video for a developer community in Colombia, built on an
open-source hand-painted animation kit (p5.js + p5.brush), music from a generation API, produced
overnight for LinkedIn. Reference: a Colombian children's-TV song that went viral.

**Stack:** p5.js 2 + p5.brush on a time-pure engine rendered by headless Chrome; ElevenLabs Music
(composition plan, word timestamps); beat_this + fuzzy lyric alignment for sync; ffmpeg; ~21
subagents. Render: 1536 frames at 24 fps in ~5 min on an M1 Pro using 2 processes.

**What worked**
- Writers' room: 5 songwriters with different premises → 3 critics with personas and a shared
  rubric → a synthesized lyric that took the best part of four drafts. The critics caught a real
  surname used as a punchline, lines that sounded like surveillance, and bad security advice
  delivered as a joke.
- Borrowing the viral reference's *functions* (a funny formal full name sung early, a deadpan
  twist in the first 12 s, a repeatable chorus, a didactic list, a spoken button), with a
  forbidden-phrases list so none of its words were reused.
- Music plan sections sized in exact bars (at 108 BPM, 5 bars = 11 111 ms), so cuts land on bar lines.
- One generated timing file (lines, words, beats) as the single source of truth; six scene
  animators read times from it and snapped every hit to the grid with `bAt(t)`.
- Lyrics on screen as designed type — paper-cut karaoke strips, a terminal card for commands, a
  diff card for "before → after" jokes, big title plates for the brand chorus — because LinkedIn
  autoplays muted. Contrast ratios computed; all type kept inside the 4:5 center crop.
- One literal, paintable gag per lyric line; the mascot never lip-syncs (it has no mouth; the song
  jokes about it).
- A different, motivated transition on each of six seams (cut on action, paint wipe, match cut,
  iris onto a face, whip smear, cut on the beat), with the half each scene owns written in the
  storyboard.
- A fallback shot and a hard stop time guaranteed a complete video.

**What cost hours**
- A song-choice question asked at 23:46 was answered at 06:08. The deadline was missed, animators
  were squeezed to ~10 minutes each, and the human picked the recommended take anyway.
- The music API was gated on the free tier; a first song made in the web UI didn't rhyme and
  sounded translated (1 800 credits discarded).
- Stage directions in parentheses were sung ("(hablado)"); directions go in `{braces}`.
- Frame 0 was a fade-up from blank paper; the upload preview looked empty until the cover frame was
  copied into frame 0.
- Shipped defects no one caught under time pressure: a lyric card over the hat, an orphan word in
  a monospace card, a character lost in the karaoke band, near-black frames at an iris seam, no
  audio preview per scene, true peak at −0.1 dBFS, full-range BT.601 tags from JPEG frames.

**The human said:** "ya el fest pasó" (make it evergreen) · "tienes que hacer que sí rime… no
hagas la traducción literal del inglés" · "esfuérzate bien para crear una pieza viral de calidad de
la que yo deba estar orgulloso" · "coloca en el primer frame la miniatura para que en la preview no
se vea un blanco" · then asked for the thumbnail, title, post copy and stack one by one.

**Lesson:** infrastructure (sync, rig, type system) can be built before the song exists; the
creative room and critics are worth their tokens; never park a night on a question; packaging is
part of the deliverable.

---

## 2. Paper explainer — "No se sabe" (60 s, 4:5 + 16:9)

**Brief:** "a 60 s explanation video of this paper and result, groundbreaking… push animation to
extraordinary levels, use the latest libs… read the logs, go deep into what happened."

**Stack:** Remotion 4 + React Three Fiber + three.js + postprocessing; 58 184 particles, **one per
real model answer** from the eval logs; ElevenLabs TTS with timestamps, Music (composition plan)
and SFX; ffmpeg mastering. 3 h 44 min brief-to-delivery, two full versions. Full render 87–119 s.

**What worked**
- The visual *is* the evidence: the same particles re-form scene to scene (question → word →
  constellations → run strands → accuracy lanes → vector → heatmap → the closing words), so the
  transitions carry the argument. The counter on screen is literally the number of lit dots.
- Contract-first parallelism: the engine agent and the log-mining agent started in the same minute
  against one data schema; a synthetic dataset with a burned-in "SYNTHETIC · DO NOT PUBLISH"
  badge let the engine be built before the real data existed.
- One engine owner proved the engine (lab compositions, benchmark, byte-identical determinism, a
  490-line manual with a worked example) before four scene agents fanned out on it.
- Every beat keyed to a spoken word through a lookup that throws if the word is missing — a
  re-voiced line re-times the film or fails loudly.
- Two independent reviewers on the *rendered* film — a motion director who measured (frame
  differencing for dead holds and late beats, a 360 px phone test, UI-zone overlays) and a
  fact-checker who recomputed 82 on-screen items from the data — plus a request for "the 3 moves
  that would make it extraordinary". All three moves were adopted and became the best moments.
- Frame-seeded grain on a 2 px lattice in perceptual space: hides banding, survives re-encode,
  costs little bitrate.

**What cost hours / what self-review missed**
- The orchestrator approved every v1 scene from 1-fps contact sheets. The reviewers then found 6
  must-fix craft issues and 3 wrong + 4 misleading facts: text 4–8 px on a phone, beats 6–21
  frames late, dead holds of 4.6 and 6.3 s (the longest on the conceptual crux), the music drop
  landing on a crossfade, a finale that recolored every guess and broke the film's own data rule,
  an odometer resting 82% between digits, a formula missing its sign.
- A music model ignored "breakdown, drums stop" in four takes; the breakdown was made with
  ffmpeg filters instead.
- One author's broken file blocked everyone's stills (shared bundle) for ~8 minutes; the same
  tool pitfalls were rediscovered by 4–5 agents; nothing was committed between versions.

**Lesson:** for an explainer, "groundbreaking" means the picture is the data, not more effects.
Builder self-review is not QA — independent, measuring critics are. Give every agent the
pitfalls file up front.

---

## 3. Personal series openers (15 s each, 16:9)

Three pieces from the same person and renderer (canvas `renderAt(t)` → Playwright → ffmpeg):

| Piece | Idea | Verdict |
|---|---|---|
| Animated bio | Six beats: name, role, community, projects, hobbies, URL | Competent and silent; reads as the default AI-motion template (dark ground + drifting grid + roaming glow + dust + vignette; six identical letter-rise entrances at the same cadence; window-dot "project cards") |
| Streaming-series cold open | A red letter "ta-dum", letterbox, four trailer cards ("BY DAY, / BY NIGHT, / HIS MISSION: / AND HE WON'T NEGOTIATE TWO THINGS:"), title slam, a parody streaming UI end card ("Top 10 · N.º 1 in Colombia today", "98% match", "▶ Watch now") | The format did the heavy lifting; the parody UI end card was the most shareable frame of the set |
| Anime opening | 150 BPM grid, one bar per scene, character cards (protagonist / sidekick = the dog, "Head of QA"), a "technique" montage one per beat, the home router as arch-villain, staff-credit plate | The most "only-this-person" piece; risks: 11 full-frame flashes in 15 s, 0.3 s subtitles, a private network detail on screen |

**What worked:** a genre frame the audience already knows + real personal specifics mapped onto
its slots; synthesized SFX (ta-dum, whoosh leading the cut, riser into impact, braam, UI blips);
kinetic mask-rise type, a title slam with RGB split, a glint clipped to the glyphs; a hit system
(white flash ≤0.12 s + seeded shake with 3% overscan) on downbeats.

**What cost time:** a cedilla clipped by a mask band; two words drawn at hard-coded x ("jetsononline");
a line overflowing the frame; a glint bleeding over the whole frame; a patch that silently didn't
apply so the contact sheet showed the previous video; reading an image while ffmpeg was still
writing it; a JS syntax error surfacing as "renderAt is not defined"; generated music dying at
13 s (generate 1.5× longer and trim).

**The prompt lesson:** the shareable one-liner improved by removing the tech stack, the safety
disclaimers and the negations, and adding a genre frame, "with what you know about me", a fixed
duration and a viewer outcome. See [prompting.md](prompting.md).

---

## 4. Model-race videos for LinkedIn (28 s, shipped in 4:5)

Screen recordings of AI models painting the same portrait, sped 32×, composited per frame in
Pillow (this ffmpeg build has no `drawtext`) and piped to ffmpeg with a music bed.

**The human said:** "no hagas narrative UI… deja que el video se explique solo" · "sin esa parte
inicial, solo y siempre real el video" · "recuerda less wording" · "busca una mejor música con más
taste". The approved layout went through six ASCII iterations before a single render.

**Lesson:** let real footage explain itself — keep only names and live data (clock, cost), one color
per group (lab), no titles, VS, verdicts or "(reference)" labels. Start on real content at frame 0.
Crop to the region that matters when panels get small. Offer 3–4 muxed music options instead of
picking blind. Never ship raw recordings that show the operator's screen.

---

## 5. Blender + real-time trailer — a metro line (30 s, 16:9)

Blender EEVEE product renders (AgX, warm key / cool rim, 48 mm with lens shift for title space)
mixed with frame-stepped captures of a three.js simulation, an original numpy score with accents
at the planned cuts, ffmpeg crossfades with handles.

**The human said:** "5 first seconds need to be very good" · "cada texto tiene que luchar por su
vida… no hagas narrative UI" · "en el video hay cortes muy bruscos, mejóralos" · "ese sonido que
sube y baja me marea" · "las puertas no se están abriendo" (with a screenshot, after every test had
passed).

**Lessons:** zero text until the end card; bookend with the hero shot; plan negative space in
camera. Capture real-time engines deterministically (freeze the clock, step 1/30, screenshot) and
assert each shot's action actually happened — check pixels, not state. Never fabricate ambience:
a synthesized bed whose level rose and fell periodically made the viewer dizzy; silence plus
honest one-shots is better. Re-time the score after a re-cut (the accents drifted off the new cuts).
Cast shots around the strongest assets; keep weak ones (blocky crowds, empty ground) brief or out
of frame. One grade across CGI and capture.

---

## 6. Security explainer, four iterations (60 s)

Flat illustrated stills (one locked style block, edits anchored on a hero image for coherence),
TTS narration, ffmpeg zooms and xfades. Each version answered one note:

| Version | Note from the human | Change |
|---|---|---|
| v1 → v2 | "cambia la voz de Loquendo… evita el patch narrative… desde la perspectiva de la universidad" | One point of view instead of a relay of five voices |
| v2 → v3 | "remove subtitles, remove narrative UI. widgets > text. every text needs to be very handcrafted or justified" | Numbers became data widgets in planned negative space |
| v3 → v4 | "la voz está muy paila… cada 5 s debe haber una transición… haz el video con la corrida real" | Realistic cloned narrator, a change every ~4.5 s, real current numbers |

**What was still wrong in v4** (found later by measurement): 4:4:4 pixel format in three of the four
exports (phones won't play it), Ken Burns judder from zooming at output resolution (supersample
first), PowerPoint transitions (circle, wipe, slide, noise-dissolve), text overlapping inside a
result tile that the builder had called clean, voice over silence with no music or room tone.

**Lesson:** time explainers from the measured voice (shot = VO + 0.4–0.5 s) and cut words rather than
speeding speech up; verify TTS with two transcribers; deliver yuv420p; allow only cuts, true
crossfades, fades through black and motivated match or whip cuts.

---

## Cross-cutting lessons

1. The human judges the first frame and the first five seconds before anything else.
2. Every word on screen must earn its place: data, lyrics in a lyric video, the closing line. No
   narrative UI (kickers, step numbers, chips, progress bars, verdict labels).
3. Specific beats generic: a genre frame + real lore, real data as the visual, local language.
4. Rhythm: a BPM grid, cuts on bars, the biggest picture event on the drop, holds long enough to
   read, nothing meaningful idle for more than ~1.5 s.
5. Independent critics who measure catch what builders miss; ask them for "the 3 moves that would
   make it extraordinary", not only defects.
6. Agents cannot listen: measure (LUFS, spectrum images, tempo, transcription), offer the human
   2–4 options by ear, and say plainly what nobody heard.
7. Mechanical delivery gates catch the embarrassing failures: yuv420p, faststart, loudness, true
   peak after the last re-encode, poster frame, size budget.
8. Decide and report; ship the package (poster, title, post copy, stack note, WhatsApp copy).
