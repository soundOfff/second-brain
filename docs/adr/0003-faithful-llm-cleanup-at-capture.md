# A faithful, opt-out `claude -p` cleanup pass at capture time

`brain-clip.sh` (external tool #1) originally did a purely deterministic extraction:
`curl` + a stdlib `HTMLParser` for web pages, `yt-dlp` + a WebVTT flattener for videos.
That kept the front door cheap and key-free, but the raw output was often poor:

- **Web pages** dragged in nav, social/share buttons, cookie banners, "Related posts",
  "Previous/Next", "posted in" footers, and duplicate lines. Headings arrived wrapped in
  stray `**` emphasis from the parser.
- **JS-rendered pages** (notably YouTube watch URLs when `yt-dlp` was absent) fell back to
  scraping the player-page HTML and captured only the site chrome — e.g. a YouTube
  transcript source whose entire body was `Acerca de Prensa … © 2026 Google LLC`.
- **Auto-caption transcripts** arrived as lowercase, unpunctuated, one-cue-per-line
  run-ons full of the phrase repetition auto-captioners produce.

## Decision

After the deterministic extraction, `brain-clip.sh` runs **one optional `claude -p`
pass** that *cleans and re-structures the extracted body only*:

- articles → strip non-content chrome, drop duplicate blocks, restore Markdown structure;
- transcripts → punctuate, capitalize, paragraph, and de-duplicate the caption text.

The prompt is explicitly **faithful, not generative**: preserve all substantive content
verbatim, do not summarize, translate, shorten, or invent. Summarization/synthesis remains
`/sync`'s job — this pass never crosses that line.

## Why this doesn't break the deterministic front door

- **Opt-out and graceful.** Controlled by `--llm` / `--no-llm`, or `BRAIN_CLIP_LLM=auto|1|0`
  (default `auto` = on iff `claude` is on `PATH`). Any failure — no CLI, timeout, empty
  output — falls back to the raw deterministic extraction. With it off, behaviour is
  byte-for-byte the classic path. No new **API key**: it reuses the same authenticated
  `claude` CLI the nightly `/sync` already uses (ADR-0001).
- **It's extraction, not synthesis.** ADR-0001 keeps *judgment* (synthesis, contradiction
  hunting, stubs) in Claude at `/sync` and *mechanical* schema work in `brain_tidy.py`.
  This pass is cleanup of a single source's own text — it adds no cross-source judgment,
  writes no wiki page, and still never mutates `sources/` beyond the one file it is
  depositing.
- **Isolation.** The `claude -p` call runs from a neutral cwd so it does not load this
  repo's wiki-owner `CLAUDE.md`/skills or attempt tool use — it is a pure text transform.
- **Model.** `BRAIN_CLIP_MODEL`, else `.brain/config.json` `"model"`, else `sonnet` — the
  same knob the Settings screen already exposes for the unattended agents.

## Consequences

- `yt-dlp` becomes the real path for video captures (it must be installed for transcripts;
  without it, video URLs still degrade to page extraction as before).
- The feeder (`brain-feed.py`) inherits the cleanup because it renders via
  `brain-clip.sh --dry-run`; its per-item subprocess timeout was raised 90s → 300s to give
  the pass room. Feeds remain daily-capped, so cost stays bounded; set `BRAIN_CLIP_LLM=0`
  in the cron environment to opt the unattended pull back out.
- Tests that stub the render path stay mechanical and LLM-free — the pass is external to
  the deposit/place logic they exercise.
