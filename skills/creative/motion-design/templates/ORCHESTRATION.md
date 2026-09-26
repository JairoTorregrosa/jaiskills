# {{Title}} — production orchestration

> Single source of truth for this video. Every agent reads this file first, writes only
> in the section its task names, and appends one line to the log when it finishes. The
> lead (director) updates status after every phase and re-reads the whole file after any
> context compaction before doing anything else.

Status: {{phase}} · Current best cut: `{{out/v00.mp4}}` · Updated: {{YYYY-MM-DD HH:MM}}

## 1. Brief

- **Idea in one sentence:**
- **For whom, where it runs:** {{platform(s)}} · {{aspect(s)}} · {{duration}} · {{language / accent}}
- **Why they would share it:** {{what the human wants people to feel or do}}
- **The one image people will remember:**
- **Must include / must avoid:**
- **Deadline and budgets:** {{wall-clock deadline}} · {{render budget}} · {{paid credits: voice, music, images}}
- **Context used:** {{memory about the human, brand assets, data, logs, references — with paths}}

## 2. Definition of Done — the pride test

The human would post this under their own name today, without apologizing for anything.

- [ ] Frame 0 is a designed poster (no black, white or half-built frame)
- [ ] The hook lands in the first 1.5 s, with sound off; the best material is in the first 5 s
- [ ] One memorable image, and the piece ends on a button (final beat, not a fade to logo)
- [ ] Every number, name and claim on screen traces to a source listed in §6
- [ ] Copy and voice sound native in the audience's language, not translated
- [ ] Sound is designed: music, VO and SFX mixed to {{-14}} LUFS integrated, ≤ {{-1}} dBTP
- [ ] Text readable on a phone: sizes, contrast, time on screen, inside safe zones
- [ ] No slop tells from the anti-list in §3
- [ ] Critique loop closed: no open P0/P1 findings in §8, every applied fix verified on a fresh render
- [ ] Exports in §10 exist, play, and pass `scripts/video_gates.py`; WhatsApp copy < 180 MB
- [ ] Someone watched the final file end to end at 1× with sound (or its frames and audio were fully checked)

## 3. Direction (locked at the end of phase 3; changes go through §7)

- **Concept / logline:**
- **Three tone words:**
- **Palette (4–6 named hex):**
- **Type (families, roles, minimum sizes):**
- **Motion language:** {{easing set}} · {{tempo / BPM}} · {{transition grammar}} · {{camera rules}}
- **Texture:** {{grain / dither / brush / paper}}
- **Sound:** {{music genre, BPM, key}} · {{voice}} · {{SFX palette}}
- **Stack and why:** {{from references/stack-selection.md}}
- **Anti-list for this piece:** {{the specific defaults we refuse here}}

## 4. Crew and phases

| # | Phase | Gate: evidence required to move on | Agents (run in parallel where listed) | Writes | Status |
|---|---|---|---|---|---|
| 0 | Intake | §1 and §2 filled, stack chosen | director | §1 §2 | ☐ |
| 1 | Research | sources, references, what makes this subject shareable | researcher ×1–3 | `research/` | ☐ |
| 2 | Writers' room | 3–5 divergent drafts → 3 critics → chosen script or lyrics | writer ×3–5, critic ×3 | `script/` | ☐ |
| 3 | Direction | 3 style frames reviewed against the anti-list, §3 locked | art director ×1–3 | §3, `frames/` | ☐ |
| 4 | Sound | music/VO takes chosen, beat grid and cue sheet exported | composer, VO producer | `audio/`, `cues.json` | ☐ |
| 5 | Animatic | beat sheet §5 timed to audio, rough render reviewed on a contact sheet | director | §5, `out/animatic.mp4` | ☐ |
| 6 | Build | every shot renders; each scene agent attached a sheet and a strip | animator ×N (one per scene) | `src/scenes/` | ☐ |
| 7 | Assemble & mix | full render with final audio, loudness in spec | director, sound | `out/vNN.mp4` | ☐ |
| 8 | Critique loop | lenses in parallel → verifier per finding → fixes → re-render | critic ×3–5, verifier ×N | §8 | ☐ |
| 9 | Deliver | §10 complete, pride test ticked | export engineer | §10 | ☐ |

## 5. Beat sheet

| # | In–out (s) | Beat / line | Picture | Sound | Owner | Status |
|---|---|---|---|---|---|---|
| 1 | 0.00–1.50 | hook | | | | ☐ |

## 6. Sources and asset ledger

| Asset or claim | Path / URL | Source, license or generator + prompt file | Used in |
|---|---|---|---|

## 7. Decisions

| When | Decision | Options considered | Why | Reversible? |
|---|---|---|---|---|

## 8. Findings

| ID | Sev (P0–P3) | Lens | Time / frame | Finding | Verified? | Fix | Status |
|---|---|---|---|---|---|---|---|

## 9. Render log

| When | Version | Command | Duration / size | LUFS / dBTP | Notes |
|---|---|---|---|---|---|

## 10. Delivery

- Master(s) per aspect:
- Feed export(s) + gate report:
- WhatsApp copy (< 180 MB):
- Captions (burned in and/or `.srt`; decision logged in §7):
- Poster frame / covers per aspect:
- Title and post copy:
- How it was made (short and long; credits used):
- Provenance (`provenance.json`: generated assets, licenses, seeds):
- Known issues (with timestamps) and what nobody could verify:

## Log

- {{HH:MM}} {{agent}} — {{what finished, where it wrote}}
