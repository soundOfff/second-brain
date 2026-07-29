---
type: recap
title: "Recap — TIRx: An Open Compiler Stack for Evolving Frontier ML Kernels"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels]
tags: [ai, ml-kernels, compilers, gpu, open-source, apache-tvm]
---

# Recap — TIRx: An Open Compiler Stack for Evolving Frontier ML Kernels

The **[[entities/apache-tvm]]** community announced **[[entities/tirx]]**, an
open-source, hardware-native DSL and compiler for ML kernels built on Apache TVM,
targeting GPUs and specialized AI accelerators
[2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels]. Launch
materials include a PyPI wheel/Python frontend (`apache-tvm==0.25.0`), a kernel
library/benchmark suite covering GEMM, attention, and low-precision operators on
Blackwell GPUs, and an open GPU-programming course taught as part of a Carnegie Mellon
University ML systems course
[2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].

TIRx's design philosophy: keep orchestration (pipeline structure, synchronization, role
assignment, backend intrinsics) in explicit hardware-native source code rather than
hidden behind abstractions, while exposing recurring tile operations (copy, matmul) as
dispatchable **tile primitives** so they stay reusable and portable; new hardware
features enter first as raw intrinsics and get promoted to tile primitives once usage
patterns stabilize [2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].
The post positions TIRx as sitting at a lower, more explicit boundary than
**[[entities/triton]]** and below **[[entities/tilelang]]** — TIRx is meant as a
minimal foundation that TileLang could build on, and the authors say they are working
with the TileLang community toward that
[2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels]. TIRx's layout
system is contrasted with **[[entities/cutlass-cute]]**: CuTe exposes layout as a
programmable interface for deriving work partitioning, while TIRx treats layout purely
as a storage contract (mapping logical tensor coordinates to physical hardware
coordinates via shard/replica/offset components) consumed by primitive dispatch, not
as the surface for expressing transformations
[2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].

Benchmarked on 4x **[[entities/nvidia-blackwell]]** B200 (SM100) GPUs across 54
configurations (dense GEMM, block-scaled FP8/NVFP4 GEMM, FlashAttention-4), TIRx reaches
0.95–1.00x of the best specialized baselines (cuBLAS, DeepGEMM, FlashInfer, CuTeDSL
flashattn_sm100) depending on shape
[2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels]. The post
argues TIRx is well-suited to three emerging needs: (1) a stable extension boundary as
new hardware generations arrive, since new features grow the backend library rather than
the core language; (2) **[[concepts/megakernels]]** — TIRx tasks exist as compiler IR
so a higher-level megakernel compiler can stitch/schedule them directly (citing the
authors' own Event Tensor system, MLSys '26); and (3)
**[[concepts/agentic-kernel-programming]]** — TIRx exposes its IR via TVM FFI across
Python/C++/Rust for agent tooling, and its high-level tile primitives plus low-level
access are meant to give agentic search denser feedback signals (well-formedness,
synchronization validity, race-freedom, simulated correctness) than a
compile-run-benchmark-only loop
[2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels]. The post
sketches a four-level progression for agentic kernel optimization, from agents locally
tuning an already-optimized kernel (L1) to agents bootstrapping entire search spaces
from hardware docs and compiler feedback (L4), positioning TIRx as targeting the middle
of that spectrum [2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].

## Key claims

- TIRx is built on Apache TVM and ships today as a PyPI wheel (`apache-tvm==0.25.0`)
  plus a Python frontend, kernel library, and CMU-affiliated open course
  [2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].
- Design keeps orchestration explicit in source while exposing recurring tile
  operations as dispatchable tile primitives; new hardware enters as intrinsics first,
  primitives later [2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].
- TIRx sits below TileLang (which still leaves layout inference/thread binding to the
  compiler) and is intended as a minimal foundation TileLang could compile onto
  [2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].
- TIRx layout is a storage contract only (not a work-partitioning interface, unlike
  CuTe), supports general (non-power-of-two) shapes, and uses named hardware axes
  (e.g. `laneid`, `warpid`) [2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].
- On 4x NVIDIA B200, across 54 configs, TIRx reaches up to 1517 TFLOPS on BF16 GEMM
  (0.96x best baseline) and 5930 TFLOPS on NVFP4 GEMM (within 2% of best baseline)
  [2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].
- TIRx IR is exposed via TVM FFI across Python, C++, and Rust specifically to support
  agent-driven kernel experimentation
  [2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].
- The authors built Event Tensor (MLSys '26), a megakernel compiler using tiled tasks
  and dependency tensors on top of TIRx, with deeper integration planned
  [2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels].

## Entities mentioned

- [[entities/apache-tvm]], [[entities/tirx]], [[entities/triton]],
  [[entities/tilelang]], [[entities/cutlass-cute]], [[entities/nvidia-blackwell]]

## Concepts mentioned

- [[concepts/ml-kernel-compilation]], [[concepts/gpu-programming]],
  [[concepts/agentic-kernel-programming]], [[concepts/megakernels]]

## Source

`sources/2026-06-24-tirx-an-open-compiler-stack-for-evolving-frontier-ml-kernels.md`
