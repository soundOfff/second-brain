---
type: concept
title: LLM Fallback Strategy
created: 2026-06-23
updated: 2026-06-23
status: active
sources: [2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]
tags: [llm, reliability, resilience, fallback, redundancy]
aliases: [model fallback, model redundancy, provider redundancy]
---

# LLM Fallback Strategy

A **fallback strategy** is the plan for what an LLM-backed feature does when its primary
model or provider is unavailable. A single model behind a single provider is a **single
point of failure**: if that provider has an outage, every request fails.

The pattern, in increasing robustness:

1. **Single model, no fallback** — simplest, but the feature dies with the provider.
2. **Secondary model as fallback** — on error/timeout, retry against a different model
   (ideally a different provider) so the feature degrades instead of failing.
3. **Routing gateway** — front all calls with a service like **[[entities/openrouter]]**
   that provides **model redundancy** across providers behind one API, so failover is
   handled for you rather than hand-rolled.

## Why it matters — a concrete failure

This concept is grounded in a real incident: a note-cleanup feature shipped on a single
**[[entities/groq]]** model with no fallback. When Groq went down overnight,
**[[entities/sentry]]** alerts flooded in and users were affected. The fix was exactly
the ladder above — a second model added immediately, then a migration to OpenRouter for
durable redundancy
[2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]. See the full
story in [[recaps/2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]].

## Practical guidance

- Decide the fallback **before shipping**, not after the first outage — provider downtime
  is a foreseeable edge case, not a black swan.
- Prefer a fallback on a **different provider**, since same-provider models share the
  failure domain.
- Pair fallback with **monitoring** (e.g. Sentry) so you learn about degradation from a
  dashboard, not from users.
