---
type: concept
title: Vibe Coding
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-2025-llm-year-in-review, 2026-06-24-sequoia-ascent-2026-summary, 2026-06-24-opfs-pyodide-test-harness]
tags: [llm, agentic-coding, software, ai]
aliases: [vibe code]
---

# Vibe Coding

Building software by **describing what you want in English** and largely "forgetting that
the code even exists." [[entities/andrej-karpathy]] coined the term in a 2025 "shower of
thoughts" tweet, "totally oblivious to how far it would go"
[2026-06-24-2025-llm-year-in-review].

## What changed

2025 crossed the capability threshold to build "all kinds of impressive programs simply
via English" [2026-06-24-2025-llm-year-in-review]. Two effects:

- **It raises the floor.** Programming is no longer reserved for trained professionals —
  anyone can do it. Karpathy ties this to his "Power to the people" thesis that, unlike
  prior technology, regular people benefit more from LLMs than corporations or
  governments do [2026-06-24-2025-llm-year-in-review].
- **Code becomes free and disposable.** Professionals write far more software that would
  otherwise never exist; code is "free, ephemeral, malleable, discardable after single
  use" — Karpathy has vibe-coded entire **ephemeral apps just to find a single bug**
  [2026-06-24-2025-llm-year-in-review]. ([[entities/simon-willison]]'s OPFS playground is
  a real-world instance — a throwaway UI built to probe browser behaviour
  [2026-06-24-opfs-pyodide-test-harness].)

Examples Karpathy cites: a custom BPE tokenizer in Rust for nanochat (without learning
Rust at that level), plus menugen, llm-council, reader3, and an HN time capsule
[2026-06-24-2025-llm-year-in-review].

## Vibe coding vs. agentic engineering

> Vibe coding raises the **floor**. [[concepts/agentic-engineering]] raises the
> **ceiling** [2026-06-24-sequoia-ascent-2026-summary].

Vibe coding is fine for prototypes and personal tools, but you remain responsible for
your software — "you are not allowed to introduce vulnerabilities because of vibe
coding." Serious teams need agentic engineering: the discipline of going faster *without*
sacrificing correctness, security, and taste [2026-06-24-sequoia-ascent-2026-summary].
"Vibe coding will terraform software and alter job descriptions"
[2026-06-24-2025-llm-year-in-review].
