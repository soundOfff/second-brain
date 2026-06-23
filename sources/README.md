# sources/ — Layer 1 (raw, immutable)

Raw inputs live here, untouched. **Do not edit files in this folder** — they are the
audit trail. The agent reads them and synthesizes into `wiki/`.

## Conventions

- **Filename = source ID:** `YYYY-MM-DD-slug.<ext>`
  (e.g. `2026-06-23-karpathy-llm-wiki.md`).
- **Markdown captures** carry frontmatter:

  ```yaml
  ---
  id: 2026-06-23-some-slug
  title: Original Title
  type: article | pdf | transcript | screenshot | note | data
  url: https://...
  author: ...
  captured: YYYY-MM-DD
  ---
  ```

- **Binary files** (PDF, images, data) are stored as-is alongside a sidecar
  `<stem>.meta.md` containing the same frontmatter.

Sources are added by `/capture` (one at a time) or dropped in manually and reconciled
with `/sync`. This `README.md` is not a source and is ignored by the skills.
