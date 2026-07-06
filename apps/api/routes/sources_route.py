"""Source deposit + raw source viewer routes."""
from __future__ import annotations

import brain_feed
import brain_feed_items as items_mod
import brain_wiki_data
from fastapi import APIRouter, HTTPException


router = APIRouter()


@router.post("/webpage")
def create_webpage(payload: dict):
    """Deposit one source straight into sources/ — the New Source (webpage) form.

    `body` present → note; otherwise fetch the URL. Matches the Tk GUI's flow in
    bin/brain-feed-gui.py :: _submit_new_webpage."""
    title = (payload.get("title") or "").strip() or None
    url = (payload.get("url") or "").strip()
    body = (payload.get("body") or "").strip()
    tags = payload.get("tags") or []
    if not url and not body:
        raise HTTPException(status_code=400, detail="url or body required")
    if body:
        item = {"source_kind": "text", "type": "note", "title": title,
                "url": url or None, "body": body}
    else:
        item = {"source_kind": "url", "url": url, "title": title}
    try:
        proposed, content, stderr = brain_feed.render_via_clip(item)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"clip failed: {e}")
    if not content:
        msg = ((stderr or "").strip().splitlines()[-1:] or ["render failed"])[0]
        raise HTTPException(status_code=502, detail=msg)
    content = items_mod.inject_tags(content, tags)
    dest = brain_feed.place(content, proposed, brain_feed.SOURCES, brain_feed.VAULT)
    return {"placed": str(dest.relative_to(brain_feed.VAULT))}


@router.get("/{sid}")
def get_source(sid: str):
    """Raw source viewer — text of the immutable source and which wiki pages
    cite it (backlinks-for-sources)."""
    path = brain_wiki_data.find_source_file(brain_feed.VAULT, sid)
    if path is None:
        raise HTTPException(status_code=404, detail="source not found")
    raw = path.read_text(encoding="utf-8", errors="replace")
    pages = brain_wiki_data.load_pages(brain_feed.VAULT)
    citers = brain_wiki_data.source_citers(pages)
    citing = sorted(citers.get(sid, set()))
    return {
        "id": sid,
        "filename": path.name,
        "raw": raw,
        "citers": [
            {"slug": s, "title": pages.get(s, {}).get("meta", {}).get("title", s)}
            for s in citing
        ],
    }
