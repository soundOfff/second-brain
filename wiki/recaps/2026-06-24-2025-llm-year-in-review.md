---
type: recap
title: "Recap — 2025 LLM Year in Review (Karpathy)"
created: 2026-06-26
updated: 2026-06-26
status: stable
sources: [2026-06-24-2025-llm-year-in-review]
tags: [llm, year-in-review, agentic-coding, ai]
---

# Recap — 2025 LLM Year in Review (Karpathy)

[[entities/andrej-karpathy]]'s end-of-year list of the "paradigm changes" that
reshaped the LLM landscape in 2025 — things he found personally notable and "mildly
surprising" [2026-06-24-2025-llm-year-in-review].

## Key claims

1. **RLVR became the new major training stage.**
   [[concepts/reinforcement-learning-from-verifiable-rewards]] (RLVR) was added on top
   of the prior pretraining → SFT → RLHF recipe. Training against automatically
   verifiable rewards (math/code puzzles) made models spontaneously develop
   "reasoning" strategies. Unlike the thin SFT/RLHF stages, RLVR allows long
   optimization and offered high capability/$, so it "gobbled up" compute originally
   meant for pretraining — 2025 saw ~similar-sized models but much longer RL runs. It
   added a new test-time-compute scaling knob ("thinking time"). OpenAI o1 (late 2024)
   was the first RLVR demo; **o3** (early 2025) was the felt inflection point
   [2026-06-24-2025-llm-year-in-review].
2. **Ghosts vs. animals / jagged intelligence.** We are "summoning ghosts," not
   "growing animals" — LLMs are a different kind of entity, so
   [[concepts/jagged-intelligence]] is expected: simultaneously genius polymath and
   easily-tricked grade-schooler. RLVR makes capability "spike" near verifiable
   domains. Karpathy reports growing **apathy/loss of trust in benchmarks** because
   benchmarks are themselves verifiable environments susceptible to RLVR and synthetic
   data — "training on the test set is a new art form"
   [2026-06-24-2025-llm-year-in-review]. See [[concepts/ghosts-vs-animals]].
3. **Cursor revealed a new LLM-app layer.** [[entities/cursor]] convincingly showed a
   new "[[concepts/llm-app-layer]]" — people began saying "Cursor for X." Such apps do
   context engineering, orchestrate multiple LLM calls into DAGs balancing
   cost/performance, provide a vertical-specific GUI, and offer an "autonomy slider"
   [2026-06-24-2025-llm-year-in-review].
4. **Claude Code / AI that lives on your computer.** [[entities/claude-code]] was the
   first convincing LLM **agent** (looping tool-use + reasoning) and, crucially, runs
   locally with your private environment, data, and context. Karpathy argues
   [[entities/openai]] got the order wrong by focusing early Codex/agent efforts on
   cloud containers; [[entities/anthropic]] correctly prioritized the already-booted-up
   local computer and packaged CC as a minimal CLI — "a little spirit/ghost that lives
   on your computer," a new interaction paradigm [2026-06-24-2025-llm-year-in-review].
5. **Vibe coding.** 2025 crossed the threshold where impressive programs can be built
   purely in English. [[concepts/vibe-coding]] (a term Karpathy coined) puts programming
   within reach of anyone and lets professionals write far more software — code became
   "free, ephemeral, malleable, discardable" (e.g. a throwaway app to find one bug)
   [2026-06-24-2025-llm-year-in-review].
6. **Nano Banana / the LLM GUI.** Google Gemini's [[entities/google-gemini]] "Nano
   Banana" image model is an early hint of the [[concepts/llm-gui]] — LLMs speaking to
   humans in their favored visual/spatial formats (images, infographics, slides) rather
   than console-like text. Its power comes from text + image generation + world
   knowledge tangled in one model [2026-06-24-2025-llm-year-in-review].

**TLDR.** LLMs are a new kind of intelligence — smarter and dumber than expected,
extremely useful, with <10% of potential realized; the field feels "wide open"
[2026-06-24-2025-llm-year-in-review].

## Entities mentioned

- [[entities/andrej-karpathy]], [[entities/claude-code]], [[entities/openai]],
  [[entities/anthropic]], [[entities/cursor]], [[entities/google-gemini]]
- DeepSeek (R1 paper cited as an RLVR reasoning example)

## Concepts mentioned

- [[concepts/reinforcement-learning-from-verifiable-rewards]],
  [[concepts/jagged-intelligence]], [[concepts/ghosts-vs-animals]],
  [[concepts/llm-app-layer]], [[concepts/vibe-coding]], [[concepts/llm-gui]],
  [[concepts/verifiability]]

## Source

`sources/2026-06-24-2025-llm-year-in-review.md` — blog post, 19 Dec 2025
(captured via the `andrej-karpathy` feed).
