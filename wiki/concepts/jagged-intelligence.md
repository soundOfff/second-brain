---
type: concept
title: Jagged Intelligence
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-2025-llm-year-in-review, 2026-06-24-sequoia-ascent-2026-summary]
tags: [llm, ai, capabilities, mental-model]
aliases: [jaggedness, jagged capability]
---

# Jagged Intelligence

The observation that LLM capability is **spiky**, not smooth: a model can be a "genius
polymath" in one moment and a "confused and cognitively challenged grade schooler" the
next — "seconds away from getting tricked by a jailbreak"
[2026-06-24-2025-llm-year-in-review]. [[entities/andrej-karpathy]] internalized this
"shape" of LLM intelligence in 2025 [2026-06-24-2025-llm-year-in-review].

## Why it happens

LLMs "spike" in capability in the vicinity of **verifiable domains** that receive
reinforcement learning, and stagnate where things fall outside that space — a direct
consequence of [[concepts/verifiability]] and
[[concepts/reinforcement-learning-from-verifiable-rewards]]
[2026-06-24-2025-llm-year-in-review][2026-06-24-sequoia-ascent-2026-summary].

Capability is not only about whether a task is verifiable but also whether labs
emphasized it in training:

> capability spike ≈ verifiability × training attention × data coverage × economic value
> [2026-06-24-sequoia-ascent-2026-summary]

So models "have no manual" — they are artifacts of pretraining mixtures, RL
environments, benchmark pressure, and economic incentives
[2026-06-24-sequoia-ascent-2026-summary].

## Canonical examples

- "How many letters are in *strawberry*?" — long famously wrong, now patched
  [2026-06-24-sequoia-ascent-2026-summary].
- The newer one: a model that can refactor a 100,000-line codebase or find zero-day
  vulnerabilities may still tell you to **walk** 50 meters to the car wash instead of
  drive [2026-06-24-sequoia-ascent-2026-summary].

## Why it matters

Because models stay jagged, **you must stay in the loop** — treat them as tools, learn
where they work and fail empirically, and build guardrails. This is the practical reason
behind [[concepts/agentic-engineering]] and connects to the
[[concepts/ghosts-vs-animals]] mental model [2026-06-24-sequoia-ascent-2026-summary].
Note: human intelligence is also jagged in its own way
[2026-06-24-2025-llm-year-in-review].
