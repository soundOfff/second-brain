"""Unit tests for bin/brain_video.py — the timestamped video extractor.

Everything here is offline and deterministic: only the pure helpers are exercised
(URL guarding, time formatting, deep links, VTT parsing, cue merging, rendering).
`extract()` itself shells out to yt-dlp and is covered by the live smoke test in the
/video skill, not here — a unit suite that hits the network is a flaky suite.

The rolling-caption tests are the important ones. YouTube auto-captions restate the tail
of the previous cue before adding new words, so a naive append triples the transcript;
these lock in the repair.

Run:  python3 -m unittest discover -s bin/tests -t bin -v
"""
from __future__ import annotations

import unittest

import brain_video as bv


class IsVideoURL(unittest.TestCase):
    """Host allowlist — mirrors is_video_url in brain-clip.sh, spoofs must not pass."""

    def test_accepts_known_hosts(self):
        for url in (
            "https://www.youtube.com/watch?v=abc",
            "http://youtube.com/watch?v=abc",
            "https://m.youtube.com/watch?v=abc",
            "https://music.youtube.com/watch?v=abc",
            "https://youtu.be/abc",
            "https://vimeo.com/12345",
            "https://www.vimeo.com/12345",
        ):
            with self.subTest(url=url):
                self.assertTrue(bv.is_video_url(url))

    def test_rejects_spoofs_and_articles(self):
        for url in (
            "https://notyoutube.com.evil.com/watch?v=abc",
            "https://evil.com/https://youtube.com/watch?v=a",
            "https://simonwillison.net/2026/some-post",
            "ftp://youtube.com/watch?v=abc",
            "",
        ):
            with self.subTest(url=url):
                self.assertFalse(bv.is_video_url(url))

    def test_case_and_whitespace_insensitive(self):
        self.assertTrue(bv.is_video_url("  HTTPS://WWW.YouTube.com/watch?v=x  "))


class Hms(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(bv.hms(0), "0:00")
        self.assertEqual(bv.hms(9), "0:09")
        self.assertEqual(bv.hms(59), "0:59")
        self.assertEqual(bv.hms(60), "1:00")
        self.assertEqual(bv.hms(61.9), "1:01")   # truncates, never rounds past the cue
        self.assertEqual(bv.hms(3599), "59:59")
        self.assertEqual(bv.hms(3600), "1:00:00")
        self.assertEqual(bv.hms(3661), "1:01:01")


class DeepLink(unittest.TestCase):
    def test_youtube_appends_query(self):
        self.assertEqual(
            bv.deep_link("https://www.youtube.com/watch?v=abc", 125),
            "https://www.youtube.com/watch?v=abc&t=125s",
        )

    def test_youtube_short_form_uses_question_mark(self):
        self.assertEqual(bv.deep_link("https://youtu.be/abc", 30), "https://youtu.be/abc?t=30s")

    def test_vimeo_uses_fragment(self):
        self.assertEqual(bv.deep_link("https://vimeo.com/1", 12), "https://vimeo.com/1#t=12s")

    def test_unknown_host_returns_bare_url(self):
        """Better a plain link than one that silently lands at 0:00."""
        self.assertEqual(bv.deep_link("https://example.com/v", 12), "https://example.com/v")

    def test_empty_url(self):
        self.assertEqual(bv.deep_link("", 12), "")


class ParseVTT(unittest.TestCase):
    def test_parses_timestamps_and_text(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.200 --> 00:00:03.360\n"
            "Hello there\n\n"
            "00:01:05.000 --> 00:01:07.000\n"
            "Second cue\n"
        )
        cues = bv.parse_vtt(vtt)
        self.assertEqual(len(cues), 2)
        self.assertAlmostEqual(cues[0]["start"], 1.2)
        self.assertAlmostEqual(cues[0]["end"], 3.36)
        self.assertEqual(cues[0]["text"], "Hello there")
        self.assertAlmostEqual(cues[1]["start"], 65.0)

    def test_drops_headers_cue_numbers_and_tags(self):
        vtt = (
            "WEBVTT\n"
            "Kind: captions\n"
            "Language: en\n"
            "NOTE something\n\n"
            "1\n"
            "00:00:00.000 --> 00:00:02.000\n"
            "<c>tagged</c> <00:00:01.000>text\n"
        )
        cues = bv.parse_vtt(vtt)
        self.assertEqual(len(cues), 1)
        self.assertEqual(cues[0]["text"], "tagged text")

    def test_repairs_rolling_autocaption_duplication(self):
        """Each cue restates the previous tail — the transcript must not triple."""
        vtt = (
            "WEBVTT\n\n"
            "00:00:00.000 --> 00:00:02.000\nso today we are going\n\n"
            "00:00:02.000 --> 00:00:04.000\nso today we are going to talk about\n\n"
            "00:00:04.000 --> 00:00:06.500\nto talk about transformers and how\n\n"
            "00:00:06.500 --> 00:00:09.000\ntransformers and how they work.\n"
        )
        cues = bv.parse_vtt(vtt)
        joined = " ".join(c["text"] for c in cues)
        self.assertEqual(joined, "so today we are going to talk about transformers and how they work.")

    def test_drops_exact_duplicate_cue_entirely(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:00.000 --> 00:00:02.000\nsame words\n\n"
            "00:00:02.000 --> 00:00:04.000\nsame words\n\n"
            "00:00:04.000 --> 00:00:06.000\nnew words\n"
        )
        cues = bv.parse_vtt(vtt)
        self.assertEqual([c["text"] for c in cues], ["same words", "new words"])

    def test_multiline_cue_is_joined(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:00.000 --> 00:00:03.000\n"
            "first line\n"
            "second line\n"
        )
        cues = bv.parse_vtt(vtt)
        self.assertEqual(cues[0]["text"], "first line second line")

    def test_distant_repetition_is_preserved(self):
        """A speaker genuinely repeating a phrase later must not be swallowed.

        The overlap search is bounded and only compares the running tail to the incoming
        head, so a phrase recurring after other content survives.
        """
        vtt = (
            "WEBVTT\n\n"
            "00:00:00.000 --> 00:00:02.000\nit depends\n\n"
            "00:00:02.000 --> 00:00:04.000\non the model you pick and honestly\n\n"
            "00:00:04.000 --> 00:00:06.000\nit depends\n"
        )
        cues = bv.parse_vtt(vtt)
        self.assertEqual(len(cues), 3)
        self.assertEqual(cues[2]["text"], "it depends")

    def test_comma_millisecond_separator(self):
        """Some tools emit SRT-style commas; accept both rather than silently drop cues."""
        cues = bv.parse_vtt("WEBVTT\n\n00:00:01,500 --> 00:00:03,000\nhi\n")
        self.assertEqual(len(cues), 1)
        self.assertAlmostEqual(cues[0]["start"], 1.5)

    def test_empty_input(self):
        self.assertEqual(bv.parse_vtt(""), [])
        self.assertEqual(bv.parse_vtt("WEBVTT\n"), [])


class MergeCues(unittest.TestCase):
    @staticmethod
    def _cues(specs):
        return [{"start": s, "end": e, "text": t} for s, e, t in specs]

    def test_empty(self):
        self.assertEqual(bv.merge_cues([]), [])

    def test_rejects_nonpositive_block(self):
        with self.assertRaises(ValueError):
            bv.merge_cues(self._cues([(0, 1, "a")]), block_seconds=0)

    def test_groups_until_span_and_sentence_boundary(self):
        cues = self._cues([
            (0, 5, "One."), (5, 10, "Two."), (10, 15, "Three."), (15, 20, "Four."),
        ])
        blocks = bv.merge_cues(cues, block_seconds=10)
        # Closes at the first cue that both crosses 10s and follows a full stop.
        self.assertGreaterEqual(len(blocks), 2)
        self.assertEqual(blocks[0]["start"], 0)
        self.assertTrue(blocks[0]["text"].startswith("One."))

    def test_unpunctuated_speech_still_breaks_by_2x_escape_hatch(self):
        """Auto-captions often never land a full stop; blocks must not grow unbounded."""
        cues = self._cues([(i * 5, i * 5 + 5, f"word{i}") for i in range(12)])
        blocks = bv.merge_cues(cues, block_seconds=10)
        self.assertGreater(len(blocks), 1)
        for b in blocks:
            self.assertLessEqual(b["end"] - b["start"], 10 * 2 + 5)

    def test_preserves_all_text(self):
        cues = self._cues([(i * 5, i * 5 + 5, f"w{i}") for i in range(9)])
        blocks = bv.merge_cues(cues, block_seconds=12)
        joined = " ".join(b["text"] for b in blocks)
        self.assertEqual(joined.split(), [f"w{i}" for i in range(9)])

    def test_single_cue(self):
        blocks = bv.merge_cues(self._cues([(0, 3, "only")]), block_seconds=45)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["text"], "only")


class ToMarkdown(unittest.TestCase):
    def test_no_transcript_says_so_rather_than_inventing(self):
        md = bv.to_markdown({"segments": [], "title": "T", "url": "u"})
        self.assertIn("No captions were available", md)

    def test_renders_chapters_and_segments(self):
        data = {
            "uploader": "Chan",
            "duration_hms": "1:02",
            "upload_date": "20250424",
            "chapters": [{"timestamp": "0:00", "link": "L0", "title": "Intro"}],
            "segments": [{"timestamp": "0:05", "link": "L5", "text": "Body text"}],
        }
        md = bv.to_markdown(data)
        self.assertIn("**Channel:** Chan", md)
        self.assertIn("**Published:** 2025-04-24", md)
        self.assertIn("[0:00](L0) — Intro", md)
        self.assertIn("**[0:05](L5)** Body text", md)

    def test_omits_chapters_section_when_absent(self):
        md = bv.to_markdown({"segments": [{"timestamp": "0:00", "link": "L", "text": "x"}]})
        self.assertNotIn("Chapters", md)


if __name__ == "__main__":
    unittest.main()
