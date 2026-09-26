#!/usr/bin/env bash
# Symlink this repo's skills into the local harness skill directories, so a
# `git pull` updates them everywhere:
#   ~/.claude/skills   Claude Code
#   ~/.agents/skills   Codex, pi and other Agent Skills harnesses
#
# Links every skill outside skills/deprecated/. Use it instead of the plugin,
# not with it: with both, Claude Code lists every skill twice. Plugin subagents
# (insistir's crew) and hooks only come with the plugin.
#
# Usage: scripts/link-skills.sh [--dry-run] [--force] [--unlink]
#   --dry-run  print what would change
#   --force    replace an existing real directory of the same name; it moves to
#              <parent>/skills-backup/<name>.<timestamp>, outside any skills dir
#   --unlink   remove the symlinks that point into this repo, then exit
# Runs on bash 3.2 (stock macOS).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd -P)"
DRY=0 FORCE=0 UNLINK=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --force) FORCE=1 ;;
    --unlink) UNLINK=1 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

run() { if [ "$DRY" -eq 1 ]; then echo "would: $*"; else "$@"; fi; }

real_dir() { (cd "$1" 2>/dev/null && pwd -P) || true; }

seen=""
for dest in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
  run mkdir -p "$dest"
  real="$(real_dir "$dest")"
  [ -n "$real" ] || real="$dest"
  case "$real" in
    "$REPO"|"$REPO"/*) echo "error: $dest resolves into this repo ($real)" >&2; exit 1 ;;
  esac
  # ~/.claude/skills is often a symlink to ~/.agents/skills: link once per real dir.
  case " $seen " in *" $real "*) echo "skip $dest (same directory as an earlier destination)"; continue ;; esac
  seen="$seen $real"

  if [ "$UNLINK" -eq 1 ]; then
    for link in "$dest"/*; do
      [ -L "$link" ] || continue
      case "$(readlink "$link")" in
        "$REPO"/*) run rm "$link"; [ "$DRY" -eq 1 ] || echo "unlinked $link" ;;
      esac
    done
    continue
  fi

  find "$REPO/skills" -mindepth 3 -maxdepth 3 -name SKILL.md -not -path '*/deprecated/*' -print0 |
    while IFS= read -r -d '' skill_md; do
      src="$(dirname "$skill_md")"
      target="$dest/$(basename "$src")"
      if [ -e "$target" ] && [ ! -L "$target" ]; then
        if [ "$FORCE" -eq 0 ]; then
          echo "skip $target (a real directory; --force moves it aside and links)"
          continue
        fi
        backup="$(dirname "$dest")/skills-backup/$(basename "$src").$(date +%Y%m%d%H%M%S)"
        run mkdir -p "$(dirname "$backup")"
        run mv "$target" "$backup"
        [ "$DRY" -eq 1 ] || echo "moved $target -> $backup"
      fi
      run ln -sfn "$src" "$target"
      [ "$DRY" -eq 1 ] || echo "linked $target -> $src"
    done
done
