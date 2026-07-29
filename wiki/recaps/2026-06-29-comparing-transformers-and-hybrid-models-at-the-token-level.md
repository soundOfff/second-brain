---
type: recap
title: "Recap — Comparing Transformers and Hybrid Models at the Token Level"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level]
tags: [ai, llm, transformer, hybrid-model, state-tracking, research-paper]
---

# Recap — Comparing Transformers and Hybrid Models at the Token Level

> **Data-quality note:** the stored source file's body is a corrupted capture — the
> capture pipeline embedded the raw PDF bytes (from `arxiv.org/pdf/2606.20936`) into
> the markdown file, and a lossy text re-encoding along the way replaced many
> non-UTF-8 bytes with replacement characters, breaking the PDF's internal
> compression streams beyond recovery. The frontmatter (id, title, url, captured
> date) is intact and readable. To write a faithful recap despite this, the same
> arXiv URL was re-fetched live and its text extracted for this summary; all claims
> below trace to that paper's actual content, not to garbled bytes
> [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].

This is a research paper — arXiv:2606.20936v1 ("Comparing Transformers and Hybrid
Models at the Token Level"), by Yanhong Li and William Merrill of the
[[entities/allen-institute-for-ai]] (AI2), posted 18 June 2026
[2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level]. The paper
asks a fine-grained question: hybrid language models (mixing
[[concepts/attention-mechanism]] with recurrent/state-space layers) are known to beat
pure [[concepts/transformer-architecture]]s on average loss and downstream benchmarks,
but it was unclear *which* token predictions actually drive that average gain, and
whether those gains match the theoretical expressivity advantages recurrence is
supposed to provide [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
The authors compare two matched, same-recipe 7B models released by AI2 —
[[entities/olmo-3]] (pure transformer) and [[entities/olmo-hybrid]] (hybrid
attention/recurrent) — computing a paired per-token loss gap Δᵢ = ℓ_transformer −
ℓ_hybrid at every position over the same prefixes, so a positive Δ means the hybrid
assigned higher probability to the true next token
[2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].

The central finding is that the hybrid's advantage is far from uniform. It is
largest on open-class, content-bearing tokens (nouns, verbs, adjectives, adverbs) and
smaller — sometimes near zero or reversed — on closed-class function words
(auxiliaries, wh-words, "to", pronouns), on **closing** delimiters (brackets, tags)
versus **opening** ones, and on tokens that complete long repeated n-grams (i.e.
verbatim copying from the visible prefix)
[2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level]. Controlled
synthetic probes reproduce the same split directly: a pronoun-memory probe and an
entity-tracking probe (which require reading out a maintained state) favor the
hybrid, while a structural-closure probe (predicting a closing bracket/tag whose
opener is already visible) favors the transformer at every tested distance (32–1024
tokens) [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level]. The
authors interpret this via expressivity theory: attention gives transformers direct
visible-prefix recall and structural matching, while recurrent layers give ordered
state construction/update that plain transformers (bounded by TC0-style circuit
classes) provably cannot always express under standard complexity assumptions
[2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].

The paper proposes a "discourse state" account — a structured, recurrently updated
representation of entities, attributes, bindings and document/program state that gets
consulted whenever a token's filler isn't determined by copying or by a local
grammatical slot — and argues the hybrid's edge concentrates exactly on such
state-conditioned predictions [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
It also derives a formal bound (Proposition 1) showing that for any token belonging
to a small closed vocabulary class, no amount of extra prefix information can reduce
loss by more than log of that class's size — explaining why gains on closed-class
tags are inherently capped [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
As a practical payoff, the authors show that computing *filtered* token losses (e.g.
restricting to non-copy, open-class targets, or isolating copy-only targets) during
1B-scale pretraining runs exposes architecture gaps roughly 2x larger than aggregate
validation loss, and reveals that a Transformer and a Pure RNN (GDN, no attention)
that look "matched" on aggregate loss actually differ sharply and in opposite
directions on state-tracking versus copying sub-tasks
[2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].

## Key claims

- The paper compares two matched, same-recipe-family 7B models — Olmo 3 (pure
  transformer) and Olmo Hybrid (attention + recurrent hybrid) — from AI2, evaluated on
  identical prefixes packed into length-8192 sequences across prose (PG-19, CC-News,
  Wikipedia, ArXiv, essays, textbooks) and structured text (Python, HTML, LaTeX)
  [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- Hybrid advantage is largest for open-class content words: raw loss gap of 0.0384
  nats for content words vs. 0.0238 nats for function words (~61% larger), and this
  content/function contrast survives regression controls for difficulty, frequency,
  position, subword status, and local reuse
  [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- Across all seven evaluated domains (prose, Python, HTML, LaTeX), opening brackets
  are consistently more hybrid-favored than their matching closing brackets
  [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- The hybrid's advantage shrinks rapidly and approaches zero as repeated n-gram
  length grows from 1 to 16 tokens; regression-adjusted repetition effects are
  negative (i.e. shift the gap toward the transformer) even after controls
  [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- In controlled synthetic probes at distances of 32–1024 tokens: pronoun-memory and
  entity-tracking probes favor the hybrid (the transformer's entity-tracking accuracy
  drops below chance at intermediate distances), while the structural-closure probe
  favors the transformer at every tested distance
  [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- Theoretical grounding cited: under standard fixed-depth, log-precision assumptions,
  transformer next-token predictors sit in low-depth threshold-circuit classes (TC0)
  and provably cannot express general NC1-complete ordered state-composition problems
  unless TC0 = NC1, whereas modern linear RNNs with sufficiently expressive transition
  matrices (e.g. DeltaNet/GDN variants with negative eigenvalues) can represent such
  state-tracking computations (attributed to Merrill & Sabharwal 2023, Merrill et al.
  2024, Grazzi et al. 2025) [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- Proposition 1 (proved in the paper): for a target restricted to vocabulary class
  V_τ, the KL divergence between the true distribution and any feature-restricted
  predictor is bounded above by log|V_τ| — so small closed-class tags inherently
  bound how much a richer architecture can help
  [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- The paper argues existing closed-world state-tracking benchmarks (e.g. the A5
  permutation-composition "word problem" used in prior recurrent-architecture papers)
  are becoming saturated — structured linear-RNN variants can already solve A5 nearly
  perfectly (citing Terzic et al., 2026) — and proposes an open-world "discourse state
  tracking" benchmark direction that allows dynamic entity introduction and relational
  state, as a harder target for future architecture work
  [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- In a proof-of-concept using three 1B-parameter training runs (Transformer, Hybrid
  [interleaved GDN/attention, 3:1 ratio], and Pure RNN [GDN, no attention]) from a
  companion paper (Merrill et al., 2026), filtering token loss to "top-10 hybrid-favored
  POS families, no-copy" tokens roughly doubles the Transformer–Hybrid separation
  versus aggregate loss (~0.12 nats vs. ~0.06 nats), and shows Hybrid < Pure RNN <
  Transformer on that filter, while a "copy-5-only" filter shows the Pure RNN is
  ~0.10–0.20 nats worse than both attention-based models on copying — a split invisible
  in the aggregate loss curve where Transformer and Pure RNN look matched
  [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- The models compared (Olmo 3 7B and Olmo Hybrid 7B) and the 1B-scale development
  checkpoints are released under the Apache 2.0 license
  [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].

## Entities mentioned

- [[entities/yanhong-li]] — co-author (Allen Institute for AI) [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[entities/william-merrill]] — co-author (Allen Institute for AI); also an author on the cited Olmo Hybrid and prior state-tracking-expressivity papers [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[entities/allen-institute-for-ai]] — research institute (AI2) that produced this paper and released the Olmo 3 / Olmo Hybrid models [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[entities/olmo-3]] — the pure-transformer 7B model in the matched comparison, from the Olmo 3 release (Olmo et al., 2026) [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[entities/olmo-hybrid]] — the hybrid attention/recurrent 7B model compared against Olmo 3, from Merrill et al. (2026) [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].

## Concepts mentioned

- [[concepts/transformer-architecture]] — the attention-only baseline architecture; theoretically limited to low-depth threshold-circuit expressivity (TC0) [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[concepts/hybrid-language-model]] — architecture mixing attention and recurrent/state-space layers; the paper's main subject [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[concepts/attention-mechanism]] — gives transformers visible-prefix recall/copy and structural (bracket-matching) capability [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[concepts/state-tracking]] — the ordered-state-composition capability recurrent layers provide that plain transformers provably lack under standard complexity assumptions [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[concepts/state-space-model]] — the family of recurrent sequence layers (linear RNNs, DeltaNet/GDN variants) used in the hybrid and Pure RNN models [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[concepts/discourse-state-tracking]] — the paper's proposed open-world extension of state tracking (dynamic entity introduction, relational state) as a future benchmark direction, contrasted with the closed-world A5 permutation task [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[concepts/token-level-loss-analysis]] — the paper's core method: pairing per-token NLL between two matched models on identical prefixes to localize where an aggregate loss gap comes from [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[concepts/filtered-evaluation]] — proposed technique of computing loss on selected token subsets (non-copy open-class vs. copy-only) during pretraining to get a higher-signal, more capability-resolved architecture comparison than aggregate validation loss [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].
- [[concepts/circuit-complexity-theory]] — TC0/NC1 complexity-class results used to formally justify why plain transformers cannot express general state-tracking problems [2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level].

## Source

`sources/2026-06-29-comparing-transformers-and-hybrid-models-at-the-token-level.md`
