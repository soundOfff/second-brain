---
type: recap
title: "Recap — sqlite-utils 4.0rc3"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-06-sqlite-utils-4-0rc3]
tags: [sqlite-utils, python, sqlite, release-notes, simon-willison]
---

# Recap — sqlite-utils 4.0rc3

A short blog note by Simon Willison (captured 2026-07-06) announces the release of
**sqlite-utils 4.0rc3**, a Python CLI utility and library for manipulating SQLite
databases [2026-07-06-sqlite-utils-4-0rc3]. Willison says he had hoped to ship 4.0
stable that weekend, but the changelog kept growing as he worked through a backlog of
issues and PRs using a combination of **Claude Fable 5** and **GPT-5.5**
[2026-07-06-sqlite-utils-4-0rc3]. The headline new feature is support for introspecting
and creating compound foreign keys, which required a subtle breaking change to
`table.foreign_keys` and therefore needed to land before the 4.0 stable release
[2026-07-06-sqlite-utils-4-0rc3]. The rc also makes sqlite-utils follow SQLite's
convention for case-insensitive column names, a change that touched many parts of the
codebase [2026-07-06-sqlite-utils-4-0rc3].

## Key claims

- sqlite-utils 4.0rc3 adds support for introspecting and creating compound foreign
  keys, which involves a subtle breaking change to `table.foreign_keys`
  [2026-07-06-sqlite-utils-4-0rc3].
- This rc also makes sqlite-utils follow SQLite's own convention for case-insensitive
  column names [2026-07-06-sqlite-utils-4-0rc3].
- Willison used a combination of Claude Fable 5 and GPT-5.5 to work through the
  pre-4.0-stable issue/PR backlog [2026-07-06-sqlite-utils-4-0rc3].
- Willison originally hoped to ship 4.0 stable the same weekend as this rc, but the
  scope grew instead [2026-07-06-sqlite-utils-4-0rc3].

## Entities mentioned

- [[entities/simon-willison]], [[entities/sqlite-utils]], [[entities/anthropic]]
  (Claude Fable 5), [[entities/openai]] (GPT-5.5)

## Concepts mentioned

- [[concepts/sqlite]], [[concepts/foreign-keys]]

## Source

`sources/2026-07-06-sqlite-utils-4-0rc3.md`
