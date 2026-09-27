#!/usr/bin/env bash
# ask_codex.sh: send one prompt (stdin) to headless `codex exec`, read-only, for second-opinion.
# Codex only advises, reviews and judges here: every call is forced read-only, whatever
# ~/.codex/config.toml says. Runs on bash 3.2 (macOS). Never uses the Codex MCP server.
#
# New session:
#   ask_codex.sh -C REPO [-o OUTDIR] [--schema FILE] [-m MODEL] [-e EFFORT] [-t SECS] \
#                [--keep-session] < prompt.md
# Follow-up in a kept session:
#   ask_codex.sh -C REPO --resume SESSION_ID [-o OUTDIR] [-t SECS] < followup.md
# Codex's built-in reviewer (stdin = optional extra instructions, may be empty):
#   ask_codex.sh -C REPO --review uncommitted|base:REF|commit:SHA [-m MODEL] [-e EFFORT] < /dev/null
#
#   -C REPO          working root Codex may read (required)
#   -o OUTDIR        where prompt.md, last-message.md, codex.log, session-id go (default: mktemp -d)
#   --schema FILE    JSON Schema for the final answer (codex --output-schema); answer is JSON-checked
#   -m MODEL         model; default $SECOND_OPINION_MODEL, else gpt-6-astra when Codex's catalog
#                    (~/.codex/models_cache.json) lists it, else the config default
#   -e EFFORT        model_reasoning_effort (low|medium|high|xhigh|max|ultra); default
#                    $SECOND_OPINION_EFFORT, else high (the user config may default to low)
#   --review TARGET  run `codex exec review` on uncommitted | base:REF | commit:SHA
#   -t SECS          wall-clock timeout, default 540 (under the 600 s cap of agent Bash tools)
#   --keep-session   persist the session so --resume works (default: --ephemeral)
#   --resume ID      continue session ID ("last" = newest session recorded for REPO)
#
# stdout on success, one key=value per line: out_dir, last_message, session_id, model, elapsed_s.
# Exit: 0 ok | 2 usage | 3 codex not installed | 4 codex not logged in | 5 timeout
#       6 codex failed or wrote no answer | 7 answer is not valid JSON (--schema only)
# Exit 3, 4, 5 => caller falls back to a fresh Claude subagent ("same-provider fallback").
# Every call also disables Codex memories (-c features.memories=false), so no unrelated session
# leaks in, and ignores user/project execpolicy rules (--ignore-rules): an "allow" rule such as
# `bash -ic` could otherwise run a command outside the read-only sandbox. Lifecycle hooks and the
# legacy notify command are off too (--disable hooks, notify=[]): they run outside the sandbox.
# Native review uses review_model before -m, so --review pins review_model to the chosen model.
# --review takes no instructions: codex exec review cannot combine a target with a prompt.

set -uo pipefail

REPO=""
OUT=""
SCHEMA=""
MODEL=""
EFFORT="${SECOND_OPINION_EFFORT:-high}"
REVIEW=""
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
		sed -n '2,35p' "$0"
		exit 0
		;;
	--keep-session)
		KEEP=1
		shift
		continue
		;;
	-C | -o | --schema | -m | -e | -t | --resume | --review)
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
	--review) REVIEW="$2" ;;
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
[ -t 0 ] && die 2 "pipe the prompt on stdin (for --review with no extra instructions: < /dev/null)"
[ -n "$REVIEW" ] && [ -n "$RESUME" ] && die 2 "--review and --resume are exclusive"
[ -n "$REVIEW" ] && [ -n "$SCHEMA" ] && die 2 "--review has its own output; drop --schema"
case "$REVIEW" in
'' | uncommitted) ;;
base:?*) ;;
commit:?*) ;;
*) die 2 "--review takes uncommitted, base:REF or commit:SHA" ;;
esac

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
[ -s "$PROMPT" ] || [ -n "$REVIEW" ] || die 2 "empty prompt on stdin"
[ -n "$REVIEW" ] && [ -s "$PROMPT" ] &&
	die 2 "--review cannot take instructions (codex exec review rejects a target plus a prompt); pass < /dev/null, or use adversarial mode for a steered review"
rm -f "$LAST"

# Model: explicit -m, else $SECOND_OPINION_MODEL, else gpt-6-astra if Codex's own catalog lists it.
if [ -z "$MODEL" ]; then
	want="${SECOND_OPINION_MODEL:-gpt-6-astra}"
	cache="${CODEX_HOME:-$HOME/.codex}/models_cache.json"
	if [ -n "${SECOND_OPINION_MODEL:-}" ] || grep -q "\"slug\": *\"$want\"" "$cache" 2>/dev/null; then
		MODEL="$want"
	else
		echo "ask_codex: $want not in $cache; using the config default model" >&2
	fi
fi

if [ -n "$REVIEW" ]; then
	# exec review has no --sandbox/-C flags: force read-only via config, run from REPO.
	cmd=(codex exec review --skip-git-repo-check -c 'sandbox_mode="read-only"' -o "$LAST")
	[ "$KEEP" -eq 1 ] || cmd+=(--ephemeral)
	case "$REVIEW" in
	uncommitted) cmd+=(--uncommitted) ;;
	base:*) cmd+=(--base "${REVIEW#base:}") ;;
	commit:*) cmd+=(--commit "${REVIEW#commit:}") ;;
	esac
elif [ -n "$RESUME" ]; then
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
[ -n "$REVIEW" ] && [ -n "$MODEL" ] && cmd+=(-c "review_model=\"$MODEL\"")
cmd+=(-c 'features.memories=false' -c 'approval_policy="never"' -c 'notify=[]' --ignore-rules --disable hooks)
# cmux's codex shim injects its own hooks unless told not to.
export CMUX_CODEX_HOOKS_DISABLED=1
[ -n "$REVIEW" ] || cmd+=(-)

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
# Parallel runs share ~/.codex SQLite state; a start that loses the lock race fails fast with
# this message (openai/codex#35555, #46269). Retry once after a short pause.
if [ "$rc" -ne 0 ] && [ "$rc" -ne 124 ] && grep -q 'another Codex process is using its local data' "$LOG" 2>/dev/null; then
	sleep 3
	rc=0
	(cd "$REPO" && run_limited "${cmd[@]}") || rc=$?
fi
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
