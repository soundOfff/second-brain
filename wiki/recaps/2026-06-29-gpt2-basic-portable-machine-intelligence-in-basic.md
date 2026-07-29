---
type: recap
title: "Recap — GPT2-BASIC: Portable Machine Intelligence in BASIC"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic]
tags: [local-llms, retro-computing, transformers, edge-ai, dos]
---

# Recap — GPT2-BASIC: Portable Machine Intelligence in BASIC

[[entities/gpt2-basic]] is a GitHub project by developer **tsotchke** that implements a
GPT-style transformer and assistant runtime in BASIC, designed to run on DOS-class 486
hardware [2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic]. It compiles
under DOS FreeBASIC, uses [[concepts/quantization|Q20.12 fixed-point]] weights instead of
floating point, and performs real GPT-2-architecture inference (causal
[[concepts/transformer-architecture|attention]], layer norms, learned token/position
embeddings) with integer arithmetic, targeting machines with as little as 32MB of RAM
[2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic]. The project's core claim
is that language-model inference is a portable algorithm, not something intrinsically
tied to GPUs or modern frameworks — it draws explicit inspiration from 486-era
techniques such as fixed-point math (Doom, Quake), memory streaming (Wing Commander),
and demoscene-style bit-packing "poor man's SIMD"
[2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic].

The current promoted checkpoint (`MODEL_LEXICON_GOLD_V4_S3000`) is a 2-layer,
48-dimensional, 4-head, 192-context-token model with 463,168 parameters and a
4096-token lexicon vocabulary [2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic].
Measured in QEMU emulation of a 486DX2/66, the full-resident model generates at 2.46
tokens/sec; an optional q4/log-compressed token+head variant trades some speed
(2.12 tok/s) for roughly 53% less runtime memory (974,724 bytes vs. 2,055,940 bytes),
and a fully streamed-head fallback drops to 0.81 tok/s but uses only 616,324 bytes
[2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic]. The repo also ships a
pack-based assistant shell (CHAT, DOSHELP, OFFICE, DEV, PORTABLE packs) with session
memory, golden replies, and a KDB/KB2 indexed local-recall system, plus extensive QEMU-
based validation/evidence tooling; physical 486 hardware timing is explicitly flagged
as still pending, so current performance claims are QEMU-only
[2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic]. The author frames the
result not as competing with modern hosted LLMs, but as a proof that the full local-AI
loop (weights, tokenizer, inference, retrieval, validation) can run end-to-end on
severely constrained, legacy hardware [2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic].

## Key claims

- GPT2-BASIC runs real GPT-2-style transformer inference (not a mock or API wrapper) inside DOS FreeBASIC on emulated 486-class hardware [2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic].
- The default checkpoint has 463,168 parameters, 2 layers, 48 embedding dims, 4 heads, and a 192-token context window [2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic].
- QEMU 486DX2/66 evidence: 2.46 tok/s full-resident, 2.12 tok/s with q4/log token+head compression (~53% memory savings), 0.81 tok/s with streamed output-head (~70% memory savings) [2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic].
- The design uses Q20.12 signed fixed-point weights rather than floating point, chosen for determinism, 486SX (no-FPU) compatibility, and parity-checkability against a host float reference [2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic].
- The output head's vocabulary scoring takes about 73.7% of measured decode time, making vocabulary-head compression the main performance target [2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic].
- The project explicitly distinguishes QEMU-emulated evidence from physical-hardware evidence, which had not yet been captured at time of writing [2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic].

## Entities mentioned

- [[entities/gpt2-basic]], [[entities/tsotchke]]

## Concepts mentioned

- [[concepts/quantization]], [[concepts/transformer-architecture]], [[concepts/edge-ai-inference]], [[concepts/local-llms]], [[concepts/fixed-point-arithmetic]]

## Source

`sources/2026-06-29-gpt2-basic-portable-machine-intelligence-in-basic.md`
