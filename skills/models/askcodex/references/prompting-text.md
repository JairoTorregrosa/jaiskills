# Text and code with askcodex

You are about to send one `askcodex ask` request for an answer, an analysis, an extraction, a
draft, code, or an independent review. Write a brief the model can act on without asking anything,
run it once, and check the answer before you use it. These are working heuristics; judge the
output against the task.

## Context you must respect

- The model sees only the prompt and `--instructions`. It has no access to the caller's
  repository, files, browsing session, or earlier conversation, and there is no follow-up turn: a
  clarifying question from the model ends the call without the deliverable.
- What you paste is sent to OpenAI. Always replace credentials, tokens, keys and passwords with
  placeholders. Remove personal or customer data the task does not need, and ask the user before
  sending any the task does need.
- A local path is not its contents. Paste the relevant text, or pipe a complete brief on stdin
  (UTF-8, at most 16 MiB; a client memory cap, not a context-window guarantee).
- `--json` structures the CLI envelope, not the model's answer. For an answer you will parse, pass
  `--schema FILE`: the backend then enforces that JSON Schema and `.result.json` holds the parsed
  answer. JSON you only asked for in the prompt is still text in `.result.text`; parse and validate
  it yourself.
- A model's claim that tests pass is not a test result. It ran nothing.

## Facts already verified (2026-10-02)

- `ask` defaults to `gpt-6.1-sol` at `medium`. Each model's guide lists its efforts and strengths;
  [prompting.md](prompting.md) indexes them. Check the live catalog with
  `askcodex models --no-refresh`.
- `--effort` takes `low`, `medium`, `high`, `xhigh`, `max`, or `none`. The catalog also lists
  `ultra`, which is Codex's multi-agent mode; the backend rejects it with HTTP 400. A level a model
  does not take also fails with HTTP 400 (`none` on `gpt-6-astra` and `gpt-6.1-sol`).
- askcodex sends no Codex system prompt. Without `--verbosity` the backend answers at `medium`
  verbosity; Codex sends `low`. On one prompt `--verbosity low` used 240 output tokens and `high`
  513 (observed 2026-10-02). It shapes length and detail; a hard cap still belongs in the brief.
- `--schema` is strict: every property must be in `required`, every object needs
  `"additionalProperties": false`, and an optional value adds `"null"` to its own type
  (`["string","null"]`, `["integer","null"]`, with `null` in any `enum`). A schema that breaks a
  rule fails before generation with `error.backend.code: "invalid_json_schema"` naming the key; it
  costs no answer. The backend enforced the schema even when the prompt asked for a haiku and "no
  JSON" (observed 2026-10-02).

## Do this

1. Pick the model and effort. Start from the model guide's effort table, not from habit:

   | Work | Start at, if the model takes it | Move up when |
   |---|---|---|
   | Short Q&A, classification, formatting | `low` | The answer misses a constraint or needs reasoning |
   | Summary, extraction, routine drafting | `medium` | Important evidence or relationships are missed |
   | Code review, debugging, multi-step analysis | `high` | One specific issue stays unresolved |
   | Difficult reasoning or a consequential review | `xhigh` | A concrete failure justifies a higher level |

   Change the model or the effort one at a time. Higher effort does not replace missing context.
2. Write the brief in labeled blocks with concrete acceptance criteria:

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

   Put durable instructions in `--instructions` and the task-specific material in the prompt. Keep
   the two consistent: conflicting length or format requirements waste the call. When a detail may
   be missing, tell the model to choose a reasonable default, state it in one line, and deliver;
   but when the conclusion depends on a fact (a decision, a verdict, a number), tell it to name the
   missing evidence and withhold the conclusion instead of assuming it.
3. Shape it to the deliverable:

   | Deliverable | Include | Ask for |
   |---|---|---|
   | Factual answer | The question, supplied evidence, a cutoff or context | A direct answer; evidence separated from uncertainty |
   | Summary | The full relevant source, audience, length | Main findings, decisions, exceptions, open points |
   | Structured extraction or classification | The source, field definitions, and `--schema FILE` | Identifiers preserved; null for missing values (the schema enforces keys and types) |
   | Code | Relevant code, runtime, interfaces, a failing example | A minimal change within scope and a validation plan |
   | Review | The code or proposal, intended behavior, constraints | Concrete defects with location, trigger, impact, fix; highest impact first; an empty list allowed |
   | Long analysis | Named source sections and the decision to make | Source-anchored conclusions, alternatives, missing evidence |
   | Creative writing | Audience, voice, purpose, examples, length | A complete draft in the requested register |

4. Run it. A short task:

   ```sh
   askcodex ask "Explain the tradeoffs between these two designs: [designs]. Give a recommendation and the assumptions it depends on." --model gpt-6.1-sol --effort high
   ```

   A prepared brief with a recoverable answer:

   ```sh
   mkdir -p /tmp/askcodex
   askcodex ask - --model gpt-6.1-sol --effort high --json < /tmp/askcodex/brief.txt > /tmp/askcodex/answer.json
   jq -r .result.text /tmp/askcodex/answer.json
   ```

   Write `brief.txt` with the actual inputs first. Run a call that may take minutes in the
   background or in tmux.

   An extraction you will parse:

   ```sh
   cat > /tmp/askcodex/ticket.schema.json <<'EOF'
   {"type": "object", "additionalProperties": false,
    "required": ["id", "product", "severity", "summary"],
    "properties": {
      "id": {"type": "string"},
      "product": {"type": ["string", "null"], "enum": ["app", "api", "billing", null]},
      "severity": {"type": ["integer", "null"], "enum": [1, 2, 3, null]},
      "summary": {"type": "string"}}}
   EOF
   echo "T-17: Checkout page crashes when I apply a coupon on iOS." |
     askcodex ask - --model gpt-6-luna --effort low --verbosity low \
       --schema /tmp/askcodex/ticket.schema.json --json > /tmp/askcodex/ticket.json
   jq .result.json /tmp/askcodex/ticket.json
   ```

   It returned `{"id":"T-17","product":"app","severity":2,"summary":"Checkout crashes on iOS when
   applying a coupon."}` (observed 2026-10-02). For several records, make the schema an object
   whose one property is an array of records. Check what a schema cannot express yourself, such
   as ids matching the input in order.
5. Check the answer against the acceptance criteria. For code, request real code or a diff, review
   it, apply it, and run the project's checks yourself. On a failure, read `error.backend` in the
   JSON diagnostic and follow the table in [SKILL.md](../SKILL.md) before you retry.

## Iterate

Read the first answer before you change the prompt. Name the precise failure, add the missing
context, and repeat the constraints that still apply. Include the relevant part of the previous
answer: every call must stand on its own. When comparing models, keep the brief and the criteria
fixed and compare correctness, completeness, format, and observed runtime. Stop when the
deliverable meets the criteria.

## Report

Tell the user the model and effort, where the answer was saved, what you verified, and any gap
between the answer and the brief.
