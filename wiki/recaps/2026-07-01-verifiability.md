---
type: recap
title: "Recap — Verifiability"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-01-verifiability]
tags: [ai, software-2.0, verifiability, essay]
---

# Recap — Verifiability

A short essay by **[[entities/andrej-karpathy]]** arguing that AI is best understood as a
new computing paradigm, and that within this paradigm the single most predictive feature
of whether a task/job gets automated is **[[concepts/verifiability]]**, not specifiability
[2026-07-01-verifiability]. He contrasts this with his earlier "Software 1.0" framing:
hand-written programs automate what you can *specify* (rote, easy-to-encode algorithms
like typing or bookkeeping); "Software 2.0" — programs found via gradient descent by
specifying an objective — instead automates what you can *verify*
[2026-07-01-verifiability].

Karpathy defines a verifiable task/environment as one that is resettable (a new attempt
can be started), efficient (many attempts can be made), and rewardable (there is an
automated process to score any given attempt) [2026-07-01-verifiability]. He argues this
is what drives the "jagged" frontier of LLM progress: verifiable tasks (math, code,
puzzle-like problems with checkable answers) progress rapidly, sometimes beyond expert
human ability, while tasks that combine real-world knowledge, state, context, and common
sense — or that are creative or strategic — lag, since they can only improve via weaker
means like imitation or emergent generalization [2026-07-01-verifiability].

## Key claims

- Karpathy's position: in the AI/Software 2.0 paradigm, verifiability (not specifiability)
  is the most predictive feature of whether a task/job will be automated
  [2026-07-01-verifiability].
- He defines a verifiable environment as resettable, efficient (many attempts possible),
  and rewardable (automated scoring exists) [2026-07-01-verifiability].
- Software 1.0 automates what you can specify; Software 2.0 automates what you can verify
  — his framing for why LLM progress is "jagged" across tasks [2026-07-01-verifiability].
- Verifiable tasks (math, code, puzzle-like problems) are cited as progressing rapidly,
  sometimes beyond top human experts; less-verifiable tasks (creative, strategic, tasks
  requiring real-world context/common sense) are cited as lagging
  [2026-07-01-verifiability].

## Entities mentioned

- [[entities/andrej-karpathy]]

## Concepts mentioned

- [[concepts/verifiability]], [[concepts/software-2-0]]

## Source

`sources/2026-07-01-verifiability.md`
