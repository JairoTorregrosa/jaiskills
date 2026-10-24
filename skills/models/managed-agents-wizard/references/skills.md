# skills.md — find skills that already do part of the job

You are about to look for Agent Skills to attach to the person's agent. A skill holds a procedure
or domain knowledge the agent loads only when it needs it, so the system prompt stays short. Search
before you write one: Anthropic and the vendors already publish skills for most business jobs.

## Context you must respect

- Managed Agents takes two kinds: Anthropic prebuilt skills by ID (`{type: anthropic, skill_id:
  xlsx}`) and custom skills uploaded from a folder with `SKILL.md` (`ant apply skills/<name>` →
  `skills: [../../skills/<name>]` in `skills.yaml`).
- A skill runs with the agent's own tools and network. It gets no extra access: a skill that calls
  a vendor CLI or API needs that host in `allowed_hosts` and a credential in the vault.
- A third-party skill is code and instructions that will run with the person's data. Vet it
  (§ Vet) before you attach it.

## Facts already verified (2026-10-24)

- Prebuilt skills: exactly `xlsx`, `docx`, `pptx`, `pdf` (`ant beta:skills list --source anthropic`).
- Custom skill limits: under 30 MB uncompressed; `name` at most 64 characters, lowercase, digits
  and hyphens, without "anthropic" or "claude"; `description` at most 1,024 characters; up to 500
  skills per session. Managed Agents also loads `.claude/skills/<name>/SKILL.md` from a mounted
  repository, with no review step. [managed-agents/skills, skills-guide]
- `anthropics/knowledge-work-plugins` (Apache-2.0) holds business skills by function. Useful ones:
  - finance: `reconciliation`, `variance-analysis`, `financial-statements`, `close-management`
  - small-business: `invoice-chase`, `pay-the-bills`, `cash-flow-snapshot`, `ad-manager`,
    `hiring-screener`, `lead-finder`, `speed-to-lead`, `inbox-manager`, `inventory-planner`,
    `contract-review`, `review-reputation`, `ticket-deflector`, `social-content-engine`
  - sales: `lead-triage`, `account-research`, `draft-outreach`, `pipeline-review`, `daily-briefing`
  - legal: `review-contract`, `compliance-check`, `triage-nda`, `vendor-check`
  - marketing: `performance-report`, `campaign-plan`, `seo-audit`, `content-creation`
  - customer-support: `ticket-triage`, `draft-response`, `kb-article`, `customer-escalation`
  - engineering: `incident-response`, `code-review`, `debug`, `testing-strategy`, `runbook` (operations)
  - data: `explore-data`, `validate-data`, `statistical-analysis`, `sql-queries`
  - human-resources: `recruiting-pipeline`, `interview-prep`, `policy-lookup`
  [github.com/anthropics/knowledge-work-plugins, listed 2026-10-24]
- `anthropics/skills` holds general skills (`skill-creator`, `mcp-builder`, `webapp-testing`,
  `doc-coauthoring`, `internal-comms`, `frontend-design`, …). [github.com/anthropics/skills]
- Vendor skills: Stripe `stripe/ai`, Cloudflare `cloudflare/security-audit-skill` and
  `cloudflare/skills`, Supabase `supabase/agent-skills`, Notion `makenotion/skills`, Sentry
  `getsentry/skills`, HubSpot `hubspot/agent-cli-skills`, Vercel `vercel-labs/agent-skills`.
- skills.sh has a public search endpoint that returns JSON:
  `curl -s 'https://skills.sh/api/search?q=<words>&limit=10'` (add `&owner=<github-org>` for one
  publisher) → `{skills: [{id, source, skillId, name, installs}]}`. Its install-time audit:
  `curl -s 'https://www.skills.sh/tele/audit?source=<owner/repo>&skills=<skill>'`.

## Do this

1. From the five facts (`diagnostico.md`), write 2-3 search phrases in English that name the
   **work**, not the domain: "overdue invoice reminders", "bank statement reconciliation",
   "contract compliance checklist", "incident triage runbook".
2. Search, best source first:
   ```sh
   gh api repos/anthropics/knowledge-work-plugins/contents/<function>/skills --jq '.[].name'
   curl -s 'https://skills.sh/api/search?q=<phrase>&limit=10' | jq -c '.skills[] | {id, installs}'
   curl -s 'https://skills.sh/api/search?q=<phrase>&owner=<vendor-org>&limit=10' | jq -c '.skills[]'
   ```
3. Read the candidate's `SKILL.md` (`gh api repos/<owner>/<repo>/contents/<path>/SKILL.md --jq
   .content | base64 -d`). Keep it only if its procedure matches the person's job and its tools
   exist in this agent (a skill written for Claude Code's `Read`/`WebFetch` still works: the
   Managed Agents toolset has `read` and `web_fetch`).
4. Vet it (§ Vet). Then copy the folder into `skills/<name>/` of the project, adapt the parts that
   name another product (a ledger the person does not use, a connector they do not have), keep the
   license file and a one-line credit, and add it to `skills.yaml`.
5. Write a custom skill when nothing fits and the procedure is the person's own: their collection
   policy, their requirement matrix, their scoring rules, their runbook. Use the `skill-creator`
   shape: `SKILL.md` with a trigger description, the procedure, and the data in reference files.
6. Prefer a skill over prompt text when the content is a procedure longer than about 10 lines, a
   table of rules, or knowledge only some runs need.

## Vet

1. Source: Anthropic, then the vendor's own GitHub organization, then anything else (untrusted).
2. Read every file: scripts, references, assets. Look for network calls, installs at run time,
   file writes outside the work folder, and instructions that do not match the description.
3. A skill that fetches URLs at run time can pull injected text: pair it with `limited`
   networking and no write tool on `always_allow`.
4. License: keep MIT/Apache-2.0 notices; do not copy a skill with no license into a public repo.
5. Signals, not proof: skills.sh installs and audit verdicts, stars, last push date.
6. API-uploaded skills are not scanned by Anthropic: the review is yours.

## Report

Tell the person, per skill: what it does for this agent, where it came from, its license, and
what you changed in it.

## Sources

- https://platform.claude.com/docs/en/managed-agents/skills.md
- https://platform.claude.com/docs/en/build-with-claude/skills-guide.md
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.md (security considerations)
- https://github.com/anthropics/knowledge-work-plugins · https://github.com/anthropics/skills
- https://skills.sh
