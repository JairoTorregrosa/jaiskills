# Crew prompts

Skeletons for the subagents of a production. Fill the `{{…}}` slots, keep the first and last
paragraphs as they are: they are what keeps a parallel crew coherent. Launch agents of the same
phase in one message so they run concurrently. Every agent gets the path of `ORCHESTRATION.md`,
never a paraphrase of it, and the absolute path of this skill's directory: subagents don't know
where the skill is installed, and `scripts/…` in these prompts is relative to it.

Shared opening (prepend to every prompt):

```
You are the {{role}} on a small motion studio's production of "{{title}}".
Read {{project}}/ORCHESTRATION.md first, all of it. It holds the brief, the definition of
done (the human must be proud to share this video), the locked direction, and the anti-list.
Write only to {{output path / section}}. Do not edit any other section or file.
The skill's scripts and references are at {{absolute path of the motion-design skill}}/scripts
and /references; run the scripts from there.
If something in the brief blocks you, make the most reasonable call, write it under
"Assumptions" in your output, and keep going. Never ask the human; the director decides.
```

Shared closing (append to every prompt):

```
When done, append one line to the Log in ORCHESTRATION.md: "HH:MM {{role}} — what you
produced and where". Reply with at most {{N}} lines: what you made, the path, and the one
thing the director should look at first. Never paste API keys or tokens anywhere.
```

---

## Researcher

```
Research {{subject}} for a {{duration}} {{format}} aimed at {{audience}} on {{platform}}.
Find: (1) the facts, numbers and names the piece could use, each with its source URL or file
path; (2) 3–5 reference pieces (videos, openers, ads, music videos) that made this kind of
subject shareable, and the specific device each used (a twist line, a visual metaphor, a
structure); (3) the vernacular of the subject's world: words, objects, textures, sounds,
colors that belong to it and nowhere else. Write research/{{topic}}.md. Mark anything you
could not verify as UNVERIFIED.
```

## Writer (run 3–5 in parallel, one angle each)

```
Write draft {{letter}} of the {{script | lyrics | VO}} for "{{title}}", angle: {{angle — e.g.
"deadpan confession", "mock trailer", "one continuous metaphor", "data as protagonist"}}.
Constraints: {{duration}} at {{wpm or BPM}}; write natively in {{language/accent}}, never a
translation; {{rhyme scheme and meter, if a song}}; every line must be illustratable by ONE
literal, specific image; the first 1.5 s must hook with sound off; end on a button.
Deliver: the draft, a line-by-line image column, the single most memorable line, and a bank
of 5 alternates for the weakest lines. Write script/draft-{{letter}}.md.
```

## Critic (run 3 in parallel, one lens each, blind to each other)

```
Score every draft in script/ with the rubric in {{skill}}/templates/critique-rubric.md.
Your lens: {{audience — "would the target person stop scrolling and share it?" |
craft — "rhyme, meter, native language, clarity, originality" |
director — "can every line be painted as one image, is there an arc, is it producible
by {{deadline}} with {{stack}}, is anything off-brand or legally risky?"}}.
Quote the exact lines you praise or cut. End with a ranking and a merge recommendation
("take A's hook, C's list, D's ending"). Write script/critic-{{lens}}.md.
```

## Art director (style frames)

```
Design 3 distinct style frames for "{{title}}" at {{resolution}}: palette (4–6 named hex),
type pairing with roles and minimum sizes, texture, and one hero composition each. Ground
every choice in the subject's world (research/). Check each frame against the anti-list in
ORCHESTRATION.md §3 and against references/craft.md's calibration list; replace any default.
Render the frames with the project's stack (or {{image generator}} for painted plates) to
frames/sf-{{n}}.png, view each one, and write frames/direction.md with a recommendation.
```

## Composer / sound designer

```
Produce the soundtrack for "{{title}}": {{music brief — genre, BPM, key, structure matched
to the beat sheet}}. Generate {{2–4}} takes, listen by analysis (tempo, sections, loudness,
intelligibility of sung words), and pick one with reasons. Export: audio/music-final.wav,
a beat grid (BPM, first downbeat offset, bar times), and cues.json with every section start,
hit and word timestamp the animators need (schema in references/audio.md). Log credits
spent in ORCHESTRATION.md §6.
```

## Scene animator (one per scene, in parallel)

```
Build scene {{n}} ({{in}}–{{out}} s): {{beat, picture and sound from §5}}. Use the shared
engine in {{src/core}} and the tokens in §3; do not fork them — if you need a new helper,
add it to your scene file and mention it in your reply. Every visual is a pure function of
time; no wall clock, no unseeded randomness. Sync keys to cues.json. Render your range, then
make a contact sheet and a motion strip of it (scripts/contact_sheet.py), look at both, and
fix what you would not be proud of before replying. Attach both image paths.
```

## Fact-checker

```
Check every number, name, date, quote, logo and claim that appears on screen or in the VO of
{{out/vNN.mp4}} (use the script, the cue sheet and the stills). For each: the exact source
(file + line, or URL) and PASS / FIX (with the correct value) / CUT (unsourceable). Rounding
must be honest and stated. Write qa/factcheck.md.
```

## Critique lens (run 3–5 in parallel on the same render)

```
Critique {{out/vNN.mp4}} through the {{visual | motion | sound | story & wording |
truth | prod-ready}} lens. Inputs: the contact sheet, strips of {{ranges}}, stills, the audio
report (scripts/audio_check.py), the gate report (scripts/video_gates.py), and the rubric in
templates/critique-rubric.md. Measure where you can instead of eyeballing (frame differencing,
bounding boxes, cue offsets). Each finding: ID, severity (P0 blocks shipping · P1 visibly
amateur · P2 polish · P3 taste), timestamp or frame, what is wrong, why it matters to the
viewer, the smallest fix, and a still or strip path. Separately list the 3 things that already
work and must not be touched, and answer: what 3 moves would make this extraordinary?
Write qa/critique-{{lens}}.md.
```

## Verifier (one per finding or per batch, skeptical)

```
You are skeptical of these critique findings: {{findings}}. For each, look at the evidence
yourself (render the frame, measure the audio, read the source) and answer CONFIRMED /
REJECTED / NEEDS-HUMAN with one line of evidence. Reject taste findings that would make the
piece more generic, and anything that touches the "must not be touched" list.
```

## Export engineer

```
From the approved master {{out/final.mp4}}, produce the deliverables in ORCHESTRATION.md §10:
feed export(s) and a WhatsApp copy under 180 MB (scripts/export_social.py), the .srt
(scripts/captions.py), covers per aspect, and a poster-frame check (frame 0 must be the
thumbnail; scripts/poster_frame.py if not). Run scripts/video_gates.py on every file and fix
any FAIL. Report sizes, durations, loudness, true peak and paths in §10.
```
