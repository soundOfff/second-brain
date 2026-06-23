---
type: index
title: Second Brain — Map of Content
created: 2026-06-23
updated: 2026-06-23
status: active
sources: []
tags: [meta]
---

# Map of Content

The human entry point into the wiki. The agent keeps this current as pages are added.

## How to use this brain

- Add raw material with **`/capture <url | file | pasted text>`**. You never write wiki
  pages by hand — the agent owns `wiki/`.
- Save a conversation with the agent as a source with **`/remember`** — it distils the
  chat into `sources/` and folds it into the wiki.
- Browse synthesized knowledge below. Every page links to related pages and cites its
  sources.
- Run **`/lint`** to surface gaps and contradictions, **`/digest`** for a periodic
  synthesis. Both `/sync` and `/digest` also run on a schedule (see `README.md`).

## Sections

- **Entities** — `wiki/entities/` — people, organizations, products, tools, places.
- **Concepts** — `wiki/concepts/` — ideas, methods, theories, recurring themes.
- **Recaps** — `wiki/recaps/` — one faithful summary per source.
- **Digests** — `wiki/digests/` — periodic syntheses.

## Top entities

- [[entities/andrej-karpathy]] — originator of the LLM Wiki method
- [[entities/claude-code]] — the AI engine that maintains this brain
- [[entities/obsidian]] — markdown vault for the wiki

### Tools & providers (from engineering notes)

- [[entities/groq]] — LLM inference provider (single point of failure in one incident)
- [[entities/openrouter]] — multi-provider routing gateway, adopted for model redundancy
- [[entities/sentry]] — error monitoring that surfaced an LLM outage

## Top concepts

- [[concepts/llm-wiki]] — let an LLM own and maintain the knowledge base
- [[concepts/second-brain]] — durable external knowledge store
- [[concepts/retrieval-augmented-generation]] — the query-time alternative (stub)
- [[concepts/llm-fallback-strategy]] — plan for when your primary model/provider is down

## Recently updated

- 2026-06-23 — reconciled an engineering war story
  ([[recaps/2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]]): a
  single-model Groq feature failed with no fallback. Added the
  [[concepts/llm-fallback-strategy]] concept and the Groq / OpenRouter / Sentry entities.
- 2026-06-23 — seeded the brain by capturing the founding article
  ([[recaps/2026-06-23-karpathy-llm-wiki]]): added the LLM Wiki, Second Brain, and RAG
  concepts and the Karpathy / Claude Code / Obsidian entities.
