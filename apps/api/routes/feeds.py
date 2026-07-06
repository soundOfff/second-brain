"""Feed routes — stats table, feeder run trigger + polling, and subscription."""
from __future__ import annotations

import re
import secrets
import subprocess
import sys
import threading
from pathlib import Path

import brain_feed
import brain_feed_items as items_mod
from fastapi import APIRouter, HTTPException


router = APIRouter()

_FEED_PY = Path(__file__).resolve().parent.parent.parent.parent / "bin" / "brain-feed.py"


@router.get("/stats")
def stats():
    """Per-feed table for the Feed Stats screen."""
    try:
        con = brain_feed.db_connect(brain_feed.DB_PATH)
    except Exception:
        con = None
    try:
        cfg = brain_feed.load_config(brain_feed.CONFIG)
    except Exception:
        cfg = {"feeds": []}
    rows = brain_feed.feed_stats(con, cfg) if con else []
    if con is not None:
        try:
            con.close()
        except Exception:
            pass
    return {"rows": rows}


# ---------------------------------------------------------------------------
# `brain-feed run` — the same daily pull the 01:30 launchd agent does. Long-
# running (network fetches), so we spawn it and let the client poll for a
# summary. Mirrors the Tk GUI's background-thread pattern.
# ---------------------------------------------------------------------------
_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()


def _parse_summary(out: str) -> str:
    """Same "done: X deposited, Y queued" extractor the Tk GUI uses."""
    lines = [l for l in out.splitlines() if l.strip()]
    line = next((l for l in reversed(lines) if "done:" in l),
                lines[-1] if lines else "done")
    return re.sub(r"^\[[^\]]*\]\s*", "", line)


def _run_worker(job_id: str) -> None:
    try:
        proc = subprocess.run(
            [sys.executable, str(_FEED_PY), "run"],
            capture_output=True, text=True, timeout=900,
        )
    except Exception as e:
        with _jobs_lock:
            _jobs[job_id] = {"status": "error", "error": str(e)[:220]}
        return
    if proc.returncode != 0:
        tail = ((proc.stderr or proc.stdout or "").strip().splitlines()[-1:]
                or ["run failed"])[0]
        with _jobs_lock:
            _jobs[job_id] = {"status": "error", "error": tail}
        return
    with _jobs_lock:
        _jobs[job_id] = {"status": "done", "summary": _parse_summary(proc.stdout or "")}


@router.post("/run")
def run_feeder():
    job_id = secrets.token_urlsafe(8)
    with _jobs_lock:
        _jobs[job_id] = {"status": "running"}
    threading.Thread(target=_run_worker, args=(job_id,), daemon=True).start()
    return {"jobId": job_id, "status": "running"}


@router.get("/run/{job_id}")
def run_status(job_id: str):
    with _jobs_lock:
        entry = _jobs.get(job_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="unknown jobId")
    return {"jobId": job_id, **entry}


# ---------------------------------------------------------------------------
# Subscribe (rss | yt | api) — appends a [[feed]] block to feeds.toml.
# ---------------------------------------------------------------------------
def _default_cap() -> int:
    try:
        cfg = brain_feed.load_config(brain_feed.CONFIG)
    except Exception:
        cfg = {}
    return int(cfg.get("default_cap", 5))


@router.post("/subscribe")
def subscribe(payload: dict):
    kind = payload.get("kind")
    if kind not in ("rss", "yt", "api"):
        raise HTTPException(status_code=400, detail="kind must be rss | yt | api")
    url = (payload.get("url") or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    if kind == "yt":
        url = items_mod.youtube_feed_url(url)
    title = (payload.get("title") or "").strip() or None
    tags = payload.get("tags") or []
    fid = (payload.get("id") or "").strip()
    cap = payload.get("cap")
    trust = payload.get("trust", "queue")

    # Fallback feed id: title-derived → URL-host slug (for yt: channel_id).
    import urllib.parse
    if not fid and title:
        fid = brain_feed.slugify(title)
    if not fid:
        host = urllib.parse.urlsplit(url).netloc.removeprefix("www.")
        fid = brain_feed.slugify(host)
        if kind == "yt":
            q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
            ident = (q.get("channel_id") or q.get("playlist_id") or [""])[0]
            fid = ("yt-" + brain_feed.slugify(ident)) if ident else fid
    if not fid:
        raise HTTPException(status_code=400, detail="unable to derive feed id — supply id or title")

    feed = {"id": fid, "adapter": kind, "url": url, "trust": trust,
            "n": cap, "tags": tags, "title": title}
    if kind == "api":
        mode = payload.get("mode", "url")
        mapping = {k: payload.get(k, "") for k in
                   ("items_path", "url_field", "title_field", "guid_field",
                    "body_field", "user_agent")}
        if mode == "url" and not mapping["url_field"]:
            raise HTTPException(status_code=400, detail="url mode needs url_field")
        if mode == "text" and not mapping["body_field"]:
            raise HTTPException(status_code=400, detail="text mode needs body_field")
        feed.update({k: v for k, v in mapping.items() if v})
        if mode != "url":
            feed["mode"] = mode
    try:
        brain_feed.append_feed(brain_feed.CONFIG, feed)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "id": fid}
