# MVP frontend handoff prompt (per idea)

Use this inline prompt to hand off implementation of a single idea's MVP frontend to a coding agent. Pass the desktop and mobile mockup PNGs as image inputs alongside the prompt — the image-in-context is load-bearing for visual fidelity. The result should be one clean, deployable page per idea, not a sprawling app.

Substitute every `{placeholder}` from the idea's record (`id`, `title`, `accent`, `audience`, `promise`, `wedge`, `demoTitle`, `placeholder`, `output[]`, `cta`).

```
Build a clean MVP frontend for "{title}".

Stack (mandatory):
- Invoke the /frontend-design:frontend-design skill at the start to set
  the design language. Follow its output for layout, type scale, motion.
- Consult /vercel-react-best-practices for data fetching, server vs.
  client components, bundle/perf hygiene; and
  /vercel-composition-patterns for component API shape (compound
  components, render props, context). Apply both throughout.
- /web-design-guidelines for accessibility + UX audit before declaring
  done (focus states, contrast, semantic HTML, keyboard nav, motion
  reduction).
- Next.js (App Router) + React 19 + TypeScript. Default to Server
  Components; mark `"use client"` only on the demo block (interactive)
  and motion wrappers.
- Tailwind CSS for styling. shadcn/ui for primitives (Button, Input, Card,
  etc.) — install only the components used.
- motion (Framer Motion successor: `motion/react`) for tasteful entrance
  and interaction animations. Keep it subtle: opacity/translate/scale on
  mount, hover, and submit. No parallax, no scroll-jacking.

Inputs (attached as images):
- DESKTOP mockup: app/public/mockups/{id}/desktop.png
- MOBILE mockup:  app/public/mockups/{id}/mobile.png

Product brief:
- Audience: {audience}
- Promise:  {promise}
- Wedge:    {wedge}
- Primary CTA (verbatim): "{cta}"
- Accent color: {accent}

Scope (clean MVP — nothing more):
1. ONE Next.js route at /idea/{id} (App Router segment).
2. Hero: title "{title}", one-sentence promise, shadcn `Button` CTA "{cta}"
   tinted with accent {accent}. Animate hero in with motion (fade + 8px
   rise, 400ms, ease-out).
3. Live demo block titled "{demoTitle}":
   - shadcn `Input` with placeholder "{placeholder}" + submit Button.
   - Submit POSTs to /api/demo with {{ idea, input }}; render returned
     `lines[]` as shadcn `Card` items, animated in with stagger (motion
     `staggerChildren` ~60ms).
   - Loading state (skeleton or pulsing dots) + graceful fallback to the
     static `output[]` baseline on error.
4. Static results section showing the 4 baseline `output[]` cards (also
   the fallback above).
5. Footer with one mono line: "// {id}".

Visual fidelity:
- Match the desktop mockup at ≥1100px and the mobile mockup at <720px.
- Use the editorial-dossier tokens (Instrument Serif display, Instrument
  Sans body, JetBrains Mono labels, ink #0c0c0e, cream #f0e6d2). Wire
  these as Tailwind theme extensions or CSS variables consumed by the
  shadcn theme.
- Accent {accent} appears on the CTA, the input focus ring, and one
  hairline ornament. Nothing else.
- Motion: subtle, purposeful, ≤400ms per transition. Respect
  `prefers-reduced-motion`.

Build loop:
- Implement → diff against the mockup PNGs → fix discrepancies → repeat.
- Carefully match spacing, font sizes, layout regions, and copy length.

Verification (mandatory before declaring done):
- Run /web-design-guidelines against the implemented page (a11y,
  keyboard, contrast, motion-reduction).
- Run `npm run dev` and use the /agent-browser skill to:
  1. open http://localhost:3000/idea/{id} at 1440x900, screenshot,
     compare against desktop.png.
  2. resize to 390x844, screenshot, compare against mobile.png.
  3. exercise the demo input (type, submit, observe response + fallback).
- Iterate until both screenshots are visually close to the mockups.
- Then deploy via the standard rsync → jetson → vercel deploy flow and
  re-verify the production URL with /agent-browser at both viewports.

Out of scope (do NOT add):
- Auth, sign-up, billing, settings, multi-page nav.
- Marketing sections beyond the single hero + demo + 4 baseline cards.
- Backend changes — /api/demo already exists and is the only endpoint.
- Heavyweight animation (parallax, scroll-linked, Lottie). Keep it motion-only and tasteful.

Deliverable: one Next.js route wired at /idea/{id}, using shadcn primitives
+ Tailwind + motion, verified with /agent-browser at both viewports
locally and in production.
```

## Batch dispatch tip

To process all 28 ideas, render the template once per idea (substituting fields from `prototypes[]` in `app/src/App.tsx`) and fire 4–6 implementation agents in parallel via the `Agent` tool. Each agent owns its idea end-to-end: invoke `/frontend-design:frontend-design` → build with shadcn/Tailwind/motion → visual-diff with `/agent-browser` → deploy → re-verify. Ideas are independent — no shared state, no merge conflicts (each writes its own route segment).
