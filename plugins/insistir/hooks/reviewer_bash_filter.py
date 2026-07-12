#!/usr/bin/env python3
"""PreToolUse hook: Whitelist read-only Bash commands for insistir reviewers.

Registered in the plugin's hooks/hooks.json (agent-frontmatter hooks are not
supported for plugin-shipped agents). Fires on every Bash call but exits 0
immediately unless the calling agent is the insistir reviewer (agent_type).

Only allows predefined verification commands plus any prefixes loaded from
per-team allowed_commands.txt files. Blocks everything else.

The lead seeds ~/.claude/insistir-state/<team>/allowed_commands.txt from
the plan's validation command prefixes so reviewers can run them.

Exit codes (per Claude Code hooks spec):
  0 = allow the tool call
  2 = block the tool call, feed stderr back to model
"""
import glob
import json
import re
import sys
from pathlib import Path

# Shell metacharacters that could chain/redirect commands.
# Includes newlines: bash executes each line separately, so "git log\nrm -rf /"
# would otherwise pass both the metacharacter check and the prefix whitelist.
DANGEROUS_CHARS = re.compile(r"[;|&`$><\n\r]")

# Built-in allowed prefixes: git read-only + common verification runners
BUILTIN_PREFIXES = [
    # Git read-only
    "git log",
    "git diff",
    "git show",
    "git rev-parse",
    "git status",
    "git branch",
    # Node/npm — "<pm> run" is scoped to verification scripts only; a bare
    # "<pm> run" prefix would let a malicious package.json script run anything.
    # Other scripts must be whitelisted per-team via allowed_commands.txt.
    "npm test",
    "pnpm test",
    "yarn test",
    "bun test",
    "bun lint",
    "bunx tsc",
    "npx tsc",
    # Python
    "pytest",
    "python -m pytest",
    "ruff check",
    "mypy",
    # Rust
    "cargo test",
    "cargo check",
    "cargo clippy",
    # Go
    "go test",
    "go vet",
    # Make
    "make test",
    "make lint",
    # JS/TS linting
    "eslint",
    "tsc",
]

# Verification script names allowed after "npm|pnpm|yarn|bun run"
RUN_SCRIPTS = ("test", "lint", "typecheck", "check", "build", "quality")
RUN_PREFIXES = tuple(
    f"{pm} run {script}"
    for pm in ("npm", "pnpm", "yarn", "bun")
    for script in RUN_SCRIPTS
)

# Flags that make otherwise read-only tools write files or load arbitrary
# config/plugins (git --output, pytest -c/-p, mypy --config-file, etc.)
UNSAFE_FLAGS = re.compile(r"(^|\s)(--output(=|\s|$)|-c\s|-p\s|--config-file|--rootdir)")
CONFIG_LOADING_TOOLS = ("pytest", "python -m pytest", "mypy")

# Never allow team whitelist entries that start with these — the whitelist is
# for verification runners, not general shell access.
FORBIDDEN_TEAM_PREFIXES = (
    "rm", "curl", "wget", "bash", "sh ", "zsh", "node -e", "python -c",
    "python3 -c", "chmod", "chown", "mv ", "cp ", "dd ", "sudo",
)


def load_team_prefixes() -> list[str]:
    """Load additional allowed prefixes from all team allowed_commands.txt files."""
    prefixes = []
    pattern = str(Path.home() / ".claude" / "insistir-state" / "*" / "allowed_commands.txt")
    for filepath in glob.glob(pattern):
        try:
            with open(filepath) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if any(line.startswith(bad) for bad in FORBIDDEN_TEAM_PREFIXES):
                        continue
                    prefixes.append(line)
        except OSError:
            continue
    return prefixes


def is_allowed(command: str, extra_prefixes: list[str]) -> bool:
    """Check if a command matches the whitelist."""
    cmd = command.strip()

    # Block shell metacharacters — prevents chaining (cmd1 && cmd2, cmd | rm, etc.)
    if DANGEROUS_CHARS.search(cmd):
        return False

    all_prefixes = BUILTIN_PREFIXES + list(RUN_PREFIXES) + extra_prefixes
    if not any(cmd.startswith(prefix) for prefix in all_prefixes):
        return False

    # Block file-writing / config-loading flags on git and config-loading tools
    if cmd.startswith("git ") and "--output" in cmd:
        return False
    if any(cmd.startswith(t) for t in CONFIG_LOADING_TOOLS) and UNSAFE_FLAGS.search(cmd):
        return False

    return True


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("Reviewer bash filter: failed to parse input JSON.", file=sys.stderr)
        sys.exit(2)

    # Only enforce for the insistir reviewer agent. agent_type is present
    # when the hook fires inside a subagent (e.g. "insistir-reviewer" or
    # "insistir:insistir-reviewer").
    agent_type = data.get("agent_type") or ""
    if "insistir-reviewer" not in agent_type:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        print("Reviewer bash filter: empty command blocked.", file=sys.stderr)
        sys.exit(2)

    extra_prefixes = load_team_prefixes()

    if is_allowed(command, extra_prefixes):
        sys.exit(0)

    print(
        f"Blocked: reviewers can only run read-only verification commands.\n"
        f"Attempted: {command}\n"
        f"Allowed: git read-only, common test/lint/typecheck runners, "
        f"and prefixes from ~/.claude/insistir-state/*/allowed_commands.txt",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Reviewer bash filter: unexpected error: {e}", file=sys.stderr)
        sys.exit(2)
