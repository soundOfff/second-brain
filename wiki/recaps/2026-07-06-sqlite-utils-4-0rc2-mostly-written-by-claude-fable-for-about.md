---
type: recap
title: "Recap — sqlite-utils 4.0rc2, mostly written by Claude Fable (for about $149.25)"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about]
tags: [llm, coding-agents, sqlite-utils, release-notes, simon-willison]
---

# Recap — sqlite-utils 4.0rc2, mostly written by Claude Fable (for about $149.25)

**[[entities/simon-willison]]** describes using **[[entities/claude-fable]]** (an
Anthropic preview/codename model, accessed via Claude Max on Claude Code for web,
including from his iPhone) to do a "final review before shipping" pass on
**[[entities/sqlite-utils]]** 4.0, ahead of the stable release
[2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about]. The review
surfaced 5 "release blocker" bugs, the worst being that `Table.delete_where()` ran its
DELETE without the library's `atomic()` transaction wrapper, leaving the connection
stuck `in_transaction=True` so that the delete itself — plus any subsequent writes —
were silently rolled back on connection close, a data-loss bug
[2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about]. Over 37
prompts / 34 commits / +1,321 -190 lines across 30 files, Willison and Fable worked
through the feedback and made further design improvements, most significantly to
transaction handling, the RC's signature new feature
[2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].

Willison then had **Codex Desktop** running **[[entities/gpt-5.5]]** (xhigh) review the
diff since the last RC as a second, independent pass — a practice he says he used to
consider "somewhat absurd" but now does habitually (having **[[entities/anthropic]]**'s
best model review **[[entities/openai]]**'s work and vice versa) because it reliably
turns up real issues [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].
That pass found two more P1 bugs in `db.query()`'s transaction/commit semantics around
non-row statements and `INSERT ... RETURNING`, which Willison confirmed and fixed in a
fresh Fable session [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].
To estimate the true API cost of the work (run via a subscription, so normally hidden),
he had Claude run **[[entities/agentsview]]** inside the session, giving a total of
**$149.25** across the main session and several cheaper sub-agents
[2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about]. He notes he
upgraded to the $200/month Claude Max plan specifically to get more Fable usage before
"Fablepocalypse" on July 7th, after which even Max subscribers pay full API cost for the
model [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].

The post also includes the full 4.0rc2 release notes: sqlite-utils now commits every
write method automatically inside its own transaction (previously writes could be
silently rolled back on close); `db.query()` now executes/commits immediately rather
than lazily on first iteration; validation errors now raise `ValueError` instead of bare
`AssertionError` (which is skipped under Python's `-O` flag); `upsert()`/`upsert_all()`
now raise `PrimaryKeyRequired` instead of silently inserting bad rows; and the library
now rejects Python 3.12+ `autocommit=True/False` connections outright, since sqlite-utils'
commit/rollback semantics silently broke on them
[2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].

**Notable:** this is a sequel to Willison's earlier post on sqlite-utils 4.0rc1 (referenced
directly in the opening line, "I wrote about the sqlite-utils 4.0rc1 release a couple of
weeks ago"), and there is reportedly also a source on 4.0rc3 in this batch of captures —
these three should be linked as a release-notes series on the [[entities/sqlite-utils]]
page by the central merge pass
[2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].

## Key claims

- The worst pre-release bug found: `Table.delete_where()` ran outside `atomic()`, leaving
  the connection `in_transaction=True` so the delete and all subsequent writes were lost
  on close [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].
- The review/fix cycle for 4.0rc2 spanned 37 prompts, 34 commits, +1,321/-190 lines
  across 30 files [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].
- A second independent review by GPT-5.5 (xhigh, via Codex Desktop) found two more P1
  bugs in `db.query()`'s commit timing around non-row statements and `INSERT ... RETURNING`
  [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].
- Estimated real API cost of the whole session (normally hidden behind the Claude Max
  subscription): $149.25, of which $141.02 was the main session
  [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].
- Willison upgraded to the $200/month Claude Max plan to get more Fable usage before a
  July 7th price change ("Fablepocalypse") after which Max subscribers pay full API cost
  [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].
- sqlite-utils 4.0 now auto-commits every write method inside its own transaction and
  rejects Python 3.12+ connections opened with explicit `autocommit=True/False`
  [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].
- Willison's opinion: release notes are "a great example of writing that I'm OK to
  outsource to agents because they need to be boring, predictable and accurate"
  [2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about].

## Entities mentioned

- [[entities/simon-willison]], [[entities/sqlite-utils]], [[entities/claude-fable]],
  [[entities/anthropic]], [[entities/openai]], [[entities/gpt-5.5]],
  [[entities/agentsview]]

## Concepts mentioned

- [[concepts/cross-model-review]], [[concepts/coding-agents]]

## Source

`sources/2026-07-06-sqlite-utils-4-0rc2-mostly-written-by-claude-fable-for-about.md`
