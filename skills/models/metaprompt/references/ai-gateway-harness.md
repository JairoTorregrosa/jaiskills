---
title: "Vercel AI Gateway Harness Deep Dive"
last_verified: 2026-07-18
sources_verified: true
---

> **Verification note** — Every section was researched against live documentation and community threads on 2026-07-18. Source URLs are listed at the end of each section.

# Vercel AI Gateway Harness Deep Dive

AI Gateway is not an agent — it is a unified API proxy (`https://ai-gateway.vercel.sh`) over 200+ models from 20+ providers, used as the *model backend* for coding agents and frameworks (eve, Codex CLI, Claude Code, opencode, Cline, Roo Code…). A metaprompt "targeting AI Gateway" is really targeting whatever client runs on top of it; this guide covers the gateway-level knobs a prompt/config should exploit and the subscription-auth reality.

Compatibility layers: AI SDK v5/v6 (native default provider), OpenAI Chat Completions (`/v1`), OpenAI Responses API, and the Anthropic Messages API. Pricing: prepaid AI Gateway Credits at provider list price with **zero markup**; free tier has a model subset and lower rate limits.

Source: https://vercel.com/docs/ai-gateway
Source: https://vercel.com/docs/ai-gateway/pricing

---

## 1. Model slugs and routing controls

Models are addressed as `creator/model-name`: `anthropic/claude-opus-4.8`, `openai/gpt-5.5`, `xai/grok-4.3`, `google/gemini-3.1-flash-lite-preview`. With the AI SDK, a plain string model ID auto-routes to the gateway and reads `AI_GATEWAY_API_KEY`.

Routing knobs via `providerOptions.gateway`:

```typescript
providerOptions: {
  gateway: {
    order: ['vertex', 'anthropic'],   // provider try order
    only: ['anthropic', 'vertex'],    // restrict providers
    sort: 'cost',                     // or 'ttft', 'tps'
    models: ['openai/gpt-5.4-nano'],  // fallback model chain
    caching: 'auto',                  // auto prompt-cache strategy
    zeroDataRetention: true,
    user: 'user-123', tags: ['feature:summary'],
  }
}
```

Prompt caching: Anthropic `cache_control` passes through to Anthropic/Vertex/Bedrock; `caching: 'auto'` applies a per-provider strategy; the Responses API adds `cache_anchor_items`/`cache_ttl`. Model discovery: `gateway.getAvailableModels()` or unauthenticated `GET /v1/models`.

Source: https://ai-sdk.dev/providers/ai-sdk-providers/ai-gateway
Source: https://vercel.com/docs/ai-gateway/models-and-providers/provider-options

---

## 2. Auth: API keys, OIDC, BYOK

- **API key** (`AI_GATEWAY_API_KEY`): dashboard-generated, works anywhere, per-key budget caps.
- **OIDC**: automatic `VERCEL_OIDC_TOKEN` on Vercel deployments; API key wins if both present.
- **BYOK**: attach your own provider API keys (team-level or per-request `providerOptions.gateway.byok`). Zero markup, but requires the paid tier, and **if your BYOK key fails the gateway silently retries on system credentials and bills your credits**. BYOK accepts API keys / service-account credentials only — **there is no field for consumer-subscription OAuth tokens**.

Source: https://vercel.com/docs/ai-gateway/authentication-and-byok
Source: https://vercel.com/docs/ai-gateway/authentication-and-byok/byok

---

## 3. Subscription reality (Claude Pro/Max, ChatGPT Plus/Pro)

**AI Gateway is fundamentally an API-key-billing product.** The subscription picture:

| Subscription | Through the gateway? | Mechanism | Reliability / ToS |
|---|---|---|---|
| Claude Max via **Claude Code** | Yes (special case) | Dual-header pass-through proxy | Fragile; ToS gray area |
| Claude Pro/Max via any other client | No | — | Feb 2026 ToS forbids it |
| ChatGPT Plus/Pro | No | No pass-through mechanism exists | — |
| Any sub via BYOK | No | BYOK is API-key only | — |

**Claude Max pass-through (Claude Code only):**

```bash
export ANTHROPIC_BASE_URL="https://ai-gateway.vercel.sh"
export ANTHROPIC_CUSTOM_HEADERS="x-ai-gateway-api-key: Bearer <ai-gateway-key>"
# then `claude`, login with "Claude account with subscription"
```

Claude Code's own OAuth `Authorization` header passes through to Anthropic (subscription billing); the `x-ai-gateway-api-key` header authenticates the gateway for routing/observability. Caveats:

- Community reports of the pass-through **silently failing over to gateway credits** (losses from $15/hour to ~$1,200 over two weeks); adding custom headers has flipped billing modes without warning.
- Anthropic's Feb 20, 2026 consumer ToS restricts Pro/Max OAuth tokens to first-party tools (Claude Code, claude.ai), with enforcement live since April 2026. Vercel's position is that Claude Code remains the client and the gateway is transparent infrastructure — it works today, but the ToS language is broad enough to cover it.

**ChatGPT subscriptions:** Vercel's Codex integration uses `AI_GATEWAY_API_KEY` (API billing) only — Vercel AI Gateway documents no ChatGPT-subscription pass-through. OpenAI does offer ChatGPT-plan OAuth for some tools (e.g. Roo Code, Codex CLI natively), but those flows connect *directly* to OpenAI, not through this gateway.

Source: https://vercel.com/docs/ai-gateway/coding-agents/claude-code
Source: https://vercel.com/changelog/claude-code-max-via-ai-gateway-available-now-for-claude-code
Source: https://community.vercel.com/t/vercel-ai-gateway-billing-credits-instead-of-claude-max-subscription-pass-through-in-claude-code/37001
Source: https://winbuzzer.com/2026/02/19/anthropic-bans-claude-subscription-oauth-in-third-party-apps-xcxwbn/
Source: https://vercel.com/docs/ai-gateway/coding-agents/openai-codex
Source: https://docs.roocode.com/providers/openai-chatgpt-plus-pro

---

## 4. Gateway as backend for coding agents

`vercel ai-gateway coding-agents setup` auto-detects installed agents and writes config. Manual setups:

**Claude Code (API-key billing — the reliable path):**

```bash
export ANTHROPIC_BASE_URL="https://ai-gateway.vercel.sh"
export ANTHROPIC_AUTH_TOKEN="<ai-gateway-key>"
export ANTHROPIC_API_KEY=""   # mandatory — Claude Code checks this first and it silently wins
```

Bedrock/Vertex routing needs `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` (they reject `anthropic-beta` headers). Provider routing from CLI: `CLAUDE_CODE_EXTRA_BODY='{"providerOptions":{"gateway":{"only":["bedrock"]}}}'`. The Claude Agent SDK inherits the same `ANTHROPIC_*` env vars.

**Codex CLI:**

```toml
# ~/.codex/config.toml
model_provider = "vercel"
model = "openai/gpt-5.5"

[model_providers.vercel]
name = "Vercel AI Gateway"
base_url = "https://ai-gateway.vercel.sh/v1"
env_key = "AI_GATEWAY_API_KEY"
# supports_websockets = true  (OpenAI models only)
```

Model switching via profile files (v0.134.0+ requires separate `~/.codex/<name>.config.toml`, not `[profiles.*]` tables): `codex --profile claude` with `model = "anthropic/claude-sonnet-4.6"`. Expect ignorable "model metadata not found" warnings on non-OpenAI models.

**opencode**: `/connect` → "Vercel AI Gateway" → paste key (auto-discovers models). Also documented: Cline, Roo Code, Conductor, Blackbox, Crush, Grok Build, Superset. **Not documented**: pi, amp, eve-as-client (eve consumes the gateway natively as a framework — see `eve-harness.md`).

Source: https://vercel.com/docs/ai-gateway/coding-agents
Source: https://vercel.com/docs/ai-gateway/coding-agents/openai-codex

---

## 5. Gotchas

- Free-tier monthly credits stop once you buy paid credits; full model catalog requires paid.
- BYOK fallback billing trap (section 2) — keep a credit floor even on BYOK.
- Claude Max pass-through can silently revert to credit billing; watch the spend dashboard.
- WebSocket streaming is OpenAI-models-only.
- `ANTHROPIC_API_KEY=""` is mandatory alongside `ANTHROPIC_AUTH_TOKEN`.

Source: https://vercel.com/docs/ai-gateway/pricing
Source: https://community.vercel.com/t/does-ai-gateway-still-work-with-claude-max-key/42203

---

## 6. Cloudflare AI Gateway (brief comparison)

Cloudflare's gateway is a proxy/cache layer over calls you already bill directly (BYOK, header-based): core features free, edge response caching, retries + model fallback, cost budgets (June 2026), but no coding-agent-specific docs and no subscription pass-through. For a solo dev routing coding agents, Vercel's gateway is the better-documented choice; Cloudflare fits teams already on Workers wanting edge caching/rate limiting.

Source: https://developers.cloudflare.com/ai-gateway/reference/pricing/
Source: https://developers.cloudflare.com/ai-gateway/features/
