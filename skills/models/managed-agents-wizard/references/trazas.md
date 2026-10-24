# trazas.md — read a Session's trace with the person, event by event

You are about to walk the person through what their agent did in one Session. The Console
(platform.claude.com → Sessions → the session) shows the same events as a timeline; you show them
in the terminal with `scripts/trazas.py` and explain each part, so the person learns to read the
Console alone. Do this after every test run, not only when something failed.

## Facts already verified (2026-10-24, two runs of a demo agent)

- A Session's events, in order: `session.status_running`, `session.thread_status_running`, the
  kickoff (`user.message` or `user.define_outcome`), then for each step a `span.model_request_start`
  / `span.model_request_end` pair around the agent's `agent.thinking`, `agent.tool_use` (or
  `agent.mcp_tool_use`, `agent.custom_tool_use`) and `agent.message`; each tool call is followed by
  its `agent.tool_result`; at the end `session.thread_status_idle`, `session.usage` and
  `session.status_idle` with `stop_reason`. [events.list]
- `span.model_request_end.model_usage` has `input_tokens`, `cache_creation_input_tokens`,
  `cache_read_input_tokens` and `output_tokens` for that one model request. [events.list]
- `agent.tool_use` carries `evaluated_permission` (`allow`, `ask`, `deny`) and `evaluation` (the
  policy that decided: `always_allow`, `auto`, `always_ask`). [events.list]
- `agent.thinking` carries no text: it only marks that the model reasoned. [events.list]
- The session has `stats.duration_seconds` (open time, idle included) and `stats.active_seconds`
  (running time, the part billed at USD 0.08 per hour); `usage.list_cost.amount` is in cents.
  [sessions.retrieve]
- The prompt cache carries across Sessions that start within its lifetime: the second run of the
  demo, already on Agent v2 with one prompt line changed, read 3,304 tokens (the unchanged prefix)
  from cache on its first model request and cost USD 0.01 instead of 0.02. [two runs, 2026-10-24]

## Do this

1. Give the Console URL and ask the person to open it next to the terminal.
2. Run `uv run --script scripts/trazas.py <session_id>` (the first time, with explanations; later,
   `--breve`).
3. Walk the header with them:
   - **Cost** against the cap, and its parts: tokens, web searches, running time. Billed time is
     "trabajando", not "abierta".
   - **Tokens**: the cache read is what makes a repeated prompt cheap. A large "caché nueva" on
     every request means the context keeps changing.
4. Walk the timeline in blocks: each model request, then what it decided (a tool call or a
   message), then what came back. For each block, name the ficha row that made it possible:
   - a tool call → the tool or MCP tool enabled in `tools.yaml` / `mcp.yaml`, and the permission
     in brackets → the policy you chose;
   - the order of calls → the Procedure in `system_prompt.md`;
   - the stop → `stop_reason` (end_turn = done; requires_action = waiting for an answer;
     budget_reached = the cap).
5. Compare the trace with the design: which procedure step each block carried out, which step it
   skipped or merged, which tool it never used (a candidate to turn off), what it did that the
   prompt did not ask for.
6. Read the output file together and check it against the Goal.
7. Ask with `AskUserQuestion` what to change next, with the options the trace suggests (one change
   per run: a prompt line, a tool off, a lower effort, a smaller cap). Name the file each option
   edits. After the change: `ensamblar.py`, `ant apply` (a new Agent version), run again, and run
   `trazas.py` on both sessions to compare cost, model requests and result.

## Rules

- Explain with the person's own run, never with a generic example.
- Never paste a full tool result that may hold personal data or secrets; the script already cuts
  each one to a short preview.
- A trace that looks fine but produced a wrong output is a prompt or rubric problem: change the
  file, not the explanation.
