---
type: recap
title: "Recap — RubyLLM: A Ruby Framework for All Major AI Providers"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers]
tags: [ruby, llm-framework, sdk, open-source, tool]
---

# Recap — RubyLLM: A Ruby Framework for All Major AI Providers

This is the marketing/docs landing page (v1.16.0, captured 2026-06-24) for
**[[entities/rubyllm]]**, a Ruby framework offering one unified interface across major
AI providers instead of each provider's own bespoke client
[2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers]. It advertises support
for chat, vision (image/video analysis), audio transcription, document extraction
(PDF/CSV/JSON/any file type), image generation (`RubyLLM.paint`), embeddings
(`RubyLLM.embed`), content moderation (`RubyLLM.moderate`), streaming responses, tool
calling (`RubyLLM::Tool`), reusable agents (`RubyLLM::Agent`), structured/JSON-schema
output, and Fiber-based async concurrency, plus Rails integration via `acts_as_chat`
and a generated chat UI [2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers].
The library claims a model registry covering 800+ models with capability detection and
pricing, and only three runtime dependencies: Faraday, Zeitwerk, and Marcel
[2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers]. Supported provider
backends listed are OpenAI, xAI, Anthropic, Gemini, VertexAI, Bedrock, DeepSeek,
Mistral, Ollama, OpenRouter, Perplexity, GPUStack, and any OpenAI-compatible API
[2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers].

## Key claims

- RubyLLM provides a single unified Ruby API across all major AI providers (OpenAI,
  xAI, Anthropic, Gemini, VertexAI, Bedrock, DeepSeek, Mistral, Ollama, OpenRouter,
  Perplexity, GPUStack, and OpenAI-compatible APIs) [2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers].
- It has only three dependencies: Faraday, Zeitwerk, and Marcel
  [2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers].
- It maintains a model registry of 800+ models with capability detection and pricing
  [2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers].
- It ships first-class Rails integration (`acts_as_chat` ActiveRecord mixin, a
  generator, and an optional pre-built chat UI at `/chats`) [2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers].
- Current version at capture time was 1.16.0, with a 2.0 development branch in progress
  [2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers].

## Entities mentioned

- [[entities/rubyllm]], [[entities/openai]], [[entities/anthropic]],
  [[entities/openrouter]]

## Concepts mentioned

- [[concepts/llm-fallback-strategy]] (RubyLLM's unified multi-provider interface is the
  kind of tool that could implement it), [[concepts/tool-use]], [[concepts/structured-output]]

## Source

`sources/2026-06-24-rubyllm-a-ruby-framework-for-all-major-ai-providers.md`
