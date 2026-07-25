---
type: recap
title: "Recap — Event Tensor: A Unified Abstraction for Compiling Dynamic Megakernels"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-event-tensor-a-unified-abstraction-for-compiling-dynamic-meg]
tags: [gpu-compilers, llm-inference, arxiv]
---

# Recap — Event Tensor: A Unified Abstraction for Compiling Dynamic Megakernels

This source is the arXiv listing page (abstract only, no full text captured) for "Event Tensor: A Unified Abstraction for Compiling Dynamic Megakernel" by Hongyi Jin, Tianqi Chen, and 19 co-authors, accepted at MLSys 2026 [2026-06-24-event-tensor-a-unified-abstraction-for-compiling-dynamic-meg]. The paper addresses [[concepts/megakernel]] compilation: modern GPU workloads, especially LLM inference, suffer from kernel-launch overhead and coarse synchronization; megakernels fuse many operators into one persistent kernel to eliminate launch gaps, but existing megakernel approaches struggle with dynamic shapes and data-dependent computation [2026-06-24-event-tensor-a-unified-abstraction-for-compiling-dynamic-meg].

The authors propose "Event Tensor," a compiler abstraction that encodes dependencies between tiled tasks and supports both shape- and data-dependent dynamism as first-class concepts, plus an accompanying Event Tensor Compiler (ETC) that applies static and dynamic scheduling transformations to generate persistent kernels [2026-06-24-event-tensor-a-unified-abstraction-for-compiling-dynamic-meg]. The authors claim their evaluations show ETC achieves state-of-the-art LLM serving latency while significantly reducing system warmup overhead [2026-06-24-event-tensor-a-unified-abstraction-for-compiling-dynamic-meg].

## Key claims

- Event Tensor is proposed as a unified abstraction encoding dependencies between tiled tasks, supporting both shape-dependent and data-dependent dynamism for megakernel compilation [2026-06-24-event-tensor-a-unified-abstraction-for-compiling-dynamic-meg].
- The authors report ETC achieves state-of-the-art LLM serving latency and significantly reduces system warmup overhead versus prior megakernel approaches [2026-06-24-event-tensor-a-unified-abstraction-for-compiling-dynamic-meg].
- The paper was accepted at MLSys 2026 [2026-06-24-event-tensor-a-unified-abstraction-for-compiling-dynamic-meg].

## Entities mentioned

- (none warranting dedicated entity pages — paper authors not otherwise notable in this brain)

## Concepts mentioned

- [[concepts/megakernel]], [[concepts/llm-inference-serving]], [[concepts/gpu-kernel-fusion]]

## Source

`sources/2026-06-24-event-tensor-a-unified-abstraction-for-compiling-dynamic-meg.md`
