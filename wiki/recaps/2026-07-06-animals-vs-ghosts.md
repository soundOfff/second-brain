---
type: recap
title: "Recap — Animals vs Ghosts"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-06-animals-vs-ghosts]
tags: [llm, ai-philosophy, andrej-karpathy, bitter-lesson, karpathy-blog]
---

# Recap — Animals vs Ghosts

Blog post by [[entities/andrej-karpathy]] (dated 01 Oct 2025, captured 2026-07-06)
reacting to a Dwarkesh Patel podcast episode with **Richard Sutton**, author of "The
Bitter Lesson" [2026-07-06-animals-vs-ghosts]. This post is the origin/full statement
of Karpathy's **[[concepts/animals-vs-ghosts]]** framing already referenced secondhand
elsewhere in the wiki (e.g. via the Sequoia Ascent 2026 summary and "The space of
minds") [2026-07-06-animals-vs-ghosts].

Karpathy summarizes Sutton's position: Sutton calls himself a "classicist" who wants a
Turing-style "child machine" that learns purely through environmental interaction and
reinforcement learning, with no giant pretraining stage and no supervised finetuning
(which he argues is absent from the animal kingdom) [2026-07-06-animals-vs-ghosts].
Sutton argues LLMs are not actually "[[concepts/bitter-lesson|bitter-lesson]]-pilled"
because they depend on finite, human-generated pretraining data, and he is more
interested in general animal intelligence (e.g. "if we understood a squirrel, we'd be
almost done") than in what differentiates humans [2026-07-06-animals-vs-ghosts].

Karpathy's own take (opinion, clearly attributed to him) partially agrees: he says
frontier LLMs are indeed heavily "human"-shaped at every stage (pretraining data,
curated finetuning data, human-tuned RL environments), and that no one has a clean,
"turn the crank" bitter-lesson algorithm that learns purely from experience
[2026-07-06-animals-vs-ghosts]. But he pushes back on using animals as a proof that such
an algorithm is practical: animal brains are not blank slates, since evolution encodes a
powerful initialization in DNA (his example: a baby zebra can run within minutes of
birth), so animal "learning" is largely finetuning/maturation on top of a pre-evolved
prior — he calls **pretraining "our crappy evolution"**, i.e. a practical substitute for
the DNA-encoded initialization animals get for free [2026-07-06-animals-vs-ghosts].

From this, Karpathy proposes his central metaphor: today's frontier LLM research is not
building animals, it is "summoning ghosts" — statistical distillations of humanity's
documents, muddled and engineered by humanity, occupying a different point in the space
of possible intelligences than animal minds [2026-07-06-animals-vs-ghosts]. He floats
the analogy "ghosts:animals :: planes:birds" and states real uncertainty (his words:
"double digit percent uncertainty") about whether ghosts will converge toward
animal-like intelligence through further finetuning, or diverge permanently while
remaining useful [2026-07-06-animals-vs-ghosts]. In an appendix, he also notes that
Dwarkesh's point about LLM in-context learning as a form of test-time adaptation went
under-addressed by Sutton, and mentions CLAUDE.md-style memory as an example of
text-substrate test-time learning [2026-07-06-animals-vs-ghosts].

## Key claims

- Karpathy's central metaphor: LLMs are not "animals" (evolution-initialized, RL-in-the-world learners) but "ghosts" — statistical distillations of human-generated text, engineered and muddled by humanity [2026-07-06-animals-vs-ghosts].
- Karpathy (opinion): "Pretraining is our crappy evolution" — a practical, imperfect substitute for the DNA-encoded initialization animal brains get from evolution before any learning happens [2026-07-06-animals-vs-ghosts].
- Sutton (per Karpathy's summary): argues LLMs are not truly "bitter lesson"-pilled because they depend on finite, human-generated pretraining data, unlike a pure "child machine" that learns from experience alone [2026-07-06-animals-vs-ghosts].
- Sutton: animals do not do supervised learning/direct action "teleoperation" the way LLM pretraining and SFT do [2026-07-06-animals-vs-ghosts].
- Karpathy (opinion): AlphaZero-vs-AlphaGo and animal "tabula rasa" learning are both weaker proof-of-concept examples for a pure bitter-lesson algorithm than commonly claimed, because Go is a simple closed environment and animal brains have a powerful evolved prior at birth [2026-07-06-animals-vs-ghosts].
- Karpathy floats the analogy "ghosts:animals :: planes:birds" for how LLMs may relate to biological intelligence going forward [2026-07-06-animals-vs-ghosts].
- Karpathy: pervasive current frontier-lab practice is pretraining followed by RL finetuning toward "more correct"-looking behavior [2026-07-06-animals-vs-ghosts].

## Entities mentioned

- [[entities/andrej-karpathy]], [[entities/richard-sutton]], [[entities/dwarkesh-patel]], [[entities/alan-turing]], [[entities/alphazero]], [[entities/alphago]]

## Concepts mentioned

- [[concepts/animals-vs-ghosts]], [[concepts/bitter-lesson]], [[concepts/reinforcement-learning]], [[concepts/pretraining]], [[concepts/world-model]]

## Source

`sources/2026-07-06-animals-vs-ghosts.md`
