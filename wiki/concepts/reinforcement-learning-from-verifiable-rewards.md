---
type: concept
title: Reinforcement Learning from Verifiable Rewards (RLVR)
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-2025-llm-year-in-review, 2026-06-24-sequoia-ascent-2026-summary]
tags: [llm, training, reinforcement-learning, reasoning]
aliases: [RLVR]
---

# Reinforcement Learning from Verifiable Rewards (RLVR)

A training stage in which an LLM is optimized against **automatically verifiable
reward functions** (e.g. math and code puzzles where answers can be checked) rather than
against human preference labels. [[entities/andrej-karpathy]] frames it as the de-facto
**new major stage** added in 2025 on top of the prior stable recipe — pretraining → SFT
→ RLHF [2026-06-24-2025-llm-year-in-review].

## Why it mattered in 2025

- Trained against **objective, non-gameable** rewards, RLVR allows much **longer
  optimization** than the thin SFT/RLHF finetunes, and it offered high **capability per
  dollar** — so it "gobbled up" compute originally intended for pretraining. The result:
  ~similar-sized models but much longer RL runs [2026-06-24-2025-llm-year-in-review].
- Models **spontaneously develop strategies that look like "reasoning"** — breaking
  problems into intermediate steps and backtracking — because the optimal traces aren't
  known in advance and must be found via optimization (Karpathy cites the DeepSeek R1
  paper as an example) [2026-06-24-2025-llm-year-in-review].
- It introduced a **new test-time-compute scaling knob** ("thinking time"): generate
  longer reasoning traces for more capability [2026-06-24-2025-llm-year-in-review].
- **OpenAI o1** (late 2024) was the first RLVR demonstration; **o3** (early 2025) was
  the felt inflection point [2026-06-24-2025-llm-year-in-review]. See [[entities/openai]].

## Relationship to verifiability and jaggedness

RLVR is the *mechanism* behind the [[concepts/verifiability]] thesis ("LLMs automate
what you can verify") and the cause of [[concepts/jagged-intelligence]]: capability
"spikes" in the verifiable domains that get RL environments, and stays rough elsewhere
[2026-06-24-2025-llm-year-in-review][2026-06-24-sequoia-ascent-2026-summary]. It also
undermines benchmarks, which are themselves verifiable environments and thus directly
susceptible to RLVR — "training on the test set is a new art form"
[2026-06-24-2025-llm-year-in-review].
