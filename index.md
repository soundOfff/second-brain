---
type: index
title: Second Brain — Map of Content
created: 2026-06-23
updated: 2026-06-26
status: active
sources: []
tags: [meta]
---

# Map of Content

The human entry point into the wiki. The agent keeps this current as pages are added.

## How to use this brain

- Add raw material with **`/capture <url | file | pasted text>`**. You never write wiki
  pages by hand — the agent owns `wiki/`.
- Save a conversation with the agent as a source with **`/remember`** — it distils the
  chat into `sources/` and folds it into the wiki.
- Browse synthesized knowledge below. Every page links to related pages and cites its
  sources.
- Run **`/lint`** to surface gaps and contradictions, **`/digest`** for a periodic
  synthesis. Both `/sync` and `/digest` also run on a schedule (see `README.md`).

## Sections

- **Entities** — `wiki/entities/` — people, organizations, products, tools, places.
- **Concepts** — `wiki/concepts/` — ideas, methods, theories, recurring themes.
- **Recaps** — `wiki/recaps/` — one faithful summary per source.
- **Digests** — `wiki/digests/` — periodic syntheses.

## Top entities

### People

- [[entities/andrej-karpathy]] — originator of the LLM Wiki method; source of most of the
  framings below (Software 3.0, vibe coding, ghosts vs. animals, verifiability)
- [[entities/simon-willison]] — developer/blogger, creator of Datasette (regular feed)
- [[entities/tom-macwright]] — developer/writer; "Accidental anonymity" (stub)

### AI labs & tools

- [[entities/anthropic]] — maker of Claude Code (stub)
- [[entities/claude-code]] — the AI engine that maintains this brain; "AI that lives on
  your computer"
- [[entities/openai]] — frontier lab; o1/o3 (first RLVR models), Codex (stub)
- [[entities/codex]] — OpenAI's agentic coding tool (stub)
- [[entities/cursor]] — AI editor; the "Cursor for X" LLM-app layer (stub)
- [[entities/google-gemini]] — Gemini / "Nano Banana" image model (stub)

### Data & web tooling

- [[entities/datasette]] — open-source data multi-tool; Datasette Lite (stub)
- [[entities/pyodide]] — Python in the browser via WebAssembly (stub)
- [[entities/obsidian]] — markdown vault for the wiki
- [[entities/sequoia-capital]] — VC; host of Ascent 2026 (stub)

### Inference providers & ops (from engineering notes)

- [[entities/groq]] — LLM inference provider (single point of failure in one incident)
- [[entities/openrouter]] — multi-provider routing gateway, adopted for model redundancy
- [[entities/sentry]] — error monitoring that surfaced an LLM outage

## Top concepts

### Knowledge management

- [[concepts/llm-wiki]] — let an LLM own and maintain the knowledge base
- [[concepts/second-brain]] — durable external knowledge store
- [[concepts/retrieval-augmented-generation]] — the query-time alternative (stub)
- [[concepts/outsourcing-thinking-vs-understanding]] — you can outsource thinking, not
  understanding

### The shape of LLM intelligence (Karpathy)

- [[concepts/reinforcement-learning-from-verifiable-rewards]] — RLVR, the new training
  stage
- [[concepts/verifiability]] — "automate what you can verify"
- [[concepts/jagged-intelligence]] — capability is spiky, not smooth
- [[concepts/ghosts-vs-animals]] — what kind of entity an LLM is

### Software 3.0 & agentic coding

- [[concepts/software-3-0]] — the context window as the new program
- [[concepts/vibe-coding]] — building software in English (raises the floor)
- [[concepts/agentic-engineering]] — coordinating fallible agents (raises the ceiling)
- [[concepts/git-worktrees]] — isolate parallel agent sessions
- [[concepts/agent-native-infrastructure]] — build for the agent, not just the human
- [[concepts/llm-app-layer]] — the "Cursor for X" vertical app layer
- [[concepts/llm-gui]] — LLMs speaking in images (Nano Banana, neural computers)

### Risks & resilience

- [[concepts/ai-slop]] — generated output that erases its own signal
- [[concepts/llm-fallback-strategy]] — plan for when your primary model/provider is down

## Recently updated

- 2026-06-26 — `/sync` reconciled a 6-source backlog (two Karpathy essays + three Simon
  Willison posts + the Claude Code worktrees doc). Built out the Software 3.0 / agentic
  coding and "shape of LLM intelligence" concept clusters; added the OpenAI / Anthropic /
  Cursor / Codex / Gemini / Willison / Datasette / Pyodide / MacWright / Sequoia
  entities; promoted Karpathy and Claude Code to `active`. See
  [[recaps/2026-06-24-sequoia-ascent-2026-summary]] and
  [[recaps/2026-06-24-2025-llm-year-in-review]].
- 2026-06-23 — reconciled an engineering war story
  ([[recaps/2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo]]): a
  single-model Groq feature failed with no fallback. Added the
  [[concepts/llm-fallback-strategy]] concept and the Groq / OpenRouter / Sentry entities.
- 2026-06-23 — seeded the brain by capturing the founding article
  ([[recaps/2026-06-23-karpathy-llm-wiki]]): added the LLM Wiki, Second Brain, and RAG
  concepts and the Karpathy / Claude Code / Obsidian entities.
