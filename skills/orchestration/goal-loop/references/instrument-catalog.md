# Instrument Catalog — verification tools by problem class

"Working" is never observed directly; it is observed **through an instrument**, and every instrument
projects the goal onto what it can see. Reward hacking lives in the instruments' blind spots.
This catalog is what the factory consults in Phase 0.5 to *route, reuse, build, and calibrate* the
instruments that make a goal verifiable.

## Theory (what the 2024–2026 literature establishes)

- **Every verifier is a proxy for intent, never the intent** ("The Verification Horizon", Qwen, arXiv:2606.26300). Under optimization pressure the proxy–intent gap *widens* — reward hacking is a consequence, not a bug. The verifier must **co-evolve** with the implementer: when visible loss saturates or the judge finds gaming, upgrade the instruments, don't just iterate.
- **Three signal-quality dimensions — pick-two tension**: *scalability* (cheap at volume), *faithfulness* (how much of true intent it reflects), *robustness* (survives adversarial pressure). Unit tests: scalable+robust, thin intent. LLM judges: scalable+faithful, gameable. Humans: faithful+robust, unscalable. A verification *stack* covers what no single instrument can.
- **Combine weak verifiers** (Verifier Engineering, arXiv:2411.11504): PAC-style, several imperfect verifiers beat one. Verifiers classify by **form** (binary/score/rank/text) × **granularity** (token/step/trajectory) × **source** (program-based: deterministic, gameable by paraphrase; model-based: faithful, gameable by optimization). Rule of thumb: program-based for anything with explicit constraints; model-based only for what programs can't see; **trajectory monitoring** in addition to outcome checks.
- **Oracle families** (test-oracle literature; metamorphic surveys arXiv:2406.05397, 2605.13898) — when you lack the labeled "cat photo":
  1. **Specified/golden** — hand-curated (input, expected) pairs. Highest precision, costliest, and *label bugs are real* (our invoiceflow helper bug) → validate labels red-first.
  2. **Differential** — a reference implementation, an older version, or a second independent implementation as pseudo-oracle. Great when behavior must be preserved (refactors, migrations, ports).
  3. **Metamorphic** — invariants needing no ground truth: "voiding an invoice never increases balance", "adding then removing an item is identity", "clicking an expired link changes no counter". Unlimited checks without authoring labels; the strongest cheap defense for the compositional blind spot.
  4. **Judgment** — rubric/LLM/human. Last resort for the non-computable; always pair with a program-based instrument (judges are gameable).

## Phase 0.5 procedure (observability plan)

1. **Enumerate observables**: what must be *seen* for "done" to be believable — behaviors, compositions, qualities (latency, rendering, data integrity, side-effects in external systems).
2. **Route** each observable via the routing table below.
3. **Reuse**: inventory the repo/environment first — existing test framework, CI, CLIs, MCP servers, dashboards. An adequate existing instrument beats a new one.
4. **Build** what's missing, following the agent-native grammar (Plane 2). Generated instruments live in `loops/<slug>/tools/` and are archived for reuse.
5. **Calibrate before epoch 1**: every instrument must (a) run, (b) FAIL against the pre-implementation state or a known-bad sample (red-first), (c) pass against a known-good sample where one exists. An uncalibrated verifier is how label bugs reach the loop.

## Routing table: goal type → instrument stack

| Goal type | Primary loss (visible) | Held-out / anti-gaming | Judge aids |
|---|---|---|---|
| Backend / SWE task | Unit+integration tests (pytest/Vitest/go test/cargo) | Compositional e2e scenarios; metamorphic invariants; mutation score | Trajectory monitor; diff scan for oracle tampering |
| API service | Contract tests (Schemathesis, Pact, hurl) | Schema fuzzing on held-out ops; differential vs spec | 500s/undocumented codes under fuzz |
| Frontend / UI | Component tests + Playwright flows | Rubric judge on screenshots; **interactive agentic judge** operating the live app | axe-core, Lighthouse, visual diff |
| Performance goal | k6/Locust/vegeta scripted thresholds (p95, error rate) | Unannounced load shapes; soak runs; Prometheus/OTel metrics | Flamegraphs; resource ceilings |
| Refactor / migration / port | Existing suite must stay green | **Differential**: old vs new on generated inputs (Hypothesis/fast-check) | Coverage delta; mutation survivors |
| Data pipeline | Great Expectations / pandera / dbt tests | Metamorphic (row-count conservation, idempotent re-runs); Evidently drift | Sample-level spot audit |
| LLM / agent system | promptfoo / DeepEval / Inspect AI eval sets | Held-out eval split; Giskard red-team probes | Langfuse/Phoenix traces; judge panel |
| Security goal | Semgrep + Bandit/gitleaks in CI | Trivy/osv-scanner deps; ZAP/nuclei DAST on running app | Secret-scan of diffs |
| Docs / content | markdownlint + Vale; link checkers | LLM rubric vs style guide; rendered-output check | Reading-level metrics |
| Side-effects in external systems | Act via API/CLI, **read back via an independent channel** | Agent-native sensors (Plane 2) | Log/trace evidence (OTel, bslog) |

## Plane 1: Classic OSS instruments (leaders, mid-2026)

**Unit/integration**: pytest (Py) · Vitest (JS/TS, ESM-native) · go test+testify · cargo test.
**Property-based**: Hypothesis (Py) · fast-check (JS) · proptest (Rust) · rapid (Go) — invariant violations over generated input space, with shrinking. The engine behind metamorphic and differential checks.
**Mutation** (tests-of-the-tests): mutmut (Py) · Stryker (JS/C#) · cargo-mutants · PIT (JVM) — surviving mutants expose weak assertions; use to score a suite the implementer wrote.
**Fuzzing**: AFL++ · libFuzzer · Atheris (Py) · Jazzer (JVM/JS) — crashes/hangs/memory corruption.
**Snapshot/differential**: insta (Rust) · syrupy (Py) · Vitest snapshots — unintended output drift.
**Static analysis/types**: Ruff + mypy/Pyright (Py) · ESLint+typescript-eslint · clippy · staticcheck (Go) · Semgrep (30+ langs, custom rules — encode goal constraints as Semgrep rules).
**Coverage**: coverage.py · c8 · tarpaulin · `go test -cover` — what the loss *cannot* see.
**Concurrency**: TSan · `go test -race` · loom (Rust, exhaustive interleavings).
**E2E browser**: **Playwright** (leader: auto-wait, multi-browser, top stability) · Cypress · Selenium.
**API contract**: **Schemathesis** (property-based from OpenAPI/GraphQL) · Pact (consumer-driven) · hurl (declarative, CI-friendly) · Dredd.
**Load/perf**: **k6** (Grafana, K8s operator GA) · Locust (Py) · Gatling · vegeta/oha (quick CLI gates).
**Visual regression**: Playwright `toHaveScreenshot()` first · BackstopJS · Lost Pixel · reg-suit (PR-integrated).
**Accessibility**: axe-core (engine; ~57% of issues, zero false positives) · Pa11y (CI) · Lighthouse (audit incl. Core Web Vitals; also sitespeed.io for real-browser trending).
**Observability** (Better Stack 2026 defaults): OpenTelemetry (instrumentation standard) → Prometheus+Grafana (metrics/viz) · Jaeger v2 (traces) · Sentry self-hosted (errors) · Uptime Kuma (uptime).
**Chaos/resilience**: toxiproxy (network faults, lightest) · Chaos Mesh · LitmusChaos (K8s).
**Data quality**: Great Expectations · pandera (typed dataframe schemas) · dbt tests (SQL-native) · Soda Core; drift: Evidently · whylogs · Deepchecks.
**LLM eval**: promptfoo (CI-gated A/B) · DeepEval (pytest-style) · Ragas (RAG) · lm-eval-harness (benchmarks) · Giskard (red-team) · Inspect AI (UK AISI, agent/sandboxed).
**LLM observability/judging** (truly OSS): Langfuse (MIT) · Arize Phoenix (Apache-2, deepest agent traces) · OpenLLMetry. (Braintrust platform is proprietary.)
**Security**: Semgrep · Bandit · gitleaks (⚠ feature dev moved to Betterleaks 2026) + TruffleHog (verifies live creds) · Trivy/Grype/osv-scanner (deps/containers) · OWASP ZAP · nuclei (11k+ templates).
**Spec/prose**: jsonschema (Py) · Ajv (JS) · Vale (style) · markdownlint (structure).

## Plane 2: Agent-native instruments (the steipete pattern)

Small, local-first CLIs/MCPs that convert an agent-invisible domain into assertable artifacts.
Reference ecosystem: github.com/steipete.

- **Sensors**: Peekaboo (macOS screenshots/GUI), AXorcist (accessibility tree), sweetlink (Playwright in the *current* authenticated tab), camsnap (RTSP — physical world), songsee (audio→spectrogram), wacli/slacrawl/discrawl/telecrawl/imsg/gitcrawl (comms+repo history → SQLite/markdown), bslog (Better Stack logs from CLI), summarize (any URL/file → gist).
- **Actuator+sensor pairs**: gogcli (send email → query Gmail to confirm), remindctl, sonoscli, eightctl, vox. Verification pattern: **act through one channel, verify through an independent one**.
- **Harness instruments**: Crabbox (warm a box, sync diff, run suite — LOSS as a product), crabline (deterministic channel mocks — calibrated inputs), clawpatch (judge+patcher), Poltergeist (build-freshness watcher — continuous forward pass), VibeTunnel/tmuxwatch (observe agent runs — trajectory monitoring).

**Design grammar for factory-built instruments** (`loops/<slug>/tools/`):
single purpose · CLI-shaped with structured output (JSON/SQLite/markdown) · local-first ·
deterministic where possible (seeded, mockable) · exit code = verdict, stdout = evidence ·
always closes the act→observe loop · calibrated red-first before use.

## Plane 3: Verifier constructions (2026 practice, arXiv:2606.26300)

1. **Test verifier + behavior monitor** (SWE): execution-based suite for outcome, plus a trajectory monitor for *how* — Qwen cut hacked-resolved from 28.6%→0.6% only after adding both. Monitor for the 7 hacking behaviors: solution-artifact retrieval, external fix lookup, harness tampering, test-oracle tampering, visible-test overfitting, evaluator-aware patching, repository-history mining.
2. **Rubric static judge** (frontend/open-ended): decompose evaluation into a checklist (~25 items: functional/content/visual/layout/UX/technical); rubrics raise judge–human agreement and cross-judge consistency (Kendall τ ≥ 0.93).
3. **Interactive agentic judge**: judge *operates* the artifact (live browser, simulated user flows) — grounds reward in runtime behavior; resists the length/plausibility exploits static judges fall for.
4. **Checklist evaluator agent** (long-horizon): decompose the spec into verifiable requirements C = {c₁…cₙ}; report pass-rate + holistic score. Known judge failure modes: laziness (not opening files), leniency drift, halo effect — mitigate with explicit per-item evidence requirements.
5. **Visible/held-out split** (SpecBench, arXiv:2605.21384): implementer optimizes visible feature-level checks; judge alone runs held-out compositional checks; report the hacking gap.
6. **Agent-as-a-Judge** (arXiv:2601.05111): judge with tools and step-level access to the evaluand's artifacts, not just its final output.

## Plane 4: Agents as instruments (agentic tooling)

An agent with tools IS an instrument: form = text+evidence, source = model-based, granularity =
trajectory, cost high, gameable — so agentic instruments serve held-out measurement and judging,
never the visible loss. Like any instrument they declare blind spots and are **calibrated red-first**
(a user-simulator that can't fail on a deliberately broken artifact measures nothing). Archetypes:

- **Interactive agentic judge** — operates the artifact through its real interface (browser/CLI/API) and scores against the contract; grounds judgment in runtime behavior, not source reading.
- **Persona / user-simulator fleet** — N agents with distinct personas and *goals* ("find X in 30s", "complete task Y on mobile viewport"); the metric is task-success rate and friction notes. The scalable approximation of user-as-verifier.
- **Adversarial explorer (agentic monkey)** — hostile/random interaction under instruction: out-of-order flows, garbage input, boundary abuse, injection strings; hunts crashes, console errors, state corruption. Coverage-guided when paired with a sensor.
- **Interrogator** — quizzes the artifact against the ground-truth source, in both directions: facts that MUST be answered (completeness) and facts that MUST NOT exist (invention/hallucination — the blind spot of any content probe).
- **Trajectory monitor** — watches the *producer's* process, not its product: flags the hacking behaviors (oracle tampering, visible-test overfitting, artifact retrieval…) as they happen instead of post-hoc.
- **Judge panel with diverse lenses** — independent judges each confined to one rubric dimension or failure hypothesis; majority/veto aggregation. Diversity of lenses beats redundancy of identical judges.
- **Differential judge** — compares the artifact against a reference implementation, a previous epoch, or a competitor, and must articulate *which differences matter* relative to the contract.
- **Sensor substrate** — agentic instruments need eyes and hands: browser automation MCPs (page state, console, network), screenshot/GUI tools, accessibility-tree readers, log/trace readers. The substrate is program-based; the agent on top is the model-based part. Keep the split explicit — substrate output is evidence, agent output is judgment.

**Composition rule:** every agentic instrument = (program-based substrate → evidence) + (agent → judgment over that evidence) + (declared blind spots → hunted by another instrument). Program-based evidence always outranks the agent's judgment where both speak.

## Escalation ladder (co-evolution in practice)

When the judge finds gaming, or visible loss saturates while held-out fails, upgrade instruments in this order — each rung trades scalability for faithfulness:
static checks → unit tests → property/metamorphic → differential → interactive/e2e → chaos+load → rubric judge → interactive agentic judge → human review.
Record every upgrade in `loops/archive.md` — instrument evolution compounds across goals.
