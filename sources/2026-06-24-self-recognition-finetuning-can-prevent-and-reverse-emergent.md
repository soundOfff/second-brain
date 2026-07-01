---
id: 2026-06-24-self-recognition-finetuning-can-prevent-and-reverse-emergent
title: "Self-Recognition Finetuning can Prevent and Reverse Emergent Misalignment"
type: article
url: https://arxiv.org/abs/2606.23700
captured: 2026-06-24
via: arxiv-cs-cl
tags: [paper, nlp]
---

# Computer Science > Computation and Language

arXiv:2606.23700 (cs)

[Submitted on 4 Jun 2026]

# Title:Self-Recognition Finetuning can Prevent and Reverse Emergent Misalignment

Authors:Arush Tagade, Shaoheng Zhou, Jiaxin Wen, Shi Feng

View a PDF of the paper titled Self-Recognition Finetuning can Prevent and Reverse Emergent Misalignment, by Arush Tagade and 3 other authors

View PDF

>  Abstract:Emergent misalignment (EM) has been linked to the activation of misaligned persona vectors and evil character traits, suggesting that EM operates through disruption of the model's aligned character rather than direct learning of harmful content. Motivated by this connection, we study self-generated text recognition (SGTR) finetuning as a character-targeted intervention that is distinct from existing in-training defenses. We conduct two-stage finetuning experiments across three models (GPT-4.1, Qwen2.5-32B-Instruct, Seed-OSS-36B-Instruct) and multiple EM datasets to compare SGTR finetuning against benign finetuning baselines (correct domain-specific data, general knowledge, and word counting) to find it an effective defense in both reversal and prevention settings. We find that all interventions produce comparable EM reversal, but only when restoring capabilities that EM had degraded. For prevention, only SGTR finetuning consistently reduces misalignment without exacerbating any individual metric, suggesting that character fortification specifically drives prevention. We provide further evidence for EM's relation to the LLM's default character by showing that EM finetuning induces diversity into the LLM's identity self-reports, artificially corrupting self-recognition exacerbates misalignment caused by EM finetuning, and that removing the model's identity-bearing system prompt substantially reduces the effect of EM finetuning. Together, these findings reframe EM not as the adoption of a coherent misaligned persona but as the destabilization of aligned character.

Comments: 18 pages, 11 figures

Subjects:  Computation and Language (cs.CL); Artificial Intelligence (cs.AI); Machine Learning (cs.LG)

Cite as: arXiv:2606.23700 [cs.CL]

(or  arXiv:2606.23700v1 [cs.CL] for this version)

https://doi.org/10.48550/arXiv.2606.23700

arXiv-issued DOI via DataCite

## Submission history

From: Arush Tagade [view email]

[v1] Thu, 4 Jun 2026 00:04:58 UTC (2,132 KB)

Full-text links:

## Access Paper:

View a PDF of the paper titled Self-Recognition Finetuning can Prevent and Reverse Emergent Misalignment, by Arush Tagade and 3 other authors

- View PDF

- TeX Source

view license

### Current browse context:

cs.CL

< prev   |   next >

new  |  recent  | 2026-06

Change to browse by:

cs

cs.AI

cs.LG

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
