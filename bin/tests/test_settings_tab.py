"""Tests for the Settings screen (brain-feed-gui.py).

Covers the three things it owns:
  * the feeder's global daily cap — Save rewrites `default_cap` in feeds.toml in
    place (comments and feed blocks untouched);
  * appearance prefs — a change re-themes live and persists to .brain/gui-prefs.json,
    and a saved pref is loaded back on the next launch;
  * the SHORTCUTS reference card — rendered from the same table _bind_keys binds from.

Headless Tk, temp vault, no network, no LLM (ADR-0001).

Run:  python3 -m unittest discover -s bin/tests -t bin -v
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_GUI_PY = Path(__file__).resolve().parent.parent / "brain-feed-gui.py"
_spec = importlib.util.spec_from_file_location("brain_feed_gui_under_test_settings",
                                               _GUI_PY)
gui = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gui)
bf = gui.brain_feed

CFG = ('# keep this comment\ndefault_cap = 5\n\n[[feed]]\nid = "existing"\n'
       'adapter = "rss"\nurl = "https://example.com/f.xml"\ntrust = "queue"\n')


class SettingsTab(unittest.TestCase):
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
        self.cfg = vault / "feeds.toml"
        self.cfg.write_text(CFG, encoding="utf-8")

        self._saved = {
            "gui.SOURCES": gui.SOURCES, "gui.VAULT": gui.VAULT,
            "bf.SOURCES": bf.SOURCES, "bf.VAULT": bf.VAULT,
            "bf.DB_PATH": bf.DB_PATH, "bf.CONFIG": bf.CONFIG,
        }
        gui.SOURCES = bf.SOURCES = vault / "sources"
        gui.VAULT = bf.VAULT = vault
        bf.DB_PATH = vault / ".brain" / "feed-state.db"
        bf.CONFIG = self.cfg
        self.vault = vault

        self.app = gui.ReviewApp(self.root, demo=True)
        self.app.set_screen("settings")

    def tearDown(self):
        gui.SOURCES, gui.VAULT = self._saved["gui.SOURCES"], self._saved["gui.VAULT"]
        bf.SOURCES, bf.VAULT = self._saved["bf.SOURCES"], self._saved["bf.VAULT"]
        bf.DB_PATH, bf.CONFIG = self._saved["bf.DB_PATH"], self._saved["bf.CONFIG"]
        if getattr(self.app, "_db", None) is not None:
            self.app._db.close()
        self.root.destroy()
        self._tmp.cleanup()

    def test_cap_entry_is_prefilled_from_config(self):
        self.assertEqual(self.app._set_cap_entry.get(), "5")

    def test_save_rewrites_default_cap_in_place(self):
        self.app._set_cap_entry.delete(0, "end")
        self.app._set_cap_entry.insert(0, "9")
        self.app._save_default_cap()
        self.assertEqual(bf.load_config(self.cfg)["default_cap"], 9)
        text = self.cfg.read_text()
        self.assertIn("# keep this comment", text)             # comments survive
        self.assertIn('id = "existing"', text)                 # feeds survive
        self.assertIn("Saved", self.app._set_status.cget("text"))

    def test_non_numeric_cap_is_rejected(self):
        self.app._set_cap_entry.delete(0, "end")
        self.app._set_cap_entry.insert(0, "many")
        self.app._save_default_cap()
        self.assertEqual(bf.load_config(self.cfg)["default_cap"], 5)   # unchanged
        self.assertIn("whole number", self.app._set_status.cget("text"))

    def test_pref_change_applies_and_persists(self):
        self.app._set_pref("accent", "indigo")
        self.assertEqual(self.app.accent, "indigo")            # re-themed live
        saved = json.loads((self.vault / ".brain" / "gui-prefs.json").read_text())
        self.assertEqual(saved["accent"], "indigo")

    def test_prefs_load_on_next_launch(self):
        (self.vault / ".brain" / "gui-prefs.json").write_text(
            json.dumps({"accent": "emerald", "density": "compact",
                        "intensity": "vivid"}), encoding="utf-8")
        root2 = gui.tk.Tk()
        root2.withdraw()
        try:
            app2 = gui.ReviewApp(root2, demo=True)
            self.assertEqual((app2.accent, app2.density, app2.intensity),
                             ("emerald", "compact", "vivid"))
        finally:
            root2.destroy()

    def test_bad_pref_values_fall_back_to_defaults(self):
        (self.vault / ".brain" / "gui-prefs.json").write_text(
            json.dumps({"accent": "neon", "density": 7}), encoding="utf-8")
        root2 = gui.tk.Tk()
        root2.withdraw()
        try:
            app2 = gui.ReviewApp(root2, demo=True)
            self.assertEqual((app2.accent, app2.density, app2.intensity),
                             ("amber", "comfortable", "calm"))
        finally:
            root2.destroy()

    def _label_texts(self, w):
        out = []
        for c in w.winfo_children():
            if isinstance(c, gui.tk.Label):
                out.append(c.cget("text"))
            out.extend(self._label_texts(c))
        return out

    def test_shortcuts_card_matches_the_bindings(self):
        """SHORTCUTS is the single source of truth: every row must be both bound
        globally and listed (keycap + description) on the Settings card."""
        texts = self._label_texts(self.app.card.inner)
        self.assertIn("SHORTCUTS", texts)
        for cap, seqs, desc, _act in gui.ReviewApp.SHORTCUTS:
            for seq in seqs:
                self.assertTrue(self.root.bind_class("all", seq),
                                f"{seq} is not bound")
            self.assertIn(cap, texts)
            self.assertIn(desc, texts)


if __name__ == "__main__":
    unittest.main()
