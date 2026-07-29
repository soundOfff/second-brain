---
type: entity
title: Datasette
created: 2026-06-26
updated: 2026-06-26
status: stub
sources: [2026-06-24-datasette-1-0a35, 2026-06-24-opfs-pyodide-test-harness]
tags: [tool, data, open-source, sqlite]
aliases: [Datasette, Datasette Lite]
---

# Datasette

[[entities/simon-willison]]'s open-source **multi-tool for exploring and publishing
data**, built around SQLite [2026-06-24-datasette-1-0a35].

## In these sources

- **1.0a35 release** — a "big" alpha adding: a **Create table** UI (backed by a
  `/<database>/-/create` JSON API), an **Alter table** action and
  `/<database>/<table>/-/alter` JSON API, and **template-context documentation** treated
  as a stable API for custom templates until Datasette 2.0
  [2026-06-24-datasette-1-0a35]. Shipping JSON APIs beside the human UI is an instance of
  [[concepts/agent-native-infrastructure]].
- **Datasette Lite** — a build of Datasette that runs **entirely in the browser** via
  [[entities/pyodide]] and WebAssembly. Willison is exploring whether it could edit
  persistent SQLite files on the user's computer via OPFS (Origin Private File System)
  [2026-06-24-opfs-pyodide-test-harness].

> Stub — captured only via two June 2026 Willison posts; expand with a dedicated source.
