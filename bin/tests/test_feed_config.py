"""Tests for the feeds.toml *write* helpers in brain-feed.py.

The desktop app's new-source form (rss/api subscribe) and Settings tab write config
through these: slugify(), feed_toml_block(), append_feed(), set_default_cap(). All
pure file/string work — no Tk, no network, no LLM (ADR-0001).

Run:  python3 -m unittest discover -s bin/tests -t bin -v
"""
from __future__ import annotations

import importlib.util
import tempfile
import tomllib
import unittest
from pathlib import Path

_FEED_PY = Path(__file__).resolve().parent.parent / "brain-feed.py"
_spec = importlib.util.spec_from_file_location("brain_feed_under_test_cfg", _FEED_PY)
bf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bf)


SAMPLE = """\
# Subscriptions — hand-written comments must survive every write.
default_cap = 5

# a comment between the global and the feeds
[[feed]]
id = "existing"
adapter = "rss"
url = "https://example.com/feed.xml"
trust = "queue"
# n = 99  (commented out — must never be touched)
"""


class Slugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bf.slugify("Simon Willison"), "simon-willison")

    def test_punctuation_collapses(self):
        self.assertEqual(bf.slugify("r/MachineLearning — top!"), "r-machinelearning-top")

    def test_nothing_survives(self):
        self.assertEqual(bf.slugify("™ ©"), "")


class FeedTomlBlock(unittest.TestCase):
    def test_rss_block_round_trips(self):
        feed = {"id": "my-feed", "adapter": "rss", "url": "https://x.com/f.xml",
                "trust": "auto", "n": 3, "tags": ["blog", "llm"], "title": "My Feed"}
        parsed = tomllib.loads(bf.feed_toml_block(feed))["feed"][0]
        self.assertEqual(parsed, {"id": "my-feed", "adapter": "rss",
                                  "url": "https://x.com/f.xml", "trust": "auto",
                                  "n": 3, "tags": ["blog", "llm"], "title": "My Feed"})

    def test_api_block_keeps_mapping_and_drops_empties(self):
        feed = {"id": "r-ml", "adapter": "api", "url": "https://api.example/x",
                "items_path": "data.children", "url_field": "data.url",
                "title_field": "", "guid_field": "data.id", "body_field": None,
                "mode": "text", "user_agent": "brain-feed/1.0", "trust": "queue",
                "n": None, "tags": [], "title": None}
        parsed = tomllib.loads(bf.feed_toml_block(feed))["feed"][0]
        self.assertEqual(parsed["items_path"], "data.children")
        self.assertEqual(parsed["mode"], "text")
        for absent in ("title_field", "body_field", "n", "tags", "title"):
            self.assertNotIn(absent, parsed)

    def test_strings_are_escaped(self):
        feed = {"id": "q", "adapter": "rss", "url": "https://x.com/?a=1&b=2",
                "title": 'He said "hi" \\ bye'}
        parsed = tomllib.loads(bf.feed_toml_block(feed))["feed"][0]
        self.assertEqual(parsed["title"], 'He said "hi" \\ bye')


class AppendFeed(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cfg = Path(self._tmp.name) / "feeds.toml"
        self.cfg.write_text(SAMPLE, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_appends_a_parseable_block(self):
        bf.append_feed(self.cfg, {"id": "new-one", "adapter": "api",
                                  "url": "https://api.example/items",
                                  "items_path": "results", "url_field": "link",
                                  "trust": "queue", "n": 2})
        cfg = bf.load_config(self.cfg)
        self.assertEqual([f["id"] for f in cfg["feeds"]], ["existing", "new-one"])
        new = cfg["feeds"][1]
        self.assertEqual(new["adapter"], "api")
        self.assertEqual(new["items_path"], "results")
        self.assertEqual(new["n"], 2)
        # comments + existing content untouched
        text = self.cfg.read_text()
        self.assertIn("hand-written comments must survive", text)
        self.assertIn("# n = 99", text)

    def test_duplicate_id_raises_and_leaves_file_alone(self):
        before = self.cfg.read_text()
        with self.assertRaises(ValueError):
            bf.append_feed(self.cfg, {"id": "existing", "adapter": "rss",
                                      "url": "https://y.com/f"})
        self.assertEqual(self.cfg.read_text(), before)

    def test_missing_id_or_adapter_raises(self):
        with self.assertRaises(ValueError):
            bf.append_feed(self.cfg, {"adapter": "rss", "url": "https://y.com/f"})
        with self.assertRaises(ValueError):
            bf.append_feed(self.cfg, {"id": "x", "url": "https://y.com/f"})

    def test_creates_a_missing_file(self):
        fresh = Path(self._tmp.name) / "fresh.toml"
        bf.append_feed(fresh, {"id": "a", "adapter": "rss", "url": "https://a.com/f"})
        self.assertEqual(bf.load_config(fresh)["feeds"][0]["id"], "a")


class SetDefaultCap(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cfg = Path(self._tmp.name) / "feeds.toml"
        self.cfg.write_text(SAMPLE, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_rewrites_only_the_cap_line(self):
        bf.set_default_cap(self.cfg, 9)
        self.assertEqual(bf.load_config(self.cfg)["default_cap"], 9)
        # every other line is byte-identical
        before = [l for l in SAMPLE.splitlines() if not l.startswith("default_cap")]
        after = [l for l in self.cfg.read_text().splitlines()
                 if not l.startswith("default_cap")]
        self.assertEqual(before, after)

    def test_missing_line_is_inserted_before_the_feeds(self):
        no_cap = "\n".join(l for l in SAMPLE.splitlines()
                           if not l.startswith("default_cap")) + "\n"
        self.cfg.write_text(no_cap, encoding="utf-8")
        bf.set_default_cap(self.cfg, 7)
        cfg = bf.load_config(self.cfg)
        self.assertEqual(cfg["default_cap"], 7)           # top-level, not feed.default_cap
        self.assertNotIn("default_cap", cfg["feeds"][0])

    def test_missing_file_is_created(self):
        fresh = Path(self._tmp.name) / "fresh.toml"
        bf.set_default_cap(fresh, 4)
        self.assertEqual(bf.load_config(fresh)["default_cap"], 4)

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            bf.set_default_cap(self.cfg, -1)
        self.assertEqual(bf.load_config(self.cfg)["default_cap"], 5)


if __name__ == "__main__":
    unittest.main()
