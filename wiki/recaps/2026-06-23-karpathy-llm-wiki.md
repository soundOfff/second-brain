---
type: recap
title: "Recap — Build a Second Brain: Karpathy's LLM Wiki Method"
created: 2026-06-23
updated: 2026-06-23
status: stable
sources: [2026-06-23-karpathy-llm-wiki]
tags: [knowledge-management, llm, second-brain, method]
---

# Recap — Build a Second Brain: Karpathy's LLM Wiki Method

The article describes the **[[concepts/llm-wiki]]** method for building a
**[[concepts/second-brain]]**: instead of using an LLM to *query* notes (as in
**[[concepts/retrieval-augmented-generation]]**), you let the LLM **own and maintain**
the knowledge base — writing pages, linking concepts, and linting contradictions. The
approach is attributed to **[[entities/andrej-karpathy]]** and implemented with
**[[entities/claude-code]]** over an **[[entities/obsidian]]**-style markdown vault.

## Key claims

- The core move is to let an LLM *maintain* the wiki, not just retrieve from it — "let
  it actually own the wiki, write the pages, link the concepts, lint the contradictions"
  [2026-06-23-karpathy-llm-wiki].
- A **three-layer architecture**: immutable `sources/`, an AI-owned `wiki/`, and a
  `CLAUDE.md` schema that defines rules and workflows [2026-06-23-karpathy-llm-wiki].
- **Four operations** drive it: `/capture`, `/sync`, `/lint`, `/digest`
  [2026-06-23-karpathy-llm-wiki].
- One source can ripple into updates across **10–15 wiki pages**
  [2026-06-23-karpathy-llm-wiki].
- Advantage over RAG: synthesis is **precomputed once** into navigable, auditable,
  cross-linked pages rather than re-derived per query [2026-06-23-karpathy-llm-wiki].
- Karpathy's instance reportedly grew to **~100 articles / ~400,000 words** maintained
  by the agent "incidentally" while he worked [2026-06-23-karpathy-llm-wiki].
- Setup takes ~90 minutes; budget **5–15k tokens per `/capture`**
  [2026-06-23-karpathy-llm-wiki].
- Gotchas (author's guidance): start fresh rather than migrating an old vault; don't
  hand-edit wiki pages; lint weekly; curate sources [2026-06-23-karpathy-llm-wiki].

## Entities mentioned

- [[entities/andrej-karpathy]], [[entities/claude-code]], [[entities/obsidian]]

## Concepts mentioned

- [[concepts/llm-wiki]], [[concepts/second-brain]],
  [[concepts/retrieval-augmented-generation]]

## Source

`sources/2026-06-23-karpathy-llm-wiki.md`
