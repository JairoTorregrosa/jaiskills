# Worked example — "Landing page: my CV as an OS"

End-to-end trace of the factory processing one goal, chosen because it exercises the *frontend*
row of the instrument catalog (rubric + interactive judging) — the opposite regime from
API/test-driven goals. Identity data is placeholder; swap in the real CV at intake.

**Goal (user words):** "una landing page con mi CV as a OS" — a single-page site that presents
the CV as a desktop operating system: boot screen, desktop icons, draggable windows, taskbar,
and a terminal that answers commands about me.

---

## Phase 0 — Intake → goal contract

**Interview outcomes (what the lead extracts/asks):**
- Metaphor scope: boot → desktop; icons open windows (About, Experience, Projects, Skills, Contact); taskbar shows open windows; terminal app with `help`, `whoami`, `experience`, `contact`.
- **Ground truth**: all CV facts live in ONE machine-readable file, `cv.json` — the "labeled cat photo". Every rendered fact must trace to it. (This turns "content is correct" from judgment into a program-decidable check.)
- Stack: static site, no backend; Playwright-testable; runs from `npx serve`.
- **Agentic surface**: the artifact's future visitors include agents (a recruiter's assistant interrogating the CV). `cv.json` is served machine-readable, and one observable is *agent legibility*: an interrogator agent must extract every CV fact correctly through the public surface — the measuring instrument and the future consumer are the same entity.

**Contract highlights (`loops/cv-os/loop.md`):**

| Aspect | Decision |
|---|---|
| End state | Site boots to desktop; 5 apps function; terminal answers 4 commands; all content from cv.json; keyboard accessible |
| Visible evidence | 1. `npx playwright test tests/visible/` exits 0 (feature-level: each window opens/closes, taskbar updates, each terminal command returns non-empty) · 2. `node tools/cv-content-probe.mjs --mode visible` exits 0 |
| Constraints | No content hardcoded in JS/HTML that exists in cv.json; no test modification; no external network calls at runtime |
| Budget | max_epochs 4, patience 2, edit_scope broad |

**Held-out (`loops/cv-os/heldout.md` — judge-only):**
1. `npx playwright test .heldout/cv-os/` — compositional flows: open 3 windows → drag → minimize one → focus order correct; open Experience from BOTH icon and terminal → single window instance, not duplicates; close all → taskbar empty; boot skip on reload.
2. `node tools/cv-content-probe.mjs --mode deep` — every leaf value in cv.json appears rendered somewhere reachable; every date/title exact.
3. `npx playwright test .heldout/cv-os/a11y.spec.ts` — axe-core: zero critical violations; full keyboard traversal of icons and window controls.
4. Lighthouse: performance ≥ 85, accessibility ≥ 90 on mobile emulation.

## Phase 0.5 — Observability plan

**Observables enumerated:** window lifecycle behavior · window composition (focus/z-order/instances) · content fidelity vs cv.json · terminal semantics · keyboard accessibility · visual quality (subjective) · load performance.

**Gap analysis → acquisition ladder:**

| Observable | Instrument | Rung |
|---|---|---|
| Window/terminal behavior | Playwright | reuse |
| Accessibility | axe-core via @axe-core/playwright | configure |
| Performance | Lighthouse CI | configure |
| Content fidelity | — none exists — | **generate** |
| Visual quality | rubric judge on screenshots + interactive agentic judge | model-based (judge aid, never loss) |

**Generated instrument** (`tools/cv-content-probe.mjs`) — interface declared before code:
- *Contract:* input `--mode visible|deep`, reads `cv.json` + rendered DOM (Playwright); output JSON `{missing: [], mismatched: [], checked: n}`; exit 0 iff both arrays empty. Declared blind spots: cannot judge layout/beauty; cannot detect *extra* invented facts absent from cv.json (registered — the judge probes this).
- *Calibration (red-first):* run against a stub page with one wrong date and one missing project → MUST exit non-zero listing exactly those two; run against a hand-built known-good fragment → MUST exit 0. Both runs logged in `loop.md` before epoch 1.
- *Amortization:* reused every epoch by verifier AND judge, plus any future CV goal → asset, promoted to archive at close.

## Phase 1 — Agent factory (specializations that matter)

- **implementer.md**: desktop-metaphor conventions (single window manager owning z-order/focus state; windows as instances of one component, never per-app copies); ALL content read from cv.json at runtime; hidden compositional checks exist — build real state management, not per-test behaviors.
- **diagnoser.md** seeded with the frontend failure taxonomy: z-index/focus-order bugs, state leakage between window instances, event-listener leaks on close, duplicated-singleton windows, CSS breakpoint gaps.
- **judge.md**: interactive agentic judge — *operates* the page (opens/drags/minimizes via browser tools) rather than reading code; rubric scored on functional/content/visual/layout/UX; hunts this goal's specific hack: **content hardcoded to satisfy the probe's visible mode while diverging from cv.json elsewhere**, and invented facts (the probe's declared blind spot).

## Phase 2 — Descent (illustrative epochs)

**Epoch 1.** Implementer ships boot+desktop+windows+terminal. Visible: 11/12 (terminal `contact` empty). Held-out (verifier-run): duplicate-window flow FAILS — opening Experience from icon then terminal yields two windows. Diagnoser gradient: *"window creation is call-site-owned; no registry enforcing instance singularity — centralize open() in the window manager"* + contrastive: *"drag/focus logic is sound — preserve"*. Held-out direction (abstracted, no test details): *"opening the same app through different entry points must converge on one instance."* Momentum: `call-site-owned window creation (1, open)`.

**Epoch 2.** Fresh implementer, given gradient log. Visible 12/12. Held-out: all pass except a11y — icons unreachable by Tab (div, not button). Gradient: *"interactive elements built from non-interactive primitives — semantic roles missing as a class."* Momentum adds `non-semantic interactive elements (1, open)`.

**Epoch 3.** Visible 12/12, held-out 4/4, probe deep-mode 0 missing / 0 mismatched. **Judge** (interactive): operates the page, confirms flows, probes blind spots — greps bundle for cv.json string literals (hardcoding check: none), quizzes terminal for a fact NOT in cv.json (invention check: correctly absent). Verdict: `{"met": true, "hacking_gap": 0, "reason": "..."}`.

## Phase 3 — Close

- Report: MET in 3 epochs; gap 0; evidence table green; probe promoted.
- Archive entry: *frontend/desktop-metaphor* domain — window-manager-singleton pattern worth pre-seeding; `cv-content-probe` reusable for any content-fidelity goal (pattern: **single source of truth file + DOM probe = ground-truth oracle for content sites**); judge blind-spot probing (bundle grep + invention quiz) caught nothing this time but stays in the template.

---

**Why this example earns its place:** the loss is mostly *behavioral and aesthetic* — the regime
where tests alone are thinnest — so it shows the full stack working together: program-based
instruments for everything decidable (behavior, content via ground-truth file, a11y, perf),
a generated+calibrated instrument closing the content blind spot, and the model-based judge
confined to exactly what programs cannot decide (visual quality, invention), with its own
blind-spot list to hunt.
