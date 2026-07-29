---
type: recap
title: "Recap — Introducing Claude Opus 5"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-25-introducing-claude-opus-5]
tags: [anthropic, claude, llm-release, agentic-ai]
---

# Recap — Introducing Claude Opus 5

A short link-blog reaction post by [[entities/simon-willison]] to Anthropic's release of [[entities/claude-opus-5]], written before he'd tested the model himself (he was "offline kayaking with sea otters") but based on the release post and early buzz, which he describes as positive [2026-07-25-introducing-claude-opus-5]. Anthropic describes Opus 5 as "a thoughtful and proactive model that comes close to the frontier intelligence of Claude Fable 5 at half the price," and per Willison it was, at time of writing, leading the Artificial Analysis leaderboard — ahead of even Fable 5 [2026-07-25-introducing-claude-opus-5]. It is priced the same as Opus 4.8, and continues to offer a "fast mode" at twice the base model's cost [2026-07-25-introducing-claude-opus-5].

Willison highlights an anecdote from Anthropic's release post illustrating Opus 5's proactivity: on a Frontier-Bench task, the model was shown a drawing of a machine part and asked to write code reconstructing it as a 3D FreeCAD model, but was deliberately given no way to directly view the drawing — Opus 5 responded by writing its own computer-vision pipeline to extract the geometry from raw pixels and then reconstructed the full part [2026-07-25-introducing-claude-opus-5]. On security, Willison notes Opus 5 is better at finding vulnerabilities but, like Opus 4.8 before it, was deliberately not trained on exploiting them; per the quoted release text it comes close to "Mythos 5" at finding vulnerabilities but remains substantially behind Mythos 5 at turning vulnerabilities into working exploits [2026-07-25-introducing-claude-opus-5]. Willison speculates this training choice is intended to keep the US government from restricting the model [2026-07-25-introducing-claude-opus-5].

He also flags two companion resources published alongside the release: Anthropic's own prompting guide for Claude Opus 5, and an article by Thariq Shihipar, "The new rules of [[concepts/context-engineering|context engineering]] for Claude 5 generation models" [2026-07-25-introducing-claude-opus-5]. As with his usual practice, Willison ran his pelican-riding-a-bicycle SVG benchmark against the model — the first attempt was missing the bicycle wheels, the second attempt was better [2026-07-25-introducing-claude-opus-5].

## Key claims

- Anthropic describes Claude Opus 5 as coming close to Claude Fable 5's frontier intelligence at half the price [2026-07-25-introducing-claude-opus-5].
- Opus 5 was, at time of writing, leading the Artificial Analysis leaderboard, ahead of Fable 5 [2026-07-25-introducing-claude-opus-5].
- Opus 5 is priced the same as Opus 4.8 and offers a "fast mode" at 2x base-model cost [2026-07-25-introducing-claude-opus-5].
- On a Frontier-Bench task with no direct image access, Opus 5 wrote its own computer-vision pipeline to extract geometry from a machine-part drawing's raw pixels and reconstructed it as a 3D FreeCAD model [2026-07-25-introducing-claude-opus-5].
- Like Opus 4.8, Opus 5 was intentionally not trained on cyber-exploitation tasks; it approaches "Mythos 5" at finding vulnerabilities but remains substantially behind Mythos 5 at exploiting them [2026-07-25-introducing-claude-opus-5].
- Anthropic published a prompting guide for Opus 5; Thariq Shihipar separately published "The new rules of context engineering for Claude 5 generation models" [2026-07-25-introducing-claude-opus-5].

## Entities mentioned

- [[entities/simon-willison]], [[entities/anthropic]], [[entities/claude-opus-5]]

## Concepts mentioned

- [[concepts/context-engineering]], [[concepts/agentic-proactivity]], [[concepts/cybersecurity-capability-evaluation]]

## Source

`sources/2026-07-25-introducing-claude-opus-5.md`
