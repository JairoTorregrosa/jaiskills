---
name: agent-sdk-wizard
description: >-
  Build a working Claude Agent SDK agent by asking the user 9 illustrated questions, one at a
  time, then generating and running the code. Trigger on "crea un agente", "quiero hacer un
  agente con el SDK", "ayúdame a armar mi agente", "nuevo agente paso a paso", "agent sdk
  wizard", "build an agent with the Claude Agent SDK", "help me create an agent step by step",
  "set up an agent project". Each question is one AskUserQuestion call whose options all carry an
  ASCII diagram in `preview`, in plain language for someone who has never seen an agent. Produces
  a directory with agente.py or agente.ts, its manifest, a README, a decisiones.md, and a real
  test run. NOT for the raw Messages API, Managed Agents, or the Claude Code CLI itself — those
  are different products; say so and stop.
---

# agent-sdk-wizard — 9 illustrated questions → a running agent

The user knows what they want the agent to do. They do not know which of the ~65 SDK options
does it. This skill closes that gap by **asking, not explaining**: nine questions, each with a
drawing of what changes, then it writes the agent and runs it.

## Decision table — is this the right skill?

| The user says | Do |
|---|---|
| "quiero hacer un agente", "build me an agent", "agente con el SDK" | **This wizard.** Start at step 1. |
| "explícame el Agent SDK", "¿qué es un hook?" | Answer directly. Point at `references/glosario.md`. No wizard. |
| "arregla mi agente", "¿por qué falla esto?" | Read their code. Use `references/errores.md`. No wizard. |
| "quiero usar la Messages API / Managed Agents" | Different product. Say so in one line and stop — this wizard only builds Agent SDK agents. |
| "agrégale un hook a mi agente" (agent already exists) | Just that step. Read `references/opciones-sdk.md` for the exact code, edit their file. |

## Hard rules

These are not suggestions. Breaking one breaks the wizard.

1. **One `AskUserQuestion` call per step. One question per call.** Never two questions in the
   same call — `preview` only renders on single-answer questions.
2. **Never `multiSelect: true`.** It kills the previews.
3. **Every option carries a `preview`**, copied from `references/previews.md`. No exceptions,
   including the sub-questions.
4. **The recommended option goes first**, with `(Recomendado)` appended to its label
   (`(Recommended)` if the user writes in English).
5. **`header` ≤ 12 characters.** The headers below already comply.
6. **2–4 options per question.** The UI adds "Other" by itself — never write your own.
7. **Do not advance without an answer.** After each answer, write **one line** confirming the
   decision, then ask the next question. Example: `Listo: Python. Ahora, ¿qué tiene que lograr?`
8. **Language follows the user.** `SKILL.md` and the references are English; every question,
   preview label, comment and generated README comes out in the language the user writes in.
   Spanish is the default for this audience.
9. **Never use the "explain like I am five" framing** — not that phrase, not its Spanish
   translation, not any variant of it, anywhere the user can see. Explain like you would to a
   smart person who has not seen this before: one concrete analogy, one drawing.
10. **Never invent an API name.** Every option maps to exact code in
    `references/opciones-sdk.md`, verified against TS SDK 0.3.251 / Python SDK 0.2.148 /
    Claude Code 2.1.251. If it is not in that file, do not write it.

## Skipping steps

Step 2 (objetivo) sets defaults for steps 3–9 — the table is in `references/arquetipos.md`.
When the goal makes a step meaningless, **say so in one line and skip it with the default**:

- Goal is a single question with no files → skip 6 (skills), 7 (subagentes), 9 (hooks).
- Read-only goal → skip 9 (hooks); step 8 defaults to `default` + `allowed_tools`.
- The user said "todos los recomendados" / "just use the defaults" → skip every remaining
  question, take the recommended option for each, and go straight to generation. Show them the
  9 decisions afterwards so nothing is a surprise.

Never skip step 1, step 2, or step 5.

## The nine steps

Full option text, previews and sub-questions live in `references/previews.md`, section by
section. Read that file before the first question. For each step below: ask exactly this
question, with exactly these options, in this order.

| # | `question` | `header` | Options (recommended first) | Preview section |
|---|---|---|---|---|
| 1 | ¿En qué lenguaje quieres tu agente? | `Lenguaje` | Python · TypeScript | `previews.md` § Step 1 |
| 2 | ¿Qué tiene que lograr tu agente? | `Objetivo` | Responder preguntas sobre mis archivos · Cambiar archivos o código · Llamar a mis funciones o APIs · Conversar varias vueltas con memoria | § Step 2 |
| 3 | ¿Qué tan listo lo necesitas (y cuánto quieres pagar)? | `Modelo` | Sonnet 5 · Haiku 4.5 · Opus 5 · Fable 5 | § Step 3 |
| 4 | ¿Qué personalidad y reglas fijas tiene tu agente? | `Instrucción` | Mínimo + mis reglas · Preset de Claude Code + mis reglas · Solo el preset · Mío completo desde cero | § Step 4 |
| 5 | ¿Qué puede hacer tu agente en el mundo? | `Herramientas` | Solo leer · Leer y escribir archivos · Todo, incluida la terminal · Mis propias funciones | § Step 5 |
| 6 | ¿Tu agente necesita saber un procedimiento tuyo? | `Skills` | No por ahora · Sí, una skill nueva · Sí, ya tengo skills en este proyecto | § Step 6 |
| 7 | ¿La tarea es tan grande que conviene repartirla? | `Subagentes` | No, un solo agente · Sí, un ayudante especializado · Sí, varios en paralelo | § Step 7 |
| 8 | ¿Quién autoriza cada acción del agente? | `Permisos` | Aprueba solo lo que listé · Que edite archivos sin preguntar · Que me pregunte a mí · Sin frenos (solo en sandbox) | § Step 8 |
| 9 | ¿Quieres un vigilante automático, código tuyo, en el ciclo? | `Hooks` | No por ahora · Bloquear comandos peligrosos · Guardar un registro de todo · Verificar el trabajo al final | § Step 9 |

### Three conditional sub-questions

Each is a separate `AskUserQuestion` call with its own previews. Ask only when the condition holds.

| After | Condition | `question` | `header` | Options |
|---|---|---|---|---|
| 3 | model is Opus 5 or Fable 5 | ¿Cuánto quieres que piense antes de responder? | `Esfuerzo` | Alto (`high`) · Muy alto (`xhigh`) · Medio (`medium`) |
| 4 | answer was 4A, 4B or 4D | ¿Qué reglas fijas le pones? | `Reglas` | Analista de datos · Asistente de código · Operador cuidadoso |
| 5 | answer was 5D (own functions) | ¿Además quieres conectar un servidor que ya existe? | `MCP` | No, solo mis funciones · Sí, un servidor MCP externo |

If the user picks "Otra" on the `Reglas` sub-question, take their free text verbatim as the
rules paragraph.

### What each step decides

Exact TS and Python code for every answer: `references/opciones-sdk.md`.

| Step | Produces |
|---|---|
| 1 | `agente.py` + `pyproject.toml`, or `agente.ts` + `package.json`. Also `query()` vs `ClaudeSDKClient`/`Query` — decided by step 2, not asked. |
| 2 | The test prompt, the `cwd`, the sample data, and the defaults for steps 3–9 (`arquetipos.md`). |
| 3 | `model=` (+ `effort=` if the sub-question ran). |
| 4 | `system_prompt=` — plain string, or the `preset` object with `append`. |
| 5 | `allowed_tools=[…]`; for own functions also the `@tool` / `tool()` skeleton, `create_sdk_mcp_server`, and `mcp_servers={…}`. |
| 6 | `.claude/skills/<name>/SKILL.md`, `setting_sources=["project"]`, `skills=[…]`. |
| 7 | `agents={…}` with `AgentDefinition`, plus `"Agent"` in `allowed_tools`, plus the `parent_tool_use_id` filter in the stream reader. |
| 8 | `permission_mode=`, `allowed_tools` / `disallowed_tools`, and the `can_use_tool` callback if chosen. |
| 9 | `hooks={…}` with the ready-made function from `templates/hooks.py` or `templates/hooks.ts`. |

## Generation

Once the nine answers are in, create `<nombre-del-agente>/` in the user's current directory —
ask for the name in one line if they have not said it; otherwise derive it from the goal
(kebab-case, Spanish, no accents).

Fill the templates in `templates/`. Do not write the code from memory: start from the template
and substitute.

| File | From | When |
|---|---|---|
| `agente.py` | `templates/agente.py.tmpl` | step 1 = Python |
| `agente.ts` | `templates/agente.ts.tmpl` | step 1 = TypeScript |
| `pyproject.toml` | `templates/pyproject.toml` | step 1 = Python |
| `package.json` | `templates/package.json` | step 1 = TypeScript |
| `hooks.py` / `hooks.ts` | `templates/hooks.py` / `templates/hooks.ts` | step 9 ≠ "No por ahora" |
| `.claude/skills/<n>/SKILL.md` | `templates/skill.md.tmpl` | step 6 = "una skill nueva" |
| `workspace/ventas.csv` | `templates/ventas.csv` | goal needs sample data (see `arquetipos.md`) |
| `README.md` | `templates/README.md.tmpl` | always |
| `decisiones.md` | `templates/decisiones.md.tmpl` | always |
| `agente.ipynb` | derive from `agente.py` | only if the user asked for a notebook |

Non-negotiables in the generated code:

- The whole configuration is **one visible block** at the top — `opciones = ClaudeAgentOptions(…)`
  or `const opciones: Options = {…}` — and **every line carries a `# paso N: …` comment**. That
  block is the point: it is the map from the nine answers to the SDK.
- **`max_turns` and `max_budget_usd` are always set.** Defaults: `max_turns=25`,
  `max_budget_usd=0.15`. No generated agent ships without both.
- The stream reader prints text, tool calls as `🔧 nombre(argumento)`, tool errors, and the final
  `result` with turns and cost. It is in the templates; keep it.
- Comments in the user's language.
- **No absolute paths from any machine.** Everything is relative to the generated directory.

### Notebook variant

If the user wants `agente.ipynb`, the cell body is the same code with three changes: drop
`import asyncio`, drop `async def main()` and `asyncio.run(main())`, and put the `async for`
at the top level of the cell. `await`, never `asyncio.run` — a kernel already has a running
event loop. Do not add `nest_asyncio`; it is not needed.

## Test run — the wizard is not done until the agent runs

1. Check the key: `echo "${ANTHROPIC_API_KEY:+present}"`. If it is empty, tell the user in one
   line: *"Necesito tu API key de la consola de Anthropic. Córrela en tu terminal:
   `export ANTHROPIC_API_KEY=sk-ant-…`"*, and wait. The SDK does not read `.env` on its own.
2. Install: `uv sync` (Python) or `npm install` (TypeScript), inside the generated directory.
3. Run once with the test prompt from step 2: `uv run agente.py` or `npx tsx agente.ts`.
4. Show the user the `result` line: turns and cost.
5. **If it fails, fix it before saying done.** `references/errores.md` maps the exact message to
   its cause and its fix. Do not hand back a broken agent with an explanation.

## Closing

Do not re-explain the SDK. Show:

1. The loop, drawn with the nine decisions already in it (the shape is in the generated README).
2. The three commands to run it again.
3. One line: what it cost.

Then stop. The README and `decisiones.md` carry everything else, and `decisiones.md` names the
research file for each decision so the user can go deeper on their own.
