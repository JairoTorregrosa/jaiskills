#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""TaskCompleted hook: an insistir plan task needs review approval before completion.

Wired in the plugin's hooks/hooks.json, so it fires for every TaskCompleted event
of every session that has the plugin installed. It is a no-op (exit 0) unless ALL
of these hold:

  1. ~/.claude/insistir-state/<session_id>/ exists. The insistir lead creates it
     for its own session (SKILL.md: ${CLAUDE_SESSION_ID}) before creating tasks
     and removes it at cleanup, so it marks an active run in THIS session;
  2. the event carries a task_id (implicit end-of-turn events are allowed);
  3. the subject matches the plan task convention "T<N>: ..." (worker-internal
     subtasks pass through, which prevents deadlocks).

When all hold, completion is allowed only if an approval marker exists in the
state dir, under any of: "<key>.approved" (e.g. "T3.approved", the form the lead
writes), "<sanitized subject>.approved" or "<sanitized task_id>.approved".
Sanitizing maps every char outside [A-Za-z0-9_-] to "_".

Input (Claude Code TaskCompleted): session_id, task_id, task_subject,
task_description, teammate_name, team_name (deprecated, "session-<8 hex>", unused).
Camel-case and nested "task" shapes are probed for the task fields.

Known limitation: the marker is trust-based, not tamper-proof; any agent with
Bash/Write could create it. Defense in depth: workers have TaskUpdate/TaskCreate
in disallowedTools and reviewers lack TaskUpdate, so only the lead completes
tasks. The marker stops the LEAD from completing a plan task before a verdict.

Exit codes (Claude Code hooks spec):
  0 = allow completion
  2 = block completion, stderr is fed back to the model
Error policy: once the event is known to be a plan task of an active insistir
run, any internal error blocks (exit 2): the gate never fails open inside a run.
Outside that scope, errors exit 0 so unrelated sessions are never blocked.
Unparseable input blocks only if it names a session that has an active state dir.
"""

import json
import re
import sys
from pathlib import Path

STATE_ROOT = Path.home() / ".claude" / "insistir-state"
# Plan tasks: "T1: ...", "T2 ...", "T1.2: ..." (insistir.py accepts dotted ids)
PLAN_TASK_PATTERN = re.compile(r"^(T\d+(?:\.\d+)*)[:\s]")

# Flipped to True once the event is known to be gated; decides the error policy.
_gating = False


def sanitize_id(raw_id: str) -> str:
    """Replace unsafe characters to prevent path traversal."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", raw_id)


def pick(data: dict, *keys: str) -> str:
    """First non-empty value for any key, across flat, nested-task and tool_input shapes."""
    sources = [data]
    for nested in ("task", "tool_input"):
        value = data.get(nested)
        if isinstance(value, dict):
            sources.append(value)
    for source in sources:
        for key in keys:
            value = source.get(key)
            if value:
                return str(value)
    return ""


def raw_names_active_run(raw: str) -> bool:
    """For unparseable input: does it mention a session with an active state dir?"""
    try:
        return any(d.is_dir() and d.name in raw for d in STATE_ROOT.iterdir())
    except OSError:
        return False


def main() -> int:
    global _gating
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except ValueError:
        data = None
    if not isinstance(data, dict):
        if raw_names_active_run(raw):
            print("TaskCompleted hook: unparseable input during an insistir run; blocking.", file=sys.stderr)
            return 2
        return 0

    session_id = sanitize_id(str(data.get("session_id") or ""))
    if not session_id:
        return 0
    state_dir = STATE_ROOT / session_id
    if not state_dir.is_dir():
        return 0  # no insistir run in this session

    task_id = pick(data, "task_id", "taskId", "id")
    task_subject = pick(data, "task_subject", "taskSubject", "subject") or task_id
    if not task_id:
        return 0  # implicit completion at teammate turn end
    match = PLAN_TASK_PATTERN.match(task_subject)
    if not match:
        return 0  # worker-internal subtask

    _gating = True
    key = sanitize_id(match.group(1))
    names = {f"{key}.approved", f"{sanitize_id(task_subject)}.approved", f"{sanitize_id(task_id)}.approved"}
    if any((state_dir / name).is_file() for name in names):
        return 0

    print(
        f"Plan task '{task_subject}' ({task_id}) cannot be completed: no review approval marker.\n"
        f"Write it only after the review loop returns APPROVED:\n"
        f'echo "APPROVED $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "{state_dir / (key + ".approved")}"',
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001 - hook must never crash with an undefined exit code
        if _gating:
            print(f"TaskCompleted hook: unexpected error: {e}", file=sys.stderr)
            sys.exit(2)
        sys.exit(0)
