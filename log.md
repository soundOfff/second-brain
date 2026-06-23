# Operations Log

Append-only. Every skill run records one entry. Newest at the bottom.

Format:

```
## YYYY-MM-DD HH:MM — /command [arg]
- sources: <ids added/processed>
- recaps: <recaps created/updated>
- wiki: <entity/concept pages created/updated>
- index: <updated? what>
- notes: <decisions, contradictions found, follow-ups>
```

---

## 2026-06-23 — system initialized
- Created three-layer structure: `sources/`, `wiki/{entities,concepts,recaps,digests}/`.
- Authored `CLAUDE.md` schema, `index.md` map of content, this log.
- Installed skills: `/capture`, `/sync`, `/lint`, `/digest`.
- notes: Empty brain, ready for first `/capture`.

## 2026-06-23 — /capture https://www.askglitch.com/blog/build-a-second-brain
- sources: 2026-06-23-karpathy-llm-wiki (article)
- recaps: recaps/2026-06-23-karpathy-llm-wiki
- wiki: created concepts/{llm-wiki, second-brain, retrieval-augmented-generation};
  created entities/{andrej-karpathy, claude-code, obsidian}
- index: added top entities, top concepts, recently-updated entry
- notes: Self-referential seed — the brain's first source is the article describing the
  brain. RAG, Karpathy, Claude Code, Obsidian left as stubs pending more sources. No
  contradictions. 1 source → 7 wiki pages (recap + 6).

## 2026-06-23 — infra: /remember skill + launchd scheduler
- skills: created `/remember` (.claude/skills/remember/SKILL.md) — distils the current
  conversation into a `type: note` source, then runs the `/capture` ripple. Save+ripple
  behavior chosen by the user.
- scheduler: added launchd LaunchAgents (bin/launchd/com.secondbrain.{sync,digest}.plist)
  — sync nightly 02:00, digest Mondays 09:00 — plus bin/brain-schedule.sh
  (install/uninstall/status/run) which symlinks the repo plists into ~/Library/LaunchAgents.
- gitignore: added `.brain/` (headless run logs).
- docs: updated CLAUDE.md (skills table → 5 skills + Scheduling section), README.md
  (operations table + scheduling section), index.md (how-to).
- notes: plists + script lint clean (plutil, zsh -n). The actual `launchctl` load was
  NOT performed — the auto-approval classifier blocked loading agents that run
  `claude -p --permission-mode bypassPermissions`. User must run
  `bin/brain-schedule.sh install` themselves to activate the schedule.

## 2026-06-23 — proposal: external-but-matched companion tools
- docs: created `docs/external-tools.md` — design spec for three companion tools that
  live outside the internal skills but bind to the CLAUDE.md contract: (1) capture
  bridge (`bin/brain-clip.sh` + share-sheet/extension to land valid-frontmatter sources
  from anywhere → nightly /sync folds them in), (2) wiki server (local read-only
  renderer that resolves [[wikilinks]] + backlinks, no LLM at read time), (3) contract
  validator (`bin/brain-validate.sh` pre-commit/CI guard for frontmatter, slugs,
  citations, dangling links).
- framing: tools map to the three sides of the brain — IN / OUT / INTEGRITY — and form a
  pipeline (#1 feeds → #3 guards → #2 serves). Recommended build order: #3, #1, #2.
- no code written yet; user requested spec-only via /whats-next.

## 2026-06-23 — infra: contract validator (external tool #3 of docs/external-tools.md)
- bin: created `bin/brain-validate.sh` — deterministic guard for the CLAUDE.md schema.
  Checks (FAIL): required source/wiki frontmatter keys, source `id` == filename stem,
  type/status enums, kebab-case slugs, dates parse, `updated >= created`, frontmatter
  `sources:` entries and inline `[src-id]` citations resolve to real files in sources/.
  Dangling `[[wikilinks]]` are WARN only (CLAUDE.md allows them). Strips inline `code`
  and `[[links]]` before citation scan so documented examples aren't flagged. Flags:
  `--quiet`, `--install-hook`. Exit 1 on any FAIL.
- bin: created `bin/hooks/pre-commit` (version-controlled); `--install-hook` symlinks it
  into .git/hooks (repo = source of truth, mirroring brain-schedule). Hook installed.
- verification: passes clean on the live repo (9 files, 0 fail, 0 warn). Tested against a
  throwaway broken fixture in scratchpad (NOT in sources/) — all 9 FAIL conditions and
  the dangling-link WARN fired correctly.
- docs: marked tool #3 as BUILT in docs/external-tools.md. Tools #1 (capture bridge) and
  #2 (wiki server) remain proposed.

## 2026-06-23 — infra: wiki server (external tool #2 of docs/external-tools.md)
- bin: created `bin/brain-serve.py` (stdlib-only, Python 3) + `bin/brain-serve.sh`
  launcher. Read-only local HTTP server over wiki/**.md + index.md: minimal markdown
  renderer (headings, lists, blockquotes, bold/italic, inline+fenced code), resolves
  [[wikilinks]] → /wiki/<path> navigation (dangling → red .missing), [src-id] citations
  → /source/<id> view of the immutable raw source. Per-page "Linked from" backlinks and
  "Sources" panels; source pages show a "Cited by" panel; sidebar groups pages by folder
  with stub badges. No writes, no LLM; re-reads files per request so edits show live.
- verification: smoke-tested all routes (index/wiki/source/404) via curl — wikilinks,
  citations, backlinks, and the Cited-by reverse index all resolve. Visually confirmed
  the rendered page in-browser (screenshot).
- docs: marked tool #2 BUILT in docs/external-tools.md. Only tool #1 (capture bridge)
  remains proposed.
- not committed yet — awaiting user.
