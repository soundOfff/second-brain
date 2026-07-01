"""Tests for the "new source" form added to the Feed Stats screen (brain-feed-gui.py).

This layer covers the pure frontmatter helper inject_tags() — no Tk. The headless
create-flow tests are added on top of this in a follow-up commit.

Mechanical only, no LLM — consistent with ADR-0001.

Run:  python3 -m unittest discover -s bin/tests -t bin -v
"""
from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
