# External-but-Matched Tools — Design Spec

Status: **all three built** · Created: 2026-06-23 · Last built: 2026-06-23 (#1 capture bridge)

Three companion tools that live *outside* the brain's internal skills (`/capture`,
`/sync`, `/lint`, `/digest`, `/remember`) but bind to the **same contract** defined in
`CLAUDE.md`. None of them reimplement the LLM's judgment — they feed it, serve its
output, or guard its schema deterministically.

## The shared contract ("matched" means this)

Any external tool is "matched" if it speaks these, verbatim from `CLAUDE.md`:

- **Source ID = filename stem**, kebab-case, date-prefixed: `2026-06-23-some-slug`.
- **Source frontmatter** on every `sources/` markdown file (or `.meta.md` sidecar for
  binaries): `id, title, type, url?, author?, captured`.
- **Wiki frontmatter** on every `wiki/` page: `type, title, created, updated, status,
  sources[], tags[], aliases?`.
- **Wikilinks**: `[[entities/anthropic]]` — path relative to `wiki/`, no `.md`.
- **Inline citation**: every non-obvious claim ends with `[src-id]`.
- **Sources are immutable**; the wiki is AI-owned; `/sync` ripples new sources in.

The three tools map onto the three sides of the brain:

| Tool | Side | Binds to | Without me / you-in-repo? |
|---|---|---|---|
| 1. Capture bridge | Material **IN** | Source frontmatter + sync flow | Yes — lands sources from anywhere |
| 2. Wiki server | Synthesis **OUT** | Wiki frontmatter + wikilinks | Yes — read side, no LLM at read time |
| 3. Contract validator | Schema **INTEGRITY** | Whole `CLAUDE.md` schema | Yes — guards headless runs |

They form a pipeline: **#1 feeds → #3 guards what's fed and what I write → #2 serves the
result.**

---

## 1. Capture bridge — get material IN from the wild  ✅ BUILT 2026-06-23

> Shipped as `bin/brain-clip.sh`. Deterministic, no-LLM front door (curl + python3
> stdlib only) that deposits ONE raw, immutable source into `sources/` with valid
> frontmatter — then stops. The nightly `/sync` folds it in. Three modes, auto-detected
> from the argument:
> - **URL** → `curl` fetch + a stdlib `HTMLParser` readability pass → `type: article`
>   markdown (title/author pulled from `og:`/`<title>`/`meta[author]`); nav/script/style
>   stripped.
> - **File** → text files (`.md/.txt/...`) inlined as a markdown source; binaries
>   (PDF/image/data) copied in as-is with a `<stem>.meta.md` sidecar; `type` inferred
>   from extension.
> - **Text / stdin** (`-`) → `type: note`.
>
> Slugifies the title to a date-prefixed kebab `id`, dedupes (`-2`, `-3`) on collision,
> and after writing runs the contract validator (tool #3) on what it produced — so #3
> guards what #1 feeds. Flags: `--type --title --author --url --dry-run`. Distinct from
> `bin/brain-capture.sh`, which invokes the full LLM `/capture` ripple; the clipper is
> the cheap, key-free, share-sheet-able deposit. Verified across all three modes +
> dedupe against a throwaway vault; extraction smoke-tested on real articles.

**Problem.** A source only enters the brain if someone hand-drops a correctly-
frontmattered file into `sources/`. That's the real bottleneck: capture requires being
at the keyboard *in this repo*. Everything downstream (the nightly `/sync`, the whole
wiki) is starved by it.

**What it is.** A thin external writer that lands raw, immutable material into
`sources/` with valid frontmatter — and nothing else. It does **zero synthesis**; the
launchd `/sync` already scheduled for 02:00 folds it into the wiki.

Surfaces, cheapest → richest (✅ = built):
- ✅ `bin/brain-clip.sh <url|file|"text">` — the deterministic core (above).
- ✅ **Clip to Brain.app** — an AppleScript app (built with `osacompile` into
  `~/Applications`). Double-click → clips the clipboard / a URL (or prompts); drag
  files & PDFs onto it. Source: `bin/gui/clip-to-brain.applescript`.
- ✅ **Watched inbox folder** — `~/Brain Inbox`; a launchd `WatchPaths` agent
  (`com.secondbrain.clip`) runs `bin/brain-clip-watch.sh` on every drop (resolving
  `.webloc`/`.url` links to URLs), then archives the original to `_done/`. This is the
  share-sheet "Save to folder" target.
- ✅ **Right-click Service** — an Automator Quick Action
  (`bin/gui/clip-service/Clip to Brain.workflow`) installed to `~/Library/Services`:
  select text/a link anywhere → right-click → Services → "Clip to Brain".
- ✅ **Browser button** — an unpacked Chrome extension (`bin/gui/chrome-extension`)
  whose toolbar popup POSTs the current tab to a localhost helper
  (`bin/brain-clip-server.py`, kept alive by the `com.secondbrain.clipserver` agent),
  which shells out to `brain-clip.sh`.

All five deploy via **`bin/brain-clip-gui.sh install`** (or `app|folder|service|browser`
individually; `status`; `uninstall [which]`), mirroring `bin/brain-schedule.sh`. The
launchd agents here run plain shell/python — no `claude`, no `bypassPermissions` — so
unlike the sync/digest agents they carry no special-privilege caveat.
- `email-to-source` (a watched mailbox) remains a future surface.

**MVP.** `bin/brain-clip.sh`:
1. Slugify title → `YYYY-MM-DD-<slug>`, dedupe if exists.
2. Fetch + readability-extract body to markdown.
3. Emit frontmatter (`id, title, type: article, url, captured`) + body.
4. Write to `sources/`. Done — leave it for `/sync`.

**Effort.** Low–medium (fetch + extract is the only real work).
**Risk.** HTML→markdown extraction quality; mitigated because the source is raw by
design — I clean it up in the recap, not the clipper.

---

## 2. Wiki server — get synthesis OUT to a reader  ✅ BUILT 2026-06-23

> Shipped as `bin/brain-serve.py` (+ `bin/brain-serve.sh` launcher). Run
> `bin/brain-serve.sh [port]` (default 8765) → browse at `http://127.0.0.1:<port>`.
> Stdlib-only, read-only, no LLM; re-reads files per request so edits show live.
> Resolves `[[wikilinks]]` and `[src-id]` citations into navigation, renders a
> per-page **Linked from** backlinks panel and a **Sources** panel, links citations to
> the immutable raw source (`/source/<id>` with a **Cited by** panel), shows `stub`
> badges in the sidebar, and styles dangling links red. Smoke-tested across all routes.


**Problem.** The wiki is raw `.md` on disk. Reading it = opening files; `[[wikilinks]]`
don't resolve; the source→recap→concept graph is invisible.

**What it is.** A local read-only renderer over `wiki/**.md` + `index.md`. Parses
frontmatter, rewrites `[[path]]` → real links, builds a backlink/graph view, surfaces
`status: stub` and dangling links. Crucially it does **no LLM work at read time** — it
serves only what I precomputed. That *is* principle #4 ("precompute synthesis; reads are
instant and auditable").

**MVP.** ~100-line static renderer (or tiny local server):
- Walk `wiki/`, parse frontmatter, render body.
- Resolve `[[a/b]]` → link to that page; unresolved → flagged "create me".
- `index.md` as the home/map of content.
- Bonus: backlinks panel (who cites this source ID / links this page).

**Effort.** Low for static render; medium with graph/backlinks.
**Risk.** Low. Read-only, can't corrupt anything. Keep it dumb — no querying-via-LLM
(that's a different, RAG-shaped product the brain deliberately rejects).

---

## 3. Contract validator — keep the brain VALID without me  ✅ BUILT 2026-06-23

> Shipped as `bin/brain-validate.sh` (+ `bin/hooks/pre-commit`). Run
> `bin/brain-validate.sh` to validate, `--quiet` for FAIL/WARN only, `--install-hook`
> to symlink the pre-commit guard. Exit 1 on any FAIL; dangling `[[links]]` are WARN
> only. Validated clean against the current repo (9 files, 0 fail).


**Problem.** The schema in `CLAUDE.md` is currently enforced only by my discretion
during `/lint`. On unattended headless runs (`claude -p --permission-mode
bypassPermissions`), a malformed page can land silently.

**What it is.** A standalone CLI that checks the **deterministic** subset of the
contract — runnable as a git pre-commit hook or CI gate, independent of any LLM. `/lint`
keeps the judgment calls (contradictions, starved stubs, stale dates); the validator
catches mechanical breakage instantly, and it guards both *my* output and anything tool
#1 writes.

**Checks (all mechanical, all fail-fast):**
- Every `sources/*.md` has required frontmatter; `id` == filename stem.
- Every `wiki/*.md` has required frontmatter; `type` ∈ allowed; slug is kebab-case.
- Every `[[link]]` resolves to an existing `wiki/` page (or is reported as dangling).
- Every wiki `sources: [...]` entry and inline `[src-id]` points at a real source file.
- `updated >= created`; dates parse.

**MVP.** `bin/brain-validate.sh` exiting non-zero on any violation; wire into a
pre-commit hook.
**Effort.** Low. Pure parsing, no network, no model.
**Risk.** Very low. The one design call: dangling `[[links]]` are *allowed* by
`CLAUDE.md` (they signal pages worth creating) — so the validator **warns**, never fails,
on those; it only **fails** on missing frontmatter, bad slugs, and citations to
nonexistent source IDs.

---

## Recommended build order

1. **#3 Validator first** — cheapest, pure-deterministic, and it makes #1 safe by
   guarding whatever the clipper writes.
2. **#1 Capture bridge** — the actual unlock; nothing else matters if raw material
   can't get in without a keyboard in this repo.
3. **#2 Wiki server** — highest polish, lowest urgency; the wiki is readable as files
   until the corpus is big enough to need navigation.

All three are shell-first (`bin/`), matching the existing `brain-*.sh` convention, so
they stay in-repo, version-controlled, and runnable by the same launchd machinery.
