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

Each skill is also a slash command: `/jaiskills:motion-design`, `/jaiskills:second-opinion`, and so on.

**The whole set, as a Codex plugin.** Same skills, same versions.

```bash
codex plugin marketplace add JairoTorregrosa/jaiskills
codex plugin add jaiskills@jaiskills
```

**One skill, or another agent**, through [skills.sh](https://skills.sh). It copies the files into
your project so you can edit them.

```bash
npx skills@latest add JairoTorregrosa/jaiskills                         # choose from the list
npx skills@latest add JairoTorregrosa/jaiskills --skill motion-design   # just one
```

Pick one route. With both, every skill shows up twice. Through skills.sh the commands are
`/<skill>`.

## The catalog

### Making things people look at

**[motion-design](skills/creative/motion-design/SKILL.md)**: directs a code-made video like a small
studio would. Brief, writers' room, style frames, music and sound on a beat grid, one animator per
scene working in parallel, critique rounds, and exports for every platform. It's done when I'd post
it under my own name.
<br>*I use it for* every video I make with agents. It distills six of them: a 64-second community
cumbia music video, a 60-second paper explainer, 15-second openers for my series, model-race clips
for LinkedIn, a Blender trailer for a metro line and a security explainer that took four rounds.

### Getting agents to actually finish

**[second-opinion](skills/orchestration/second-opinion/SKILL.md)**: puts GPT (GPT-6 Astra by
default, through the Codex CLI, always read-only) next to Claude as an advisor, an adversarial
reviewer or a judge. Advise gives its view beside Claude's, disagreements first; review runs
Codex's built-in reviewer; adversarial tries to break a change, optionally with two or three lenses
in parallel, and Claude checks every finding against the code before showing it; judge scores a
reviewer's verdict when you ask it to. GPT never writes the code. When fixes go back for
another look, a fix-and-recheck loop caps the rounds and keeps a ledger (adapted from tstack's
`sol-loop`, t3dotgg/tstack).
<br>*I use it for* the minute before I commit to a plan, and an adversarial pass before I ship. A model
reviewing its own family's work shares its blind spots.

### Building on models

**[agent-sdk-wizard](skills/models/agent-sdk-wizard/SKILL.md)**: first it checks your machine
(Mac or Windows) and sets up one way to pay: an `ant auth login` with the account that has your
credits, a Console API key, or your Pro/Max plan. Then nine questions, one at a time, each option
drawn as a small diagram of how your agent changes if you pick it. Out comes a runnable Claude
Agent SDK agent in Python or TypeScript, with a full system prompt, a well-built skill when one
helps, a README, the decisions behind it and a real test run. Bring a rough idea; it maps it to a
small first version. It talks in your language, Spanish by default.
<br>*I use it for* people building their first agent: my Claude Agent SDK workshops at Platzi
Conf 2026, Universidad Santo Tomás and Universidad Javeriana.

**[managed-agents-wizard](skills/models/managed-agents-wizard/SKILL.md)**: takes you from "I want an
agent that…" to a Claude Managed Agents agent that runs on its own: it explains Agent, Environment,
Session and Deployment at the moment each one matters, asks the real decisions as drawn options,
writes the system prompt in Simplified Technical English, finds MCP connectors, loads credentials
into a vault without the secret touching the chat, and lays every agent out as one folder with one
file per concern (`system_prompt.md`, `tools.yaml`, `mcp.yaml`, `schedule.yaml`…). Then it applies
with the `ant` CLI, runs a capped test session, and reads a failed session's events to tell you why
it stopped. Spanish by default.
<br>*I use it for* my Claude Managed Agents workshop at Universidad de La Salle (Oct 2026), and for
the agents I run myself: a weekly vulnerability patcher for my repos and ten always-on agents
(briefs, PR review, CI triage, release notes, a papers radar, site checks, reports, support).

**[metaprompt](skills/models/metaprompt/SKILL.md)**: takes a goal, a target model and a target
harness, and writes the complete prompt for that combination, from researched guides per model
(Claude, GPT-5.x) and per harness (Claude Code, Codex, pi, Amp and more).
<br>*I use it for* system prompts and subagent briefs in pi, Codex and Claude Code.

**[askcodex](skills/models/askcodex/SKILL.md)**: OpenAI's models from the terminal on a ChatGPT
subscription, no API key: text (or schema-checked JSON to parse), image generation and editing
(transparent or opaque background on request), transcription, quota. Drives my
[askcodex](https://github.com/JairoTorregrosa/askcodex) CLI, with a prompting guide for each model
(GPT-6.1 Sol, GPT-6 Astra, Sol and Luna, the GPT-5.6 family, Daybreak Blue, GPT Image 2).
<br>*I use it for* images for my talks and videos, and a quick GPT answer without leaving the
terminal.

## How they fit together

- **A video:** motion-design directs it end to end; askcodex makes image plates when a scene needs
  one.

## What you need

- Claude Code for the plugin, or any agent that reads `SKILL.md` files.
- [uv](https://docs.astral.sh/uv/) for the Python scripts, and `ffmpeg` for motion-design.
- agent-sdk-wizard's test run needs one credential: the `ant` CLI logged in (default), an API key, or a `claude setup-token` token (and Node for a TypeScript agent).
- managed-agents-wizard needs the `ant` CLI 1.40 or later, logged in (`ant auth login`), and
  `ANTHROPIC_API_KEY` (or the `ant` login) for its test sessions, which cost real money (capped).
- Optional: the [Codex CLI](https://github.com/openai/codex), logged in, for second-opinion
  (without it, it falls back to a Claude subagent); the
  [askcodex](https://github.com/JairoTorregrosa/askcodex) CLI for askcodex.

## Upgrading from 0.x

Commands are now the skills themselves (`/jaiskills:<skill>`). The constatar skills are gone: their
engine is private. The last 0.x layout is tagged
[`v0.3.0`](https://github.com/JairoTorregrosa/jaiskills/tree/v0.3.0). Details in the
[changelog](CHANGELOG.md).

## License

MIT. These skills follow my taste and my workflow: issues are welcome, and forking is encouraged.
