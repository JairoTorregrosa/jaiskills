---
name: second-opinion
description: >-
  GPT (GPT-6 Astra by default) as advisor, adversarial reviewer or judge through headless
  `codex exec`, always read-only; never an implementer. Modes: advise (independent read on a plan,
  diff or design, beside Claude's own view, with follow-ups), review (Codex's built-in reviewer on
  uncommitted work, a branch or a commit), adversarial (tries to break confidence in a change;
  optional parallel lenses; every finding verified by Claude before it is shown), judge (scores a
  reviewer's verdict for insistir and goal-loop). Trigger on "second opinion", "segunda opinión",
  "ask codex/GPT to review", "que codex lo revise", "revisión adversarial", "adversarial review",
  "que GPT ataque este cambio", "critica este plan", "challenge this design", "judge this review",
  "usa astra". Falls back to a Claude subagent, labelled same-provider, when Codex is unavailable.
  Not askcodex (one-shot text or images) and not for writing code.
argument-hint: "[advise|review|adversarial|judge] [--lenses a,b] [--provider claude] <question, plan, range or paths>"
---

# Second opinion

Request: $ARGUMENTS

Mode by first word: `review` → review mode · `adversarial` (or `challenge`) → adversarial mode ·
`judge` → judge mode · anything else (or `advise`) → advise mode. `--provider claude` anywhere in
the request → skip Codex, go straight to the fallback path and label the result
"same-provider (requested)".

**Codex advises, reviews and judges; it never implements.** Every call is read-only whatever the
user's Codex config says (it may set `danger-full-access`). Never ask Codex for a patch to apply,
never pass it a writable sandbox. Claude verifies what it reports and does any fixing.

Paths below are relative to this skill's directory, `${CLAUDE_SKILL_DIR}` (other harnesses: the
absolute path of the folder holding this SKILL.md). Shell state does not survive between Bash
calls: set `REPO` in the same call that runs the script.

## Transport (both modes)

Always `scripts/ask_codex.sh` (the Codex MCP server no longer exists: removed in codex-cli
0.154). Never hand-rolled `codex` flags. The script runs `codex exec --sandbox read-only
--skip-git-repo-check --ephemeral -C "$REPO" -o <out>/last-message.md -` (or `codex exec review`
with `sandbox_mode="read-only"`; `review` ignores `--output-schema`, openai/codex#38545), disables Codex memories so no unrelated session leaks in, ignores execpolicy `.rules`, lifecycle
hooks and the notify command (each can run outside the sandbox), pins `review_model` for native
review, checks
install and `codex login status` first, and enforces a timeout.

**Model and effort.** Default model `gpt-6-astra` when Codex's catalog
(`~/.codex/models_cache.json`) lists it, else the config default; `SECOND_OPINION_MODEL` or `-m`
overrides. Default effort `high` (`SECOND_OPINION_EFFORT` or `-e`; the user's config may default
to `low`). Use `xhigh` for adversarial reviews of risky changes; `max`/`ultra` only when asked.

```bash
REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd) && \
"${CLAUDE_SKILL_DIR}/scripts/ask_codex.sh" -C "$REPO" [--schema FILE] [-e high|xhigh] \
  [--keep-session] [--resume SESSION_ID|last] [--review uncommitted|base:REF|commit:SHA] \
  [-t 540] [-m MODEL] < prompt.md        # --review: < /dev/null (it takes no instructions)
```

- stdout (key=value): `out_dir`, `last_message`, `session_id`, `model`, `elapsed_s`.
  `out_dir` also holds `prompt.md` and `codex.log` (stderr, includes the session header).
- Exit 0 ok · 2 usage · **3 not installed · 4 not logged in · 5 timeout** → fallback now ·
  6 codex failed or empty answer → retry once, then fallback · 7 invalid JSON (judge) → retry once,
  then fallback.
- The Bash tool caps a call at 600000 ms: keep `-t` at or below its 540 s default and set the tool
  timeout to 600000 ms, or run it with `run_in_background` for long judges, so exit 5 reaches you
  instead of the tool's own kill. Any other exit (e.g. 127) → fallback. Measured on a one-file
  repo: codex-cli 0.156 + gpt-5.6-sol judge `-e high` 37 s, advise 35 s, `--resume` 10-12 s;
  codex-cli 0.157.1 + gpt-6-astra `-e high` native review 28 s, adversarial 44-51 s with two
  lenses running in parallel. Real repos take longer: for a diff over ~10 files, `-e xhigh`, or
  when the caller has other work, run with Bash `run_in_background: true` and `-t 1800`; the
  harness wakes you when it exits.

## Advise mode

1. **Material**, first match wins:
   1. Question, plan path, paths or git range given in the request → use them.
   2. A plan file the conversation is working from (e.g. `*-plan.md`, `plans/*.md`) → its path.
   3. Uncommitted changes → `git diff` (name the range; Codex can run it).
   4. Branch ahead of its base → `git diff <base>...HEAD`.
   5. Nothing → stop: "Nothing to review: give a question, a plan, or changes." Never call Codex
      with empty material.
   Prefer paths and ranges over pasted content: Codex reads the repo. Paste only what exists
   nowhere on disk; cap pasted material at ~12,000 characters.
2. **Own view first.** Before reading Codex's answer, write Claude's position in 3-6 bullets
   (verdict, top risks, recommendation). This keeps the comparison honest in both directions.
   Never put this view into the prompt.
3. Render [references/advise-prompt.md](references/advise-prompt.md) to a file and run:
   `ask_codex.sh -C "$REPO" --keep-session < prompt.md`. Keep `session_id`.
4. Read `last_message`. Before endorsing any Codex claim that changes the recommendation, open
   the cited file:line or rerun the cited command yourself. Mark each Codex point checked or
   unchecked.
5. Present:

   ```
   ## Second opinion: Codex (<model>, read-only)        # or: same-provider fallback (Claude)
   **Disagreements**
   - <topic>. Codex: … Claude: … Resolution: <who is right and the evidence, or what would settle it>
   **Agreed independently**: points both reached (strongest signal)
   **Only Codex raised**: each marked checked / unchecked
   **Only Claude raised**
   **Recommendation**: what to do next, one short paragraph
   ```

   No disagreements → say so in one line; do not invent any.
6. **Follow-ups** on the same topic: pipe the new question to
   `ask_codex.sh -C "$REPO" --resume <session_id> < followup.md` (the session keeps the earlier
   context and stays read-only). Resume by explicit `session_id`; `--resume last` picks the newest
   session in `$REPO` and races with any other Codex run there (parallel lenses included). Same presentation format.
   Unrelated question → new session.

## Review mode

Codex's built-in reviewer, the same one as `/review` inside Codex. Use it for "review my changes"
with no special framing; use adversarial mode when the question is whether the change should ship.

1. Target, first match wins: a commit SHA in the request → `commit:<sha>`; a base branch named →
   `base:<ref>`; uncommitted changes (`git status --porcelain` not empty) → `uncommitted`; branch
   ahead of its base → `base:<base>`; nothing → stop, "Nothing to review".
2. `ask_codex.sh -C "$REPO" --review <target> < /dev/null`. The built-in reviewer takes no
   instructions (Codex rejects a target plus a prompt): a request with a focus ("focus on
   migrations") goes to adversarial mode instead.
3. For each finding, open the cited lines and mark it confirmed or rejected (with the reason)
   before presenting. Present Codex's summary, then confirmed findings by priority, then rejected
   ones. Never start fixing: offer.

## Adversarial mode

Tries to break confidence in a change: failure modes, trust boundaries, data loss, races, and the
design assumptions the approach depends on. Findings are JSON forced by
[references/adversarial.schema.json](references/adversarial.schema.json). Read
[references/adversarial.md](references/adversarial.md) for the procedure: target and focus,
Claude's own view first, one run or 2-3 parallel lenses, merging, verifying every finding, and
the presentation.

## Judge mode

Scores a reviewer's verdict for insistir, goal-loop, or a user who asks to judge a review.

**Send only artifacts:**

| Input | Source |
|---|---|
| Task spec + acceptance criteria | plan task or goal contract |
| Diff (inline) or range + paths | `git diff <base>..<head> -- <files>` |
| Check results | reviewer `checks`, verifier evidence runs |
| Caller-specific checks | goal-loop: `agents/judge.md` body + held-out results; else `none` |
| Reviewer verdict | reviewer JSON, verbatim; goal-loop has no reviewer: pass `none` |

**Never send the implementer's reasoning, chain-of-thought, self-assessment or summary of what it
did.** The judge sees artifacts only; anything else anchors it.

Steps:

1. Empty diff → do not call; return "nothing to judge".
2. Render [references/judge-prompt.md](references/judge-prompt.md) and run:
   `ask_codex.sh -C "$REPO" --schema "${CLAUDE_SKILL_DIR}/references/verdict.schema.json" -e high < prompt.md`.
   `--output-schema` is honored (verified): the final message is one JSON object matching
   [references/verdict.schema.json](references/verdict.schema.json).
3. **Shape is forced, substance is not.** A schema-forced model answers even an empty or broken
   prompt with a well-formed, vacuous APPROVED (observed: all 5s, evidence "N/A"). Reject the
   verdict and rerun once if any criterion's `evidence` lacks a file:line, or if it is APPROVED
   while the check results show a failure. Second failure → fallback.
4. Recompute `score = 0.4*correctness + 0.2*spec_compliance + 0.2*security + 0.2*maintainability`
   from `criteria`; use the recomputed value. A `critical` finding is a correctness or security
   defect; a `major` finding is an unmet acceptance criterion (schema definition), so the work does
   not meet its contract whatever the score.
5. Gate:

   | Band | Condition | Action |
   |---|---|---|
   | Auto-approve | `verdict` APPROVED, score ≥ 4.0, no critical or major finding | judge confirms quality |
   | Auto-revise | score < 2.5, or any critical or major finding | fix now; findings become the fixer's input |
   | Middle | anything else (minor findings only, or 2.5 ≤ score < 4.0) | caller decides; the reviewer verdict is the tiebreaker |

   Reviewer vs judge:

   ```
   Reviewer APPROVED + judge auto-approve → APPROVED (consensus)
   Reviewer APPROVED + judge auto-revise  → REVISE with the judge findings
   Reviewer APPROVED + judge middle band  → APPROVED; judge findings go to the summary as follow-ups
   Reviewer REVISE   + judge any          → REVISE; union of reviewer and judge findings
   ```

   Callers without a reviewer (goal-loop) treat only auto-approve as a pass. Always return every
   finding, whatever the band: callers carry them into their summary.
6. Return to the caller: the verdict JSON, the recomputed score, the band, the provider label
   (`codex <model>` or `same-provider fallback (Claude)`), and `elapsed_s`.

**When the judge is worth its cost:** multi-file, cross-cutting or security-sensitive tasks; any
REVISE or borderline reviewer verdict; citation- or provenance-bearing docs (same-family reviewers
check coherence, not correspondence). Skip single-file or config edits the reviewer clearly
APPROVED with all checks green, and record `judge: skipped (trivial)`.

## Fallback: same-provider

Triggers: exit 3/4/5, a second exit 6/7, a second vacuous verdict, or `--provider claude`.

1. Tell the user which case happened (e.g. "codex not logged in: run `codex login`").
2. Spawn a fresh subagent (Agent tool; a read-only type such as `Explore` when available, else
   `general-purpose`) with the rendered prompt verbatim. It has no sandbox: tell it to modify
   nothing and run only commands that write nothing (observed: running Python left
   `__pycache__/` behind; set `PYTHONDONTWRITEBYTECODE=1`). Judge mode: add
   "Reply with only the JSON object; it must match `references/verdict.schema.json`" and give the
   schema's absolute path. Validate and gate exactly as above.
3. Judge mode: if the fallback's verdict also fails step 3 (evidence without file:line, or
   APPROVED against failing checks), return `judge: unavailable` with the reason; never gate on it.
4. Label every output `same-provider fallback (Claude)`. It still gates, but callers must report
   it as such: it loses the cross-provider independence the judge exists for.
5. Never fail the caller's pipeline because Codex is unavailable, and never present a fallback
   answer as Codex's.

## Why a different provider

Models rate their own family's output higher than warranted; a model with different training
data and reward models has different blind spots. Cross-model judging separates good from bad
work better than same-model judging ("Judging the Judges", arXiv 2604.23178). But unverified
cross-provider findings hurt: Codex reviewing Claude's drafts without running anything lowered the
pass rate from 91.4% to 82.8% (arXiv 2607.21656). That is why every finding is verified before it
is shown and nothing is auto-applied.
