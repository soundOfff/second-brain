"""Tests for the generic `api` adapter in brain-feed.py (see docs/adr/0002).

This layer covers the pure building blocks — the dotted-path resolver and field
coercion — with no I/O. Normalization and the local-HTTP e2e are added on top of this
in a follow-up commit. Mechanical only, no LLM (ADR-0001).

Loads the hyphenated module via importlib (like the other feed tests).

Run:  python3 -m unittest discover -s bin/tests -t bin -v
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_FEED_PY = Path(__file__).resolve().parent.parent / "brain-feed.py"
_spec = importlib.util.spec_from_file_location("brain_feed_under_test_api", _FEED_PY)
bf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bf)


# --- the dotted-path resolver + scalar coercion (pure, no I/O) --------------

class ResolvePath(unittest.TestCase):
    def test_dotted_descends_nested_dicts(self):
        obj = {"a": {"b": {"c": "deep"}}}
        self.assertEqual(bf.resolve_path(obj, "a.b.c"), "deep")

    def test_single_key(self):
        self.assertEqual(bf.resolve_path({"a": {"b": 1}}, "a"), {"b": 1})

    def test_empty_path_is_identity(self):
        obj = [1, 2, 3]
        self.assertIs(bf.resolve_path(obj, ""), obj)          # "the response IS the array"

    def test_missing_key_is_none(self):
        self.assertIsNone(bf.resolve_path({"a": 1}, "x"))

    def test_traversing_into_a_non_dict_is_none(self):
        self.assertIsNone(bf.resolve_path({"a": 1}, "a.b"))   # a is an int, can't descend

    def test_lists_are_not_indexed(self):
        self.assertIsNone(bf.resolve_path([1, 2], "0"))       # no wildcards/indexing by design


class Scalar(unittest.TestCase):
    def test_strips_strings(self):
        self.assertEqual(bf._scalar("  hi \n"), "hi")

    def test_empty_string_is_none(self):
        self.assertIsNone(bf._scalar("   "))

    def test_none_is_none(self):
        self.assertIsNone(bf._scalar(None))

    def test_numbers_stringify(self):
        self.assertEqual(bf._scalar(42), "42")

    def test_containers_are_none(self):
        self.assertIsNone(bf._scalar({"a": 1}))
        self.assertIsNone(bf._scalar([1, 2]))


if __name__ == "__main__":
    unittest.main()
