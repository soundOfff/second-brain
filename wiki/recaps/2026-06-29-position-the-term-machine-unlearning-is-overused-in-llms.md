---
type: recap
title: "Recap — Position: The Term \"Machine Unlearning\" Is Overused in LLMs"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms]
tags: [paper, machine-unlearning, llm-alignment, terminology]
---

# Recap — Position: The Term "Machine Unlearning" Is Overused in LLMs

An ICML 2026 Position Paper Track paper (Sangyeon Yoon, Yeachan Jun, Albert No) arguing
that **[[concepts/machine-unlearning]]** is used too loosely in LLM research
[2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms]. The authors'
position is that the term should be reserved specifically for *dataset-defined deletion*:
removing the training influence of a precisely specified "forget set" such that the
resulting model is approximately indistinguishable from one retrained without that data
[2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms].

They argue many tasks currently labeled "unlearning" — refusal for harmful requests,
entity/knowledge removal, targeted suppression — actually pursue different,
policy-dependent objectives and should instead be called alignment, suppression, editing,
or obfuscation [2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms]. The
authors contend this is not merely a labeling quibble: because different papers make
different implicit guarantees under the same "unlearning" label, metrics and benchmarks
get reused outside their intended scope, rewarding surface-level non-disclosure (e.g. low
ROUGE / forget-accuracy scores) even when retraining-equivalence is never tested and the
underlying capability is still present in the model
[2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms]. They call for
stricter terminology tied to explicit guarantees and reference models, and for evaluations
matched to the objective actually being claimed
[2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms].

## Key claims

- The paper's position: "machine unlearning" should be reserved for dataset-defined
  deletion where the resulting model is approximately indistinguishable from one retrained
  without the forget set [2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms].
- Tasks like refusal training, entity/knowledge removal, and targeted suppression are
  argued to be distinct, policy-dependent objectives mislabeled as "unlearning," and should
  instead be called alignment, suppression, editing, or obfuscation
  [2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms].
- The authors argue mislabeling causes benchmarks/metrics to be reused outside their
  intended scope, rewarding low ROUGE/forget-accuracy scores (surface non-disclosure) even
  when retraining-equivalence isn't tested and derived capabilities remain
  [2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms].
- The paper calls for terminology tied to explicit guarantees and reference models, with
  evaluation protocols matched to the claimed objective
  [2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms].

## Entities mentioned

- None.

## Concepts mentioned

- [[concepts/machine-unlearning]]

## Source

`sources/2026-06-29-position-the-term-machine-unlearning-is-overused-in-llms.md`
