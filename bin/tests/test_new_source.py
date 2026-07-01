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
        self.app._ns_expanded = True                  # form is collapsed by default
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


class FeedSubscribe(unittest.TestCase):
    """The form's rss/api types: instead of depositing a source, they append a
    [[feed]] block to feeds.toml. No network, no worker thread — a config edit."""

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
        self.cfg.write_text(
            'default_cap = 5\n\n[[feed]]\nid = "existing"\nadapter = "rss"\n'
            'url = "https://example.com/f.xml"\ntrust = "queue"\n', encoding="utf-8")

        self._saved = {
            "gui.SOURCES": gui.SOURCES, "gui.VAULT": gui.VAULT,
            "bf.SOURCES": bf.SOURCES, "bf.VAULT": bf.VAULT,
            "bf.DB_PATH": bf.DB_PATH, "bf.CONFIG": bf.CONFIG,
        }
        gui.SOURCES = bf.SOURCES = vault / "sources"
        gui.VAULT = bf.VAULT = vault
        bf.DB_PATH = vault / ".brain" / "feed-state.db"
        bf.CONFIG = self.cfg

        self.app = gui.ReviewApp(self.root, demo=True)
        self.app._stats_cache = []
        self.app.screen = "stats"
        self.app._ns_expanded = True                  # form is collapsed by default
        self.app.render_main()

    def tearDown(self):
        gui.SOURCES, gui.VAULT = self._saved["gui.SOURCES"], self._saved["gui.VAULT"]
        bf.SOURCES, bf.VAULT = self._saved["bf.SOURCES"], self._saved["bf.VAULT"]
        bf.DB_PATH, bf.CONFIG = self._saved["bf.DB_PATH"], self._saved["bf.CONFIG"]
        if getattr(self.app, "_db", None) is not None:
            self.app._db.close()
        self.root.destroy()
        self._tmp.cleanup()

    def _feeds(self):
        return bf.load_config(self.cfg)["feeds"]

    def test_form_collapsed_behind_expander_by_default(self):
        self.app._ns_expanded = False
        self.app.render_main()
        self.assertFalse(self.app._ns_title.winfo_exists())    # only the expander shows
        self.app._ns_set_expanded(True)
        self.assertTrue(self.app._ns_title.winfo_exists())     # expander builds the form
        self.app._ns_set_expanded(False)
        self.assertFalse(self.app._ns_title.winfo_exists())    # hide collapses it again

    def test_type_selector_swaps_the_fields(self):
        self.assertTrue(self.app._ns_body.winfo_exists())      # webpage: TEXT area
        self.app._ns_set_kind("rss")
        self.assertTrue(self.app._ns_id.winfo_exists())        # rss: feed id + cap
        self.assertEqual(self.app._ns_map, {})                 # …but no mapping
        self.app._ns_set_kind("yt")
        self.assertTrue(self.app._ns_id.winfo_exists())        # yt: feed id + cap too
        self.assertEqual(self.app._ns_map, {})                 # …and no mapping
        self.app._ns_set_kind("api")
        self.assertIn("items_path", self.app._ns_map)          # api: mapping fields

    def test_values_survive_a_type_switch(self):
        self.app._ns_title.insert(0, "Kept Title")
        self.app._ns_url.insert(0, "https://x.com/feed")
        self.app._ns_set_kind("rss")
        self.assertEqual(self.app._ns_title.get(), "Kept Title")
        self.assertEqual(self.app._ns_url.get(), "https://x.com/feed")

    def test_rss_subscribe_appends_feed(self):
        self.app._ns_set_kind("rss")
        self.app._ns_title.insert(0, "Simon Willison")
        self.app._ns_url.insert(0, "https://simonwillison.net/atom/everything/")
        self.app._ns_tags.insert(0, "blog, llm")
        self.app._ns_cap.insert(0, "3")
        self.app._submit_new_source()

        feeds = self._feeds()
        self.assertEqual(len(feeds), 2)
        new = feeds[1]
        self.assertEqual(new["id"], "simon-willison")          # derived from the title
        self.assertEqual(new["adapter"], "rss")
        self.assertEqual(new["trust"], "queue")                # the safe default
        self.assertEqual(new["n"], 3)
        self.assertEqual(new["tags"], ["blog", "llm"])
        self.assertEqual(new["title"], "Simon Willison")

    def test_feed_id_falls_back_to_the_url_host(self):
        self.app._ns_set_kind("rss")
        self.app._ns_url.insert(0, "https://www.example.com/feed.xml")
        self.app._submit_new_source()
        self.assertEqual(self._feeds()[1]["id"], "example-com")

    def test_missing_url_is_rejected(self):
        self.app._ns_set_kind("rss")
        self.app._ns_title.insert(0, "No URL")
        self.app._submit_new_source()
        self.assertEqual(len(self._feeds()), 1)
        self.assertIn("URL", self.app._ns_status.cget("text"))

    def test_duplicate_id_is_rejected(self):
        self.app._ns_set_kind("rss")
        self.app._ns_id.insert(0, "existing")
        self.app._ns_url.insert(0, "https://y.com/feed")
        self.app._submit_new_source()
        self.assertEqual(len(self._feeds()), 1)
        self.assertIn("already exists", self.app._ns_status.cget("text"))

    def test_api_url_mode_requires_url_field(self):
        self.app._ns_set_kind("api")
        self.app._ns_url.insert(0, "https://api.example/items")
        self.app._submit_new_source()
        self.assertEqual(len(self._feeds()), 1)
        self.assertIn("url_field", self.app._ns_status.cget("text"))

    def test_api_subscribe_writes_the_mapping(self):
        self.app._ns_set_kind("api")
        self.app._ns_title.insert(0, "r ML")
        self.app._ns_url.insert(0, "https://www.reddit.com/r/ML/top.json")
        self.app._ns_map["items_path"].insert(0, "data.children")
        self.app._ns_map["url_field"].insert(0, "data.url")
        self.app._ns_map["guid_field"].insert(0, "data.id")
        self.app._ns_map["user_agent"].insert(0, "brain-feed/1.0")
        self.app._submit_new_source()

        new = self._feeds()[1]
        self.assertEqual(new["adapter"], "api")
        self.assertEqual(new["items_path"], "data.children")
        self.assertEqual(new["url_field"], "data.url")
        self.assertEqual(new["guid_field"], "data.id")
        self.assertEqual(new["user_agent"], "brain-feed/1.0")
        self.assertNotIn("mode", new)                          # url mode stays implicit

    def test_yt_subscribe_appends_a_yt_feed(self):
        self.app._ns_set_kind("yt")
        self.app._ns_title.insert(0, "Lex Fridman")
        self.app._ns_url.insert(
            0, "https://www.youtube.com/feeds/videos.xml?channel_id=UCSHZKyawb77ixDdsGog4iWA")
        self.app._ns_tags.insert(0, "video")
        self.app._submit_new_source()

        new = self._feeds()[1]
        self.assertEqual(new["id"], "lex-fridman")             # derived from the title
        self.assertEqual(new["adapter"], "yt")                 # routed to the yt adapter
        self.assertEqual(new["trust"], "queue")
        self.assertEqual(new["tags"], ["video"])
        self.assertNotIn("mode", new)                          # yt carries no api mapping

    def test_yt_channel_url_is_normalized_to_the_rss_feed(self):
        self.app._ns_set_kind("yt")
        self.app._ns_url.insert(
            0, "https://www.youtube.com/channel/UCSHZKyawb77ixDdsGog4iWA")
        self.app._submit_new_source()

        new = self._feeds()[1]
        self.assertEqual(
            new["url"],
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCSHZKyawb77ixDdsGog4iWA")
        self.assertEqual(new["id"], "yt-ucshzkyawb77ixddsgog4iwa")   # id from the channel


class YoutubeFeedURL(unittest.TestCase):
    """youtube_feed_url() — the offline normalizer that turns what a user pastes into
    the channel's RSS feed URL the yt adapter fetches. Pure string work, no network."""

    FEED = "https://www.youtube.com/feeds/videos.xml"

    def test_already_a_feed_url_passes_through(self):
        u = f"{self.FEED}?channel_id=UCSHZKyawb77ixDdsGog4iWA"
        self.assertEqual(gui.youtube_feed_url(u), u)

    def test_channel_page_url_becomes_a_feed_url(self):
        self.assertEqual(
            gui.youtube_feed_url("https://www.youtube.com/channel/UCSHZKyawb77ixDdsGog4iWA"),
            f"{self.FEED}?channel_id=UCSHZKyawb77ixDdsGog4iWA")

    def test_bare_channel_id_becomes_a_feed_url(self):
        self.assertEqual(gui.youtube_feed_url("UCSHZKyawb77ixDdsGog4iWA"),
                         f"{self.FEED}?channel_id=UCSHZKyawb77ixDdsGog4iWA")

    def test_playlist_url_becomes_a_playlist_feed(self):
        self.assertEqual(
            gui.youtube_feed_url("https://www.youtube.com/playlist?list=PLabc123def456"),
            f"{self.FEED}?playlist_id=PLabc123def456")

    def test_a_handle_url_is_left_untouched(self):
        # An @handle's channel_id needs a network lookup we don't do here.
        u = "https://www.youtube.com/@lexfridman"
        self.assertEqual(gui.youtube_feed_url(u), u)

    def test_empty_stays_empty(self):
        self.assertEqual(gui.youtube_feed_url(""), "")


if __name__ == "__main__":
    unittest.main()
