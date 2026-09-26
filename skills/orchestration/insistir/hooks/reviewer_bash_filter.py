#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""PreToolUse hook: Whitelist read-only Bash commands for insistir reviewers.

Wired in the plugin's hooks/hooks.json (agent-frontmatter hooks are not
supported for plugin-shipped agents). Fires on every Bash call of every session
with the plugin installed, but exits 0 immediately unless the calling agent is
the insistir reviewer: agent_type contains "insistir-reviewer", which covers
"jaiskills:insistir-reviewer" and "plugin:jaiskills:insistir-reviewer".
Unparseable input blocks only if the raw payload mentions insistir-reviewer.

Only allows predefined verification commands plus any prefixes loaded from
allowed_commands.txt in every active run's state dir, and blocks flags that
make a whitelisted tool write (autofix, formatter write, git branch mutation).
Blocks everything else.

The lead seeds ~/.claude/insistir-state/<session id>/allowed_commands.txt from
the plan's validation command prefixes. Teammates may run under their own
session id, so every state dir is read (glob), not just the caller's.

Exit codes (per Claude Code hooks spec):
  0 = allow the tool call
  2 = block the tool call, feed stderr back to model
"""
import glob
import json
import re
import shlex
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

# Whole-token flags that make a whitelisted tool write files: linter autofix
# (eslint/ruff/clippy --fix), formatter write (prettier --write), cargo's
# dirty-tree overrides.
WRITE_FLAGS = re.compile(r"^(--fix(=.*)?|--fix-only|--write(=.*)?|--allow-dirty|--allow-staged|--allow-no-vcs)$")
# "-w" writes in place for formatters (gofmt -w, prettier -w) but means
# "ignore whitespace" for git diff/log/show, so it is blocked outside git only.
# git branch: delete, rename, copy, force, re-point upstream, edit description.
GIT_BRANCH_LONG = {
    "--delete", "--move", "--copy", "--force",
    "--set-upstream-to", "--unset-upstream", "--edit-description",
}
GIT_BRANCH_SHORT = set("dDmMcCfu")

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


def writes_files(tokens: list[str]) -> bool:
    """True if the tokens carry a flag that makes a whitelisted tool write."""
    if any(WRITE_FLAGS.match(t) for t in tokens):
        return True
    if tokens[0] != "git":
        return "-w" in tokens
    if tokens[1:2] == ["branch"]:
        for t in tokens[2:]:
            if t.startswith("--"):
                if t.split("=", 1)[0] in GIT_BRANCH_LONG:
                    return True
            elif t.startswith("-") and GIT_BRANCH_SHORT & set(t[1:]):
                return True
    return False


def is_allowed(command: str, extra_prefixes: list[str]) -> bool:
    """Check if a command matches the whitelist."""
    cmd = command.strip()

    # Block shell metacharacters — prevents chaining (cmd1 && cmd2, cmd | rm, etc.)
    if DANGEROUS_CHARS.search(cmd):
        return False

    all_prefixes = BUILTIN_PREFIXES + list(RUN_PREFIXES) + extra_prefixes
    if not any(cmd.startswith(prefix) for prefix in all_prefixes):
        return False

    try:
        tokens = shlex.split(cmd)
    except ValueError:
        return False  # unbalanced quotes: bash would not run it as intended either
    if not tokens or writes_files(tokens):
        return False

    # Block file-writing / config-loading flags on git and config-loading tools
    if cmd.startswith("git ") and "--output" in cmd:
        return False
    loads_config = any(cmd.startswith(t) for t in CONFIG_LOADING_TOOLS)
    return not (loads_config and UNSAFE_FLAGS.search(cmd))


REVIEWER_MARK = "insistir-reviewer"


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except ValueError:
        data = None
    if not isinstance(data, dict):
        if REVIEWER_MARK in raw:
            print("Reviewer bash filter: failed to parse input JSON.", file=sys.stderr)
            sys.exit(2)
        sys.exit(0)

    # Only enforce for the insistir reviewer agent. agent_type is present
    # when the hook fires inside a subagent or teammate launched from an agent
    # definition ("jaiskills:insistir-reviewer", "plugin:jaiskills:insistir-reviewer").
    agent_type = str(data.get("agent_type") or "")
    if REVIEWER_MARK not in agent_type:
        sys.exit(0)

    tool_input = data.get("tool_input")
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    if not isinstance(command, str):
        command = ""

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
    except Exception as e:  # noqa: BLE001 - fail closed: an error must not let a reviewer command through
        print(f"Reviewer bash filter: unexpected error: {e}", file=sys.stderr)
        sys.exit(2)
