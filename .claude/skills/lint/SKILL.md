---
name: lint
description: Health-check the wiki for contradictions, orphans, dangling links, missing citations, and stale pages. Use when the user runs /lint or asks to "lint", "check the wiki", "audit the brain", "find contradictions", or "what's broken/missing". Run at least weekly — contradictions compound. Reports issues and offers to fix the safe ones.
---

# /lint — health check the wiki

Read `CLAUDE.md` first if you have not this session. `/lint` is read-first: diagnose,
report, then fix only safe, unambiguous issues (and only after telling the user).

## Checks

Scan all of `wiki/` and `sources/` and report each finding with the file and line:

1. **Contradictions** — claims on different pages (or within one page) that conflict.
   The most important check. Cite both sides.
2. **Dangling links** — `[[...]]` wikilinks whose target page does not exist. Each is
   either a typo to fix or a page worth creating — say which.
3. **Orphan pages** — wiki pages no other page links to (and that don't link out).
   Surface them so they can be connected or retired.
4. **Missing citations** — non-obvious factual claims with no source ID. List them.
5. **Source-starved stubs** — pages with `status: stub` and few/no `sources:`, or that
   no source actually supports.
6. **Unprocessed sources** — `sources/<id>` with no matching recap (suggest `/sync`).
7. **Frontmatter problems** — missing required fields, `updated:` older than the page's
   last real change, invalid `type`/`status`, duplicate slugs/aliases.
8. **Duplicate pages** — two pages covering the same entity/concept (suggest merge).

## Report

Group findings by severity:
- **Contradictions** (resolve first),
- **Broken structure** (dangling links, duplicates, frontmatter),
- **Gaps** (orphans, missing citations, starved stubs, unprocessed sources).

Give counts and a concrete fix suggestion for each.

## Safe auto-fixes

After reporting, fix only the unambiguous, low-risk items (and note what you changed):
- correct obvious link typos to existing pages,
- repair frontmatter (missing/incorrect required fields, stale `updated:`),
- create clearly-warranted stub pages for high-value dangling links,
- merge exact-duplicate pages into a canonical + redirect stub.

**Do not** auto-resolve contradictions, delete pages, or rewrite substantive content —
flag those for the user. Append a `log.md` entry: checks run, issues found by category,
fixes applied.
