---
id: 2026-06-29-supersede-diagnosing-and-training-the-memory-update-gap-in-l
title: "Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents"
type: article
url: https://arxiv.org/abs/2606.27472
captured: 2026-06-29
via: arxiv-cs-cl
tags: [paper, nlp]
---

# Computer Science > Computation and Language

arXiv:2606.27472 (cs)

[Submitted on 25 Jun 2026]

# Title:Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents

Authors:Vedant Patel

View a PDF of the paper titled Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents, by Vedant Patel

View PDF HTML (experimental)

>  Abstract:Large language model (LLM) agents operate over long, multi-session interactions in which facts change: a user moves, a price updates, a plan is revised. Acting correctly requires using the current value of a fact and discarding values that have been superseded. We isolate this ability on real conversational data and show that it is a distinct, unsolved failure. On the knowledge-update subset of LongMemEval, replacing an agent's full context with a bounded, self-maintained memory drops accuracy from 92% to 77% even on a frontier model (gpt-5.4), a gap that is statistically significant (paired McNemar p<0.005) and persists across model scale while full-context accuracy saturates near 92%. The bottleneck is therefore memory maintenance, not comprehension, and is not closed by a stronger model. We then ask whether this is merely an undersized memory, and find it is not: as the conversation grows 24x, accuracy falls further (from 68% to 28%), and granting the agent proportionally more memory yields no detectable recovery (28% to 28%, n=25). The failure scales with the length of the conversation, not the compression ratio. We release Supersede, an open reinforcement-learning environment (on the verifiers / prime-rl stack) that turns this measurement into a training signal: agents are rewarded for answering from the current value and penalized for stale ones. Finally, we close the loop and show the gap is trainable: GRPO fine-tuning a small open model (Qwen2.5-3B) on this environment nearly doubles its held-out supersession accuracy on real, unseen conversations (9.0% to 16.7%, a single run), along a monotonic checkpoint curve indicating the learned policy, not the harness, carries the gain. To our knowledge this is the first trainable environment whose reward targets temporal fact-currency, and the first evidence the supersession gap can be trained down, not only measured.

Comments: 11 pages, 4 figures, 3 tables. Code, environment, model, and dataset: this https URL

Subjects:  Computation and Language (cs.CL); Artificial Intelligence (cs.AI); Machine Learning (cs.LG)

Cite as: arXiv:2606.27472 [cs.CL]

(or  arXiv:2606.27472v1 [cs.CL] for this version)

https://doi.org/10.48550/arXiv.2606.27472

arXiv-issued DOI via DataCite (pending registration)

## Submission history

From: Vedant Patel [view email]

[v1] Thu, 25 Jun 2026 18:50:32 UTC (73 KB)

Full-text links:

## Access Paper:

View a PDF of the paper titled Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents, by Vedant Patel

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
