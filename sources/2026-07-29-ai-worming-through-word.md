---
id: 2026-07-29-ai-worming-through-word
title: "AI Worming through Word"
type: article
url: https://simonwillison.net/2026/Jul/29/ai-worming-through-word/#atom-everything
author: Simon Willison
captured: 2026-07-29
via: simon-willison
tags: [blog, llm]
---

# Simon Willison’s Weblog

Subscribe

Sponsored by: Cursor — Delegate engineering tasks to Cursor Cloud Agents—even while your laptop is closed. Try Cursor & get 50% off your first month

29th July 2026 - Link Blog

AI Worming through Word (via) Neat new prompt injection variant by Håkon Måløy, who found a way to upgrade prompt injection attacks against Microsoft Word to full self-replicating worms:

An attacker places hidden instructions in a document that is later used as source material in Copilot for Word. Copilot may interpret those instructions as part of the user’s request, causing it to manipulate the document being drafted or edited. Copilot may then also copy the hidden instructions into the resulting document, turning that document into a new carrier. If the carrier is subsequently used in another Copilot-assisted workflow, the instructions can trigger again and propagate into further documents, even without the attacker’s original document being present.

We've seen plenty of hidden white-on-white text before - the kids are using it in their job applications now - but this is the first one I've seen that deliberately copies instructions to self-replicate itself.

It was responsibly disclosed to Microsoft who then had 144 days to work on a fix, but so far (unsurprisingly) there's no mitigation that covers the full class of attack.

Posted 29th July 2026 at 6:43 pm

## Recent articles

- OpenAI’s accidental cyberattack against Hugging Face is science fiction that happened - 22nd July 2026

- A Fireside Chat with Cat and Thariq from the Claude Code team - 21st July 2026

- Kimi K3, and what we can still learn from the pelican benchmark - 16th July 2026

This is a link post by Simon Willison, posted on 29th July 2026.

microsoft 133   security 620   ai 2,150   prompt-injection 158   generative-ai 1,902   llms 1,869

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
