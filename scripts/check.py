#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Lint the catalog: every invariant in AGENTS.md that a machine can check.

Usage:
  scripts/check.py            exit 1 and list every violation
  scripts/check.py --quiet    print violations only

Checks:
  skills      skills/<bucket>/<skill>/SKILL.md, known buckets, frontmatter (name = dir,
              description <= 1024 chars, no version), agents/openai.yaml, invocation in sync
  manifests   plugin.json skills == promoted skills; versions match marketplace.json
  readme      every promoted skill linked to its SKILL.md; no status-bucket skill linked
  wiring      no commands/ directory; hook commands and plugin agents exist
  hygiene     no home-directory paths, no secrets, relative Markdown links resolve
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
USE_BUCKETS = ("creative", "orchestration", "models", "knowledge")
STATUS_BUCKETS = ("in-progress", "deprecated")
SELF = Path(__file__).resolve()

HOME_PATH = re.compile(r"/(?:Users|home)/(?!(?:user|username|you|me|runner|ubuntu|example|shared)/)[a-z][\w.-]*/", re.IGNORECASE)
SECRETS = {
    "OpenAI/Anthropic-style key": re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{24,}"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "Slack token": re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{20,}"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
}
MD_LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^(```|~~~)")

errors: list[str] = []


def err(where: Path | str, msg: str) -> None:
    rel = where.relative_to(ROOT) if isinstance(where, Path) else where
    errors.append(f"{rel}: {msg}")


def frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        err(path, "missing YAML frontmatter")
        return None
    end = text.find("\n---", 4)
    if end < 0:
        err(path, "unterminated frontmatter")
        return None
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as e:
        err(path, f"frontmatter is not valid YAML: {e}")
        return None
    return data if isinstance(data, dict) else {}


def tracked_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    return [ROOT / p for p in out.split("\0") if p and (ROOT / p).is_file()]


def check_skills() -> tuple[list[str], list[str]]:
    promoted, parked = [], []
    for skill_md in sorted(ROOT.glob("skills/**/SKILL.md")):
        rel = skill_md.relative_to(ROOT / "skills").parts
        if len(rel) != 3:
            err(skill_md, "skills live at skills/<bucket>/<skill>/SKILL.md")
            continue
        bucket, name, _ = rel
        skill_dir = skill_md.parent
        path = f"./skills/{bucket}/{name}"
        if bucket in USE_BUCKETS:
            promoted.append(path)
        elif bucket in STATUS_BUCKETS:
            parked.append(path)
        else:
            err(skill_md, f"unknown bucket '{bucket}' (use {', '.join(USE_BUCKETS + STATUS_BUCKETS)})")

        fm = frontmatter(skill_md)
        if fm is None:
            continue
        if fm.get("name") != name:
            err(skill_md, f"name '{fm.get('name')}' must equal the directory name '{name}'")
        desc = fm.get("description")
        if not isinstance(desc, str) or not desc.strip():
            err(skill_md, "description missing")
        elif len(desc) > 1024:
            err(skill_md, f"description is {len(desc)} chars (max 1024)")
        if "version" in fm:
            err(skill_md, "drop the version field; the plugin version is the only version")
        user_invoked = fm.get("disable-model-invocation") is True

        oai = skill_dir / "agents" / "openai.yaml"
        if not oai.is_file():
            err(skill_dir, "missing agents/openai.yaml")
            continue
        try:
            meta = yaml.safe_load(oai.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            err(oai, f"invalid YAML: {e}")
            continue
        iface = meta.get("interface") or {}
        for key in ("display_name", "short_description"):
            if not iface.get(key):
                err(oai, f"interface.{key} missing")
        implicit = (meta.get("policy") or {}).get("allow_implicit_invocation", True)
        if user_invoked and implicit is not False:
            err(oai, "user-invoked skill needs policy.allow_implicit_invocation: false")
        if not user_invoked and implicit is False:
            err(oai, "policy blocks implicit invocation but SKILL.md lacks disable-model-invocation: true")
    return promoted, parked


def check_manifests(promoted: list[str]) -> None:
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    market_path = ROOT / ".claude-plugin" / "marketplace.json"
    plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
    market = json.loads(market_path.read_text(encoding="utf-8"))
    listed = plugin.get("skills", [])
    for p in sorted(set(promoted) - set(listed)):
        err(plugin_path, f"promoted skill not listed: {p}")
    for p in sorted(set(listed) - set(promoted)):
        err(plugin_path, f"listed skill is not a promoted skill directory: {p}")
    if len(listed) != len(set(listed)):
        err(plugin_path, "duplicate entries in skills")
    entries = [p for p in market.get("plugins", []) if p.get("name") == plugin.get("name")]
    if not entries:
        err(market_path, f"no plugin entry named {plugin.get('name')}")
    elif entries[0].get("version") != plugin.get("version"):
        err(market_path, f"version {entries[0].get('version')} != plugin.json {plugin.get('version')}")


def check_readme(promoted: list[str], parked: list[str]) -> None:
    readme = ROOT / "README.md"
    links = {t.split("#", 1)[0].removeprefix("./") for _, t in prose_links(readme.read_text(encoding="utf-8"))}
    for p in promoted:
        target = p.removeprefix("./") + "/SKILL.md"
        if target not in links:
            err(readme, f"catalog entry must link {target}")
    for p in parked:
        target = p.removeprefix("./")
        if any(link.startswith(target) for link in links):
            err(readme, f"status-bucket skill must not be in the catalog: {target}")


def check_wiring() -> None:
    commands = ROOT / "commands"
    if commands.exists() and any(commands.iterdir()):
        err(commands, "skills are the slash commands; fold commands into their skill")
    hooks = ROOT / "hooks" / "hooks.json"
    if hooks.is_file():
        spec = json.loads(hooks.read_text(encoding="utf-8"))
        for groups in spec.get("hooks", {}).values():
            for group in groups:
                for hook in group.get("hooks", []):
                    for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)", hook.get("command", "")):
                        if not (ROOT / ref).is_file():
                            err(hooks, f"hook script not found: {ref}")
    for agent in sorted((ROOT / "agents").glob("*.md")):
        fm = frontmatter(agent)
        if fm is not None and fm.get("name") != agent.stem:
            err(agent, f"agent name '{fm.get('name')}' must equal the file name")


def check_hygiene(files: list[Path]) -> None:
    for f in files:
        if f == SELF or f.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".wav", ".mp4"}:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if HOME_PATH.search(line):
                err(f, f"line {n}: home-directory path")
            for label, rx in SECRETS.items():
                if rx.search(line):
                    err(f, f"line {n}: looks like a {label}")
        if f.suffix == ".md":
            check_links(f, text)


def prose_links(text: str) -> list[tuple[int, str]]:
    """(line number, target) of Markdown links outside code fences and inline code."""
    found, in_fence = [], False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line.lstrip()):
            in_fence = not in_fence
            continue
        if not in_fence:
            found += [(n, m.group(1)) for m in MD_LINK.finditer(re.sub(r"`[^`]*`", "", line))]
    return found


def check_links(f: Path, text: str) -> None:
    for n, target in prose_links(text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith(("#", "<")) or "{{" in target:
            continue
        path = target.split("#", 1)[0].split("?", 1)[0]
        if path and not (f.parent / path).exists():
            err(f, f"line {n}: broken link {target}")


def main() -> int:
    quiet = "--quiet" in sys.argv
    promoted, parked = check_skills()
    check_manifests(promoted)
    check_readme(promoted, parked)
    check_wiring()
    check_hygiene(tracked_files())
    for e in errors:
        print(f"FAIL {e}")
    if not quiet:
        state = "FAIL" if errors else "PASS"
        print(f"{state}: {len(promoted)} promoted, {len(parked)} parked skills, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
