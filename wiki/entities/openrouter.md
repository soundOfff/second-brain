---
type: entity
title: OpenRouter
created: 2026-06-23
updated: 2026-06-23
status: stub
sources: [2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]
tags: [tool, llm, gateway, routing, api, provider]
---

# OpenRouter

A unified API gateway that routes requests across many LLM providers and models behind a
single interface. In this brain it appears as the **durable fix** for a single-provider
outage: after a **[[entities/groq]]**-backed feature went down with no fallback, the
author migrated to OpenRouter specifically because it **provides model redundancy**
[2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]. It is a
concrete instance of the routing-gateway tier of an [[concepts/llm-fallback-strategy]].

> Stub — known here only through one migration, not yet profiled as a product.
