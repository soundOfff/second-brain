"""Unit tests for the decision log + keep-rate helpers in brain-feed.py.

The module under test has a hyphen in its filename, so (like the GUI) we load it via
importlib. Each test runs against a fresh temp vault + sqlite db; the module's path
globals are pointed at the temp dir in setUp and restored in tearDown.

Run:  python3 -m unittest discover -s bin/tests -t bin -v
"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_FEED_PY = Path(__file__).resolve().parent.parent / "brain-feed.py"
_spec = importlib.util.spec_from_file_location("brain_feed_under_test", _FEED_PY)
bf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bf)

_PATH_GLOBALS = ("VAULT", "SOURCES", "BRAIN", "DB_PATH", "REVIEW_DIR", "CONFIG")


class _TempVault(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self._saved = {k: getattr(bf, k) for k in _PATH_GLOBALS}
        bf.VAULT = root
        bf.SOURCES = root / "sources"
        bf.BRAIN = root / ".brain"
        bf.DB_PATH = root / ".brain" / "feed-state.db"
        bf.REVIEW_DIR = root / ".brain" / "review"
        bf.CONFIG = root / "feeds.toml"
        self.con = bf.db_connect(bf.DB_PATH)

    def tearDown(self):
        self.con.close()
        for k, v in self._saved.items():
            setattr(bf, k, v)
        self._tmp.cleanup()

    def _log(self, feed, n, action, base_ts):
        for i in range(n):
            bf.log_decision(self.con, feed, f"{feed}-{action}-{i}", action, ts=base_ts + i)
        self.con.commit()


class TestDecisionsTable(_TempVault):
    def test_table_created_and_db_connect_idempotent(self):
        def has_table():
            return self.con.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='decisions'"
            ).fetchone() is not None

        self.assertTrue(has_table())
        bf.db_connect(bf.DB_PATH)  # second call must not error
        self.assertTrue(has_table())

    def test_log_decision_inserts_and_returns_ts(self):
        ts = bf.log_decision(self.con, "hn-ai", "2026-06-24-x", "keep", ts=1700)
        self.con.commit()
        self.assertEqual(ts, 1700)
        row = self.con.execute(
            "SELECT feed_id, item_id, action, timestamp FROM decisions"
        ).fetchone()
        self.assertEqual(row, ("hn-ai", "2026-06-24-x", "keep", 1700))

    def test_log_decision_defaults_ts_to_now(self):
        ts = bf.log_decision(self.con, "hn-ai", "y", "drop")
        self.con.commit()
        self.assertIsInstance(ts, int)
        self.assertGreater(ts, 1_000_000_000)

    def test_pk_collision_is_ignored(self):
        bf.log_decision(self.con, "hn-ai", "dup", "keep", ts=42)
        bf.log_decision(self.con, "hn-ai", "dup", "drop", ts=42)  # same (item_id, ts)
        self.con.commit()
        n = self.con.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        self.assertEqual(n, 1)


class TestDeleteDecision(_TempVault):
    def test_delete_removes_exact_row_only(self):
        bf.log_decision(self.con, "hn-ai", "item", "keep", ts=10)
        bf.log_decision(self.con, "hn-ai", "item", "keep", ts=20)  # same item, later ts
        self.con.commit()
        bf.delete_decision(self.con, "item", 10)
        self.con.commit()
        rows = self.con.execute(
            "SELECT timestamp FROM decisions WHERE item_id='item'"
        ).fetchall()
        self.assertEqual(rows, [(20,)])

    def test_delete_missing_is_noop(self):
        bf.delete_decision(self.con, "nope", 999)  # must not raise
        self.con.commit()
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM decisions").fetchone()[0], 0)


class TestComputeKeepRate(_TempVault):
    def test_below_threshold_returns_none(self):
        self._log("f", 9, "keep", 100)
        self.assertIsNone(bf.compute_keep_rate(self.con, "f"))

    def test_at_threshold_seven_keep_three_drop(self):
        self._log("f", 7, "keep", 100)
        self._log("f", 3, "drop", 200)
        self.assertAlmostEqual(bf.compute_keep_rate(self.con, "f"), 0.7)

    def test_all_keep_is_one(self):
        self._log("f", 10, "keep", 100)
        self.assertEqual(bf.compute_keep_rate(self.con, "f"), 1.0)

    def test_all_drop_is_zero(self):
        self._log("f", 10, "drop", 100)
        self.assertEqual(bf.compute_keep_rate(self.con, "f"), 0.0)

    def test_feed_isolation(self):
        self._log("f1", 10, "keep", 100)
        self._log("f2", 10, "drop", 100)
        self.assertEqual(bf.compute_keep_rate(self.con, "f1"), 1.0)
        self.assertEqual(bf.compute_keep_rate(self.con, "f2"), 0.0)

    def test_custom_min_decisions(self):
        self._log("f", 2, "keep", 100)
        self.assertIsNone(bf.compute_keep_rate(self.con, "f"))           # default 10
        self.assertEqual(bf.compute_keep_rate(self.con, "f", min_decisions=2), 1.0)


if __name__ == "__main__":
    unittest.main()
