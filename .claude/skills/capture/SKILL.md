---
name: capture
description: Ingest one source into the second brain. Use when the user runs /capture with a URL, a file path, or pasted text, or asks to "capture", "clip", "save this source", or "add this to the brain". Stores the raw source immutably in sources/, writes or refreshes its recap, and updates every affected wiki page.
---

# /capture — ingest one source

Read `CLAUDE.md` first if you have not this session. Process exactly **one** source per
run. Budget ~5–15k tokens.

## Input

The argument is one of:
- a **URL** → fetch and clip it,
- a **file path** (PDF, image, text, data) → copy it into `sources/`,
- **pasted text** → save it as a note.

If no argument is given, ask the user for the source.

## Procedure

### 1. Acquire & store the raw source (immutable)

1. Derive the **source ID**: `YYYY-MM-DD-slug` where the date is today and the slug is a
   kebab-case from the title. Ensure uniqueness (append `-2`, `-3` if needed).
2. For a **URL**: fetch it (WebFetch). Save the cleaned article text as
   `sources/<id>.md` with the required source frontmatter (id, title, type: article,
   url, author if known, captured: today). Preserve the content faithfully — this is the
   immutable record, not a summary.
3. For a **file**: copy it unchanged into `sources/<id>.<ext>`. If binary (PDF/image),
   also write `sources/<id>.meta.md` with the source frontmatter. If text, prepend
   frontmatter only if it's a markdown/text file you can safely annotate; otherwise use
   a sidecar.
4. For **pasted text**: save as `sources/<id>.md` with `type: note` frontmatter.
5. **Never overwrite an existing source file.** If the ID exists, it's already captured.

### 2. Write the recap (`wiki/recaps/<id>.md`)

A faithful, structured summary of this one source:
- frontmatter: `type: recap`, title, created/updated today, `status`, `sources: [<id>]`,
  tags.
- A short summary (3–8 sentences).
- `## Key claims` — bulleted, each citing `[<id>]`, noting if it's the source's opinion.
- `## Entities mentioned` and `## Concepts mentioned` — as wikilinks to the pages you
  will touch in step 3.
- `## Source` — link/reference back to `sources/<id>`.

### 3. Follow the ripple — update affected wiki pages

For **each entity and concept** the source meaningfully discusses:
1. If a page exists (`wiki/entities/<slug>.md` or `wiki/concepts/<slug>.md`), **update**
   it: integrate the new information, add the source ID to `sources:`, add inline
   citations, bump `updated:`, add wikilinks to newly related pages, and raise `status`
   if it has matured.
2. If no page exists and the entity/concept is substantive, **create** a stub or full
   page following the page conventions in `CLAUDE.md`. Link it back to related pages.
3. Record any conflict with existing content under `## Open questions / contradictions`
   on the page (cite both sources) — do not silently overwrite.

A single capture commonly touches 5–15 pages. Follow the links; don't stop at one.

### 4. Update `index.md`

Add new entities/concepts to the relevant lists and refresh "Recently updated".

### 5. Log it

Append an entry to `log.md` per the format there: command, source ID, recap, pages
created/updated, index change, and any contradictions or follow-ups noted.

## Report back

Tell the user: the source ID stored, the recap written, and a short list of the wiki
pages created vs. updated, plus anything that needs their attention (contradictions,
gaps).
