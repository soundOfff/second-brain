---
type: entity
title: Groq
created: 2026-06-23
updated: 2026-06-23
status: stub
sources: [2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]
tags: [tool, llm, inference, api, provider]
aliases: [Groq API]
---

# Groq

An LLM inference provider, used via the **Groq API**. In this brain it appears as the
original single-model backend for a text-cleanup feature; when the model became
unavailable overnight, the feature had no fallback and users were affected
[2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]. The author
later added a fallback and migrated to **[[entities/openrouter]]** for redundancy — see
[[concepts/llm-fallback-strategy]].

> Stub — known here only through one incident, not yet profiled as a product.
