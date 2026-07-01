"""Tests for the Feed Stats "Run feeder now" button (brain-feed-gui.py).

Covers the pieces that don't need a real feeder subprocess:
  * demo mode never starts a run;
  * the header renders the run affordance + status label, and the "running…"
    state survives a re-render;
  * _finish_feed_run success/error paths update state and the label in place,
    including when the stats pane isn't on screen (stale-widget guard);
  * _parse_run_summary distils the run's stdout into the status one-liner.

The worker itself (subprocess spawn) is deliberately not exercised: it would run
the real feeder against the real vault. Headless Tk, temp vault, no network,
no LLM (ADR-0001).

Run:  python3 -m unittest discover -s bin/tests -t bin -v
"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_GUI_PY = Path(__file__).resolve().parent.parent / "brain-feed-gui.py"
_spec = importlib.util.spec_from_file_location("brain_feed_gui_under_test_run", _GUI_PY)
gui = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gui)
bf = gui.brain_feed

CFG = ('default_cap = 5\n\n[[feed]]\nid = "existing"\nadapter = "rss"\n'
       'url = "https://example.com/f.xml"\ntrust = "queue"\n')


class RunFeederButton(unittest.TestCase):
    def setUp(self):
        try:
            self.root = gui.tk.Tk()
        except gui.tk.TclError as e:
            self.skipTest(f"no Tk display: {e}")
        self.root.withdraw()

        self._tmp = tempfile.TemporaryDirectory()
        vault = Path(self._tmp.name)
        (vault / "sources").mkdir()
        (vault / ".brain").mkdir()
        cfg = vault / "feeds.toml"
        cfg.write_text(CFG, encoding="utf-8")

        self._saved = {
            "gui.SOURCES": gui.SOURCES, "gui.VAULT": gui.VAULT,
            "bf.SOURCES": bf.SOURCES, "bf.VAULT": bf.VAULT,
            "bf.DB_PATH": bf.DB_PATH, "bf.CONFIG": bf.CONFIG,
        }
        gui.SOURCES = bf.SOURCES = vault / "sources"
        gui.VAULT = bf.VAULT = vault
        bf.DB_PATH = vault / ".brain" / "feed-state.db"
        bf.CONFIG = cfg

        self.app = gui.ReviewApp(self.root, demo=True)
        self.app.set_screen("stats")

    def tearDown(self):
        gui.SOURCES, gui.VAULT = self._saved["gui.SOURCES"], self._saved["gui.VAULT"]
        bf.SOURCES, bf.VAULT = self._saved["bf.SOURCES"], self._saved["bf.VAULT"]
        bf.DB_PATH, bf.CONFIG = self._saved["bf.DB_PATH"], self._saved["bf.CONFIG"]
        if getattr(self.app, "_db", None) is not None:
            self.app._db.close()
        self.root.destroy()
        self._tmp.cleanup()

    def test_demo_mode_never_runs(self):
        self.app.run_feeder()
        self.assertFalse(self.app._feed_running)
        self.assertIn("Demo", self.app.toast.cget("text"))

    def test_stats_header_renders_the_status_label(self):
        self.assertIn("01:30", self.app._feedrun_label.cget("text"))  # idle hint

    def test_running_state_survives_a_rerender(self):
        self.app._feed_running = True
        self.app.render_main()
        self.assertTrue(self.app._feedrun_label.cget("text").startswith("running"))

    def test_finish_success_updates_state_and_label(self):
        self.app._feed_running = True
        self.app._finish_feed_run("done: 1 deposited, 3 queued", None)
        self.assertFalse(self.app._feed_running)
        self.assertEqual(self.app._feedrun_msg, "done: 1 deposited, 3 queued")
        self.assertFalse(self.app._feedrun_err)
        self.assertEqual(self.app._feedrun_label.cget("text"),
                         "done: 1 deposited, 3 queued")

    def test_finish_error_marks_the_label(self):
        self.app._feed_running = True
        self.app._finish_feed_run(None, "boom")
        self.assertFalse(self.app._feed_running)
        self.assertTrue(self.app._feedrun_err)
        self.assertIn("boom", self.app._feedrun_label.cget("text"))
        self.assertIn("failed", self.app.toast.cget("text").lower())

    def test_finish_on_review_screen_hints_rescan_and_survives_stale_label(self):
        self.app.set_screen("review")          # tears the stats pane (and label) down
        self.app._feed_running = True
        self.app._finish_feed_run("done: 0 deposited, 2 queued", None)
        self.assertFalse(self.app._feed_running)
        self.assertEqual(self.app._feedrun_msg, "done: 0 deposited, 2 queued")
        self.assertIn("⇧R", self.app.toast.cget("text"))
        # ...and the summary shows once the stats screen is opened again
        self.app.set_screen("stats")
        self.assertEqual(self.app._feedrun_label.cget("text"),
                         "done: 0 deposited, 2 queued")

    def test_parse_run_summary(self):
        parse = gui.ReviewApp._parse_run_summary
        out = ("[2026-07-01] [existing] 0 deposited, 2 queued, 0 deferred, 1 skipped\n"
               "[2026-07-01] done: 0 deposited, 2 queued\n")
        self.assertEqual(parse(out), "done: 0 deposited, 2 queued")
        self.assertEqual(parse("[2026-07-01] no feeds configured (edit feeds.toml). "
                               "nothing to do.\n"),
                         "no feeds configured (edit feeds.toml). nothing to do.")
        self.assertEqual(parse(""), "done")


if __name__ == "__main__":
    unittest.main()
