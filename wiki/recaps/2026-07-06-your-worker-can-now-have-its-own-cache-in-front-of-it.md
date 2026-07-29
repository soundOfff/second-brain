---
type: recap
title: "Recap — Your Worker can now have its own cache in front of it"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it]
tags: [cloudflare, workers, caching, edge-computing, developer-tools]
---

# Recap — Your Worker can now have its own cache in front of it

**[[entities/cloudflare]]** announced **Workers Cache**, a tiered cache that sits in
front of a **[[entities/cloudflare-workers]]** deployment, configured with one Wrangler
config block and standard HTTP `Cache-Control`/`Cache-Tag` headers
[2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it]. The post frames this
as a architectural inversion: Workers originally ran *in front of* an origin and its
cache, but frameworks like Astro, TanStack Start, Next.js, Remix, and SvelteKit now ship
the Worker *as* the origin, leaving nothing to cache under the old model
[2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it]. Workers Cache flips
this so a cache hit means the Worker doesn't run at all and no CPU time is billed
[2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].

Key mechanics described: full **[[concepts/stale-while-revalidate]]** support (serves a
stale response instantly while refreshing in the background, `Cf-Cache-Status:
UPDATING`); `Vary` header support for multiple representations of one URL (per RFC
9110/9111); a two-tier **[[concepts/tiered-caching]]** topology (per-datacenter lower
tier + network-wide upper tier) enabled automatically with no configuration; and
multi-tenant-safe cache keys via `ctx.props`, letting authenticated, per-user API
responses be cached safely
[2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it]. Unlike Cloudflare's
existing zone-level cache (Cache Rules, Page Rules, Tiered Cache), Workers Cache belongs
to the Worker itself, follows it across custom domains, `workers.dev`, previews, and
Workers for Platforms tenants, and purges are scoped to the Worker's entrypoint
[2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].

The feature the post calls "the biggest unlock" is that the cache sits in front of
*every* Worker entrypoint, including calls between entrypoints in the same Worker via
`ctx.exports` — letting a single Worker be authored as a chain of small
entrypoints (auth, normalization, routing, expensive reads) with cache stages
composed in via ordinary code, opting each entrypoint in or out of caching individually
[2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it]. This also lets an
app run one Worker near the user (auth, routing) and a second Worker near the data
(via Smart Placement), with the cache as the seam that avoids a data-center hop on
repeat requests [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it]. The
**[[entities/astro]]** Cloudflare adapter ships built-in integration via a
`cacheCloudflare` provider; TanStack Start and Next.js (via Vinext) integrations are
planned [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].

Billing: cache hits bill the standard request rate but zero CPU time; misses and
bypasses bill normally. Static-asset requests and worker-to-worker invocations, normally
free, become billed at the standard request rate once caching is enabled, since they now
consult the cache [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].
Planned follow-ups: coordinating the upper-tier cache location with Smart Placement to
avoid a double network hop on a full miss, raising the launch-time 512MB cacheable
response size limit to standard per-plan limits, and a `ctx.cache.invalidate()` API to
mark responses stale (vs. hard-purging)
[2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].

## Key claims

- Workers Cache is available today to every Worker on any plan, enabled via a single
  `"cache": { "enabled": true }` line in Wrangler config
  [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].
- On a cache hit, the Worker does not run and no CPU time is billed; only the standard
  request charge applies [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].
- The cache is tiered (lower per-datacenter tier + upper network-wide tier)
  automatically, with no separate "enable tiered cache" step
  [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].
- `ctx.props` (e.g. a user ID passed on a service-binding call) becomes part of the
  cache key, enabling safe per-user caching of authenticated API responses
  [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].
- The cache sits in front of every Worker entrypoint, including `ctx.exports` calls
  between entrypoints in the same Worker, letting developers compose cache stages
  into a single-file app architecture
  [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].
- Astro's Cloudflare adapter has built-in Workers Cache integration via
  `cacheCloudflare`; TanStack Start and Next.js integrations are planned
  [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].
- At launch, all responses are capped at the Free plan's 512MB cacheable size limit
  regardless of account plan, described as temporary
  [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].
- Enabling caching causes previously-free static asset requests and worker-to-worker
  invocations to bill at the standard request rate
  [2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it].

## Entities mentioned

- [[entities/cloudflare]], [[entities/cloudflare-workers]], [[entities/astro]],
  [[entities/wrangler]]

## Concepts mentioned

- [[concepts/workers-cache]], [[concepts/stale-while-revalidate]],
  [[concepts/tiered-caching]], [[concepts/edge-computing]]

## Source

`sources/2026-07-06-your-worker-can-now-have-its-own-cache-in-front-of-it.md`
