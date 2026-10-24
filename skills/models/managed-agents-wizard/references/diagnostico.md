# diagnostico.md — find the real problem before you design the agent

You are about to turn what a person said ("un agente financiero", "un agente que me ayude con
marketing") into an agent worth building. Most first answers name a domain, not a job. Your work
here is to find the job: the moment it happens, the data it eats, the decision or action it ends
in, and who is hurt when it is late or wrong. Design nothing until you have those five facts.

## Facts already verified (2026-10-24)

- Of 147 registrations for the La Salle workshop that answered "¿Qué agente quieres construir?",
  about 1 in 5 named only a domain or nothing ("Financiero", "marketing", "Agents", "No sé aún"),
  and about 1 in 3 described a concrete loop (source → decision → action). The concrete ones came
  with the data already named: "extractos bancarios por correo", "logs de Snowflake", "decreto
  1881 de 2017", "fotos desde el celular". [registration export, read locally; names not kept]
- The strongest ideas share one shape: something arrives or changes on a schedule, a person
  today spends hours turning it into a decision, and a mistake costs money or a deadline. [same]

## 1. Get the five facts

Ask in one message, in plain words, only what the description did not already give:

| Fact | Ask | A good answer sounds like |
|---|---|---|
| **Trigger** | ¿Qué pasa justo antes de que necesites esto? ¿Cada cuánto? | "Cada lunes llega el extracto", "cuando un contratista sube una póliza", "cuando cae una métrica" |
| **Input** | ¿Qué miras hoy para hacerlo a mano? ¿Dónde vive? | "PDFs en Gmail", "una hoja de Sheets", "el tablero de Meta Ads", "logs en Snowflake" |
| **Output** | Si el agente lo hiciera perfecto, ¿qué tienes en la mano al final, y dónde lo quieres ver? | "una tabla con lo que falta por contratista", "una pestaña en mi Sheet", "un borrador en mi Gmail", "un PR" |
| **Action** | ¿Quién hace qué con ese resultado? ¿El agente puede hacerlo él? | "yo apruebo y se envía", "se crea la tarea en Notion", "se escala al de guardia" |
| **Cost of error** | ¿Qué pasa si se equivoca o llega tarde? | "glosa de la EPS", "una multa", "perdemos el lead", "nada grave" |

Two more things decide the design; ask when the job has rules or third-party data:

- **Rules and reference data**: the thresholds and policies only they know (what counts as a
  duplicate, the collection policy, the 25 rules of a matrix) and the data a rule needs that is
  not in the documents (contract value and end date). They become a custom skill and a mounted file.
- **Whose data**: documents of clients, patients or contractors carry personal data (in Colombia,
  Ley 1581). Test with invented data; before real data, the person confirms their contracts and
  data-processing authorization cover it.

If the person cannot answer **Input**, the idea is not ready: help them pick one real source they
already have, or offer the closest archetype with sample data so they still build something today.

## 2. Reframe vague ideas into a job

A domain is not a job. Turn it into one with a concrete first loop, then confirm:

| They said | Ask yourself | First loop to propose |
|---|---|---|
| "Un agente financiero" | Whose money, which document, which decision? | Every month, read the bank statements that arrive by email, categorize, compare with last month, flag anomalies, write the report. |
| "Marketing" / "redes" | Which channel, which metric, who approves posts? | Every Monday, pull last week's campaign metrics, find the 3 ads losing money, draft the changes and the copy for approval. |
| "Asistente personal" | Which inbox and calendar, which recurring pain? | Every evening, read today's email and chats, extract commitments with dates, put them on the calendar, send a digest. |
| "Agente de ventas" | Where do leads arrive, what makes one good? | On each new lead, enrich it from the web, score it against the ideal customer, draft the first message, log it in the CRM. |
| "Revisar documentos" | Which document, against which rule list? | On each upload, check the document against the requirement matrix, list what is missing, ask the uploader for it. |
| "Investigación" | Which question, which sources, for whom? | Every week, search the named sources for the questions in memory, read the top items in parallel, write a cited digest. |
| "Un orquestador de N subagentes" | What is the one deliverable? | Start with one agent and skills on the real deliverable; add a worker only where parallel reading is measured. |
| "No sé" / "quiero aprender" | What do they do every week that is boring? | Pick from `catalogo-ideas.md` by their role, build it with sample data. |

## 3. Decide what the agent may do alone

Grade the action, not the agent:

| Action | Default |
|---|---|
| Read and report | Runs alone on a schedule. |
| Write to its own space (a file, a draft, a branch, a task in a list it owns) | Runs alone; a person reviews the result. This is the gate for unattended runs. |
| Write where others see it (a comment, a message to a customer, a post) | With a person present: `always_ask` or a custom tool their app answers. Unattended: the agent writes a draft in its own space and a person sends it. Dry run in tests. |
| Money, legal, health, deleting data | Never alone. The agent prepares, a person decides. Say this to the person in one line. |

## 4. Be ambitious by default

The person came to build, and the workshop pays for the credits. Design the agent that actually
does the job, not a toy that summarizes a text:

- **A real source.** Connect the system where the input lives (an MCP connector, a mounted repo, a
  file they upload), not a pasted paragraph.
- **A real action.** End in something that changes the person's week: a draft in their inbox, a
  task, a PR, a filled sheet, an alert. Gate it, do not remove it.
- **Memory.** If the job repeats, the agent keeps a baseline, a "seen" list or a playbook in a
  memory store and gets better each run.
- **A schedule or a trigger.** An agent that only runs when someone remembers to run it is a script.
- **A checkable Goal.** The system prompt says what done looks like and the check the agent runs
  before it stops. An outcome with a rubric comes later, from real outputs, if the person wants it.
- **The right model.** Sonnet 5.5 at `medium` for most jobs; Opus 5.5 at `high` when an error
  costs a fine, a legal or a safety problem (audits, clinical, legal, tax checks); a Haiku 5.5
  worker only for parallel reading. The person can switch later with one line in `model.yaml`.
- **A test budget that lets it finish.** USD 5 for Sonnet, up to 20 for Opus `high`; measure,
  then set the cap of the schedule.

Say what you left out and why ("sin pagos automáticos: el agente prepara, tú pagas").

## Report

Before step 2 of the wizard, write back to the person in five lines: trigger, input, output,
action and its gate, and what an error costs. Confirm with `AskUserQuestion` (`Diagnóstico`):
"Sí, es esto (Recomendado)" plus the 1-3 facts most likely to be wrong as options to correct.
For a vague idea, offer the 2-3 example jobs as `AskUserQuestion` options with a preview each.
