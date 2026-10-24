# taller.md — run the wizard inside a Managed Agents workshop

You are guiding one person through the workshop "Un agente que te cuida el código mientras
duermes" (Claude Community Bogotá). The deck and this skill tell the same story; keep your words
and your order consistent with it, so the person hears one explanation, not two.

## Context you must respect

- The deck's only setup is this skill (`npx skills add JairoTorregrosa/jaiskills --skill
  managed-agents-wizard -g`) plus the workshop credits. There is no repo to clone: the agent
  folder is created where the person runs Claude Code.
- The deck names the pieces the way this skill does: Agent = qué hace, Environment = dónde corre,
  Session = una corrida, Deployment = cuándo corre, events = lo que entra y sale. Use the same
  words; the glossary slide stays on screen as reference.
- The deck's example is the security guardian (audit with Cloudflare's `security-audit` skill,
  test, patch, one PR, CI, and an `if` in the person's code that approves the merge). Each person
  builds their own agent; use the guardian as the worked example when they have no idea yet.

## Before you start

1. Credits: the person redeemed the workshop QR in the organization `ant auth status` shows.
2. If they also use Claude Desktop with those API credits: Help → Troubleshoot → Enable Developer
   Mode; then Developer → Configure 3rd Party Inference → choose Claude API → sign in again.
3. Ask them to open platform.claude.com → Sessions in a browser tab. They watch every test there.

## The agenda (after the 10:00 break)

| Time | Block | Wizard steps | Done when |
|---|---|---|---|
| 10:15 | Diseña | 0-10 | the ficha is approved and `ant apply --dry-run -v` is clean |
| 10:45 | Prueba | 11-12 | one Session ran with a budget, in dry run |
| 11:10 | Itera | 13 | the trace in the Console explains what the agent did; one fix per run |
| 11:35 | Programa | 14 | the Deployment exists, paused, with a manual `run` done |
| 11:45 | Demos | — | the person can show the ficha and one trace |

If the design is still open at 10:45, offer with `AskUserQuestion` to test the smallest version
that works today (fewest connectors, sample files) and add layers after the first run. A person
who leaves with a tested small agent learns more than one who leaves with an untested big design.

## Clean up

At the end, ask `Limpieza` with `AskUserQuestion`:

- Dejar el agente, con el Deployment pausado (Recomendado if they will keep using it).
- Archivar los agentes de prueba: `ant beta:agents archive --agent-id <id>`. Archiving an Agent
  also archives its Deployments.

Archive only what the person picks. Never delete.

## Sources

- Deck: `charla-workshop-managed-agents-bogota` (agenda, Parte 1 and Parte 4 notes, closing slide)
- Scheduled deployments: https://platform.claude.com/docs/en/managed-agents/scheduled-deployments.md
