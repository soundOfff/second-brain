---
type: concept
title: Retrieval-Augmented Generation (RAG)
created: 2026-06-23
updated: 2026-06-23
status: stub
sources: [2026-06-23-karpathy-llm-wiki]
tags: [llm, retrieval, method]
aliases: [RAG]
---

# Retrieval-Augmented Generation (RAG)

A pattern where, at query time, relevant raw documents are retrieved and fed to an LLM
which **re-synthesizes an answer on each query**. In the context of personal notes, this
means the synthesis is transient — recomputed every time and not persisted as a
navigable artifact [2026-06-23-karpathy-llm-wiki].

The **[[concepts/llm-wiki]]** method is positioned as an alternative: precompute the
synthesis **once** into human-readable, cross-linked, auditable wiki pages, then update
them incrementally rather than re-deriving per query [2026-06-23-karpathy-llm-wiki].

> Stub — this page reflects only how one source (the LLM Wiki article) frames RAG.
> Capture a dedicated source on RAG to flesh it out.
