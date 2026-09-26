# QA and the critique loop

The builder is the worst judge of its own render. In the productions behind this skill, the
orchestrator approved every scene from 1-fps contact sheets; independent critics who *measured*
then found text 4–8 px tall on a phone, beats 6–21 frames late, 6-second dead holds, a music drop
landing on a crossfade, a finale that broke the film's own data rule, and three wrong numbers.
Run the loop below on every cut from `v01` on.

## The loop

```
render vNN ──► evidence pack ──► mechanical gates ──► lenses in parallel ──► verifier
    ▲                                                                          │
    └──── re-render ◄──── numbered work orders per owner (facts first) ◄───────┘
```

Stop when no P0/P1 findings remain open, the pride test in
[../templates/critique-rubric.md](../templates/critique-rubric.md) passes, and every applied fix was verified on a fresh render —
or after three rounds, reporting what is still open. Log every round in `ORCHESTRATION.md` §8–9.

## 1. Evidence pack (build it before anyone critiques)

| Evidence | How | Catches |
|---|---|---|
| Contact sheet of the encoded file | `scripts/contact_sheet.py sheet out/vNN.mp4` | Pacing, composition, blank frame 0, flat frames |
| Mid-hold stills per shot | `contact_sheet.py frames out/vNN.mp4 --at …` at the middle of each hold (from the beat sheet) | 1-fps sampling lands on transitions and flashes; mid-holds show the designed frame |
| Motion strips | `contact_sheet.py strip … --range a:b --step 0.1` on every transition, every hit, the first 5 s | Easing, overlap, collisions mid-transition, late beats |
| Phone test | downscale stills to 360 px wide (`magick in.png -resize 360x phone.png`) | Illegible type, lost focal points |
| Platform UI overlay | draw the safe zone of the target platform over key stills (see [delivery.md](delivery.md)) | Text under the like/comment rail or the caption area |
| Full-res text stills | every moment a line of text rests | Typos, orphans, overlaps, clipped diacritics (Ç Ñ É) and descenders |
| Audio report | `scripts/audio_check.py`; loudness per section; `ffmpeg -i mix.wav -lavfi showspectrumpic=s=1600x600 spec.png` | Levels, drops, a breakdown that isn't there, clipping |
| Mechanical gates | `scripts/video_gates.py out/vNN.mp4 --cues cues.json` | Format, faststart, decode errors, loudness, poster, frozen runs, periodic wobble, cuts off the beat |

Never read an image while the command that writes it is still running — you will critique the
previous render. Check that the sheet matches the current build (timestamp, content).

## 2. Measure, don't eyeball

- **Dead holds and glitches:** per-frame mean absolute luma difference on a downscaled copy. A
  run of ≥30 frames under the grain floor is a dead hold; a single frame that differs from both
  neighbours is a glitch; a huge spike is a cut. Compare to the beat sheet: holds are fine where the
  script says "breathe", not on the conceptual crux.
- **Late beats:** the same difference on a crop around the element; the first frame above the
  floor vs `round(word_time × fps)`. Target: visual onset within ±2 frames of the word, motion
  starting 3–9 frames before it.
- **Cuts vs beats:** detected cuts vs the beat grid (`video_gates.py --cues`, which accepts the
  `scripts/beats.py` output); every cut within 1 frame of a beat unless the script says otherwise.
  The detector misses cuts between flat grounds of similar brightness: check those seams in a strip.
- **Text collisions:** in HTML/Remotion stacks, assert text bounding boxes
  (`getBoundingClientRect`) don't intersect each other, the safe zone edges, or the character's box,
  per frame, in a test render. Builder self-review misses these.
- **Judder:** a slow zoom or pan whose frame difference swings erratically is snapping to integer
  pixels; supersample the source or move it in the renderer.
- **Settled values:** every number that comes to rest on screen equals its source value exactly
  (odometers must round the target before animating).

## 3. Lenses (run in parallel on the same render)

Each lens is a fresh agent with the evidence pack, the rubric, `ORCHESTRATION.md`, and one question:

| Lens | The question | Typical findings |
|---|---|---|
| Visual | Would a senior motion designer call any frame templated, cheap or cluttered? | Default look, weak focal point, palette drift, banding, type too small |
| Motion | Does every move have weight, intent and timing? | Uniform easing, simultaneous entrances, stalls between chained moves, whips too fast (strobe), late hits |
| Sound | Does the audio carry the arc and stay intelligible on a phone speaker? | VO buried, SFX on every move, energy flat, drop missing, clipping, periodic wobble |
| Story & wording | Does every word earn its place, in native language? | Narrative UI, redundant text, calques, hype, "patch narrative", orphan words |
| Truth | Does every number, name and claim match its source, in scope? | Wrong values, misleading comparisons, unscoped claims, stale source comments |
| Prod-ready | Would this upload and play correctly everywhere it's going? | 4:4:4 pixel format, loud true peak after AAC, no faststart, frame 0 blank, oversize files |

Each finding: ID, severity (P0 blocks shipping · P1 visibly amateur · P2 polish · P3 taste),
timestamp or frame, what's wrong, why it matters to the viewer, the smallest fix, and a still or
strip path. Each lens also lists the **3 things that already work and must not be touched**, and
answers: **"What 3 moves would make this extraordinary?"** — in one production all three proposed
moves were adopted and became the best moments of the film.

For the final round, add a critic from a different model provider when available; same-model
critics share blind spots.

## 4. The fact-check

- Build a table with one row per on-screen or spoken item: scene · time · what is shown/said ·
  source (file + field/line, or URL) · recomputation · verdict (OK / WRONG / MISLEADING / UNVERIFIABLE).
- Recompute counts and metrics from the raw data, not from the script.
- Check semantics, not just arithmetic: a true number framed so it implies a false comparison is
  MISLEADING.
- Scope every claim (which model, which split, which condition, which date).
- Tag sources by publicity: PUB (public), LOC (local, not sensitive), PRIV (needs the owner's OK
  before it appears on screen).
- Fetch every URL on the end card and in the post; verify dates, weekdays, "registration open".
- Keep `// source:` comments next to every number in scene code, and check them for staleness too.

## 5. The verifier

A skeptical agent reviews each finding before anything changes: it re-renders the frame, re-measures
the audio, or re-reads the source, and returns CONFIRMED / REJECTED / NEEDS-HUMAN with one line of
evidence. It rejects taste findings that would make the piece more generic, and anything on a
"must not be touched" list. Only confirmed findings become work.

## 6. Work orders

Merge confirmed findings into numbered lists **per owner** (the scene agent who owns the file),
facts first, then craft, each with frames, the target value and how to verify the fix. Resume the
same agents if their context is healthy; otherwise start fresh agents with a handoff file — agents
near their context limit compact mid-fix. Genuine owner decisions (wording that changes meaning,
private details) go to the human as a short list with a recommendation.

## 7. Audio QA without ears

Agents cannot listen. Use proxies and say so:

- Integrated loudness and true peak (whole mix and per section), VO-over-bed margin per line
  (≥ 9 dB is comfortable), SFX peaks relative to the voice.
- Spectrum images to see a drop, a breakdown, or a band that never enters.
- Tempo and first beat (librosa or the cue sheet) vs the picture's grid.
- A transcription round-trip of every TTS line and every sung hook/brand word; with two
  transcribers when one disagrees (local models hallucinate on synthetic audio).
- Correlate the final mix with candidate files to confirm which take is actually playing.
- Tell the human plainly what nobody has heard, and offer 2–4 alternatives to pick by ear.

## 8. Failure catalogue → detector

| Failure seen in a shipped or near-shipped cut | Detector |
|---|---|
| Blank or black frame 0 | `video_gates.py` poster gate; `contact_sheet.py` frame-0 warning |
| 4:4:4 / 10-bit export that phones won't play | format gate (`yuv420p`, High/Main) |
| True peak over −1 dBTP after the AAC re-encode | loudness gate on every export, not just the master |
| Fake ambience bed that rises and falls (nausea) | tremolo gate; never synthesize continuous beds |
| Text overlapping text or the subject | bounding-box asserts; full-res text stills; the visual lens |
| Title touching the subject | stills at title times; negative space planned in camera |
| Dead holds / late beats / drop on a crossfade | frame differencing vs the cue sheet |
| Stale numbers from an old run | fact-check recomputation from the latest data |
| Logic says it happened, pixels say it didn't | assert on rendered frames, not app state; re-capture after fixes |
| Brand logo painted where it shouldn't be | grep scene code for logo/brand identifiers before the final render |
| Hard horizon line on a studio floor | stills of every 3D shot; cyclorama or matching world color |
| Contact sheet from the previous build | check timestamps; assert patches applied; don't read while writing |

## 9. Report honestly

The delivery message lists what was verified and how, what was fixed in each round, what remains
open (with timestamps), and what nobody could verify (usually: listening). A known issue stated
plainly is part of the pride test; one discovered by the human after posting is not.
