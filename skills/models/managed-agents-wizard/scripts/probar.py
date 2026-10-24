#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["anthropic>=0.80"]
# ///
"""Run one test session of a Managed Agents agent and save what it produced.

Usage (from the project root, next to claude-lock.json):
  uv run --script scripts/probar.py agents/<name>/tests/<case>.json

The spec (JSON):
  {"agent": "<dir under agents/>", "title": "...", "budget_usd": 5,
   "vault_ids": ["vlt_..."],
   "resources": ["./agents/x/memory_store-y.yaml" (mounted read_only), {"path": "./agents/x/memory_store-y.yaml", "access": "read_write"}, {"type": "file", "file_id": "file_...", "mount_path": "..."}],
   "fixtures": {"<custom tool>": "text" | {"by": "<input field>", "values": {...}, "default": "..."}},
   "dry_run": true,              # appends "Dry run." to agents/<agent>/kickoff.md (the default kickoff)
   "events": [<optional: replaces the kickoff; user.message or user.define_outcome>]}

A string resource is a path in claude-lock.json (memory stores). Paused calls (evaluated_permission
"ask") are denied, because nobody watches a test. Custom tools get their answer from "fixtures".
Outputs go to tests/out/<agent>/<session_id>/: the files from /mnt/session/outputs/ (not the
mounted inputs), transcript.md and result.json. Exit code 1 if the session did not end cleanly.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import anthropic

BETA = "managed-agents-2026-04-01"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    lock_path = Path("claude-lock.json")
    if not lock_path.exists():
        print("claude-lock.json not found: run this from the project root, after ant apply", file=sys.stderr)
        return 2
    lock = json.loads(lock_path.read_text(encoding="utf-8"))["resources"]

    def id_of(path: str) -> str:
        entry = lock.get(path)
        if not entry:
            raise SystemExit(f"{path} is not in claude-lock.json")
        return entry["id"]

    resources = []
    for r in spec.get("resources", []):
        if isinstance(r, str):
            # tests never write to a production store unless the spec says so
            resources.append({"type": "memory_store", "memory_store_id": id_of(r), "access": "read_only"})
        elif r.get("path"):
            resources.append({"type": "memory_store", "memory_store_id": id_of(r["path"]),
                              "access": r.get("access", "read_only")})
        else:
            resources.append(r)
    mounted = {Path(r["mount_path"]).name for r in resources if r.get("type") == "file" and r.get("mount_path")}
    fixtures = spec.get("fixtures", {})
    budget_cents = str(int(float(spec.get("budget_usd", 5)) * 100))

    agent_dir = spec["agent"]
    events = spec.get("events")
    if not events:
        # same kickoff as the Deployment: agents/<agent>/kickoff.md, plus "Dry run." when asked
        kickoff = (Path("agents") / agent_dir / "kickoff.md").read_text(encoding="utf-8").strip()
        if spec.get("dry_run"):
            kickoff += "\nDry run."
        events = [{"type": "user.message", "content": [{"type": "text", "text": kickoff}]}]
    client = anthropic.Anthropic()
    session = client.beta.sessions.create(
        agent=id_of(f"./agents/{agent_dir}/agent.md"),
        environment_id=id_of(f"./agents/{agent_dir}/environment.yaml"),
        title=spec.get("title", f"test {agent_dir}"),
        vault_ids=spec.get("vault_ids", []),
        resources=resources,
        budget={"type": "limit", "max_list_cost": {"amount": budget_cents, "currency": "USD"}},
    )
    out = Path("tests/out") / agent_dir / session.id
    out.mkdir(parents=True, exist_ok=True)
    print(f"[{agent_dir}] {session.id}  https://platform.claude.com/workspaces/default/sessions/{session.id}", flush=True)

    log: list[str] = []
    stop = "unknown"
    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(session_id=session.id, events=events)
        for event in stream:
            t = event.type
            if t == "agent.message":
                log.extend(b.text for b in event.content if b.type == "text")
            elif t == "agent.custom_tool_use":
                answer = fixture_answer(fixtures, event.name, event.input or {})
                log.append(f">> {event.name} {json.dumps(event.input, ensure_ascii=False)}")
                client.beta.sessions.events.send(
                    session_id=session.id,
                    events=[{"type": "user.custom_tool_result", "custom_tool_use_id": event.id,
                             "content": [{"type": "text", "text": answer}]}],
                )
            elif t in ("agent.tool_use", "agent.mcp_tool_use") and getattr(event, "evaluated_permission", None) == "ask":
                log.append(f">> denied paused call {event.name}")
                client.beta.sessions.events.send(
                    session_id=session.id,
                    events=[{"type": "user.tool_confirmation", "tool_use_id": event.id, "result": "deny",
                             "deny_message": "Unattended test: no approvals."}],
                )
            elif t == "span.outcome_evaluation_end":
                log.append(f"== outcome iteration {event.iteration}: {event.result} - {event.explanation}")
            elif t == "session.error":
                log.append(f"!! session.error {event.model_dump_json()}")
            elif t == "session.status_terminated":
                stop = "terminated"
                break
            elif t == "session.status_idle" and event.stop_reason.type != "requires_action":
                stop = event.stop_reason.type
                break

    final = client.beta.sessions.retrieve(session_id=session.id)
    files = []
    for _ in range(6):  # outputs are indexed a few seconds after the session goes idle
        files = [f for f in client.beta.files.list(scope_id=session.id, betas=[BETA]).data if f.filename not in mounted]
        if files:
            break
        time.sleep(5)
    for f in files:
        client.beta.files.download(f.id).write_to_file(out / f.filename)
    usage = final.usage.model_dump() if final.usage else {}
    cost = int((usage.get("list_cost") or {}).get("amount") or 0) / 100
    outcomes = [o.model_dump(mode="json") for o in (getattr(final, "outcome_evaluations", None) or [])]
    (out / "transcript.md").write_text("\n\n".join(log), encoding="utf-8")
    (out / "result.json").write_text(json.dumps(
        {"session": session.id, "status": final.status, "stop_reason": stop, "cost_usd": cost,
         "outcomes": outcomes, "files": [f.filename for f in files]}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{agent_dir}] stop={stop} status={final.status} cost=USD {cost:.2f} files={[f.filename for f in files]} -> {out}")
    print(f"[{agent_dir}] trace: uv run --script scripts/trazas.py {session.id}")
    return 0 if stop in ("end_turn", "retries_exhausted") else 1


def fixture_answer(fixtures: dict, name: str, tool_input: dict) -> str:
    fx = fixtures.get(name)
    if fx is None:
        return "Not available in this test."
    if isinstance(fx, dict) and "by" in fx:
        value = fx["values"].get(str(tool_input.get(fx["by"])), fx.get("default", "not found"))
        return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return fx if isinstance(fx, str) else json.dumps(fx, ensure_ascii=False)


if __name__ == "__main__":
    sys.exit(main())
