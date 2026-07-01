"""Tests for the generic `api` adapter in brain-feed.py (see docs/adr/0002).

Three layers, all mechanical / no LLM (ADR-0001):
  * resolve_path() / _scalar() — the pure dotted-path resolver + field coercion.
  * adapter_api() with a stubbed fetch_url — normalization, both modes, the guid
    fallback chain, and missing-field -> None, over canned JSON bytes.
  * one local-HTTP-server e2e — real fetch_url + json parse across three response
    shapes (nested envelope, flat array, top-level array), both modes.

Loads the hyphenated module via importlib (like the other feed tests).

Run:  python3 -m unittest discover -s bin/tests -t bin -v
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
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


# --- adapter_api() normalization over canned JSON (fetch_url stubbed) -------

class _StubFetch:
    """Patch bf.fetch_url to return canned bytes; capture the user_agent it was passed."""

    def __init__(self, payload):
        self.body = json.dumps(payload).encode()
        self.seen_ua = "<unset>"

    def __enter__(self):
        self._orig_fetch, self._orig_log = bf.fetch_url, bf.log

        def fake(url, timeout=30, user_agent=None):
            self.seen_ua = user_agent
            return self.body

        bf.fetch_url = fake
        bf.log = lambda *a, **k: None          # keep the real vault's feed.log untouched
        return self

    def __exit__(self, *exc):
        bf.fetch_url, bf.log = self._orig_fetch, self._orig_log


def _feed(**kw):
    base = {"id": "f", "adapter": "api", "url": "http://x"}
    base.update(kw)
    return base


class NormalizeUrlMode(unittest.TestCase):
    def test_nested_envelope_maps_every_field(self):
        payload = {"data": {"items": [
            {"id": "g1", "link": "https://e/1", "name": "One"},
            {"id": "g2", "link": "https://e/2", "name": "Two"},
        ]}}
        with _StubFetch(payload):
            out = bf.adapter_api(_feed(items_path="data.items", url_field="link",
                                       title_field="name", guid_field="id"))
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0], {"guid": "g1", "url": "https://e/1", "title": "One",
                                  "body": None, "type": None, "source_kind": "url"})

    def test_guid_falls_back_to_url_then_title(self):
        payload = [
            {"link": "https://e/3", "name": "Three"},   # no id -> guid = url
        ]
        with _StubFetch(payload):
            out = bf.adapter_api(_feed(items_path="", url_field="link",
                                       title_field="name", guid_field="id"))
        self.assertEqual(out[0]["guid"], "https://e/3")

    def test_url_mode_skips_items_with_no_url(self):
        payload = [{"name": "linkless"}]                 # url mode can't fetch without a link
        with _StubFetch(payload):
            out = bf.adapter_api(_feed(items_path="", url_field="link", title_field="name"))
        self.assertEqual(out, [])

    def test_missing_field_becomes_none(self):
        payload = [{"link": "https://e/x"}]              # no name -> title None
        with _StubFetch(payload):
            out = bf.adapter_api(_feed(items_path="", url_field="link", title_field="name",
                                       guid_field="id"))
        self.assertIsNone(out[0]["title"])
        self.assertEqual(out[0]["guid"], "https://e/x")  # falls through id->url

    def test_default_items_path_is_top_level_array(self):
        payload = [{"link": "https://e/1", "name": "One"}]
        with _StubFetch(payload):                        # no items_path given
            out = bf.adapter_api(_feed(url_field="link", title_field="name"))
        self.assertEqual(len(out), 1)

    def test_non_list_items_path_yields_nothing(self):
        with _StubFetch({"data": {"items": {"not": "a list"}}}):
            out = bf.adapter_api(_feed(items_path="data.items", url_field="link"))
        self.assertEqual(out, [])

    def test_user_agent_override_reaches_fetch(self):
        with _StubFetch([{"link": "https://e/1"}]) as s:
            bf.adapter_api(_feed(items_path="", url_field="link", user_agent="brain-bot/1"))
        self.assertEqual(s.seen_ua, "brain-bot/1")


class NormalizeTextMode(unittest.TestCase):
    def test_text_mode_deposits_body_and_keeps_url(self):
        payload = {"results": [
            {"guid": "a", "url": "https://e/a", "subject": "Sub", "text": "Hello body"},
        ]}
        with _StubFetch(payload):
            out = bf.adapter_api(_feed(items_path="results", url_field="url",
                                       title_field="subject", guid_field="guid",
                                       body_field="text", mode="text"))
        self.assertEqual(out[0], {"guid": "a", "url": "https://e/a", "title": "Sub",
                                  "body": "Hello body", "type": None, "source_kind": "text"})

    def test_text_mode_survives_without_a_url(self):
        payload = [{"guid": "only", "text": "body"}]      # no url_field value
        with _StubFetch(payload):
            out = bf.adapter_api(_feed(items_path="", guid_field="guid", body_field="text",
                                       mode="text"))
        self.assertEqual(len(out), 1)
        self.assertIsNone(out[0]["url"])
        self.assertEqual(out[0]["body"], "body")

    def test_item_with_no_stable_guid_is_dropped(self):
        payload = [{"text": "body only, nothing to dedup on"}]
        with _StubFetch(payload):
            out = bf.adapter_api(_feed(items_path="", body_field="text", mode="text"))
        self.assertEqual(out, [])                         # no guid/url/title -> skipped


# --- one real local-HTTP-server e2e across three response shapes -----------

_SHAPES = {
    "/nested": {"data": {"items": [
        {"id": "n1", "link": "https://e/n1", "name": "Nested", "text": "nested body"}]}},
    "/flat": {"results": [
        {"id": "f1", "link": "https://e/f1", "name": "Flat", "text": "flat body"}]},
    "/toplevel": [
        {"id": "t1", "link": "https://e/t1", "name": "Top", "text": "top body"}],
}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in _SHAPES:
            body = json.dumps(_SHAPES[self.path]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *a):
        pass  # keep the test run quiet


class E2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = HTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        # keep adapter error-logging off the real vault
        cls._tmp = tempfile.TemporaryDirectory()
        cls._saved = {"BRAIN": bf.BRAIN, "LOG": bf.LOG}
        bf.BRAIN = Path(cls._tmp.name)
        bf.LOG = bf.BRAIN / "feed.log"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()                 # release the listening socket (no ResourceWarning)
        bf.BRAIN, bf.LOG = cls._saved["BRAIN"], cls._saved["LOG"]
        cls._tmp.cleanup()

    def test_nested_envelope_url_mode(self):
        out = bf.adapter_api(_feed(url=self.base + "/nested", items_path="data.items",
                                   url_field="link", title_field="name", guid_field="id"))
        self.assertEqual([i["guid"] for i in out], ["n1"])
        self.assertEqual(out[0]["source_kind"], "url")
        self.assertIsNone(out[0]["body"])

    def test_flat_array_url_mode(self):
        out = bf.adapter_api(_feed(url=self.base + "/flat", items_path="results",
                                   url_field="link", title_field="name", guid_field="id"))
        self.assertEqual([i["url"] for i in out], ["https://e/f1"])

    def test_top_level_array_url_mode(self):
        out = bf.adapter_api(_feed(url=self.base + "/toplevel", items_path="",
                                   url_field="link", title_field="name", guid_field="id"))
        self.assertEqual([i["title"] for i in out], ["Top"])

    def test_text_mode_over_the_wire(self):
        out = bf.adapter_api(_feed(url=self.base + "/nested", items_path="data.items",
                                   url_field="link", title_field="name", guid_field="id",
                                   body_field="text", mode="text"))
        self.assertEqual(out[0]["source_kind"], "text")
        self.assertEqual(out[0]["body"], "nested body")

    def test_registered_in_adapters(self):
        self.assertIs(bf.ADAPTERS["api"], bf.adapter_api)


if __name__ == "__main__":
    unittest.main()
