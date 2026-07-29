---
type: recap
title: "Recap — Stanford CME295 Transformers & LLMs | Lecture 8 – LLM Evaluation"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-03-stanford-cme295-transformers-llms]
tags: [llm, evaluation, benchmarks, llm-as-a-judge, agents, stanford, lecture]
---

# Recap — Stanford CME295 Transformers & LLMs | Lecture 8 – LLM Evaluation

Transcript of Lecture 8 of Stanford's CME295 ("Transformers & LLMs," Autumn 2025), co-taught
by instructors referred to in the transcript as Afshine and Shervine ([[entities/afshine-amidi]]
and [[entities/shervine-amidi]], via [[entities/stanford-online]]). The lecture covers how to
evaluate LLM output quality, moving from human ratings, to rule-based reference metrics (METEOR,
BLEU, ROUGE), to [[concepts/llm-as-a-judge]] as the now-dominant technique, then covers agentic
workflow failure taxonomies and a survey of standard LLM benchmarks
[2026-07-03-stanford-cme295-transformers-llms].

Afshine opens by arguing pure human rating doesn't scale and that even human judgment can be
subjective/noisy, motivating inter-rater agreement metrics like Cohen's kappa, Fleiss's kappa,
and Krippendorff's alpha, which normalize the raw agreement rate against the rate expected by
pure chance [2026-07-03-stanford-cme295-transformers-llms]. He walks through reference-based
metrics (METEOR, BLEU, ROUGE), arguing they penalize valid stylistic paraphrase and correlate
only weakly with human judgment [2026-07-03-stanford-cme295-transformers-llms]. This motivates
[[concepts/llm-as-a-judge]]: an LLM given a prompt, a response, and grading criteria, asked to
output a rationale before a score (mirroring chain-of-thought reasoning), on a preferably binary
pass/fail scale, at low temperature (~0.1–0.2) for reproducibility, with output format guaranteed
via [[concepts/structured-output]]/constrained decoding
[2026-07-03-stanford-cme295-transformers-llms]. He catalogs three named judge failure modes —
[[concepts/position-bias]] (favoring whichever response is shown first, mitigated by swapping
order and majority-voting), [[concepts/verbosity-bias]] (favoring longer responses regardless of
correctness), and [[concepts/self-enhancement-bias]] (a model favoring its own generations when
used to judge its own output) — and recommends judging with a separate, larger/more-capable model
than the generator [2026-07-03-stanford-cme295-transformers-llms]. He closes his half with a
factuality-scoring pipeline: decompose text into atomic facts via an LLM call, fact-check each
(often via RAG/web search) as binary correct/incorrect, then aggregate with importance weights
into a single score, illustrated on a "teddy bear" example text with two factual errors that
scores 0.6 [2026-07-03-stanford-cme295-transformers-llms].

Shervine's half covers agentic evaluation. Building on the [[concepts/react-framework]]
(observe/plan/act) from the prior lecture, he enumerates seven concrete agent failure modes
across three pipeline stages — tool prediction (not calling an available tool and "punting"; a
tool-router recall miss; the LLM ignoring an available tool; tool hallucination, i.e. calling a
function that doesn't exist; the wrong tool chosen among valid options; wrong arguments passed),
tool execution (a buggy tool returns the wrong output; a tool silently returns no response, which
is especially bad for action-performing tools — he recommends returning a meaningful/structured
output, even an empty JSON, rather than nothing or a raw error), and response synthesis (the model
fails to ground on tool output, the tool output is too verbose/noisy to parse, or the output isn't
structured meaningfully) [2026-07-03-stanford-cme295-transformers-llms]. He then surveys standard
benchmark categories with one example each: knowledge ([[concepts/mmlu]], ~60 multiple-choice
tasks across domains), reasoning ([[concepts/aime]] for math, [[concepts/piqa]] for
physical-world common sense), coding ([[concepts/swe-bench]], built from real GitHub PRs with
before/after tests), safety ([[concepts/harmbench]], the only benchmark of the set graded by a
trained classifier rather than exact match), and agentic tool-use ([[concepts/tau-bench]],
LLM-simulated multi-turn user/agent tasks in airline and retail domains, scored by
database-state reward, introducing the "pass-hat-k" metric — the probability that *all* k
attempts succeed, versus pass@k's "at least one") [2026-07-03-stanford-cme295-transformers-llms].
He notes a recent [[entities/gemini]] model report used multilingual/agentic variants of these
benchmarks (Global PIQA, tau-squared-bench) [2026-07-03-stanford-cme295-transformers-llms]. He
closes with three caveats: benchmarks characterize a model's *profile* rather than yielding one
"best" ranking (illustrated via a cost/performance [[concepts/pareto-frontier]]), data
contamination is mitigated via hashing/blocklists or using genuinely-new test items, and invokes
[[concepts/goodharts-law]] ("when a measure becomes a target, it ceases to be a good measure") as
the reason benchmark scores should never be over-optimized in isolation
[2026-07-03-stanford-cme295-transformers-llms]. As a personal, explicitly non-authoritative aside,
Shervine says he finds Sonnet models strong for coding and Gemini Flash good for fast/cheap output
[2026-07-03-stanford-cme295-transformers-llms].

## Key claims

- LLM-as-a-judge takes a prompt, response, and grading criteria, and returns a rationale plus a
  score; outputting rationale before score empirically improves judge quality (echoing
  chain-of-thought) [2026-07-03-stanford-cme295-transformers-llms].
- Binary pass/fail scales are recommended over granular scales for both LLM judges and human
  raters, since they reduce rating noise [2026-07-03-stanford-cme295-transformers-llms].
- Best practice is to judge with a different, and ideally larger/more capable, model than the one
  that generated the response, to reduce self-enhancement bias
  [2026-07-03-stanford-cme295-transformers-llms].
- Reference-based MT/summarization metrics (METEOR, BLEU, ROUGE) penalize valid paraphrases and
  correlate only weakly with human ratings [2026-07-03-stanford-cme295-transformers-llms].
- Inter-rater agreement should be measured relative to chance agreement (Cohen's kappa / Fleiss's
  kappa / Krippendorff's alpha), not as a raw percentage, since raw agreement can be high by pure
  chance [2026-07-03-stanford-cme295-transformers-llms].
- A factuality score can be computed by decomposing text into atomic facts, fact-checking each
  (e.g. via RAG/web search) as correct/incorrect, and aggregating with importance weights
  [2026-07-03-stanford-cme295-transformers-llms].
- Seven distinct agent failure modes were catalogued spanning tool prediction, tool execution, and
  response synthesis, including tool hallucination (calling a nonexistent function) and silent/
  no-op tool responses [2026-07-03-stanford-cme295-transformers-llms].
- An empty JSON is a more meaningful "not found" tool response than a bare "none," because it's
  structurally interpretable [2026-07-03-stanford-cme295-transformers-llms].
- MMLU spans ~60 multiple-choice tasks across domains and mainly measures pretraining knowledge
  retention [2026-07-03-stanford-cme295-transformers-llms].
- AIME (math olympiad problems, three-digit numeric answers) and PIQA (~20,000 binary-choice
  physical-commonsense questions) are the two reasoning benchmarks discussed
  [2026-07-03-stanford-cme295-transformers-llms].
- SWE-bench is built from real Python GitHub pull requests that fix an issue and add tests,
  scoring models on whether their generated patch makes the tests pass
  [2026-07-03-stanford-cme295-transformers-llms].
- HarmBench has four categories (standard, copyright, contextual, multimodal) and is the only
  benchmark discussed that is graded by a trained classifier rather than exact-match
  [2026-07-03-stanford-cme295-transformers-llms].
- tau-bench (name reads as "tool, agent, users") simulates multi-turn user/agent interactions in
  airline and retail domains via a separate LLM playing the user, scored by database-state/action
  reward; it introduces "pass-hat-k," the probability all k attempts succeed
  [2026-07-03-stanford-cme295-transformers-llms].
- A recent Gemini model report reportedly used multilingual/agentic benchmark variants: Global
  PIQA and tau-squared-bench [2026-07-03-stanford-cme295-transformers-llms].
- Shervine's personal (explicitly non-authoritative) take: Sonnet models are strong for coding;
  Gemini Flash is good for fast/cheap output [2026-07-03-stanford-cme295-transformers-llms].

## Entities mentioned

- [[entities/stanford-online]], [[entities/afshine-amidi]], [[entities/shervine-amidi]],
  [[entities/openai]], [[entities/anthropic]], [[entities/gemini]]

## Concepts mentioned

- [[concepts/llm-as-a-judge]], [[concepts/retrieval-augmented-generation]],
  [[concepts/tool-calling]], [[concepts/react-framework]], [[concepts/position-bias]],
  [[concepts/verbosity-bias]], [[concepts/self-enhancement-bias]], [[concepts/structured-output]],
  [[concepts/mmlu]], [[concepts/aime]], [[concepts/piqa]], [[concepts/swe-bench]],
  [[concepts/harmbench]], [[concepts/tau-bench]], [[concepts/goodharts-law]],
  [[concepts/pareto-frontier]], [[concepts/cohens-kappa]], [[concepts/bleu]],
  [[concepts/meteor]], [[concepts/rouge]], [[concepts/pass-at-k]]

## Source

`sources/2026-07-03-stanford-cme295-transformers-llms.md`
