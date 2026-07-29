---
type: recap
title: "Recap — ModTGCN: Modularity-aware Graph Neural Networks for Text Classification"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas]
tags: [paper, graph-neural-networks, nlp, text-classification]
---

# Recap — ModTGCN: Modularity-aware Graph Neural Networks for Text Classification

An arXiv paper (Rajarshi Misra, Aditya Sharma, Vinti Agarwal, Hari Om Aggrawal;
PAKDD 2026) proposing ModTGCN, a **[[concepts/graph-neural-networks|graph neural
network]]** for **[[concepts/text-classification]]** that jointly optimizes
cross-entropy loss with a modularity-based auxiliary objective
[2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas]. The authors'
claim is that standard graph-based text classifiers (e.g. TextGCN-style models) rely on
local neighborhood aggregation and overlook global community structure, even though
semantic document graphs exhibit strong class-consistent clustering — and that ignoring
this blurs class boundaries and causes over-smoothing
[2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas].

The modularity term is computed on a document-document similarity graph derived from
transformer embeddings (pretrained or fine-tuned), promoting class-coherent document
communities while preserving discriminative representations
[2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas]. To improve
scalability, the authors decouple the original heterogeneous TextGCN graph into separate
document-word and word-word components, which they report achieves 2x–10x faster
training [2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas]. The
paper also studies graph construction strategies, label-aware edge reweighting, and
supervision choices for modularity optimization, reporting consistent gains across five
benchmarks with larger improvements on complex, low-homophily datasets such as Ohsumed and
20NG [2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas].

## Key claims

- ModTGCN jointly optimizes cross-entropy and a modularity-based auxiliary objective to
  promote class-coherent document communities in graph-based text classification
  [2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas].
- The modularity term is computed on a document-document similarity graph built from
  transformer embeddings [2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas].
- Decoupling the heterogeneous TextGCN graph into document-word and word-word components
  achieves a claimed 2x–10x training speedup
  [2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas].
- Reported consistent gains across five benchmarks, with the largest improvements on
  complex, low-homophily datasets such as Ohsumed and 20NG
  [2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas].

## Entities mentioned

- None.

## Concepts mentioned

- [[concepts/graph-neural-networks]], [[concepts/text-classification]]

## Source

`sources/2026-06-24-modtgcn-modularity-aware-graph-neural-networks-for-text-clas.md`
