# Delivery: formats, platforms, packaging

Phase 9. A video isn't delivered until the files play correctly everywhere they're going, frame 0 sells
it, the loudness survives the platform's re-encode, and the human can post it in one go.
Platform facts verified 2026-09-26 against official help pages unless marked [3P] (third party) or
[DER] (derived); platforms change these often, so re-check a hard limit before relying on it.

## 1. Pick the aspect per platform, compose each natively

| Where it will live | Primary canvas | Notes |
|---|---|---|
| LinkedIn feed, Instagram/Facebook feed | **1080×1350 (4:5)** | Biggest footprint in a mixed feed |
| Reels, TikTok, YouTube Shorts, WhatsApp Status, Stories | **1080×1920 (9:16)** | Mind the UI safe zones (§3) |
| YouTube long-form, desktop embeds, talks | **1920×1080 (16:9)** | |
| X | 16:9 or 4:5; 9:16 officially max 1200×1900 | 1080×1920 uploads widely, unverified [DER] |

Build each aspect as its own composition from shared scene code (a unit like `u = min(w, h) / 100`
for type, a per-aspect safe area). Never crop, pad or blur-fill a master made for another aspect:
center crops cut captions and faces, and blurred pillars read as a repost. If you must derive, compose
every shot for the smallest crop from day one; the music video that did this read *better* at 4:5.

## 2. Encode spec

Render a high-quality master (PNG frames, ProRes, or H.264 CRF ≤ 16), then derive every export with
`scripts/export_social.py`:

```bash
scripts/export_social.py out/master-4x5.mp4 --name clip --targets feed,whatsapp   # + prores for an editor
```

| Parameter | Value | Why |
|---|---|---|
| Codec | H.264 High, **yuv420p** (4:2:0, 8-bit), progressive | The only codec every platform lists; 4:4:4 and 10-bit don't play on many phones |
| Frame rate | **30 fps CFR** (24 for a filmic piece, 60 only for screen demos) | Reels wants a fixed rate ≥ 30; X caps at 40 fps; TikTok 23–60 |
| Quality | CRF 18, `-preset slow`, maxrate ~25 Mbit/s | Stays under X (25) and LinkedIn (30 Mbit/s) caps |
| Color | Converted to and tagged **BT.709**, limited (tv) range | Untagged or full-range files shift color on some players (§6) |
| Audio | AAC-LC **48 kHz stereo**, 192–320 kbit/s, encoded **once** | Every re-encode adds true-peak overs (audio.md) |
| Container | MP4 with `-movflags +faststart` (moov before mdat) | Starts playing before the download ends; LinkedIn Pages refuse MOV |
| Dimensions | Even width and height | Required for 4:2:0 |

Then run the gates on **every** export, not just the master:

```bash
scripts/video_gates.py out/clip-1080x1350-feed.mp4 --cues cues.json --expect-size 1080x1350 --expect-duration 45
scripts/video_gates.py out/clip-1080x1350-whatsapp.mp4 --max-mb 180
```

## 3. Hard limits worth knowing (15–90 s pieces)

| Platform | Duration | File | Other |
|---|---|---|---|
| LinkedIn member post | 3 s–15 min | ≤ 5 GB | 10–60 fps, ≤ 30 Mbit/s; SRT sidecar on desktop at posting time; custom thumbnail desktop only |
| X (free) | **≤ 140 s** | ≤ 512 MB | ≤ 40 fps, ≤ 25 Mbit/s; SRT on web; ≤ 60 s videos loop |
| Instagram Reels | ≤ 3 min to be recommended to non-followers | 4 GB | ≥ 720 px, ≥ 30 fps, fixed frame rate |
| TikTok | upload ≤ 60 min | API 4 GB; app caps ~72 MB Android / ~287 MB iOS [3P] | 23–60 fps |
| YouTube Shorts | ≤ 3 min, 9:16 or 1:1 | | Library music often capped at 90 s inside a Short |
| WhatsApp Status | **≤ 90 s** | always recompressed, no HD | |
| WhatsApp chat | | standard video 100 MB @ 720p on a fast link; as a document up to 2 GB | Document = no inline preview |

## 4. Safe zones (keep text, logos and faces inside)

**9:16, 1080×1920**

| Platform | Top | Bottom | Left | Right | Source |
|---|---|---|---|---|---|
| Instagram/Facebook Reels | 14% ≈ 270 px | 35% ≈ 672 px | 6% ≈ 65 px | 6% ≈ 65 px | Meta ads guide |
| TikTok | ~130–150 px | ~440–484 px | ~44–60 px | ~140 px (action rail) | [3P]; TikTok ships only templates |
| YouTube Shorts | ~120–180 px | ~300–400 px | ~60 px | ~96–120 px | [3P] |
| **Post anywhere** | **270** | **672** | **65** | **140** | → box **x 65–940, y 270–1248** |

Hook text in y 270–620. Captions ≤ 2 lines, block bottom ≤ y 1248. Instagram's profile grid shows Reels
as a 3:4 crop (loses ~240 px top and bottom): keep the cover's key content in y 240–1680.

**4:5, 1080×1350:** no official overlay; keep 5% graphics-safe (54 px sides, 68 px top/bottom) and captions
above y ≈ 1215 (player controls). **16:9:** 5% graphics-safe (96/54 px), captions above y ≈ 970.

Overlay the zone on key stills during QA (qa-critique.md §1).

## 5. Frame 0, covers, thumbnails

Most feeds show the first frame before anyone presses play (LinkedIn and X autoplay muted; WhatsApp
previews frame 0; LinkedIn custom thumbnails are desktop-only). So:

- Frame 0 is a finished, legible composition that states the promise. Never black, never a fade from
  paper or black, never a logo sting. `video_gates.py` fails a flat frame 0.
- If the design needs a fade-in, stamp the poster over the first 1–2 frames:
  `scripts/poster_frame.py out/master.mp4 --from-time 19.3 --out out/master-poster.mp4` (or `--image cover.png`).
- Export a cover PNG per aspect (`contact_sheet.py frames … --at 19.3`, or a designed cover) for
  platforms that accept a custom thumbnail. For TikTok, hold a clean poster moment ≥ 1 s early so it
  can be picked in the app.
- On X, a ≤ 60 s video loops: consider cutting the last frame cleanly into frame 0.

## 6. Color and pixel-format traps

| Source | What happens | Fix |
|---|---|---|
| JPEG frame sequence | Encodes as `yuvj420p`, full range, BT.601 tags | Convert range and matrix (export_social.py does) |
| PNG/RGB → `yuv420p` untagged | Players assume BT.601 on HD and shift hues | Convert with `scale=…out_color_matrix=bt709` **and** tag with `setparams` + `-colorspace/-color_primaries/-color_trc bt709` |
| PNG with sRGB tag | ffmpeg 9 copies the sRGB transfer tag into the MP4 even with `-color_trc bt709` | `setparams=color_trc=bt709` in the filter chain |
| libx264rgb / 4:4:4 output | Plays in QuickTime, fails or looks wrong on phones | `-pix_fmt yuv420p`, `-profile:v high` |
| Remotion v4 default | `--color-space` defaults to BT.601 | Pass `--color-space=bt709` (stack-remotion.md) |
| Thin saturated text | 4:2:0 halves chroma resolution: color bleeds | Thicker strokes, less saturated small text, or render at 2× and downscale |
| Subtle dark gradients | Band after the platform re-encode | 1–3% monochrome grain, fewer large dark gradients (craft.md §5) |

## 7. Captions and text tracks

Decide per piece and log it in `ORCHESTRATION.md` §7 (policy in craft.md §10):

- The story must read with the sound off, whatever the caption decision.
- VO-led social pieces: designed burned-in captions by default, rendered in the scene (the local
  Homebrew ffmpeg has no `drawtext`/`subtitles`/`ass`; audio.md §7 has a static-ffmpeg fallback).
- Always write an `.srt` (`scripts/captions.py words.json out/clip.srt`) for platform CC and search
  (LinkedIn desktop, X web, YouTube). If captions are burned in, tell the human that enabling CC shows
  the words twice, so the sidecar is mainly for YouTube and accessibility.
- Lyric videos: the designed lyrics are the captions; still ship the `.srt`.

## 8. WhatsApp: the review channel

Humans often review on their phone through WhatsApp before posting. Always ship a review copy **under
180 MB** (`export_social.py --targets whatsapp`, two-pass, sized to 175 MB by default; a 60 s piece at
~17 Mbit/s is ≈ 130 MB). For Status (≤ 90 s, always recompressed) a 720×1280 copy at ~4 Mbit/s survives
better than a 1080p file. When quality matters more than inline preview, send the master as a document.

## 9. The packaging kit (ship it with the files, unasked)

In `out/` next to the videos:

1. Masters per aspect + feed exports + WhatsApp review copy (+ ProRes if an editor will touch it).
2. Cover PNG per aspect.
3. `.srt`.
4. Title (one line, native language).
5. Post copy in the human's voice, starting from their hook line if they gave one; no hype words; link
   in the first comment where the platform penalizes links; every date, weekday, URL and "registration
   open" claim verified (qa-critique.md §4).
6. A "how it was made" note: short (for a comment) and long (for questions), claiming only tools that
   were actually used. Leave out anything the human prefers private.
7. `provenance.json`: for every generated or third-party asset, the model or source, prompt or plan,
   seed, account tier or license, date. Music and voice licenses decide whether the piece may be used
   commercially (audio.md §8, pitfall 21).
8. Known issues with timestamps, and what nobody could verify (usually: listening).

## 10. Licenses and disclosure

- Code stacks: Remotion is free for individuals and organizations of ≤ 3 people, paid above that; GSAP
  (all plugins) is free under Webflow's standard license; HyperFrames is Apache-2.0; three.js MIT;
  p5.js LGPL-2.1 with p5.brush MIT; Blender GPL (outputs are yours). Fonts: check the license before
  embedding; brand fonts are often not redistributable, so keep them out of public repos.
- Music: generated tracks follow the generating plan's terms; copyrighted songs get videos muted or
  blocked.
- AI disclosure: if a reasonable viewer could mistake generated footage, voices or people for real,
  label it (YouTube, TikTok and Meta require it; TikTok and LinkedIn read C2PA credentials). Production
  assists (captions, grading, code-rendered graphics) are exempt. Never let generative models render
  on-screen text or logos; set them in code.

## 11. Final checklist

- [ ] Each aspect composed natively; nothing important outside the safe zone
- [ ] Frame 0 is the poster; covers exported
- [ ] `video_gates.py` passes on every export (format, faststart, loudness −14 LUFS ±1 / ≤ −1 dBTP, poster, frozen runs, cuts on beats)
- [ ] BT.709 tags and yuv420p confirmed
- [ ] WhatsApp copy < 180 MB
- [ ] `.srt`, title, post copy, how-it-was-made note, provenance, known issues
- [ ] Watched end to end at full resolution, once muted and once with sound
