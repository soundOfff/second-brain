---
type: recap
title: "Recap — OPFS + Pyodide test harness"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-opfs-pyodide-test-harness]
tags: [blog, browser, tools, claude-code, pyodide]
---

# Recap — OPFS + Pyodide test harness

A brief blog post by Simon Willison noting he built a small playground UI to test whether
**[[entities/datasette|Datasette Lite]]** — the Python Datasette application that runs
entirely in-browser via **[[concepts/pyodide]]**/WebAssembly — could edit persistent
SQLite files stored on the user's computer using the **[[concepts/opfs|Origin Private File
System]]** (OPFS) [2026-06-24-opfs-pyodide-test-harness]. He states he had
**[[entities/claude-code]]** "for web" build the test harness so he could try it out across
different browsers [2026-06-24-opfs-pyodide-test-harness]. The post is very short — a
single-paragraph tool note rather than an in-depth writeup.

## Key claims

- Simon Willison built (via Claude Code for web) a test harness to check whether OPFS can
  let Datasette Lite edit persistent SQLite files on the user's machine
  [2026-06-24-opfs-pyodide-test-harness].
- The goal was to test this across different browsers
  [2026-06-24-opfs-pyodide-test-harness].

## Entities mentioned

- [[entities/simon-willison]], [[entities/claude-code]], [[entities/datasette]]

## Concepts mentioned

- [[concepts/opfs]], [[concepts/pyodide]]

## Source

`sources/2026-06-24-opfs-pyodide-test-harness.md`
