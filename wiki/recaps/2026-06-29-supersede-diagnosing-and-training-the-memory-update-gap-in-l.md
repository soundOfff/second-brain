---
type: recap
title: "Recap — Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l]
tags: [paper, llm-agents, memory, reinforcement-learning, benchmark]
---

# Recap — Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents

An arXiv paper (submitted 25 June 2026) by Vedant Patel identifying and addressing a specific failure mode in LLM agents: correctly using the *current* value of a fact that has changed over a long, multi-session conversation (e.g., a user's address or a price) instead of a stale, superseded one [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l]. The paper isolates this as a distinct, unsolved capability gap on the knowledge-update subset of the **[[concepts/longmemeval]]** benchmark: replacing an agent's full context with a bounded, self-maintained memory drops accuracy from 92% to 77% even on a frontier model (GPT-5.4), a statistically significant gap (paired McNemar p<0.005) [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l].

The authors show the bottleneck is memory *maintenance*, not comprehension, and that it isn't simply an undersized-memory problem: as conversation length grows 24x, accuracy falls further (68% to 28%), and giving the agent proportionally more memory produces no detectable recovery (28% to 28%, n=25) — the failure scales with conversation length, not compression ratio [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l]. They release "Supersede," an open reinforcement-learning environment (built on the verifiers/prime-rl stack) that rewards agents for answering from the current value of a fact and penalizes stale answers, turning the diagnosis into a trainable signal [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l]. GRPO fine-tuning a small open model (Qwen2.5-3B) on this environment nearly doubles held-out supersession accuracy on real, unseen conversations (9.0% to 16.7%, single run), with a monotonic checkpoint curve suggesting the learned policy — not the training harness — drives the gain [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l]. The authors claim this is the first trainable environment targeting temporal fact-currency and the first evidence the supersession gap can be trained down rather than merely measured [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l].

## Key claims

- On LongMemEval's knowledge-update subset, swapping full context for a bounded self-maintained memory drops a frontier model (GPT-5.4) from 92% to 77% accuracy (p<0.005), and this gap persists across model scale even as full-context accuracy saturates near 92% [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l].
- As conversation length grows 24x, accuracy on the supersession task falls from 68% to 28%; giving the agent proportionally more memory does not recover accuracy (28% to 28%, n=25) — the failure tracks conversation length, not memory/compression budget [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l].
- The authors release "Supersede," an open RL environment (verifiers/prime-rl stack) rewarding correct use of current (non-stale) facts [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l].
- GRPO fine-tuning Qwen2.5-3B on the Supersede environment raised held-out supersession accuracy from 9.0% to 16.7% (single run), with a monotonic checkpoint curve [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l].
- The authors claim this is the first trainable environment targeting "temporal fact-currency" and the first evidence the memory-update gap in LLM agents can be trained down, not just measured [2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l].

## Entities mentioned

- [[entities/qwen]]

## Concepts mentioned

- [[concepts/llm-agent]], [[concepts/longmemeval]], [[concepts/reinforcement-learning]], [[concepts/grpo]], [[concepts/memory-update-gap]], [[concepts/context-window]]

## Source

`sources/2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l.md`
