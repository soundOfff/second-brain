---
type: recap
title: "Recap — The Three Flavors of Generative UI"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-03-the-three-flavors-of-generative-ui]
tags: [generative-ui, agents, protocols, frontend, copilotkit]
---

# Recap — The Three Flavors of Generative UI

A conference talk transcript by Tyler Slaton of **[[entities/copilotkit]]** (an open-source framework for building "AI copilots" — user-facing agentic applications, ~30k GitHub stars, ~15M agent interactions/month, used by 10% of the Fortune 500) [2026-07-03-the-three-flavors-of-generative-ui]. Slaton frames the talk around **[[concepts/ag-ui]]**, CopilotKit's "Agent User Interaction" protocol, which he positions as the user-facing counterpart to **[[concepts/mcp]]** (tools/context/resources) and **[[concepts/a2a-protocol]]** (agent-to-agent communication) — a streaming, client-server protocol for transporting events (text deltas, tool calls, state updates) between an agentic backend and a frontend client [2026-07-03-the-three-flavors-of-generative-ui].

The core of the talk is a spectrum of three "generative UI" approaches, trading control for flexibility: (1) **controlled generative UI** — the agent is given specific React components (e.g. a PieChart) via tool calls with Zod-schema args, giving pixel-perfect, on-brand output but requiring one tool per component and high frontend/backend coupling; (2) **declarative generative UI**, built on Google's **[[concepts/a2ui]]** spec — the agent emits a JSON schema (cards/widgets with predetermined components but agent-controlled layout) that CopilotKit renders, lowering coupling at the cost of unpredictable layout; and (3) **open generative UI** — a newly released CopilotKit feature where the agent generates raw HTML rendered in a double-iframe sandbox, giving maximum flexibility but the least predictable and hardest-to-style output [2026-07-03-the-three-flavors-of-generative-ui]. Slaton also demos agent state/working memory (via **[[entities/mastra]]**) as a fourth pattern for bidirectional, collaborative UI state shared between user and agent [2026-07-03-the-three-flavors-of-generative-ui].

Looking ahead, Slaton argues more autonomous agents will need more mid-run steering ("human-in-the-loop"), and frames naturalistic user corrections as valuable training signal, citing Cursor's use of user interactions to train its Composer model as precedent; CopilotKit says it's exploring self-improvement via RLHF on this signal [2026-07-03-the-three-flavors-of-generative-ui]. In Q&A, Slaton (whose company owns AG-UI) states AG-UI and Google's A2UI are complementary rather than competing — AG-UI is transport/streaming, A2UI is a declarative UI schema — and claims AG-UI already has ~3 million monthly package downloads [2026-07-03-the-three-flavors-of-generative-ui].

## Key claims

- CopilotKit: ~30,000 GitHub stars, AG-UI protocol at ~12,000 stars, ~15 million agent interactions/month, used by 10% of the Fortune 500 [2026-07-03-the-three-flavors-of-generative-ui].
- AG-UI is described as a streaming client-server protocol carrying events (run-started, text-message deltas, tool calls, "activity events," state updates) between agent backends and frontends, with clients in React, Angular, and (in progress) Slack [2026-07-03-the-three-flavors-of-generative-ui].
- Generative UI spans a control-vs-flexibility spectrum: controlled (predefined components via tool calls) → declarative (A2UI JSON schema → renderer) → open (agent-generated raw HTML in a sandboxed double-iframe) [2026-07-03-the-three-flavors-of-generative-ui].
- CopilotKit released "open generative UI" (agent-generated raw HTML, double-iframed for security) the day before this talk [2026-07-03-the-three-flavors-of-generative-ui].
- Mastra's "working memory" concept is used to share structured, bidirectionally-editable agent state (e.g. a to-do list) between user and agent via AG-UI state events [2026-07-03-the-three-flavors-of-generative-ui].
- Slaton (CopilotKit) claims AG-UI is already a de facto standard (~3M monthly downloads across packages) and that A2UI (Google's declarative UI spec) is "emerging" and complementary, not competing [2026-07-03-the-three-flavors-of-generative-ui].
- Slaton cites Cursor's use of user interaction data to train its "Composer" model as a precedent for training on implicit human-steering signal [2026-07-03-the-three-flavors-of-generative-ui].
- Claude is cited as already able to generate ad hoc UI on the fly (e.g., a diagram of "how electrons work") as an example of open-ended generative UI's practical use case [2026-07-03-the-three-flavors-of-generative-ui].

## Entities mentioned

- [[entities/copilotkit]], [[entities/mastra]], [[entities/claude-code]], [[entities/google]], [[entities/openai]], [[entities/anthropic]], [[entities/linear]], [[entities/cursor]]

## Concepts mentioned

- [[concepts/ag-ui]], [[concepts/a2ui]], [[concepts/mcp]], [[concepts/a2a-protocol]], [[concepts/generative-ui]], [[concepts/human-in-the-loop]]

## Source

`sources/2026-07-03-the-three-flavors-of-generative-ui.md`
