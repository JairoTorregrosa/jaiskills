#!/usr/bin/env bash
# ask_codex.sh: send one prompt (stdin) to headless `codex exec`, read-only, for second-opinion.
# Runs on bash 3.2 (macOS). Never uses the Codex MCP server.
#
# New session:
#   ask_codex.sh -C REPO [-o OUTDIR] [--schema FILE] [-m MODEL] [-e EFFORT] [-t SECS] \
#                [--keep-session] < prompt.md
# Follow-up in a kept session:
#   ask_codex.sh -C REPO --resume SESSION_ID [-o OUTDIR] [-t SECS] < followup.md
#
#   -C REPO          working root Codex may read (required)
#   -o OUTDIR        where prompt.md, last-message.md, codex.log, session-id go (default: mktemp -d)
#   --schema FILE    JSON Schema for the final answer (codex --output-schema); answer is JSON-checked
#   -m MODEL         override the model
#   -e EFFORT        model_reasoning_effort (low|medium|high|xhigh)
#   -t SECS          wall-clock timeout, default 540 (under the 600 s cap of agent Bash tools)
#   --keep-session   persist the session so --resume works (default: --ephemeral)
#   --resume ID      continue session ID ("last" = newest session recorded for REPO)
#
# stdout on success, one key=value per line: out_dir, last_message, session_id, model, elapsed_s.
# Exit: 0 ok | 2 usage | 3 codex not installed | 4 codex not logged in | 5 timeout
#       6 codex failed or wrote no answer | 7 answer is not valid JSON (--schema only)
# Exit 3, 4, 5 => caller falls back to a fresh Claude subagent ("same-provider fallback").

set -uo pipefail

REPO=""
OUT=""
SCHEMA=""
MODEL=""
EFFORT=""
TIMEOUT_S=540
KEEP=0
RESUME=""

die() {
	echo "ask_codex: $2" >&2
	exit "$1"
}

while [ $# -gt 0 ]; do
	case "$1" in
	-h | --help)
		sed -n '2,23p' "$0"
		exit 0
		;;
	--keep-session)
		KEEP=1
		shift
		continue
		;;
	-C | -o | --schema | -m | -e | -t | --resume)
		[ $# -ge 2 ] || die 2 "$1 needs a value"
		;;
	*) die 2 "unknown argument: $1 (see --help)" ;;
	esac
	case "$1" in
	-C) REPO="$2" ;;
	-o) OUT="$2" ;;
	--schema) SCHEMA="$2" ;;
	-m) MODEL="$2" ;;
	-e) EFFORT="$2" ;;
	-t) TIMEOUT_S="$2" ;;
	--resume) RESUME="$2" ;;
	esac
	shift 2
done

[ -n "$REPO" ] || die 2 "-C REPO is required"
[ -d "$REPO" ] || die 2 "not a directory: $REPO"
REPO=$(cd "$REPO" && pwd)
case "$TIMEOUT_S" in '' | *[!0-9]*) die 2 "-t needs whole seconds" ;; esac
if [ -n "$SCHEMA" ]; then
	[ -f "$SCHEMA" ] || die 2 "schema not found: $SCHEMA"
	SCHEMA=$(cd "$(dirname "$SCHEMA")" && pwd)/$(basename "$SCHEMA")
fi
[ -t 0 ] && die 2 "pipe the prompt on stdin"

command -v codex >/dev/null 2>&1 || die 3 "codex CLI not installed"
codex login status >/dev/null 2>&1 || die 4 "codex is not logged in (run: codex login)"

if [ -z "$OUT" ]; then
	OUT=$(mktemp -d "${TMPDIR:-/tmp}/second-opinion.XXXXXX") || die 6 "mktemp failed"
fi
mkdir -p "$OUT" || die 6 "cannot create $OUT"
OUT=$(cd "$OUT" && pwd)

PROMPT="$OUT/prompt.md"
LAST="$OUT/last-message.md"
LOG="$OUT/codex.log"
cat >"$PROMPT"
[ -s "$PROMPT" ] || die 2 "empty prompt on stdin"
rm -f "$LAST"

if [ -n "$RESUME" ]; then
	# resume has no --sandbox/-C flags: force read-only via config, run from REPO.
	cmd=(codex exec resume --skip-git-repo-check -c 'sandbox_mode="read-only"' -o "$LAST")
	if [ "$RESUME" = "last" ]; then cmd+=(--last); else cmd+=("$RESUME"); fi
else
	cmd=(codex exec --sandbox read-only --skip-git-repo-check -C "$REPO" -o "$LAST")
	[ "$KEEP" -eq 1 ] || cmd+=(--ephemeral)
fi
[ -n "$SCHEMA" ] && cmd+=(--output-schema "$SCHEMA")
[ -n "$MODEL" ] && cmd+=(-m "$MODEL")
[ -n "$EFFORT" ] && cmd+=(-c "model_reasoning_effort=\"$EFFORT\"")
cmd+=(-)

# Portable timeout: coreutils timeout/gtimeout if present, else a watchdog. 124 = timed out.
run_limited() {
	if command -v timeout >/dev/null 2>&1; then
		timeout "$TIMEOUT_S" "$@" <"$PROMPT" >"$OUT/stdout.txt" 2>"$LOG"
		return $?
	fi
	if command -v gtimeout >/dev/null 2>&1; then
		gtimeout "$TIMEOUT_S" "$@" <"$PROMPT" >"$OUT/stdout.txt" 2>"$LOG"
		return $?
	fi
	"$@" <"$PROMPT" >"$OUT/stdout.txt" 2>"$LOG" &
	local pid=$! rc=0 wd
	(sleep "$TIMEOUT_S" && kill -TERM "$pid" 2>/dev/null) &
	wd=$!
	wait "$pid" || rc=$?
	kill "$wd" 2>/dev/null
	wait "$wd" 2>/dev/null
	[ "$rc" -eq 143 ] && rc=124
	return "$rc"
}

start=$(date +%s)
rc=0
(cd "$REPO" && run_limited "${cmd[@]}") || rc=$?
elapsed=$(($(date +%s) - start))

session=$(sed -n 's/^session id: *//p' "$LOG" 2>/dev/null | head -n 1)
[ -n "$session" ] || session="none"
echo "$session" >"$OUT/session-id"
model=$(sed -n 's/^model: *//p' "$LOG" 2>/dev/null | head -n 1)
[ -n "$model" ] || model="unknown"

[ "$rc" -eq 124 ] && die 5 "timed out after ${TIMEOUT_S}s (log: $LOG)"
[ "$rc" -eq 0 ] || die 6 "codex exited $rc (log: $LOG)"
[ -s "$LAST" ] || die 6 "codex wrote no final message (log: $LOG)"

if [ -n "$SCHEMA" ]; then
	if command -v jq >/dev/null 2>&1; then
		jq -e . "$LAST" >/dev/null 2>&1 || die 7 "final message is not valid JSON: $LAST"
	elif command -v python3 >/dev/null 2>&1; then
		python3 -m json.tool "$LAST" >/dev/null 2>&1 || die 7 "final message is not valid JSON: $LAST"
	fi
fi

printf 'out_dir=%s\nlast_message=%s\nsession_id=%s\nmodel=%s\nelapsed_s=%s\n' \
	"$OUT" "$LAST" "$session" "$model" "$elapsed"
