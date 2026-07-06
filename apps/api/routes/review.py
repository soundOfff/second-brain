"""Review queue routes — mirrors the Tk GUI's Keep/Drop/Skip/Undo flow.

Undo state is kept per-connection in a small in-memory store (see UndoStore).
The Tk GUI holds a single-level undo record on the app instance; the API does
the same, keyed by an opaque token returned to the client. That token is a
short random string, safe to round-trip through JSON.
"""
from __future__ import annotations

import secrets
import time
from pathlib import Path

import brain_feed
import brain_feed_items as items_mod
from fastapi import APIRouter, HTTPException, Query


router = APIRouter()


class UndoStore:
    """In-memory single-level undo, keyed by token. Entries older than an hour
    are swept lazily so a long-lived process never leaks orphaned files."""

    _entries: dict[str, dict] = {}
    _ttl_sec = 3600

    @classmethod
    def put(cls, payload: dict) -> str:
        cls._sweep()
        token = secrets.token_urlsafe(12)
        cls._entries[token] = {"at": time.time(), **payload}
        return token

    @classmethod
    def pop(cls, token: str) -> dict | None:
        cls._sweep()
        return cls._entries.pop(token, None)

    @classmethod
    def _sweep(cls) -> None:
        cutoff = time.time() - cls._ttl_sec
        stale = [t for t, e in cls._entries.items() if e["at"] < cutoff]
        for t in stale:
            cls._entries.pop(t, None)


@router.get("/queue")
def get_queue(demo: bool = Query(default=False)):
    """Return the current review queue as JSON."""
    loader = items_mod.load_demo_items if demo else items_mod.load_real_items
    return {
        "items": [it.to_json() for it in loader()],
        "demo": demo,
    }


def _item_by_id(iid: str, demo: bool):
    loader = items_mod.load_demo_items if demo else items_mod.load_real_items
    for it in loader():
        if it.iid == iid:
            return it
    return None


@router.post("/keep")
def keep(payload: dict):
    """Place a queued item into sources/. Body: {id, demo?}. Returns the placed
    path (relative to the vault) and an undo token."""
    iid = payload.get("id")
    demo = bool(payload.get("demo", False))
    if not iid:
        raise HTTPException(status_code=400, detail="id required")
    if demo:
        return {"placed": f"sources/demo-{iid}.md", "undoToken": UndoStore.put({
            "kind": "keep", "demo": True, "id": iid,
        })}
    it = _item_by_id(iid, demo=False)
    if it is None or it.path is None:
        raise HTTPException(status_code=404, detail="item not in queue")
    path = Path(it.path)
    text = path.read_text(encoding="utf-8", errors="replace")
    dest = brain_feed.place(text, path.name, brain_feed.SOURCES, brain_feed.VAULT,
                            check_review=False)
    path.unlink()
    ts = _log_decision(it.via, path.stem, "keep")
    token = UndoStore.put({
        "kind": "keep", "demo": False, "name": path.name, "text": text,
        "placed": str(dest), "review_path": str(path),
        "decision_ts": ts, "item_id": path.stem, "feed_id": it.via,
    })
    return {"placed": str(dest.relative_to(brain_feed.VAULT)), "undoToken": token}


@router.post("/drop")
def drop(payload: dict):
    iid = payload.get("id")
    demo = bool(payload.get("demo", False))
    if not iid:
        raise HTTPException(status_code=400, detail="id required")
    if demo:
        return {"undoToken": UndoStore.put({
            "kind": "drop", "demo": True, "id": iid,
        })}
    it = _item_by_id(iid, demo=False)
    if it is None or it.path is None:
        raise HTTPException(status_code=404, detail="item not in queue")
    path = Path(it.path)
    text = path.read_text(encoding="utf-8", errors="replace")
    path.unlink()
    ts = _log_decision(it.via, path.stem, "drop")
    token = UndoStore.put({
        "kind": "drop", "demo": False, "name": path.name, "text": text,
        "review_path": str(path),
        "decision_ts": ts, "item_id": path.stem, "feed_id": it.via,
    })
    return {"undoToken": token}


@router.post("/undo")
def undo(payload: dict):
    token = payload.get("undoToken")
    if not token:
        raise HTTPException(status_code=400, detail="undoToken required")
    entry = UndoStore.pop(token)
    if entry is None:
        raise HTTPException(status_code=410, detail="undo token expired or unknown")
    if entry.get("demo"):
        return {"ok": True, "demo": True}
    review_path = Path(entry["review_path"])
    if entry["kind"] == "keep":
        placed = Path(entry["placed"])
        if placed.exists():
            placed.unlink()
    # Restore the queued file either way.
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(entry["text"], encoding="utf-8")
    # Undo the decision-log row so keep-rate stays honest.
    if entry.get("decision_ts") is not None and entry.get("item_id"):
        _delete_decision(entry["item_id"], entry["decision_ts"])
    return {"ok": True, "restored": str(review_path.relative_to(brain_feed.VAULT))}


def _log_decision(feed_id: str, item_id: str, action: str):
    """Best-effort decision-log write — never surfaces db errors to the client."""
    try:
        con = brain_feed.db_connect(brain_feed.DB_PATH)
    except Exception:
        return None
    try:
        ts = brain_feed.log_decision(con, feed_id or "", item_id, action)
        con.commit()
        return ts
    except Exception:
        return None
    finally:
        try:
            con.close()
        except Exception:
            pass


def _delete_decision(item_id: str, ts: int) -> None:
    try:
        con = brain_feed.db_connect(brain_feed.DB_PATH)
    except Exception:
        return
    try:
        brain_feed.delete_decision(con, item_id, ts)
        con.commit()
    except Exception:
        pass
    finally:
        try:
            con.close()
        except Exception:
            pass


@router.post("/open-url")
def open_url(payload: dict):
    """Stub — the desktop app used `open <url>` via subprocess. In the browser,
    the frontend should just window.open() itself. Kept for API completeness."""
    return {"ok": True, "url": payload.get("url")}
