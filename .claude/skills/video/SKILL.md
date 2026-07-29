---
name: video
description: Break down an entire video (YouTube/Vimeo) into a timestamped analysis. Use when the user runs /video with a video URL, or asks to "analyze this video", "break down this video", "desglosar/desglose un video", "what does this video cover", or pastes a YouTube link expecting more than a summary. Deposits the timestamped transcript as an immutable source, then writes a section-by-section breakdown with deep links, key claims, and quotes, and ripples into the wiki.
---

# /video — break down an entire video

Read `CLAUDE.md` first if you have not this session. Process exactly **one** video per
run.

This is `/capture`'s deeper sibling. `/capture` on a video URL gives you a flat
transcript and a summary recap. `/video` keeps the **clock**: every claim, quote and
section is pinned to the second it happens and deep-linked back to the video, so the
reader can jump straight to any moment and verify it.

Use `/capture` when the video is one source among many. Use `/video` when the video *is*
the artifact worth studying.

## Input

A YouTube or Vimeo URL. If none is given, ask for one.

## Procedure

### 1. Extract the timestamped transcript

```
python3 bin/brain_video.py "<url>" --json --out /tmp/<slug>.json
```

Useful flags:
- `--block-seconds N` — transcript granularity. Default 45s reads like paragraphs. Use
  90–120 for a long talk, 20–30 for a dense, fast-moving video.
- `--markdown` — the same thing rendered as a transcript document (what step 2 deposits).

Read the JSON. It gives you `title`, `uploader`, `duration_hms`, `upload_date`,
`chapters` (the uploader's own, when they defined any), and `segments` — each with
`timestamp`, a `link` that opens the video at that second, and `text`.

**If `has_transcript` is false**, the video has no captions. Say so plainly and stop —
do not invent content from the title and description. Offer the metadata-only page
instead if the user wants it.

**If the video is long** (say over ~45 minutes of transcript), do not try to hold every
segment at once. Re-extract with a larger `--block-seconds`, work through the segments in
order in a few passes, drafting the section breakdown incrementally, then synthesize the
top-level sections once at the end. Never skip the tail of a video — a breakdown that
quietly stops at the halfway mark is worse than no breakdown.

### 2. Deposit the raw source (immutable)

1. Derive the **source ID**: `YYYY-MM-DD-slug`, today's date + a kebab-case slug of the
   video title. Ensure uniqueness (`-2`, `-3`).
2. Write `sources/<id>.md` — the timestamped transcript from `--markdown`, with source
   frontmatter: `id`, `title`, `type: transcript`, `url`, `author` (the channel),
   `captured` (today).
3. **Never overwrite an existing source.** If the ID exists, it is already captured —
   reuse it and go straight to step 3.

The timestamped transcript *is* the raw record here: it is strictly more faithful than
the flattened prose, because it preserves when each thing was said. Do not edit, tidy or
summarize it on the way in.

### 3. Write the breakdown (`wiki/recaps/<id>.md`)

Frontmatter: `type: recap`, title, created/updated today, `status`, `sources: [<id>]`,
tags. Then:

```markdown
# Breakdown — <video title>

> **<Channel>** · <duration> · published <YYYY-MM-DD> · [Watch](<url>)

**In one line:** <the whole video in a single sentence>

## What this video is

2–4 sentences: what it covers, who it is for, what form it takes (talk, interview,
tutorial, demo).

## Structure at a glance

| Time | Section | What happens |
|---|---|---|
| [0:00](link) | Framing the problem | … |

The skeleton of the video — enough that a reader knows whether to watch and where to
start. If the uploader defined chapters, use them as the spine; your own sections may
refine them but should not silently contradict them.

## Section by section

### [0:00](link) — <section title>

What is actually said, faithfully and in order. Attribute opinions to the speaker. Cite
`[<id>]` on non-obvious factual claims. Keep the reader's ability to verify: when a claim
matters, pin it to its own timestamp inline.

(one `###` per section, covering the video end to end)

## Key claims

- Each claim, with its `[m:ss](link)` and a `[<id>]` citation. Mark clearly whether it is
  the speaker's opinion, a cited result, or an established fact.

## Notable quotes

> "Exact words." — [<m:ss>](link)

Verbatim only. If the captions are garbled at that moment, do not clean the quote into
something the speaker did not say — pick a different one.

## Entities mentioned
## Concepts mentioned

Wikilinks to the pages you touch in step 4.

## Open questions / contradictions

Anything the video leaves hanging, or that conflicts with what the wiki already holds
(cite both sides).

## Source

`sources/<id>` — <url>
```

Faithfulness rules, in order of importance:
1. **Never invent.** If the captions are unclear, say they are unclear.
2. **Auto-captions mishear things** — names, jargon and numbers especially. Correct one
   only when context makes the intended word unmistakable, and never flip a negation or a
   figure on a guess. Where a number or name matters and the caption looks wrong, flag it
   rather than quietly "fixing" it.
3. **Separate what the speaker claims from what is established.** Attribute throughout.

### 4. Follow the ripple

For each entity and concept the video meaningfully discusses, update the existing
`wiki/entities/<slug>.md` / `wiki/concepts/<slug>.md` (integrate, add the source ID to
`sources:`, add inline citations, bump `updated:`, raise `status` if matured) or create a
page if it is substantive and missing. Record conflicts under
`## Open questions / contradictions` citing both sources — never silently overwrite.

A meaty talk commonly touches 5–15 pages.

### 5. Update `index.md` and log it

Add new pages to the relevant lists, refresh "Recently updated", and append an entry to
`log.md` per the format there: command, source ID, breakdown written, pages created vs.
updated, and any contradictions or follow-ups.

## Report back

The source ID stored, the breakdown written, how much of the video it covers (duration
and section count), the wiki pages created vs. updated, and anything needing attention —
especially any place the captions were too unreliable to trust.
