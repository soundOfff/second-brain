---
id: 2026-08-25-llm-anthropic-0-27
title: "llm-anthropic 0.27"
type: article
url: https://simonwillison.net/2026/Aug/24/llm-anthropic/
author: Simon Willison
captured: 2026-08-25
via: simon-willison
tags: [blog, llm]
---

# Simon Willison’s Weblog

Subscribe

Sponsored by: Teleport — AI agents don’t sleep and will try anything to achieve their goal. Teleport explains how to deploy AI safely, starting with an isolated ephemeral trusted runtime.

24th August 2026

Release llm-anthropic 0.27 — LLM access to models by Anthropic, including the Claude series

This release of the Anthropic plugin for LLM mainly provides compatibility with the recently released anthropic v1.0.0 Python library, which switches from httpx to httpx2. OpenAI made the same change in their v3.0.0 release two weeks ago.

Anthropic provide this migration guide for upgrading to 1.0, so I prompted Fable 5 in Claude Code with:

Upgrade to anthropic>=1 - read https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/refs/heads/main/MIGRATION.md and get the tests passing

Here's the resulting PR.

Posted 24th August 2026 at 4:27 pm

## Recent articles

- Conceptual integrity and counting lines of code - 19th August 2026

- Qwen 3.8 27B is excellent, but it defaults to wildly overthinking things - 16th August 2026

- Now we have a timeline of the OpenAI accidental attack against Hugging Face - 7th August 2026

This is a beat by Simon Willison, posted on 24th August 2026.

python 1,277   httpx 8   llm 626   anthropic 331   claude 303

### Monthly briefing

Sponsor me for $10/month and get a curated email digest of the month's most important LLM developments.

Pay me to send you less!

Sponsor & subscribe

- Disclosures

- Colophon

- ©

- 2002

- 2003

- 2004

- 2005

- 2006

- 2007

- 2008

- 2009

- 2010

- 2011

- 2012

- 2013

- 2014

- 2015

- 2016

- 2017

- 2018

- 2019

- 2020

- 2021

- 2022

- 2023

- 2024

- 2025

- 2026
