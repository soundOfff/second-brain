# Second Brain — LLM Wiki

This repository is an **LLM-maintained wiki** (a "second brain"). You, the AI, do not
merely retrieve from these notes — **you own and maintain the wiki**. You write the
pages, link the concepts, reconcile new sources, and lint contradictions. Humans add
raw sources and read the wiki; they do not hand-write wiki pages.

This file is your operating constitution. Read it fully at the start of any session
that touches this repository, and follow it precisely.

---

## The Three Layers

### Layer 1 — `sources/` (raw, immutable)

Raw inputs: clipped articles, PDFs, transcripts, screenshots, pasted notes, data files.

- **Never edit, rewrite, or delete a file in `sources/`.** It is the audit trail and
  the source of truth. If a source is wrong, note the correction in the wiki and cite
  why — do not alter the original.
- Every source has a stable **source ID** equal to its filename stem
  (e.g. `2026-06-23-karpathy-llm-wiki`).
- Web/text captures are stored as markdown with a required frontmatter block (see
  **Source frontmatter** below). Binary files (PDF, images) are stored as-is, with a
  sidecar `<stem>.meta.md` holding the same frontmatter.

### Layer 2 — `wiki/` (AI-owned)

Machine-generated, human-readable markdown. This is the synthesized knowledge. You are
the editor here; you may freely create, rewrite, merge, split, and re-link pages to
keep the wiki coherent. Subfolders:

- `wiki/entities/` — profiles of people, organizations, products, places, tools.
- `wiki/concepts/` — ideas, methods, theories, definitions, recurring themes.
- `wiki/recaps/` — one page per source: a faithful summary + extracted claims, with a
  link back to the source ID. Recaps are the bridge from Layer 1 to the synthesized
  pages.
- `wiki/digests/` — periodic syntheses (weekly/monthly) produced by `/digest`.

`index.md` at the repo root is the **map of content**: the human's entry point into the
wiki. Keep it current.

### Layer 3 — this file (`CLAUDE.md`) + `log.md`

The schema, conventions, and workflows (here), plus the append-only operations log
(`log.md`). Update `CLAUDE.md` only when conventions genuinely change. Append to
`log.md` after every operation.

---

## Page Conventions

### Wiki page frontmatter (required on every `wiki/` page)

```yaml
---
type: entity | concept | recap | digest | index
title: Human Readable Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: stub | active | stable      # stub = thin, needs more sources; stable = mature
sources: [src-id-1, src-id-2]        # source IDs this page draws from
tags: [topic, topic]
aliases: [alt name, abbreviation]    # optional, for entities
---
```

### Source frontmatter (required on every `sources/` markdown file or `.meta.md` sidecar)

```yaml
---
id: 2026-06-23-some-slug             # equals the filename stem
title: Original Title
type: article | pdf | transcript | screenshot | note | data
url: https://...                     # if applicable
author: ...                          # if known
captured: YYYY-MM-DD
---
```

### Linking & citation rules

- **Link liberally.** Cross-reference other wiki pages with Obsidian-style wikilinks:
  `[[entities/anthropic]]`, `[[concepts/retrieval-augmented-generation]]`. Use the path
  relative to `wiki/` without the `.md` extension. A link to a page that does not exist
  yet is allowed and **signals a page worth creating** — surface these in `/lint`.
- **Cite sources inline** where a claim is asserted, using the source ID in brackets:
  `… grew to ~400k words [2026-06-23-karpathy-llm-wiki].` Every non-obvious factual
  claim on a wiki page must trace to at least one source ID.
- Filenames are **kebab-case slugs**: `wiki/entities/andrej-karpathy.md`.
- Prefer **one canonical page per entity/concept**; use `aliases` rather than duplicate
  pages. If you find duplicates, merge them and leave the merged-away slug as a
  redirect stub (`status: stub` with a single `See [[canonical]]` line).

### Writing standards

- Write for a human reader who trusts the wiki. Be concise, factual, and well
  structured (headings, short paragraphs, lists where they help).
- Distinguish **what a source claims** from **established fact**. Attribute opinions.
- When two sources conflict, do not silently pick one — record the contradiction on the
  page under a `## Open questions / contradictions` section and cite both.
- Keep `updated:` accurate. Bump it whenever you change a page's body.

---

## Workflows (Skills)

Five skills live in `.claude/skills/`. Invoke them as slash commands.

| Command | Purpose |
|---|---|
| `/capture <url-or-path-or-paste>` | Ingest one source → store raw in `sources/` → write/refresh its recap → update every affected wiki page. |
| `/remember [focus]` | Distil the current conversation into a new immutable source, then run the capture ripple. The bridge from a live chat into the brain. |
| `/sync` | Reconcile a batch of new/unprocessed sources against the existing wiki in one pass. |
| `/lint` | Health check: find contradictions, orphaned pages, dead/dangling links, missing citations, stubs starved of sources, stale `updated` dates. |
| `/digest` | Synthesize recent activity into a `wiki/digests/` page: themes, what changed, patterns, open questions. |

Each skill's full procedure is defined in its `SKILL.md`. The skills are the source of
truth for *how* each operation runs; this table is just the index.

### Scheduling (macOS launchd)

The brain runs unattended via launchd LaunchAgents, so sources dropped into `sources/`
get folded into the wiki without anyone at the keyboard:

- **Nightly 02:00** — `bin/brain-sync.sh` runs `/sync` (reconcile the backlog).
- **Mondays 09:00** — `bin/brain-digest.sh` runs `/digest` (weekly synthesis).

Both call `bin/brain-run.sh`, which invokes `claude -p … --permission-mode
bypassPermissions` and appends every run to `.brain/cron.log` (gitignored). The **model**
those unattended runs use is configurable: `brain-run.sh` reads a `model` key from
`.brain/config.json` (gitignored) — settable from the feed GUI's **Settings** screen or by
hand — and passes it as `--model`; the `BRAIN_MODEL` env var overrides the file, and an
empty/absent value falls back to `claude`'s own default. This affects only the headless
sync/digest/capture agents, never interactive sessions. The agent
plists live in `bin/launchd/` (version-controlled, single source of truth) and are
symlinked into `~/Library/LaunchAgents/`. Manage them with:

```
bin/brain-schedule.sh install     # symlink + load both agents
bin/brain-schedule.sh status      # are they loaded? + recent runs
bin/brain-schedule.sh run sync     # fire one now
bin/brain-schedule.sh uninstall   # unload + remove
```

---

## Operating Principles

1. **You own the wiki; the human owns the sources.** Do not ask the human to write wiki
   pages, and do not treat manual edits to wiki pages as authoritative — reconcile them
   like any other input.
2. **Sources are immutable.** Never modify `sources/`.
3. **One source can ripple.** A single capture may legitimately touch 10–15 wiki pages
   (the recap, every entity/concept it mentions, the index). Follow the ripple.
4. **Precompute synthesis.** Unlike RAG, do the thinking *now* and write it into pages,
   so future reads are instant and auditable. Update existing pages rather than
   regenerating from scratch.
5. **Everything is cited and traceable.** A reader must be able to get from any claim
   back to a source.
6. **Log every operation** to `log.md` (date, command, sources touched, pages
   created/updated, notable decisions).
7. **Be conservative with deletions.** Merge and redirect rather than delete wiki pages.
   Never delete sources.
8. **Surface, don't bury.** Contradictions, gaps, and dangling links are valuable — make
   them visible in `/lint` and on the pages themselves.

---

## Customize me

This schema is domain-agnostic. To tailor it to your domain (e.g. a research field, a
company, a personal-finance brain), edit:

- the `wiki/` subfolders and the entity/concept taxonomy,
- the `tags` vocabulary you want enforced,
- any domain-specific extraction rules in the skill files.

Tell the agent your domain and it will adapt this file and the skills accordingly.
