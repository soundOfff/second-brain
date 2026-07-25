---
type: recap
title: "Recap — Introducing A2UI: An Open Project for Agent-Driven Interfaces"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces]
tags: [ai, agents, protocol, ui, google, open-source]
---

# Recap — Introducing A2UI: An Open Project for Agent-Driven Interfaces

A Google Developers Blog post (dated Dec. 15, 2025, captured 2026-07-03) announces
**[[concepts/a2ui]]** as a public, Apache-2-licensed open-source project and format that
lets AI agents generate rich, native-feeling user interfaces instead of only text
[2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces]. The stated
problem: in a multi-agent world built on the **[[concepts/agent-to-agent-protocol]]**
(A2A, donated to the Linux Foundation), a remote agent cannot directly manipulate a
client's UI (DOM), and historically the only option was sending HTML/JS sandboxed in
iframes — heavy, visually inconsistent, and a security concern
[2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces]. A2UI's
answer is a *declarative* JSON message format (not executable code): agents send a
component tree plus data model referencing a client-owned "catalog" of pre-approved
trusted components (Card, Button, TextField, etc.), and the client renders it with its
own native framework (Lit, Angular, Flutter, React, SwiftUI, etc.), keeping full control
of styling and security [2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces].

The post positions A2UI as complementary to, not competing with, adjacent tools: it can
serve as the UI data format under **AG UI**/CopilotKit (which the post says has
"day-zero" A2UI compatibility), differs from **MCP Apps** (which treats UI as a
sandboxed HTML resource fetched via a `ui://` URI) by sending a native component
blueprint instead, and differs from platform-specific tools like OpenAI's **ChatKit**
by targeting cross-platform, cross-organization agent meshes rather than a single
ecosystem [2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces].
Named collaborators/adopters quoted in the piece include CopilotKit/AG-UI, Google's
**Opal** (AI mini-app builder), **Gemini Enterprise**, and **Flutter**'s GenUI SDK,
which the post says already uses A2UI under the hood
[2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces]. As of this
post, the format is at v0.8, with early client libraries for Flutter, Web Components,
and Angular, and the source is available at `github.com/google/A2UI`
[2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces].

## Key claims

- A2UI is a declarative (non-executable) JSON format for agents to describe UI
  component trees, designed to be transmitted over A2A, AG UI, and potentially other
  transports [2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces].
- Clients maintain a "catalog" of pre-approved trusted UI components; the agent can only
  request components from that catalog, which Google states is meant to reduce UI
  injection risk [2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces].
- The format is designed to be generated incrementally (as a flat list of components
  with ID references) to support progressive/streaming rendering
  [2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces].
- A2UI differs from MCP Apps (which returns an opaque HTML resource for a sandboxed
  iframe) by sending a native component blueprint that inherits the host app's styling
  and accessibility features [2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces].
- Flutter's GenUI SDK already uses A2UI as its declaration format between server-side
  agents and the app, per Google [2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces].
- AG UI/CopilotKit provides "day-zero" compatibility with A2UI, per a quote from Atai
  Barkai (Founder of CopilotKit and AG-UI) [2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces].
- The A2UI format is at v0.8 as of this announcement, licensed Apache 2.0, with early
  client libraries for Flutter, Web Components, and Angular
  [2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces].

## Entities mentioned

- [[entities/google]], [[entities/openai]]

## Concepts mentioned

- [[concepts/a2ui]], [[concepts/agent-to-agent-protocol]], [[concepts/model-context-protocol]],
  [[concepts/generative-ui]], [[concepts/ai-agents]]

## Source

`sources/2026-07-03-introducing-a2ui-an-open-project-for-agent-driven-interfaces.md`
