---
type: recap
title: "Recap — 2025 LLM Year in Review"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-2025-llm-year-in-review]
tags: [llm, year-in-review, reasoning, agents, vibe-coding, karpathy]
---

# Recap — 2025 LLM Year in Review

**[[entities/andrej-karpathy]]**'s year-end blog post lists six "paradigm changes" he found personally notable in LLM progress during 2025 [2026-06-24-2025-llm-year-in-review]. These are his own curated, opinionated observations rather than a comprehensive survey, and he frames them as conceptual shifts rather than benchmark wins.

1. **[[concepts/rlvr]]** (Reinforcement Learning from Verifiable Rewards) emerged as a new major stage added to the standard pretrain → SFT → RLHF recipe, letting models develop reasoning-like behavior by training against automatically verifiable rewards (math/code); Karpathy notes OpenAI's o1 (late 2024) was the first demo but o3 (early 2025) was the clear inflection point, and that RLVR absorbed compute originally destined for pretraining [2026-06-24-2025-llm-year-in-review].
2. **"Ghosts vs. animals" / jagged intelligence** — Karpathy argues LLMs shouldn't be understood via an animal-evolution analogy since their training pressures are entirely different, producing simultaneously genius-level and "cognitively challenged" jagged capability profiles; he also reports declining trust in benchmarks in 2025 because verifiable benchmark-adjacent environments are trivially gamed via RLVR/synthetic data ("training on the test set is a new art form") [2026-06-24-2025-llm-year-in-review].
3. **[[entities/cursor]]** revealed a new "LLM app" layer — orchestrating multiple LLM calls into DAGs, doing context engineering, providing vertical-specific GUIs and an "autonomy slider"; Karpathy speculates labs will produce generally-capable "college student" models while apps like Cursor organize/finetune them into deployed professionals for specific verticals [2026-06-24-2025-llm-year-in-review].
4. **[[entities/claude-code]]** is called the first convincing demonstration of an LLM agent, notable specifically for running locally on the user's own machine/context/data rather than in the cloud (a contrast Karpathy draws with OpenAI's early cloud-container-based Codex/agent efforts); he frames this as "Anthropic got this order of precedence correct" [2026-06-24-2025-llm-year-in-review].
5. **Vibe coding** — a term Karpathy says he personally coined — crossed a capability threshold in 2025 where building software via natural language became broadly accessible to non-professionals, and also let professionals write far more ephemeral/throwaway code than before; he cites his own projects (nanochat's custom Rust BPE tokenizer, menugen, llm-council, reader3, HN time capsule) as examples [2026-06-24-2025-llm-year-in-review].
6. **Google Gemini "Nano Banana"** is cited as an early hint of an "LLM GUI" — Karpathy's thesis that LLMs are a new computing paradigm (like 1970s/80s personal computing) that will eventually need to speak to humans visually/spatially rather than via raw text/chat, combining text generation, image generation, and world knowledge in one model [2026-06-24-2025-llm-year-in-review].

Karpathy's overall take: 2025 LLMs are simultaneously smarter and dumber than expected, the industry has realized "nowhere near 10%" of current-capability potential, and he expects both continued rapid progress and a large amount of remaining foundational work [2026-06-24-2025-llm-year-in-review].

## Key claims

- RLVR became the de facto new training stage beyond pretrain/SFT/RLHF in 2025, adding a test-time-compute "knob" (longer reasoning traces) as a new scaling axis [2026-06-24-2025-llm-year-in-review].
- OpenAI's o1 (late 2024) was the first RLVR demo; o3 (early 2025) was the point where the capability jump became intuitively obvious [2026-06-24-2025-llm-year-in-review].
- Karpathy (opinion): benchmarks are increasingly unreliable in 2025 because they're verifiable-by-construction and thus gameable via RLVR-adjacent training ("benchmaxxing") [2026-06-24-2025-llm-year-in-review].
- Karpathy (opinion): Claude Code's key innovation is running locally with the user's existing environment/data/secrets, not merely "being an agent" [2026-06-24-2025-llm-year-in-review].
- Karpathy says he personally coined the term "vibe coding" via a tweet, "totally oblivious to how far it would go" [2026-06-24-2025-llm-year-in-review].
- Karpathy (opinion): Google's Gemini "Nano Banana" model is an early sign of an emerging "LLM GUI" paradigm — image/infographic/video output as the natural interface for LLMs, not just chat text [2026-06-24-2025-llm-year-in-review].
- Karpathy (opinion): LLM labs will likely produce a generally-capable "college student" model while a separate layer of LLM apps (à la Cursor) verticalizes and deploys them as professionals [2026-06-24-2025-llm-year-in-review].

## Entities mentioned

- [[entities/andrej-karpathy]], [[entities/claude-code]], [[entities/cursor]], [[entities/openai]], [[entities/google]], [[entities/deepseek]]

## Concepts mentioned

- [[concepts/rlvr]], [[concepts/reinforcement-learning-from-human-feedback]], [[concepts/reasoning-models]], [[concepts/vibe-coding]], [[concepts/ai-agent]], [[concepts/jagged-intelligence]], [[concepts/benchmarking]]

## Source

`sources/2026-06-24-2025-llm-year-in-review.md`
