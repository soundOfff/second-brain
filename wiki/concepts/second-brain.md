---
type: concept
title: Second Brain
created: 2026-06-23
updated: 2026-06-26
status: active
sources: [2026-06-23-karpathy-llm-wiki, 2026-06-24-sequoia-ascent-2026-summary]
tags: [knowledge-management, second-brain]
aliases: [personal knowledge base, PKM]
---

# Second Brain

An external, durable store of one's knowledge — notes, sources, and synthesized ideas —
meant to offload memory and surface connections. The chronic failure mode of such
systems is **maintenance**: capture is easy, but keeping notes organized, linked, and
contradiction-free decays over time [2026-06-23-karpathy-llm-wiki].

The **[[concepts/llm-wiki]]** method addresses this by handing maintenance to an LLM
that owns the wiki, rather than relying on human discipline or on querying raw notes via
[[concepts/retrieval-augmented-generation]] [2026-06-23-karpathy-llm-wiki].

[[entities/andrej-karpathy]] frames such knowledge bases not as "answer machines" but as
**tools for turning information into understanding** — which matters because you can
[[concepts/outsourcing-thinking-vs-understanding|outsource thinking but not
understanding]] [2026-06-24-sequoia-ascent-2026-summary].

This repository is itself a second brain built on that method — see [[index]] and the
schema in `CLAUDE.md`.
