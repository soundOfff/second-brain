---
id: 2026-08-25-your-executable-is-a-sqlite-database
title: "Your executable is a SQLite database"
type: article
url: https://simonwillison.net/2026/Aug/24/your-executable-is-a-sqlite-database/
author: Simon Willison
captured: 2026-08-25
via: simon-willison
tags: [blog, llm]
---

# Simon Willison’s Weblog

Subscribe

Sponsored by: Teleport — AI agents don’t sleep and will try anything to achieve their goal. Teleport explains how to deploy AI safely, starting with an isolated ephemeral trusted runtime.

24th August 2026 - Link Blog

Your executable is a SQLite database (via) Farid Zakaria describes a neat Linux pattern for creating a SQLite database file that can be directly used as an executable binary.

The trick sets the SQLite file format's 4-byte application ID (68 bytes into the file) to SELF, standing for Structured Executable & Linkable Format. The various components of the ELF executable format are then arranged into a number of different SQLite tables, using this schema.

Their self-exec interpreter (C code here) can then extract and execute the necessary pieces.

You can additionally use a Linux mechanism called binfmt_misc to teach the kernel to execute that any time it encounters an executable matching that binary pattern. Farid uses NixOS here, but without NixOS I think registration looks something like this:

printf '%s\n' ':self:M:68:SELF::/usr/local/bin/self-exec:' \ > /proc/sys/fs/binfmt_misc/register

Posted 24th August 2026 at 11:38 am

## Recent articles

- Conceptual integrity and counting lines of code - 19th August 2026

- Qwen 3.8 27B is excellent, but it defaults to wildly overthinking things - 16th August 2026

- Now we have a timeline of the OpenAI accidental attack against Hugging Face - 7th August 2026

This is a link post by Simon Willison, posted on 24th August 2026.

c 54   linux 51   sqlite 485

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
