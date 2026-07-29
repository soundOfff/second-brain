---
type: concept
title: Agent-Native Infrastructure
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-sequoia-ascent-2026-summary, 2026-06-24-datasette-1-0a35]
tags: [llm, agents, infrastructure, ai, tooling]
aliases: [agent-native, build for the agent, sensors and actuators]
---

# Agent-Native Infrastructure

Building products for the case where **the user is no longer the human directly — it is
the human's agent** [2026-06-24-sequoia-ascent-2026-summary]. [[entities/andrej-karpathy]]
notes that most software is still built for humans clicking through screens, and docs
still say "go to this URL, click this button" — his "favorite pet peeve": "I don't want
to do anything. What is the thing I should copy-paste to my agent?"
[2026-06-24-sequoia-ascent-2026-summary].

## Agent-native surfaces

Products need machine-legible surfaces alongside (or instead of) human ones
[2026-06-24-sequoia-ascent-2026-summary]:

- Markdown docs, CLIs, APIs, MCP servers
- Structured logs, machine-readable schemas
- Copy-pasteable agent instructions
- Safe permissioning, auditable actions, headless setup flows

## Sensors and actuators

Karpathy frames the future stack as **agents using sensors and actuators on behalf of
people and organizations**: a *sensor* turns world-state into digital information; an
*actuator* lets an agent change something [2026-06-24-sequoia-ascent-2026-summary].
Ultimately "my agent will talk to your agent" to handle tasks like scheduling
[2026-06-24-sequoia-ascent-2026-summary].

## The deployment benchmark

Building MenuGen was easy; the hard part was **wiring Vercel, auth, payments, DNS,
secrets, and production settings** — all human-clicking work. A mature agent-native world
would let you say "build MenuGen" and have the agent deploy the whole thing without
manual clicking [2026-06-24-sequoia-ascent-2026-summary].

## In the wild

[[entities/datasette]] 1.0a35 ships its new create/alter-table features as **JSON APIs
beside the human UI** (`/<database>/-/create`, `/<database>/<table>/-/alter`) and
documents a stable template-context API — a concrete step toward machine-legible
surfaces [2026-06-24-datasette-1-0a35]. This is the infrastructure side of
[[concepts/software-3-0]].
