# debugging.md — symptom → cause → fix

You are about to find why a Session did not do what the person expected. Start with the facts,
not a theory: run `uv run --script scripts/inspeccionar.py <session_id>` (read-only, free). It
prints status, last stop reason, cost, outcome verdicts, calls still waiting for an answer, tool
errors, denied calls, session errors, the last message and the output files. Then find the line
below. Fix the cause in its own file, re-run `ensamblar.py`, re-apply, re-test. One change per run.

## The session did not finish

| Symptom (inspeccionar) | Cause | Fix |
|---|---|---|
| `WAITING FOR YOU: agent.tool_use …` / `last_stop=requires_action` | a call paused for approval (`always_ask`, or `auto` could not judge it) and nobody answered | answer it: `ant beta:sessions:events send --session-id S --event '{type: user.tool_confirmation, tool_use_id: <id>, result: allow}'` (or `deny`). For scheduled runs, change the policy in `tools.yaml`/`mcp.yaml` |
| `WAITING FOR YOU: agent.custom_tool_use` | your app did not send `user.custom_tool_result` | answer with the id shown; fix the app's event loop |
| `last_stop=budget_reached` | the run hit `max_list_cost` | raise it and the run resumes by itself: `ant beta:sessions update --session-id S --budget '{type: limit, max_list_cost: {amount: "<cents>", currency: USD}}'`; then lower the work or raise the cap in `schedule.yaml` |
| `status=running` for a long time, cost rising | real long work, or a loop | open the Console URL; look at the last tool calls; add a hard limit to the prompt ("Stop after 30 minutes…") |
| `session.error` about a tool config | a web tool domain list or MCP setting became invalid | fix the agent, apply, start a new session |

## Creation fails

| Message | Cause | Fix |
|---|---|---|
| 400 naming a blocked host | the agent declares an MCP server and `limited` networking blocks it | `allow_mcp_servers: true` in `environment.yaml` |
| "Can't access this organization" | the `ant` profile points at another org | `ant auth login --profile <name>` |
| `ant apply`: "mapping value is not allowed in this context" | a YAML value with `: ` inside | quote it, or move the text to `kickoff.md` |
| `ant apply`: "file name too long" / one huge path | a multi-line file list passed as one word | `F=(…); ant apply "${F[@]}"` |
| `ant apply` wants to create things you did not write | you passed `.` or a directory | name the files; never `--force`, never `--prune` |
| `ensamblar.py`: "toolset for unknown server" | `mcp.yaml` toolset name ≠ server name | make `mcp_server_name` match |

## It finished but the result is wrong

| Symptom | Cause | Fix |
|---|---|---|
| `tool error: … 401/403` on an MCP tool | wrong token, or the token lacks a permission | rotate the credential (`credenciales.md`); add the permission. Fine-grained PATs have no Checks |
| `denied: <write tool>` | `auto` judged the write risky and denied it | if the write is essential and unattended, use a narrow `always_allow` on that one tool with a clear rule in the prompt; else accept that a person does it |
| `tool error: … url_not_allowed` | `web_fetch` outside `allowed_domains`, or the host is not in `allowed_hosts` | add the host to both lists |
| `curl` / `pip` fails in the sandbox | host not in `allowed_hosts` / `allow_package_managers` off | open only that host or package managers |
| the agent says a tool "is not available" | the tool is not in the allowlist (`default_config: {enabled: false}`) | add a `configs` entry |
| outcome `needs_revision` until `max_iterations` on good work | the rubric is stricter than you meant (e.g. "every fact links" when ages cannot link) | rewrite `rubric.md`; the agent is fine |
| outcome satisfied on bad work | the rubric does not check what matters | add a checkable criterion for the failure you saw |
| no output files | written outside `/mnt/session/outputs/`, or listed too early | the prompt names the path; wait a few seconds after idle (probar.py retries) |
| inputs you mounted appear as "outputs" | `files.list` also returns mounted copies | filter by mount names (probar.py does) |
| memory empty next run | wrote to `/mnt/memory/` instead of `/mnt/memory/<store>/`, or the store was mounted read-only | fix the path in the prompt; `access: read_write` |
| a fact in the output that no tool returned | the prompt allows filling gaps | add "Use only facts from the tools. Write 'not stated'." and a rubric line for it |
| Deployment runs the old prompt | it is pinned to the old Agent version | `ant apply` the deployment file too, or `ant beta:deployments update --agent …` |

## When you are stuck

After 3 runs on the same symptom with no progress, stop. Show the person the inspeccionar output,
what you changed each time, and the next hypothesis. Offer an outside read: call the Skill tool
with `second-opinion` on the prompt and the event trace.

## Sources

- Sessions: https://platform.claude.com/docs/en/managed-agents/sessions.md
- Events and streaming: https://platform.claude.com/docs/en/managed-agents/events-and-streaming.md
- Permission policies: https://platform.claude.com/docs/en/managed-agents/permission-policies.md
- Define outcomes: https://platform.claude.com/docs/en/managed-agents/define-outcomes.md
- Observability: https://platform.claude.com/docs/en/managed-agents/session-observability.md
