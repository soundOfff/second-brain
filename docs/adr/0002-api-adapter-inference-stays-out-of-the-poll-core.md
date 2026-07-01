# Generic `api` adapter; config-time inference stays out of the poll core

The pull feeder (`bin/brain-feed.py`) grows a fifth adapter, `api`, that reads any
public JSON HTTP endpoint into normalized items via a **declarative mapping** in
`feeds.toml` (see CONTEXT.md → *Mapping*). Crucially, the AI that *authors* a mapping
from a sample response lives **entirely outside `brain-feed.py`** — in an interactive
Claude-session skill — and never in the daily poll path.

## The decision

- **Generality comes from static config, not runtime code.** One `adapter = "api"` +ó a
  a small mapping block (`items_path`, `url_field`, `title_field`, `guid_field`,
  `body_field`, `mode`) covers many APIs. Adding a source is a `feeds.toml` edit, exactly
  like adding an `rss` blog — not new Python.
- **The mapping path language is deliberately minimal** — dotted keys resolving to a JSON
  array (`items_path`; empty string = the response *is* the array) and dotted paths for
  each field. No wildcards, filters, or jq. This keeps the adapter **pure-stdlib**, so
  unlike `yt`/`email` it never has to disable itself for a missing dependency. An API too
  irregular for dotted-path mapping is the signal to write a *named* bespoke adapter, not
  to grow a query language in TOML.
- **AI is config-time only, and physically separate.** A skill/session workflow fetches a
  sample, infers the `[[feed]]` block, validates it with `brain-feed run --dry-run --feed
  <id>`, and appends reviewed config. `brain-feed.py` never imports or shells to a model.

## Why this boundary

- **The poll loop must stay [[Outside of Claude]].** The feeder runs unattended at 01:30
  via plain-python launchd with **no `claude` binary and no `ANTHROPIC_API_KEY`**. A
  model call in an adapter — even to shape JSON — would break that invariant and move the
  documented Sync/Tidy cleave line (CONTEXT.md). Inference-as-a-skill keeps the wall hard:
  mechanical core here, judgment (including "how do I read this API?") in Claude.
- **A `brain-feed infer` subcommand was the obvious convenience, and we rejected it.** One
  binary is tidier, but it drags a model dependency *into the feed tool* and muddies "the
  feeder never invokes an LLM" even if it's a different subcommand than `run`. The skill
  keeps `brain-feed.py` provably model-free.
- **Inference is self-checking.** The skill doesn't guess blindly: it proposes a mapping,
  dry-runs it, and iterates until real items come out — then a human reviews the config
  before it's committed.

## Scope (v1)

- **Public APIs only.** No auth is built; the mapping reserves room for a later `auth`
  field (`none`/`bearer`/`header`/`query`) whose secret would come from the Keychain,
  reusing the `email` adapter's `keychain_password()` pattern — deferred, not designed in.
- **GET, JSON, single response, no pagination.** Daily poll + `guid` dedup + per-feed cap
  already give continuous coverage without walking pages. Optional per-feed `user_agent`
  override (not a secret) avoids the common 429/UA-block failure (e.g. Reddit).
- **Per-feed `mode`** (`url` default → brain-clip fetches the link, like `rss`; `text` →
  deposit `body_field`, like `email`). `url_field` is read in *both* modes for provenance
  and cross-source dedup.

## Consequences

- The `api` adapter is a thin function like the others, registered in `ADAPTERS`; the
  deterministic core (dedup → cap → trust-route → deposit) is unchanged.
- Tests follow ADR-0001 (mechanical, no LLM): unit tests for the dotted-path resolver +
  normalization, plus one local-HTTP-server e2e across three response shapes (nested
  envelope, flat array, top-level array), both modes, the guid fallback chain, and
  missing-field → `None`.
- `keychain_password()` is worth factoring into a shared helper when `auth` lands, so
  `email` and `api` share one secrets mechanism.
