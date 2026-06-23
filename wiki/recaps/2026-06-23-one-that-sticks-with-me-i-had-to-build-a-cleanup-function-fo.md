---
type: recap
title: "Recap — The Groq outage: a cleanup function with no fallback"
created: 2026-06-23
updated: 2026-06-23
status: stable
sources: [2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]
tags: [llm, reliability, incident, war-story, fallback]
---

# Recap — The Groq outage: a cleanup function with no fallback

A first-person engineering **war story**. The author built a text-cleanup function to
improve note-writing quality, backed by a single model on the **[[entities/groq]]** API.
Confident in the implementation, they didn't think through edge cases — in particular,
what happens when the provider goes down. One night the Groq model became unavailable
and **[[entities/sentry]]** alerts flooded in; with no fallback in place, users were
affected. The author patched it immediately by adding a second model as a fallback, then
the next morning migrated to **[[entities/openrouter]]** for ongoing model redundancy
[2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo].

## Key claims

- A text-cleanup function for note inputs was built on a **single model via the Groq
  API**, with no fallback strategy
  [2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo].
- The author was confident and **did not think through edge cases** — notably provider
  downtime [2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo].
- The model went down overnight; **Sentry alerts** surfaced the incident and **users
  were affected** [2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo].
- Immediate fix: **add a second model as a fallback**. Durable fix: **migrate to
  OpenRouter** for model redundancy
  [2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo].

## Lesson

A single-provider LLM dependency is a single point of failure. The takeaway is an
[[concepts/llm-fallback-strategy]]: provision a fallback model (or a routing gateway that
provides one) *before* shipping, not after the pager goes off.

## Entities mentioned

- [[entities/groq]], [[entities/openrouter]], [[entities/sentry]]

## Concepts mentioned

- [[concepts/llm-fallback-strategy]]

## Source

`sources/2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo.md`
