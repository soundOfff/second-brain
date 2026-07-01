---
id: 2026-06-29-max-models-can-now-run-on-apple-silicon-gpus
title: "MAX models can now run on Apple silicon GPUs"
type: article
url: https://forum.modular.com/t/max-models-can-now-run-on-apple-silicon-gpus/3283
captured: 2026-06-29
via: lobsters-ai
tags: [news, ai]
---

# MAX models can now run on Apple silicon GPUs

MAX

BradLarson  (Brad Larson)    June 27, 2026, 6:38pm   1

For the last several months, we’ve been progressively improving support for Mojo and MAX on Apple silicon GPUs, first unlocking the ability to program them via Mojo, then enabling basic MAX graphs to run on these GPUs. With the 26.4 release, many MAX models can now run on Apple silicon GPUs for the first time. Support for models has even gotten better in the nightlies since.

In the current nightlies, M1 through M5 Apple silicon GPUs are supported in MAX, and appropriately-sized text LLMs, vision models, and image diffusion models run across these devices. Due to the generational differences in Apple silicon GPUs, some models may not work as well on older M-series SoCs due to lack of testing (most of us are working on M3-M5 systems). If you encounter a combination of model / system that aren’t working right, please feel free to file an issue for us to track compatibility.

MAX models will run best on M5 systems, because they contain dedicated matrix-multiplication operations via the new Neural Accelerators. Preston and Fabio have been working on kernels specifically targeting those operations and while we haven’t yet benchmarked directly against MLX or other frameworks, we’ve seen some pretty fast model execution in anecdotal tests.

To try out a simple LLM on your Mac, you can set up MAX (or clone the modular repo) and run an invocation like the following to do direct text generation:

max generate --model-path=Qwen/Qwen3.5-0.8B --device-memory-utilization 0.5 --max-batch-size 1 --prompt "The sky is blue because"

or the following to start serving an endpoint on your machine:

max serve --model-path=Qwen/Qwen3.5-0.8B --device-memory-utilization 0.5 --max-batch-size 1

The --device-memory-utilization and --max-batch-size flags are there to limit the amount of memory MAX will try to allocate, because Apple silicon systems use shared memory between CPU and GPU.

If you have at least 15 GB of RAM available on your system after everything else that’s running, you can even use the FLUX.2 [klein] 4-billion-parameter image generation model directly on your Mac. To quickly generate an image, you can use our simple_offline_generation example from the modular repo:

./bazelw run //max/examples/diffusion:simple_offline_generation -- --model black-forest-labs/FLUX.2-klein-4B --num-inference-steps 4 --width 256 --height 256 --prompt "A beautiful sunset"

or serve an Open Responses endpoint with:

MAX_SERVE_API_TYPES='["responses"]' max serve --model-path black-forest-labs/FLUX.2-klein-4B

We’re working to improve model coverage and performance, and it’s possible you’ll notice temporary regressions in the nightlies as we tune kernels and work on models. There are many areas still to be optimized for specific models of Apple silicon GPUs, especially for pre-M5 systems. As always, follow the nightlies for the latest improvements here.

melodyogonna  (Melody Daniel)    June 28, 2026, 4:26pm   2

Are there plans to take advantage of Apple’s NPUs in the future?

### Related topics

Topic  Replies Views Activity

MAX Nightly 26.5.0.dev2026061906 (Mojo 1.0.0b3.dev2026061906) Released

Nightly

0   37   June 19, 2026

Porting various models to MAX

MAX

5   277   May 1, 2025

Will Max support cerebras.ai hardware?

MAX

discussion , gpu , modular-content , 24_6

3   413   December 28, 2024

New resources for building models in MAX

Models & Pipelines

gpu

0   130   June 27, 2025

MAX Model Repository

MAX

3   136   August 6, 2025
