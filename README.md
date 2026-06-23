# Second Brain — an LLM-maintained wiki

An AI-owned knowledge base, built on the **LLM Wiki** method (Karpathy's approach,
[writeup](https://www.askglitch.com/blog/build-a-second-brain)). The idea: don't use an
LLM to *query* your notes — let it **own and maintain** the wiki. It writes the pages,
links the concepts, reconciles new sources, and lints contradictions. You add raw
sources and read the result.

## Why not just RAG?

RAG re-synthesizes an answer from raw documents on every query. This precomputes the
synthesis **once** into human-readable, cross-linked, auditable pages — then keeps them
updated as new sources arrive. The knowledge is a navigable artifact, not a transient
answer.

## The three layers

```
second-brain/
├── CLAUDE.md          # Layer 3: the schema — rules, conventions, workflows (the agent's constitution)
├── log.md             # Layer 3: append-only operations log
├── index.md           # the human entry point — map of content
├── sources/           # Layer 1: raw, IMMUTABLE inputs (never edited)
└── wiki/              # Layer 2: AI-owned synthesis (you read, you don't hand-write)
    ├── entities/      #   people, orgs, products, tools, places
    ├── concepts/      #   ideas, methods, theories, themes
    ├── recaps/        #   one faithful summary per source
    └── digests/       #   periodic syntheses
```

## The operations (Claude Code skills in `.claude/skills/`)

| Command | What it does |
|---|---|
| `/capture <url \| file \| pasted text>` | Ingest one source → store raw → recap → update every affected wiki page. |
| `/remember [focus]` | Distil the current conversation with Claude into a new source, then fold it into the wiki. |
| `/sync` | Reconcile a batch of new sources in one coherent pass. |
| `/lint` | Find contradictions, orphans, dangling links, missing citations, stale pages. Run weekly. |
| `/digest` | Synthesize recent activity into a dated digest: themes, patterns, open questions. |

## Running on a schedule (macOS)

The brain maintains itself unattended via launchd — drop sources in, read the wiki
later. `bin/brain-schedule.sh install` loads two LaunchAgents that run `claude`
headlessly in this vault:

- **nightly 02:00** → `/sync` reconciles any new sources,
- **Mondays 09:00** → `/digest` writes the weekly synthesis.

Plists live in `bin/launchd/` (symlinked into `~/Library/LaunchAgents/`); every run is
logged to `.brain/cron.log`. Check state with `bin/brain-schedule.sh status`, fire one
now with `bin/brain-schedule.sh run sync`, or remove them with `… uninstall`.

## Getting started

1. Open this folder in Claude Code.
2. Run `/capture <a url or file>` to add your first source. Watch the wiki populate.
3. Run `/lint` to see structural health, `/digest` for a synthesis.
4. Read the wiki via `index.md`.

## Use it well (gotchas from the article)

- **Don't bulk-migrate an old vault.** Start fresh; let the brain grow source by source.
- **Don't hand-edit wiki pages.** Let the agent own `wiki/` — that's what keeps it
  coherent and trustworthy. Add knowledge as *sources* instead.
- **Sources are immutable.** Corrections go in the wiki (cited), never by editing
  `sources/`.
- **Curate inputs.** Bad sources poison the brain. Capture deliberately.
- **Lint weekly, minimum.** Contradictions compound.
- **Budget tokens** (~5–15k per `/capture`).

## Tailoring

`CLAUDE.md` is domain-agnostic out of the box. Tell the agent your domain (a research
field, a company, personal finance, a course) and it will adapt the taxonomy, tags, and
extraction rules in `CLAUDE.md` and the skills.
