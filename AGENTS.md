# Agent instructions

This repo is Jairo Torregrosa's catalog of personal agent skills. It ships as one Claude Code plugin
(`jaiskills`) and installs per skill through skills.sh. `README.md` is the only file written for
humans. Everything else (skills, references, scripts, this file, the changelog) is written for coding
agents: imperative, concrete, numbers over adjectives, no marketing, no tutorial tone.

## Layout

```
skills/<bucket>/<skill>/     one skill per directory; everything it needs lives inside it
  creative/                  things people look at: videos, pages
  orchestration/             getting agents to finish: pipelines, goal loops, cross-provider judges, remote workers
  models/                    building on models: SDK agents, prompts, OpenAI from the terminal
  knowledge/                 keeping what worked: solution docs, file-based TODOs
agents/                      plugin subagents (insistir's crew); the plugin format requires them at the root
hooks/hooks.json             hook wiring only; hook scripts live in the owning skill
scripts/check.py             catalog lint: every invariant below that a machine can check
scripts/link-skills.sh       symlink skills into ~/.claude/skills and ~/.agents/skills (instead of the plugin)
.claude-plugin/              plugin.json (the shipped skill list) and marketplace.json (the repo is its own marketplace)
.claude/CLAUDE.md            imports this file for Claude Code sessions in this repo
```

Status buckets, created only when a skill needs one:

- `skills/in-progress/`: public on purpose, not in `plugin.json`, not in the README catalog.
- `skills/deprecated/`: not shipped, not in the README. Prefer deleting: tags keep old versions
  (`v0.3.0` has the constatar skills and the old `commands/`).

## Invariants

`scripts/check.py` enforces all of them except private hostnames (a review item); CI runs it on
every push and pull request.

1. Every skill in a use bucket (`creative`, `orchestration`, `models`, `knowledge`) is listed in
   `.claude-plugin/plugin.json` `skills` and has a README catalog entry that links its `SKILL.md`.
   Status-bucket skills appear in neither.
2. Frontmatter `name` equals the directory name; `description` is at most 1024 characters; no
   `version` field (the plugin version is the only version).
3. Every skill has `agents/openai.yaml` (Codex picker metadata), and its invocation policy matches
   the SKILL.md frontmatter.
4. No `commands/` directory: skills are the slash commands (`/jaiskills:<skill>` from the plugin).
5. No home-directory paths, no secrets, no private hostnames except as a documented, overridable
   default (`REMOTO_HOST`, default `jetson`).
6. Relative Markdown links resolve; hook commands in `hooks/hooks.json` point at existing scripts.

Before every commit:

```bash
uv run scripts/check.py
claude plugin validate .claude-plugin/plugin.json --strict   # plugin + components (needs the claude CLI)
claude plugin validate . --strict                            # marketplace
```

Keep `CLAUDE.md` out of the repo root: strict validation rejects it there, because a plugin-root
`CLAUDE.md` is never loaded for plugin users. Claude Code reads these rules from
`.claude/CLAUDE.md`, which imports this file.

## Writing a skill

- **Invocation.** Model-invoked by default: `description` is model-facing, lists trigger phrases in
  English and the Spanish Jairo actually uses, and says what the skill is not for. User-invoked only
  for heavy orchestrators the model must never start on its own (`insistir`, `goal-loop`):
  `disable-model-invocation: true` in SKILL.md, `policy.allow_implicit_invocation: false` in
  `agents/openai.yaml`, and a one-line human-readable description.
- **Arguments.** `argument-hint` in the frontmatter, `$ARGUMENTS` in the body.
- **`agents/openai.yaml`:**
  ```yaml
  interface:
    display_name: "Second opinion"
    short_description: "Cross-provider critique of a plan, diff or verdict"
  policy:                           # user-invoked skills only
    allow_implicit_invocation: false
  ```
- **Calling another skill.** Write "Call the Skill tool with `second-opinion`": bare name, one skill
  per call. Never link across skill folders. A user-invoked skill cannot be called by another
  skill; tell the human to run it. Plugin subagents stay namespaced (`jaiskills:insistir-worker`)
  and need a fallback, because skills.sh installs have no plugin agents.
- **Codex** runs headless through `codex exec` via `skills/orchestration/second-opinion/`, never
  through the Codex MCP server.
- **Shape.** SKILL.md is the entry point, about 250 lines at most (motion-design is the exception).
  Long procedures go to `references/`, one level deep, each linked from SKILL.md with when to read
  it. Paths inside a skill are relative to the skill directory; tell subagents the absolute skill
  path.
- **Scripts.** Python with a PEP 723 header, run by `uv run --script`. Bash with
  `#!/usr/bin/env bash`, bash 3.2 compatible, shellcheck-clean.
- **Credit** adapted work in one line in the skill and in its README entry (file-todos,
  compound-knowledge and insistir's plan deepening come from EveryInc's compound-engineering plugin).

## Adding, changing or removing a skill

One commit touches:

1. the skill directory, including `agents/openai.yaml`;
2. `.claude-plugin/plugin.json` `skills`;
3. the README catalog entry: what the skill does, and what Jairo uses it for. The use must be real
   (a production, a talk, a repo); if you don't know it, ask instead of inventing one;
4. `CHANGELOG.md`.

## Releasing

Bump `version` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` together (Claude
Code uses it to decide when installed users get an update), add a dated `CHANGELOG.md` entry, merge,
then tag the merge commit and push the tag (`git tag -a vX.Y.Z <sha> -m … && git push origin
vX.Y.Z`); the README links to tags.

## Code Review Rules

Review as the person who runs this software, not as a style checker. A
finding names an input, a state or a sequence of actions that produces a
wrong result, lost data or a broken flow for that person, and says what
they see when it happens. Without that, there is no finding.

### A confident wrong answer is the worst outcome

A visible failure is better than a quiet lie. Flag anything that turns a
missing or malformed input into a plausible-looking result: a fallback
that invents a value, a partial result presented as complete, an error
swallowed into a default, a retry that hides the first failure.

Safe path: fail loudly, return nothing, or mark the result as degraded
where the user will see it.

### Data that crosses a boundary is not ours

Input from a network, a file, a user, a model or another process can be
absent, malformed or hostile. Flag a read that does not cover those
cases, and any secret, token or personal datum that reaches a log, a URL,
an error message or a third party.

Safe path: validate at the boundary, keep secrets out of anything that
is stored or shared, and declare what could not be verified.

### What not to report

CI owns formatting, lint and tests. Do not spend a comment on
formatting, naming, comment wording, test names, doc phrasing, or a
refactor that changes nothing the user sees. Do not report an input the
system cannot receive, or a defect someone has to construct on purpose
to trigger.

One finding that costs a user beats five that cost a reviewer their
attention. When nothing meets that bar, say so and approve.
