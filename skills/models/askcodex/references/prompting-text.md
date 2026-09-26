# Text and code with askcodex

Use `askcodex ask` for a focused answer, analysis, extraction, draft, code
generation, or an independent review. These recipes are working heuristics;
evaluate the output against the task.

## Choose the model and effort

Read `askcodex models --json --no-refresh` when selecting a model. Choose from
the returned `.result.models` catalog and check that model's supported efforts.
The installed CLI defaults to `gpt-5.6-sol` at `medium`; pin the choice when
comparing outputs or when reproducibility matters.

| Work | Starting effort, if supported | Escalate when |
|---|---|---|
| Short Q&A, classification, formatting | low | The response misses a constraint or needs deeper reasoning |
| Summarization, extraction, routine drafting | medium | Important evidence or relationships are missed |
| Code review, debugging, multi-step analysis | high | A specific unresolved issue needs further analysis |
| Difficult reasoning or a consequential review | xhigh | A concrete failure justifies testing a higher supported level |

Use a faster model for straightforward transformations and a more capable
model when the task depends on difficult reasoning. Judge that choice on a
representative input. Change model or effort one at a time; do not assume
higher effort fixes missing context.

## Build the brief

Use labeled blocks and concrete acceptance criteria:

```text
Task:
Produce [deliverable] for [audience and purpose].

Context:
[Relevant facts, source text, code, or examples.]

Constraints:
[Scope, requirements, exclusions, and what must remain unchanged.]

Output:
[Structure, length, schema, or required files.]

Verification:
Check [specific requirements]. Identify missing evidence and assumptions.
```

Put durable instructions in `--instructions`; put task-specific source material
and the request in the prompt. Align the two: conflicting length or format
requirements waste the call.

A local file path is not a substitute for its contents. Include the relevant
text or pipe a complete brief to stdin (UTF-8, at most 16 MiB). This is a
client memory cap, not a model context-window guarantee.
Do not assume this command has access
to the caller's repository, browsing session, or prior conversation.

## Run a request

For a short task:

```sh
askcodex ask "Explain the tradeoffs between these two designs: [designs]. Give a recommendation and the assumptions it depends on." --model gpt-5.6-sol --effort high
```

For a prepared brief and a recoverable answer:

```sh
mkdir -p /tmp/askcodex
askcodex ask - --model gpt-5.6-sol --effort high --json < /tmp/askcodex/brief.txt > /tmp/askcodex/answer.json
jq -r .result.text /tmp/askcodex/answer.json
```

Create `brief.txt` with the actual inputs first. Check that the selected model
is available. Queue the invocation or use tmux when it may take minutes.

## Adapt the prompt to the deliverable

| Deliverable | Include | Request |
|---|---|---|
| Factual answer | Question, supplied evidence, required cutoff or context | Direct answer; distinguish evidence from uncertainty |
| Summary | Full relevant source, audience, desired length | Main findings, decisions, exceptions, and unresolved points |
| Structured extraction | Source, exact schema, field definitions | Preserve identifiers; use null for missing values; no extra keys |
| Code | Relevant code, runtime, interfaces, failure example | Minimal implementation within scope and a validation plan |
| Review | Code or proposal, intended behavior, known constraints | Concrete defects with locations, triggers, impact, and fixes |
| Long analysis | Named source sections and the decision to make | Source-anchored conclusions, alternatives, and missing evidence |
| Creative writing | Audience, voice, purpose, examples, length | A complete draft in the requested register |

For extraction, `--json` structures the CLI envelope, not the model's answer.
The requested JSON is still text in `.result.text`; parse and validate it separately.

For coding, request actual code or a diff when that is the deliverable.
A model's claim that tests pass is not a test result. Run appropriate checks
in the target project after reviewing and applying the output.

For reviews, ask for the highest-impact findings first. Require enough evidence
to reproduce each finding and permit an empty findings list.

## Iterate with evidence

Read the first answer before changing the prompt. State the precise failure,
supply any missing context, and repeat the constraints that still apply.
Include the relevant prior answer in the next request; each invocation should
be understandable on its own.

When comparing models, keep the brief and acceptance criteria fixed. Compare
correctness, completeness, format, and observed runtime on the same task.
Stop when the deliverable meets the criteria.
