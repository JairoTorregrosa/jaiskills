#!/usr/bin/env bash
# remoto — spawn and manage headless claude/codex agents on a remote SSH host.
#
# Jobs live on the REMOTE at ~/.remoto/jobs/<id>/ :
#   prompt.md   the full prompt the agent was given
#   run.sh      the generated runner (setsid'd process-group leader)
#   meta.env    engine=/model=/workdir=/created= key=value metadata
#   pid         process-group id of the runner
#   out.log     agent stdout (claude: stream-json lines; codex: human log)
#   err.log     agent stderr
#   result.txt  codex only — final message (--output-last-message)
#   exit_code   written when the agent exits; its presence means "finished"
#
# Host selection: REMOTO_HOST env var (default: jetson).
set -euo pipefail

HOST="${REMOTO_HOST:-jetson}"
JOBS_ROOT=".remoto/jobs"
SSH_OPTS=(-o ConnectTimeout=10 -o BatchMode=yes)

die() { echo "remoto: $*" >&2; exit 1; }
rssh() { ssh "${SSH_OPTS[@]}" "$HOST" "$@"; }

usage() {
  cat <<'EOF'
usage: remoto.sh <command> [args]

  hosts                             probe hosts (REMOTO_HOSTS, default: jetson jetson-ts)
  spawn -e claude|codex -d <dir> [-m model] [-n name] [--safe] <prompt|->
                                    launch a headless agent on $REMOTO_HOST; prints job id.
                                    <dir> is the REMOTE working directory (must exist).
                                    '-' reads the prompt from stdin.
                                    --safe: claude acceptEdits / codex --full-auto sandbox
                                    (default: full bypass — remote box is disposable).
  ls                                list all jobs with status
  status <job>...                   status of specific jobs (RUNNING|DONE|FAILED|DEAD)
  wait [-t seconds] <job>...        block until all jobs finish (poll 15s, default timeout 7200)
  logs [-f] <job>                   tail err.log + out.log (-f follows)
  result <job>                      print the agent's final answer
  kill <job>                        kill the job's whole process group
  push <local> <remote>             rsync a local path to the host (mind trailing slashes)
  pull <remote> <local>             rsync a remote path back
  clean                             delete finished job dirs on the host
EOF
  exit 1
}

remote_status() {  # args: job ids -> lines "id STATE rc"
  rssh "bash -s -- $*" <<'RS'
for j in "$@"; do
  d="$HOME/.remoto/jobs/$j"
  if [ ! -d "$d" ]; then echo "$j MISSING -"
  elif [ -f "$d/exit_code" ]; then
    rc=$(cat "$d/exit_code")
    if [ "$rc" = 0 ]; then echo "$j DONE 0"; else echo "$j FAILED $rc"; fi
  elif [ -f "$d/pid" ] && kill -0 "$(cat "$d/pid")" 2>/dev/null; then echo "$j RUNNING -"
  else echo "$j DEAD -"
  fi
done
RS
}

cmd="${1:-}"; [ -n "$cmd" ] || usage; shift

case "$cmd" in

hosts)
  for h in ${REMOTO_HOSTS:-jetson jetson-ts}; do
    if out=$(ssh "${SSH_OPTS[@]}" -o ConnectTimeout=5 "$h" \
        'export PATH="$HOME/.local/bin:$PATH"; printf "claude %s | codex %s | load %s" "$(claude --version 2>/dev/null | head -1)" "$(codex --version 2>/dev/null)" "$(cut -d" " -f1 /proc/loadavg)"' 2>/dev/null); then
      echo "$h: UP — $out"
    else
      echo "$h: DOWN"
    fi
  done
  ;;

spawn)
  engine="" workdir="" model="" name="agent" safe=0
  args=()
  while [ $# -gt 0 ]; do
    case "$1" in
      -e|--engine) engine="$2"; shift 2 ;;
      -d|--dir) workdir="$2"; shift 2 ;;
      -m|--model) model="$2"; shift 2 ;;
      -n|--name) name="$2"; shift 2 ;;
      --safe) safe=1; shift ;;
      *) args+=("$1"); shift ;;
    esac
  done
  [ "$engine" = claude ] || [ "$engine" = codex ] || die "spawn: -e must be claude or codex"
  [ -n "$workdir" ] || die "spawn: -d <remote workdir> is required"

  prompt="${args[*]:-}"
  if [ "$prompt" = "-" ] || [ -z "$prompt" ]; then
    [ -t 0 ] && die "spawn: no prompt given (pass as argument or pipe with '-')"
    prompt="$(cat)"
  fi
  [ -n "$prompt" ] || die "spawn: empty prompt"

  id="${name}-$(date +%Y%m%d-%H%M%S)-$RANDOM"
  job="$JOBS_ROOT/$id"
  # ~ in the workdir must expand on the REMOTE, so rewrite it to a literal $HOME.
  rwd="${workdir/#\~/\$HOME}"

  if [ "$engine" = claude ]; then
    agent_cmd='claude -p --verbose --output-format stream-json'
    if [ "$safe" = 1 ]; then agent_cmd+=' --permission-mode acceptEdits'; else agent_cmd+=' --dangerously-skip-permissions'; fi
    [ -n "$model" ] && agent_cmd+=" --model $model"
  else
    agent_cmd='codex exec --skip-git-repo-check --output-last-message "$JOB/result.txt"'
    if [ "$safe" = 1 ]; then agent_cmd+=' --full-auto'; else agent_cmd+=' --dangerously-bypass-approvals-and-sandbox'; fi
    [ -n "$model" ] && agent_cmd+=" -m $model"
    agent_cmd+=' -'
  fi

  printf '%s' "$prompt" | rssh "mkdir -p '$job' && cat > '$job/prompt.md'"

  rssh "cat > '$job/meta.env'" <<EOF
engine=$engine
model=$model
workdir=$workdir
safe=$safe
host=$HOST
created=$(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

  # run.sh: local vars ($job, $rwd, $agent_cmd) expand NOW; \$-escaped ones expand on the remote.
  rssh "cat > '$job/run.sh' && chmod +x '$job/run.sh'" <<EOF
#!/usr/bin/env bash
export PATH="\$HOME/.local/bin:\$PATH"
JOB="\$HOME/$job"
echo \$\$ > "\$JOB/pid"
cd "$rwd" || { echo 127 > "\$JOB/exit_code"; exit 127; }
$agent_cmd < "\$JOB/prompt.md" > "\$JOB/out.log" 2> "\$JOB/err.log"
rc=\$?
echo \$rc > "\$JOB/exit_code"
exit \$rc
EOF

  rssh "cd '$job' && nohup setsid ./run.sh > launcher.log 2>&1 < /dev/null & exit 0"
  echo "$id"
  ;;

ls)
  rssh bash -s <<'RS'
cd "$HOME/.remoto/jobs" 2>/dev/null || exit 0
for j in $(ls -1t); do
  [ -d "$j" ] || continue
  engine=$(sed -n 's/^engine=//p' "$j/meta.env" 2>/dev/null)
  if [ -f "$j/exit_code" ]; then
    rc=$(cat "$j/exit_code")
    if [ "$rc" = 0 ]; then st="DONE"; else st="FAILED($rc)"; fi
  elif [ -f "$j/pid" ] && kill -0 "$(cat "$j/pid")" 2>/dev/null; then st="RUNNING"
  else st="DEAD"
  fi
  printf '%-12s %-8s %s\n' "$st" "$engine" "$j"
done
RS
  ;;

status)
  [ $# -gt 0 ] || die "status: give at least one job id"
  remote_status "$@"
  ;;

wait)
  timeout=7200
  if [ "${1:-}" = "-t" ]; then timeout="$2"; shift 2; fi
  [ $# -gt 0 ] || die "wait: give at least one job id"
  start=$(date +%s)
  while true; do
    out="$(remote_status "$@")"
    echo "$out"
    if ! grep -q ' RUNNING ' <<<"$out "; then
      grep -qE ' (FAILED|DEAD|MISSING) ' <<<"$out " && exit 1
      exit 0
    fi
    elapsed=$(( $(date +%s) - start ))
    [ "$elapsed" -ge "$timeout" ] && { echo "remoto: wait timed out after ${timeout}s" >&2; exit 124; }
    sleep 15
  done
  ;;

logs)
  follow=0
  if [ "${1:-}" = "-f" ]; then follow=1; shift; fi
  [ $# -eq 1 ] || die "logs: give exactly one job id"
  job="$JOBS_ROOT/$1"
  if [ "$follow" = 1 ]; then
    rssh -t "tail -n 50 -F '$job/err.log' '$job/out.log'"
  else
    rssh "tail -n 100 '$job/err.log' '$job/out.log' 2>/dev/null"
  fi
  ;;

result)
  [ $# -eq 1 ] || die "result: give exactly one job id"
  job="$JOBS_ROOT/$1"
  engine=$(rssh "sed -n 's/^engine=//p' '$job/meta.env'")
  case "$engine" in
    codex)
      rssh "cat '$job/result.txt' 2>/dev/null || { echo 'remoto: no result.txt — job failed? err.log tail:' >&2; tail -n 30 '$job/err.log' >&2; exit 1; }"
      ;;
    claude)
      rssh "cd '$job' && python3 -" <<'PY'
import json, sys
res = None
try:
    with open("out.log") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if obj.get("type") == "result":
                res = obj
except FileNotFoundError:
    sys.exit("remoto: no out.log for this job")
if res is None:
    sys.exit("remoto: no result event in out.log — job still running or crashed; check logs")
if res.get("is_error"):
    print("[AGENT ERRORED]", file=sys.stderr)
print(res.get("result", ""))
PY
      ;;
    *) die "result: unknown engine '$engine' for job $1" ;;
  esac
  ;;

kill)
  [ $# -eq 1 ] || die "kill: give exactly one job id"
  job="$JOBS_ROOT/$1"
  rssh "pid=\$(cat '$job/pid' 2>/dev/null) && kill -TERM -- -\$pid 2>/dev/null && echo 137 > '$job/exit_code' && echo killed || echo 'not running'"
  ;;

push)
  [ $# -eq 2 ] || die "push: usage: push <local> <remote>"
  rsync -az -e "ssh ${SSH_OPTS[*]}" "$1" "$HOST:$2"
  ;;

pull)
  [ $# -eq 2 ] || die "pull: usage: pull <remote> <local>"
  rsync -az -e "ssh ${SSH_OPTS[*]}" "$HOST:$1" "$2"
  ;;

clean)
  rssh bash -s <<'RS'
cd "$HOME/.remoto/jobs" 2>/dev/null || exit 0
for j in *; do
  [ -f "$j/exit_code" ] && rm -rf "$j" && echo "removed $j"
done
true
RS
  ;;

*) usage ;;
esac
