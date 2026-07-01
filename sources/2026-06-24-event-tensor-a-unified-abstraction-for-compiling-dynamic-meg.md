---
id: 2026-06-24-event-tensor-a-unified-abstraction-for-compiling-dynamic-meg
title: "Event Tensor: A Unified Abstraction for Compiling Dynamic Megakernel"
type: article
url: https://arxiv.org/abs/2604.13327
captured: 2026-06-24
via: lobsters-ai
tags: [news, ai]
---

# Computer Science > Distributed, Parallel, and Cluster Computing

arXiv:2604.13327 (cs)

[Submitted on 14 Apr 2026 (v1), last revised 21 Apr 2026 (this version, v2)]

# Title:Event Tensor: A Unified Abstraction for Compiling Dynamic Megakernel

Authors:Hongyi Jin, Bohan Hou, Guanjie Wang, Ruihang Lai, Jinqi Chen, Zihao Ye, Yaxing Cai, Yixin Dong, Xinhao Cheng, Zhihao Zhang, Yilong Zhao, Yingyi Huang, Lijie Yang, Jinchen Jiang, Gabriele Oliaro, Jianan Ji, Xupeng Miao, Vinod Grover, Todd C. Mowry, Zhihao Jia, Tianqi Chen

View a PDF of the paper titled Event Tensor: A Unified Abstraction for Compiling Dynamic Megakernel, by Hongyi Jin and 20 other authors

View PDF HTML (experimental)

>  Abstract:Modern GPU workloads, especially large language model (LLM) inference, suffer from kernel launch overheads and coarse synchronization that limit inter-kernel parallelism. Recent megakernel techniques fuse multiple operators into a single persistent kernel to eliminate launch gaps and expose inter-kernel parallelism, but struggle to handle dynamic shapes and data-dependent computation in real workloads. We present Event Tensor, a unified compiler abstraction for dynamic megakernels. Event Tensor encodes dependencies between tiled tasks, and enables first-class support for both shape and data-dependent dynamism. Built atop this abstraction, our Event Tensor Compiler (ETC) applies static and dynamic scheduling transformations to generate high-performance persistent kernels. Evaluations show that ETC achieves state-of-the-art LLM serving latency while significantly reducing system warmup overhead.

Comments: 16 pages. 18 figures. accepted in MLSys 2026. References corrected

Subjects:  Distributed, Parallel, and Cluster Computing (cs.DC); Machine Learning (cs.LG); Programming Languages (cs.PL)

Cite as: arXiv:2604.13327 [cs.DC]

(or  arXiv:2604.13327v2 [cs.DC] for this version)

https://doi.org/10.48550/arXiv.2604.13327

arXiv-issued DOI via DataCite

## Submission history

From: Hongyi Jin [view email]

[v1] Tue, 14 Apr 2026 22:19:51 UTC (1,005 KB)

[v2] Tue, 21 Apr 2026 00:31:44 UTC (1,005 KB)

Full-text links:

## Access Paper:

View a PDF of the paper titled Event Tensor: A Unified Abstraction for Compiling Dynamic Megakernel, by Hongyi Jin and 20 other authors

- View PDF

- HTML (experimental)

- TeX Source

view license

### Current browse context:

cs.DC

< prev   |   next >

new  |  recent  | 2026-04

Change to browse by:

cs

cs.LG

cs.PL

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
