---
type: recap
title: "Recap — What's New in Claude Sonnet 5"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-01-what-s-new-in-claude-sonnet-5]
tags: [anthropic, claude, llm-release, pricing]
---

# Recap — What's New in Claude Sonnet 5

A link-blog post by [[entities/simon-willison]] reacting to Anthropic's "what's new" developer docs for the release of [[entities/claude-sonnet-5]] on 30 June 2026, which Willison says tend to have more actionable detail than the official announcement post [2026-07-01-what-s-new-in-claude-sonnet-5]. Per Anthropic, Sonnet 5's performance is close to Claude Opus 4.8 but at lower prices [2026-07-01-what-s-new-in-claude-sonnet-5]. Willison quotes the system card's explanation of why the model could ship without being blocked by the US government: Sonnet 5 is significantly less capable at cyber tasks than a model called "Mythos 5," putting its safeguards in the same tier as Opus 4.7 and Opus 4.8 [2026-07-01-what-s-new-in-claude-sonnet-5].

Willison lists concrete API changes: `temperature`, `top_p`, and `top_k` sampling parameters are no longer supported; the model has a 1 million token context window and 128,000 max output tokens; it retains the same tool/platform feature set as Claude Sonnet 4.6; and adaptive thinking is on by default unless explicitly disabled [2026-07-01-what-s-new-in-claude-sonnet-5]. Pricing nominally matches Sonnet 4.6 ($3/million input, $15/million output — Willison's text has a likely typo listing $15 as "per million input" — with an introductory discount to $2/$10 through 31 August 2026), but Willison flags that Sonnet 5 uses a new tokenizer that produces roughly 30% more tokens for the same English input, which he characterizes as effectively a 30% price increase [2026-07-01-what-s-new-in-claude-sonnet-5].

Willison ran his own Claude Token Counter tool against several documents to quantify the new tokenizer's overhead relative to Sonnet 4.6/Opus 4.7: about 1.42x more tokens for English text (Universal Declaration of Human Rights), 1.33x for Spanish, 1.28x for Python code (sqlite_utils/db.py), and roughly 1.01x (near parity) for Simplified Mandarin [2026-07-01-what-s-new-in-claude-sonnet-5]. He also notes he ran his standard "pelican riding a bicycle" SVG benchmark against Sonnet 5, calling the result unremarkable, and observes the model itself judged its own drawing to look like a goose [2026-07-01-what-s-new-in-claude-sonnet-5].

## Key claims

- Anthropic states Claude Sonnet 5's performance is close to Opus 4.8 but at lower prices [2026-07-01-what-s-new-in-claude-sonnet-5].
- Sonnet 5's system card states it is significantly less capable at cyber tasks than "Mythos 5," keeping its safeguard tier similar to Opus 4.7/Opus 4.8 [2026-07-01-what-s-new-in-claude-sonnet-5].
- Sampling params temperature/top_p/top_k are no longer supported in Sonnet 5's API [2026-07-01-what-s-new-in-claude-sonnet-5].
- Sonnet 5 has a 1M token context window and 128,000 max output tokens [2026-07-01-what-s-new-in-claude-sonnet-5].
- Adaptive thinking is on by default for Sonnet 5 unless explicitly disabled via `"thinking": {type: "disabled"}` [2026-07-01-what-s-new-in-claude-sonnet-5].
- Sonnet 5 list pricing matches Sonnet 4.6 ($3/$15 per million tokens, introductory $2/$10 through 31 Aug 2026), but a new tokenizer produces ~30% more tokens for English text, which Willison calls an effective 30% price increase [2026-07-01-what-s-new-in-claude-sonnet-5].
- Willison's tokenizer benchmark: ~1.42x more tokens for English, ~1.33x for Spanish, ~1.28x for Python code, ~1.01x for Simplified Mandarin, versus the prior tokenizer [2026-07-01-what-s-new-in-claude-sonnet-5].

## Entities mentioned

- [[entities/simon-willison]], [[entities/anthropic]], [[entities/claude-sonnet-5]]

## Concepts mentioned

- [[concepts/llm-tokenizer]], [[concepts/context-window]], [[concepts/llm-pricing]]

## Source

`sources/2026-07-01-what-s-new-in-claude-sonnet-5.md`
