#!/usr/bin/env python3
"""Second Brain — brain-feed-gui: a desktop triage window for the pull-feeder queue.

The terminal `brain-feed review` walks .brain/review/ item-by-item asking k/d/s at a
prompt. This is the same triage as a native macOS window (Tkinter/ttk): the queue on the
left, the selected item's preview on the right, and Keep / Drop / Skip as buttons + one-
key shortcuts. It is a thin shell over brain-feed.py — all the real logic (where a kept
item lands, collision-safe naming) is reused from there, so behaviour stays single-source.

  Keep  (k / ⏎)   place the item into sources/  (collision-safe via brain-feed.place)
  Drop  (d)       delete the queued candidate   (the pen is gitignored scratch)
  Skip  (s / →)   leave it queued, advance
  Undo  (u)       reverse the last Keep or Drop (single level)
  ↑/↓             move selection      o  open url      r  rescan      q  quit

No synthesis happens here (same as the CLI): kept items wait for the 02:00 /sync. Run:
    bin/brain-feed-gui.sh        (or:  python3 bin/brain-feed-gui.py)
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

# --- reuse brain-feed.py (hyphenated filename → import via importlib) ----------
_FEED_PY = Path(__file__).resolve().parent / "brain-feed.py"
_spec = importlib.util.spec_from_file_location("brain_feed", _FEED_PY)
brain_feed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(brain_feed)

VAULT = brain_feed.VAULT
SOURCES = brain_feed.SOURCES
REVIEW_DIR = brain_feed.REVIEW_DIR

# macOS system-ish fonts (fall back gracefully if absent)
FONT_TITLE = ("Helvetica Neue", 16, "bold")
FONT_META = ("Helvetica Neue", 12)
FONT_BODY = ("Menlo", 12)
FONT_LIST = ("Helvetica Neue", 13)


class ReviewApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.queue: list[Path] = []
        self.kept = 0
        self.dropped = 0
        self.undo: dict | None = None  # last action, for single-level undo

        root.title("Brain Feed — Review Queue")
        root.geometry("1040x680")
        root.minsize(760, 480)

        self._build_layout()
        self._bind_keys()
        self.refresh_queue(select_first=True)

    # -- layout ----------------------------------------------------------------
    def _build_layout(self) -> None:
        outer = ttk.Frame(self.root, padding=(10, 8))
        outer.pack(fill="both", expand=True)

        # toolbar
        bar = ttk.Frame(outer)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Label(bar, text="Review queue", font=("Helvetica Neue", 14, "bold")).pack(side="left")
        ttk.Button(bar, text="Rescan (r)", command=lambda: self.refresh_queue(select_first=True)).pack(side="right")

        # split: queue list | detail
        paned = ttk.PanedWindow(outer, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned)
        self.tree = ttk.Treeview(left, show="tree", selectmode="browse")
        self.tree.tag_configure("via", foreground="#888")
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        paned.add(left, weight=1)

        right = ttk.Frame(paned)
        self.lbl_title = ttk.Label(right, text="", font=FONT_TITLE, wraplength=560, justify="left")
        self.lbl_title.pack(fill="x", anchor="w")
        self.lbl_meta = ttk.Label(right, text="", font=FONT_META, foreground="#666",
                                  wraplength=560, justify="left")
        self.lbl_meta.pack(fill="x", anchor="w", pady=(2, 8))
        self.body = ScrolledText(right, wrap="word", font=FONT_BODY, relief="flat",
                                 borderwidth=0, background="#fafafa", padx=10, pady=8)
        self.body.pack(fill="both", expand=True)
        self.body.configure(state="disabled")
        paned.add(right, weight=2)

        # action bar
        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(8, 0))
        self.btn_keep = ttk.Button(actions, text="✓ Keep → sources  (k)", command=self.do_keep)
        self.btn_keep.pack(side="left")
        self.btn_drop = ttk.Button(actions, text="✕ Drop  (d)", command=self.do_drop)
        self.btn_drop.pack(side="left", padx=6)
        self.btn_skip = ttk.Button(actions, text="↷ Skip  (s)", command=self.do_skip)
        self.btn_skip.pack(side="left")
        self.btn_open = ttk.Button(actions, text="Open URL  (o)", command=self.open_url)
        self.btn_open.pack(side="left", padx=6)
        self.btn_undo = ttk.Button(actions, text="Undo  (u)", command=self.do_undo, state="disabled")
        self.btn_undo.pack(side="left")

        self.status = ttk.Label(outer, text="", font=("Helvetica Neue", 11), foreground="#555")
        self.status.pack(fill="x", pady=(8, 0))

    def _bind_keys(self) -> None:
        b = self.root.bind_all
        b("<k>", lambda e: self.do_keep())
        b("<Return>", lambda e: self.do_keep())
        b("<d>", lambda e: self.do_drop())
        b("<s>", lambda e: self.do_skip())
        b("<Right>", lambda e: self.do_skip())
        b("<u>", lambda e: self.do_undo())
        b("<o>", lambda e: self.open_url())
        b("<r>", lambda e: self.refresh_queue(select_first=True))
        b("<q>", lambda e: self.root.destroy())
        b("<Down>", lambda e: self._move(1))
        b("<Up>", lambda e: self._move(-1))

    # -- queue state -----------------------------------------------------------
    def refresh_queue(self, select_first: bool = False) -> None:
        REVIEW_DIR.mkdir(parents=True, exist_ok=True)
        self.queue = sorted(REVIEW_DIR.glob("*.md"))
        self.tree.delete(*self.tree.get_children())
        for p in self.queue:
            fm, _ = self._read(p)
            title = fm.get("title", p.stem)
            via = fm.get("via", "")
            label = f"  {title}"
            iid = self.tree.insert("", "end", iid=str(p), text=label)
            if via:
                self.tree.insert("", "end", iid=str(p) + "::via", text=f"      via {via}", tags=("via",))
        if select_first and self.queue:
            self.tree.selection_set(str(self.queue[0]))
            self.tree.focus(str(self.queue[0]))
        self._render_selection()
        self._update_status()

    def _read(self, path: Path) -> tuple[dict, list[str]]:
        text = path.read_text(encoding="utf-8", errors="replace")
        return brain_feed._preview(text, n=500)

    def _current(self) -> Path | None:
        sel = self.tree.selection()
        if not sel:
            return None
        iid = sel[0].replace("::via", "")
        p = Path(iid)
        return p if p in self.queue else None

    def _on_select(self, _event=None) -> None:
        # snap a "via" sub-row selection back to its parent item row
        sel = self.tree.selection()
        if sel and sel[0].endswith("::via"):
            parent = sel[0].replace("::via", "")
            self.tree.selection_set(parent)
            return
        self._render_selection()

    def _render_selection(self) -> None:
        p = self._current()
        self.body.configure(state="normal")
        self.body.delete("1.0", "end")
        if p is None:
            self.lbl_title.configure(text="Review queue empty 🎉" if not self.queue else "")
            self.lbl_meta.configure(text="" if self.queue else "Nothing to triage. New queued items land here after `brain-feed run`.")
            self.body.configure(state="disabled")
            self._set_actions("disabled")
            return
        fm, body = self._read(p)
        self.lbl_title.configure(text=fm.get("title", p.stem))
        meta = []
        if fm.get("via"):
            meta.append(f"via {fm['via']}")
        if fm.get("type"):
            meta.append(fm["type"])
        if fm.get("url"):
            meta.append(fm["url"])
        self.lbl_meta.configure(text="   ·   ".join(meta))
        self.body.insert("end", "\n".join(body) if body else "(no body preview)")
        self.body.configure(state="disabled")
        self._set_actions("normal")

    def _set_actions(self, state: str) -> None:
        for b in (self.btn_keep, self.btn_drop, self.btn_skip, self.btn_open):
            b.configure(state=state)

    def _move(self, delta: int) -> None:
        if not self.queue:
            return
        cur = self._current()
        i = self.queue.index(cur) if cur in self.queue else 0
        i = max(0, min(len(self.queue) - 1, i + delta))
        target = str(self.queue[i])
        self.tree.selection_set(target)
        self.tree.focus(target)
        self.tree.see(target)

    def _advance_after_remove(self, removed: Path) -> None:
        """Keep selection sensible after a kept/dropped item leaves the queue."""
        try:
            i = self.queue.index(removed)
        except ValueError:
            i = 0
        self.refresh_queue()
        if self.queue:
            j = min(i, len(self.queue) - 1)
            self.tree.selection_set(str(self.queue[j]))
            self.tree.focus(str(self.queue[j]))
        else:
            self._render_selection()
        self._update_status()

    # -- actions ---------------------------------------------------------------
    def do_keep(self) -> None:
        p = self._current()
        if p is None:
            return
        text = p.read_text(encoding="utf-8", errors="replace")
        dest = brain_feed.place(text, p.name, SOURCES, VAULT, check_review=False)
        p.unlink()
        self.kept += 1
        self.undo = {"kind": "keep", "name": p.name, "text": text, "placed": dest}
        self.btn_undo.configure(state="normal")
        self._flash(f"kept → {dest.relative_to(VAULT)}")
        self._advance_after_remove(p)

    def do_drop(self) -> None:
        p = self._current()
        if p is None:
            return
        text = p.read_text(encoding="utf-8", errors="replace")
        p.unlink()
        self.dropped += 1
        self.undo = {"kind": "drop", "name": p.name, "text": text, "placed": None}
        self.btn_undo.configure(state="normal")
        self._flash("dropped")
        self._advance_after_remove(p)

    def do_skip(self) -> None:
        self._move(1)

    def do_undo(self) -> None:
        if not self.undo:
            return
        u = self.undo
        if u["kind"] == "keep" and u["placed"] and Path(u["placed"]).exists():
            Path(u["placed"]).unlink()
            self.kept -= 1
        elif u["kind"] == "drop":
            self.dropped -= 1
        (REVIEW_DIR / u["name"]).write_text(u["text"], encoding="utf-8")
        restored = REVIEW_DIR / u["name"]
        self.undo = None
        self.btn_undo.configure(state="disabled")
        self._flash(f"undo — {u['name']} back in queue")
        self.refresh_queue()
        self.tree.selection_set(str(restored))
        self.tree.focus(str(restored))

    def open_url(self) -> None:
        p = self._current()
        if p is None:
            return
        fm, _ = self._read(p)
        url = fm.get("url")
        if url:
            subprocess.Popen(["open", url])

    # -- status ----------------------------------------------------------------
    def _update_status(self) -> None:
        n = len(self.queue)
        self.status.configure(
            text=f"{n} queued   ·   {self.kept} kept   ·   {self.dropped} dropped this session"
            + ("   ·   kept items fold in at the 02:00 /sync" if self.kept else "")
        )

    def _flash(self, msg: str) -> None:
        self.status.configure(text=msg)
        self.root.after(1600, self._update_status)


def main() -> int:
    root = tk.Tk()
    try:
        ttk.Style().theme_use("aqua")  # native macOS look
    except tk.TclError:
        pass
    ReviewApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
