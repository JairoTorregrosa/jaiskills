#!/usr/bin/env python3
"""Re-sync skills/models/askcodex from a checkout of the askcodex repo.

Usage: uv run scripts/sync-askcodex.py PATH/TO/askcodex

The canonical skill is `skill/` in https://github.com/JairoTorregrosa/askcodex.
This replaces everything in skills/models/askcodex/ except `agents/` (local
Codex picker metadata) with the committed `skill/` at the checkout's HEAD
(`git archive`, so ignored or untracked files never ship; a dirty `skill/` is
refused), then re-applies the mirror's only delta:

1. the description's not-for clause points to second-opinion;
2. a "Canonical copy" note above the first `##` section.

It exits non-zero, before touching anything, when the upstream wording the
delta replaces has moved, so the delta is never silently lost. Prints a JSON
summary on success.
"""

import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "skills" / "models" / "askcodex"
KEEP = {"agents"}

# The exact upstream sentence, matched word for word across any line wrap: a
# reworded or extended clause must stop the sync, not vanish into the delta.
UPSTREAM_SENTENCE = (
    "Not for reviewing a repository, plan or diff in place: askcodex sends only the text you "
    "give it and cannot read files."
)
UPSTREAM_NOT_FOR = re.compile(r"\s+".join(map(re.escape, UPSTREAM_SENTENCE.split())))
LOCAL_NOT_FOR = "Not for critiquing repo work, plans or diffs: use second-opinion, which reads the repo."
NOTE = (
    "Canonical copy: `skill/` in https://github.com/JairoTorregrosa/askcodex (this is a mirror; change\n"
    "it there, then re-sync). Local delta: the description's not-for clause points to second-opinion.\n"
)


def die(message: str) -> None:
    print(f"sync-askcodex: {message}", file=sys.stderr)
    sys.exit(1)


def localize(skill_md: str) -> str:
    """Apply the mirror delta to an upstream SKILL.md, or die."""
    if skill_md.count("\n---\n") < 1 or not skill_md.startswith("---\n"):
        die("upstream SKILL.md has no frontmatter")
    end = skill_md.index("\n---\n", 4)
    front, body = skill_md[:end], skill_md[end:]
    front, hits = UPSTREAM_NOT_FOR.subn(LOCAL_NOT_FOR, front)
    if hits != 1:
        die(f"expected one upstream not-for clause in the description, found {hits}")
    section = body.find("\n## ")
    if section < 0:
        die("upstream SKILL.md has no ## section to put the canonical note above")
    body = body[: section + 1] + NOTE + "\n" + body[section + 1 :]
    return front + body


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )
    if done.returncode != 0:
        die(f"git {' '.join(args)} failed in {repo}: {done.stderr.strip()}")
    return done.stdout.strip()


def main() -> None:
    if len(sys.argv) != 2:
        die("usage: sync-askcodex.py PATH/TO/askcodex")
    repo = Path(sys.argv[1]).expanduser().resolve()
    source = repo / "skill"
    if not (source / "SKILL.md").is_file():
        die(f"{source}/SKILL.md not found")
    # Only committed upstream content may ship: refuse local edits or
    # untracked files under skill/, and report exactly which commit synced.
    if git(repo, "status", "--porcelain", "--untracked-files=all", "--", "skill"):
        die(
            f"{source} has uncommitted or untracked changes; sync from a clean checkout"
        )
    commit = git(repo, "rev-parse", "--short", "HEAD")
    describe = git(repo, "describe", "--tags", "--always", "HEAD")

    # Build the new mirror next to the old one, then swap, so a failure
    # midway leaves the old mirror intact. The content comes from
    # `git archive HEAD`, so only tracked, committed files can ship: ignored
    # files (a local secret, a build artifact) never reach the mirror.
    with tempfile.TemporaryDirectory(dir=MIRROR.parent) as scratch:
        archive = Path(scratch) / "skill.tar"
        git(repo, "archive", "--format=tar", "-o", str(archive), "HEAD", "skill")
        with tarfile.open(archive) as tar:
            tar.extractall(scratch, filter="data")
        staged = Path(scratch) / "skill"
        if (staged / "agents").exists():
            die("skill/agents exists upstream; decide which copy wins before syncing")
        skill_md = staged / "SKILL.md"
        skill_md.write_text(
            localize(skill_md.read_text(encoding="utf-8")), encoding="utf-8"
        )
        for kept in KEEP:
            if (MIRROR / kept).exists():
                shutil.copytree(MIRROR / kept, staged / kept)
        old = Path(scratch) / "old"
        MIRROR.rename(old)
        staged.rename(MIRROR)

    files = sorted(str(p.relative_to(MIRROR)) for p in MIRROR.rglob("*") if p.is_file())
    print(
        json.dumps(
            {
                "source": str(source),
                "commit": commit,
                "describe": describe,
                "released": describe.count("-") < 2 and describe.startswith("v"),
                "mirror": str(MIRROR.relative_to(ROOT)),
                "files": len(files),
                "kept": sorted(KEEP),
            }
        )
    )


if __name__ == "__main__":
    main()
