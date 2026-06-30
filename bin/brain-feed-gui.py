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
  Skip  (s / →)   leave it queued, just advance  (non-destructive)
  Undo  (u)       reverse the last Keep or Drop (single level)
  Open  (o)       open the source url            Rescan (r)   reload the queue from disk
  ↑/↓             move selection                 g            toggle Recap / Outline
  click select    ·    drag to reorder (session) ·    q       quit

Locked theme — amber accent · comfortable density · calm intensity. No synthesis happens
here (same as the CLI): kept items wait for the 02:00 /sync.

  bin/brain-feed-gui.sh                 triage the real .brain/review/ queue
  bin/brain-feed-gui.sh --demo          showcase with 3 seeded items (no filesystem writes)

Needs Tk: `brew install python-tk@3.14` (matches your Homebrew python3).
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import time
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

    def outline_segments(self) -> list[dict]:
        """A genuine, data-driven decomposition for the Outline view."""
        if self.breakdown:
            return self.breakdown
        segs = []
        for i, para in enumerate(self.paragraphs()[:6], 1):
            words = para.split()
            label = " ".join(words[:11]) + ("…" if len(words) > 11 else "")
            segs.append({"at": f"¶{i}", "label": label, "target": ""})
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
        for w in (self.canvas, self.inner):
            w.bind("<MouseWheel>", self._wheel)
            w.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
            w.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _wheel(self, e):
        self.canvas.yview_scroll(-1 if e.delta > 0 else 1, "units")


# ============================================================================
# The app.
# ============================================================================
SIDEBAR_W = 296


class ReviewApp:
    def __init__(self, root: tk.Tk, demo: bool = False) -> None:
        self.root = root
        self.demo = demo
        # locked theme — no live selectors
        self.accent = "amber"
        self.density = "comfortable"
        self.intensity = "calm"

        self.items: list[Item] = []
        self.sel = 0
        self.view = "recap"               # 'recap' | 'graph'
        self.kept = 0
        self.dropped = 0
        self.undo_rec: dict | None = None  # single-level undo
        self.drag: dict | None = None
        self._toast_after = None

        root.title("Brain Feed — Review Queue")
        root.geometry("1120x740")
        root.minsize(900, 600)
        root.configure(bg=BASE["bg"])

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
        t["tag_bg"] = BASE["node"]
        t["vivid"] = vivid
        return t

    # -- key bindings ----------------------------------------------------------
    def _bind_keys(self) -> None:
        b = self.root.bind_all
        b("<k>", lambda e: self.do_keep())
        b("<Return>", lambda e: self.do_keep())
        b("<d>", lambda e: self.do_drop())
        b("<s>", lambda e: self.do_skip())
        b("<Right>", lambda e: self.do_skip())
        b("<o>", lambda e: self.open_url())
        b("<u>", lambda e: self.do_undo())
        b("<r>", lambda e: self.do_rescan())
        b("<g>", lambda e: self.toggle_view())
        b("<q>", lambda e: self.root.destroy())
        b("<Down>", lambda e: self.move(1))
        b("<Up>", lambda e: self.move(-1))

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

        body = tk.Frame(root_frame, bg=BASE["bg"])
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        self._build_main(body)

        # toast overlay (placed over the main pane, hidden until used)
        self.toast = tk.Label(self.root, text="", font=self.font("mono", 12, "bold"),
                              bg=self.t["ac"], fg=self.t["ac_on"], padx=16, pady=8)

        self.render_queue()
        self.render_main()

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
        self._action_button(frow, "Rescan", "r", "outline", self.do_rescan).pack(side="right")

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
    def _round_rect(c, x1, y1, x2, y2, r, **kw):
        """Draw a rounded rectangle on canvas c (smooth polygon). Returns item id."""
        r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
               x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
               x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return c.create_polygon(pts, smooth=True, **kw)

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
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
               x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return c.create_polygon(pts, smooth=True, **kw)

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
        if not self.items:
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

        cur = self.current()
        self._render_actions(cur)
        if cur is None:
            self._render_empty()
            return

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
        tk.Label(sw, text=("Source outline" if self.view == "graph" else "Recap preview"),
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

    def _render_recap(self, pad, cur):
        t = self.t
        # recap card
        card = tk.Frame(pad, bg=BASE["raise"], highlightthickness=1, highlightbackground=BASE["border"])
        card.pack(fill="x")
        if t["vivid"]:
            tk.Frame(card, bg=t["ac"], width=3).pack(side="left", fill="y")
        body = tk.Frame(card, bg=BASE["raise"])
        body.pack(fill="x", expand=True)
        tk.Label(body, text=cur.summary, bg=BASE["raise"], fg=BASE["recap_ink"],
                 font=self.font("ui", t["recap"]), justify="left",
                 wraplength=self._wrap() - 40).pack(anchor="w", padx=20, pady=16)

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
        self._branch(pad, f"BREAKDOWN · {len(segs)} SEGMENT{'S' if len(segs) != 1 else ''}",
                     [(s.get("at", ""), s.get("label", ""),
                       (f"↳ feeds {s['target']}" if s.get("target") else "")) for s in segs])

        if cur.overlaps:
            self._branch(pad, f"MAPS TO {len(cur.overlaps)} WIKI "
                         f"PAGE{'S' if len(cur.overlaps) != 1 else ''}",
                         [("", o["page"], o["note"]) for o in cur.overlaps], page_style=True)
        elif cur.tags:
            self._branch(pad, "TAGS", [("", f"#{tg}", "") for tg in cur.tags], page_style=True)

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

    def _render_actions(self, cur):
        has = cur is not None
        row = self.actionrow
        self._action_button(row, "Keep → sources", "k", "primary", self.do_keep,
                            enabled=has, width_mult=2).pack(side="left")
        tk.Frame(row, bg=BASE["border"], width=1, height=22).pack(side="left", padx=8)
        self._action_button(row, "Drop", "d", "drop", self.do_drop, enabled=has).pack(side="left", padx=(0, self.t["gap"]))
        self._action_button(row, "Skip", "s", "outline", self.do_skip, enabled=has).pack(side="left", padx=(0, self.t["gap"]))
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
        self._ghost_button(wrap, "Rescan feeds", "r", self.do_rescan).pack(pady=(14, 0))

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
        if cur is None:
            return
        idx = self.sel
        if cur.path is not None:
            text = cur.path.read_text(encoding="utf-8", errors="replace")
            dest = brain_feed.place(text, cur.path.name, SOURCES, VAULT, check_review=False)
            cur.path.unlink()
            self.undo_rec = {"kind": "keep", "name": cur.path.name, "text": text,
                             "placed": dest, "item": cur, "idx": idx}
            self.flash(f"Kept → {dest.relative_to(VAULT)}")
        else:
            self.undo_rec = {"kind": "keep", "item": cur, "idx": idx, "placed": None}
            self.flash("Kept → sources/")
        self.kept += 1
        self._advance_after_remove(idx)

    def do_drop(self):
        cur = self.current()
        if cur is None:
            return
        idx = self.sel
        if cur.path is not None:
            text = cur.path.read_text(encoding="utf-8", errors="replace")
            cur.path.unlink()
            self.undo_rec = {"kind": "drop", "name": cur.path.name, "text": text,
                             "placed": None, "item": cur, "idx": idx}
        else:
            self.undo_rec = {"kind": "drop", "item": cur, "idx": idx, "placed": None}
        self.dropped += 1
        self.flash("Dropped")
        self._advance_after_remove(idx)

    def do_skip(self):
        """Non-destructive: leave the item queued, just advance."""
        if not self.items:
            return
        self.move(1)
        self.flash("Skipped — still queued")

    def do_undo(self):
        u = self.undo_rec
        if not u:
            return
        cur = u["item"]
        if cur.path is not None:
            if u["kind"] == "keep" and u.get("placed") and Path(u["placed"]).exists():
                Path(u["placed"]).unlink()
            cur.path.write_text(u["text"], encoding="utf-8")
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
