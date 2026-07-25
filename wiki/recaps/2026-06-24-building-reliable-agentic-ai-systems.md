---
type: recap
title: "Recap — Building Reliable Agentic AI Systems"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-building-reliable-agentic-ai-systems]
tags: [agentic-ai, rag, llm-engineering, case-study]
---

# Recap — Building Reliable Agentic AI Systems

A Thoughtworks case study (by Sarang Sanjay Kulkarni, published on Martin Fowler's site) describing PRINCE (Preclinical Information Center), a cloud platform [[entities/bayer]] built with [[entities/thoughtworks]] to help pharmaceutical researchers search decades of preclinical safety-study reports [2026-06-24-building-reliable-agentic-ai-systems]. PRINCE evolved through three phases — "Search" (keyword/metadata search), "Ask" (RAG-based Q&A), and "Do" (a multi-agent research assistant that can draft regulatory documents) [2026-06-24-building-reliable-agentic-ai-systems].

The author frames the engineering lessons through two lenses coined for the piece: *context engineering* (what information each agent sees, and when) and *harness engineering* (the orchestration, retries, state persistence, and recovery scaffolding around the models) [2026-06-24-building-reliable-agentic-ai-systems]. PRINCE is built on [[concepts/agentic-rag]], orchestrated with [[entities/langgraph]] and served via FastAPI, combining [[concepts/retrieval-augmented-generation]] over unstructured PDF study reports (indexed in Amazon OpenSearch) with [[concepts/text-to-sql]] over structured data in Amazon Athena [2026-06-24-building-reliable-agentic-ai-systems]. The agentic workflow is composed of specialized steps/agents — Clarify User Intent, Think & Plan (process reflection, inspired by "Anthropic's Think tool"), Researcher Agent, Reflection Agent (data sufficiency), and Writer Agent (answer synthesis with citations) — each deliberately scoped to a narrow slice of context rather than one large prompt [2026-06-24-building-reliable-agentic-ai-systems].

Reliability is engineered explicitly: LLM calls and workflow nodes have automatic retries with fallback to alternate models/providers on failure ([[concepts/llm-fallback-strategy]]), agent state is checkpointed to PostgreSQL via LangGraph, application state lives in DynamoDB, and failed workflows can resume from the point of failure rather than restarting [2026-06-24-building-reliable-agentic-ai-systems]. Observability runs through [[entities/langfuse]] (tracing plus stored eval datasets) and CloudWatch, with evaluation via the RAGAS framework measuring faithfulness, answer relevancy, context relevancy, answer accuracy, and semantic similarity — run daily on live traffic and on-demand against curated datasets [2026-06-24-building-reliable-agentic-ai-systems]. The system's internal GenAI platform exposes models from OpenAI, [[entities/anthropic]], Google, and open-source providers behind a unified OpenAI-compatible endpoint so models can be swapped [2026-06-24-building-reliable-agentic-ai-systems].

The author's stated broader lesson: production-ready agentic AI is not just about better models or prompts — reliability comes from engineering both the context the model sees and the harness within which it acts, and this remains essential in regulated, trust-sensitive domains even as model capabilities improve [2026-06-24-building-reliable-agentic-ai-systems].

## Key claims

- PRINCE has been available to end users since early 2024, with agentic integration added later that year [2026-06-24-building-reliable-agentic-ai-systems].
- The RAG pipeline uses a hybrid retriever: metadata filtering + kNN semantic search + keyword search, weighted 0.7 semantic / 0.3 keyword, over 5 expanded queries, then reranked with a bge-reranker-large cross-encoder from ~20 candidates down to 7 chunks [2026-06-24-building-reliable-agentic-ai-systems].
- The Text-to-SQL tool dynamically injects only relevant schema, uses few-shot examples retrieved via vector similarity, blocks non-SELECT queries, and retries failed SQL up to 3 times using the DB error message [2026-06-24-building-reliable-agentic-ai-systems].
- An earlier LLM-based SQL review step was removed because the reviewer LLM incorrectly flagged valid queries as erroneous, hurting efficiency without improving accuracy [2026-06-24-building-reliable-agentic-ai-systems].
- The system has three complementary reflection loops: process reflection (Think & Plan, is the workflow on track), data reflection (Reflection Agent, is retrieved evidence sufficient), and draft reflection (Writer Agent review loop, is the output complete) [2026-06-24-building-reliable-agentic-ai-systems].
- All AI-drafted regulatory-document outputs are intended for expert review; final submissions are authored/approved by qualified personnel [2026-06-24-building-reliable-agentic-ai-systems].
- The Researcher Agent is being evolved from one monolithic agent into a hierarchy of domain-specific sub-agents (e.g., toxicology vs. pharmacology) each owning its own tools and schema knowledge [2026-06-24-building-reliable-agentic-ai-systems].
- The article's author disclosed using AI assistance (brainstorming, outlines, draft polishing) while writing it [2026-06-24-building-reliable-agentic-ai-systems].

## Entities mentioned

- [[entities/bayer]], [[entities/thoughtworks]], [[entities/langgraph]], [[entities/langfuse]], [[entities/anthropic]]

## Concepts mentioned

- [[concepts/agentic-rag]], [[concepts/retrieval-augmented-generation]], [[concepts/text-to-sql]], [[concepts/context-engineering]], [[concepts/harness-engineering]], [[concepts/llm-fallback-strategy]], [[concepts/process-reflection]]

## Source

`sources/2026-06-24-building-reliable-agentic-ai-systems.md`
