---
type: concept
title: Verifiability (automate what you can verify)
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-sequoia-ascent-2026-summary, 2026-06-24-2025-llm-year-in-review]
tags: [llm, framework, reinforcement-learning, ai]
aliases: [verifiability thesis]
---

# Verifiability

[[entities/andrej-karpathy]]'s framework for predicting **where AI improves fastest**:

> Traditional software automates what you can **specify**. LLMs and reinforcement
> learning automate what you can **verify** [2026-06-24-sequoia-ascent-2026-summary].

If a task has an automatic reward or success signal — it is resettable, repeatable, and
rewardable — models can "practice" it. This is why math, coding, tests, benchmarks, and
games improve so quickly, and why coding agents feel dramatically better than ordinary
chatbots: coding gives constant feedback (tests pass/fail, programs run/crash, diffs are
inspectable) [2026-06-24-sequoia-ascent-2026-summary].

## The mechanism

Verifiability is realized through
[[concepts/reinforcement-learning-from-verifiable-rewards]]: frontier labs train LLMs in
giant RL environments with verification rewards, and capability concentrates wherever
those environments exist [2026-06-24-sequoia-ascent-2026-summary].

## Capability is more than verifiability

The Sequoia talk refines the thesis: capability also depends on **training attention**.
A rough formula —

> capability spike ≈ verifiability × training attention × data coverage × economic value
> [2026-06-24-sequoia-ascent-2026-summary]

Chess is the example: GPT-4 improved at chess partly because more chess data was added
to the mix, not purely from general progress. Frontier models are "artifacts of
pretraining mixtures, RL environments, benchmark pressure, product priorities, and
economic incentives" — they "have no manual." This produces
[[concepts/jagged-intelligence]] [2026-06-24-sequoia-ascent-2026-summary].

## Implications

- **For builders:** ask "are you on the model's rails?" If your task is verifiable and
  heavily trained, the model may fly; if not, it may fail in basic ways and you may need
  better context, tools, fine-tuning, or your own evals/RL environments
  [2026-06-24-sequoia-ascent-2026-summary].
- **Founder wedge:** find domains that are **valuable, verifiable, and undertrained** by
  frontier labs. Coding and math are saturated; latent verifiable structure elsewhere is
  a startup opportunity. "Almost everything can be made verifiable to some extent" — even
  writing, via a council of LLM judges [2026-06-24-sequoia-ascent-2026-summary].
