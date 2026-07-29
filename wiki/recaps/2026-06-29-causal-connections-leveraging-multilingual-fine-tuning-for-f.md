---
type: recap
title: "Recap — Causal Connections: Leveraging Multilingual Fine-Tuning for Financial QA@FinCausal 2026"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-29-causal-connections-leveraging-multilingual-fine-tuning-for-f]
tags: [paper, nlp, finetuning, finance, multilingual]
---

# Recap — Causal Connections: Leveraging Multilingual Fine-Tuning for Financial QA@FinCausal 2026

This is an arXiv abstract page (arXiv:2606.27446, submitted 25 Jun 2026) describing
team HSA_CORAL's submission (Akash Kumar Gautam, Serhii Hamotskyi, Christian Hänig) to
the **FinCausal 2026** shared task, which extracts cause-effect relations from
financial narratives via extractive question answering in English and Spanish
[2026-06-29-causal-connections-leveraging-multilingual-fine-tuning-for-f]. The paper
compares three modeling families: encoder-only token tagging with multilingual BERT,
encoder-decoder generation with multilingual BART, and decoder-only LLMs (Llama 3.1 and
GPT variants) using prompt refinement, few-shot demonstrations, and supervised
finetuning [2026-06-29-causal-connections-leveraging-multilingual-fine-tuning-for-f].

## Key claims

- Prompting and few-shot examples yielded competitive performance across settings, but
  supervised finetuning provided the largest gains [2026-06-29-causal-connections-leveraging-multilingual-fine-tuning-for-f].
- The team's best system — GPT-4.1 Mini finetuned on combined English and Spanish
  training data — achieved a tied-highest score on the English subtask (4.8140) and
  ranked third on the Spanish subtask (4.7753), under the shared task's LLM-as-a-judge
  metric [2026-06-29-causal-connections-leveraging-multilingual-fine-tuning-for-f].
- The paper concludes task-specific adaptation and multilingual finetuning provide
  meaningful cross-lingual transfer benefit for financial causality QA
  [2026-06-29-causal-connections-leveraging-multilingual-fine-tuning-for-f].
- Published as part of the Proceedings of the 7th Financial Narrative Processing
  Workshop (FNP 2026) at LREC 2026 [2026-06-29-causal-connections-leveraging-multilingual-fine-tuning-for-f].

## Entities mentioned

- [[entities/openai]] (GPT-4.1 Mini), [[entities/meta]] (Llama 3.1)

## Concepts mentioned

- [[concepts/finetuning]], [[concepts/llm-as-a-judge]], [[concepts/question-answering]],
  [[concepts/multilingual-nlp]]

## Source

`sources/2026-06-29-causal-connections-leveraging-multilingual-fine-tuning-for-f.md`
