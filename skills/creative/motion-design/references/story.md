# Story: concepts, hooks, beat sheets, lyrics and VO

The picture can only be as good as the idea it serves. This file covers phase 2 (writers' room)
and the story side of phases 4–5. Timing and craft rules live in [craft.md](craft.md).

## Start from know / feel / do

Before any draft, write three lines in `ORCHESTRATION.md` §1: what the viewer should **know**
after one watch, what they should **feel**, and what they should **do** (reply, follow, visit,
forward it). Then name the one image people will remember. Every beat either sets it up, pays it
off, or gets cut.

## Pick a frame before you pick a style

A borrowed format gives structure, pacing, sound grammar and joke slots for free. In the
productions behind this skill, genre-framed briefs beat neutral ones every time: a personal
"animated bio" read as a template, while the same person's streaming-series cold open and anime
opening were the pieces people shared.

| Frame | Structure it lends | Good for |
|---|---|---|
| Streaming-series cold open / trailer | Logo sting, letterbox, "BY DAY / BY NIGHT" cards, title slam, parody UI end card | Personal intros, team or product launches |
| Anime or TV opening | One scene per bar, character cards, "technique" montage on beats, villain, staff credits | Personal or community pieces with in-jokes |
| Lyric / music video | Verse–chorus–list–chorus, one literal image per line, a spoken button | Communities, campaigns, anything that should be sung back |
| Data documentary | Question → evidence → mechanism → verdict, the data as protagonist | Papers, evals, benchmarks, reports |
| Race / versus replay | Real footage side by side, only live data on screen | Benchmarks, before/after, tool comparisons |
| Keynote reveal | Problem, one hero object, three proofs, the reveal, the price or CTA | Products, features |
| Commercial parody | Voice-over promise, absurd specifics, disclaimer gag, slogan | Humor pieces, community promos |

If the brief has no frame, propose one (or three, in the writers' room) instead of defaulting to
a neutral montage.

## Specific beats generic

- Mine real lore: the person's actual projects, the community's in-jokes, the dataset's real
  numbers, the logs' real timestamps. Map them onto the frame's slots (the villain, the sidekick,
  the "technique", the Top-10 badge).
- "Deep inside what happened" means putting the raw material on screen: verbatim log lines,
  the real clock of the night the run happened, one mark per real data point.
- Anchor palette and symbols to the source's own material (a paper's diagram colors, a brand's
  mascot, a country's flag used sparingly).
- Private details are an editorial decision, not a default: home network details, family,
  locations and travel go on screen only deliberately, and get flagged to the human before a
  public post.

## Hooks (first frame, first 1.5 s, first 5 s)

- **Frame 0 is the thumbnail.** It states the promise as a composed still: the question, the
  character, the claim. Never black, never a fade-in, never a logo sting.
- **First 1.5 s, sound off:** one of — payoff first; an impossible or contrast image; a claim with a
  specific number; mid-action; a pattern interrupt; a direct question the video answers.
- **First 5 s:** the best material. Viewers and the humans commissioning the video judge here first.
- For explainers: make it clear why the viewer should care before 20% of the runtime.

## Beat sheets

Adapt, don't fill in blindly. Times in seconds.

- **15 s opener:** hook 0–2 · setup 2–5 · turn 5–10 · payoff 10–13 · button 13–15 (hold, then cut).
- **30 s:** hook 0–2 · problem 2–7 · turn 7–12 · three proof beats 12–24 · payoff 24–27 · button 27–30.
- **60 s explainer:** hook 0–3 · why care 3–10 · mechanism in three steps 10–40 · proof or number
  40–50 · payoff image 50–56 · button 56–60. Change the picture at least every ~5 s; keep every
  shot ≥ 1.2 s.
- **60–90 s music video:** intro motif (4–8 bars) · verse (establish) · chorus (peak visual idea) ·
  list or bridge (change of palette or space) · final chorus (bigger) · button on the last hit.

Write the beat sheet into `ORCHESTRATION.md` §5 with in/out times, picture, sound and owner.

## The writers' room

Run 3–5 writers in parallel, each forced into a different angle (the frame, the premise, the
point of view). Each delivers: the draft, a line-by-line image column (one literal, specific,
drawable image per line), the single most memorable line, and alternates for the weakest lines.
Three blind critics score with [../templates/critique-rubric.md](../templates/critique-rubric.md): the audience (would the target
person stop and share?), the craft (language, rhyme, meter, clarity), the director (visualizable,
arc, producible, brand-safe). The director merges the strongest parts and logs what was cut and why.

Put the forbidden list in the brief: phrases from the reference you must not reuse, hype words,
anything off-brand, and facts that are no longer true ("the fest already happened").

## Writing lyrics

- Write natively in the audience's language and register. Never translate from English; calques
  and English syntax are the first thing a native ear rejects.
- Borrow a viral reference's **functions**, never its words or melody: e.g. a funny formal full
  name sung early, a deadpan twist line in the first 10–15 s (the one that becomes the meme), a
  repeatable hook with the name, a self-deprecating self-description, a didactic list of concrete
  items, a final chorus, a spoken button.
- Meter: at 100–108 BPM, about one octosyllable per bar (≈ 3.3 syllables/s); keep list lines
  ≤ 4.3 syllables/s. Rhyming lines within ±1 syllable of each other; the stressed syllable on
  the downbeat; one anchor rhyme family through the song.
- Double meanings and local register carry humor (a word that means both "patch" and "your
  crew"). Humor comes from content, not from acting.
- For music generators: write a "for the generator" version with phonetic respellings of brand
  and technical words, and a "for the screen" version with real spelling. Put stage directions in
  `{braces}` (parentheses get sung). Have the lead vocal sing the brand line; crowds only double it.
- Size song sections in whole bars at the target BPM so section changes land where cuts belong.

## Writing VO

- Time explainers from the voice: shot length = measured VO + 0.4–0.5 s tail. Budget words
  against the duration (Spanish narration lands around 2.3–2.8 words per second at a natural
  pace); when over budget, cut words — don't speed the voice up.
- Write numbers as words for the TTS and as digits on screen; check pronunciation of names with a
  transcription round-trip and rewrite lines the voice keeps mangling.
- One point of view, one narrator. A relay of voices reads as patchwork.
- Don't narrate the latest fix ("patch narrative"); tell the whole thing from the viewer's side.
- Leave room: VO does not need to cover every second. A beat of music alone after a reveal lands
  harder than another sentence.

## On-screen words

- Every word must earn its place: data widgets (one number per beat), lyrics in a lyric video,
  the closing line. No narrative UI: kickers, step numbers, chips, progress bars, "(reference)"
  labels, verdicts that tell the viewer what to think.
- Never repeat what the picture or the VO already says.
- Positive statements of what it is; no negations or disclaimers as copy.
- Local formats: numbers, dates and decimals in the audience's locale (es-CO: `58.184`, `0,655`).
- Verify every date, weekday, link and "registration is open" claim before it goes on screen or
  into the post.

## Endings

End on a button: an image, line or sound that closes the loop the hook opened, held 1.5–2.5 s,
then one clear action (URL, handle, "reply with your favorite line"). A fading logo with a tagline
is not an ending. For loops on social, consider matching the last frame to the first.

## Packaging is part of the story

Draft alongside the cut: the title, the poster (frame 0 or a designed cover per aspect), the post
copy in the human's voice (start from their hook line if they gave one; link in the first comment
when the platform penalizes links), captions, and a short "how it was made" note that claims only
what was actually used.
