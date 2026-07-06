"""Wiki routes — nav tree + page bodies + source viewer.

Returns raw markdown; the React app is in charge of parsing wikilinks and
citations into anchor tags. Backlinks and source-cite adjacency are computed
here, since they need the whole page set.
"""
from __future__ import annotations

import brain_feed
import brain_wiki_data
from fastapi import APIRouter, HTTPException


router = APIRouter()


def _title_of(pages: dict, slug: str) -> str:
    return pages.get(slug, {}).get("meta", {}).get("title", slug)


@router.get("/pages")
def pages_index():
    """Nav sidebar payload — one entry per page, grouped by top-level folder."""
    pages = brain_wiki_data.load_pages(brain_feed.VAULT)
    entries = []
    for slug, pg in pages.items():
        if slug == "index":
            group = "_"
        else:
            group = slug.split("/")[0] if "/" in slug else "_"
        entries.append({
            "slug": slug,
            "title": pg["meta"].get("title", slug),
            "status": pg["meta"].get("status"),
            "group": group,
        })
    entries.sort(key=lambda e: (e["group"], e["title"].lower()))
    return {"entries": entries}


@router.get("/page/{slug:path}")
def get_page(slug: str):
    """Single page: metadata, raw body markdown, backlinks, source references."""
    pages = brain_wiki_data.load_pages(brain_feed.VAULT)
    srcids = brain_wiki_data.source_ids(brain_feed.VAULT)
    slug = slug.strip("/") or "index"
    if slug not in pages:
        # 404 with a hint — the React app renders a "missing page" state instead.
        raise HTTPException(status_code=404, detail=f"page {slug!r} not found")
    pg = pages[slug]
    bl = brain_wiki_data.backlinks(pages).get(slug, [])
    sources = []
    for sid in pg["meta"].get("sources", []):
        sources.append({"id": sid, "exists": sid in srcids})
    return {
        "slug": slug,
        "meta": pg["meta"],
        "body": pg["body"],
        "backlinks": [{"slug": s, "title": _title_of(pages, s)} for s in bl],
        "sources": sources,
        "exists": True,
    }
