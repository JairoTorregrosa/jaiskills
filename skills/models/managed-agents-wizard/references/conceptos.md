# conceptos.md — explain each concept the first time it matters

Read the section for a concept right before the step that introduces it. Say it in two or three
sentences with the drawing, in the person's language. One analogy per concept, no more. Never
dump all of them at once (except § Final drawing, at the end).

## The whole picture (show only if they ask "how does it all fit")

```
 tus archivos (git)            Plataforma de Anthropic
 ┌────────────────┐  ant apply  ┌─────────┐   ┌─────────────┐
 │ agents/<x>/... │ ──────────► │  Agent  │   │ Environment │
 └────────────────┘             │ (v1,v2…)│   │ (contenedor)│
                                └────┬────┘   └──────┬──────┘
 horario ─► Deployment ─┐            │               │
 evento  ─► tu código ──┼──────► Session = Agent + Environment
 persona ─► tu app ─────┘          + recursos + vaults + kickoff
                                   └─► traza en la Console, archivos en outputs/
```

## Agent

What: the brain's configuration. Model, system prompt, tools, MCP connectors, skills, workers.
Each change creates a new version; old sessions keep the version they started with.
Analogy: a job description. It says what the worker knows and may do, not when it works.

```
 Agent "pr-reviewer"  v3
 ├─ modelo:  claude-sonnet-5-5 · effort medium
 ├─ prompt:  system_prompt.md
 ├─ tools:   bash, read, grep…   (permisos: auto / always_ask / always_allow)
 ├─ MCP:     github → pull_request_read, pull_request_review_write
 └─ skills:  clear-writing
```

## Environment

What: the template of the container where tools run: network rules and packages. Reused across
agents. Each Session gets a fresh container from it; nothing survives the Session except
outputs and memory.
Analogy: the desk you give the worker each morning, cleared every night.
Cloud sandbox (2026-10-24): Ubuntu 24.04, up to 8 GB RAM and 10 GB disk; Python, Node, Go, Rust,
Java, git, rg, Playwright, LibreOffice and ffmpeg preinstalled; packages cached between Sessions.
[managed-agents/cloud-sandboxes-reference]

```
 Environment  (cloud, networking: limited)
 ┌──────────────── contenedor nuevo por Session ────────────────┐
 │ bash · python · git        /mnt/session/outputs/  → archivos  │
 │ salida permitida: api.github.com, pypi (si lo activas)        │
 │ todo lo demás: bloqueado                                      │
 └───────────────────────────────────────────────────────────────┘
```

## Session

What: one run. It joins an Agent version, an Environment, mounted resources (repos, files,
memory), vaults, and a kickoff event. It streams events, keeps the full trace in the Console,
and ends idle (done, needs you, or out of budget) or terminated.
Analogy: one shift, with a recording of everything the worker did.

```
 kickoff ─► [running] ─► agent.tool_use … agent.message ─► [idle]
                │                                           ├─ end_turn          listo
                └─ llamada en "ask" ─► [idle: requires_action] ─► tú apruebas/niegas
                                                            └─ budget_reached    sube el tope y sigue
```

## Deployment

What: a schedule (cron + IANA time zone) that creates a Session by itself, with a fixed kickoff,
budget, vaults and resources. It pins the Agent version it was created with. It can be paused;
"run now" works even while paused.
Analogy: the shift calendar. It does not do the work; it opens the shift on time.

```
 lun-vie 07:30 America/Bogota
      │
      ▼
 Deployment ──crea──► Session (Agent v3 + Environment + kickoff + tope USD 5)
      │                   └─► brief.md en outputs/, traza en la Console
   pausado = no crea nada · run = crea una ya
```

## Vault

What: a safe for credentials, outside the sandbox. MCP credentials match their server by URL;
environment-variable credentials are swapped in only on the way out, only to listed hosts. The
agent never sees the secret.
Analogy: a badge at the door, not a key in the worker's pocket.

```
 sandbox: Authorization: Bearer $TOKEN (marcador) ──► salida ──► el vault pone el valor real
                                                       solo hacia api.github.com
```

## Memory store

What: files that survive between Sessions, mounted at `/mnt/memory/<store>/`. For baselines,
"already reported" lists, playbooks. Read-only or read-write per Session. Never secrets.

## Outcome

What: a kickoff with a rubric. A separate grader checks the result against it; the agent revises
until it passes or hits `max_iterations`. Use it when a run produces one checkable deliverable.

## Final drawing

At the end, draw the person's agent with their values in place of the examples:

```
 <disparador> ─► <Deployment "<nombre>" cron, tz | trigger>
                    └─► Session ─► Agent "<nombre>" v<N> (<modelo>)
                                    ├─ tools / MCP: <...>
                                    ├─ skills: <...>
                                    └─ Environment "<...>" (hosts: <...>)
                         vault: <...>   memoria: <...>   entrega: <outputs/...>
```

## Sources

- Overview: https://platform.claude.com/docs/en/managed-agents/overview.md
- Every concept's own page: `docs.md`.
