# Advise prompt template

Render by replacing each `{{PLACEHOLDER}}`, write to a file, pipe it to `scripts/ask_codex.sh`.
Put paths and git ranges in `{{MATERIAL}}` when the content is on disk (Codex reads the repo
itself); paste only content that exists nowhere else (a plan still in the conversation). Keep
pasted material under ~12,000 characters. Never paste Claude's own opinion into this prompt.

---

You are giving an independent second opinion on work produced with a different AI model. You
have read-only access to the repository in your working directory: open files and run read-only
commands (`git log`, `git diff`, `rg`, tests that write nothing) to check claims instead of
assuming them. Do not modify anything.

Be direct. Disagree where the evidence supports it. No praise, no restating what the work does.

## Question

{{QUESTION}}

## Material

{{MATERIAL}}

## Answer in this shape

1. **Verdict**: one line, one of sound / sound with changes / unsound.
2. **Risks**: the 2-4 riskiest assumptions or decisions. For each: what breaks, for which input
   or sequence of actions, the evidence (file:line or quoted text), and the alternative.
3. **Missing**: what should have been considered and was not.
4. **Unverified**: claims you could not check, and why.
5. **Confidence**: high / medium / low, with one sentence of why.
