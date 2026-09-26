# Asking for better work

How to commission a video from an agent (or from yourself) so the result is specific, tasteful
and shareable — and how to push an iteration without making it worse. Everything here comes from
real sessions: the prompts that produced videos people shared, and the notes that fixed the ones
that looked generic.

## Anatomy of a prompt that gets a shareable video

A good commission is short and names five things. Specs come later, from the agent.

| Part | Why it matters | Example |
|---|---|---|
| **A format the audience already knows** | Borrowed structure gives instant readability and a built-in joke or thrill | "the opening of my series", "the trailer of my life", "a Netflix protagonist intro", "a superhero intro", "a 15 s commercial", "a lyric video like the Frailejón song" |
| **Duration and destination** | Sets pacing, aspect ratio and specs | "15 seconds", "1 minute for LinkedIn" |
| **The source of truth** | Specific content is what makes it not-a-template | "with everything you know about me", "read the logs", "use the assets in this folder", "the real results of this paper" |
| **A feeling or effect** | Gives the director a target to judge against | "that makes me want to watch it twice", "cringe and proud at the same time", "groundbreaking", "something I'd be proud to post" |
| **A role** (optional) | Pulls in a craft vocabulary | "as a motion designer", "plan it like a full music-video production team" |

Leave out what the agent should decide: hex codes, fonts, libraries, scene lists. Put those in
only when reproducing a finished piece (see below) or when a brand system is fixed.

## What made prompts worse

- **Defensive clauses.** "Don't invent data", "no private info", "ask me at most 3 questions" read
  as distrust and produce timid videos. The agent should already respect truth and privacy (the
  skill says so); the prompt should spend its words on flavor. A human reviewer called an early,
  over-hedged version "muy anti-hallucinations" and "muy AI slop".
- **Tool prescriptions in a creative ask.** "Animate it in a canvas, render with Playwright and
  ffmpeg" narrows the idea before it exists. Name tools only when they are the point (e.g. a
  specific animation base the human wants to showcase).
- **Asking for virality.** "Make it viral" gives nothing to judge. Name a reference that went
  viral and ask for its *devices* (a twist line, a repeated name, a deadpan tone), not its words.
- **Genericity words.** "Dynamic", "modern", "engaging", "professional" describe every template.

## Community one-liners (Spanish originals, tested)

Short prompts anyone can paste into an agent that knows them (memory, CLAUDE.md, context). The
first two produced the videos that got shared.

```
Arma el opening de mi serie: 15 segundos, con todo lo que sabes de mí.
Preséntame en 15 segundos como si fuera el protagonista de una película de Netflix.
Hazme el tráiler de mi vida en 15 segundos, con efectos, ritmo y todo el drama.
Hazme un video de 15 segundos sobre mí que dé ganas de verlo dos veces.
Si mi vida fuera un comercial de 15 segundos, ¿cómo se vería? Móntalo.
Hazme un video de 15 segundos sobre mí, con sabor, que se sienta como yo y no como una plantilla.
Dame mi intro de superhéroe: 15 segundos, animado, con lo que sabes de mí.
Hazme un video de 15 segundos sobre mí que me dé pena ajena y orgullo al mismo tiempo.
Échame flores en 15 segundos de animación. Sin pena.
Tú me conoces: hazme un video de 15 segundos que lo demuestre.
```

English equivalents: "Make the opening credits of my series: 15 seconds, with everything you know
about me." · "Introduce me in 15 seconds as if I were the lead of a Netflix show." · "Cut the
trailer of my life in 15 seconds — rhythm, drama, all of it." · "Make a 15-second video about me
that people want to watch twice."

## Commissioning a big piece

For a 60–90 s production, one paragraph like these real commissions is enough; the skill turns it
into `ORCHESTRATION.md`:

> Use {{animation base or repo}} to create a 1-minute music video about {{community}}. Look at
> the assets in {{folder}}; you can sketch more with {{image model}}. Study why {{viral
> reference}} went viral. Take all the time you need — by {{deadline}} I want a production-ready
> video to post on LinkedIn. I have {{N}} credits on {{music/voice service}}. Plan it like a full
> music-video production team, with everything that implies, and use many subagents.

> Now a 60 s explainer of {{paper / repo}} and its results — groundbreaking. Push animation to
> extraordinary levels, use the latest animation libraries and tools, read the logs, go deep
> into what actually happened.

What makes these work: a deliverable and a deadline, real material to mine, a reference with a
reason, an explicit budget, permission to take time, and an explicit ambition level.

## Pushing an iteration

Feedback that moves a piece forward names a symptom and a direction. Use these on yourself before
the human has to:

| Note | What to actually change |
|---|---|
| "It looks AI slop / generic" | Replace every default (see craft.md calibration list) with something from the subject's world; bolder single idea; cut hedges and filler motion |
| "Más sabor" / "more flavor" | More specificity and personality: local references, in-jokes, a stronger format metaphor, a real voice; not more effects |
| "It's too busy" | One focal point per moment; stagger or remove entrances; add holds |
| "It's boring" | Escalate: shorter shots toward the payoff, a surprise at 60–70 % of the runtime, a harder button at the end |
| "I can't read it" | Bigger, fewer words, longer holds, higher contrast, captions chunked by phrase |
| "It doesn't hit" | Snap keys to beats/transients from the cue sheet; add anticipation; use a real sound for the hit |
| "It feels cheap" | Texture (grain/dither), a real typeface choice, fewer colors, consistent easing, better sound mix |
| A screenshot with no text | The human is pointing at that frame: find its timestamp, name the problem yourself, fix it, and show the before/after still |

Iteration prompts that work on an agent:

```
Dame 3 direcciones radicalmente distintas antes de animar; recomiéndame una.
¿Cuál es el frame que la gente va a capturar? Constrúyelo y dale más tiempo en pantalla.
Quítale un accesorio: el efecto del que estás más orgulloso por sí mismo.
Que la tipografía actúe lo que dice.
Cada golpe en el beat: saca los tiempos del audio, no a ojo.
Revísalo como un director que odia las plantillas y arregla todo lo que te daría pena.
```

## Reproduction prompts

When the human wants to regenerate a finished video with another tool or share "how it was made",
write the full spec — this is the one place hex codes and timecodes belong: format (resolution,
fps, codec, audio), aesthetic tokens (palette, type, texture, motion language), scenes with
timecodes and exact on-screen text, technique (render pipeline), and the QA step (review key
frames on a contact sheet before exporting). Keep it faithful to what shipped, not to the plan.
