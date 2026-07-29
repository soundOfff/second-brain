---
type: recap
title: "Recap — Sequoia Ascent 2026: Software 3.0, Agentic Engineering, Jagged Intelligence"
created: 2026-06-26
updated: 2026-06-26
status: stable
sources: [2026-06-24-sequoia-ascent-2026-summary]
tags: [llm, agentic-coding, software-3-0, verifiability, ai]
---

# Recap — Sequoia Ascent 2026 (Karpathy × Stephanie Zhan)

A fireside chat by [[entities/andrej-karpathy]] with Stephanie Zhan at
[[entities/sequoia-capital]]'s Ascent 2026 (30 Apr 2026). The source bundles an
AI-generated summary **and** a cleaned-up transcript that Karpathy himself produced by
feeding a top model (Codex 5.5) his blog/tweets plus the video transcript — itself an
example of the [[concepts/llm-gui]] / agent-native-content idea
[2026-06-24-sequoia-ascent-2026-summary].

## Key claims

1. **December 2025 was an agentic inflection point.** Generated chunks suddenly became
   large, coherent, and reliable; Karpathy "started trusting the agents" and felt "more
   behind as a programmer." The unit of programming shifted from typing lines to
   delegating "macro actions" (implement a feature, refactor a subsystem, write+run
   tests). The programmer becomes an **orchestrator of agents**
   [2026-06-24-sequoia-ascent-2026-summary].
2. **[[concepts/software-3-0]].** Software 1.0 = explicit code; 2.0 = learned weights;
   3.0 = programming LLMs through prompts/context/tools. The **context window is the new
   program** and the LLM is its interpreter. Example: an installer becomes a pasteable
   block of instructions the agent adapts to your machine, instead of a brittle shell
   script [2026-06-24-sequoia-ascent-2026-summary].
3. **MenuGen / "software disappears."** MenuGen (photo of a menu → OCR → generated dish
   images) needed a whole web stack; the Software 3.0 version just hands the photo to a
   multimodal model that renders dishes onto the menu image directly. "Some apps should
   stop existing as apps." Extrapolated: **neural computers** where the neural net is
   the host process and CPUs are coprocessors [2026-06-24-sequoia-ascent-2026-summary].
4. **The new opportunity is not just faster coding.** LLMs make previously
   non-programmable information transformations possible — his
   [[concepts/llm-wiki]] knowledge-base pattern is the clearest example: an agent
   incrementally compiles messy sources into a persistent wiki, which no classical
   program could robustly do. Ask "what was impossible before but is now natural?"
   [2026-06-24-sequoia-ascent-2026-summary].
5. **[[concepts/verifiability]].** Traditional software automates what you can
   *specify*; LLMs/RL automate what you can *verify*. Tasks with automatic
   reward/success signals (math, code, tests, games) improve fastest — which is why
   coding agents feel far better than ordinary chatbots
   [2026-06-24-sequoia-ascent-2026-summary].
6. **Jagged intelligence has two axes.** Capability ≈ verifiability × training
   attention × data coverage × economic value. Chess improved partly because more chess
   data was added, not just from general progress. Frontier models "have no manual";
   the founder question is "are you on the model's rails?" See
   [[concepts/jagged-intelligence]] [2026-06-24-sequoia-ascent-2026-summary].
7. **Vibe coding vs. [[concepts/agentic-engineering]].** [[concepts/vibe-coding]] raises
   the floor (anyone can build); agentic engineering raises the ceiling (the discipline
   of coordinating fallible agents while preserving correctness, security, taste). The
   MenuGen payment bug — matching Stripe and Google emails instead of using persistent
   user IDs — shows why human system judgment is still required. The "10x engineer" may
   become far more extreme [2026-06-24-sequoia-ascent-2026-summary].
8. **Hiring should change.** Replace coding puzzles with "build a substantial project
   with agents, deploy it, secure it, then have adversarial agents try to break it"
   [2026-06-24-sequoia-ascent-2026-summary].
9. **Founder wedge: valuable, verifiable, undertrained domains.** Where you can build an
   RL environment with reliable rewards, you can fine-tune/RL even if the base model is
   weak there. Coding/math are saturated by labs; latent verifiable structure elsewhere
   is the opportunity [2026-06-24-sequoia-ascent-2026-summary].
10. **[[concepts/agent-native-infrastructure]].** Most software is built for humans
    clicking screens, but increasingly the user is the human's agent. Products need
    agent-native surfaces (markdown docs, CLIs, APIs, MCP servers, structured logs,
    machine-readable schemas, safe permissioning, headless setup). Framed as "sensors
    and actuators." Deploying MenuGen (Vercel, auth, payments, DNS, secrets) was harder
    than building it [2026-06-24-sequoia-ascent-2026-summary].
11. **[[concepts/ghosts-vs-animals]].** LLMs aren't animals (no biological drives); they
    are statistical simulations of human artifacts. Anthropomorphic expectations
    mislead. Right posture: empirical familiarity + guardrails
    [2026-06-24-sequoia-ascent-2026-summary].
12. **Education: outsource thinking, not understanding.** "You can outsource your
    thinking, but you can't outsource your understanding" — the human stays the
    bottleneck for direction, taste, and knowing when a result is suspicious. LLM
    knowledge bases and his single-file microGPT are tools for turning information into
    understanding. See [[concepts/outsourcing-thinking-vs-understanding]]
    [2026-06-24-sequoia-ascent-2026-summary].

## Entities mentioned

- [[entities/andrej-karpathy]], [[entities/sequoia-capital]] (Stephanie Zhan,
  interviewer), [[entities/claude-code]], [[entities/codex]], [[entities/openai]],
  [[entities/cursor]], [[entities/google-gemini]] (Nano Banana). Karpathy's bio:
  ex-Tesla Autopilot, OpenAI co-founder, founder of Eureka Labs.

## Concepts mentioned

- [[concepts/software-3-0]], [[concepts/verifiability]],
  [[concepts/jagged-intelligence]], [[concepts/agentic-engineering]],
  [[concepts/vibe-coding]], [[concepts/agent-native-infrastructure]],
  [[concepts/ghosts-vs-animals]], [[concepts/llm-wiki]], [[concepts/llm-gui]],
  [[concepts/outsourcing-thinking-vs-understanding]],
  [[concepts/reinforcement-learning-from-verifiable-rewards]]

## Source

`sources/2026-06-24-sequoia-ascent-2026-summary.md` — fireside chat write-up + edited
transcript, 30 Apr 2026 (captured via the `andrej-karpathy` feed).
