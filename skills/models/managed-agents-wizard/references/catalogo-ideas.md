# catalogo-ideas.md — the agents people actually ask for, designed to do the job

You are about to match a person's idea to a family below and propose the agent in full: trigger,
connectors, skills, memory, kickoff, gate. Every family comes from what 147 people answered when
they registered for a Managed Agents workshop in Bogotá (Oct 2026). The designs are ambitious on
purpose: real sources, real actions behind a gate, memory, a schedule. Shrink one only when the
person asks or a credential is missing.

Connector URLs and their auth are in `conectores.md`; finding extra skills is in `skills.md`.
Never copy a design without step 1 of `diagnostico.md`: the person's five facts decide the details.

## Facts already verified (2026-10-24)

Family sizes, out of 147 answers (names not kept): finance 18, marketing and content 17,
engineering and ops 17, personal assistant 12, document compliance 11, sales 9, research,
education and health 9, field and sector operations 8, market watch 6, support 6, data 4,
"many sub-agents" 3, no concrete idea 27. [La Salle registration export, read locally]

## How to read a design

`Trigger` · `Input → connectors` · `Work` · `Output` · `Gate` · `Memory` · `Kickoff` · `Model`.
"Draft + approval": the agent never sends money, messages to third parties, or posts on its own.
In an unattended run (Deployment, trigger) the draft is a file, a Gmail draft to the person or a
tab it owns, and a person sends it; `queue_for_approval` or `always_ask` only fit when a person
or their app is there to answer, otherwise the Session waits forever.

---

## 1. Finance (18) — "un agente financiero", extractos, facturas, cartera, portafolio

What hurts: statements and invoices arrive as PDFs in email; someone types them into a sheet; late
or missed payments and collections cost money; nobody watches the portfolio daily.

**Design A — Monthly statement analyst** (one person or an accountant with N clients).
Trigger: Deployment over a window, days 2-6 of each month, so late statements still get done.
Input: statement PDFs in a Drive folder per month and client (Drive MCP); the Gmail MCP cannot
download attachments, so the person saves them from Gmail ("Guardar en Drive") or uploads them.
Encrypted PDFs must arrive unlocked (`credenciales.md` § Inside the sandbox). Work: extract every
transaction (`pdf` skill), categorize with the person's own categories and thresholds (custom
skill), check opening balance + movements = closing balance, flag duplicates, unknown suppliers,
spikes and new subscriptions. Output: where the person works: a new month tab in their Sheet
(Sheets MCP, writing only that tab) or an `xlsx`, plus a short note per client and a Gmail draft
to themselves. Gate: nothing goes to clients; the person reviews. Memory: client list, what is
done this month, suppliers seen, last month's totals. Kickoff: message; the Goal checks totals
match and every transaction has one of their categories or "Por revisar". Model: Sonnet 5.5
`medium`; Opus 5.5 if the statements feed a tax filing and Sonnet misreads them.

**Design B — Collections (cartera) agent for a small business.**
Trigger: Deployment, weekdays 08:00. Input: receivables from the ERP or a Sheet (Sheets MCP or a
file). Work: age each invoice, apply the person's collection policy (custom skill with the rules),
pick the next action per client, draft the message. Output: a task list and drafts. Gate: drafts
stay in outputs or the person's Gmail drafts; nothing is sent. Memory: last contact per client, promises to pay.
Kickoff: message. Model: Sonnet 5.5 `medium`.

**Design C — Portfolio watcher.** Trigger: Deployment, market close. Input: a market data API
(`environment_variable` credential, one host). Work: compare positions with thresholds in memory,
explain moves with cited news (`web_search` limited to news domains). Output: alert digest only
when a threshold breaks. Gate: read-only, never trades. Model: Sonnet 5.5 `low`.

## 2. Marketing and content (17) — redes, Meta Ads, tendencias, piezas

What hurts: hours each week reading campaign metrics; content calendars that slip; nobody knows
why a post went viral.

**Design — Weekly ads doctor.**
Trigger: Deployment, Monday 07:00. Input: Meta Ads or Google Ads metrics (connector, or a weekly
CSV export). Work: find campaigns below the target CPL/ROAS in memory, diagnose (audience, creative
fatigue, budget pacing), write concrete changes and 3 new copy variants per losing ad. Output:
`pptx` 5-slide report for the client + a change list. Gate: changes are proposals; a person
applies them. Memory: targets per client, last week's numbers, what was tried. Kickoff: message;
the Goal checks every claim cites a metric and every losing ad has a change. Model: Sonnet 5.5.

**Variant — Trend scout.** `web_search` limited to the platforms' public pages and news, a memory
of trends already reported, a weekly digest with 5 ideas and why each fits the niche.

## 3. Engineering and ops (17) — on-call triage, PR review, QA, vulnerabilities, migrations

What hurts: a developer gets paged for noise; PRs wait; tests are written last; legacy code blocks
a migration.

**Design A — On-call first responder.** Trigger: event (alert webhook → your code creates the
Session). Input: logs (Snowflake, Datadog, Sentry connector), the repo mounted read-only, the
runbook as a skill. Work: correlate the alert with recent deploys and errors, classify (real
incident / known flake / noise), propose the fix or the rollback. Output: a triage note in the
incident channel. Gate: posting is allowed; paging a human only when the class is "real incident".
Memory: past incidents and their causes. Model: Opus 5.5 `high` (ambiguous, costly when wrong).

**Design B — PR reviewer / CI triager / vulnerability patcher.** The tested agents in the
showcase: `pr-reviewer`, `ci-failure-triager`, the weekly vuln-patcher (repo mounts + GitHub MCP +
`security-audit` skill, merge only by a narrow rule). Never auto-approve PRs: review, comment,
and let the merge rule live in code.

**Design C — Test writer.** Trigger: label on a PR. Input: the diff (repo mounted). Work: write the
missing tests, run them in the sandbox, push to a branch. Output: a PR with tests. Gate: the person
merges.

## 4. Personal assistant (12) — agenda, correo, chats, proyectos freelance

What hurts: commitments scattered across email, WhatsApp and calendars; weekly status reports by
hand; follow-ups forgotten.

**Design — Chief of staff.** Trigger: Deployment, 18:00 every weekday. Input: Gmail and Calendar
connectors (or Microsoft 365), the project tracker (Notion, Linear, Sheets). Work: extract every
commitment with a date and owner, compare with the calendar and the tracker, detect conflicts and
things that will slip, draft the follow-ups. Output: a 1-screen evening digest + calendar holds
created in a calendar the agent owns. Gate: emails are drafts, never sent. Memory: projects,
people, open promises. Kickoff: message. Model: Sonnet 5.5 `medium`.

## 5. Document compliance (11) — pólizas, soportes clínicos, aduanas, SST, procesos judiciales

What hurts: someone checks every document against a requirement list by hand; a missing page
costs a rejected invoice (glosa), a fine, or a missed legal deadline. These are the best ideas in
the set: clear input, clear rule, measurable cost.

**Design — Document auditor.** Trigger: event (a folder or form upload creates the Session) or a
daily Deployment over a Drive folder; uploaded files are fixed, so a daily run over uploads
re-reads the same documents. Input: the documents (Drive connector or mounted files), the
requirement matrix as a custom skill (one rule per line, with its legal source), and the reference
data the rules need but the documents lack (contract value, end date, type) as a mounted sheet.
Scanned Spanish documents: check which OCR languages the sandbox has before you promise OCR. Work: read
each document (`pdf` skill; images too), check every rule, quote the page that proves each pass.
Output: a per-document checklist (pass / fail / unreadable, with page) and a message to the
uploader listing exactly what is missing. Gate: the message is a draft file; the decision stays
human. Memory: files already checked, pending items per contractor, rules that caused disputes;
mount the rules `read_only`, because the agent reads documents written by third parties. Kickoff: message; the Goal checks every rule
has a verdict with a page reference and nothing is marked pass without evidence. Model: Opus 5.5
`high` (clinical, legal, customs).

**Variant — Court case watcher.** Daily Deployment, `web_fetch` limited to the public court
consultation site, memory of the last action per case, email digest only on changes.

## 6. Sales (9) — copiloto, SDR, cotizaciones, lead scoring

**Design — Inbound SDR.** Trigger: event (new lead in the CRM or form). Input: HubSpot or
Salesforce connector, `web_search` for company research. Work: enrich, score against the ideal
customer profile (custom skill), pick the playbook, draft the first message, log everything in the
CRM. Output: CRM note + draft. Gate: the draft waits for the rep. Memory: what converted. Model:
Sonnet 5.5. Reference: Anthropic's own sales team rebuilt inbound on Managed Agents.

## 7. Research, education and health (9)

**Design — Literature radar.** The tested `research-radar`: web tools limited to scholarly
domains, Haiku `paper-reader` workers in parallel, memory of seen papers, PDF digest. For clinical
decision support, add: answers cite the source, the agent never gives a diagnosis to a patient,
and a clinician reads every output.

**Design — Exam coach.** Conversation (`user.message`), the syllabus and past questions as files,
memory of the learner's weak topics, a quiz each session that targets them.

## 8. Field and sector operations (8) — cultivo, inmobiliaria, energía, Autodesk

**Design — Field log from the phone.** Trigger: event (a WhatsApp or Telegram message with a photo
reaches your webhook, which creates the Session). Input: the photo and text, the parcel history in
memory. Work: describe the state, extract the fields, write the record into the ERP or a Sheet,
answer with the next action. Gate: writes only to the log. Model: Sonnet 5.5 (vision).

## 9. Market watch (6) — arriendos, precios, empleo, convocatorias

**Design — Watcher with memory.** Daily Deployment, `web_fetch` limited to the listed sites (check
their terms; prefer official APIs), memory of items already seen, score each new item against the
person's criteria in memory, alert only on new matches. For job search: also tailor the CV draft
per offer (`docx` skill), never apply automatically.

## 10. Support (6) — clasificar incidentes, base de conocimiento, preguntas

**Design — Front desk.** The tested `support-triage`: custom tools answered by the person's app,
docs as files, playbook as read-only memory, escalation on refunds, security and anger. Add the
ticket history (Zendesk or Intercom connector) to suggest the fix that worked last time.

## 11. Data (4) — EDA, dashboards, bases públicas

**Design — Dataset analyst.** The tested `spreadsheet-reporter`: file upload, data-quality
section, `xlsx` + `pptx`. For Looker Studio or BigQuery: a read-only connector and the rule that
the agent never edits a dashboard, only documents it.

## 12. "Un orquestador de N subagentes" (3)

Start with one agent and skills on one real deliverable. Add a worker only where parallel reading
is measured (`research-radar` pattern). Say this plainly: more agents cost more and lose context
at every handoff.

## 13. No concrete idea yet (27)

Ask their role and their most boring weekly task, then propose the family that fits. If they
have no data at hand, build Design 1A or 5 with sample files so they leave with a working agent.
