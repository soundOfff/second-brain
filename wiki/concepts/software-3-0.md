---
type: concept
title: Software 3.0
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-sequoia-ascent-2026-summary]
tags: [llm, software, paradigm, ai]
aliases: [Software 3.0, context window as program]
---

# Software 3.0

[[entities/andrej-karpathy]]'s name for the third paradigm of programming
[2026-06-24-sequoia-ascent-2026-summary]:

- **Software 1.0** — humans write explicit code.
- **Software 2.0** — humans create datasets, objectives, and neural networks; the
  program is *learned* into weights.
- **Software 3.0** — humans **program LLMs through prompts, context, tools, examples,
  memory, and instructions** [2026-06-24-sequoia-ascent-2026-summary].

## The context window is the new program

In Software 3.0 the **context window is the main lever** and the LLM is an **interpreter**
over that context, performing computation in digital-information space. Once GPT/LLMs are
trained on a sufficiently large set of tasks, they become "programmable computers in a
certain sense" [2026-06-24-sequoia-ascent-2026-summary].

The canonical example is **installation**: instead of a brittle shell script full of
per-platform conditionals (Software 1.0), the installer becomes a **block of text you
paste into an agent** that reads the local environment, debugs errors, and adapts. "Less
precise, but more adaptive." So "what is the piece of text to copy-paste into your agent"
becomes part of the programming paradigm [2026-06-24-sequoia-ascent-2026-summary].

## Software can disappear

Software 3.0 lets the neural network do more of the work directly, so some apps should
**stop existing as apps** — the MenuGen example, where a multimodal model renders dish
images onto a menu photo, eliminates most of the old web stack. Extrapolated to "neural
computers," see [[concepts/llm-gui]] [2026-06-24-sequoia-ascent-2026-summary]. It also
makes previously non-programmable information transformations possible — e.g. the
[[concepts/llm-wiki]] knowledge-base pattern
[2026-06-24-sequoia-ascent-2026-summary].

## Related

The disciplined practice of building in this paradigm is
[[concepts/agentic-engineering]]; its low-floor counterpart is [[concepts/vibe-coding]];
its infrastructure implication is [[concepts/agent-native-infrastructure]].
