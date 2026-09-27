# Adversarial mode

GPT tries to break confidence in a change. Claude runs it, verifies every finding, and presents
only what survives. Codex never fixes anything.

## 1. Target and focus

- Target, first match wins: a range or paths in the request; uncommitted changes (`git status
  --porcelain`); the branch against its base (`git merge-base HEAD origin/main`); a plan or design
  file for a design-level challenge. Nothing → stop: "Nothing to challenge".
- Focus: the user's words after the mode and flags ("auth", "the migration", "rollback"), verbatim.
  None → `none`.
- Name the range in the prompt (`git diff <base>...HEAD -- <paths>`) and let Codex read it. Paste
  only what exists nowhere on disk.

## 2. Claude's own view first

Before reading any Codex output, write Claude's top 3 risks for the change in bullets. Never put
them in the prompt; they keep the comparison honest.

## 3. One run or parallel lenses

| Change | Runs |
|---|---|
| Small (≤ 3 files) or a single concern | 1 run, lens `general` |
| Larger, risky, or `--lenses a,b,c` given | 2-3 runs, one lens each, in parallel |

Lenses (pick the ones the change can actually fail on, max 3):

- `correctness and data`: wrong results, data loss, duplication, irreversible changes, rollback
- `security and boundaries`: auth, permissions, tenant isolation, secrets, hostile input
- `failure and concurrency`: partial failure, retries, idempotency, races, timeouts, degraded deps
- `design assumptions`: what the approach assumes about scale, users, ordering, versions, and where
  that stops holding

For each run, render [adversarial-prompt.md](adversarial-prompt.md) (fill `{{TARGET}}`,
`{{RANGE}}`, `{{FOCUS}}`, `{{LENS}}`; drop the leading comment) into its own file and start every
run in the same message, each with its own output dir:

```bash
REPO=$(git rev-parse --show-toplevel) && \
"${CLAUDE_SKILL_DIR}/scripts/ask_codex.sh" -C "$REPO" -e high -o "$OUT/<lens>" \
  --schema "${CLAUDE_SKILL_DIR}/references/adversarial.schema.json" < "$OUT/<lens>.md"
```

Parallel runs work (tested: two ephemeral read-only runs at once, 44 s and 51 s on gpt-6-astra).
They share `~/.codex` SQLite state, so start them about 2 s apart; the script retries once when a
start loses the lock race. Keep it to 3 at a time: every run counts against the ChatGPT plan's
Codex limit, and Astra's is the tightest. Use `-e xhigh` for auth, money, migrations or anything
irreversible. Large diffs: Bash `run_in_background: true` with `-t 1800`, launched from the main
conversation (background commands started inside a foreground subagent die when it returns).

## 4. Merge

- Parse each `last-message.md`. A run that fails (exit 6/7) is retried once; exit 3/4/5 → the
  fallback in SKILL.md, labelled.
- Deduplicate findings whose file matches and line ranges overlap; keep the higher severity and
  note which lenses found it (found by two lenses = stronger signal).

## 5. Verify every finding (Claude, skeptical)

For each finding: open `file:line_start-line_end`, follow the scenario through the code, and run a
command that writes nothing when that settles it. Mark it:

- **confirmed**: the scenario happens as described;
- **plausible**: the code allows it but it depends on an input or state you could not confirm;
- **rejected**: the code does not do that (give the line that shows it).

Confidence below 0.5 needs a reproduction or it cannot be confirmed. A finding with no real file
or line is rejected outright.

## 6. Present

```
## Adversarial review: Codex (<model>, <effort>, read-only)   # or same-provider fallback (Claude)
**Verdict**: ship | needs-attention | no-ship, recomputed from the confirmed findings only
**Confirmed** (by severity): title · file:lines · scenario → what the user sees · recommendation · lenses
**Plausible**: same, plus what would settle it
**Rejected**: title · why (the line that shows it)
**Assumptions tested**: from `assumptions_challenged`
**Claude's own risks**: which Codex also found, which it missed
**Next step**: one line; offer to fix, never start
```

Verdict rule: any confirmed critical or high → `no-ship`; confirmed medium only → `needs-attention`;
nothing confirmed → `ship`, even if Codex said otherwise.
