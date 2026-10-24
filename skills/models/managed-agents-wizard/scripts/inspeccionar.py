#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["anthropic>=0.80"]
# ///
"""Diagnose one Managed Agents session: why it stopped, what failed, what it cost.

Usage:
  uv run --script <skill>/scripts/inspeccionar.py <session_id>          # human summary
  uv run --script <skill>/scripts/inspeccionar.py <session_id> --json   # the same, as JSON

Reads the session and its full event list (read-only, costs nothing). Reports: status, last stop
reason, cost and tokens, outcome verdicts, paused calls still waiting (requires_action), tool calls
that returned an error (with the first 300 characters), denied calls, session errors, the last
agent message, and the output files.
"""

from __future__ import annotations

import json
import sys

import anthropic

BETA = "managed-agents-2026-04-01"


def text_of(content) -> str:
    parts = []
    for block in content or []:
        if isinstance(block, dict):
            parts.append(str(block.get("text", "")))
        else:
            parts.append(str(getattr(block, "text", "")))
    return " ".join(p for p in parts if p).strip()


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    sid = args[0]
    client = anthropic.Anthropic()
    s = client.beta.sessions.retrieve(session_id=sid)
    events = list(client.beta.sessions.events.list(session_id=sid))

    uses: dict[str, str] = {}
    errors, denied, session_errors = [], [], []
    last_idle, last_msg = None, ""
    answered: set[str] = set()
    pending = []
    for e in events:
        t = e.type
        if t in ("agent.tool_use", "agent.mcp_tool_use", "agent.custom_tool_use"):
            uses[e.id] = e.name
            if getattr(e, "evaluated_permission", None) == "ask" or t == "agent.custom_tool_use":
                pending.append((e.id, e.name, t))
        elif t in ("user.tool_confirmation",):
            answered.add(e.tool_use_id)
            if e.result == "deny":
                denied.append(uses.get(e.tool_use_id, e.tool_use_id))
        elif t == "user.custom_tool_result":
            answered.add(e.custom_tool_use_id)
        elif t in ("agent.tool_result", "agent.mcp_tool_result"):
            ref = getattr(e, "tool_use_id", None) or getattr(e, "mcp_tool_use_id", None)
            body = text_of(getattr(e, "content", None))
            if "has been denied" in body:
                denied.append(uses.get(ref, "?"))
            elif getattr(e, "is_error", False):
                errors.append({"tool": uses.get(ref, "?"), "error": " ".join(body.split())[:300]})
        elif t == "session.error":
            session_errors.append(e.model_dump(mode="json"))
        elif t == "session.status_idle":
            last_idle = e.stop_reason.type
        elif t == "agent.message":
            last_msg = text_of(e.content) or last_msg

    waiting = [{"id": i, "tool": n, "kind": k} for i, n, k in pending if i not in answered]
    usage = s.usage.model_dump() if s.usage else {}
    files = client.beta.files.list(scope_id=sid, betas=[BETA]).data
    report = {
        "session": sid,
        "console": f"https://platform.claude.com/workspaces/default/sessions/{sid}",
        "status": s.status,
        "last_stop_reason": last_idle,
        "cost_usd": int((usage.get("list_cost") or {}).get("amount") or 0) / 100,
        "tokens": {k: usage.get(k) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens")},
        "outcomes": [{"result": o.result, "explanation": (o.explanation or "")[:400]}
                     for o in (getattr(s, "outcome_evaluations", None) or [])],
        "waiting_for_you": waiting,
        "tool_errors": errors,
        "denied_calls": denied,
        "session_errors": session_errors,
        "last_agent_message": " ".join(last_msg.split())[:800],
        "files": [f.filename for f in files],
        "events": len(events),
    }
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    print(f"{report['console']}\nstatus={report['status']} last_stop={last_idle} cost=USD {report['cost_usd']:.2f} events={len(events)}")
    for o in report["outcomes"]:
        print(f"outcome: {o['result']} - {o['explanation'][:200]}")
    for w in waiting:
        print(f"WAITING FOR YOU: {w['kind']} {w['tool']} ({w['id']}) - answer it or the session never moves")
    for x in errors:
        print(f"tool error: {x['tool']}: {x['error']}")
    for d in denied:
        print(f"denied: {d}")
    for se in session_errors:
        print(f"session.error: {json.dumps(se, ensure_ascii=False)[:300]}")
    print(f"files: {report['files']}")
    print(f"last message: {last_msg[:400]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
