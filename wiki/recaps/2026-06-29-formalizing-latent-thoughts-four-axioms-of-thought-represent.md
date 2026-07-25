---
type: recap
title: "Recap — Formalizing Latent Thoughts: Four Axioms of Thought Representation in LLMs"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent]
tags: [paper, interpretability, nlp, evaluation]
---

# Recap — Formalizing Latent Thoughts: Four Axioms of Thought Representation in LLMs

arXiv paper (arXiv:2606.27378, submitted 7 May 2026) by **Fahd Seddik** and **Fatemeh
Fard** introducing an axiomatic evaluation framework for latent "thought"
representations inside LLMs, designed to be independent of downstream benchmark scores
[2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent]. The captured
source is the arXiv abstract/metadata page only, not the full paper text
[2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent].

The authors argue existing evaluations conflate representation quality with model
capacity, making it impossible to attribute failures specifically to a representation
rather than to the model processing it [2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent].
They formalize four functional axioms — **Causality, Minimality, Separability, and
Stability** — each with a quantitative measure computed directly on the representation,
independent of downstream task accuracy
[2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent]. Auditing
open-weight LLMs across 23 reasoning tasks (e.g. spatial reasoning, factual QA), they
report that no evaluated model satisfies all four axioms simultaneously; that
representations reliably distinguish task type but fail to distinguish between two
different questions within the same task; and that representations encode little
information beyond what is already present in the input embedding
[2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent]. This pattern
held consistently across dense, reasoning-distilled, and RL-trained model families,
which the authors take as evidence that the gap is structural rather than a function of
model size or training procedure [2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent].

## Key claims

- The paper defines four axioms for latent thought representations — Causality, Minimality, Separability, Stability — each independently measurable without reference to downstream benchmark accuracy [2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent].
- Across an audit of open-weight LLMs on 23 reasoning tasks, no model satisfied all four axioms simultaneously [2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent].
- Representations reliably distinguish task type, but not between two different questions within the same task [2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent].
- The evaluated latent representations encode little information beyond what is already present in the input embedding [2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent].
- The failure pattern is consistent across dense, reasoning-distilled, and RL-trained model families, suggesting a structural rather than size- or procedure-specific gap (authors' interpretation) [2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent].

## Entities mentioned

- [[entities/fahd-seddik]], [[entities/fatemeh-fard]]

## Concepts mentioned

- [[concepts/mechanistic-interpretability]], [[concepts/latent-thought-representation]], [[concepts/benchmarking]], [[concepts/reasoning-models]]

## Source

`sources/2026-06-29-formalizing-latent-thoughts-four-axioms-of-thought-represent.md`
