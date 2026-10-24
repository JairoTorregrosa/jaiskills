# deployments.md — layout, triggers, schedules, going live, operating

## Layout

One folder per agent, one concern per file, so the person reads each layer in their editor.
`ant apply` reads only `agent.md` (frontmatter = config, body = prompt) and `deployment-*.yaml`;
`scripts/ensamblar.py` builds both from the parts. Its frontmatter `system: "@file"` trick does not
work in `ant apply` (checked 2026-10-24), so the build step is required.

| File | Holds | Read by |
|---|---|---|
| `README.md` | what it does, how it starts, file table, IDs, measured cost | the person |
| `model.yaml` | `name`, `description`, `model: {id, effort}` | ensamblar |
| `system_prompt.md` | the system prompt | ensamblar |
| `tools.yaml` | `tools:` toolset entry and custom tools | ensamblar |
| `mcp.yaml` | `mcp_servers:` and `toolsets:` (mcp_toolset allowlists) | ensamblar |
| `skills.yaml` | `skills:` | ensamblar |
| `subagents.yaml` | `multiagent:` | ensamblar |
| `environment.yaml` | `config: {type, networking}` | `ant apply` |
| `vault.yaml` | `type: vault`, `display_name` | `ant apply` |
| `credentials.md` | which credential, which permissions, the load command | the person |
| `memory_store-<x>.yaml` | `name`, `description` | `ant apply` |
| `memory/` | the store's starting files | you, with `ant beta:memory-stores:memories create` |
| `files.yaml`, `files/` | `files: [{path, mount_path, file_id}]` and the files | ensamblar (adds mounts) |
| `schedule.yaml` | `name`, `deployment_file`, `schedule`, `budget`, `vault_ids`, `resources`, `max_iterations` | ensamblar |
| `kickoff.md` | the text that starts each scheduled run | ensamblar |
| `rubric.md` | present → the kickoff is `user.define_outcome` with this rubric | ensamblar |
| `trigger/` | GitHub Action or webhook that creates the Session for events | the person |
| `tests/<case>.json` | test specs for `scripts/probar.py` | probar |
| `agent.md`, `deployment-*.yaml` | generated; a header says so | `ant apply` |

`ant apply` recognizes a file as a resource by its name (`agent*`, `environment*`,
`memory_store*`, `deployment*`), by a top-level `type:`, or by a directory with `SKILL.md`. The
other parts are invisible to it. Name the files on the command line; never pass `.`.

Seed a memory store: `ant beta:memory-stores:memories create --memory-store-id <memstore_...> --path /topics.md --content "$(cat agents/<name>/memory/topics.md)"`.
Upload an input: `ant files upload --file agents/<name>/files/<file>`, then put the ID in `files.yaml`.

## Three triggers

| Trigger | What creates the Session | Where it lives |
|---|---|---|
| Schedule | a Deployment | `schedule.yaml` + `kickoff.md` (+ `rubric.md`) |
| Event | the other system: a GitHub Action with `curl` to `POST /v1/sessions`, or a webhook in the person's app with the SDK | `trigger/` |
| Person | the person's app or the Console | their app |

External users never talk to the agent directly: the person's app or trigger creates the Session
and decides what goes into the kickoff. Treat that text as untrusted in the prompt.

## Schedule facts (verified 2026-10-24)

- `schedule: {type: cron, expression: "30 7 * * 1-5", timezone: America/Bogota}`. The pause and
  run responses show `schedule.upcoming_runs_at`.
- `budget.max_list_cost.amount` is in cents, per run.
- A Deployment pins the Agent version. When `ant apply` manages the Deployment file, applying
  `agent.md` re-pins it in the same run. A Deployment created any other way must be moved by hand:
  `ant beta:deployments update --deployment-id <id> --agent '{type: agent, id: <agent_id>, version: <N>}'`.
- `ant beta:deployments pause|unpause|run --deployment-id <id>`. `run` works while paused.
- A scheduled Session has nobody streaming it. A call that pauses for approval (`ask`) and a
  custom tool nobody answers both wait forever. Design for no pauses: reads `always_allow`, writes
  only to the agent's own space, and the human gate is the artifact it leaves (a draft, a file, a
  tab it owns). A `session.status_idled` webhook that answers by rule is the other way out.
- `vault_ids: [./vault.yaml]` and `resources: [{path: ./memory_store-<x>.yaml, access: read_only}]`
  are paths `ant apply` resolves in the same run (`--dry-run -v` shows `vault_ids: (known after
  apply)`). One apply creates the vault, the store and the Deployment. [dry run, 2026-10-24]
- Uploaded files are fixed: every scheduled run mounts the same `file_id`s. Changing inputs come
  through a connector (Drive, Gmail) or a trigger that uploads and mounts the new files.
- Same job for N entities (12 clients, 80 contractors): one Deployment, the entity list in memory,
  one note file per entity as it works; not one Deployment per entity.
- Inputs that arrive late: run over a window (`0 6 2-6 * *`), keep in memory what is done this
  period, process only what is new, and list what is still missing instead of guessing.

## Go live (only when the person says so)

1. Remove "Dry run" from `kickoff.md`, re-run `ensamblar.py`, `ant apply` the deployment file.
2. `ant beta:deployments unpause --deployment-id <id>`, or install `trigger/` in the source repo.
3. Tell them the first real run's date from `upcoming_runs_at`.

## Operate

- Latest runs: `ant beta:deployment-runs list --deployment-id <id> --format json` (each run has
  its `session_id`), then `scripts/inspeccionar.py <session_id>`.
- Cost: `ant beta:sessions retrieve --session-id <id> --format json | jq '.usage.list_cost'` (cents).
- Change anything: edit the part, `ensamblar.py`, `ant apply` the two generated files.
- After the first week, tune `rubric.md` with what the grader rejected wrongly or let through.

## Sources

- Scheduled deployments: https://platform.claude.com/docs/en/managed-agents/scheduled-deployments.md
- `ant apply`: https://platform.claude.com/docs/en/cli-sdks-libraries/cli/apply.md
- Webhooks: https://platform.claude.com/docs/en/managed-agents/webhooks.md
- Memory: https://platform.claude.com/docs/en/managed-agents/memory.md
- Files: https://platform.claude.com/docs/en/managed-agents/files.md
