#!/usr/bin/env python3
"""TaskCompleted hook: Plan tasks need review approval before completion.

Only gates tasks whose subject matches the plan task naming convention
(e.g., "T1: Research", "T2: HTML Development"). Worker-internal subtasks
(created by workers to organize their own work) are allowed through
unconditionally to prevent deadlocks.

Known limitation: the approval marker is trust-based, not tamper-proof — any
agent with Bash/Write access could create it. Defense in depth comes from the
worker agent's instructions plus its disallowedTools (TaskUpdate/TaskCreate),
which prevent workers from completing tasks at all. The marker gates the LEAD
from marking tasks complete before a review verdict arrives.

Exit codes (per Claude Code hooks spec):
  0 = allow completion
  2 = block completion, feed stderr back to model
  1 = non-blocking error (gate fails open — avoided by catching all exceptions)
"""
import json
import re
import sys
from pathlib import Path

# Pattern for plan tasks: "T1: ...", "T2: ...", etc.
PLAN_TASK_PATTERN = re.compile(r"^T\d+[:\s]")


def sanitize_id(raw_id: str) -> str:
    """Replace unsafe characters to prevent path traversal."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", raw_id)


def is_plan_task(subject: str) -> bool:
    """Check if a task subject matches the plan task naming convention."""
    return bool(PLAN_TASK_PATTERN.match(subject))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("TaskCompleted hook: failed to parse input JSON.", file=sys.stderr)
        sys.exit(2)

    # The TaskCompleted input schema does not document task fields, and field
    # names have varied across Claude Code versions. Probe every known shape
    # (flat snake_case, flat camelCase, nested task object, tool_input) so the
    # gate activates whenever the information is present under any of them.
    task_obj = data.get("task") or {}
    tool_input = data.get("tool_input") or {}

    def pick(*keys):
        for source in (data, task_obj, tool_input):
            for key in keys:
                value = source.get(key)
                if value:
                    return str(value)
        return ""

    team_name = pick("team_name", "teamName", "team")
    task_id = pick("task_id", "taskId", "id")
    task_subject = pick("task_subject", "taskSubject", "subject", "description") or task_id

    # Only activate for insistir sessions
    if not team_name.startswith("insistir-"):
        sys.exit(0)

    # No task_id means implicit TaskCompleted event (teammate turn end).
    # Allow these — the gate only enforces explicit task completion.
    if not task_id:
        sys.exit(0)

    # Only gate plan tasks (T1, T2, T3, etc.). Worker-internal subtasks
    # are allowed through to prevent deadlocks where workers create their
    # own subtasks that then get blocked by missing approval markers.
    if not is_plan_task(task_subject):
        sys.exit(0)

    safe_team = sanitize_id(team_name)
    safe_task = sanitize_id(task_subject)

    state_dir = Path.home() / ".claude" / "insistir-state" / safe_team
    marker = state_dir / f"{safe_task}.approved"

    if marker.exists():
        sys.exit(0)

    print(
        f"Plan task '{task_subject}' ({task_id}) cannot be completed — "
        f"no review approval found.\n"
        f"The lead must write the approval marker after receiving "
        f"APPROVED verdict from the reviewer.\n"
        f"Run: mkdir -p {state_dir} && "
        f"echo APPROVED > {state_dir}/{safe_task}.approved",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"TaskCompleted hook: unexpected error: {e}", file=sys.stderr)
        sys.exit(2)
