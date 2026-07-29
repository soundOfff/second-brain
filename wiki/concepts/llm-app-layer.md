---
type: concept
title: The LLM App Layer ("Cursor for X")
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-2025-llm-year-in-review]
tags: [llm, products, apps, ai]
aliases: [Cursor for X, LLM apps]
---

# The LLM App Layer ("Cursor for X")

A distinct layer of software that sits between frontier LLM labs and end users,
**bundling and orchestrating LLM calls for a specific vertical**.
[[entities/andrej-karpathy]] says [[entities/cursor]]'s rise in 2025 "convincingly
revealed" this layer — people started saying "**Cursor for X**"
[2026-06-24-2025-llm-year-in-review].

## What an LLM app does

Drawing on his Y Combinator talk, Karpathy lists four jobs
[2026-06-24-2025-llm-year-in-review]:

1. **Context engineering** — assemble the right context for the model.
2. **Orchestration** — string multiple LLM calls into increasingly complex DAGs,
   balancing performance and cost tradeoffs.
3. **Application-specific GUI** — for the human in the loop.
4. **An "autonomy slider"** — let the user dial how much the app does on its own.

## How "thick" is this layer?

The open 2025 question: will LLM labs capture all applications, or are there "green
pastures" for LLM apps? Karpathy's bet: **labs trend to graduate the generally capable
"college student," while LLM apps organize, finetune, and animate teams of them into
deployed professionals in specific verticals** — supplying private data, sensors,
actuators, and feedback loops [2026-06-24-2025-llm-year-in-review]. This connects to
[[concepts/agent-native-infrastructure]] (sensors/actuators) and the founder framing in
[[concepts/verifiability]].
