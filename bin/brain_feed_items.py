"""Item model + preview helpers, extracted from bin/brain-feed-gui.py.

Both the Tk GUI and the FastAPI backend (apps/api) load these helpers so real and
demo queue items are described identically on every surface. The `bin/brain-feed.py`
core (which has a hyphen in its filename) is loaded via importlib and registered in
sys.modules under the name "brain_feed" so subsequent imports return the same instance
— tests that mutate module-level paths on `gui.brain_feed` / `api.brain_feed` see the
same changes here.

Nothing in this module writes to disk on import; everything is a pure helper or reads
from the vault. See `bin/brain-feed-gui.py` (original home) for behavioural context.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path


# ---------------------------------------------------------------------------
# Load bin/brain-feed.py once, share via sys.modules so every consumer that
# imports it gets the same instance (and the same VAULT/SOURCES/REVIEW_DIR).
# ---------------------------------------------------------------------------
_FEED_PY = Path(__file__).resolve().parent / "brain-feed.py"


def _load_brain_feed():
    if "brain_feed" in sys.modules:
        return sys.modules["brain_feed"]
    spec = importlib.util.spec_from_file_location("brain_feed", _FEED_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["brain_feed"] = mod
    spec.loader.exec_module(mod)
    return mod


brain_feed = _load_brain_feed()

# Convenience aliases — do not rebind these after import; look them up on
# `brain_feed.*` in code paths that need to respect test-time patches.
VAULT = brain_feed.VAULT
SOURCES = brain_feed.SOURCES
REVIEW_DIR = brain_feed.REVIEW_DIR
RECAPS = VAULT / "wiki" / "recaps"


# ---------------------------------------------------------------------------
# Prefs / config helpers (appearance + Claude model).
# ---------------------------------------------------------------------------
def prefs_path() -> Path:
    return brain_feed.VAULT / ".brain" / "gui-prefs.json"


def load_prefs() -> dict:
    try:
        d = json.loads(prefs_path().read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save_prefs(prefs: dict) -> None:
    try:
        p = prefs_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(prefs, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def brain_config_path() -> Path:
    return brain_feed.VAULT / ".brain" / "config.json"


def load_brain_config() -> dict:
    try:
        d = json.loads(brain_config_path().read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save_brain_config(updates: dict) -> None:
    cfg = load_brain_config()
    cfg.update(updates)
    p = brain_config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Text utilities.
# ---------------------------------------------------------------------------
def parse_tags(raw: str) -> list[str]:
    if not raw:
        return []
    raw = raw.strip().lstrip("[").rstrip("]")
    out = []
    for part in raw.split(","):
        t = part.strip().strip('"').strip("'").lstrip("#").strip()
        if t:
            out.append(t)
    return out


def inject_tags(content: str, tags: list[str]) -> str:
    """Add a `tags: [...]` line to a source's frontmatter if absent."""
    if not tags:
        return content
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return content
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return content
    fm = lines[1:end]
    if any(re.match(r"^tags:\s", l) for l in fm):
        return content
    fm.append("tags: [" + ", ".join(tags) + "]")
    out = "\n".join(["---", *fm, "---", *lines[end + 1:]])
    return out + "\n" if content.endswith("\n") else out


def youtube_feed_url(url: str) -> str:
    """Normalize what a user pastes for a YouTube channel into the RSS feed URL."""
    url = (url or "").strip()
    if not url or "feeds/videos.xml" in url:
        return url
    feed = "https://www.youtube.com/feeds/videos.xml"
    if re.fullmatch(r"UC[\w-]{22}", url):
        return f"{feed}?channel_id={url}"
    if re.fullmatch(r"(?:PL|UU|OL|LL|FL)[\w-]{10,}", url):
        return f"{feed}?playlist_id={url}"
    m = re.search(r"youtube\.com/channel/(UC[\w-]{22})", url)
    if m:
        return f"{feed}?channel_id={m.group(1)}"
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    if q.get("list"):
        return f"{feed}?playlist_id={q['list'][0]}"
    return url


def rel_time(epoch: float) -> str:
    secs = max(0, time.time() - epoch)
    if secs < 90:
        return "just now"
    mins = secs / 60
    if mins < 90:
        return f"{round(mins)}m ago"
    hrs = mins / 60
    if hrs < 36:
        return f"{round(hrs)}h ago"
    return f"{round(hrs / 24)}d ago"


# ---------------------------------------------------------------------------
# Item model — the unified queue-row abstraction.
# ---------------------------------------------------------------------------
class Item:
    def __init__(self, *, iid, title, via, itype, url, reason, summary, tags,
                 overlaps=None, breakdown=None, queued="", length="", tokens="",
                 path: Path | None = None, text: str | None = None):
        self.iid = iid
        self.title = title or iid
        self.via = via or ""
        self.itype = itype or ""
        self.url = url or ""
        self.reason = reason or ""
        self.summary = summary or ""
        self.tags = tags or []
        self.overlaps = overlaps or []
        self.breakdown = breakdown or []
        self.queued = queued
        self.length = length
        self.tokens = tokens
        self.path = path
        self.text = text

    def paragraphs(self) -> list[str]:
        return [p.strip() for p in self.summary.split("\n") if p.strip()]

    _DATE_RE = re.compile(r"^\s*\d{1,2}\s+[A-Za-z]+\s+\d{4}\s*$")
    _SKIP_HEADINGS = {"contents", "table of contents", "acknowledgments",
                      "acknowledgements", "disclaimer", "references", "footnotes"}

    def outline_kind(self) -> str:
        if self.breakdown:
            return "breakdown"
        if self._heading_segments():
            return "sections"
        return "preview"

    def outline_segments(self) -> list[dict]:
        if self.breakdown:
            return self.breakdown
        return self._heading_segments() or self._preview_segments()

    def _heading_segments(self) -> list[dict]:
        if not self.text:
            return []
        segs = []
        for line in self.text.splitlines():
            m = re.match(r"^##\s+(.*\S)\s*$", line)
            if not m:
                continue
            label = m.group(1).strip()
            if label.lower() in self._SKIP_HEADINGS:
                continue
            segs.append({"at": "", "label": label, "target": ""})
            if len(segs) >= 8:
                break
        return segs

    def _preview_segments(self) -> list[dict]:
        segs = []
        for para in self.paragraphs():
            if para.startswith("# ") or self._DATE_RE.match(para):
                continue
            stripped = para.lstrip("#").strip()
            if not stripped:
                continue
            words = stripped.split()
            label = " ".join(words[:11]) + ("…" if len(words) > 11 else "")
            segs.append({"at": "", "label": label, "target": ""})
            if len(segs) >= 6:
                break
        return segs

    def to_json(self) -> dict:
        """Serialise to the shape shared with the React frontend (see
        packages/types/src/index.ts::ReviewItem)."""
        return {
            "id": self.iid,
            "title": self.title,
            "via": self.via,
            "type": self.itype,
            "url": self.url,
            "reason": self.reason,
            "summary": self.summary,
            "tags": list(self.tags),
            "overlaps": list(self.overlaps),
            "breakdown": self.outline_segments(),
            "queued": self.queued,
            "length": self.length,
            "tokens": self.tokens,
            "path": str(self.path) if self.path is not None else None,
        }


def _from_file(path: Path) -> Item:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = brain_feed._preview(text, n=400)
    summary = "\n".join(body)
    words = len(summary.split())
    via = fm.get("via", "")
    try:
        queued = rel_time(path.stat().st_mtime)
    except OSError:
        queued = fm.get("captured", "")
    return Item(
        iid=str(path),
        title=fm.get("title", path.stem),
        via=via,
        itype=fm.get("type", ""),
        url=fm.get("url", ""),
        reason=(f"queued from {via}" if via else "queued candidate"),
        summary=summary or "(no body preview)",
        tags=parse_tags(fm.get("tags", "")),
        overlaps=[],
        breakdown=[],
        queued=queued,
        length=(f"{words:,} words" if words else ""),
        tokens=(f"~{words * 4 // 3000 + 1}k" if words > 200 else ""),
        path=path,
        text=text,
    )


def load_real_items() -> list[Item]:
    brain_feed.REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    return [_from_file(p) for p in sorted(brain_feed.REVIEW_DIR.glob("*.md"))]


def load_demo_items() -> list[Item]:
    seed = [
        dict(
            iid="arxiv", title="Attention Is All You Need, Revisited",
            via="arxiv-cs-cl", itype="paper", url="arxiv.org/abs/2406.99021",
            reason="matched filter: transformers",
            summary=("A retrospective re-derivation of the original Transformer that re-runs the "
                     "2017 ablations at modern scale. Core claim: multi-head attention’s edge over "
                     "recurrence holds, but the gap from positional encoding choices is far larger "
                     "than first reported. Includes updated training curves and a cleaner notation "
                     "for the attention operator."),
            tags=["transformers", "attention", "architecture"],
            overlaps=[
                {"page": "concepts/transformer", "note": "updates §Architecture, adds 2024 ablation data"},
                {"page": "entities/vaswani-et-al", "note": "new citation → follow-up work"},
            ],
            breakdown=[
                {"at": "§1", "label": "Re-derivation of the attention operator", "target": "concepts/transformer"},
                {"at": "§3", "label": "Modern-scale ablations", "target": "concepts/transformer"},
                {"at": "§5", "label": "The positional-encoding gap", "target": "entities/vaswani-et-al"},
            ],
            queued="2h ago", length="8,200 words", tokens="~11k",
        ),
        dict(
            iid="hn", title="HN thread — are local LLMs finally good enough?",
            via="hn-ai", itype="article", url="news.ycombinator.com/item?id=99999999",
            reason="high score (480+) on topic: local-llms",
            summary=("A 400-comment thread weighing whether 30B-class local models have crossed the "
                     "“daily-driver” line. Strong disagreement: the pro camp cites privacy, offline "
                     "use, and falling latency; the skeptics point at tool-use reliability and "
                     "long-context degradation. Consensus forms around “good enough for drafting, "
                     "not for agents.”"),
            tags=["local-llms", "inference", "privacy"],
            overlaps=[
                {"page": "concepts/local-inference", "note": "open question: where is the daily-driver threshold?"},
            ],
            breakdown=[
                {"at": "cluster 1", "label": "Pro: privacy, offline, falling latency", "target": "concepts/local-inference"},
                {"at": "cluster 2", "label": "Skeptic: tool-use reliability, long-context decay", "target": "concepts/local-inference"},
                {"at": "cluster 3", "label": "Consensus: drafting, not agents", "target": "concepts/local-inference"},
            ],
            queued="5h ago", length="12,400 words", tokens="~16k",
        ),
        dict(
            iid="yt", title="Karpathy — Build a second brain with an LLM-maintained wiki",
            via="youtube-wl", itype="video", url="youtube.com/watch?v=aBcD1234xyz",
            reason="channel you follow: A. Karpathy",
            summary=("Talk arguing you should let the model own and maintain a wiki rather than RAG "
                     "over raw notes. The synthesis is precomputed once into cross-linked, auditable "
                     "pages and kept current as sources arrive. Walks through the three-layer vault "
                     "(immutable sources → AI-owned wiki → schema) and the capture/sync/lint loop."),
            tags=["second-brain", "knowledge-mgmt", "agents"],
            overlaps=[
                {"page": "concepts/llm-wiki", "note": "primary source for the method — create page"},
                {"page": "index", "note": "add to map of content"},
            ],
            breakdown=[
                {"at": "00:00", "label": "Why not RAG over raw notes", "target": "concepts/llm-wiki"},
                {"at": "04:10", "label": "The three-layer vault", "target": "concepts/llm-wiki"},
                {"at": "11:30", "label": "The capture / sync / lint loop", "target": "index"},
                {"at": "16:05", "label": "Running it unattended (launchd)", "target": "index"},
            ],
            queued="1d ago", length="18:42 video", tokens="~9k",
        ),
    ]
    return [Item(**d) for d in seed]
