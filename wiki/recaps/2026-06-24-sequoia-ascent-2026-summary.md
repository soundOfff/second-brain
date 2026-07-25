---
type: recap
title: "Recap — Sequoia Ascent 2026 Summary"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-sequoia-ascent-2026-summary]
tags: [ai, agentic-engineering, software-3-0, karpathy, essay]
---

# Recap — Sequoia Ascent 2026 Summary

An AI-generated summary and cleaned transcript of a fireside chat between
**[[entities/andrej-karpathy]]** and Sequoia's **[[entities/stephanie-zhan]]** at
**[[entities/sequoia-capital]]**'s Ascent 2026 event. Karpathy himself notes the summary
and transcript were produced by feeding an LLM his blog posts/tweets plus the talk's
transcript, then cleaning it up with a "top capability model" (Codex 5.5)
[2026-06-24-sequoia-ascent-2026-summary]. The talk argues that December 2025 marked an
"agentic inflection point" after which coding agents like **[[entities/claude-code]]**
and **[[entities/codex]]** began producing large, coherent, trustworthy chunks of work
without frequent correction, shifting programming from writing lines of code to
delegating "macro actions" to agents [2026-06-24-sequoia-ascent-2026-summary].

Karpathy frames this as **[[concepts/software-3-0]]**: Software 1.0 is explicit code,
Software 2.0 is learned weights/datasets, and Software 3.0 is programming LLMs via
prompts, context, tools, and instructions, with the context window as the main lever
[2026-06-24-sequoia-ascent-2026-summary]. He illustrates this with his **MenuGen**
project — a traditional app (OCR, image generation, auth, payments) that in a
"Software 3.0" version collapses into a single multimodal-model call that overlays
dish images directly onto a photographed menu, implying some apps "should stop existing
as apps" [2026-06-24-sequoia-ascent-2026-summary]. He also cites his own
**[[concepts/llm-wiki]]** project (used as the design pattern for this very second-brain
repository) as an example of an information transformation — compiling messy documents
into a persistent, cross-linked wiki — that was not possible with classical software
[2026-06-24-sequoia-ascent-2026-summary].

Two recurring frameworks structure the talk. First, **[[concepts/verifiability]]**:
"traditional software automates what you can specify; LLMs and RL automate what you can
verify" — capability spikes where a task is verifiable *and* labs have devoted training
attention to it (his example: chess improved sharply from GPT-3.5 to GPT-4 largely
because more chess data entered the training mix, not just general capability growth)
[2026-06-24-sequoia-ascent-2026-summary]. This produces **[[concepts/jagged-intelligence]]**
— models that can refactor 100k-line codebases yet answer confidently wrong on trivial
tasks (e.g., recommending walking a 50-meter "drive vs. walk" question)
[2026-06-24-sequoia-ascent-2026-summary]. Second, he distinguishes **[[concepts/vibe-coding]]**
(raises the floor — lets anyone build software by describing intent) from
**[[concepts/agentic-engineering]]** (raises the ceiling — the professional discipline of
supervising fallible agents while preserving correctness, security, and taste)
[2026-06-24-sequoia-ascent-2026-summary]. His running example of an agent mistake is a
MenuGen payment bug where an agent matched Stripe purchases to Google accounts by email
address rather than persistent user ID — plausible code, bad system design
[2026-06-24-sequoia-ascent-2026-summary].

Other threads: his **[[concepts/animals-vs-ghosts]]** framing (LLMs are not
animal-like intelligences with biological drives; they are "statistical simulation
circuits" shaped by pretraining and RL, so they should be treated empirically rather
than anthropomorphized) [2026-06-24-sequoia-ascent-2026-summary]; a call for
**agent-native infrastructure** — docs, CLIs, APIs, and MCP servers built for agents
rather than humans clicking through UIs, framed as "sensors and actuators"
[2026-06-24-sequoia-ascent-2026-summary]; hiring advice to replace coding puzzles with
"build and secure a real project with agents, then have adversarial agents try to break
it" [2026-06-24-sequoia-ascent-2026-summary]; and a closing line he attributes to a tweet
he liked: "You can outsource your thinking, but you can't outsource your understanding"
— used to argue that human understanding remains the bottleneck for directing agents
[2026-06-24-sequoia-ascent-2026-summary]. He also references his **microGPT** project (a
dependency-free single-file GPT trainer/inference implementation) as an educational
artifact, and notes he co-founded **[[entities/openai]]**, worked on Autopilot at
**[[entities/tesla]]**, and founded **[[entities/eureka-labs]]**
[2026-06-24-sequoia-ascent-2026-summary].

## Key claims

- Karpathy says he "never felt more behind as a programmer," dating a step-change in
  agent reliability to around December 2025 [2026-06-24-sequoia-ascent-2026-summary].
- Proposed automation formula: `capability spike ~= verifiability x training attention x
  data coverage x economic value` [2026-06-24-sequoia-ascent-2026-summary].
- MenuGen's "Software 3.0" version replaces an entire app stack (OCR, image gen, UI)
  with a single multimodal prompt to overlay dish images onto a menu photo
  [2026-06-24-sequoia-ascent-2026-summary].
- Karpathy's [[concepts/llm-wiki]] pattern compiles raw sources into a persistent
  Markdown wiki (summaries, entity/concept pages, contradictions, cross-links) —
  something no classical program could robustly do [2026-06-24-sequoia-ascent-2026-summary].
- Vibe coding raises the floor of who can build software; agentic engineering raises the
  ceiling of professional-grade output while using agents
  [2026-06-24-sequoia-ascent-2026-summary].
- Proposed hiring test: have a candidate build and secure a real project with agents,
  then have adversarial agents try to break it, instead of algorithmic puzzles
  [2026-06-24-sequoia-ascent-2026-summary].
- Chess capability jumps from GPT-3.5 to GPT-4 are attributed (per Karpathy) to
  increased chess data in the pretraining mix, not pure general-intelligence gains
  [2026-06-24-sequoia-ascent-2026-summary].
- The "drive vs. walk 50 meters" and (patched) "letters in strawberry" examples are cited
  as evidence of jagged intelligence in otherwise highly capable frontier models
  [2026-06-24-sequoia-ascent-2026-summary].
- Karpathy's Animals vs. Ghosts framing: LLMs lack biological drives/curiosity and should
  be treated as jagged, alien statistical tools, not anthropomorphized
  [2026-06-24-sequoia-ascent-2026-summary].
- Quoted aphorism (from a tweet Karpathy liked): "You can outsource your thinking, but
  you can't outsource your understanding" [2026-06-24-sequoia-ascent-2026-summary].

## Entities mentioned

- [[entities/andrej-karpathy]], [[entities/stephanie-zhan]], [[entities/sequoia-capital]],
  [[entities/openai]], [[entities/tesla]], [[entities/claude-code]], [[entities/codex]],
  [[entities/menugen]], [[entities/microgpt]], [[entities/eureka-labs]]

## Concepts mentioned

- [[concepts/software-3-0]], [[concepts/vibe-coding]], [[concepts/agentic-engineering]],
  [[concepts/verifiability]], [[concepts/jagged-intelligence]],
  [[concepts/animals-vs-ghosts]], [[concepts/llm-wiki]]

## Source

`sources/2026-06-24-sequoia-ascent-2026-summary.md`
