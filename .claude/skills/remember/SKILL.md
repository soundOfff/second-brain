---
name: remember
description: Distill the current conversation with Claude into a permanent source, then fold it into the wiki. Use when the user runs /remember, or asks to "remember this", "save this chat/conversation", "turn this into a source", or "add what we discussed to the brain". Writes a faithful note into sources/ (Layer 1, immutable) and then runs the capture ripple to update every affected wiki page.
---

# /remember — turn this conversation into a source

Read `CLAUDE.md` first if you have not this session. This skill is the bridge from a
**live conversation** into the immutable source layer and then on into the wiki. The
conversation is the raw material; the source file you write is the permanent record.

Budget ~5–15k tokens. The argument (optional) narrows what to keep, e.g.
`/remember the decision about launchd vs cron` — capture that thread, not the whole log.

## What counts as worth remembering

Distil the **substance**, not the chatter. Keep: decisions made and their rationale,
facts established, designs/architectures agreed, definitions, conclusions, open
questions, and concrete next steps. Drop: tool-call noise, false starts that were
superseded, pleasantries, and anything the user explicitly says to exclude. If almost
nothing durable was discussed, say so and ask whether to proceed before writing a file.

## Procedure

### 1. Distil the conversation into a clean note

Write a faithful, self-contained note a future reader (who never saw this chat) can
understand without context. Use your own clear prose — this is a distilled note, not a
verbatim transcript. Attribute opinions ("the user prefers…", "we decided…") and keep
claims checkable. Structure with short headings and lists where they help.

### 2. Store it as an immutable source

1. Derive the **source ID**: `YYYY-MM-DD-slug`, today's date + a kebab-case slug from
   the note's topic (e.g. `2026-06-23-launchd-vs-cron-decision`). Ensure uniqueness
   (append `-2`, `-3`).
2. Save the distilled note as `sources/<id>.md` with source frontmatter:

   ```yaml
   ---
   id: <id>                         # equals the filename stem
   title: <human-readable topic>
   type: note
   author: conversation with Claude
   captured: <today>
   ---
   ```

   Use `type: note`. (Reserve `type: transcript` for cases where the user explicitly
   asks to keep the raw back-and-forth verbatim rather than a distillation.)
3. **Never overwrite an existing source.** If the ID collides, bump the slug. Sources
   are immutable (see `CLAUDE.md` — Layer 1).

### 3. Run the capture ripple

The new source is now exactly like any other captured source — fold it into the wiki by
following the **`/capture` procedure from step 2 onward**:

- Write the recap at `wiki/recaps/<id>.md`.
- Follow the ripple: create/update every entity and concept page the note meaningfully
  touches, adding the source ID to `sources:`, inline citations `[<id>]`, wikilinks, and
  bumped `updated:` dates. Record any conflicts under `## Open questions / contradictions`.
- Update `index.md` (new pages + "Recently updated").

Do not duplicate that logic here — `/capture` owns it. This skill's only extra job is
manufacturing the source from the conversation; after that the pipeline is identical.

### 4. Log it

Append a `log.md` entry: `/remember`, the source ID created, the recap, wiki pages
created vs. updated, index change, and any contradictions or follow-ups.

## Report back

Tell the user: the source ID written (and its path), the recap, a short list of wiki
pages created vs. updated, and anything needing their attention. Note that the raw
conversation itself is ephemeral — only what you distilled into the source survives.
