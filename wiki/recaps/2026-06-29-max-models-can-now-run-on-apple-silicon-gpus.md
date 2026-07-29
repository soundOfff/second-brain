---
type: recap
title: "Recap — MAX models can now run on Apple silicon GPUs"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-29-max-models-can-now-run-on-apple-silicon-gpus]
tags: [inference, apple-silicon, gpu, local-llms, modular]
---

# Recap — MAX models can now run on Apple silicon GPUs

Forum announcement by **Brad Larson** of [[entities/modular]] on the Modular community
forum, announcing that as of the 26.4 release, [[entities/max|MAX]] (Modular's model
serving/inference framework) can run many models directly on Apple silicon GPUs, after
months of incremental work first enabling [[entities/mojo]] programming on those GPUs
and then basic MAX graph execution [2026-06-29-max-models-can-now-run-on-apple-silicon-gpus].
Current nightlies support M1 through M5 chips for appropriately-sized text LLMs, vision
models, and image diffusion models, though older pre-M3 chips may see weaker support
since most of Modular's own testing happens on M3–M5 [2026-06-29-max-models-can-now-run-on-apple-silicon-gpus].

M5 systems are highlighted as the best target because they expose dedicated
matrix-multiplication hardware via Apple's new Neural Accelerators, which Modular
engineers have been writing kernels for; the post notes anecdotally fast execution but
no formal benchmark yet against [[entities/mlx|MLX]] or other frameworks
[2026-06-29-max-models-can-now-run-on-apple-silicon-gpus]. The post gives example CLI
invocations for running [[entities/qwen|Qwen3.5-0.8B]] via `max generate`/`max serve`,
and for running the 4-billion-parameter **FLUX.2 [klein]** image-generation model
(from [[entities/black-forest-labs]]) locally, given at least 15GB of free RAM, using
`--device-memory-utilization` and `--max-batch-size` flags to manage the shared
CPU/GPU memory pool on Apple hardware [2026-06-29-max-models-can-now-run-on-apple-silicon-gpus].
The author flags that coverage and performance are still being tuned, with possible
temporary regressions in the nightlies, and a forum reply from Melody Daniel asks about
future NPU support, which is left unanswered in this source
[2026-06-29-max-models-can-now-run-on-apple-silicon-gpus].

## Key claims

- With the 26.4 release, MAX can run appropriately-sized text LLMs, vision models, and image diffusion models on Apple silicon GPUs (M1–M5) [2026-06-29-max-models-can-now-run-on-apple-silicon-gpus].
- M5 chips are expected to run MAX models best due to dedicated matrix-multiplication "Neural Accelerator" hardware, though no formal benchmark vs. MLX or other frameworks had been published at time of writing [2026-06-29-max-models-can-now-run-on-apple-silicon-gpus].
- Apple silicon's shared CPU/GPU memory requires explicit `--device-memory-utilization` and `--max-batch-size` limits when running MAX models [2026-06-29-max-models-can-now-run-on-apple-silicon-gpus].
- The 4B-parameter FLUX.2 [klein] image diffusion model can run locally on Mac with ~15GB free RAM via MAX's offline generation example [2026-06-29-max-models-can-now-run-on-apple-silicon-gpus].
- Older, pre-M3 Apple silicon GPUs may have weaker MAX model compatibility due to limited testing coverage on those generations [2026-06-29-max-models-can-now-run-on-apple-silicon-gpus].

## Entities mentioned

- [[entities/modular]], [[entities/max]], [[entities/mojo]], [[entities/brad-larson]], [[entities/apple-silicon]], [[entities/qwen]], [[entities/black-forest-labs]], [[entities/mlx]]

## Concepts mentioned

- [[concepts/edge-ai-inference]], [[concepts/local-llms]], [[concepts/gpu-programming]], [[concepts/quantization]]

## Source

`sources/2026-06-29-max-models-can-now-run-on-apple-silicon-gpus.md`
