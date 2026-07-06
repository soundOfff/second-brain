"""HTTP tests for apps/api — temp vault, demo queue, settings parity."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


@pytest.fixture()
def client(monkeypatch):
    """Point brain_feed at a temp vault for isolated API tests."""
    with tempfile.TemporaryDirectory() as tmp:
        vault = Path(tmp)
        (vault / "sources").mkdir()
        (vault / "wiki" / "entities").mkdir(parents=True)
        (vault / ".brain").mkdir()
        (vault / "feeds.toml").write_text('default_cap = 5\n', encoding="utf-8")
        (vault / ".brain" / "config.json").write_text("{}", encoding="utf-8")
        (vault / ".brain" / "gui-prefs.json").write_text(
            json.dumps({"accent": "amber", "density": "comfortable", "intensity": "calm"}),
            encoding="utf-8",
        )
        index = vault / "wiki" / "index.md"
        index.write_text(
            "---\ntype: index\ntitle: Test Index\ncreated: 2026-07-06\nupdated: 2026-07-06\nstatus: active\nsources: []\ntags: []\n---\n\nHello wiki.\n",
            encoding="utf-8",
        )

        BIN = REPO / "bin"
        sys.path.insert(0, str(BIN))
        import brain_feed_items as items_mod

        brain_feed = items_mod.brain_feed

        monkeypatch.setattr(brain_feed, "VAULT", vault)
        monkeypatch.setattr(brain_feed, "SOURCES", vault / "sources")
        monkeypatch.setattr(brain_feed, "REVIEW_DIR", vault / ".brain" / "review")
        monkeypatch.setattr(brain_feed, "CONFIG", vault / "feeds.toml")
        monkeypatch.setattr(brain_feed, "DB_PATH", vault / ".brain" / "feeds.sqlite")
        monkeypatch.setattr(items_mod, "VAULT", vault)
        monkeypatch.setattr(items_mod, "SOURCES", vault / "sources")
        monkeypatch.setattr(items_mod, "REVIEW_DIR", vault / ".brain" / "review")

        from apps.api.main import app

        yield TestClient(app)


def test_health(client: TestClient):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_demo_queue(client: TestClient):
    r = client.get("/api/review/queue?demo=1")
    assert r.status_code == 200
    body = r.json()
    assert body["demo"] is True
    assert len(body["items"]) >= 1


def test_settings_roundtrip(client: TestClient):
    r = client.get("/api/settings")
    assert r.status_code == 200
    assert r.json()["default_cap"] == 5

    r = client.patch("/api/settings", json={"default_cap": 7, "accent": "emerald"})
    assert r.status_code == 200
    data = r.json()
    assert data["default_cap"] == 7
    assert data["accent"] == "emerald"


def test_wiki_pages(client: TestClient):
    r = client.get("/api/wiki/pages")
    assert r.status_code == 200
    entries = r.json()["entries"]
    assert any(e["slug"] == "index" for e in entries)


def test_wiki_page_body(client: TestClient):
    r = client.get("/api/wiki/page/index")
    assert r.status_code == 200
    body = r.json()
    assert "Hello wiki" in body["body"]


def test_demo_keep_noop(client: TestClient):
    q = client.get("/api/review/queue?demo=1").json()
    iid = q["items"][0]["id"]
    r = client.post("/api/review/keep", json={"id": iid, "demo": True})
    assert r.status_code == 200
    assert "undoToken" in r.json()
