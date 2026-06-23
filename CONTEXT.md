# Second Brain

An LLM-maintained wiki. Humans add raw sources; Claude owns and maintains the synthesized
`wiki/`. This glossary fixes the language used to describe the brain's *operations* and the
boundary between what needs an LLM and what does not.

## Language

**Tidy**:
The deterministic, no-LLM maintenance pass: validate every page against the schema and
apply the *safe, unambiguous* auto-fixes (repair frontmatter, correct `updated:` dates,
fix obvious link typos to existing pages). Rule-based only — never makes judgment calls.
The Claude-free subset of what `/lint` does today.
_Avoid_: lint (lint is the judgment-requiring superset), clean, fixup, validate (validate
is only the read-only half of tidy).

**Sync**:
The synthesis pass: read unprocessed sources and write/update the wiki pages they ripple
into. Requires an LLM by definition — it is the brain's thinking. Cannot run "outside of
Claude" in any meaningful sense.
_Avoid_: reconcile, process, ingest, capture (capture is the single-source variant).

**Judgment vs. mechanical**:
The cleave line between [[Sync]] and [[Tidy]]. *Mechanical* = expressible as a rule a
program can check/apply with no model (frontmatter shape, slug format, citation syntax,
dangling links, stale dates). *Judgment* = requires reading meaning (contradictions,
whether a claim is supported, whether a stub is source-starved, synthesis). Tidy owns the
mechanical; Claude (sync/lint) owns the judgment.

**Backlog**:
The set of sources with no recap yet — `sources/<id>` exists but `wiki/recaps/<id>.md`
does not. Pure file-existence check, no LLM, so it belongs to [[Tidy]] even though acting
on it (writing the recaps) is [[Sync]]. Lets cron skip invoking Claude when there is
nothing to synthesize.
_Avoid_: unprocessed, queue, pending.

**Outside of Claude**:
Runnable without an Anthropic API key and without an interactive Claude Code session.
NOTE: the Agent SDK does **not** qualify — it requires a per-token `ANTHROPIC_API_KEY` and
cannot reuse the CLI subscription. So only two things are "outside of Claude": fully
deterministic code (true, for [[Tidy]]), or a subprocess wrapper around the already-
authenticated `claude -p` CLI (partial, for [[Sync]] — still depends on the binary + sub).
_Avoid_: headless, standalone, SDK (ambiguous — the Agent SDK specifically does not fit).
