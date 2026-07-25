---
type: recap
title: "Recap — Vibe coding MenuGen"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-06-vibe-coding-menugen]
tags: [ai, vibe-coding, llm, karpathy, web-development]
---

# Recap — Vibe coding MenuGen

**[[entities/andrej-karpathy]]** wrote about building **[[entities/menugen]]** — an app
that takes a photo of a restaurant menu and generates an image for each dish — as his
first end-to-end **[[concepts/vibe-coding]]** project, built at a hackathon and then
deployed to a real, paid product (`menugen.app`) with authentication and payments
[2026-07-06-vibe-coding-menugen]. He describes himself as someone with "little to no
actual web development experience" who wrote none of the code directly: 100% was
written by **[[entities/cursor]]** paired with Claude (Claude 3.7 for the initial
prototype) [2026-07-06-vibe-coding-menugen].

The post is a step-by-step account of the pain points: getting the local React
prototype working was fast (he initially felt "80% done" but says it was closer to
20%), but integrating **[[entities/openai]]**'s API (OCR) and **[[entities/replicate]]**
(image generation) surfaced outdated LLM knowledge of current API conventions and
aggressive rate limiting; deploying to **[[entities/vercel]]** broke on lint errors
invisible locally, and he discovered `.env.local` secrets don't get pushed to git and
must be re-added manually in Vercel's dashboard — and that Vercel auto-deploys even
private repos to a public, guessable URL [2026-07-06-vibe-coding-menugen]. Adding
**[[entities/clerk]]** for auth required a purchased custom domain (Clerk's production
tier rejects `*.vercel.app`), a Google OAuth app, and manual back-and-forth across
Vercel/Clerk/Google settings; adding **[[entities/stripe]]** payments meant
copy-pasting JavaScript snippets into a TypeScript app and catching Claude at one point
proposing to match Stripe payments to users by email (unreliable, since checkout email
may not match the sign-in account) — Karpathy caught the bug and Claude fixed it by
passing user IDs through request metadata instead
[2026-07-06-vibe-coding-menugen]. He left adding a database/work queue (e.g.
**[[entities/supabase]]** Postgres + a queue like Upstash) as future work, noting Claude
pitched him on Vercel KV despite it being deprecated
[2026-07-06-vibe-coding-menugen].

Karpathy's takeaways: vibe coding a local demo is "exhilarating," but shipping a real,
production app is "a bit of a painful slog" because most of the effort is spent
navigating browser-based service configuration (accounts, API keys, dev/prod toggles)
that an LLM can't see or manipulate, not writing code
[2026-07-06-vibe-coding-menugen]. He suggests the industry needs either an opinionated
all-batteries-included app platform, or for existing dev services to become more
LLM-friendly (CLIs, curl-configurable backends, markdown docs) — and speculates that for
his next app he may use a simpler HTML/CSS/JS + Python (FastAPI/Fly.io) stack, or that
an app as simple as MenuGen might not need to be a full app at all (just an LLM call
plus a loop, possibly shippable as an "app store" prompt/artifact)
[2026-07-06-vibe-coding-menugen].

## Key claims

- MenuGen is Karpathy's first fully vibe-coded, deployed, paid product; he wrote no code
  directly, and it charges a 10% markup on generation costs
  [2026-07-06-vibe-coding-menugen].
- Claude (via Cursor) repeatedly hallucinated deprecated APIs/model names for OpenAI,
  Replicate, and Clerk, resolved only after the docs were pasted back into the chat
  [2026-07-06-vibe-coding-menugen].
- A Vercel deploy failure traced back to `.env.local` (correctly gitignored) not
  carrying API keys to the deployed environment, requiring manual entry in Vercel's
  dashboard [2026-07-06-vibe-coding-menugen].
- Vercel auto-deploys a private GitHub repo to a public, easily guessable URL by
  default [2026-07-06-vibe-coding-menugen].
- Claude initially proposed matching Stripe payments to user credits via email address,
  a bug Karpathy caught (checkout email can differ from the account email); Claude
  apologized and fixed it using user IDs in request metadata
  [2026-07-06-vibe-coding-menugen].
- Karpathy did not implement a database or job queue for MenuGen, calling that
  "future work" [2026-07-06-vibe-coding-menugen].
- His central critique: most of the effort in shipping a modern app is spent in browser
  tabs configuring third-party services — work an LLM cannot see or perform — not in
  the code editor [2026-07-06-vibe-coding-menugen].

## Entities mentioned

- [[entities/andrej-karpathy]], [[entities/menugen]], [[entities/cursor]],
  [[entities/openai]], [[entities/replicate]], [[entities/vercel]],
  [[entities/clerk]], [[entities/stripe]], [[entities/supabase]]

## Concepts mentioned

- [[concepts/vibe-coding]]

## Source

`sources/2026-07-06-vibe-coding-menugen.md`
