# Critique rubrics

Two rubrics: one for concepts and scripts (writers' room), one for renders (critique loop).
Score 1–10; doubled criteria weigh twice. A score without a quoted line or a timestamp is not
evidence — critics must point at the thing.

## A. Concept / script rubric (writers' room)

| # | Criterion | Weight | What a 9–10 looks like |
|---|---|---|---|
| 1 | Hook | ×2 | First 1.5 s stop the scroll with sound off; the first line could stand alone as a clip |
| 2 | One idea | ×1 | A stranger can say what the video is about in one sentence after one watch |
| 3 | Specificity | ×2 | Details that belong to this subject and no other; nothing a template would produce |
| 4 | Native voice | ×1 | Sounds written in the audience's language and register; no calques, no hype words |
| 5 | Visualizable | ×2 | Every line maps to one literal, specific, drawable image |
| 6 | Arc and button | ×1 | Tension builds, pays off, ends on a beat that invites a replay or a reply |
| 7 | Craft of the form | ×1 | Songs: rhyme and meter hold (±1 syllable). VO: speakable at the target pace. Titles: fit the frame |
| 8 | Truth | ×1 | Every claim sourceable; humor never costs accuracy |
| 9 | Producible | ×1 | Buildable with the chosen stack before the deadline, without a cheaper-looking fallback |
| 10 | Pride | ×2 | The human would post it under their own name and forward it to people they respect |

Max 140. Ties break on Pride, then Specificity. Critics end with a merge recommendation.

## B. Render rubric (critique loop)

Each lens scores its criteria and files findings with severities:
**P0** blocks shipping (wrong fact, broken frame, clipped audio, unreadable key text, flash risk) ·
**P1** visibly amateur (default look, dead air, off-beat cut, jitter, text too small) ·
**P2** polish (spacing, easing, mix balance) · **P3** taste (debatable; director decides).

### Visual (contact sheet + stills)
- Frame 0 is a designed poster; every sampled frame would work as a still
- One focal point per frame; hierarchy readable at phone size
- Palette and type follow §3; no slop tells from the anti-list
- Text inside safe zones; minimum sizes met; contrast ≥ 4.5:1 for small text
- Texture present where intended (grain/dither); no banding in gradients after encode

### Motion (strips of the busiest and the most important ranges)
- Easing vocabulary consistent; nothing linear that should breathe, nothing floaty that should hit
- Overlap and stagger feel natural; no simultaneous identical entrances
- Holds long enough to read (see references/craft.md reading-time rule)
- Hits land on the beat or transient (within 1 frame); cuts motivated
- No jitter, popping, z-fighting, aliasing, or sub-pixel crawl on text

### Sound (audio_check.py report + listening by analysis)
- Loudness in spec (integrated and true peak); no clipping
- VO intelligible over music (music ducked under VO); sung words intelligible
- SFX serve the picture and are sparse; no stock whoosh on every move
- Music energy follows the arc; the ending resolves on the button

### Story & wording (script + captions + stills)
- Native language, register and spelling; no translation calques or hype vocabulary
- On-screen text never repeats what the picture already says
- Captions chunked by phrase, ≤ 2 lines, readable time

### Prod-ready (exports)
- Master, feed and WhatsApp (< 180 MB) files exist, play, have audio, correct duration and aspect
- Poster frame, title, post copy and captions delivered
- Numbers match the fact-check; license/source of every asset recorded

## C. The pride test (director, last)

Answer yes or no, honestly, after watching the final file end to end:
1. Would the human post this today under their own name without a disclaimer?
2. Is there one moment people will screenshot or quote?
3. Did anything make you wince? (If yes, it is a finding, not a feeling.)
4. Is it better than the last video this human shipped?
