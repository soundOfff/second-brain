---
type: recap
title: "Recap — Reverse Engineering the Qualcomm NPU Compiler"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler]
tags: [reverse-engineering, edge-ai, npu, compilers, qualcomm]
---

# Recap — Reverse Engineering the Qualcomm NPU Compiler

A technical writeup by Sagnik Bhattacharjee (datavorous), an edge-ML engineer, describing how he reverse-engineered a stripped [[entities/qualcomm]] QAIRT NPU compiler binary (`libHtpPrepare.so`, QNPU SDK v2.46.0.260424) using Ghidra decompilation, surviving unmangled symbol names, and empirical parameter sweeping, because he found Qualcomm's public NPU documentation inadequate [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler]. He explicitly credits using [[entities/claude-code]] for the reversing work [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].

The core problem the compiler solves is placement: the Hexagon NPU has a small on-chip scratchpad (VTCM, vector tightly coupled memory) versus slow main DDR memory, and the compiler must decide which tensors sit in VTCM at each point in execution, spilling/filling the rest to/from DDR [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler]. The author's headline findings: the compiler's scheduler uses a "Priority BFS" over a topological ordering (with tie-break heuristics like graph distance and branch weight) to minimize peak working-set size, then a fallback path places tensors via a recursive 3D-coordinate backtracking allocator; but when it can, the compiler instead formulates VTCM placement as a formal Mixed Integer Linear Program and solves it with [[concepts/mixed-integer-linear-programming]] solver HiGHS — something the author says was previously undocumented publicly [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler]. He also found the compiler can silently downcast tensor precision (float32 → FP16/BF16, via `relaxed_precision_cast` operations) during placement to relieve memory pressure, without the user being informed [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].

To estimate cost for scheduling/placement decisions before any real hardware run, the compiler embeds an internal analytical simulator the author dubs "Hextimate," which models compute and memory-movement cost separately, accounts for contention, returns a best/worst-case range rather than one number, and — for the memory side — implements a standard [[concepts/roofline-model]] (`bandwidth = channels × width × efficiency × frequency`), a formula the author says he recovered from the decompiled machine code with help from Claude Sonnet 4.6 [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler]. He notes the cost model has dedicated detectors/pricing for FlashAttention, MoE, KV-cache, and rotary embeddings, i.e. it is biased toward LLM workloads [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler]. He explicitly checked for and ruled out a learned/ML model driving compile-time decisions despite suggestive internal names — the cost path turned out to be a plain CSV lookup table [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].

The author caveats his own findings heavily: this reflects one SDK version of one binary and could change in other releases; he could not recover actual VTCM capacities (only a mysterious "4" field common across different chips); and he says this level of RE was "only possible with the help of Claude Code," urging readers to weigh claims accordingly [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].

## Key claims

- On an SM8350, a Qwen 0.8B model spilled 5.46 MB and filled 33.9 MB (37.9 MB DDR traffic); on an SM8650 (V75), nothing spilled and DDR read was only 1.15 MB — a ~33x difference — despite both chips reporting the same VTCM size field (value "4", units unknown) [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].
- A `spillFillBufferSize` metadata field of 0 in the compiled binary indicates model weights fit entirely on-chip, usable as a static fit/spill oracle [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].
- VTCM placement, when using the full optimizer, is solved as a formal MILP via HiGHS, minimizing total bytes moved (DDR spill/fill plus inter-core traffic on multi-core chips); the compiler dumps the problem to `.mps` files for debugging [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].
- The compiler can automatically downgrade tensor precision (e.g., FP32→FP16/BF16) during placement to relieve memory pressure, without user awareness [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].
- The internal simulator "Hextimate" prices integer vs. float compute separately, multicast vs. unicast writes separately, and gives KV-cache/weight tensors a distinct "fast DDR" cost factor [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].
- The author found no evidence of a weight-bearing learned model running at compile time; the apparent ML-sounding cost logic is a static CSV lookup table, with `special_mlp_features` actually being a Python feature-export function for offline training [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].
- The compiler also does graph min-cut partitioning for spill decisions, concatenation-elision via direct producer writes, im2col-based convolution-to-matmul lowering, and duplicate-op merging via checksumming [2026-06-29-reverse-engineering-the-qualcomm-npu-compiler].

## Entities mentioned

- [[entities/qualcomm]], [[entities/claude-code]]

## Concepts mentioned

- [[concepts/npu-compiler]], [[concepts/mixed-integer-linear-programming]], [[concepts/roofline-model]], [[concepts/reverse-engineering]], [[concepts/edge-ai-inference]]

## Source

`sources/2026-06-29-reverse-engineering-the-qualcomm-npu-compiler.md`
