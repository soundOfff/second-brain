---
type: entity
title: Claude Code
created: 2026-06-23
updated: 2026-06-23
status: stub
sources: [2026-06-23-karpathy-llm-wiki]
tags: [tool, ai, agent]
aliases: [Claude Code CLI]
---

# Claude Code

Anthropic's agentic coding tool, used as the **AI engine** that owns and maintains an
[[concepts/llm-wiki]] [2026-06-23-karpathy-llm-wiki]. In this method its **skills**
(`.claude/skills/<name>/SKILL.md`) implement the four operations — `/capture`, `/sync`,
`/lint`, `/digest` — and its `CLAUDE.md` schema defines the conventions that make it a
disciplined maintainer rather than a generic chatbot [2026-06-23-karpathy-llm-wiki]. Its
scheduling feature can run `/digest` on a recurring basis.

> Stub — described here only in its role within the LLM Wiki method.
