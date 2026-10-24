# docs.md — where each fact lives in the official docs

Read the page for a topic before you write a field this skill does not show, before you tell the
person something is not supported, and whenever the API answers differently from this skill.
Fetch the `.md` URL: it returns the page as Markdown. If the `claude-api` skill is installed, its
`shared/managed-agents-*.md` files carry the same content offline.

All URLs returned HTTP 200 on 2026-10-24.

## Managed Agents

| Topic | URL | Read it for |
|---|---|---|
| Overview | https://platform.claude.com/docs/en/managed-agents/overview.md | how agents, environments, sessions and vaults fit together |
| Quickstart | https://platform.claude.com/docs/en/managed-agents/quickstart.md | the shortest agent → environment → session → stream path |
| Onboarding | https://platform.claude.com/docs/en/managed-agents/onboarding.md | account and region prerequisites |
| Agent setup | https://platform.claude.com/docs/en/managed-agents/agent-setup.md | agent fields, versions, update, archive |
| Tools | https://platform.claude.com/docs/en/managed-agents/tools.md | `agent_toolset_20260401`, per-tool `configs`, web tool domain lists, custom tools |
| Permission policies | https://platform.claude.com/docs/en/managed-agents/permission-policies.md | `always_allow` / `always_ask` / `auto`, the three `auto` outcomes, answering `user.tool_confirmation` |
| MCP connector | https://platform.claude.com/docs/en/managed-agents/mcp-connector.md | `mcp_servers`, `mcp_toolset`, how a vault credential reaches a server |
| Skills | https://platform.claude.com/docs/en/managed-agents/skills.md | Anthropic and custom skills on an agent |
| Multi-agent | https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration.md | `multiagent`, `predefined_agents`, dynamic workflows |
| Environments | https://platform.claude.com/docs/en/managed-agents/environments.md | `cloud` config, `networking`, `allowed_hosts`, package managers |
| Cloud sandboxes | https://platform.claude.com/docs/en/managed-agents/cloud-sandboxes-reference.md | what the container has: runtime, storage, network knobs |
| Self-hosted sandboxes | https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes.md | running the tools on the person's own infrastructure |
| Sessions | https://platform.claude.com/docs/en/managed-agents/sessions.md | lifecycle, idle and terminated, `stop_reason`, budgets, resume |
| Events and streaming | https://platform.claude.com/docs/en/managed-agents/events-and-streaming.md | event types, stream-first ordering, reconnect |
| Define outcomes | https://platform.claude.com/docs/en/managed-agents/define-outcomes.md | `user.define_outcome`, rubrics, `max_iterations`, grader results |
| Files | https://platform.claude.com/docs/en/managed-agents/files.md | uploads, mount paths, `/mnt/session/outputs/`, listing outputs |
| GitHub | https://platform.claude.com/docs/en/managed-agents/github.md | `github_repository` mounts, checkout, token rotation |
| Vaults | https://platform.claude.com/docs/en/managed-agents/vaults.md | credential types, `mcp_oauth` refresh block (`token_endpoint_auth`: `none`, `client_secret_basic`, `client_secret_post`), rotation |
| Memory | https://platform.claude.com/docs/en/managed-agents/memory.md | memory stores, mount path, access modes |
| Scheduled deployments | https://platform.claude.com/docs/en/managed-agents/scheduled-deployments.md | cron and time zone, pause, run now, `deployment_runs` and their `session_id` |
| Webhooks | https://platform.claude.com/docs/en/managed-agents/webhooks.md | `session.status_idled`, `deployment_run.*` events, signature check |
| Observability | https://platform.claude.com/docs/en/managed-agents/session-observability.md | reading a session in the Console, usage and cost |
| Secure deployment | https://platform.claude.com/docs/en/managed-agents/secure-deployment.md | the security checklist before going live |
| Migration | https://platform.claude.com/docs/en/managed-agents/migration.md | older preview shapes and how to move off them |

## CLI, files, skills, models, cost

| Topic | URL | Read it for |
|---|---|---|
| `ant` CLI | https://platform.claude.com/docs/en/cli-sdks-libraries/cli/quickstart.md | install, `ant auth login`, profiles, command shape |
| `ant apply` | https://platform.claude.com/docs/en/cli-sdks-libraries/cli/apply.md | file kinds, path references, `claude-lock.json`, `--dry-run`, `--yes`, CI |
| `ant beta:sessions connect` | https://platform.claude.com/docs/en/cli-sdks-libraries/cli/sessions-connect.md | watching a live session from the terminal and answering paused calls |
| Files API | https://platform.claude.com/docs/en/build-with-claude/files.md | uploading inputs |
| Skills guide | https://platform.claude.com/docs/en/build-with-claude/skills-guide.md | writing and uploading a custom skill |
| Models | https://platform.claude.com/docs/en/models/overview.md | current model IDs and prices |
| Pricing | https://platform.claude.com/docs/en/about-claude/pricing.md | Managed Agents: tokens, USD 0.08 per session-hour running, web search |
| Effort | https://platform.claude.com/docs/en/build-with-claude/effort.md | choosing `effort` per agent |
| Usage and cost API | https://platform.claude.com/docs/en/manage-claude/usage-cost-api.md | cost reports for a watchdog agent (needs an organization) |

## Prompting, tools, skills

| Topic | URL | Read it for |
|---|---|---|
| Prompting best practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md | calm wording, reasons behind rules, scope, long-horizon state |
| Prompting Opus 5.5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5.md | effort default, progress reports, early stops on unattended runs |
| Prompting Sonnet 5.5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5.md | effort levels, verification, scope creep, date and search |
| Prompting Haiku 5.5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5.md | worker prompts, early stops, rules that hold in chat |
| Define tools | https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools.md | custom tool names, descriptions, schemas |
| Agent Skills overview | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.md | skill structure and the security review before attaching one |
| Writing tools for agents | https://www.anthropic.com/engineering/writing-tools-for-agents | fewer, bigger tools; high-signal results; fixable errors |
| Context engineering | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | prompt altitude, minimal prompts, state in files |
| Evals for agents | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | rubric criteria that grade consistently |

## Outside the platform docs

| Topic | URL | Read it for |
|---|---|---|
| MCP Registry | https://registry.modelcontextprotocol.io/v0/servers?search=NAME | finding a remote MCP server and its auth headers |
| Knowledge-work plugins | https://github.com/anthropics/knowledge-work-plugins | business skills by function and their remote MCP URLs (`*/.mcp.json`) |
| skills.sh search | https://skills.sh/api/search?q=WORDS | finding published skills (JSON) |
| One loop or subagents | https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop | when a worker agent earns its cost |
| Python SDK | https://github.com/anthropics/anthropic-sdk-python | exact `client.beta.sessions` / `deployments` signatures for the person's app |
| TypeScript SDK | https://github.com/anthropics/anthropic-sdk-typescript | the same, for Node apps and webhooks |
