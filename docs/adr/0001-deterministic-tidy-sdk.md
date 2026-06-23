# Deterministic `tidy` SDK; `sync` stays Claude-side

We split the brain's maintenance along the judgment/mechanical line (see CONTEXT.md):
the **mechanical** subset — validate the schema and apply the few provably-safe fixes —
becomes a stdlib-only, importable Python SDK (`bin/brain_tidy.py`) that runs with **no
LLM, no API key, no network**. The **judgment** subset (synthesis, contradictions,
starved stubs) — i.e. `sync`, `lint`, `digest` — stays in Claude, invoked via the
already-authenticated `claude -p` CLI.

## Why this boundary

- **The Claude Agent SDK was the obvious "run it outside the session" answer, and we
  rejected it.** It requires a per-token `ANTHROPIC_API_KEY` from the Console and
  *cannot* reuse the Claude Code subscription/OAuth login (Anthropic explicitly forbids
  reusing claude.ai login for SDK-built tools). The user has the subscription, not an
  API plan. So a "real SDK" for the synthesis half was not available to us.
- **`sync` is synthesis — it cannot exist without an LLM.** The most we could do for it
  is wrap `claude -p`, which `brain-sync.sh` already does. So there is nothing to gain by
  pulling `sync` into the SDK, and doing so would muddy the one clean property the SDK
  has: it never needs Claude. The SDK is therefore **deterministic-only, on purpose.**
- **Backlog detection is the one deterministic sliver of sync** ("which sources lack a
  recap?" is pure file-existence), so it lives in the SDK as `backlog()`. The nightly
  cron runs `tidy --fix`, then calls `claude -p /sync` **only if `backlog()` is
  non-empty** — mechanical cleanup is free, tokens are spent only on real work.

## Consequences

- `bin/brain_tidy.py` is the single source of truth for the deterministic schema checks.
  `bin/brain-validate.sh` is now a thin shim that delegates to it (keeping the
  pre-commit hook and `--install-hook` working) — there is no second validator to drift.
- The pre-commit hook is **check-only**; it never auto-fixes/re-stages (a commit hook
  silently rewriting files is surprising). `--fix` is an explicit act (cron + on demand).
- Fixes are intentionally narrow — only `clamp updated<created`, case-only wikilink
  repair, and frontmatter list-spacing. Anything requiring interpretation is reported,
  never auto-fixed, because the wiki is Claude-owned and an over-eager fixer silently
  degrades a trusted artifact. tidy never writes to `sources/` (immutable).
