# arquetipos.md — the job → defaults for every decision

Map the person's job to the closest row and say so in one line. The defaults are proposals; the
person can change any of them. Every row was built and run as a real agent (Oct 2026); the cost
is one measured run.

| Archetype | Example | Trigger | Kickoff | Connectors / inputs | Skills | Memory | Cost |
|---|---|---|---|---|---|---|---|
| Digest | daily brief of repos | Deployment, weekdays | outcome | GitHub MCP read-only | custom writing skill | - | USD 0.19-0.31 |
| Reviewer | review each PR | Event (GitHub Action) | message | GitHub MCP, review write as `auto` | - | - | USD 0.12 |
| Triager | why CI failed | Event (workflow_run) | message | repo mounted at the failing commit + GitHub MCP logs | - | - | USD 0.13 |
| Writer with PR | weekly release notes | Deployment, Fridays | outcome | GitHub MCP: branch, file, PR | writing skill | - | USD 0.17 |
| Researcher | weekly papers digest | Deployment, Mondays | outcome | `web_search`/`web_fetch` with `allowed_domains` | `pdf` | seen items | USD 1.57 |
| Monitor | website health | Deployment, daily | outcome | `curl` to one host | - | baseline + own check script | USD 0.11 |
| Analyst | monthly Excel + deck | Deployment, monthly | outcome | Files API upload | `xlsx`, `pptx` | - | USD 0.41 |
| Operator | meeting notes → tasks | Deployment, evenings | message | Notion MCP (`mcp_oauth`) | - | - | not run |
| Front desk | support ticket | Event (your webhook) | message | custom tools your app answers + docs files | - | playbook, read-only | USD 0.02-0.03 |
| Watchdog | API cost spikes | Deployment, daily | outcome | `environment_variable` credential, one host | - | history | not run |
| Patcher | weekly vulnerability sweep + PRs | Deployment, weekly | outcome | repos mounted + GitHub MCP writes | security-audit | - | USD 104.66 |

Defaults that hold for all rows: `claude-sonnet-5-5` (Opus only for Patcher), toolset `auto`,
web tools off unless listed, `networking: limited`, one agent (a Haiku worker only for
Researcher), a "dry run" switch in every agent that writes to a real system.
