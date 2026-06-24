# External-but-Matched Tools — Design Spec

Status: **all four built** · Created: 2026-06-23 ·
Last built: 2026-06-24 (#4 pull feeder)

Companion tools that live *outside* the brain's internal skills (`/capture`, `/sync`,
`/lint`, `/digest`, `/remember`) but bind to the **same contract** defined in
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

The tools map onto the three sides of the brain:

| Tool | Side | Binds to | Without me / you-in-repo? |
|---|---|---|---|
| 1. Capture bridge | Material **IN** (push) | Source frontmatter + sync flow | Yes — lands sources from anywhere |
| 2. Wiki server | Synthesis **OUT** | Wiki frontmatter + wikilinks | Yes — read side, no LLM at read time |
| 3. Contract validator | Schema **INTEGRITY** | Whole `CLAUDE.md` schema | Yes — guards headless runs |
| 4. Pull feeder | Material **IN** (pull) | Source frontmatter + sync flow + #1 deposit | Yes — subscribes to feeds, deposits unattended |

They form a pipeline: **#1/#4 feed → #3 guards what's fed and what I write → #2 serves
the result.** #1 is *push* (you clip something); #4 is *pull* (it subscribes and fetches
on a schedule). #4 deliberately reuses #1's deposit path rather than reimplementing it.

---

## 1. Capture bridge — get material IN from the wild  ✅ BUILT 2026-06-23

> Shipped as `bin/brain-clip.sh`. Deterministic, no-LLM front door (curl + python3
> stdlib only) that deposits ONE raw, immutable source into `sources/` with valid
> frontmatter — then stops. The nightly `/sync` folds it in. Three modes, auto-detected
> from the argument:
> - **URL** → `curl` fetch + a stdlib `HTMLParser` readability pass → `type: article`
>   markdown (title/author pulled from `og:`/`<title>`/`meta[author]`); nav/script/style
>   stripped.
> - **Video URL** (YouTube/Vimeo) → recognized by host and pulled as its **captions
>   transcript** via `yt-dlp` (auto/uploaded subs, flattened from WebVTT to prose;
>   title/uploader from the `info.json`) → `type: transcript`. This is the one path with
>   an optional dependency: no `yt-dlp` ⇒ a logged heads-up and graceful fall-back to the
>   page-extraction path above (the player HTML), never a silent failure.
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
  which shells out to `brain-clip.sh`. On a YouTube/Vimeo tab the popup detects the
  video host, relabels its button to **“Clip transcript”**, and captures the captions
  transcript (`type: transcript`) instead of the page — same auto-detection as the CLI.

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
>
> **Upgraded 2026-06-23 → `tidy` SDK.** The checks now live in `bin/brain_tidy.py`
> (stdlib-only, importable + CLI; the single source of truth), and `brain-validate.sh`
> is a thin shim that delegates to it. `tidy` adds the **safe auto-fix** half (`--fix`:
> clamp `updated<created`, case-only wikilink repair, frontmatter list spacing — nothing
> that needs judgment, and never writes `sources/`) and a deterministic `--backlog`
> (sources lacking a recap). SDK: `find_violations()`, `fix()`, `backlog()`. The nightly
> `brain-sync.sh` now runs `tidy --fix` then calls `claude -p /sync` *only if the backlog
> is non-empty*. Rationale in [docs/adr/0001](adr/0001-deterministic-tidy-sdk.md).


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

## 4. Pull feeder — get material IN on a schedule  ✅ BUILT 2026-06-24

> Shipped as `bin/brain-feed.py` (+ `bin/brain-feed.sh` wrapper). Where #1 is *push* (you
> clip one thing, deliberately, now), #4 is *pull* — it subscribes to feeds (`feeds.toml`)
> and fetches new material **unattended, once a day**, doing the same zero-synthesis
> deposit as #1 and reusing #1's renderer; the 02:00 `/sync` folds it in. The design's
> hard part — not poisoning the brain with a firehose — is solved by **per-feed trust**
> (`auto` → `sources/`; `queue` → `.brain/review/`) + a **per-feed daily cap** (overflow
> deferred unseen, drains over later days). Four adapters: `rss`/`list` are pure-stdlib;
> `yt` (yt-dlp captions) and `email` (IMAP, Keychain app-password) degrade gracefully —
> absent dep/creds disables the adapter with a logged reason, never breaking the run.
> State in `.brain/feed-state.db` (sqlite: seen GUIDs + per-feed daily counts); deposits
> carry `via: <feed-id>` provenance and are deduped against existing `sources/` `url:`s.
> Commands: `brain-feed run [--dry-run] [--feed ID]`, `brain-feed review` (interactive
> k/d/s triage), `brain-feed status`. Schedule (opt-in, daily 01:30) via
> `bin/brain-feed-schedule.sh install|status|run|uninstall` +
> `bin/launchd/com.secondbrain.feed.plist` — plain python, no `claude`, no special
> privilege. Verified end-to-end (rss auto+queue, atom, list line-commenting, cap +
> defer/drain across days, dedup, provenance, review, dry-run, validator-clean deposits;
> VTT + email-body helpers unit-tested) against a throwaway vault + local HTTP server.

**Problem.** #1 closed "capture needs a keyboard in this repo" — but it's still *push*:
a human has to decide, per item, to clip it. The material a person most wants in a second
brain (a favourite author's blog, newsletters, a few YouTube channels, a to-read pile)
arrives *continuously* and never gets clipped because clipping each one is friction. The
brain starves not for lack of a deposit path but for lack of an *active* one.

**What it is.** A deterministic, once-daily poller. It reads a committed `feeds.toml`,
pulls new items from each subscribed feed via a small set of **adapters**, and routes
each item by the feed's **trust level**: `trust` feeds deposit straight into `sources/`;
`queue` feeds drop candidates into a review pen you triage by hand. A **per-feed N/day
cap** bounds throughput so no single feed can flood the brain; overflow is deferred
(left unseen) and drains over subsequent days — **bounded but lossless**. It does **zero
synthesis** and reuses #1 for the actual deposit; the 02:00 `/sync` does the folding.

### Resolving the core tension — a poller is not "deliberate capture"

`CLAUDE.md` principle: *"Bad sources poison the brain. Capture deliberately."* A
scheduled poller is, by construction, not deliberate per-item. The design moves the
deliberate act **up one level**, from *per-item* to *per-subscription*:

- **Per-feed trust.** You curate once, when you add a feed: a trusted author's blog gets
  `trust = "auto"` and flows straight in; a noisy firehose (an HN query, a subreddit)
  gets `trust = "queue"` and waits for your `k/d/s` triage. Choosing and trusting feeds
  *is* the deliberate act.
- **Per-feed daily cap (`n`).** Even a trusted feed can't dump 40 posts in one night —
  it contributes at most `n`/day, the rest deferred unseen and drained over following
  days. Closes the one hole in trust-only routing (a trusted feed going rogue).

### Architecture — one core, four adapters

```
feeds.toml ─┐
            ├─► [poller core] ──per item──► dedup ──► cap ──► (trust?)
 adapters:  │        │                                  ├─auto──► sources/
  rss ──────┤   .brain/feed-state.db (sqlite)           └─queue─► .brain/review/
  email ────┤   seen GUIDs + per-feed daily counts                     │
  list ─────┤                                              brain-feed review (k/d/s)
  yt  ──────┘                                                    keep ──► sources/
 (rss + captions)
```

Each adapter yields normalized items `(title, url | body, type, feed-id, tags)`. The
core handles dedup, cap, trust-routing, and deposit — so adapters stay thin. **Deposit
reuses tool #1**: the core calls `brain-clip.sh --dry-run` to render a contract-valid
source, then *places* that file into `sources/` (trusted) or `.brain/review/` (queued)
itself. All frontmatter/slug/extraction logic stays in one place, and tool #3 still
guards whatever lands.

**Adapters** (RSS/Atom is the universal substrate — blogs, newsletters-with-RSS,
YouTube channels, podcasts, Reddit, HN, GitHub releases, arXiv all expose it):

- **`rss`** — parse a feed (stdlib `xml.etree` / `HTMLParser`), yield new entries; body
  via #1's URL fetch+extract. *Pure stdlib.*
- **`list`** — drain a markdown URL list (e.g. `~/Brain Inbox/to-read.md`), one clip per
  URL. Drained lines are **commented out** (`# done: …`) in place, not deleted, to keep
  a record. *Pure stdlib.*
- **`yt`** — the `rss` adapter plus a caption fetch: if `yt-dlp` is on `PATH`, pull
  transcript → `type: transcript`; else fall back to the RSS summary as body →
  `type: article`. *Optional dep.*
- **`email`** — IMAP poll (stdlib `imaplib`) of a Gmail label; app-password read at
  runtime from the **macOS Keychain** (`security find-generic-password`), never on disk
  or in git. Activates only if creds are present; else the adapter is disabled and logs
  why. *Optional creds.*

The heavyweight adapters (`yt`, `email`) are **optional with graceful degradation** —
the core (`rss`, `list`) stays pure-stdlib and key-free, preserving the "runs anywhere,
no keys" property the rest of `bin/` guards.

### State, config, cadence

- **Seen-state:** `.brain/feed-state.db` (stdlib `sqlite3`, gitignored) — tables for
  seen `(feed, guid, ts)` and per-feed daily counts. SQLite is what makes the
  defer-overflow cap implementable: the DB remembers what it held back.
- **Config:** `feeds.toml` (committed; stdlib `tomllib` on py3.14). Per-feed:
  `adapter`, `trust` (`auto` | `queue`), `n` (daily cap, default global), `url`/label/
  path, optional `tags`/`title`. Committed because your subscription list *is* part of
  the brain's identity. Ships with 2–3 commented example feeds (an author blog, an
  HN-RSS query, an arXiv feed) so it's self-documenting on first run.
- **Cadence:** once daily ~01:30 via a `com.secondbrain.feed` launchd agent — just
  before the 02:00 `/sync`, so trusted deposits ride the same night's fold and the
  review queue is waiting each morning. The agent runs plain python/shell (no `claude`,
  no `bypassPermissions`), so unlike the sync/digest agents it carries no
  special-privilege caveat.
- **Provenance & dedup:** each pulled source carries `via: <feed-id>` and `url:` in its
  frontmatter (the validator checks required keys are *present*, not that extras are
  absent — extra keys are fine). Before depositing, the core scans existing
  `sources/*` `url:` values so anything you already clipped by hand is never re-pulled.

### Review triage

Queued candidates are *already* complete, frontmattered source files in `.brain/review/`
— "approve" is just "move into `sources/`." `brain-feed review` walks them interactively:
prints title + url + first lines, you press `k`(eep → `sources/`) / `d`(rop → delete) /
`s`(kip → leave for next time). Keyboard-only, deterministic, no LLM.

### Surfaces & deploy

`bin/brain-feed.py` (core) + `bin/brain-feed.sh` (wrapper), with
`bin/brain-feed-schedule.sh install | status | run | uninstall` mirroring
`bin/brain-schedule.sh`. The deterministic core is always hand-runnable
(`brain-feed run`, `brain-feed review`); the 01:30 schedule is opt-in.

**MVP path (if/when built).** Even committing to all four adapters, land them against a
stable core in order of cost: **`rss` → `list`** (both pure-stdlib, the actual unlock)
**→ `yt` → `email`** (each drags in one optional dependency/secret). The core, sqlite
state, cap logic, trust routing, and `review` command are built once, up front.

**Effort.** Medium — the poller core + sqlite state + cap/trust routing is the real
work; `rss`/`list` are small; `yt`/`email` add one external dependency each.
**Risk.** Low–medium. *Poisoning* is the main risk, mitigated by trust + cap + the
review gate. Extraction quality inherits #1's (raw by design — cleaned in the recap, not
the clipper). The one secret (IMAP) is quarantined in the Keychain. `email`/`yt` failing
degrades gracefully rather than breaking the run.

**Open design defaults (revisit at build time):** `yt` type fallback (transcript→
`transcript`, else `article`); `list` drain comments-out rather than deletes; ship
`feeds.toml` with commented examples. All three lean the "keep a record / self-
documenting" way.

---

## Recommended build order

All four are **built**. #4 slotted in last because it *depends on* #1 (it reuses the
clipper's deposit) and #3 (which guards what it writes):

1. **#3 Validator first** — cheapest, pure-deterministic, and it makes #1 safe by
   guarding whatever the clipper writes. ✅
2. **#1 Capture bridge** — the actual unlock; nothing else matters if raw material
   can't get in without a keyboard in this repo. ✅
3. **#2 Wiki server** — highest polish, lowest urgency; the wiki is readable as files
   until the corpus is big enough to need navigation. ✅
4. **#4 Pull feeder** — built on #1's deposit + #3's guard. Turns capture from *push*
   into *pull* so the brain feeds itself; the highest-leverage tool, built last only
   because it presumes the deposit path #1 already provides. ✅

All four are shell/python-first (`bin/`), matching the existing `brain-*.sh` convention,
so they stay in-repo, version-controlled, and runnable by the same launchd machinery.
