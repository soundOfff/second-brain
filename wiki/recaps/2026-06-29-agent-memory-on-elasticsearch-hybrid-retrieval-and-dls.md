---
type: recap
title: "Recap — Agent memory on Elasticsearch: hybrid retrieval and DLS"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls]
tags: [agent-memory, elasticsearch, hybrid-retrieval, rag, multi-tenancy, mcp]
---

# Recap — Agent memory on Elasticsearch: hybrid retrieval and DLS

A detailed engineering write-up by Noam Schwartz of **[[entities/elasticsearch]]** describing
a persistent, multi-tenant **[[concepts/agent-memory]]** layer built entirely on
Elasticsearch, reporting R@10 recall of 0.89 across 168 eval questions with zero
cross-tenant leaks [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].
The author argues a large context window is "a scratchpad, not a memory system" and that
long-term memory requires a persistent store queryable by content, time, and user
[2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].

The architecture splits memory into three indices mirroring the cognitive-science
episodic/semantic/procedural split (the COALA framing): episodic (raw timestamped
events), semantic (durable facts about the user), and procedural (multi-step playbooks
with success/failure counters), plus a fourth shared "catalog" index for non-personal
world data [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls]. Recall
uses **[[concepts/hybrid-retrieval]]**: BM25 keyword search and Jina v5 dense vectors
fused with **[[concepts/reciprocal-rank-fusion]]** (RRF, tightened rank_constant=30),
then re-ordered by a Jina v2 cross-encoder reranker over an 80-candidate-per-leg pool
[2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls]. Every user turn also
triggers an automatic "pre-recall" on the verbatim message before any LLM paraphrasing
can strip literal tokens like version numbers or error codes
[2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].

Contradictions are handled by supersession rather than deletion: a new fact is written,
the old doc is marked `superseded_by`, and default recall filters out superseded docs
while preserving them for audit — with a confidence penalty applied when a correction is
classified as "harsh" (denial) versus "natural" (an update)
[2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls]. Ranking combines a
gauss-shaped time-decay (180-day flat zone, ~5-year half-life) with a use-count boost, and
tenant isolation is enforced server-side via Elasticsearch **[[concepts/document-level-security]]**
(DLS) keyed per user, with an app-level `user_id` filter as a defense-in-depth check
[2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls]. The whole memory
layer is exposed to any client via **[[concepts/model-context-protocol]]** (MCP), tested
with Claude Desktop and Cursor [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].

## Key claims

- Long-term agent memory needs three separate stores by lifecycle — episodic, semantic,
  procedural — because each has different write rates and aging rules
  [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].
- Hybrid retrieval (BM25 + dense vectors via RRF, then cross-encoder reranking) beats
  either leg alone because BM25 anchors literal tokens an LLM paraphrase would drop, while
  dense vectors catch semantic rephrasings
  [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].
- Writes use `refresh=True` per turn (not batched) so same-turn write-then-recall patterns
  don't hit Elasticsearch's async refresh propagation gap
  [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].
- Contradictions are resolved by supersession (old doc kept, marked superseded) rather than
  deletion, preserving an audit trail
  [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].
- Semantic facts are the hardest retrieval case (R@10 ≈ 0.81) versus episodic (0.98) and
  procedural (1.0), attributed to "sibling collisions" between plausible facts
  [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].
- Multi-tenant isolation is enforced at the Elasticsearch cluster level via per-user DLS
  API keys, not application-layer filtering, with R@10 ≥ 0.85 and zero leaks as a CI gate
  [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].
- The author notes several parts of the reference implementation are simplified stand-ins
  for production behavior (e.g. dedup relies on an LLM "do not duplicate" instruction
  rather than the described similarity-threshold guards; success/failure counts aren't
  yet wired into ranking) [2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls].

## Entities mentioned

- [[entities/elasticsearch]], [[entities/noam-schwartz]]

## Concepts mentioned

- [[concepts/agent-memory]], [[concepts/hybrid-retrieval]],
  [[concepts/reciprocal-rank-fusion]], [[concepts/document-level-security]],
  [[concepts/model-context-protocol]], [[concepts/retrieval-augmented-generation]]

## Source

`sources/2026-06-29-agent-memory-on-elasticsearch-hybrid-retrieval-and-dls.md`
