---
name: digest
description: Synthesize recent activity into a periodic digest page. Use when the user runs /digest or asks for a "digest", "weekly summary", "what's new in the brain", or "synthesize recent notes". Identifies themes and patterns across recently added sources and pages, and writes a dated page in wiki/digests/. Good to schedule weekly.
---

# /digest — periodic synthesis

Read `CLAUDE.md` first if you have not this session. `/digest` steps back from
individual sources and finds the patterns across a recent window.

## 1. Choose the window

Default to the last **7 days** (by `captured`/`updated` dates and `log.md` entries).
Accept an explicit window from the user (e.g. "this month", a date range). If little
changed since the last digest in `wiki/digests/`, say so and offer a shorter summary.

## 2. Gather

- New sources captured in the window.
- Wiki pages created or updated in the window.
- Open contradictions and dangling links still outstanding (cross-check with `/lint`'s
  view, but don't re-run the full lint).

## 3. Synthesize — write `wiki/digests/YYYY-MM-DD-digest.md`

Frontmatter: `type: digest`, title (`Digest — <window>`), created/updated today,
`status: stable`, `sources:` (the window's source IDs), tags.

Body:
- **`## Themes`** — the 3–6 ideas/patterns that recurred or strengthened this window,
  each citing the pages and sources behind it (`[[...]]`, `[src-id]`).
- **`## What changed`** — notable new/updated entities and concepts.
- **`## Connections`** — links the agent drew between previously separate pages.
- **`## Open questions & contradictions`** — what remains unresolved.
- **`## Suggested next sources`** — gaps where a new source would most help.

This is synthesis, not a changelog: prefer "X and Y both point at Z" over "added page
X, added page Y".

## 4. Wire it up & log

Link the new digest from `index.md` (Digests section / Recently updated). Append a
`log.md` entry.

## Scheduling

To run this automatically (e.g. weekly), use Claude Code's scheduler — ask the user, or
run the `/schedule` skill, to create a routine that invokes `/digest` on a cron (e.g.
every Monday 09:00). Do not create a schedule without the user's go-ahead.

## Report back

Give the user the digest's headline themes and the path to the new page.
