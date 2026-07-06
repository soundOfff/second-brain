"""FastAPI backend for the Second Brain web app.

Wraps the existing `bin/brain-feed.py` core and the wiki data model in a small
JSON API so the React frontend (apps/web) can drive the same review + feed +
wiki flows the Tk GUI already does. Nothing here re-implements domain logic —
routes delegate to `brain_feed`, `brain_feed_items`, and `brain_wiki_data`.
"""
from __future__ import annotations

from . import paths  # noqa: F401  (side-effect: adds bin/ to sys.path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import review, feeds, settings, sources_route, wiki


def create_app() -> FastAPI:
    app = FastAPI(title="Second Brain API", version="0.1.0")

    # CORS is only needed if the SPA is served from a different origin.
    # In dev, Vite proxies /api/* → this server, so browsers see one origin.
    # We still allow localhost:5173 so `pnpm preview` (static build) works.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(review.router, prefix="/api/review", tags=["review"])
    app.include_router(feeds.router, prefix="/api/feeds", tags=["feeds"])
    app.include_router(sources_route.router, prefix="/api/sources", tags=["sources"])
    app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
    app.include_router(wiki.router, prefix="/api/wiki", tags=["wiki"])

    @app.get("/api/health")
    def health():
        return {"ok": True}

    return app


app = create_app()
