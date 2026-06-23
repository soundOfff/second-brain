---
name: sync
description: Reconcile a batch of new or unprocessed sources against the existing wiki in one pass. Use when the user runs /sync, drops several files into sources/ at once, or asks to "sync", "reconcile", "process the backlog", or "catch up the wiki". Like /capture but for many sources together, deduplicating shared work.
---

# /sync — reconcile a batch of sources

Read `CLAUDE.md` first if you have not this session. `/sync` processes **all
unprocessed sources** together so overlapping entities/concepts are updated once,
coherently, instead of repeatedly.

## 1. Find the backlog

A source is **unprocessed** if `sources/<id>` exists but `wiki/recaps/<id>.md` does
not. List every such source (ignore `sources/README.md` and `.meta.md` sidecars whose
primary file is already recapped). If there is no backlog, say so and stop.

## 2. Plan the ripple

Read all backlog sources first. Build a single plan:
- one recap per source (`wiki/recaps/<id>.md`),
- the union of entities and concepts mentioned across the batch,
- for each entity/concept, the set of sources that touch it (so you write each page
  once, integrating every relevant source, rather than N times).

Note cross-source agreements and contradictions while planning.

## 3. Execute

1. Write all recaps (same structure as `/capture` step 2).
2. For each entity/concept page, create or update it **once**, integrating all batch
   sources at once: merge information, add every relevant source ID to `sources:`, add
   inline citations, wikilink related pages, set `status`, bump `updated:`.
3. Record cross-source contradictions on the affected pages under
   `## Open questions / contradictions`, citing each source.
4. Merge any duplicate pages you discover (canonical page + redirect stub via aliases).

## 4. Update `index.md` and log

Refresh the map of content. Append one `log.md` entry summarizing the batch: how many
sources processed, recaps written, pages created/updated, contradictions found.

## Report back

Summarize: N sources reconciled, recaps written, pages created vs. updated, and a short
list of contradictions or gaps for the user's attention.
