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

## 2026-06-23 — infra: capture bridge (external tool #1 of docs/external-tools.md)
- bin: created `bin/brain-clip.sh` — the deterministic, no-LLM front door that lands ONE
  raw, immutable source into `sources/` with valid frontmatter, then stops (nightly
  `/sync` folds it in). Dependency-light (curl + python3 stdlib) so it can run from a
  macOS Shortcut / iOS share-sheet / browser button / cron with no API key. Three
  auto-detected modes: URL → curl fetch + stdlib `HTMLParser` readability extract →
  `type: article` markdown (title/author from `og:`/`<title>`/`meta`); FILE → text files
  inlined as markdown source, binaries (pdf/image/data) copied as-is + `<stem>.meta.md`
  sidecar, type by extension; TEXT/stdin (`-`) → `type: note`. Slugifies to a
  date-prefixed kebab `id`, dedupes (`-2`,`-3`) on collision, then runs the contract
  validator (tool #3) on its own output (#3 guards what #1 feeds). Flags: `--type
  --title --author --url --dry-run`. Distinct from `bin/brain-capture.sh` (full LLM
  ripple) — the clipper only deposits.
- verification: built and tested against a throwaway fakevault in scratchpad (never the
  immutable real `sources/`). Confirmed all three modes + dedupe, flags-anywhere parsing
  (incl. flags after the path), bad-`--type` rejection, empty-input guard; extraction
  smoke-tested on real pages (example.com + the askglitch seed article, ~15KB clean
  markdown, title+author resolved). Validator passes on every written source (0 fail).
  Real repo still 9 files / 0 fail; real `sources/` left pristine.
- docs: marked tool #1 BUILT in docs/external-tools.md; updated the status line to
  "all three built". The IN/INTEGRITY/OUT pipeline is now complete in code.
- not committed yet — awaiting user.

## 2026-06-23 — infra: capture-bridge GUI surfaces + brain-clip.sh cwd bugfix
- bin: created `bin/brain-clip-gui.sh` — one installer (mirrors brain-schedule.sh:
  install/app/folder/service/browser/status/uninstall) deploying four GUI front ends,
  all of which funnel into `bin/brain-clip.sh`:
  1. **Clip to Brain.app** — `bin/gui/clip-to-brain.applescript`, built via `osacompile`
     into ~/Applications. Double-click clips the clipboard/URL (or prompts); drag files
     onto it. PATH + script path injected at build time.
  2. **Watched inbox** — `bin/brain-clip-watch.sh` + launchd WatchPaths agent
     `bin/launchd/com.secondbrain.clip.plist` over ~/Brain Inbox; resolves `.webloc`/
     `.url` links, archives originals to `_done/`, lock-serialized.
  3. **Right-click Service** — Automator Quick Action
     `bin/gui/clip-service/Clip to Brain.workflow` → ~/Library/Services.
  4. **Browser button** — unpacked Chrome extension `bin/gui/chrome-extension/`
     (MV3 popup) → POSTs the tab to `bin/brain-clip-server.py` (stdlib HTTP, 127.0.0.1:8766,
     arg-list subprocess, no shell), kept alive by `com.secondbrain.clipserver.plist`.
- BUGFIX (important): `bin/brain-clip.sh` wrote to `sources/` **relative to the current
  working directory**, not to the vault — it computed `$VAULT` but only used it for the
  validator call. Last turn's tests masked this by `cd`-ing into the test vault first.
  The watched-folder test (run from the repo root against the scratch vault) exposed it:
  the scratch clipper wrote into the REAL `sources/`. Root cause confirmed by a
  controlled experiment. Fix: absolutize a file argument before `cd`, then `cd "$VAULT"`
  so every mode writes into the repo regardless of where it's launched (app, share-sheet,
  cron, any directory). Re-verified: foreign-cwd CLI and the watcher now write to the
  vault only; no stray `./sources` is created.
- cleanup: removed 4 test artifacts that the pre-fix bug leaked into the real `sources/`
  (`2026-06-23-{dropped,example-domain,example-domain-2,zzz-experiment-marker}.md`) —
  my own accidental output, never committed, not genuine captures. `sources/` is back to
  the single real source + README; repo validates 9 files / 0 fail.
- verification: all static checks pass (zsh -n, py_compile, `plutil -lint` on both plists
  + the .workflow's Info.plist/document.wflow, manifest.json JSON-lint, `osacompile`
  compiles the app). Runtime smoke tests against the scratch vault: helper server
  (GET /health, POST /clip url + text + empty-error) and the inbox watcher (file +
  `.url` + `.webloc`, archiving, log) both pass; every written source validates clean.
  Not runtime-verifiable headlessly (documented as manual GUI steps): the app's
  click/drop handlers, the Service appearing in the right-click menu (enable under System
  Settings ▸ Keyboard ▸ Services), and loading the unpacked Chrome extension.
- docs: expanded the tool #1 "Surfaces" list in docs/external-tools.md (all five marked
  built, with file pointers + the installer).
- not run on this machine / not committed — the user runs `bin/brain-clip-gui.sh install`
  to deploy (builds the app, loads the two agents, installs the Service, creates the
  inbox). Left for the user, consistent with the scheduler.

## 2026-06-23 — `tidy` SDK (deterministic maintenance, outside Claude)

Design settled via /grill-with-docs ("can we make an SDK to run tidy or sync outside of
Claude"), then built.

- **Key finding.** The Claude Agent SDK can't be the answer: it requires a per-token
  `ANTHROPIC_API_KEY` and may not reuse the Claude Code subscription/OAuth — which is the
  only auth the user has. And `sync` is synthesis (needs an LLM), so it can't leave Claude
  in any real sense. Conclusion: only the **mechanical** half can run outside Claude.
- **Built `bin/brain_tidy.py`** — stdlib-only, importable SDK + CLI; the single source of
  truth for deterministic schema checks. SDK: `find_violations()`, `fix()`, `backlog()`.
  CLI: default check (exit 1 on FAIL), `--quiet`, `--fix`, `--backlog`, `--json`.
  - Ports every check from the old shell validator into structured `Violation` objects.
  - Adds the **safe-fix** half (only these three): clamp `updated<created`, case-only
    wikilink repair (unique case-insensitive match; alias/anchor preserved; skips inline
    code), frontmatter list-spacing. Never writes `sources/`. Reports — never fixes —
    anything needing judgment (missing keys, fuzzy typos, bad type/status, stubs, dupes).
  - Existence checks are **case-sensitive via a page index**, not `Path.is_file()` —
    macOS's case-insensitive FS otherwise hid wrong-case links and killed the case-fix.
- **`bin/brain-validate.sh` → thin shim** that execs `brain_tidy.py` (keeps the
  pre-commit hook + `--install-hook` working; no second validator to drift).
- **`bin/brain-sync.sh` rewired**: run `tidy --fix` first, then invoke `claude -p /sync`
  **only if `--backlog` is non-empty** — mechanical cleanup is free, tokens spent only on
  real synthesis work.
- **Docs.** Added `docs/adr/0001-deterministic-tidy-sdk.md` (why the boundary), `CONTEXT.md`
  glossary (tidy / sync / backlog / judgment-vs-mechanical / "outside of Claude"), and
  updated `docs/external-tools.md` tool #3.
- **Verified.** `py_compile` clean; real vault validates 0 fail (parity with old shim) and
  `--backlog` lists the 2 unprocessed sources. Scratch vault with deliberate breakage:
  all checks fire, the three fixes apply correctly, re-running `--fix` is idempotent,
  the immutable bad-`id` source is reported not touched, an in-code `[[link]]` is left
  alone. `zsh -n` clean on both shell scripts; pre-commit hook + `--install-hook` work.

---

## 2026-06-23 — /sync (1 source + 1 skip-marker)

**Backlog reconciled.** Two sources were unprocessed; one was test noise.

- **Skip-marker.** `2026-06-23-testing-from-extension` (body: "Testing from extension",
  url `chrome://extensions/`) was a capture-extension smoke test. Sources are immutable,
  so rather than delete it, wrote a stub recap
  `wiki/recaps/2026-06-23-testing-from-extension.md` (`status: stub`, tags
  `[test-artifact, ignore]`) to drop it from the backlog and tell `/sync` + `/digest` not
  to ripple it. This kept tonight's 02:00 auto-sync from synthesizing junk into the wiki.
- **Real source reconciled.** `2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo`
  — a first-person war story: a note-cleanup feature on a single Groq model, no fallback,
  went down overnight (Sentry flood, users affected); fixed with a second model, then
  migrated to OpenRouter for redundancy. This is the brain's first piece of personal
  engineering knowledge (prior pages were all meta, about the wiki method itself).
- **Pages written:** recap; new concept `concepts/llm-fallback-strategy` (`active`,
  aliases: model fallback / model redundancy / provider redundancy); new entity stubs
  `entities/groq`, `entities/openrouter`, `entities/sentry`.
- **Index updated.** Added a "Tools & providers" entity subsection, the fallback-strategy
  concept, and a Recently-updated entry.
- **No contradictions** (single-source batch). Verified: `--backlog` now empty.

## 2026-06-23 — design: pull feeder (external tool #4 of docs/external-tools.md)

Froze the design for a fourth external-but-matched tool via a `/grill-me` session. No
code written — spec only.

- **What.** `brain-feed` — a deterministic, once-daily *pull* poller (vs #1's *push*
  clip). Subscribes to feeds, deposits new material unattended, reuses #1's renderer for
  the actual deposit; the 02:00 `/sync` folds it in.
- **Core tension resolved.** A scheduled poller contradicts "capture deliberately." Fix:
  move the deliberate act from *per-item* to *per-subscription* via **per-feed trust**
  (`auto` → straight to `sources/`; `queue` → review pen) plus a **per-feed daily cap**
  (overflow deferred, lossless — bounded throughput stops any feed flooding the brain).
- **Adapters.** `rss` (universal substrate) + `list` (drain a to-read md) are pure
  stdlib; `yt` (yt-dlp captions) + `email` (IMAP, Keychain app-password) are optional
  with graceful degradation, preserving bin/'s "runs anywhere, no keys" property.
- **State/config.** `.brain/feed-state.db` (sqlite, gitignored) for seen GUIDs + daily
  counts; `feeds.toml` (committed, stdlib tomllib) as the curation surface. Review via
  `brain-feed review` (interactive k/d/s). Provenance `via:` frontmatter; corpus dedup
  on `url:`.
- **Decisions captured in** `docs/external-tools.md` §4 (status: DESIGNED, NOT BUILT) +
  build-order entry #4. Build deferred — it depends on #1 (deposit) and #3 (guard),
  both already shipped.

## 2026-06-24 — build: pull feeder (external tool #4 of docs/external-tools.md)

Built the fourth external-but-matched tool, the *pull* feeder, from its frozen design.
Turns capture from push-only into pull: the brain now feeds itself unattended.

- **Shipped.** `bin/brain-feed.py` (core + four adapters), `bin/brain-feed.sh` (wrapper),
  `bin/brain-feed-schedule.sh` (install/status/run/uninstall), `bin/launchd/
  com.secondbrain.feed.plist` (opt-in daily 01:30 — plain python, no `claude`), and a
  committed `feeds.toml` (ships with commented examples; first run is a safe no-op).
- **How it works.** Reads `feeds.toml`, pulls new items per adapter, dedups (seen GUIDs
  in `.brain/feed-state.db` + against existing `sources/` `url:`s), applies a per-feed
  daily cap (overflow deferred unseen, drains later days), then routes by trust:
  `auto` → `sources/`, `queue` → `.brain/review/`. Deposit RENDERS via `brain-clip.sh
  --dry-run` then places the file itself, injecting `via:`/`tags:` provenance — so all
  frontmatter/slug/extraction logic stays in tool #1 and tool #3 still guards what lands.
- **Adapters.** `rss` (RSS+Atom, namespace-agnostic) and `list` (drain a markdown
  to-read pile; drained URLs commented `# done:` in place) are pure stdlib. `yt` (yt-dlp
  captions → transcript, else feed summary → article) and `email` (IMAP poll, app-
  password from the macOS Keychain) degrade gracefully — a missing dep/cred disables the
  adapter with a logged reason, never breaking the run.
- **Commands.** `brain-feed run [--dry-run] [--feed ID]`, `brain-feed review` (interactive
  k/d/s), `brain-feed status`.
- **Verified.** Integration-tested end-to-end against a throwaway vault + a local HTTP
  server: rss auto+queue, atom parsing, list line-commenting, cap + defer/drain across
  days, idempotent re-run, dedup vs a hand-clip, provenance injection, review triage,
  dry-run leaving no trace, and validator-clean deposits — plus unit tests for the VTT
  flattener, email body extraction, and the degradation paths. 23/23 green.
- **Docs.** `docs/external-tools.md` §4 flipped to BUILT (+ status header + build-order);
  README "Local tooling" gained a pull bullet. No `CLAUDE.md` change (the feeder, like
  the clipper, is a deterministic surrounding tool, not an LLM workflow).

## 2026-06-24 — feat: clipper recognizes video URLs → captions transcript

- **What.** `bin/brain-clip.sh` MODE 1 (URL) now branches: a recognized video host
  (YouTube `youtube.com`/`youtu.be`/`m.`/`music.`, Vimeo) is pulled as its **captions
  transcript** via `yt-dlp` (auto + uploaded subs, `en.*`, WebVTT flattened to prose;
  `title`/`uploader` from the `--write-info-json`) and written as `type: transcript`.
  Everything else keeps the existing `curl` + `HTMLParser` article path. Both branches
  emit the same `@@TITLE@@/@@AUTHOR@@/@@BODY@@` protocol, so the downstream id/slug/
  dedupe/validate logic is untouched.
- **Why.** Before, a bare video URL only got a real transcript through the feed's `yt`
  *channel* adapter; a one-off video link (hand-clipped, dropped in the watch folder, or
  listed in a `list` to-read feed) fell through to player-page HTML — useless. Putting
  the detection in the clipper means every URL deposit path gains video support at once.
- **Graceful degradation.** `yt-dlp` is the only optional dep and stays optional: if it
  isn't on PATH the clipper logs a heads-up and falls back to page extraction; if it runs
  but the video has no captions, it deposits a clear "no transcript available" stub
  (`type: transcript`) rather than failing. `--no-playlist` + `--socket-timeout 30` keep
  a stray `?list=` or a hang from biting.
- **Verified.** Tested with a stub `yt-dlp` injecting a synthetic VTT + info.json:
  transcript deposited as `type: transcript`, title/author from the json, timing tags and
  adjacent dupe captions stripped, `youtu.be` short form detected, `&list=` ignored. Also
  confirmed the no-yt-dlp warning fires and falls back, and a non-video URL is unchanged.
- **Docs.** README capture bullet, `docs/external-tools.md` §1 (added a Video-URL mode),
  and `feeds.toml` `list` note all updated. No `CLAUDE.md` change — the clipper remains a
  deterministic surrounding tool, not an LLM workflow. Follow-up worth considering: thin
  the feed's `yt` adapter to reuse this one transcript path (removes the duplicate VTT
  flattener in `brain-feed.py`).

## 2026-06-24 — feat: Chrome clip extension is video-aware

- **What.** The "Clip to Brain" popup (`bin/gui/chrome-extension`) now detects a
  YouTube/Vimeo tab (`VIDEO_RE`, mirroring `is_video_url` in `brain-clip.sh`), relabels
  its primary button to **"Clip transcript"**, and shows a hint that it captures the
  captions transcript (needs `yt-dlp` on the host). manifest bumped to 1.1.0.
- **Plumbing was already there.** `brain-clip-server.py` forwards the tab URL straight to
  `brain-clip.sh`, which already auto-routes video URLs to the transcript path — so this
  is a pure UX change, no server/permission change (still `tabs` + localhost only).
- **One correctness fix.** For a video tab the primary button now ALWAYS posts the URL
  (the transcript); previously a typed note silently hijacked any page-clip into a plain
  note, which would have been surprising under a "Clip transcript" label. "Clip note
  only" still deposits a standalone note.
- **Verified.** Detection unit-tested in node across youtube/youtu.be/m./music./shorts/
  vimeo + a `notyoutube.com.evil.com` spoof (rejected). Full chain exercised live:
  POST {url,title} → clip server → clipper video branch deposited `type: transcript`
  with metadata + flattened captions (stub `yt-dlp`), throwaway file then removed.
- **Docs.** `docs/external-tools.md` browser-button bullet + `bin/brain-clip-gui.sh`
  install hint updated.

## 2026-06-24 — feat: redesigned clip extension popup + note-above-capture

- **What.** Reskinned the "Clip to Brain" popup (`bin/gui/chrome-extension`) to the dark
  gold-on-charcoal design: `CLIP TO BRAIN` wordmark + `→ sources/` tag, a current-tab
  card (favicon/title/url), a detection row (Article/Video/Local file + a token-size
  estimate), toggleable suggested-tag chips, the optional-note box, a non-web-page
  warning, primary **Clip to sources** (⌘S) + ghost **Note only**, and a success state
  (checkmark + saved `sources/inbox/…` path + Clip another). manifest → 1.2.0.
- **Real data, no mock state.** favicon/title/url/kind come from `chrome.tabs`; suggested
  tags + the size estimate are read from the live page by a one-shot
  `chrome.scripting.executeScript` (page `<meta keywords>`/`og:tag` + `body.innerText`
  length) under the `activeTab` grant — added `activeTab` + `scripting` to the manifest.
  The tags section hides itself when the page exposes none (nothing fabricated).
- **Backend: `--note` so a note rides ABOVE a page capture.** New `--note` flag on
  `brain-clip.sh` prepends the reader's note (as a blockquote, with a `---` rule) above
  the extracted page/file body, keeping the raw capture intact beneath it. Source
  frontmatter is unchanged (no `tags` key — tags live on wiki pages), so selected chips
  are folded into the body as a `Tags: #a #b` hint line for the nightly `/sync`.
  `brain-clip-server.py` now accepts `note`/`tags`: a page clip routes through `--note`
  (extraction preserved) instead of the old behaviour where a typed note hijacked the
  page into a plain note; note-only and the legacy `{url,text}`/`{url,title}` payloads
  are unchanged.
- **Deliberately NOT done.** URL-dedupe-and-update from the design spec was skipped — it
  would mutate an existing `sources/` file, violating Layer-1 immutability; the clipper
  stays append-only. No "Open Review Queue" button either (the `queue-ui` app isn't
  built yet — no dead link shipped).
- **Verified.** `zsh -n` + `py_compile` + `node --check` clean; manifest is valid JSON;
  `--note` prepend confirmed via `--dry-run`; server `run_clip` routing unit-checked for
  page-clip/note-only/legacy/empty payloads (correct arg lists, tags slugified). Live
  popup render is the human's to eyeball on reload.

## 2026-06-24 — activate: pull feeder (5 subscriptions + daily schedule)

- **Why.** The pull-feeder machinery (external tool #4) was built but dormant: `feeds.toml`
  had zero active feeds and `com.secondbrain.feed` was never loaded, so nothing flowed in
  automatically. The human asked to turn it on.
- **Subscriptions (all HTTP-200 validated at activation).** Wrote 5 `[[feed]]` blocks to
  `feeds.toml`, chosen to match the brain's demonstrated focus (LLMs, agentic coding, NLP):
  `simon-willison` (rss, auto, cap 3), `andrej-karpathy` (rss, auto, cap 2,
  karpathy.bearblog.dev), `hn-ai` (rss, queue, cap 10), `arxiv-cs-cl` (rss, queue, cap 5),
  `lobsters-ai` (rss, queue, cap 8).
- **Lobsters gotcha.** Used the `ai` tag feed only — Lobsters' `ml` tag means
  MetaLanguage/OCaml, not machine learning, so `ai,ml` would import compiler noise.
- **Schedule.** `bin/brain-feed-schedule.sh install` → `com.secondbrain.feed` loaded, polls
  daily 01:30 (just before the 02:00 `/sync`). Plain python/shell, no bypassPermissions.
- **First real pull.** 5 deposited to `sources/` (the two `auto` blogs), 23 queued to
  `.brain/review/` (the three aggregators; overflow deferred under per-feed caps). Deposited
  sources carry valid frontmatter (`id/title/type/url/captured/via/tags`). They ride
  tonight's `/sync`; the queue awaits `brain-feed review`. Now 9 sources, 25 in queue.
- **Not committed.** `feeds.toml` + the 5 new `sources/` files are left uncommitted for the
  human (deposits are normally folded by the nightly `/sync` PR flow).

## 2026-06-30 — fix: recap preview won't scroll on Mac (issue #2)

- **Why.** GitHub issue #2: in the Brain Feed review-queue prototype
  (`bin/gui/review-queue/index.html`), the **Recap view** clipped long content on the Mac
  UI — tags, the "will touch X wiki pages" overlaps, and recap stats fell below the panel
  with no way to scroll to them. Reported during a Mac UI QA pass.
- **Root cause (WebKit-only).** The scroll container `.card-body`
  (`flex:1;overflow-y:auto;min-height:0`) sits under `.main` — a `flex-direction:column`
  item whose height comes from *stretching* inside the `flex-direction:row` `.body`. The
  Mac UI renders via WebKit (Safari/WKWebView), which treats a stretch-derived cross-axis
  height as *indefinite*, so `.card-body` grew to fit its content instead of capping, and
  `#win{overflow:hidden}` clipped the overflow → no scroll. Blink/Gecko treat it as
  definite, so it scrolled fine in Chrome — which is why a static CSS read and a Chrome
  render both looked correct, masking the bug.
- **Fix.** Added explicit `height:100%` to the two column-flex children of the row `.body`
  — `.main` (the recap panel; the reported bug) and `.sidebar` (same latent pattern,
  fixed for free). `.body`'s height is already definite (main-axis flex length of the
  fixed-720px `#win`), so `height:100%` resolves and gives WebKit the definite height it
  needs to cap `.card-body`/`.queue` and engage `overflow-y:auto`. No JS/markup changes.
- **Verified (Chrome, no regression).** Rendered via local `python3 -m http.server`,
  forced overflow: `#win` stays fixed at 720px, `.card-body` caps at 487px client height
  over 1253px of content, `scrollTop` reaches the 766px max → scrolls. The change is a
  no-op in Chrome (same value the stretch already produced). The decisive WebKit/Safari
  test on the Mac UI is the human's to eyeball on reload.

## 2026-06-30 — fix: review-queue sidebar won't scroll (issue #4)

- **Why.** GitHub issue #4: in the **native** Brain Feed review-queue app (the Tkinter
  desktop GUI, `bin/brain-feed-gui.py` — not the WebKit `index.html` prototype), the left
  **Review queue** sidebar that lists items awaiting triage didn't scroll. With more
  queued items than fit the sidebar height, the overflow was clipped and the bottom items
  couldn't be reached or selected. Reported during a Mac UI QA pass.
- **Root cause.** The sidebar queue is a hand-drawn `tk.Canvas` (`self.qcanvas`).
  `render_queue()` already set the canvas `scrollregion` to the full content height
  (`0,0,W,n*row_h`), but **nothing was bound to scroll it** — no mouse-wheel/trackpad
  handler and no scrollbar. The content extended past the viewport with no way to pan.
- **Fix.** Bound wheel events to `self.qcanvas`, mirroring the proven pattern already used
  by the right-pane `ScrollFrame`: `<MouseWheel>` → new `_q_wheel` (`yview_scroll` by
  `±1 units` on `e.delta` sign) plus `<Button-4>`/`<Button-5>` for X11-style wheels.
  Wheel-only, no visible scrollbar — consistent with `ScrollFrame`. No other changes
  needed: `scrollregion` is already maintained per render; drag-reorder already hit-tests
  via `qcanvas.canvasy(e.y)` so it stays correct while scrolled; header and Rescan footer
  are separate frames outside the canvas, so they stay pinned; Canvas `confine` (default
  `True`) re-clamps the view as the queue shrinks during triage.
- **Verified.** `python3 -m py_compile bin/brain-feed-gui.py` passes. The interactive
  trackpad/wheel + drag-while-scrolled test on the native app is the human's to run
  (`bin/brain-feed-gui.sh --demo`, overflow the queue, scroll the sidebar).

## 2026-06-30 — feature: Feed Stats + keep-rate (desktop triage app) [issue #6]

- **Why.** Issue #6's PRD asked for a *browser* review UI with a Feed Stats tab. On
  inspection the browser HTML (`bin/gui/review-queue/index.html`) is a non-functional
  mockup and the working triage surface is the Tkinter desktop app (`bin/brain-feed-gui.py`).
  The human chose **option B**: skip the browser UI, add the genuinely-missing half — per-feed
  **statistics + keep-rate** — to the desktop app. Mechanical only (files + sqlite, no LLM),
  consistent with ADR-0001.
- **Decision tracking (`bin/brain-feed.py`).** New `decisions` table in `.brain/feed-state.db`
  (`feed_id, item_id, action, timestamp`, PK `(item_id, timestamp)`), created idempotently in
  `db_connect()`. Added `log_decision` (INSERT OR IGNORE, returns ts), `delete_decision` (undo),
  `compute_keep_rate` (None below 10 decisions, else kept/(kept+dropped)), `_queued_counts`
  (scan `.brain/review/` by `via:`), and `feed_stats` (per-feed dict; sort rate-desc, N/A last,
  id-stable). CLI `review()` now logs every keep/drop via a `_safe_log` wrapper that never
  aborts triage; `status()` gained a keep-rate column.
- **No `brain_lib.py`.** The PRD's extract-to-shared-module step was for sharing with a web
  server that option B doesn't build; the existing `brain_feed` module already serves both the
  CLI and the GUI, so the helpers live there.
- **GUI (`bin/brain-feed-gui.py`).** Top-level "Review Queue ↔ Feed Stats" tab bar (`t` toggles),
  a read-only stats table (feed/adapter/trust/cap/seen/today/queued/keep-rate) with a
  "tracked going forward" note, drawn with the existing dark theme. New `self.screen` state
  (distinct from the per-item recap/outline `view`) so stats is viewable even with an empty
  queue; per-item actions (k/d/s/o/u + queue clicks) are guarded inert on the stats screen.
  `do_keep`/`do_drop` log decisions (feed=`via`, item=`path.stem`); `do_undo` deletes the row.
  Lazy cached db connection (`busy_timeout=3000`), committed/closed on window close; logging
  failures silently no-op so triage never crashes.
- **Tests (first suite).** `bin/tests/test_decisions.py` + `test_feed_stats.py` (stdlib
  `unittest`, temp vault per test, module loaded via importlib). 20 tests, all green:
  `python3 -m unittest discover -s bin/tests -t bin`.
- **Verified.** Unit suite green; `py_compile` clean; CLI `status` shows keep-rate; `review()`
  logs keep/drop and moves/deletes files (checked in an isolated temp vault, not the real
  `sources/`); GUI constructs headless, switches to the stats screen rendering all 5 feeds,
  guards hold, closes cleanly. `.brain/feed-state.db` stays gitignored.
- **Untouched.** No browser UI built; `feeds.toml`, `sources/`, the Tkinter triage flow and
  the existing review-queue mockup are unchanged.
