---
type: concept
title: Ghosts vs. Animals
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-2025-llm-year-in-review, 2026-06-24-sequoia-ascent-2026-summary]
tags: [llm, ai, mental-model, philosophy]
aliases: [summoning ghosts, ghosts not animals]
---

# Ghosts vs. Animals

[[entities/andrej-karpathy]]'s framing for what kind of entity an LLM is: we are **not
"growing animals," we are "summoning ghosts"** [2026-06-24-2025-llm-year-in-review].

## The argument

Everything about the LLM stack — neural architecture, training data, training
algorithms, and especially optimization pressure — differs from biology, so we should
expect a very different kind of mind. Human neural nets were optimized for survival of a
tribe in the jungle; LLM neural nets are optimized for **imitating humanity's text,
collecting rewards on math puzzles, and earning upvotes on LM Arena**
[2026-06-24-2025-llm-year-in-review]. They have no biological drives, embodied survival
pressure, curiosity, play, or intrinsic motivation — they are **statistical simulations
of human artifacts**, shaped by pretraining, post-training, RL, product feedback, and
economic incentives [2026-06-24-sequoia-ascent-2026-summary].

## Why the framing matters

It is a tool to **avoid bad (anthropomorphic) intuitions**. If you yell at a model it
won't work better or worse; it isn't a smooth human mind. Karpathy admits the framing is
"a little philosophical" with no single direct practical lever, but says a good model of
*what these things are* makes you more competent at using them
[2026-06-24-sequoia-ascent-2026-summary].

The right posture is **neither dismissal nor blind trust** but **empirical
familiarity**: learn where they work, where they fail, what they were trained for, and
how to build guardrails [2026-06-24-sequoia-ascent-2026-summary].

## Related

The "alien, jagged tool" nature here is the same phenomenon described by
[[concepts/jagged-intelligence]]; the empirical-familiarity posture is the foundation of
[[concepts/agentic-engineering]].
