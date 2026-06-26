---
type: recap
title: "Recap — OPFS + Pyodide test harness"
created: 2026-06-26
updated: 2026-06-26
status: stable
sources: [2026-06-24-opfs-pyodide-test-harness]
tags: [datasette, pyodide, browsers, tools]
---

# Recap — OPFS + Pyodide test harness

A short tool note by [[entities/simon-willison]] [2026-06-24-opfs-pyodide-test-harness].

## Key claims

- Willison is exploring whether **Datasette Lite** — the [[entities/datasette]]
  application running entirely in the browser via [[entities/pyodide]] and WebAssembly —
  could **edit persistent SQLite files on the user's computer**
  [2026-06-24-opfs-pyodide-test-harness].
- **OPFS (Origin Private File System)** is the browser API for that persistence
  [2026-06-24-opfs-pyodide-test-harness].
- He had **[[entities/claude-code]] for web** build a playground UI to test OPFS
  behaviour across different browsers — an example of [[concepts/vibe-coding]] a
  throwaway tool to probe an unknown [2026-06-24-opfs-pyodide-test-harness].

## Entities mentioned

- [[entities/simon-willison]] (author), [[entities/datasette]], [[entities/pyodide]],
  [[entities/claude-code]]

## Concepts mentioned

- [[concepts/vibe-coding]]

## Source

`sources/2026-06-24-opfs-pyodide-test-harness.md` — weblog tool note, 23 Jun 2026
(captured via the `simon-willison` feed).
