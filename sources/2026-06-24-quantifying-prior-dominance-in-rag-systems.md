---
id: 2026-06-24-quantifying-prior-dominance-in-rag-systems
title: "Quantifying Prior Dominance in RAG Systems"
type: article
url: https://arxiv.org/abs/2606.23695
captured: 2026-06-24
via: arxiv-cs-cl
tags: [paper, nlp]
---

# Computer Science > Computation and Language

arXiv:2606.23695 (cs)

[Submitted on 29 Apr 2026]

# Title:Quantifying Prior Dominance in RAG Systems

Authors:Barak Or

View a PDF of the paper titled Quantifying Prior Dominance in RAG Systems, by Barak Or

View PDF HTML (experimental)

>  Abstract:Retrieval-Augmented Generation (RAG) grounds Large Language Models in external knowledge, yet current evaluations rely on discrete heuristics that suffer from ''epistemic blindness'' - failing to distinguish genuine contextual information extraction from parametric memory recall. To address this, we introduce the Normalized Context Utilization (NCU) metric, leveraging continuous token log-probabilities across zero-shot, oracle, and adversarial conditions to strictly quantify contextual information gain. Evaluating architectures ranging from 1.5B to 72B parameters alongside a proprietary commercial API reveals that for strict factual extraction (without Chain-of-Thought reasoning), traditional scaling laws exhibit extreme diminishing returns: highly efficient Small Language Models (SLMs) match or outperform high-capacity architectures. Furthermore, we demonstrate that ``Prior Dominance'' correlates with model scale and proprietary alignments. The evaluated commercial API not only overrode explicit external evidence in nearly half of adversarial conflicts, but also frequently suffered from systemic confidence collapse (Negative Transfer) when its parametric priors were contradicted. Our findings highlight the structural epistemic advantage and superior contextual adherence of SLMs in strict extraction workflows.

Comments: 15 pages, Preprint

Subjects:  Computation and Language (cs.CL); Artificial Intelligence (cs.AI)

Cite as: arXiv:2606.23695 [cs.CL]

(or  arXiv:2606.23695v1 [cs.CL] for this version)

https://doi.org/10.48550/arXiv.2606.23695

arXiv-issued DOI via DataCite

## Submission history

From: Barak Or [view email]

[v1] Wed, 29 Apr 2026 15:38:24 UTC (89 KB)

Full-text links:

## Access Paper:

View a PDF of the paper titled Quantifying Prior Dominance in RAG Systems, by Barak Or

- View PDF

- HTML (experimental)

- TeX Source

view license

### Current browse context:

cs.CL

< prev   |   next >

new  |  recent  | 2026-06

Change to browse by:

cs

cs.AI

### References & Citations

- NASA ADS

- Google Scholar

- Semantic Scholar

Loading...

## BibTeX formatted citation

loading...

Data provided by:

### Bookmark

Bibliographic Tools

# Bibliographic and Citation Tools

Bibliographic Explorer Toggle

Bibliographic Explorer *(What is the Explorer?)*

Connected Papers Toggle

Connected Papers *(What is Connected Papers?)*

Litmaps Toggle

Litmaps *(What is Litmaps?)*

scite.ai Toggle

scite Smart Citations *(What are Smart Citations?)*

Code, Data, Media

# Code, Data and Media Associated with this Article

alphaXiv Toggle

alphaXiv *(What is alphaXiv?)*

Links to Code Toggle

CatalyzeX Code Finder for Papers *(What is CatalyzeX?)*

DagsHub Toggle

DagsHub *(What is DagsHub?)*

GotitPub Toggle

Gotit.pub *(What is GotitPub?)*

Huggingface Toggle

Hugging Face *(What is Huggingface?)*

ScienceCast Toggle

ScienceCast *(What is ScienceCast?)*

Demos

# Demos

Replicate Toggle

Replicate *(What is Replicate?)*

Spaces Toggle

Hugging Face Spaces *(What is Spaces?)*

Spaces Toggle

TXYZ.AI *(What is TXYZ.AI?)*

Related Papers

# Recommenders and Search Tools

Link to Influence Flower

Influence Flower *(What are Influence Flowers?)*

Core recommender toggle

CORE Recommender *(What is CORE?)*

- Author

- Venue

- Institution

- Topic

About arXivLabs

# arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs.

Which authors of this paper are endorsers? | Disable MathJax (What is MathJax?)
