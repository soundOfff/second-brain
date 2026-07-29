---
type: concept
title: LLM Wiki
created: 2026-06-23
updated: 2026-06-26
status: active
sources: [2026-06-23-karpathy-llm-wiki, 2026-06-24-sequoia-ascent-2026-summary]
tags: [knowledge-management, llm, method, second-brain]
aliases: [LLM-maintained wiki, AI-owned wiki]
---

# LLM Wiki

A method for building a **[[concepts/second-brain]]** in which a large language model
**owns and maintains** the knowledge base rather than merely retrieving from it. The LLM
writes the pages, links concepts, reconciles new inputs, and lints contradictions —
turning note maintenance (the chronic failure point of personal knowledge systems) over
to the agent [2026-06-23-karpathy-llm-wiki]. The approach is associated with
[[entities/andrej-karpathy]].

## Three-layer architecture

1. **Sources** — raw, immutable inputs (`sources/`). Never edited; the audit trail.
2. **Wiki** — AI-owned synthesized markdown (`wiki/`): entity profiles, concept pages,
   recaps, cross-references. Humans read; the agent writes.
3. **Schema** — a `CLAUDE.md` defining structure, conventions, and workflows that turns
   a general chatbot into a disciplined maintainer [2026-06-23-karpathy-llm-wiki].

## Four operations

`/capture` (ingest one source and ripple updates), `/sync` (reconcile a batch),
`/lint` (find contradictions/orphans/gaps), `/digest` (periodic synthesis)
[2026-06-23-karpathy-llm-wiki]. A single capture can touch 10–15 pages.

## Versus RAG

Where [[concepts/retrieval-augmented-generation]] re-synthesizes an answer from raw docs
on every query, the LLM Wiki **precomputes synthesis once** into navigable, auditable,
cross-linked pages and updates them incrementally [2026-06-23-karpathy-llm-wiki].

## Reported results

Karpathy's instance grew to ~100 articles / ~400k words, maintained by the agent while
he worked normally [2026-06-23-karpathy-llm-wiki].

## Practice notes

Start fresh rather than migrating an old vault; don't hand-edit wiki pages (preserves
the agent's ownership/trust); lint weekly (contradictions compound); curate sources
(bad inputs poison the base); budget ~5–15k tokens per capture
[2026-06-23-karpathy-llm-wiki].

## Why it's a Software 3.0 example

In his Sequoia Ascent 2026 talk, [[entities/andrej-karpathy]] returns to the LLM Wiki /
knowledge-base pattern as the clearest example of an information transformation that **no
classical program could robustly do** but an LLM can — an agent incrementally compiling
messy sources into a persistent markdown wiki (summaries, entity/concept pages,
contradictions, cross-links, logs) [2026-06-24-sequoia-ascent-2026-summary]. It is an
instance of [[concepts/software-3-0]], and he prizes it as a tool for
[[concepts/outsourcing-thinking-vs-understanding|understanding]] ("synthetic data
generation over fixed data"): "whenever I see a different projection onto information, I
feel like I gain insight" [2026-06-24-sequoia-ascent-2026-summary].

## Implemented with

[[entities/claude-code]] over an [[entities/obsidian]]-style markdown vault.
