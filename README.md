# jaiskills

My personal agent skills, and what I actually use each one for.

Every skill here earned its place in real work: videos I posted, workshops I taught, skills I built
with other skills. They run in Claude Code, and most also run in Codex, pi and any other agent that
reads a `SKILL.md`. Take the whole set or a single skill, then make it yours.

## Install

**The whole set, as a Claude Code plugin.** It updates when I ship.

```
/plugin marketplace add JairoTorregrosa/jaiskills
/plugin install jaiskills@jaiskills
```

Each skill is also a slash command: `/jaiskills:motion-design`, `/jaiskills:insistir`, and so on.

**One skill, or another agent**, through [skills.sh](https://skills.sh). It copies the files into
your project so you can edit them.

```bash
npx skills@latest add JairoTorregrosa/jaiskills                         # choose from the list
npx skills@latest add JairoTorregrosa/jaiskills --skill motion-design   # just one
```

Pick one route. With both, every skill shows up twice. Through skills.sh the commands are
`/<skill>`, and insistir's reviewer agents and completion hook stay behind: those come only with
the plugin.

## The catalog

### Making things people look at

**[motion-design](skills/creative/motion-design/SKILL.md)**: directs a code-made video like a small
studio would. Brief, writers' room, style frames, music and sound on a beat grid, one animator per
scene working in parallel, critique rounds, and exports for every platform. It's done when I'd post
it under my own name.
<br>*I use it for* every video I make with agents. It distills six of them: a 64-second community
cumbia music video, a 60-second paper explainer, 15-second openers for my series, model-race clips
for LinkedIn, a Blender trailer for a metro line and a security explainer that took four rounds.

**[image-to-frontend](skills/creative/image-to-frontend/SKILL.md)**: turns a brief or a reference
image into four visual directions, a build spec and a working React or HTML page, iterated until it
matches.
<br>*I use it for* turning a screenshot I like, or a paragraph about a product, into a real first
page instead of a mockup.

### Getting agents to actually finish

**[insistir](skills/orchestration/insistir/SKILL.md)** (you start it: `/jaiskills:insistir <task>`):
splits a big task across parallel workers and has every worker's output reviewed by a different
agent. Nothing is marked done without an APPROVED verdict, and a hook enforces it.
<br>*I use it for* changes too big for one agent, where the reviewer must never be the author. It
built the reference guides of my metaprompt skill, and its cross-provider judge caught source
citations that the Claude reviewers had approved.

**[goal-loop](skills/orchestration/goal-loop/SKILL.md)** (you start it: `/jaiskills:goal-loop <goal>`):
loops toward a goal with a checkable finish line, the way gradient descent does: specialized agents,
a loss, textual gradients, early stopping. Some checks are hidden from the implementer, so gaming
the visible ones shows up as a gap and the iteration doesn't count.
<br>*I use it for* work with a hard finish line. The metaprompt skill came out of it, done in 2 of
its 5 allowed iterations.

**[second-opinion](skills/orchestration/second-opinion/SKILL.md)**: asks a model from another
provider (GPT-5 through the Codex CLI, read-only) to critique a plan, a diff or a review. You get
its view next to Claude's, disagreements first. In judge mode it scores a reviewer's verdict for
insistir and goal-loop.
<br>*I use it for* the minute before I commit to a plan, and as the last judge of every insistir
run. A model reviewing its own family's work shares its blind spots.

**[remote-agents](skills/orchestration/remote-agents/SKILL.md)**: runs headless Claude Code and
Codex workers on another machine over SSH. Jobs survive disconnects; results come back
cross-reviewed by the other provider.
<br>*I use it for* long jobs on the Jetson at home while my laptop sleeps.

### Building on models

**[agent-sdk-wizard](skills/models/agent-sdk-wizard/SKILL.md)**: nine questions, one at a time,
each option drawn as a small diagram of how your agent changes if you pick it. Out comes a runnable
Claude Agent SDK agent in Python or TypeScript, with a README, the decisions behind it and a real
test run. It talks in your language, Spanish by default.
<br>*I use it for* people building their first agent. It was born from my Claude Agent SDK workshop
at Platzi Conf 2026.

**[metaprompt](skills/models/metaprompt/SKILL.md)**: takes a goal, a target model and a target
harness, and writes the complete prompt for that combination, from researched guides per model
(Claude, GPT-5.x) and per harness (Claude Code, Codex, pi, Amp and more).
<br>*I use it for* system prompts and subagent briefs in pi, Codex and Claude Code.

**[askcodex](skills/models/askcodex/SKILL.md)**: OpenAI's models from the terminal on a ChatGPT
subscription, no API key: text, image generation and editing, transcription, quota. Drives my
[askcodex](https://github.com/JairoTorregrosa/askcodex) CLI.
<br>*I use it for* images for my talks and videos, and a quick GPT answer without leaving the
terminal.

### Keeping what worked

**[compound-knowledge](skills/knowledge/compound-knowledge/SKILL.md)**: when a hard problem is
solved, parallel agents write it up as a searchable solution doc in `docs/solutions/`. insistir
reads those docs before it plans the next task.
<br>*I use it for* not solving the same problem twice. One entry it wrote: why reviewers from the
same model family approve citation drift that a cross-provider judge catches.

**[file-todos](skills/knowledge/file-todos/SKILL.md)**: review findings become markdown files that
move from pending to ready to complete. You triage them one by one, then parallel workers fix the
approved ones.
<br>*I use it for* findings I won't fix today. In the metaprompt build, the judge's findings became
five todos, all closed.

file-todos, compound-knowledge and insistir's plan deepening are adapted from EveryInc's
[compound-engineering plugin](https://github.com/EveryInc/compound-engineering-plugin).

## How they fit together

- **A big change:** insistir or goal-loop does the work, second-opinion judges it, file-todos
  keeps what's left, and compound-knowledge writes down the lesson. That's how the metaprompt skill
  was built.
- **A video:** motion-design directs it end to end; askcodex makes image plates when a scene needs
  one.

## What you need

- Claude Code for the plugin, or any agent that reads `SKILL.md` files.
- [uv](https://docs.astral.sh/uv/) for the Python scripts, and `ffmpeg` for motion-design.
- insistir is built for Claude Code's agent teams, which are experimental: set
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and run it in an interactive session. Without them it
  runs the same crew as plain subagents, and the completion hook may not apply.
- agent-sdk-wizard's test run needs an `ANTHROPIC_API_KEY` (and Node for a TypeScript agent).
- Optional: the [Codex CLI](https://github.com/openai/codex), logged in, for second-opinion and the
  judges in insistir and goal-loop (without it they fall back to a Claude judge); the
  [askcodex](https://github.com/JairoTorregrosa/askcodex) CLI for askcodex and image-to-frontend;
  for remote-agents, a Linux host you reach over SSH with a key, with `python3`, `setsid` and
  `claude` or `codex` logged in, plus `rsync` on your machine.

## Upgrading from 0.x

Commands are now the skills themselves (`/jaiskills:<skill>`). The constatar skills are gone: their
engine is private. The last 0.x layout is tagged
[`v0.3.0`](https://github.com/JairoTorregrosa/jaiskills/tree/v0.3.0). Details in the
[changelog](CHANGELOG.md).

## License

MIT. These skills follow my taste and my workflow: issues are welcome, and forking is encouraged.
