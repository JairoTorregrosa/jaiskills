# Orchestration: run the video like a studio

A shareable 15–90 s video is a production, not a prompt: research, writing, direction, sound,
animation, critique and delivery are different jobs that benefit from different eyes. Run them
as a crew of parallel subagents coordinated through one file, with you as the director.

## Director and crew

**You are the director.** You own `ORCHESTRATION.md`, make the calls, integrate the crew's work,
review every render, and protect the idea. Critics advise; they don't vote. The most common way a
crewed production goes wrong is averaging: five opinions merged into a piece with no edge. Merge
by picking the strongest parts ("A's hook, D's arc, C's ending"), not the mean.

| Role | Phase | Parallel | Writes |
|---|---|---|---|
| Researcher | 1 | ×1–3 by topic (facts, references, vernacular) | `research/*.md` |
| Writer | 2 | ×3–5, each forced into a different angle | `script/draft-*.md` |
| Critic | 2 | ×3, blind to each other (audience, craft, director) | `script/critic-*.md` |
| Art director | 3 | ×1–3 style frames | `frames/`, §3 proposal |
| Composer / sound designer | 4 | takes in parallel | `audio/`, `cues.json` |
| VO producer | 4 | voices/takes in parallel | `audio/vo/` |
| Scene animator | 6 | ×N, one per scene | `src/scenes/<scene>` + sheet + strip |
| Fact-checker | 8 | ×1 | `qa/factcheck.md` |
| Critique lens | 8 | ×3–5 on the same render | `qa/critique-*.md` |
| Verifier | 8 | ×1 per finding batch, skeptical | verdicts into §8 |
| Export engineer | 9 | ×1 | §10 |

Prompts for each role: [../templates/crew-prompts.md](../templates/crew-prompts.md). Launch all agents of a phase in one
message so they run concurrently.

## The orchestration file

`ORCHESTRATION.md` at the project root (from [../templates/ORCHESTRATION.md](../templates/ORCHESTRATION.md)) is the contract:

- **Why a file:** parallel agents need a shared, persistent brief; chat context gets compacted but
  files survive; the human can open it at any moment and see status, decisions and findings.
- **Every agent reads all of it first** and gets its path, never a paraphrase.
- **Every agent writes only its section or output path**, then appends one line to the Log.
- **The director updates Status and the phase table at each gate**, and re-reads the whole file
  after any context compaction before touching anything.
- **§7 Decisions** records every non-obvious call with the alternative considered — that is what
  lets the human disagree precisely later, and what stops a fresh agent from undoing it.
- **§6 Ledger** records each asset's origin: source URL or file, license, or generator + the
  prompt file. Generated assets without saved prompts cannot be fixed later.
- **§8 Findings** is the only QA queue. A finding not in the table does not exist; a fix not
  verified on a fresh render is not done.

Suggested layout:

```
<project>/
  ORCHESTRATION.md
  research/            facts with sources, references, vernacular
  script/              drafts, critics, final script or lyrics
  frames/              style frames, direction notes
  prompts/             every image / music / voice prompt actually used
  audio/               takes/, vo/, music-final.wav, mix.wav, cues.json
  src/                 engine (time-pure core) + scenes/
  qa/                  sheets/, strips/, critique-*.md, factcheck.md
  out/                 animatic.mp4, v01.mp4 … final.mp4, exports/
```

## Parallel patterns

**1. Diverge → blind critics → merge.** For drafts, style frames and music takes. Force divergence
by assigning each agent a different angle (not "write a draft" five times). Critics score with the
rubric ([../templates/critique-rubric.md](../templates/critique-rubric.md)), quote lines, and end with a merge recommendation.
The writers' room of a music video that shipped ran 5 songwriters (a formal self-introduction,
a list of dev habits, the mascot arriving in the country, a community anthem, a dance-craze cumbia)
against three critics with distinct personas (a local developer scrolling LinkedIn, a professional
songwriter, the director as brand guardian). The anthem won as a film because it was the only draft
with an arc; the merge took its structure and chorus, the funny formal name and twist line from
two others, the jokes from a fourth, and one twist from the fifth — and logged what the critics
killed. The personas caught different classes of problem: a real surname used as a punchline,
lines that read as surveillance, bad security advice played as a joke.

**2. Fan out by scene on a frozen engine.** Freeze the shared engine (time-pure core, helpers,
tokens, cue loader) before phase 6. Then one animator per scene, each rendering only its range at
draft quality and attaching a contact sheet and a motion strip it has looked at. Engine changes go
through the director; parallel edits to the core are how scenes silently break each other.
What made six animators ship a full scene each in about ten minutes: a beat-by-beat storyboard
with exact times, documented helper APIs written by the agents who built them, one owned file per
animator registering only its time range, the half of each transition each scene owns written
into the storyboard, and shared helpers consumed through guarded fallbacks
(`typeof helper === 'function' ? helper(...) : fallback(...)`) so nobody waits on anybody.

**Build infrastructure before the content exists.** The timing pipeline, character rig, type
system and render tooling can be built and validated while the script and song are still being
written. When the song landed, sync was ready within minutes.

**3. Lenses → verifier → fix.** Critique lenses (visual, motion, sound, story & wording, prod-ready)
run in parallel on the same render. A skeptical verifier checks each finding against evidence
before anything is changed, rejecting fixes that would make the piece more generic or touch the
"do not touch" list. Batch the confirmed fixes, re-render, re-check the affected ranges. Stop after
three rounds or when no P0/P1 remain and the pride test passes.

**4. Research fan-out.** Facts, reference pieces and the subject's vernacular are independent —
run them together at the start.

**Mind the machine.** Renders are CPU/GPU-bound. Crew agents render their range at draft settings
(half resolution, or every Nth frame); full-quality renders belong to the director, one at a time,
in the background (tmux or a queue), never blocking the conversation.

## Gates

A phase ends on artifacts, not on an agent saying it's done: a chosen script with an image column,
locked tokens with style frames, a cue sheet that matches the audio, a contact sheet per scene, a
loudness report, a verified findings table, exports that play. The gate column of the phase table
in `ORCHESTRATION.md` lists the evidence for each.

## The human is the client

- **Default: no questions.** Decide, log in §7, keep going. The human commissioned a result.
- **Genuine taste forks only** — which concept after the writers' room, which song take, the final
  cut — and always with a recommended option first. Keep building the recommended path while
  waiting.
- **Never park a long run on a question.** In one overnight production a blocking question sat
  unanswered for hours and cost the deadline. If the human is likely away (overnight, "take all the
  time you need"), take the default and report it.
- **Screenshots without text are findings.** Locate the timestamp, name the problem yourself, fix
  it, and reply with before/after stills.
- **Report like a studio:** what was made, where the files are, what was verified and how, what
  you decided on their behalf, and what's still open.

## Deadlines and budgets

- Work backwards from the deadline: a playable `v01` by the halfway point; keep the last 25% for
  the critique loop and exports.
- Keep `out/latest.mp4` shippable at all times; every change must leave a better playable file.
- Track paid credits (music, voice, images) in §6. Prototype with cheap previews (short takes,
  draft voices, low-res images); spend on finals only after the script is locked.
- Long renders and generations go to the background with a log; check them, don't stare at them.
- Probe every paid API in the first minutes (a cheap call per endpoint you plan to use) and tell
  the human the exact plan requirement if one is gated. A music API blocked on the free tier cost
  the first hour of one production.
- Keep a fallback shot (the hero character or type on the textured ground, beat-locked) that can
  stand in for any scene that fails, and a hard stop time after which you render what exists.
- Relay new client feedback to running agents immediately (message them) instead of waiting for
  them to finish on stale instructions.
- Render finished ranges first while the last agents are still working; the frame renderer should
  be resumable so a final pass only fills gaps.

## Context durability

After compaction or a new session: re-read `ORCHESTRATION.md`, the open findings, the last render
log entry and `out/latest.mp4`'s contact sheet. Prompts in `prompts/` and cues in `cues.json` mean
any asset can be regenerated without the chat that made it.

## Optional: encode the crew as a workflow

If the harness supports scripted multi-agent workflows (for example Claude Code's Workflow tool,
when the user has opted into it), encode the phases as a script: diverge/critic/merge as parallel
agent calls, scenes as a fan-out, critique as a pipeline of lens → verifier. Save the script next
to `ORCHESTRATION.md` (e.g. `production/workflow.js`) so it can be resumed or rerun. The workflow
runs the crew; `ORCHESTRATION.md` stays the ledger.

## Cross-checking the crew

Same-model critics share blind spots. For the final critique round, add a critic from a different
model provider when one is available (for example through a CLI such as askcodex, or a
cross-provider judge skill), and give image-capable critics the stills rather than descriptions of
them.
