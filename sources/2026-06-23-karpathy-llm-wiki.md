---
id: 2026-06-23-karpathy-llm-wiki
title: "Build a Second Brain: Karpathy's LLM Wiki Method"
type: article
url: https://www.askglitch.com/blog/build-a-second-brain
author: Glitch
captured: 2026-06-23
---

# Build a Second Brain: Karpathy's LLM Wiki Method

## Core Concept

The LLM Wiki solves the chronic problem of note-taking system maintenance by having an
AI actively own and manage the knowledge base rather than just retrieve from it: "let
an LLM maintain it. Not use an LLM to query your notes. Let it actually own the wiki,
write the pages, link the concepts, lint the contradictions."

## Three-Layer Architecture

- **Layer 1: Sources (Raw, Immutable).** Raw documents — PDFs, articles, transcripts,
  screenshots, data files — stored untouched in a `sources/` folder. No edits permitted,
  to maintain audit trails and source-of-truth integrity.
- **Layer 2: The Wiki (AI-Owned).** Machine-generated markdown pages: entity profiles,
  concept pages, recaps, and cross-references. The AI is the editor; humans read but
  don't write here. A single source can trigger updates to 10–15 pages.
- **Layer 3: The Schema (CLAUDE.md).** Configuration specifying folder structure,
  conventions, and available workflows. Transforms Claude from a generic chatbot into a
  disciplined knowledge maintainer with defined rules and operations.

## Four Core Operations

1. `/capture <url>` — ingest sources, clip content, update affected wiki pages.
2. `/sync` — reconcile batches of new sources with existing wiki structure.
3. `/lint` — weekly health checks for contradictions, orphaned pages, data gaps.
4. `/digest` — generate weekly synthesis and pattern identification.

## Technical Stack

- Primary tool: Obsidian (note vault application).
- AI engine: Claude Code.
- File format: Markdown with frontmatter.
- Structure: three distinct folders plus configuration and logging files.

## Setup (≈90 minutes)

1. Create folder structure: `~/notes/{sources,wiki}` plus `CLAUDE.md`, `log.md`,
   `index.md`.
2. Develop a `CLAUDE.md` schema tailored to your domain: layer definitions and edit
   permissions, workflow descriptions, wiki page formatting rules (frontmatter,
   backlinking, citation formats).
3. Create four Claude Code skills as `.claude/skills/<name>/SKILL.md` files, one per
   operation.
4. Ingest the first source via `/capture`.
5. Run `/lint` to identify structural issues.
6. Schedule `/digest` (e.g. weekly) via Claude Code's scheduling feature.

## Key Advantages Over RAG

Traditional retrieval-augmented generation re-synthesizes answers from raw documents on
each query. The LLM Wiki approach instead: precomputes synthesis once then updates
existing pages; makes cross-references explicit within a navigable wiki; and produces
human-readable, auditable knowledge artifacts.

## Results & Scale

Karpathy's implementation grew to approximately 100 articles and 400,000 words
maintained by the agent while he worked normally — comparable to a textbook generated
incidentally.

## Gotchas

- Don't migrate existing vaults immediately; start fresh.
- Resist manually editing wiki pages, to preserve the AI's ownership and trust.
- Budget for token usage (5–15k tokens per `/capture`).
- Run `/lint` weekly minimum; contradictions compound.
- Curate sources carefully; bad inputs poison the knowledge base.
