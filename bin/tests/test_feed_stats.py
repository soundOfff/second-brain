"""Unit tests for feed_stats() / _queued_counts() in brain-feed.py.

Loads the hyphenated module via importlib (like the GUI), points its path globals at a
fresh temp vault per test, writes a temp feeds.toml + review files + seeds the db, then
asserts the aggregation, the queued counting and the keep-rate/sort rules.

Run:  python3 -m unittest discover -s bin/tests -t bin -v
"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_FEED_PY = Path(__file__).resolve().parent.parent / "brain-feed.py"
_spec = importlib.util.spec_from_file_location("brain_feed_under_test_stats", _FEED_PY)
bf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bf)

_PATH_GLOBALS = ("VAULT", "SOURCES", "BRAIN", "DB_PATH", "REVIEW_DIR", "CONFIG")
DAY = "2026-06-30"


class _TempVault(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._saved = {k: getattr(bf, k) for k in _PATH_GLOBALS}
        bf.VAULT = self.root
        bf.SOURCES = self.root / "sources"
        bf.BRAIN = self.root / ".brain"
        bf.DB_PATH = self.root / ".brain" / "feed-state.db"
        bf.REVIEW_DIR = self.root / ".brain" / "review"
        bf.CONFIG = self.root / "feeds.toml"
        bf.REVIEW_DIR.mkdir(parents=True, exist_ok=True)
        self.con = bf.db_connect(bf.DB_PATH)

    def tearDown(self):
        self.con.close()
        for k, v in self._saved.items():
            setattr(bf, k, v)
        self._tmp.cleanup()

    # -- seeding helpers ----------------------------------------------------
    def write_feeds(self, toml: str):
        bf.CONFIG.write_text(toml, encoding="utf-8")
        return bf.load_config(bf.CONFIG)

    def queue_item(self, stem: str, via: str | None):
        fm = ["---", f"id: {stem}", "title: t", "type: article"]
        if via is not None:
            fm.append(f"via: {via}")
        fm.append("---")
        (bf.REVIEW_DIR / f"{stem}.md").write_text("\n".join(fm) + "\n\nbody\n",
                                                  encoding="utf-8")

    def seed_seen(self, feed: str, n: int):
        for i in range(n):
            bf.mark_seen(self.con, feed, f"{feed}-g{i}", None)
        self.con.commit()

    def seed_today(self, feed: str, n: int, day: str = DAY):
        for _ in range(n):
            bf.bump_day(self.con, feed, day)
        self.con.commit()

    def decide(self, feed: str, keeps: int, drops: int):
        ts = 1000
        for i in range(keeps):
            bf.log_decision(self.con, feed, f"{feed}-k{i}", "keep", ts=ts); ts += 1
        for i in range(drops):
            bf.log_decision(self.con, feed, f"{feed}-d{i}", "drop", ts=ts); ts += 1
        self.con.commit()


class TestAggregation(_TempVault):
    def test_basic_fields(self):
        cfg = self.write_feeds(
            '[[feed]]\nid="simon"\nadapter="rss"\ntrust="auto"\nn=3\n'
            '[[feed]]\nid="hn-ai"\nadapter="rss"\ntrust="queue"\nn=10\n'
        )
        self.seed_seen("simon", 5)
        self.seed_seen("hn-ai", 12)
        self.seed_today("hn-ai", 4)
        stats = {r["id"]: r for r in bf.feed_stats(self.con, cfg, day=DAY)}
        self.assertEqual(stats["simon"]["adapter"], "rss")
        self.assertEqual(stats["simon"]["trust"], "auto")
        self.assertEqual(stats["simon"]["cap"], 3)
        self.assertEqual(stats["simon"]["total_seen"], 5)
        self.assertEqual(stats["simon"]["today_seen"], 0)
        self.assertEqual(stats["hn-ai"]["total_seen"], 12)
        self.assertEqual(stats["hn-ai"]["today_seen"], 4)

    def test_cap_falls_back_to_default(self):
        cfg = self.write_feeds(
            'default_cap=7\n[[feed]]\nid="x"\nadapter="rss"\ntrust="queue"\n'
        )
        stats = bf.feed_stats(self.con, cfg, day=DAY)
        self.assertEqual(stats[0]["cap"], 7)

    def test_inactive_feed_has_zero_counts(self):
        cfg = self.write_feeds('[[feed]]\nid="quiet"\nadapter="rss"\ntrust="queue"\nn=5\n')
        r = bf.feed_stats(self.con, cfg, day=DAY)[0]
        self.assertEqual((r["total_seen"], r["today_seen"], r["queued"]), (0, 0, 0))
        self.assertIsNone(r["keep_rate"])


class TestQueuedCounting(_TempVault):
    def test_counts_by_via_and_excludes_missing_via(self):
        cfg = self.write_feeds(
            '[[feed]]\nid="hn-ai"\nadapter="rss"\ntrust="queue"\n'
            '[[feed]]\nid="arxiv"\nadapter="rss"\ntrust="queue"\n'
        )
        self.queue_item("a", "hn-ai")
        self.queue_item("b", "hn-ai")
        self.queue_item("c", "arxiv")
        self.queue_item("d", None)  # no via -> excluded from any configured feed
        stats = {r["id"]: r for r in bf.feed_stats(self.con, cfg, day=DAY)}
        self.assertEqual(stats["hn-ai"]["queued"], 2)
        self.assertEqual(stats["arxiv"]["queued"], 1)
        # and the no-via file is not silently attributed to a feed
        counts = bf._queued_counts()
        self.assertEqual(counts.get(""), 1)


class TestKeepRateAndSort(_TempVault):
    def test_populated_vs_na(self):
        cfg = self.write_feeds(
            '[[feed]]\nid="busy"\nadapter="rss"\ntrust="queue"\n'
            '[[feed]]\nid="new"\nadapter="rss"\ntrust="queue"\n'
        )
        self.decide("busy", keeps=7, drops=3)  # 10 -> 0.7
        self.decide("new", keeps=2, drops=1)   # 3  -> None
        stats = {r["id"]: r for r in bf.feed_stats(self.con, cfg, day=DAY)}
        self.assertAlmostEqual(stats["busy"]["keep_rate"], 0.7)
        self.assertIsNone(stats["new"]["keep_rate"])

    def test_sorted_rate_desc_then_na_last_id_stable(self):
        # config order deliberately scrambled to prove the sort
        cfg = self.write_feeds(
            '[[feed]]\nid="c-feed"\nadapter="rss"\ntrust="queue"\n'
            '[[feed]]\nid="d-feed"\nadapter="rss"\ntrust="queue"\n'
            '[[feed]]\nid="a-feed"\nadapter="rss"\ntrust="queue"\n'
            '[[feed]]\nid="b-feed"\nadapter="rss"\ntrust="queue"\n'
        )
        self.decide("a-feed", keeps=9, drops=1)  # 0.9
        self.decide("b-feed", keeps=5, drops=5)  # 0.5
        self.decide("d-feed", keeps=5, drops=5)  # 0.5 (tie with b-feed -> id breaks it)
        self.decide("c-feed", keeps=2, drops=1)  # None
        order = [r["id"] for r in bf.feed_stats(self.con, cfg, day=DAY)]
        self.assertEqual(order, ["a-feed", "b-feed", "d-feed", "c-feed"])

    def test_auto_trust_feed_with_seen_but_no_decisions_is_na(self):
        cfg = self.write_feeds('[[feed]]\nid="simon"\nadapter="rss"\ntrust="auto"\nn=3\n')
        self.seed_seen("simon", 40)
        r = bf.feed_stats(self.con, cfg, day=DAY)[0]
        self.assertEqual(r["total_seen"], 40)
        self.assertIsNone(r["keep_rate"])


class TestEmptyConfig(_TempVault):
    def test_empty_feeds_returns_empty_list(self):
        self.assertEqual(bf.feed_stats(self.con, {"feeds": []}, day=DAY), [])


if __name__ == "__main__":
    unittest.main()
