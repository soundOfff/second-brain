"""Tests for the "new source" form added to the Feed Stats screen (brain-feed-gui.py).

Two layers:
  * inject_tags() — the pure frontmatter helper (no Tk).
  * the create flow — construct the app headless, fill the form, deposit into a temp
    sources/ with a canned render (no network/subprocess), and assert what lands.

The GUI's brain-clip render and file threading are stubbed so the test is deterministic
and never touches the real vault. Mechanical only, no LLM — consistent with ADR-0001.

Run:  python3 -m unittest discover -s bin/tests -t bin -v
"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_GUI_PY = Path(__file__).resolve().parent.parent / "brain-feed-gui.py"
_spec = importlib.util.spec_from_file_location("brain_feed_gui_under_test", _GUI_PY)
gui = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gui)
bf = gui.brain_feed


class InjectTags(unittest.TestCase):
    def test_appends_tags_line(self):
        src = "---\nid: x\ntitle: X\n---\n\nbody\n"
        out = gui.inject_tags(src, ["a", "b"])
        self.assertIn("tags: [a, b]", out)
        self.assertTrue(out.endswith("\n"))          # trailing newline preserved
        self.assertIn("\nbody\n", out)               # body untouched

    def test_noop_without_tags(self):
        src = "---\nid: x\n---\nbody"
        self.assertEqual(gui.inject_tags(src, []), src)

    def test_does_not_double_tag(self):
        src = "---\nid: x\ntags: [keep]\n---\nbody\n"
        self.assertEqual(gui.inject_tags(src, ["new"]), src)

    def test_ignores_bodyless_or_frontmatterless(self):
        self.assertEqual(gui.inject_tags("no frontmatter", ["a"]), "no frontmatter")
        self.assertEqual(gui.inject_tags("---\nid: x\nbody", ["a"]),
                         "---\nid: x\nbody")          # no closing fence → unchanged


class _SyncThread:
    """Stand-in for threading.Thread that runs the target inline, so the worker and its
    root.after() callback complete within the test (flushed by root.update())."""

    def __init__(self, target=None, args=(), daemon=None):
        self._target, self._args = target, args

    def start(self):
        if self._target:
            self._target(*self._args)


class CreateFlow(unittest.TestCase):
    def setUp(self):
        try:
            self.root = gui.tk.Tk()
        except gui.tk.TclError as e:                  # no display → skip UI tests
            self.skipTest(f"no Tk display: {e}")
        self.root.withdraw()

        self._tmp = tempfile.TemporaryDirectory()
        vault = Path(self._tmp.name)
        (vault / "sources").mkdir()
        self.sources = vault / "sources"

        # redirect the deposit target + db away from the real vault
        self._saved = {
            "gui.SOURCES": gui.SOURCES, "gui.VAULT": gui.VAULT,
            "bf.SOURCES": bf.SOURCES, "bf.VAULT": bf.VAULT, "bf.DB_PATH": bf.DB_PATH,
            "render": bf.render_via_clip, "Thread": gui.threading.Thread,
        }
        gui.SOURCES = bf.SOURCES = self.sources
        gui.VAULT = bf.VAULT = vault
        bf.DB_PATH = vault / ".brain" / "feed-state.db"
        (vault / ".brain").mkdir(exist_ok=True)
        gui.threading.Thread = _SyncThread

        self.last_item = {}

        def fake_render(item):
            self.last_item = item
            title = item.get("title") or "untitled"
            slug = "2026-07-01-" + title.lower().replace(" ", "-")
            content = (f"---\nid: {slug}\ntitle: {title}\n"
                       f"type: {item.get('type', 'article')}\ncaptured: 2026-07-01\n"
                       f"---\n\n{item.get('body', 'fetched body')}\n")
            return (f"sources/{slug}.md", content, "")

        bf.render_via_clip = fake_render

        self.app = gui.ReviewApp(self.root, demo=True)
        self.app._stats_cache = []
        self.app.screen = "stats"
        self.app.render_main()                        # builds the form widgets

    def tearDown(self):
        gui.SOURCES, gui.VAULT = self._saved["gui.SOURCES"], self._saved["gui.VAULT"]
        bf.SOURCES, bf.VAULT = self._saved["bf.SOURCES"], self._saved["bf.VAULT"]
        bf.DB_PATH = self._saved["bf.DB_PATH"]
        bf.render_via_clip = self._saved["render"]
        gui.threading.Thread = self._saved["Thread"]
        if getattr(self.app, "_db", None) is not None:
            self.app._db.close()                      # opened lazily by refresh_stats
        self.root.destroy()
        self._tmp.cleanup()

    def _pump(self):
        self.root.update()                            # flush after() callbacks

    def test_note_creates_source_with_tags(self):
        self.app._ns_title.insert(0, "My Note")
        self.app._ns_tags.insert(0, "alpha, beta")
        self.app._ns_body.insert("1.0", "a quick thought")
        self.app._submit_new_source()
        self._pump()

        files = list(self.sources.glob("*.md"))
        self.assertEqual(len(files), 1)
        text = files[0].read_text()
        self.assertIn("tags: [alpha, beta]", text)
        self.assertIn("a quick thought", text)
        self.assertEqual(self.last_item["source_kind"], "text")
        self.assertEqual(self.last_item["type"], "note")
        self.assertFalse(self.app._creating)          # guard released

    def test_url_only_is_a_url_clip(self):
        self.app._ns_url.insert(0, "https://example.com/post")
        self.app._submit_new_source()
        self._pump()

        self.assertEqual(len(list(self.sources.glob("*.md"))), 1)
        self.assertEqual(self.last_item["source_kind"], "url")
        self.assertEqual(self.last_item["url"], "https://example.com/post")

    def test_empty_form_is_rejected(self):
        self.app._submit_new_source()
        self._pump()
        self.assertEqual(list(self.sources.glob("*.md")), [])
        self.assertIn("Enter a URL", self.app._ns_status.cget("text"))
        self.assertFalse(self.app._creating)

    def test_render_failure_reports_and_writes_nothing(self):
        bf.render_via_clip = lambda item: (None, None, "boom: could not fetch")
        self.app._ns_url.insert(0, "https://dead.example/x")
        self.app._submit_new_source()
        self._pump()
        self.assertEqual(list(self.sources.glob("*.md")), [])
        self.assertIn("Failed", self.app._ns_status.cget("text"))
        self.assertFalse(self.app._creating)


if __name__ == "__main__":
    unittest.main()
