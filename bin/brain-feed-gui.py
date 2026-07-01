#!/usr/bin/env python3
"""Second Brain — brain-feed-gui: a desktop triage window for the pull-feeder queue.

The terminal `brain-feed review` walks .brain/review/ item-by-item asking k/d/s at a
prompt. This is the same triage as a refined dark "dev-tool" macOS window (Tkinter): an
ordered queue on the left (numbered nodes on a connecting rail, the current item filled
amber with a NOW tag, drag to reorder), the selected item's recap/outline on the right,
and Keep / Drop / Skip / Open / Undo as an action bar with mono keyboard-hint chips.

It is a thin shell over brain-feed.py — all the real logic (where a kept item lands,
collision-safe naming) is reused from there, so behaviour stays single-source:

  Keep  (k / ⏎)   place the item into sources/  (collision-safe via brain-feed.place)
  Drop  (d)       delete the queued candidate   (the pen is gitignored scratch)
  Skip  (→)       leave it queued, just advance  (non-destructive)
  Undo  (u)       reverse the last Keep or Drop (single level)
  Open  (o)       open the source url            Rescan (⇧R)  reload the queue from disk
  ↑/↓             move selection                 g            toggle Recap / Outline
  r / f / s       jump to Review Queue / Feed Stats / Settings screens
  click select    ·    drag to reorder (session) ·    q       quit

A top tab bar switches between the Review Queue, a **Feed Stats** screen (t), and a
**Settings** screen. Feed Stats holds a read-only per-feed table (seen / today / queued /
keep-rate) plus a **New source** form with a type selector:

  webpage   deposit one source straight into sources/ — clip a URL or jot a note —
            reusing the same brain-clip render + place path the feeder uses, so it's
            contract-valid and the next /sync folds it in.
  rss/api   subscribe instead: append a [[feed]] block to feeds.toml (trust, cap, tags;
            plus the declarative mapping fields for api) via brain_feed.append_feed —
            the next feeder run pulls it.

Settings edits the feeder's global daily cap (default_cap, written back into feeds.toml
in place) and the appearance options (accent / density / intensity), persisted to
.brain/gui-prefs.json (gitignored). Global one-key shortcuts yield to normal typing
while a form field has focus.

Theme defaults — amber accent · comfortable density · calm intensity. No synthesis
happens here (same as the CLI): kept items wait for the 02:00 /sync.

  bin/brain-feed-gui.sh                 triage the real .brain/review/ queue
  bin/brain-feed-gui.sh --demo          showcase with 3 seeded items (no filesystem writes)

Needs Tk: `brew install python-tk@3.14` (matches your Homebrew python3).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import subprocess
import sys
import threading
import time
import urllib.parse
from pathlib import Path

import tkinter as tk
import tkinter.font as tkfont

# --- reuse brain-feed.py (hyphenated filename → import via importlib) ----------
_FEED_PY = Path(__file__).resolve().parent / "brain-feed.py"
_spec = importlib.util.spec_from_file_location("brain_feed", _FEED_PY)
brain_feed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(brain_feed)

VAULT = brain_feed.VAULT
SOURCES = brain_feed.SOURCES
REVIEW_DIR = brain_feed.REVIEW_DIR
RECAPS = VAULT / "wiki" / "recaps"       # a source has a recap iff RECAPS/<id>.md exists


# ============================================================================
# Palette — warm near-black "refined terminal / dev-tool" dark.
# ============================================================================
BASE = {
    "bg":          "#1a1916",
    "panel":       "#1d1b17",
    "raise":       "#211e1a",
    "sunk":        "#1f1c18",
    "node":        "#252219",
    "border":      "#322e28",
    "border_soft": "#2a2722",
    "rail":        "#3a362f",
    "frame":       "#34302a",
    "ink":         "#ece8df",
    "ink_bright":  "#f5f1e8",
    "ink_muted":   "#b8b1a4",
    "ink_dim":     "#9a9384",
    "ink_dim2":    "#8a8474",
    "ink_faint":   "#7e786b",
    "ink_fainter": "#5a554c",
    "hair":        "#4a443a",
    "recap_ink":   "#d7d1c4",
    "drop_border": "#8a5a45",
    "drop_ink":    "#e0a890",
}

ACCENTS = {
    "amber":   {"h": "#d8a04a", "on": "#1a1916"},
    "indigo":  {"h": "#8aa0ff", "on": "#10131f"},
    "emerald": {"h": "#56c98e", "on": "#0d1a12"},
    "mono":    {"h": "#cfc9bd", "on": "#1a1916"},
}

DENSITY = {
    "comfortable": dict(
        side_padx=18, side_pady=14, head_padx=28, head_pady=20, card_padx=28, card_pady=22,
        title=23, recap=15, row_h=64, row_pt=12, node_c=23, btn_ipady=8, bar_h=60,
        gap=10, footer_padx=16, btn_w=120, btn_h=40,
    ),
    "compact": dict(
        side_padx=16, side_pady=11, head_padx=24, head_pady=13, card_padx=24, card_pady=16,
        title=19, recap=13, row_h=54, row_pt=9, node_c=20, btn_ipady=6, bar_h=48,
        gap=8, footer_padx=16, btn_w=106, btn_h=34,
    ),
}


# ============================================================================
# Color helpers — Tk canvas/widgets have no alpha, so composite tints to hex.
# ============================================================================
def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in rgb)


def blend(fg: str, bg: str, alpha: float) -> str:
    """Composite `fg` over `bg` at `alpha` → opaque hex (emulates rgba on a known bg)."""
    f, b = _hex_to_rgb(fg), _hex_to_rgb(bg)
    return _rgb_to_hex(tuple(f[i] * alpha + b[i] * (1 - alpha) for i in range(3)))


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
    """Add a `tags: [...]` line to a source's frontmatter if absent, returning the
    content unchanged when there's nothing to do. Mirrors brain_feed.inject_provenance
    but *without* stamping a feed `via:` — a source hand-made in this window is a plain
    source, not a feed pull, so it carries no feed provenance."""
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


def prefs_path() -> Path:
    """Appearance prefs live in the gitignored .brain/ — looked up lazily so tests
    that redirect VAULT never touch the real vault."""
    return VAULT / ".brain" / "gui-prefs.json"


def load_prefs() -> dict:
    try:
        d = json.loads(prefs_path().read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save_prefs(prefs: dict) -> None:
    """Best-effort persist — appearance must never crash triage."""
    try:
        p = prefs_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(prefs, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


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


# ============================================================================
# Markdown → display blocks.
#
# Tk has no markdown widget and a Label holds exactly one font/colour, so we
# render *block* structure (headings, quotes, lists, paragraphs) as stacked
# frames and flatten *inline* markup to plain text:
#   - *italic* / **bold** markers are stripped (no per-word styling in a Label);
#   - in recaps, wikilinks [[path/slug]] are cleaned to a readable title, and a
#     block that is *only* wikilinks is accent-coloured wholesale (entity/concept
#     lists) — inline links buried in prose are cleaned but not coloured;
#   - citations [src-id] are kept verbatim so provenance stays on screen.
# ============================================================================
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*(?!\s)([^*]+?)\*(?!\*)")
_LINKS_ONLY_RE = re.compile(r"^(?:\[\[[^\]]+\]\][\s,;·]*)+$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+")


_ACRONYMS = {"llm", "llms", "rag", "ai", "api", "ui", "ux", "gui", "cli", "pdf",
             "url", "sdk", "adr"}


def _link_title(inner: str) -> str:
    """[[path/to/slug]] or [[slug|Alias]] → a human label. Aliases pass through
    verbatim; slugs are title-cased with known acronyms re-uppercased."""
    if "|" in inner:
        return inner.split("|", 1)[1].strip()
    seg = inner.rstrip("/").split("/")[-1].strip()
    if not seg:
        return inner
    words = seg.replace("-", " ").replace("_", " ").split()
    return " ".join(w.upper() if w.lower() in _ACRONYMS else w.title() for w in words)


def clean_inline(s: str, *, recap: bool) -> str:
    """Flatten inline markup to plain text. Citations [src-id] are left verbatim."""
    if recap:
        s = _WIKILINK_RE.sub(lambda m: _link_title(m.group(1)), s)
    s = _BOLD_RE.sub(r"\1", s)
    s = _ITALIC_RE.sub(r"\1", s)
    return s.strip()


def parse_blocks(lines: list[str], *, recap: bool, join_wrapped: bool = False) -> list[dict]:
    """Classify each non-blank line into a display block. Returns
    [{kind, text, accent?}] with kind in h2 | h3 | p | quote | li.

    `join_wrapped` reflows hard-wrapped prose: a plain line that continues the
    previous paragraph/list-item (no blank line between) is appended to it, and a
    blank line separates paragraphs. Use it for raw files that wrap at ~90 cols
    (recaps); leave it off for `_preview` output, where blanks are already gone
    and every line is its own paragraph."""
    blocks: list[dict] = []
    prev_blank = True
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            prev_blank = True
            continue
        accent = recap and bool(_LINKS_ONLY_RE.match(line.strip()))
        if line.startswith("### ") or line.startswith("#### "):
            blocks.append({"kind": "h3", "text": clean_inline(line.lstrip("#").strip(), recap=recap)})
        elif line.startswith("## "):
            blocks.append({"kind": "h2", "text": clean_inline(line[3:].strip(), recap=recap)})
        elif line.startswith("# "):
            blocks.append({"kind": "h2", "text": clean_inline(line[2:].strip(), recap=recap)})
        elif line.lstrip().startswith("> "):
            text = clean_inline(line.lstrip()[2:].strip(), recap=recap)
            if blocks and blocks[-1]["kind"] == "quote" and not prev_blank:
                blocks[-1]["text"] += " " + text
            else:
                blocks.append({"kind": "quote", "text": text})
        elif _BULLET_RE.match(line):
            content = _BULLET_RE.sub("", line)
            blocks.append({"kind": "li", "text": clean_inline(content, recap=recap),
                           "accent": recap and bool(_LINKS_ONLY_RE.match(content.strip()))})
        elif join_wrapped and not prev_blank and blocks and blocks[-1]["kind"] in ("p", "li"):
            blocks[-1]["text"] += " " + clean_inline(line, recap=recap)
        else:
            blocks.append({"kind": "p", "text": clean_inline(line, recap=recap), "accent": accent})
        prev_blank = False
    return blocks


def strip_masthead(blocks: list[dict]) -> list[dict]:
    """Drop the leading run of headings (source title/date, or the recap's own
    title line) — the card header already shows the title."""
    i = 0
    while i < len(blocks) and blocks[i]["kind"] in ("h2", "h3"):
        i += 1
    return blocks[i:]


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:])
    return text


# ============================================================================
# Item model — unifies real queued files and the demo showcase data.
# ============================================================================
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
        self.summary = summary or ""             # recap body (string, may be multi-para)
        self.tags = tags or []
        self.overlaps = overlaps or []           # [{page, note}]  (empty for real items)
        self.breakdown = breakdown or []         # [{at, label, target}]
        self.queued = queued
        self.length = length
        self.tokens = tokens
        self.path = path                          # None → demo (no filesystem side effects)
        self.text = text

    # paragraphs of the recap, for the outline view
    def paragraphs(self) -> list[str]:
        return [p.strip() for p in self.summary.split("\n") if p.strip()]

    # masthead lines to skip in the preview fallback (bare "16 June 2026" dates)
    _DATE_RE = re.compile(r"^\s*\d{1,2}\s+[A-Za-z]+\s+\d{4}\s*$")
    # source headings that are scaffolding, not real content sections
    _SKIP_HEADINGS = {"contents", "table of contents", "acknowledgments",
                      "acknowledgements", "disclaimer", "references", "footnotes"}

    def outline_kind(self) -> str:
        """How the Outline view's segments were derived — drives an honest label.

        'breakdown' = a real, /sync-computed decomposition; 'sections' = the
        source's own markdown headings; 'preview' = just its first body lines.
        """
        if self.breakdown:
            return "breakdown"
        if self._heading_segments():
            return "sections"
        return "preview"

    def outline_segments(self) -> list[dict]:
        """Segments for the Outline view.

        A real, /sync-computed breakdown wins. Otherwise fall back to the
        source's own section headings — and, lacking those, its first few body
        lines with the masthead (title, date, byline) skipped. The fallback is
        a preview of the raw source, not a semantic decomposition.
        """
        if self.breakdown:
            return self.breakdown
        return self._heading_segments() or self._preview_segments()

    def _heading_segments(self) -> list[dict]:
        """Level-2 markdown headings from the raw source, as outline sections."""
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
        """First few real body lines, with masthead (title/date) skipped."""
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
        overlaps=[],                              # real overlaps are computed at /sync
        breakdown=[],
        queued=queued,
        length=(f"{words:,} words" if words else ""),
        tokens=(f"~{words * 4 // 3000 + 1}k" if words > 200 else ""),
        path=path,
        text=text,
    )


def load_real_items() -> list[Item]:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    return [_from_file(p) for p in sorted(REVIEW_DIR.glob("*.md"))]


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


# ============================================================================
# A vertically scrollable frame (Canvas + inner frame) for the card body.
# ============================================================================
class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win, width=e.width))
        self.bind_wheel(self.canvas)
        self.bind_wheel(self.inner)

    def bind_wheel(self, w):
        """Bind the wheel handler onto one widget. Tk delivers a wheel event to the
        widget *under the cursor*, not the scroll canvas — and the recap fills the pane
        with child labels/frames — so binding only the canvas/inner leaves scrolling
        dead everywhere the content actually is. `bind_wheel_to_children` walks the
        freshly-rendered subtree after each render to cover them all."""
        w.bind("<MouseWheel>", self._wheel)
        w.bind("<Button-4>", self._wheel)
        w.bind("<Button-5>", self._wheel)

    def bind_wheel_to_children(self):
        """(Re)bind the wheel across every descendant of `inner`. `tk.Text` is skipped
        so a multi-line text area keeps its own vertical scrolling."""
        def walk(w):
            if not isinstance(w, tk.Text):
                self.bind_wheel(w)
            for c in w.winfo_children():
                walk(c)
        for c in self.inner.winfo_children():
            walk(c)

    def _wheel(self, e):
        # Button-4/5 (X11/older trackpads) carry no `delta`; map them by button number.
        num = getattr(e, "num", 0)
        if num == 4:
            step = -1
        elif num == 5:
            step = 1
        else:
            step = -1 if e.delta > 0 else 1
        self.canvas.yview_scroll(step, "units")


# ============================================================================
# The app.
# ============================================================================
SIDEBAR_W = 296


class ReviewApp:
    def __init__(self, root: tk.Tk, demo: bool = False) -> None:
        self.root = root
        self.demo = demo
        # theme — defaults locked, overridable from the Settings tab (persisted)
        prefs = load_prefs()
        self.accent = prefs.get("accent") if prefs.get("accent") in ACCENTS else "amber"
        self.density = (prefs.get("density")
                        if prefs.get("density") in DENSITY else "comfortable")
        self.intensity = (prefs.get("intensity")
                          if prefs.get("intensity") in ("calm", "vivid") else "calm")

        self.items: list[Item] = []
        self.sel = 0
        self.view = "recap"               # 'recap' | 'graph'  (per-item card)
        self.screen = "review"            # 'review' | 'stats' (whole main pane)
        self.kept = 0
        self.dropped = 0
        self.undo_rec: dict | None = None  # single-level undo
        self.drag: dict | None = None
        self._toast_after = None
        self._db = None                   # cached sqlite connection (lazy)
        self._stats_cache: list[dict] | None = None
        self._creating = False            # new-source deposit in flight (form guard)
        self._ns_kind = "webpage"         # new-source type: webpage | rss | api
        self._ns_trust = "queue"          # feed trust for rss/api subscriptions
        self._ns_mode = "url"             # api mapping mode: url | text
        self._ns_expanded = False         # form starts collapsed behind "+ Add source"
        self._ns_vals: dict = {}          # field values carried across form rebuilds

        root.title("Brain Feed — Review Queue")
        root.geometry("1120x740")
        root.minsize(900, 600)
        root.configure(bg=BASE["bg"])
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._init_fonts()
        self._bind_keys()
        self.reload(select_first=True, fresh_session=True)
        self.rebuild()

    # -- fonts -----------------------------------------------------------------
    def _init_fonts(self) -> None:
        fams = set(tkfont.families(self.root))

        def pick(cands, fallback):
            for c in cands:
                if c in fams:
                    return c
            return fallback

        self.ui_face = pick(["Inter", "SF Pro Text", "Helvetica Neue"], "Helvetica")
        self.mono_face = pick(["JetBrains Mono", "SF Mono", "Menlo"], "Courier")

    def font(self, kind: str, size: int, weight="normal"):
        face = self.mono_face if kind == "mono" else self.ui_face
        return tkfont.Font(family=face, size=-size, weight=weight)  # -size = pixels

    # -- theme -----------------------------------------------------------------
    def compute_theme(self) -> dict:
        ac = ACCENTS[self.accent]
        d = DENSITY[self.density]
        vivid = self.intensity == "vivid"
        a = ac["h"]
        t = dict(BASE)
        t.update(d)
        t["ac"] = a
        t["ac_on"] = ac["on"]
        t["sel_bg"] = blend(a, BASE["panel"], 0.13 if vivid else 0.08)
        t["qrail"] = blend(a, BASE["panel"], 0.40) if vivid else BASE["rail"]
        t["qrail_w"] = 2 if vivid else 1
        t["grail"] = blend(a, BASE["panel"], 0.42) if vivid else BASE["rail"]
        t["grail_w"] = 2 if vivid else 1
        t["glow"] = blend(a, BASE["panel"], 0.30)
        t["now_bg"] = blend(a, BASE["panel"], 0.16)
        t["pill_bg"] = blend(a, BASE["panel"], 0.12)
        t["pill_bd"] = blend(a, BASE["panel"], 0.30)
        t["reason_bg"] = blend(a, BASE["bg"], 0.16 if vivid else 0.12)
        t["reason_bd"] = blend(a, BASE["bg"], 0.30)
        t["kbd_bg"] = blend(a, BASE["bg"], 0.16)
        t["kbd_bd"] = blend(a, BASE["bg"], 0.34)
        t["kbd_on_bg"] = blend("#000000", a, 0.30)
        t["field_bd"] = blend(a, BASE["raise"], 0.55)
        t["tag_bg"] = BASE["node"]
        t["vivid"] = vivid
        return t

    # -- key bindings ----------------------------------------------------------
    def _bind_keys(self) -> None:
        b = self.root.bind_all

        def key(fn):
            # Global single-key shortcuts must not fire while the user is typing in a
            # form field, or "type", "quit", etc. would trigger mid-word. Let the
            # widget's own class binding handle the keystroke and no-op the shortcut.
            def handler(e):
                if self._typing():
                    return
                fn()
            return handler

        b("<k>", key(self.do_keep))
        b("<Return>", key(self.do_keep))
        b("<d>", key(self.do_drop))
        b("<Right>", key(self.do_skip))
        b("<o>", key(self.open_url))
        b("<u>", key(self.do_undo))
        b("<R>", key(self.do_rescan))
        b("<g>", key(self.toggle_view))
        b("<r>", key(lambda: self.set_screen("review")))
        b("<f>", key(lambda: self.set_screen("stats")))
        b("<s>", key(lambda: self.set_screen("settings")))
        b("<t>", key(self.toggle_screen))
        b("<q>", key(self._on_close))
        b("<Down>", key(lambda: self.move(1)))
        b("<Up>", key(lambda: self.move(-1)))

    def _typing(self) -> bool:
        """True when keyboard focus is in a text-input widget, so global shortcuts
        should yield to normal typing."""
        try:
            return isinstance(self.root.focus_get(), (tk.Entry, tk.Text))
        except Exception:
            return False

    # -- data ------------------------------------------------------------------
    def reload(self, select_first=False, fresh_session=False) -> None:
        self.items = load_demo_items() if self.demo else load_real_items()
        if select_first:
            self.sel = 0
        else:
            self.sel = max(0, min(self.sel, len(self.items) - 1))
        if fresh_session:
            self.kept = self.dropped = 0
            self.undo_rec = None

    def current(self) -> Item | None:
        if 0 <= self.sel < len(self.items):
            return self.items[self.sel]
        return None

    # ======================================================================
    # Build — full (re)construction of the widget tree (theme/density change).
    # ======================================================================
    def rebuild(self) -> None:
        self.t = self.compute_theme()
        for w in self.root.winfo_children():
            w.destroy()

        root_frame = tk.Frame(self.root, bg=BASE["bg"])
        root_frame.pack(fill="both", expand=True)

        self._build_topbar(root_frame)

        body = tk.Frame(root_frame, bg=BASE["bg"])
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        self._build_main(body)

        # toast overlay (placed over the main pane, hidden until used)
        self.toast = tk.Label(self.root, text="", font=self.font("mono", 12, "bold"),
                              bg=self.t["ac"], fg=self.t["ac_on"], padx=16, pady=8)

        self.render_queue()
        self.render_main()

    # -- top tab bar (Review Queue ↔ Feed Stats) -------------------------------
    def _build_topbar(self, parent) -> None:
        t = self.t
        bar = tk.Frame(parent, bg=BASE["panel"], height=40)
        bar.pack(side="top", fill="x")
        bar.pack_propagate(False)
        tk.Frame(bar, bg=BASE["border"], height=1).pack(side="bottom", fill="x")
        seg = tk.Frame(bar, bg=BASE["raise"], highlightthickness=1,
                       highlightbackground=BASE["border"])
        seg.pack(side="left", padx=t["head_padx"], pady=6)
        self._screen_tab(seg, "Review Queue  r", "review")
        self._screen_tab(seg, "Feed Stats  f", "stats")
        self._screen_tab(seg, "Settings  s", "settings")

    def _screen_tab(self, parent, label, value):
        t = self.t
        on = (self.screen == value)
        cell = tk.Frame(parent, bg=(t["ac"] if on else BASE["raise"]))
        cell.pack(side="left", padx=2, pady=2)
        lab = tk.Label(cell, text=label, bg=cell["bg"],
                       fg=(t["ac_on"] if on else BASE["ink_dim"]),
                       font=self.font("mono", 11, "bold"), padx=12, pady=4)
        lab.pack()
        for w in (cell, lab):
            w.bind("<Button-1>", lambda e: self.set_screen(value))

    # -- sidebar ---------------------------------------------------------------
    def _build_sidebar(self, parent) -> None:
        t = self.t
        side = tk.Frame(parent, bg=BASE["panel"], width=SIDEBAR_W)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        # right border
        tk.Frame(side, bg=BASE["border"], width=1).pack(side="right", fill="y")

        inner = tk.Frame(side, bg=BASE["panel"])
        inner.pack(side="left", fill="both", expand=True)

        # header
        head = tk.Frame(inner, bg=BASE["panel"])
        head.pack(fill="x", padx=t["side_padx"], pady=(t["side_pady"], 8))
        htext = tk.Frame(head, bg=BASE["panel"])
        htext.pack(side="left")
        tk.Label(htext, text="Review queue", bg=BASE["panel"], fg=BASE["ink"],
                 font=self.font("ui", 13, "bold")).pack(anchor="w")
        tk.Label(htext, text="awaiting triage", bg=BASE["panel"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10)).pack(anchor="w", pady=(3, 0))
        self.count_pill = tk.Label(head, text="0", bg=t["pill_bg"], fg=t["ac"],
                                   font=self.font("mono", 11, "bold"), padx=8, pady=3,
                                   highlightthickness=1, highlightbackground=t["pill_bd"])
        self.count_pill.pack(side="right")

        # progress
        prog = tk.Frame(inner, bg=BASE["border_soft"], height=3)
        prog.pack(fill="x", padx=t["side_padx"], pady=(0, 8))
        prog.pack_propagate(False)
        self.progress = tk.Frame(prog, bg=t["ac"], width=0)
        self.progress.place(x=0, y=0, relheight=1.0, width=0)
        self._prog_track = prog

        # queue canvas
        qwrap = tk.Frame(inner, bg=BASE["panel"])
        qwrap.pack(fill="both", expand=True, padx=(0, 0))
        self.qcanvas = tk.Canvas(qwrap, bg=BASE["panel"], highlightthickness=0, bd=0)
        self.qcanvas.pack(fill="both", expand=True)
        self.qcanvas.bind("<ButtonPress-1>", self._q_press)
        self.qcanvas.bind("<B1-Motion>", self._q_motion)
        self.qcanvas.bind("<ButtonRelease-1>", self._q_release)
        self.qcanvas.bind("<Configure>", lambda e: self.render_queue())
        self.qcanvas.bind("<MouseWheel>", self._q_wheel)
        self.qcanvas.bind("<Button-4>", lambda e: self.qcanvas.yview_scroll(-1, "units"))
        self.qcanvas.bind("<Button-5>", lambda e: self.qcanvas.yview_scroll(1, "units"))

        # footer (height matches action bar)
        foot = tk.Frame(inner, bg=BASE["panel"], height=t["bar_h"])
        foot.pack(fill="x")
        foot.pack_propagate(False)
        tk.Frame(foot, bg=BASE["border_soft"], height=1).pack(side="top", fill="x")
        frow = tk.Frame(foot, bg=BASE["panel"])
        frow.pack(fill="both", expand=True, padx=t["footer_padx"])
        nfeeds = self._feed_count()
        tk.Label(frow, text=f"feeds: {nfeeds} active", bg=BASE["panel"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10)).pack(side="left")
        self._action_button(frow, "Rescan", "⇧r", "outline", self.do_rescan).pack(side="right")

    def _feed_count(self) -> int:
        try:
            cfg = brain_feed.load_config(brain_feed.CONFIG)
            feeds = cfg.get("feeds", []) or []
            return sum(1 for f in feeds if f.get("enabled", True))
        except Exception:
            return 0

    # -- main pane -------------------------------------------------------------
    def _build_main(self, parent) -> None:
        t = self.t
        main = tk.Frame(parent, bg=BASE["bg"])
        main.pack(side="left", fill="both", expand=True)
        self.main = main

        # header (rebuilt per item by render_main)
        self.head = tk.Frame(main, bg=BASE["bg"])
        self.head.pack(fill="x")
        tk.Frame(main, bg=BASE["border_soft"], height=1).pack(fill="x")

        # card body (scrollable)
        self.card = ScrollFrame(main, bg=BASE["bg"])
        self.card.pack(fill="both", expand=True)

        # action bar
        bar = tk.Frame(main, bg=BASE["panel"], height=t["bar_h"])
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        tk.Frame(bar, bg=BASE["border"], height=1).pack(side="top", fill="x")
        self.actionrow = tk.Frame(bar, bg=BASE["panel"])
        self.actionrow.pack(fill="both", expand=True, padx=t["head_padx"] - 6)

    # ======================================================================
    # Reusable button widgets.
    # ======================================================================
    @staticmethod
    def _rounded_polygon(c, x1, y1, x2, y2, r, **kw):
        """Draw a rounded rectangle whose corners are real arc points.

        Tk's ``smooth=True`` polygon approximates the corners with a quadratic
        B-spline that isn't pixel-symmetric, so the four corners round by
        different amounts (an extra pixel on one, a missing pixel on another)
        and the spline steps fringe the outline like particles. Instead we
        emit the actual arc coordinates and draw a crisp (non-smooth) polygon,
        so every corner is identical and the edges stay dead straight.
        """
        r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
        # Clockwise: each corner is (center_x, center_y, start_angle_degrees),
        # swept 90° toward the next edge. Canvas y grows downward, so sin() is
        # measured downward too — the angles below are in that convention.
        corners = ((x2 - r, y1 + r, 270),   # top-right
                   (x2 - r, y2 - r, 0),      # bottom-right
                   (x1 + r, y2 - r, 90),     # bottom-left
                   (x1 + r, y1 + r, 180))    # top-left
        steps = 8  # points per corner; symmetric for all four
        pts = []
        for cx, cy, a0 in corners:
            for i in range(steps + 1):
                a = math.radians(a0 + 90 * i / steps)
                pts.extend((cx + r * math.cos(a), cy + r * math.sin(a)))
        return c.create_polygon(pts, smooth=False, **kw)

    @staticmethod
    def _round_rect(c, x1, y1, x2, y2, r, **kw):
        """Draw a rounded rectangle on canvas c. Returns item id."""
        return ReviewApp._rounded_polygon(c, x1, y1, x2, y2, r, **kw)

    def _action_button(self, parent, text, key, kind, command, enabled=True, width_mult=1):
        """kind: 'primary' | 'outline' | 'drop'. Returns a rounded canvas button.

        All buttons share a fixed height/width (t['btn_h'] / t['btn_w']); pass
        width_mult=2 to make one twice as wide (Keep)."""
        t = self.t
        if not enabled:
            bg, fg, bd, chip_bg, chip_fg, chip_bd = (
                BASE["raise"], BASE["ink_fainter"], BASE["border_soft"],
                blend("#000000", BASE["bg"], 0.18), BASE["ink_fainter"], BASE["border_soft"])
        elif kind == "primary":
            bg, fg, bd = t["ac"], t["ac_on"], t["ac"]
            chip_bg, chip_fg, chip_bd = t["kbd_on_bg"], t["ac_on"], blend("#000000", t["ac"], 0.18)
        elif kind == "drop":
            # Destructive action: keycap is tinted with the drop palette, not the
            # affirmative accent, so it doesn't read like Keep.
            bg, fg, bd = BASE["panel"], BASE["ink_muted"], BASE["rail"]
            chip_bg = blend(BASE["drop_border"], BASE["bg"], 0.16)
            chip_bd = blend(BASE["drop_border"], BASE["bg"], 0.40)
            chip_fg = BASE["drop_ink"]
        else:
            bg, fg, bd = BASE["panel"], BASE["ink_muted"], BASE["rail"]
            chip_bg, chip_fg, chip_bd = t["kbd_bg"], t["ac"], t["kbd_bd"]

        W, H = t["btn_w"] * width_mult, t["btn_h"]
        r = round(H * 0.30)
        c = tk.Canvas(parent, width=W, height=H, bg=BASE["panel"], bd=0,
                      highlightthickness=0, cursor="arrow" if not enabled else "hand2")
        body = self._round_rect(c, 1, 1, W - 1, H - 1, r, fill=bg, outline=bd, width=1)

        lab_font, chip_font = self.font("ui", 12, "bold"), self.font("mono", 10, "bold")
        lab_w = lab_font.measure(text)
        chip_w = chip_font.measure(key) + 12
        chip_h = chip_font.metrics("linespace") + 4
        gap, cy = 8, H / 2
        x0 = (W - (lab_w + gap + chip_w)) / 2
        lab_id = c.create_text(x0, cy, text=text, fill=fg, font=lab_font, anchor="w")
        cx = x0 + lab_w + gap
        chip_box = self._round_rect(c, cx, cy - chip_h / 2, cx + chip_w, cy + chip_h / 2,
                                    4, fill=chip_bg, outline=chip_bd, width=1)
        c.create_text(cx + chip_w / 2, cy, text=key, fill=chip_fg, font=chip_font)

        if enabled:
            c.bind("<Button-1>", lambda e: command())

            def enter(_):
                if kind == "primary":
                    nb = blend("#ffffff", t["ac"], 0.10)
                    c.itemconfig(body, fill=nb, outline=nb)
                    c.itemconfig(chip_box, fill=blend("#000000", nb, 0.30))
                elif kind == "drop":
                    c.itemconfig(body, outline=BASE["drop_border"])
                    c.itemconfig(lab_id, fill=BASE["drop_ink"])
                    c.itemconfig(chip_box, fill=blend(BASE["drop_border"], BASE["bg"], 0.30))
                else:
                    c.itemconfig(body, outline=BASE["hair"])
                    c.itemconfig(lab_id, fill=BASE["ink"])

            def leave(_):
                c.itemconfig(body, fill=bg, outline=bd)
                c.itemconfig(lab_id, fill=fg)
                c.itemconfig(chip_box, fill=chip_bg)

            c.bind("<Enter>", enter)
            c.bind("<Leave>", leave)
        return c

    def _ghost_button(self, parent, text, key, command):
        t = self.t
        font = self.font("mono", 10, "bold")
        lab_w, hint_w = font.measure(text), font.measure(key)
        gap, padx = 6, 10
        H = font.metrics("linespace") + 10
        W = padx * 2 + lab_w + gap + hint_w
        c = tk.Canvas(parent, width=W, height=H, bg=BASE["panel"], bd=0,
                      highlightthickness=0, cursor="hand2")
        body = self._round_rect(c, 1, 1, W - 1, H - 1, round(H * 0.32),
                                fill=BASE["panel"], outline=BASE["rail"], width=1)
        cy = H / 2
        lab_id = c.create_text(padx, cy, text=text, fill=BASE["ink_muted"],
                               font=font, anchor="w")
        c.create_text(padx + lab_w + gap, cy, text=key, fill=BASE["ink_faint"],
                      font=font, anchor="w")
        c.bind("<Button-1>", lambda e: command())

        def enter(_):
            c.itemconfig(body, outline=t["ac"])
            c.itemconfig(lab_id, fill=t["ac"])

        def leave(_):
            c.itemconfig(body, outline=BASE["rail"])
            c.itemconfig(lab_id, fill=BASE["ink_muted"])

        c.bind("<Enter>", enter)
        c.bind("<Leave>", leave)
        return c

    # ======================================================================
    # Queue canvas rendering + drag-to-reorder.
    # ======================================================================
    def render_queue(self) -> None:
        c = self.qcanvas
        t = self.t
        c.delete("all")
        W = c.winfo_width() or SIDEBAR_W
        n = len(self.items)
        self.count_pill.configure(text=str(n))

        # progress (triaged this session)
        total = self.kept + self.dropped + n
        frac = ((self.kept + self.dropped) / total) if total else 0.0
        tw = max(0, self._prog_track.winfo_width())
        self.progress.configure(width=int(tw * frac))
        self.progress.place_configure(width=int(tw * frac))

        if n == 0:
            return

        row_h = t["row_h"]
        node_cx = 20
        node_c = t["node_c"]
        title_face = self.font("ui", 13 if self.density == "comfortable" else 12, "normal")
        title_font = tkfont.Font(family=self.ui_face,
                                 size=-(13 if self.density == "comfortable" else 12))
        mono_small = self.font("mono", 10)
        mono_type = self.font("mono", 9)
        num_font = self.font("mono", 10, "bold")

        # connecting rail (behind nodes)
        first_cy = 0 * row_h + node_c
        last_cy = (n - 1) * row_h + node_c
        if n > 1:
            c.create_line(node_cx, first_cy, node_cx, last_cy,
                          fill=t["qrail"], width=t["qrail_w"])

        for i, it in enumerate(self.items):
            top = i * row_h
            cy = top + node_c
            selected = (i == self.sel)
            dragging = self.drag and self.drag.get("active") and self.drag.get("from") == i

            if selected and not dragging:
                self._round_rect(c, 6, top + 2, W - 6, top + row_h - 2, 8, fill=t["sel_bg"], outline="")

            # node
            if selected:
                c.create_oval(node_cx - 15, cy - 15, node_cx + 15, cy + 15,
                              fill=t["glow"], outline="")
                c.create_oval(node_cx - 11, cy - 11, node_cx + 11, cy + 11,
                              fill=t["ac"], outline="")
                c.create_text(node_cx, cy, text=str(i + 1).zfill(2),
                              fill=t["ac_on"], font=num_font)
            else:
                c.create_oval(node_cx - 11, cy - 11, node_cx + 11, cy + 11,
                              fill=BASE["node"], outline=BASE["rail"])
                c.create_text(node_cx, cy, text=str(i + 1).zfill(2),
                              fill=BASE["ink_dim"], font=num_font)

            ink = BASE["ink"] if not dragging else BASE["ink_faint"]
            # title (clamp to 2 lines)
            tx = 44
            now_w = 40 if selected else 0
            avail = max(40, W - tx - 12 - now_w)
            lines = self._clamp_lines(it.title, title_font, avail, 2)
            ty = top + t["row_pt"]
            for ln in lines:
                c.create_text(tx, ty, text=ln, anchor="nw", fill=ink, font=title_font)
                ty += title_font.metrics("linespace")

            # NOW tag
            if selected and not dragging:
                nx2 = W - 12
                nw = mono_small.measure("NOW") + 10
                self._round_rect(c, nx2 - nw, top + t["row_pt"] - 1,
                                 nx2, top + t["row_pt"] + 15, 4, fill=t["now_bg"], outline="")
                c.create_text(nx2 - nw / 2, top + t["row_pt"] + 7, text="NOW",
                              fill=t["ac"], font=self.font("mono", 8, "bold"))

            # via + type
            my = ty + 3
            via_txt = f"via {it.via}" if it.via else "queued"
            via_col = t["ac"] if selected else BASE["ink_dim2"]
            c.create_text(tx, my, text=via_txt, anchor="nw", fill=via_col, font=mono_small)
            vw = mono_small.measure(via_txt)
            if it.itype:
                c.create_text(tx + vw + 8, my, text=it.itype.upper(), anchor="nw",
                              fill=BASE["ink_faint"], font=mono_type)

        # drag insertion line
        if self.drag and self.drag.get("active"):
            gap = self.drag.get("target", 0)
            gy = gap * row_h + 1
            c.create_line(8, gy, W - 8, gy, fill=t["ac"], width=2.5)

        c.configure(scrollregion=(0, 0, W, n * row_h))

    def _round_rect(self, c, x1, y1, x2, y2, r, **kw):
        return self._rounded_polygon(c, x1, y1, x2, y2, r, **kw)

    def _clamp_lines(self, text, font, width, max_lines):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if font.measure(trial) <= width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
                if len(lines) == max_lines:
                    break
        if len(lines) < max_lines and cur:
            lines.append(cur)
        # ellipsize last line if content remains
        joined = " ".join(lines)
        if font.measure(" ".join(words)) > font.measure(joined) and lines:
            last = lines[-1]
            while last and font.measure(last + "…") > width:
                last = last[:-1]
            lines[-1] = last.rstrip() + "…"
        return lines[:max_lines]

    def _row_at(self, y) -> int:
        return max(0, min(len(self.items) - 1, int(self.qcanvas.canvasy(y) // self.t["row_h"])))

    def _q_press(self, e):
        if not self.items or self.screen != "review":
            return
        idx = self._row_at(e.y)
        self.sel = idx
        self.drag = {"from": idx, "active": False, "y0": e.y, "target": idx}
        self.render_queue()
        self.render_main()

    def _q_motion(self, e):
        if not self.drag:
            return
        if not self.drag["active"] and abs(e.y - self.drag["y0"]) < 5:
            return
        self.drag["active"] = True
        y = self.qcanvas.canvasy(e.y)
        row_h = self.t["row_h"]
        gap = int((y + row_h / 2) // row_h)
        gap = max(0, min(len(self.items), gap))
        self.drag["target"] = gap
        self.qcanvas.configure(cursor="closedhand")
        self.render_queue()

    def _q_release(self, e):
        if not self.drag:
            return
        self.qcanvas.configure(cursor="arrow")
        if self.drag.get("active"):
            src = self.drag["from"]
            dst = self.drag["target"]
            it = self.items.pop(src)
            if dst > src:
                dst -= 1
            dst = max(0, min(len(self.items), dst))
            self.items.insert(dst, it)
            self.sel = dst
            self.drag = None
            self.render_queue()
            self.render_main()
            self.flash("Reordered")
        else:
            self.drag = None

    def _q_wheel(self, e):
        self.qcanvas.yview_scroll(-1 if e.delta > 0 else 1, "units")

    # ======================================================================
    # Main pane rendering.
    # ======================================================================
    def render_main(self) -> None:
        for w in self.head.winfo_children():
            w.destroy()
        for w in self.card.inner.winfo_children():
            w.destroy()
        for w in self.actionrow.winfo_children():
            w.destroy()

        if self.screen == "stats":
            self._render_stats()      # global view; works with an empty queue
        elif self.screen == "settings":
            self._render_settings()
        else:
            cur = self.current()
            self._render_actions(cur)
            if cur is None:
                self._render_empty()
            else:
                self._render_item(cur)

        # Wheel events land on whichever child is under the cursor, so rebind across the
        # subtree we just built and reset the view to the top for the new content.
        self.card.bind_wheel_to_children()
        self.card.canvas.yview_moveto(0)

    def _render_item(self, cur) -> None:
        t = self.t
        # header
        hpad = tk.Frame(self.head, bg=BASE["bg"])
        hpad.pack(fill="x", padx=t["head_padx"], pady=(t["head_pady"], t["head_pady"] - 6))
        chip = tk.Label(hpad, text=f"⤳ {cur.reason}", bg=t["reason_bg"], fg=t["ac"],
                        font=self.font("mono", 10, "bold"), padx=8, pady=3,
                        highlightthickness=1, highlightbackground=t["reason_bd"])
        chip.pack(anchor="w")
        tk.Label(hpad, text=cur.title, bg=BASE["bg"], fg=BASE["ink_bright"],
                 font=self.font("ui", t["title"], "bold"), justify="left",
                 wraplength=self._wrap()).pack(anchor="w", pady=(12, 0))
        meta = tk.Frame(hpad, bg=BASE["bg"])
        meta.pack(anchor="w", pady=(12, 0))
        self._meta_chip(meta, cur.via, t["ac"])
        for part, col in [(cur.itype.upper(), BASE["ink_dim"]), (cur.url, BASE["ink_faint"])]:
            if part:
                tk.Label(meta, text="·", bg=BASE["bg"], fg=BASE["hair"],
                         font=self.font("mono", 11)).pack(side="left", padx=8)
                self._meta_chip(meta, part, col)

        # card body
        inner = self.card.inner
        inner.configure(padx=0)
        pad = tk.Frame(inner, bg=BASE["bg"])
        pad.pack(fill="both", expand=True, padx=t["card_padx"], pady=t["card_pady"])

        # view switch
        sw = tk.Frame(pad, bg=BASE["bg"])
        sw.pack(fill="x", pady=(0, 14))
        if self.view == "graph":
            head_label = "Source outline"
        else:
            head_label = "Recap" if self._recap_path(cur) is not None else "Source · no recap yet"
        tk.Label(sw, text=head_label,
                 bg=BASE["bg"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10, "bold")).pack(side="left")
        seg = tk.Frame(sw, bg=BASE["raise"], highlightthickness=1, highlightbackground=BASE["border"])
        seg.pack(side="right")
        self._view_tab(seg, "Recap", "recap")
        self._view_tab(seg, "Outline  g", "graph")

        if self.view == "graph":
            self._render_graph(pad, cur)
        else:
            self._render_recap(pad, cur)

    def _wrap(self) -> int:
        w = self.main.winfo_width() if hasattr(self, "main") else 0
        if w < 50:
            w = 1120 - SIDEBAR_W
        return max(260, w - 2 * self.t["card_padx"])

    def _meta_chip(self, parent, text, color):
        tk.Label(parent, text=text, bg=BASE["bg"], fg=color,
                 font=self.font("mono", 11)).pack(side="left")

    def _view_tab(self, parent, label, value):
        t = self.t
        on = (self.view == value)
        cell = tk.Frame(parent, bg=(t["ac"] if on else BASE["raise"]))
        cell.pack(side="left", padx=2, pady=2)
        lab = tk.Label(cell, text=label, bg=cell["bg"],
                       fg=(t["ac_on"] if on else BASE["ink_dim"]),
                       font=self.font("mono", 11, "bold"), padx=12, pady=4)
        lab.pack()
        for w in (cell, lab):
            w.bind("<Button-1>", lambda e: self.set_view(value))

    # Feed items in the review queue are Backlog by definition (no recap yet), so
    # this resolves to None for them; it flips to the recap once a kept source has
    # been synced and RECAPS/<id>.md exists — and demo items (path=None) stay None.
    def _recap_path(self, cur) -> Path | None:
        if getattr(cur, "path", None) is None:
            return None
        p = RECAPS / f"{cur.path.stem}.md"
        return p if p.is_file() else None

    _PREVIEW_CAP = 10   # backlog previews stay previews: first N blocks, then an affordance

    def _render_blocks(self, parent, blocks, *, recap) -> None:
        """Stack parsed markdown blocks as frames — the idiom the card already uses."""
        t = self.t
        wrap = self._wrap() - 40
        for i, b in enumerate(blocks):
            kind = b["kind"]
            top = 16 if i == 0 else (14 if kind in ("h2", "h3") else 8)
            if kind in ("h2", "h3"):
                tk.Label(parent, text=b["text"], bg=BASE["raise"], fg=BASE["ink_bright"],
                         font=self.font("ui", t["recap"] + (3 if kind == "h2" else 1), "bold"),
                         justify="left", anchor="w", wraplength=wrap).pack(anchor="w", padx=20, pady=(top, 2))
            elif kind == "quote":
                row = tk.Frame(parent, bg=BASE["raise"])
                row.pack(fill="x", padx=20, pady=(top, 0))
                tk.Frame(row, bg=t["ac"], width=3).pack(side="left", fill="y")
                italic = tkfont.Font(family=self.ui_face, size=-t["recap"], slant="italic")
                tk.Label(row, text=b["text"], bg=BASE["raise"], fg=BASE["ink_muted"], font=italic,
                         justify="left", anchor="w", wraplength=wrap - 18).pack(side="left", anchor="w", padx=(12, 0))
            elif kind == "li":
                fg = t["ac"] if b.get("accent") else BASE["recap_ink"]
                tk.Label(parent, text="•  " + b["text"], bg=BASE["raise"], fg=fg,
                         font=self.font("ui", t["recap"]), justify="left", anchor="w",
                         wraplength=wrap - 16).pack(anchor="w", padx=(30, 20), pady=(top, 0))
            else:  # p
                fg = t["ac"] if b.get("accent") else BASE["recap_ink"]
                tk.Label(parent, text=b["text"], bg=BASE["raise"], fg=fg,
                         font=self.font("ui", t["recap"]), justify="left", anchor="w",
                         wraplength=wrap).pack(anchor="w", padx=20, pady=(top, 0))

    def _render_more(self, parent, hidden, cur) -> None:
        """Dim '… N more · open source' affordance below a capped backlog preview."""
        tk.Frame(parent, bg=BASE["border_soft"], height=1).pack(fill="x", padx=20, pady=(14, 0))
        clickable = getattr(cur, "path", None) is not None
        text = f"…  {hidden} more block{'s' if hidden != 1 else ''}"
        if clickable:
            text += "  ·  open source"
        lab = tk.Label(parent, text=text, bg=BASE["raise"], fg=BASE["ink_faint"],
                       font=self.font("mono", 10), cursor=("hand2" if clickable else ""))
        lab.pack(anchor="w", padx=20, pady=(8, 0))
        if clickable:
            lab.bind("<Button-1>", lambda e: self.open_source(cur))

    def _render_recap(self, pad, cur):
        t = self.t
        recap_path = self._recap_path(cur)
        # recap card
        card = tk.Frame(pad, bg=BASE["raise"], highlightthickness=1, highlightbackground=BASE["border"])
        card.pack(fill="x")
        shell = tk.Frame(card, bg=BASE["raise"])
        shell.pack(fill="x", expand=True)
        if t["vivid"]:
            tk.Frame(shell, bg=t["ac"], width=3).pack(side="left", fill="y")
        body = tk.Frame(shell, bg=BASE["raise"])
        body.pack(side="left", fill="x", expand=True)

        if recap_path is not None:
            # Synthesised recap present → render it whole.
            src = strip_frontmatter(recap_path.read_text(encoding="utf-8", errors="replace"))
            blocks = strip_masthead(parse_blocks(src.splitlines(), recap=True, join_wrapped=True))
            self._render_blocks(body, blocks, recap=True)
        else:
            # Backlog: a marked source preview, capped so it stays a preview.
            lines = [ln for ln in cur.summary.split("\n") if ln.strip()]
            blocks = strip_masthead(parse_blocks(lines, recap=False))
            shown = blocks[:self._PREVIEW_CAP]
            self._render_blocks(body, shown, recap=False)
            hidden = len(blocks) - len(shown)
            if hidden > 0:
                self._render_more(body, hidden, cur)
        tk.Frame(body, bg=BASE["raise"], height=16).pack(fill="x")

        # tags
        if cur.tags:
            tags = tk.Frame(pad, bg=BASE["bg"])
            tags.pack(fill="x", pady=(18, 0))
            for tg in cur.tags:
                tk.Label(tags, text=f"#{tg}", bg=BASE["node"], fg=BASE["ink_muted"],
                         font=self.font("mono", 11), padx=9, pady=4,
                         highlightthickness=1, highlightbackground=BASE["border"]).pack(side="left", padx=(0, 8))

        # wiki overlaps (real items: computed at /sync → muted note)
        block = tk.Frame(pad, bg=BASE["bg"])
        block.pack(fill="x", pady=(24, 0))
        if cur.overlaps:
            tk.Label(block, text=f"WILL TOUCH {len(cur.overlaps)} WIKI "
                     f"PAGE{'S' if len(cur.overlaps) != 1 else ''}",
                     bg=BASE["bg"], fg=BASE["ink_faint"],
                     font=self.font("mono", 10, "bold")).pack(anchor="w", pady=(0, 11))
            for o in cur.overlaps:
                row = tk.Frame(block, bg=BASE["sunk"], highlightthickness=1, highlightbackground=BASE["border_soft"])
                row.pack(fill="x", pady=(0, 8))
                rr = tk.Frame(row, bg=BASE["sunk"])
                rr.pack(fill="x", padx=14, pady=11)
                tk.Label(rr, text=o["page"], bg=BASE["sunk"], fg=t["ac"],
                         font=self.font("mono", 12)).pack(side="left")
                tk.Frame(rr, bg=BASE["rail"], width=1, height=14).pack(side="left", padx=12)
                tk.Label(rr, text=o["note"], bg=BASE["sunk"], fg=BASE["ink_dim"],
                         font=self.font("ui", 12), justify="left",
                         wraplength=self._wrap() - 220).pack(side="left")
        else:
            tk.Label(block, text="WIKI OVERLAPS", bg=BASE["bg"], fg=BASE["ink_faint"],
                     font=self.font("mono", 10, "bold")).pack(anchor="w", pady=(0, 8))
            tk.Label(block, text="Computed when this source is folded in at the next /sync.",
                     bg=BASE["bg"], fg=BASE["ink_dim2"], font=self.font("ui", 12)).pack(anchor="w")

        # stat line
        stats = [s for s in [
            f"queued {cur.queued}" if cur.queued else "",
            cur.length, (f"{cur.tokens} est." if cur.tokens else "")] if s]
        if stats:
            sr = tk.Frame(pad, bg=BASE["bg"])
            sr.pack(fill="x", pady=(24, 0))
            tk.Label(sr, text="     ".join(stats), bg=BASE["bg"], fg=BASE["ink_faint"],
                     font=self.font("mono", 10)).pack(anchor="w")

    def _render_graph(self, pad, cur):
        t = self.t
        # root node
        rootf = tk.Frame(pad, bg=BASE["bg"])
        rootf.pack(fill="x")
        dotc = tk.Canvas(rootf, width=14, height=14, bg=BASE["bg"], highlightthickness=0)
        dotc.create_oval(1, 1, 13, 13, fill=t["ac"], outline="")
        dotc.pack(side="left", padx=(0, 11))
        tk.Label(rootf, text=cur.title, bg=BASE["bg"], fg=BASE["ink_bright"],
                 font=self.font("ui", 14, "bold")).pack(side="left")
        badge_txt = cur.itype.upper() + (f" · {cur.length}" if cur.length else "")
        tk.Label(rootf, text=badge_txt, bg=BASE["raise"], fg=BASE["ink_dim"],
                 font=self.font("mono", 10, "bold"), padx=8, pady=3,
                 highlightthickness=1, highlightbackground=BASE["border"]).pack(side="left", padx=11)

        segs = cur.outline_segments()
        n = len(segs)
        heading = {
            "breakdown": f"BREAKDOWN · {n} SEGMENT{'S' if n != 1 else ''}",
            "sections": f"OUTLINE · {n} SECTION{'S' if n != 1 else ''}",
            "preview": f"PREVIEW · FIRST {n} LINE{'S' if n != 1 else ''}",
        }[cur.outline_kind()]
        # rows carry no locator number — just the node and its optional target
        self._branch(pad, heading,
                     [("", s.get("label", ""),
                       (f"↳ feeds {s['target']}" if s.get("target") else "")) for s in segs])

        if cur.overlaps:
            self._branch(pad, f"MAPS TO {len(cur.overlaps)} WIKI "
                         f"PAGE{'S' if len(cur.overlaps) != 1 else ''}",
                         [("", o["page"], o["note"]) for o in cur.overlaps], page_style=True)
        elif cur.tags:
            self._render_tags(pad, cur.tags)

    def _branch(self, parent, label, rows, page_style=False):
        t = self.t
        br = tk.Frame(parent, bg=BASE["bg"])
        br.pack(fill="x", pady=(16, 0))
        tk.Label(br, text=label, bg=BASE["bg"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10, "bold")).pack(anchor="w", padx=(36, 0), pady=(0, 2))
        rowswrap = tk.Frame(br, bg=BASE["bg"])
        rowswrap.pack(fill="x")
        rail = tk.Frame(rowswrap, bg=t["grail"], width=max(1, t["grail_w"]))
        rail.place(x=8, rely=0.0, relheight=1.0)
        for at, label_txt, note in rows:
            row = tk.Frame(rowswrap, bg=BASE["bg"])
            row.pack(fill="x", pady=4)
            dot = tk.Canvas(row, width=36, height=18, bg=BASE["bg"], highlightthickness=0)
            dot.create_oval(4, 5, 12, 13, fill=t["ac"], outline=t["glow"], width=3)
            dot.pack(side="left")
            txt = tk.Frame(row, bg=BASE["bg"])
            txt.pack(side="left", fill="x", expand=True)
            head = tk.Frame(txt, bg=BASE["bg"])
            head.pack(anchor="w", fill="x")
            if at:
                tk.Label(head, text=at, bg=BASE["bg"], fg=t["ac"],
                         font=self.font("mono", 12, "bold")).pack(side="left", padx=(0, 11))
            tk.Label(head, text=label_txt, bg=BASE["bg"],
                     fg=(t["ac"] if page_style else BASE["ink"]),
                     font=(self.font("mono", 12, "bold") if page_style else self.font("ui", 13)),
                     justify="left", wraplength=self._wrap() - 80).pack(side="left")
            if note:
                tk.Label(txt, text=note, bg=BASE["bg"], fg=BASE["ink_dim"],
                         font=(self.font("mono", 11) if not page_style else self.font("ui", 12)),
                         justify="left", wraplength=self._wrap() - 80).pack(anchor="w", pady=(4, 0))

    def _render_tags(self, parent, tags):
        """Tags as plain #tag chips laid out side by side — not a graph branch."""
        br = tk.Frame(parent, bg=BASE["bg"])
        br.pack(fill="x", pady=(16, 0))
        tk.Label(br, text="TAGS", bg=BASE["bg"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10, "bold")).pack(anchor="w", padx=(36, 0), pady=(0, 6))
        row = tk.Frame(br, bg=BASE["bg"])
        row.pack(anchor="w", padx=(36, 0))
        for tg in tags:
            tk.Label(row, text=f"#{tg}", bg=BASE["node"], fg=BASE["ink_muted"],
                     font=self.font("mono", 11), padx=9, pady=4,
                     highlightthickness=1, highlightbackground=BASE["border"]).pack(side="left", padx=(0, 8))

    def _render_actions(self, cur):
        has = cur is not None
        row = self.actionrow
        self._action_button(row, "Keep → sources", "k", "primary", self.do_keep,
                            enabled=has, width_mult=2).pack(side="left")
        tk.Frame(row, bg=BASE["border"], width=1, height=22).pack(side="left", padx=8)
        self._action_button(row, "Drop", "d", "drop", self.do_drop, enabled=has).pack(side="left", padx=(0, self.t["gap"]))
        self._action_button(row, "Skip", "→", "outline", self.do_skip, enabled=has).pack(side="left", padx=(0, self.t["gap"]))
        self._action_button(row, "Open URL", "o", "outline", self.open_url, enabled=has).pack(side="left")
        # undo far right
        self._action_button(row, "Undo", "u", "outline", self.do_undo,
                            enabled=self.undo_rec is not None).pack(side="right")

    def _render_empty(self):
        t = self.t
        wrap = tk.Frame(self.card.inner, bg=BASE["bg"])
        wrap.pack(fill="both", expand=True, pady=120)
        check = tk.Canvas(wrap, width=58, height=58, bg=BASE["bg"], highlightthickness=0)
        check.create_oval(3, 3, 55, 55, fill=blend(t["ac"], BASE["bg"], 0.10),
                          outline=blend(t["ac"], BASE["bg"], 0.28))
        check.create_text(29, 30, text="✓", fill=t["ac"], font=self.font("mono", 26))
        check.pack()
        tk.Label(wrap, text="Queue cleared", bg=BASE["bg"], fg=BASE["ink"],
                 font=self.font("ui", 18, "bold")).pack(pady=(14, 0))
        tk.Label(wrap, text="Everything kept is now in sources/ and will be folded in on the "
                 "next nightly /sync.", bg=BASE["bg"], fg=BASE["ink_dim"],
                 font=self.font("ui", 13), wraplength=360, justify="center").pack(pady=(8, 0))
        self._ghost_button(wrap, "Rescan feeds", "⇧r", self.do_rescan).pack(pady=(14, 0))

    # ======================================================================
    # Actions (real triage logic, preserved from the CLI/ttk version).
    # ======================================================================
    def _advance_after_remove(self, idx: int):
        self.items.pop(idx)
        if self.items:
            self.sel = min(idx, len(self.items) - 1)
        else:
            self.sel = 0
        self.render_queue()
        self.render_main()

    def do_keep(self):
        cur = self.current()
        if cur is None or self.screen != "review":
            return
        idx = self.sel
        if cur.path is not None:
            text = cur.path.read_text(encoding="utf-8", errors="replace")
            dest = brain_feed.place(text, cur.path.name, SOURCES, VAULT, check_review=False)
            item_id = cur.path.stem
            cur.path.unlink()
            ts = self._log_decision(cur.via, item_id, "keep")
            self.undo_rec = {"kind": "keep", "name": cur.path.name, "text": text,
                             "placed": dest, "item": cur, "idx": idx,
                             "decision_ts": ts, "item_id": item_id}
            self.flash(f"Kept → {dest.relative_to(VAULT)}")
        else:
            self.undo_rec = {"kind": "keep", "item": cur, "idx": idx, "placed": None}
            self.flash("Kept → sources/")
        self.kept += 1
        self._advance_after_remove(idx)

    def do_drop(self):
        cur = self.current()
        if cur is None or self.screen != "review":
            return
        idx = self.sel
        if cur.path is not None:
            text = cur.path.read_text(encoding="utf-8", errors="replace")
            item_id = cur.path.stem
            cur.path.unlink()
            ts = self._log_decision(cur.via, item_id, "drop")
            self.undo_rec = {"kind": "drop", "name": cur.path.name, "text": text,
                             "placed": None, "item": cur, "idx": idx,
                             "decision_ts": ts, "item_id": item_id}
        else:
            self.undo_rec = {"kind": "drop", "item": cur, "idx": idx, "placed": None}
        self.dropped += 1
        self.flash("Dropped")
        self._advance_after_remove(idx)

    def do_skip(self):
        """Non-destructive: leave the item queued, just advance."""
        if not self.items or self.screen != "review":
            return
        self.move(1)
        self.flash("Skipped — still queued")

    def do_undo(self):
        u = self.undo_rec
        if not u or self.screen != "review":
            return
        cur = u["item"]
        if cur.path is not None:
            if u["kind"] == "keep" and u.get("placed") and Path(u["placed"]).exists():
                Path(u["placed"]).unlink()
            cur.path.write_text(u["text"], encoding="utf-8")
            if u.get("decision_ts") is not None and u.get("item_id"):
                self._delete_decision(u["item_id"], u["decision_ts"])
        if u["kind"] == "keep":
            self.kept = max(0, self.kept - 1)
        else:
            self.dropped = max(0, self.dropped - 1)
        idx = min(u["idx"], len(self.items))
        self.items.insert(idx, cur)
        self.sel = idx
        self.undo_rec = None
        self.render_queue()
        self.render_main()
        self.flash(f"Undone — {cur.title[:32]} back in queue")

    def open_url(self):
        if self.screen != "review":
            return
        cur = self.current()
        if cur and cur.url:
            url = cur.url if "://" in cur.url else "https://" + cur.url
            try:
                subprocess.Popen(["open", url])
                self.flash(f"Opening {cur.url}")
            except Exception:
                self.flash("Could not open url")
        elif cur:
            self.flash("No url on this item")

    def open_source(self, cur):
        """Reveal the full raw source file behind a capped backlog preview."""
        path = getattr(cur, "path", None)
        if path is None:
            return
        try:
            subprocess.Popen(["open", str(path)])
            self.flash(f"Opening {path.name}")
        except Exception:
            self.flash("Could not open source")

    def do_rescan(self):
        self.reload(select_first=True, fresh_session=True)
        self.render_queue()
        self.render_main()
        n = len(self.items)
        self.flash(f"Rescanned — {n} item{'s' if n != 1 else ''} queued")

    def move(self, delta: int):
        if not self.items:
            return
        self.sel = max(0, min(len(self.items) - 1, self.sel + delta))
        self.render_queue()
        self.render_main()

    def set_view(self, v: str):
        if self.view != v:
            self.view = v
            self.render_main()

    def toggle_view(self):
        self.set_view("recap" if self.view == "graph" else "graph")

    # -- top-level screen (Review Queue ↔ Feed Stats) --------------------------
    def set_screen(self, s: str):
        if self.screen == s:
            return
        self.screen = s
        if s == "stats":
            self.refresh_stats()      # recompute from disk + db on open
        self.rebuild()                # re-highlight the top tabs + swap main pane

    def toggle_screen(self):
        self.set_screen("stats" if self.screen == "review" else "review")

    # -- sqlite connection lifecycle (lazy, cached on the app) -----------------
    def _db_conn(self):
        """Lazy cached connection. Returns None if it can't be opened — logging then
        silently no-ops, because triage must never crash on a db hiccup."""
        if self._db is None:
            try:
                self._db = brain_feed.db_connect(brain_feed.DB_PATH)
                self._db.execute("PRAGMA busy_timeout=3000")  # tolerate CLI contention
            except Exception:
                self._db = None
        return self._db

    def _log_decision(self, feed_id, item_id, action):
        con = self._db_conn()
        if con is None:
            return None
        try:
            ts = brain_feed.log_decision(con, feed_id, item_id, action)
            con.commit()
            self._stats_cache = None
            return ts
        except Exception:
            return None

    def _delete_decision(self, item_id, ts):
        con = self._db_conn()
        if con is None:
            return
        try:
            brain_feed.delete_decision(con, item_id, ts)
            con.commit()
            self._stats_cache = None
        except Exception:
            pass

    def _on_close(self):
        if self._db is not None:
            try:
                self._db.commit()
                self._db.close()
            except Exception:
                pass
        self.root.destroy()

    # -- feed stats screen -----------------------------------------------------
    def refresh_stats(self):
        """Recompute per-feed stats from disk + db. Called when the screen is opened."""
        try:
            con = self._db_conn()
            cfg = brain_feed.load_config(brain_feed.CONFIG)
            self._stats_cache = brain_feed.feed_stats(con, cfg) if con else []
        except Exception:
            self._stats_cache = []

    def _render_stats(self):
        t = self.t
        # header
        hpad = tk.Frame(self.head, bg=BASE["bg"])
        hpad.pack(fill="x", padx=t["head_padx"], pady=(t["head_pady"], t["head_pady"] - 6))
        tk.Label(hpad, text="Feed Stats", bg=BASE["bg"], fg=BASE["ink_bright"],
                 font=self.font("ui", t["title"], "bold")).pack(anchor="w")
        tk.Label(hpad, text="all feeds · keep-rate tracked going forward",
                 bg=BASE["bg"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10)).pack(anchor="w", pady=(4, 0))

        pad = tk.Frame(self.card.inner, bg=BASE["bg"])
        pad.pack(fill="both", expand=True, padx=t["card_padx"], pady=t["card_pady"])

        # -- per-feed table ----------------------------------------------------
        tk.Label(pad, text="PER-FEED", bg=BASE["bg"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10, "bold")).pack(anchor="w", pady=(0, 8))

        rows = self._stats_cache or []
        cols = [("FEED", "id", 22), ("ADAPTER", "adapter", 9), ("TRUST", "trust", 7),
                ("CAP", "cap", 5), ("SEEN", "total_seen", 6), ("TODAY", "today_seen", 7),
                ("QUEUED", "queued", 8), ("KEEP-RATE", "keep_rate", 11)]
        table = tk.Frame(pad, bg=BASE["raise"], highlightthickness=1,
                         highlightbackground=BASE["border"])
        table.pack(fill="x")
        hdr = tk.Frame(table, bg=BASE["raise"])
        hdr.pack(fill="x")
        for i, (label, _key, w) in enumerate(cols):
            tk.Label(hdr, text=label, bg=BASE["raise"], fg=BASE["ink_faint"],
                     font=self.font("mono", 10, "bold"), width=w, anchor="w",
                     padx=8, pady=8).grid(row=0, column=i, sticky="w")
        for row in rows:
            rf = tk.Frame(table, bg=BASE["raise"])
            rf.pack(fill="x")
            tk.Frame(rf, bg=BASE["border_soft"], height=1).pack(fill="x")
            line = tk.Frame(rf, bg=BASE["raise"])
            line.pack(fill="x")
            for i, (_label, key, w) in enumerate(cols):
                val = row[key]
                if key == "keep_rate":
                    text = "N/A" if val is None else f"{val * 100:.0f}%"
                    fg = BASE["ink_dim2"] if val is None else t["ac"]
                else:
                    text = str(val)
                    fg = BASE["ink"] if key == "id" else BASE["ink_muted"]
                tk.Label(line, text=text, bg=BASE["raise"], fg=fg,
                         font=self.font("mono", 11), width=w, anchor="w",
                         padx=8, pady=7).grid(row=0, column=i, sticky="w")

        if not rows:
            tk.Label(pad, text="No feeds configured (feeds.toml).", bg=BASE["bg"],
                     fg=BASE["ink_dim"], font=self.font("ui", 13)).pack(anchor="w", pady=24)

        note = tk.Frame(pad, bg=BASE["bg"])
        note.pack(fill="x", pady=(18, 0))
        tk.Label(note, text="WHY SOME SHOW N/A", bg=BASE["bg"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10, "bold")).pack(anchor="w", pady=(0, 6))
        tk.Label(note, text="Keep-rate is tracked going forward: a feed needs at least 10 "
                 "keep/drop decisions before a number is shown. Auto-trust feeds never "
                 "enter the review queue, so they stay N/A by design.",
                 bg=BASE["bg"], fg=BASE["ink_dim2"], font=self.font("ui", 12),
                 justify="left", wraplength=self._wrap()).pack(anchor="w")

        # -- new-source form (collapsed behind "+ Add source") ------------------
        self._render_new_source_form(pad)

    # -- new-source form -------------------------------------------------------
    def _render_new_source_form(self, parent):
        """A form on the stats screen with a TYPE selector that routes what a URL *is*:

        webpage → deposit one source straight into sources/ (render-via-brain-clip +
                  place, so the frontmatter is contract-valid; next /sync folds it in).
        rss/api → subscribe instead: append a [[feed]] block to feeds.toml via
                  brain_feed.append_feed — the daily feeder pulls it from then on.

        The card rebuilds in place when the type (or trust/mode) changes; shared field
        values are carried across rebuilds via _ns_collect/_ns_vals. It sits below the
        per-feed table, collapsed behind a "+ Add source" expander until needed."""
        holder = tk.Frame(parent, bg=BASE["bg"])
        holder.pack(fill="x", pady=(22, 0))
        self._ns_holder = holder
        self._ns_fill_holder()

    _NS_BLURB = {
        "webpage": "Clip a URL or jot a note straight into sources/ — the next /sync "
                   "folds it into the wiki.",
        "rss": "Subscribe to an RSS/Atom feed — appends a [[feed]] to feeds.toml; the "
               "daily feeder pulls new items from the next run.",
        "api": "Subscribe to a public JSON endpoint via a declarative mapping — appends "
               "a [[feed]] to feeds.toml; the daily feeder pulls new items.",
    }
    _NS_URL_HINT = {
        "webpage": "a web page to fetch, or a link to attach",
        "rss": "the RSS/Atom feed URL",
        "api": "the JSON endpoint URL (public, no auth)",
    }

    def _build_ns_card(self):
        for w in self._ns_holder.winfo_children():
            w.destroy()
        t = self.t
        kind = self._ns_kind
        vals = self._ns_vals
        self._ns_map = {}

        card = tk.Frame(self._ns_holder, bg=BASE["raise"], highlightthickness=1,
                        highlightbackground=BASE["border"])
        card.pack(fill="x")
        inner = tk.Frame(card, bg=BASE["raise"])
        inner.pack(fill="x", padx=18, pady=16)

        head = tk.Frame(inner, bg=BASE["raise"])
        head.pack(fill="x")
        tk.Label(head, text="NEW SOURCE", bg=BASE["raise"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10, "bold")).pack(side="left")
        self._segmented(head, [("webpage", "webpage"), ("rss", "rss"), ("api", "api")],
                        kind, self._ns_set_kind).pack(side="right")
        hide = tk.Label(head, text="hide ✕", bg=BASE["raise"], fg=BASE["ink_faint"],
                        font=self.font("mono", 9, "bold"), cursor="hand2")
        hide.pack(side="right", padx=(0, 12))
        hide.bind("<Button-1>", lambda e: self._ns_set_expanded(False))
        tk.Label(inner, text=self._NS_BLURB[kind], bg=BASE["raise"], fg=BASE["ink_dim2"],
                 font=self.font("ui", 12), justify="left",
                 wraplength=self._wrap() - 40).pack(anchor="w", pady=(3, 12))

        title_hint = ("optional — derived if left blank" if kind == "webpage"
                      else "optional — the feed's label; also derives the id")
        tags_hint = ("optional — comma-separated" if kind == "webpage"
                     else "optional — stamped on every pulled item")
        self._ns_title = self._form_entry(inner, "Title", title_hint,
                                          vals.get("title", ""))
        self._ns_url = self._form_entry(inner, "URL", self._NS_URL_HINT[kind],
                                        vals.get("url", ""))
        self._ns_tags = self._form_entry(inner, "Tags", tags_hint, vals.get("tags", ""))

        if kind in ("rss", "api"):
            self._ns_id = self._form_entry(
                inner, "Feed id",
                "optional — derived from title/URL; must be unique in feeds.toml",
                vals.get("fid", ""))
            self._ns_cap = self._form_entry(
                inner, "Daily cap",
                f"optional — items/day for this feed (default {self._default_cap()})",
                vals.get("cap", ""))
            trow = tk.Frame(inner, bg=BASE["raise"])
            trow.pack(fill="x", pady=(10, 0))
            tk.Label(trow, text="TRUST", bg=BASE["raise"], fg=BASE["ink_faint"],
                     font=self.font("mono", 9, "bold")).pack(side="left")
            self._segmented(trow, [("queue", "queue"), ("auto", "auto")],
                            self._ns_trust, self._ns_set_trust).pack(side="left",
                                                                     padx=(10, 0))
            tk.Label(inner, text="queue → items land in the review pen for triage; "
                     "auto → a trusted feed flows straight into sources/",
                     bg=BASE["raise"], fg=BASE["ink_fainter"],
                     font=self.font("mono", 9)).pack(anchor="w", pady=(3, 0))

        if kind == "api":
            tk.Label(inner, text="MAPPING", bg=BASE["raise"], fg=BASE["ink_faint"],
                     font=self.font("mono", 9, "bold")).pack(anchor="w", pady=(12, 0))
            tk.Label(inner, text="dotted dict paths into the JSON — see the commented "
                     "api examples in feeds.toml", bg=BASE["raise"],
                     fg=BASE["ink_fainter"],
                     font=self.font("mono", 9)).pack(anchor="w", pady=(2, 0))
            mrow = tk.Frame(inner, bg=BASE["raise"])
            mrow.pack(fill="x", pady=(8, 0))
            tk.Label(mrow, text="MODE", bg=BASE["raise"], fg=BASE["ink_faint"],
                     font=self.font("mono", 9, "bold")).pack(side="left")
            self._segmented(mrow, [("url", "url"), ("text", "text")],
                            self._ns_mode, self._ns_set_mode).pack(side="left",
                                                                   padx=(10, 0))
            tk.Label(inner, text="url → brain-clip fetches each item's link (like rss); "
                     "text → deposit body_field as the source (like email)",
                     bg=BASE["raise"], fg=BASE["ink_fainter"],
                     font=self.font("mono", 9)).pack(anchor="w", pady=(3, 0))
            map_fields = [
                ("items_path", "path to the item array — blank = the response IS the array"),
                ("url_field", "each item's link (provenance + dedup) — required in url mode"),
                ("title_field", "optional — each item's title"),
                ("guid_field", "optional — stable dedup key (falls back to url, then title)"),
                ("body_field", "inline text to deposit — required in text mode"),
                ("user_agent", "optional — override the default UA (some hosts 429 it)"),
            ]
            for key, hint in map_fields:
                self._ns_map[key] = self._form_entry(inner, key, hint,
                                                     vals.get(key, ""))

        if kind == "webpage":
            tk.Label(inner, text="TEXT", bg=BASE["raise"], fg=BASE["ink_faint"],
                     font=self.font("mono", 9, "bold")).pack(anchor="w", pady=(10, 0))
            tk.Label(inner, text="paste text for a note; leave blank to fetch the URL above",
                     bg=BASE["raise"], fg=BASE["ink_fainter"],
                     font=self.font("mono", 9)).pack(anchor="w", pady=(2, 4))
            body = tk.Text(inner, height=4, bg=BASE["sunk"], fg=BASE["ink"],
                           insertbackground=t["ac"], relief="flat", bd=0, wrap="word",
                           highlightthickness=1, highlightbackground=t["field_bd"],
                           highlightcolor=t["ac"], font=self.font("ui", 12), padx=10, pady=8)
            body.pack(fill="x")
            if vals.get("body"):
                body.insert("1.0", vals["body"])
            self._ns_body = body

        srow = tk.Frame(inner, bg=BASE["raise"])
        srow.pack(fill="x", pady=(12, 0))
        self._ns_status = tk.Label(srow, text="", bg=BASE["raise"], fg=BASE["ink_faint"],
                                   font=self.font("mono", 10), anchor="w", justify="left",
                                   wraplength=self._wrap() - 220)
        self._ns_status.pack(side="left", fill="x", expand=True)
        label = "Add to sources" if kind == "webpage" else "Add feed"
        self._ns_btn = self._simple_button(srow, label, self._submit_new_source)
        self._ns_btn.pack(side="right")

    def _segmented(self, parent, options, value, on_change):
        """The top-bar segment idiom as a reusable form/settings control.
        `options` is [(label, value)]; clicking a cell fires on_change(value)."""
        t = self.t
        seg = tk.Frame(parent, bg=BASE["raise"], highlightthickness=1,
                       highlightbackground=BASE["border"])
        for label, val in options:
            on = (val == value)
            cell = tk.Frame(seg, bg=(t["ac"] if on else BASE["raise"]))
            cell.pack(side="left", padx=2, pady=2)
            lab = tk.Label(cell, text=label, bg=cell["bg"],
                           fg=(t["ac_on"] if on else BASE["ink_dim"]),
                           font=self.font("mono", 11, "bold"), padx=12, pady=4)
            lab.pack()
            for w in (cell, lab):
                w.bind("<Button-1>", lambda e, v=val: on_change(v))
        return seg

    def _ns_collect(self) -> dict:
        """Snapshot the form's current field values so an in-place rebuild (type/trust/
        mode change) doesn't eat what the user already typed."""
        out = {}
        entries = {"title": "_ns_title", "url": "_ns_url", "tags": "_ns_tags",
                   "fid": "_ns_id", "cap": "_ns_cap"}
        for key, attr in entries.items():
            w = getattr(self, attr, None)
            try:
                if w is not None and w.winfo_exists():
                    out[key] = w.get().strip()
            except tk.TclError:
                pass
        for key, w in (getattr(self, "_ns_map", None) or {}).items():
            try:
                if w.winfo_exists():
                    out[key] = w.get().strip()
            except tk.TclError:
                pass
        w = getattr(self, "_ns_body", None)
        try:
            if w is not None and w.winfo_exists():
                out["body"] = w.get("1.0", "end").strip()
        except tk.TclError:
            pass
        return out

    def _ns_fill_holder(self):
        """Render the holder's current face: the form card, or the collapsed expander."""
        if self._ns_expanded:
            self._build_ns_card()
            return
        for w in self._ns_holder.winfo_children():
            w.destroy()
        self._simple_button(self._ns_holder, "＋  Add source",
                            lambda: self._ns_set_expanded(True),
                            canvas_bg=BASE["bg"]).pack(anchor="w")

    def _ns_set_expanded(self, on: bool):
        if self._ns_expanded != on:
            self._ns_expanded = on
            self._ns_rebuild()

    def _ns_rebuild(self):
        self._ns_vals = self._ns_collect()
        # The in-place rebuild momentarily shrinks the scroll canvas's inner frame,
        # which clamps the viewport to the top — snapshot and restore it.
        frac = self.card.canvas.yview()[0]
        self._ns_fill_holder()
        self.card.bind_wheel_to_children()   # fresh widgets need the wheel again
        self.card.inner.update_idletasks()
        self.card.canvas.configure(scrollregion=self.card.canvas.bbox("all"))
        self.card.canvas.yview_moveto(frac)

    def _ns_set_kind(self, kind):
        if self._ns_kind != kind:
            self._ns_kind = kind
            self._ns_rebuild()

    def _ns_set_trust(self, trust):
        if self._ns_trust != trust:
            self._ns_trust = trust
            self._ns_rebuild()

    def _ns_set_mode(self, mode):
        if self._ns_mode != mode:
            self._ns_mode = mode
            self._ns_rebuild()

    def _default_cap(self) -> int:
        try:
            return int(brain_feed.load_config(brain_feed.CONFIG)["default_cap"])
        except Exception:
            return brain_feed.DEFAULT_CAP

    def _form_entry(self, parent, label, hint, value=""):
        t = self.t
        tk.Label(parent, text=label.upper(), bg=BASE["raise"], fg=BASE["ink_faint"],
                 font=self.font("mono", 9, "bold")).pack(anchor="w", pady=(8, 3))
        e = tk.Entry(parent, bg=BASE["sunk"], fg=BASE["ink"], insertbackground=t["ac"],
                     relief="flat", bd=0, highlightthickness=1,
                     highlightbackground=t["field_bd"], highlightcolor=t["ac"],
                     font=self.font("ui", 12))
        e.pack(fill="x", ipady=6)
        if value:
            e.insert(0, value)
        if hint:
            tk.Label(parent, text=hint, bg=BASE["raise"], fg=BASE["ink_fainter"],
                     font=self.font("mono", 9)).pack(anchor="w", pady=(3, 0))
        return e

    def _simple_button(self, parent, text, command, canvas_bg=None):
        """A primary rounded button with no keyboard chip (for the form), drawn on the
        card's raised background so its corners blend; pass canvas_bg when the button
        sits on a different surface (e.g. the stats pane's plain bg)."""
        t = self.t
        font = self.font("ui", 12, "bold")
        W, H = font.measure(text) + 36, t["btn_h"]
        r = round(H * 0.30)
        bg, fg, bd = t["ac"], t["ac_on"], t["ac"]
        c = tk.Canvas(parent, width=W, height=H, bg=canvas_bg or BASE["raise"], bd=0,
                      highlightthickness=0, cursor="hand2")
        body = self._round_rect(c, 1, 1, W - 1, H - 1, r, fill=bg, outline=bd, width=1)
        lab = c.create_text(W / 2, H / 2, text=text, fill=fg, font=font)
        c.bind("<Button-1>", lambda e: command())

        def enter(_):
            nb = blend("#ffffff", t["ac"], 0.10)
            c.itemconfig(body, fill=nb, outline=nb)

        def leave(_):
            c.itemconfig(body, fill=bg, outline=bd)

        c.bind("<Enter>", enter)
        c.bind("<Leave>", leave)
        return c

    def _ns_set_status(self, msg, err=False):
        if getattr(self, "_ns_status", None) is None:
            return
        try:
            self._ns_status.configure(
                text=msg, fg=(BASE["drop_ink"] if err else BASE["ink_faint"]))
        except tk.TclError:
            pass                                  # form was torn down; nothing to update

    def _submit_new_source(self):
        if getattr(self, "_creating", False):
            return
        if self._ns_kind in ("rss", "api"):
            self._submit_new_feed(self._ns_kind)
            return
        title = self._ns_title.get().strip()
        url = self._ns_url.get().strip()
        tags = parse_tags(self._ns_tags.get())
        body = self._ns_body.get("1.0", "end").strip()
        if not url and not body:
            self._ns_set_status("Enter a URL or write some text.", err=True)
            return
        if body:                                   # text present → a note (url optional)
            item = {"source_kind": "text", "type": "note", "title": title or None,
                    "url": url or None, "body": body}
        else:                                      # url only → fetch + extract the page
            item = {"source_kind": "url", "url": url, "title": title or None}
        self._creating = True
        self._ns_set_status("Creating… (fetching a URL can take a few seconds)")
        # brain-clip may fetch the network → run off the Tk thread; marshal the result
        # back with root.after so only the main thread touches widgets.
        threading.Thread(target=self._create_source_worker, args=(item, tags),
                         daemon=True).start()

    def _submit_new_feed(self, kind):
        """rss/api submit: validate, then append a [[feed]] block to feeds.toml.
        No network is touched — subscribing is a config edit; the feeder pulls later."""
        title = self._ns_title.get().strip()
        url = self._ns_url.get().strip()
        tags = parse_tags(self._ns_tags.get())
        fid = self._ns_id.get().strip()
        cap_raw = self._ns_cap.get().strip()
        if not url:
            self._ns_set_status("Enter the feed URL.", err=True)
            return
        fid = fid or brain_feed.slugify(title) or brain_feed.slugify(
            urllib.parse.urlsplit(url).netloc.removeprefix("www."))
        if not fid:
            self._ns_set_status("Enter a title or a feed id.", err=True)
            return
        n = None
        if cap_raw:
            try:
                n = int(cap_raw)
                if n < 0:
                    raise ValueError
            except ValueError:
                self._ns_set_status("Daily cap must be a whole number ≥ 0.", err=True)
                return
        feed = {"id": fid, "adapter": kind, "url": url, "trust": self._ns_trust,
                "n": n, "tags": tags, "title": title or None}
        if kind == "api":
            mapping = {k: w.get().strip() for k, w in self._ns_map.items()}
            if self._ns_mode == "url" and not mapping.get("url_field"):
                self._ns_set_status("url mode needs url_field — each item's link.",
                                    err=True)
                return
            if self._ns_mode == "text" and not mapping.get("body_field"):
                self._ns_set_status("text mode needs body_field — the text to deposit.",
                                    err=True)
                return
            feed.update(mapping)
            if self._ns_mode != "url":       # url is the adapter default; keep toml lean
                feed["mode"] = self._ns_mode
        try:
            brain_feed.append_feed(brain_feed.CONFIG, feed)
        except Exception as e:               # duplicate id / unwritable file / bad toml
            self._ns_set_status(f"Failed: {e}", err=True)
            return
        self._ns_vals = {}                   # clear the form on success
        self.refresh_stats()                 # the new feed shows up in the table below
        self.rebuild()                       # sidebar "feeds: N active" count too
        self.flash(f"Subscribed → feeds.toml · {fid}")

    def _create_source_worker(self, item, tags):
        try:
            proposed, content, stderr = brain_feed.render_via_clip(item)
            if not content:
                msg = ((stderr or "").strip().splitlines()[-1:] or ["render failed"])[0]
                self.root.after(0, lambda: self._finish_create(None, msg))
                return
            content = inject_tags(content, tags)
            dest = brain_feed.place(content, proposed, SOURCES, VAULT)
        except Exception as e:                     # subprocess/timeout/write failure
            err = str(e)
            self.root.after(0, lambda: self._finish_create(None, err))
            return
        self.root.after(0, lambda: self._finish_create(dest, None))

    def _finish_create(self, dest, err):
        self._creating = False
        if dest is None:
            self._ns_set_status(f"Failed: {(err or 'unknown error')[:120]}", err=True)
            return
        self.flash(f"Created → {dest.relative_to(VAULT)}")
        self._ns_vals = {}                         # don't resurrect the submitted values
        if self.screen == "stats":                 # refresh the pane → clears the form
            self.refresh_stats()
            self.render_main()

    # -- settings screen ---------------------------------------------------------
    def _render_settings(self):
        """Global config in one place: the feeder's default daily cap (written back
        into feeds.toml in place) and the appearance options (persisted to the
        gitignored .brain/gui-prefs.json; applied live via a full rebuild)."""
        t = self.t
        hpad = tk.Frame(self.head, bg=BASE["bg"])
        hpad.pack(fill="x", padx=t["head_padx"], pady=(t["head_pady"], t["head_pady"] - 6))
        tk.Label(hpad, text="Settings", bg=BASE["bg"], fg=BASE["ink_bright"],
                 font=self.font("ui", t["title"], "bold")).pack(anchor="w")
        tk.Label(hpad, text="feeder config lives in feeds.toml · appearance in "
                 ".brain/gui-prefs.json", bg=BASE["bg"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10)).pack(anchor="w", pady=(4, 0))

        pad = tk.Frame(self.card.inner, bg=BASE["bg"])
        pad.pack(fill="both", expand=True, padx=t["card_padx"], pady=t["card_pady"])

        # -- feeder: the global daily cap ---------------------------------------
        card = tk.Frame(pad, bg=BASE["raise"], highlightthickness=1,
                        highlightbackground=BASE["border"])
        card.pack(fill="x", pady=(0, 22))
        inner = tk.Frame(card, bg=BASE["raise"])
        inner.pack(fill="x", padx=18, pady=16)
        tk.Label(inner, text="FEEDER", bg=BASE["raise"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10, "bold")).pack(anchor="w")
        tk.Label(inner, text="The global daily cap bounds how many items each feed may "
                 "deposit per day, so no single feed floods the brain. A feed's own n "
                 "in feeds.toml overrides it.", bg=BASE["raise"], fg=BASE["ink_dim2"],
                 font=self.font("ui", 12), justify="left",
                 wraplength=self._wrap() - 40).pack(anchor="w", pady=(3, 4))
        self._set_cap_entry = self._form_entry(
            inner, "Global daily cap", "whole number ≥ 0 — saved to feeds.toml "
            "(default_cap)", str(self._default_cap()))
        srow = tk.Frame(inner, bg=BASE["raise"])
        srow.pack(fill="x", pady=(12, 0))
        self._set_status = tk.Label(srow, text="", bg=BASE["raise"],
                                    fg=BASE["ink_faint"], font=self.font("mono", 10),
                                    anchor="w", justify="left",
                                    wraplength=self._wrap() - 220)
        self._set_status.pack(side="left", fill="x", expand=True)
        self._simple_button(srow, "Save cap", self._save_default_cap).pack(side="right")

        # -- appearance -----------------------------------------------------------
        card2 = tk.Frame(pad, bg=BASE["raise"], highlightthickness=1,
                         highlightbackground=BASE["border"])
        card2.pack(fill="x")
        inner2 = tk.Frame(card2, bg=BASE["raise"])
        inner2.pack(fill="x", padx=18, pady=16)
        tk.Label(inner2, text="APPEARANCE", bg=BASE["raise"], fg=BASE["ink_faint"],
                 font=self.font("mono", 10, "bold")).pack(anchor="w")
        tk.Label(inner2, text="applies immediately · saved for the next launch",
                 bg=BASE["raise"], fg=BASE["ink_fainter"],
                 font=self.font("mono", 9)).pack(anchor="w", pady=(2, 6))
        rows = [
            ("ACCENT", "accent", [(k, k) for k in ACCENTS], self.accent),
            ("DENSITY", "density", [(k, k) for k in DENSITY], self.density),
            ("INTENSITY", "intensity", [("calm", "calm"), ("vivid", "vivid")],
             self.intensity),
        ]
        for label, key, options, current in rows:
            row = tk.Frame(inner2, bg=BASE["raise"])
            row.pack(fill="x", pady=(8, 0))
            tk.Label(row, text=label, bg=BASE["raise"], fg=BASE["ink_faint"],
                     font=self.font("mono", 9, "bold"), width=10,
                     anchor="w").pack(side="left")
            self._segmented(row, options, current,
                            lambda v, k=key: self._set_pref(k, v)).pack(side="left")

    def _settings_set_status(self, msg, err=False):
        try:
            self._set_status.configure(
                text=msg, fg=(BASE["drop_ink"] if err else BASE["ink_faint"]))
        except (AttributeError, tk.TclError):
            pass                                  # pane was torn down; nothing to update

    def _save_default_cap(self):
        raw = self._set_cap_entry.get().strip()
        try:
            cap = int(raw)
            if cap < 0:
                raise ValueError
        except ValueError:
            self._settings_set_status("Cap must be a whole number ≥ 0.", err=True)
            return
        try:
            brain_feed.set_default_cap(brain_feed.CONFIG, cap)
        except Exception as e:                    # unwritable / unparseable feeds.toml
            self._settings_set_status(f"Failed: {e}", err=True)
            return
        self._stats_cache = None                  # the stats CAP column derives from it
        self._settings_set_status(f"Saved — feeds without their own n now cap at "
                                  f"{cap}/day.")
        self.flash(f"default_cap = {cap} → feeds.toml")

    def _set_pref(self, key, value):
        if getattr(self, key) == value:
            return
        setattr(self, key, value)
        save_prefs({"accent": self.accent, "density": self.density,
                    "intensity": self.intensity})
        self.rebuild()                            # re-theme in place; stays on Settings

    # -- toast -----------------------------------------------------------------
    def flash(self, msg: str):
        self.toast.configure(text=msg, bg=self.t["ac"], fg=self.t["ac_on"])
        self.root.update_idletasks()
        rw, rh = self.root.winfo_width(), self.root.winfo_height()
        tw, th = self.toast.winfo_reqwidth(), self.toast.winfo_reqheight()
        margin = self.t["head_padx"] - 6                   # match the pane's right inset
        self.toast.place(x=rw - tw - margin,               # bottom-right corner
                         y=rh - self.t["bar_h"] - th - 12)  # just above the action bar
        if self._toast_after:
            self.root.after_cancel(self._toast_after)
        self._toast_after = self.root.after(1600, self.toast.place_forget)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Brain Feed review queue (desktop)")
    ap.add_argument("--demo", action="store_true",
                    help="showcase with 3 seeded items (no filesystem writes)")
    args = ap.parse_args(argv)

    root = tk.Tk()
    ReviewApp(root, demo=args.demo)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
