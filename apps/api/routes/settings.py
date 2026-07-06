"""Settings routes — feeder cap, Claude model, appearance prefs.

Reads and writes the same files the Tk GUI does, via the shared helpers in
brain_feed_items. That way the desktop app and the web app can co-exist —
each surface sees the same settings the moment the other saves them.
"""
from __future__ import annotations

import brain_feed
import brain_feed_items as items_mod
from fastapi import APIRouter, HTTPException


router = APIRouter()


_ACCENTS = {"amber", "indigo", "emerald", "mono"}
_DENSITIES = {"comfortable", "compact"}
_INTENSITIES = {"calm", "vivid"}


def _current() -> dict:
    prefs = items_mod.load_prefs()
    cfg = items_mod.load_brain_config()
    try:
        feeds = brain_feed.load_config(brain_feed.CONFIG)
    except Exception:
        feeds = {}
    accent = prefs.get("accent") if prefs.get("accent") in _ACCENTS else "amber"
    density = prefs.get("density") if prefs.get("density") in _DENSITIES else "comfortable"
    intensity = prefs.get("intensity") if prefs.get("intensity") in _INTENSITIES else "calm"
    model = cfg.get("model", "")
    return {
        "default_cap": int(feeds.get("default_cap", 5)),
        "model": model if isinstance(model, str) else "",
        "accent": accent,
        "density": density,
        "intensity": intensity,
    }


@router.get("")
def get_settings():
    return _current()


@router.patch("")
def patch_settings(payload: dict):
    """Partial update — only mutates the fields present. All persistence goes
    through the existing feeds.toml / .brain/config.json / .brain/gui-prefs.json
    files, so the desktop GUI picks up the change on its next read."""
    # 1) Feeder default cap → feeds.toml
    if "default_cap" in payload:
        try:
            cap = int(payload["default_cap"])
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="default_cap must be an integer")
        try:
            brain_feed.set_default_cap(brain_feed.CONFIG, cap)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # 2) Claude model → .brain/config.json (only for the unattended agents).
    if "model" in payload:
        model = payload["model"]
        if model is None:
            model = ""
        if not isinstance(model, str):
            raise HTTPException(status_code=400, detail="model must be a string")
        items_mod.save_brain_config({"model": model.strip()})

    # 3) Appearance prefs → .brain/gui-prefs.json (best-effort, never fatal).
    prefs_update: dict = {}
    if "accent" in payload:
        if payload["accent"] not in _ACCENTS:
            raise HTTPException(status_code=400, detail="unknown accent")
        prefs_update["accent"] = payload["accent"]
    if "density" in payload:
        if payload["density"] not in _DENSITIES:
            raise HTTPException(status_code=400, detail="unknown density")
        prefs_update["density"] = payload["density"]
    if "intensity" in payload:
        if payload["intensity"] not in _INTENSITIES:
            raise HTTPException(status_code=400, detail="unknown intensity")
        prefs_update["intensity"] = payload["intensity"]
    if prefs_update:
        prefs = items_mod.load_prefs()
        prefs.update(prefs_update)
        items_mod.save_prefs(prefs)

    return _current()
