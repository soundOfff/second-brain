---
id: 2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo
title: "EXPO-SQL: Execution-based Clause-level Policy Optimization for Text-to-SQL"
type: article
url: https://arxiv.org/abs/2606.23693
captured: 2026-06-24
via: arxiv-cs-cl
tags: [paper, nlp]
---

# Computer Science > Computation and Language

arXiv:2606.23693 (cs)

[Submitted on 29 Apr 2026]

# Title:EXPO-SQL: Execution-based Clause-level Policy Optimization for Text-to-SQL

Authors:Jaehoon Lee, CheolWon Na, Suyoung Bae, Jin-Seop Lee, Jihyung Lee, YunSeok Choi, Jee-Hyong Lee

View a PDF of the paper titled EXPO-SQL: Execution-based Clause-level Policy Optimization for Text-to-SQL, by Jaehoon Lee and 6 other authors

View PDF HTML (experimental)

>  Abstract:Text-to-SQL enables users to query databases using natural language by generating executable SQL queries. Recent methods have increasingly adopted Large Language Models based reinforcement learning (RL) to leverage execution feedback for training. However, existing RL methods assign uniform query-level rewards to all clauses in a SQL query, treating correct and incorrect clauses equally. This coarse-grained reward design leads to insufficient learning signals for correct SQL generation. To address this issue, we propose EXPO-SQL (EXecution-based clause-level Policy Optimization for Text-to-SQL) which provides fine-grained supervision through clause-level rewards. To assign clause-level rewards, our method identifies erroneous clauses by analyzing execution results, including error messages and clause-wise incremental execution. Experiments on widely-used Text-to-SQL benchmarks demonstrate that EXPO-SQL significantly outperforms existing supervised fine-tuning, prompting, and RL-based methods through fine-grained clause-level learning. Our code is available at https://github. com/jhn25/EXPO-SQL.

Comments: 20 pages, 8 figures

Subjects:  Computation and Language (cs.CL); Information Retrieval (cs.IR)

Cite as: arXiv:2606.23693 [cs.CL]

(or  arXiv:2606.23693v1 [cs.CL] for this version)

https://doi.org/10.48550/arXiv.2606.23693

arXiv-issued DOI via DataCite

Journal reference: ACL 2026 Findings

## Submission history

From: Jaehoon Lee [view email]

[v1] Wed, 29 Apr 2026 10:33:16 UTC (763 KB)

Full-text links:

## Access Paper:

View a PDF of the paper titled EXPO-SQL: Execution-based Clause-level Policy Optimization for Text-to-SQL, by Jaehoon Lee and 6 other authors

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

cs.IR

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
