---
type: concept
title: Outsourcing Thinking vs. Understanding
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-sequoia-ascent-2026-summary]
tags: [ai, education, understanding, knowledge-management]
aliases: [you can't outsource understanding]
---

# Outsourcing Thinking vs. Understanding

A line [[entities/andrej-karpathy]] "keeps returning to," from a tweet that "blew my
mind":

> You can outsource your **thinking**, but you can't outsource your **understanding**
> [2026-06-24-sequoia-ascent-2026-summary].

## The argument

Even as agents do more of the work, the **human stays the bottleneck** for direction:
you need understanding to know what is worth building, which question matters, what result
is suspicious, and what tradeoff is acceptable. "You cannot be a good director if you do
not understand" [2026-06-24-sequoia-ascent-2026-summary]. LLMs do not yet fully excel at
understanding, so the human is "uniquely in charge of that"
[2026-06-24-sequoia-ascent-2026-summary]. This is the same reason human judgment stays
central to [[concepts/agentic-engineering]].

## Tools that enhance understanding

Karpathy is interested in LLM knowledge bases ([[concepts/llm-wiki]]) precisely because
they are **not just answer machines** but tools for **turning information into
understanding** — "whenever I see a different projection onto information, I feel like I
gain insight… synthetic data generation over fixed data"
[2026-06-24-sequoia-ascent-2026-summary]. His single-file **microGPT** (a complete,
dependency-free GPT training/inference implementation) is another: a distilled artifact
small enough for both humans and agents to inspect, where the human contributes the taste
and the agent can explain it interactively to each learner
[2026-06-24-sequoia-ascent-2026-summary].

## Related

The flip side — generated output that conveys no real understanding — is
[[concepts/ai-slop]] / accidental anonymity.
