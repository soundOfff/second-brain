---
type: recap
title: "Recap — Attention Is All You Need, Revisited"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-22-attention-is-all-you-need-revisited]
tags: [transformers, attention, architecture, scaling, opinion]
---

# Recap — Attention Is All You Need, Revisited

Very short piece (captured as a brief note rather than a full article; the source URL points to a
placeholder `example.com` domain and the byline "Jane Researcher" is not otherwise corroborated,
so this may be a lightly-sourced or synthetic entry) framed as a retrospective on the
[[concepts/transformer-architecture]] eight years after its introduction
[2026-06-22-attention-is-all-you-need-revisited]. The author's claimed thesis is that the original
scaling intuitions held up, but that the community underestimated how much of the eventual gains
came from data curation rather than from architectural changes
[2026-06-22-attention-is-all-you-need-revisited].

The piece states it walks through three "surprises": (1) [[concepts/attention-mechanism]] sparsity
patterns that emerged without being explicitly trained for, (2) the persistence/stubbornness of
[[concepts/positional-encoding]] choices over the years, and (3) how little FFN (feed-forward
network) width mattered once past some threshold
[2026-06-22-attention-is-all-you-need-revisited]. No further detail on these three points is given
in the captured text.

## Key claims

- The author argues original transformer scaling intuitions held, but that data curation mattered
  more than architecture for later gains [2026-06-22-attention-is-all-you-need-revisited].
- Attention sparsity patterns reportedly emerged without being explicitly trained for
  [2026-06-22-attention-is-all-you-need-revisited].
- Positional encoding choices are described as unusually persistent/"stubborn" over the years
  [2026-06-22-attention-is-all-you-need-revisited].
- FFN width is claimed to matter little past some unspecified threshold
  [2026-06-22-attention-is-all-you-need-revisited].

## Entities mentioned

- [[entities/jane-researcher]]

## Concepts mentioned

- [[concepts/transformer-architecture]], [[concepts/attention-mechanism]],
  [[concepts/positional-encoding]], [[concepts/scaling-laws]], [[concepts/data-curation]]

## Source

`sources/2026-06-22-attention-is-all-you-need-revisited.md`
