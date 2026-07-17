---
name: status
description: "Show the remote agent fleet: host health and all jobs with their states"
argument-hint: "[job-id ...]"
---

Using the remote-agents skill's CLI (`${CLAUDE_PLUGIN_ROOT}/scripts/remoto.sh`):

1. Run `hosts` to probe host health.
2. If job ids were given ($ARGUMENTS), run `status` on them and `result` for any that are DONE; otherwise run `ls` for the whole fleet.
3. Summarize: what's running, what finished, what failed (include `logs` tail for failures).
