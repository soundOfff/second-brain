---
type: entity
title: Sentry
created: 2026-06-23
updated: 2026-06-23
status: stub
sources: [2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]
tags: [tool, monitoring, observability, error-tracking]
---

# Sentry

An error-monitoring and alerting service. In this brain it appears as the **detection
layer** in an LLM outage: when a single-model **[[entities/groq]]** feature went down,
"a flood of Sentry alerts" is how the author learned of the incident
[2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]. It illustrates
why monitoring is a companion to an [[concepts/llm-fallback-strategy]] — you want to hear
about degradation from a dashboard, not from users.

> Stub — known here only through one incident, not yet profiled as a product.
