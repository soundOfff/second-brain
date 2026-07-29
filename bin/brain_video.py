"""Timestamped video extraction — the raw material for a /video breakdown.

`brain-clip.sh` already deposits a video's captions as a flat `type: transcript` source.
That is the right raw artifact for *summarizing*, but it throws the clock away:
`vtt_to_text()` drops every `-->` line. A flat wall of prose cannot tell you where a
claim was made, what the middle third covers, or which minute to rewatch — so it cannot
support a real breakdown.

This module keeps the clock. It pulls the metadata, the uploader's chapters (when they
exist) and the caption cues with their start times, repairs the rolling-window
duplication that YouTube auto-captions are full of, and merges the 2-3s cues into
readable blocks that each carry a deep link back to the exact second.

Two deliberate design points, both learned from bugs:

* **Metadata is fetched on its own pass.** YouTube rate-limits caption requests (HTTP
  429) once a video carries several `en*` variants, and a combined call aborts on that
  error *before* `--write-info-json` lands — silently costing the title and uploader.
  Fetching the info.json separately means a throttled caption never loses the metadata.
* **Captions are requested narrowly first** (`en` exact, one request) and only widened to
  every `en*` variant if that lands nothing. We read a single track anyway, so the narrow
  try is both cheaper and far less likely to trip the limiter.

Stdlib only. `yt-dlp` is the single external dependency — the same one `brain-clip.sh`
already relies on — and its absence is reported as a clean error, never a traceback.

CLI:
    brain_video.py <url> [--json | --markdown] [--block-seconds N] [--out PATH]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Caption cues arrive every 2-3 seconds, which is far too granular to reason about.
# ~45s blocks read like paragraphs and still pin a claim closely enough to rewatch.
DEFAULT_BLOCK_SECONDS = 45

# How far back to look for rolling-caption overlap. Auto-caption cues repeat at most a
# line or so of context; bounding the search keeps legitimate repetition (a speaker
# genuinely saying the same phrase twice) from being swallowed as a duplicate.
_MAX_OVERLAP_WORDS = 24

_VIDEO_HOST_RE = re.compile(
    r"^https?://(?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be|vimeo\.com)(?:/|$)",
    re.IGNORECASE,
)

_TIMESTAMP_RE = re.compile(
    r"(\d{2}):(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[.,](\d{3})"
)


class ExtractError(RuntimeError):
    """Raised for the expected failures (no yt-dlp, not a video URL, no captions)."""


# ---------------------------------------------------------------------------
# Small pure helpers — all independently testable, no network, no disk.
# ---------------------------------------------------------------------------

def is_video_url(url: str) -> bool:
    """Mirror of `is_video_url` in brain-clip.sh: known video hosts only.

    Kept to a host allowlist so we never shell out to yt-dlp for an arbitrary article
    URL. The regex anchors the host to defeat `notyoutube.com.evil.com` style spoofs.
    """
    return bool(_VIDEO_HOST_RE.match(url.strip()))


def hms(seconds: float) -> str:
    """Format a cue offset the way a reader scrubs: M:SS under an hour, else H:MM:SS."""
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def deep_link(webpage_url: str, seconds: float) -> str:
    """A URL that opens the video already scrubbed to this moment.

    YouTube takes `&t=<n>s`; Vimeo takes `#t=<n>s`. Anything else gets the bare URL back
    rather than a link that silently lands at 0:00.
    """
    if not webpage_url:
        return ""
    t = int(seconds)
    low = webpage_url.lower()
    if "youtube.com" in low or "youtu.be" in low:
        sep = "&" if "?" in webpage_url else "?"
        return f"{webpage_url}{sep}t={t}s"
    if "vimeo.com" in low:
        return f"{webpage_url}#t={t}s"
    return webpage_url


def _new_words(prev_words: list[str], new_words: list[str]) -> list[str]:
    """Return only the genuinely-new tail of `new_words`.

    YouTube auto-captions roll: each cue tends to restate the tail of the previous one
    before adding a few words ("so today we're going to" → "so today we're going to talk
    about"). Appending cues naively triples the transcript. We find the longest overlap
    between the tail of what we already have and the head of the incoming cue, and keep
    only the remainder. An exact duplicate collapses to nothing.
    """
    limit = min(len(prev_words), len(new_words), _MAX_OVERLAP_WORDS)
    for k in range(limit, 0, -1):
        if prev_words[-k:] == new_words[:k]:
            return new_words[k:]
    return new_words


def parse_vtt(vtt: str) -> list[dict]:
    """Parse WebVTT into de-duplicated cues: [{start, end, text}, ...].

    Drops the header, cue numbers and inline `<c>`/timing tags, then repairs rolling
    auto-caption duplication across cue boundaries. A cue whose text is entirely a
    repeat of what came before is dropped rather than emitted empty.
    """
    cues: list[dict] = []
    start = end = None
    buf: list[str] = []
    spoken: list[str] = []  # every word emitted so far, for overlap detection

    def flush() -> None:
        nonlocal start, end, buf
        if start is None or not buf:
            buf = []
            return
        raw = re.sub(r"\s+", " ", " ".join(buf)).strip()
        if raw:
            fresh = _new_words(spoken, raw.split())
            if fresh:
                cues.append({"start": start, "end": end, "text": " ".join(fresh)})
                spoken.extend(fresh)
        buf = []

    for raw_line in vtt.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == "WEBVTT" or line.startswith(("NOTE", "STYLE", "Kind:", "Language:")):
            continue
        m = _TIMESTAMP_RE.search(line)
        if m:
            flush()  # a new timestamp closes the previous cue
            h1, m1, s1, ms1, h2, m2, s2, ms2 = (int(g) for g in m.groups())
            start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0
            end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0
            continue
        if line.isdigit():  # bare cue number
            continue
        text = re.sub(r"<[^>]+>", "", line)  # <c>, <00:00:00.000> timing tags
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            buf.append(text)

    flush()
    return cues


def merge_cues(cues: list[dict], block_seconds: int = DEFAULT_BLOCK_SECONDS) -> list[dict]:
    """Group 2-3s cues into ~`block_seconds` paragraphs: [{start, end, text}, ...].

    A block closes once it has covered its span AND the text has reached a sentence
    boundary, so we prefer breaking where the speaker did rather than mid-clause. The
    sentence check is skipped past 2x the target so a speaker who never lands a full stop
    (common in auto-captions, which punctuate poorly) cannot produce one giant block.
    """
    if not cues:
        return []
    if block_seconds <= 0:
        raise ValueError("block_seconds must be positive")

    blocks: list[dict] = []
    cur: dict | None = None

    for cue in cues:
        if cur is None:
            cur = {"start": cue["start"], "end": cue["end"], "parts": [cue["text"]]}
            continue

        span = cue["end"] - cur["start"]
        text_so_far = " ".join(cur["parts"]).rstrip()
        ended_sentence = text_so_far.endswith((".", "!", "?", '."', '?"', '!"'))

        if span >= block_seconds and (ended_sentence or span >= block_seconds * 2):
            blocks.append(
                {"start": cur["start"], "end": cur["end"], "text": " ".join(cur["parts"]).strip()}
            )
            cur = {"start": cue["start"], "end": cue["end"], "parts": [cue["text"]]}
        else:
            cur["parts"].append(cue["text"])
            cur["end"] = cue["end"]

    if cur is not None:
        blocks.append(
            {"start": cur["start"], "end": cur["end"], "text": " ".join(cur["parts"]).strip()}
        )
    return blocks


# ---------------------------------------------------------------------------
# yt-dlp — the only external dependency, and the only code here that touches the network.
# ---------------------------------------------------------------------------

def _run_ytdlp(args: list[str], timeout: int = 120) -> int:
    """Run yt-dlp, swallowing its noise. Returns the exit code; never raises on failure.

    Callers decide what a non-zero exit means — for captions it is routine (throttling,
    or simply no subtitles), and we parse whatever landed on disk regardless.
    """
    try:
        proc = subprocess.run(
            ["yt-dlp", *args],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
        )
        return proc.returncode
    except subprocess.TimeoutExpired:
        return 124
    except FileNotFoundError as exc:  # pragma: no cover - guarded by extract()
        raise ExtractError("yt-dlp is not installed or not on PATH") from exc


def _fetch(url: str, tdir: str, timeout: int = 120) -> tuple[dict, str]:
    """Fetch metadata then captions into `tdir`. Returns (info_json, vtt_text).

    Two passes on purpose — see the module docstring. Missing captions yield an empty
    string rather than an error, so a caption-less video still produces a metadata-only
    breakdown instead of failing outright.
    """
    out_tmpl = os.path.join(tdir, "%(id)s.%(ext)s")
    common = ["-q", "--no-warnings", "--no-playlist", "--skip-download",
              "--socket-timeout", "30", "-o", out_tmpl, url]

    # Pass 1 — metadata alone, so a throttled caption cannot cost us the title/uploader.
    _run_ytdlp(["--write-info-json", *common], timeout=timeout)

    info: dict = {}
    infos = sorted(glob.glob(os.path.join(tdir, "*.info.json")))
    if infos:
        try:
            with open(infos[0], encoding="utf-8", errors="replace") as fh:
                info = json.load(fh)
        except (OSError, ValueError):
            info = {}

    # Pass 2 — captions. `en` exact keeps this to one request in the common case.
    sub_flags = ["--write-auto-subs", "--write-subs", "--sub-format", "vtt"]
    _run_ytdlp([*sub_flags, "--sub-langs", "en", *common], timeout=timeout)
    vtts = sorted(glob.glob(os.path.join(tdir, "*.vtt")))
    if not vtts:
        # Nothing landed — widen to every en* variant (auto-translations included).
        _run_ytdlp([*sub_flags, "--sub-langs", "en.*", *common], timeout=timeout)
        vtts = sorted(glob.glob(os.path.join(tdir, "*.vtt")))

    vtt_text = ""
    if vtts:
        try:
            with open(vtts[0], encoding="utf-8", errors="replace") as fh:
                vtt_text = fh.read()
        except OSError:
            vtt_text = ""

    return info, vtt_text


def extract(url: str, block_seconds: int = DEFAULT_BLOCK_SECONDS,
            timeout: int = 120) -> dict:
    """Pull a video down to a structured, timestamped dict.

    Returns metadata, the uploader's chapters (verbatim, when present), and the merged
    transcript blocks — each with a `link` that opens the video at that second.
    """
    if not is_video_url(url):
        raise ExtractError(f"not a recognized video URL: {url}")
    if shutil.which("yt-dlp") is None:
        raise ExtractError("yt-dlp is not installed or not on PATH")

    tdir = tempfile.mkdtemp(prefix="brain-video-")
    try:
        info, vtt_text = _fetch(url, tdir, timeout=timeout)
    finally:
        shutil.rmtree(tdir, ignore_errors=True)

    webpage_url = (info.get("webpage_url") or url).strip()
    cues = parse_vtt(vtt_text) if vtt_text else []
    blocks = merge_cues(cues, block_seconds=block_seconds)

    # The uploader's own chapters are editorial structure we should never overwrite with
    # our own guesses — pass them through verbatim so the breakdown can defer to them.
    chapters = []
    for ch in info.get("chapters") or []:
        try:
            chapters.append({
                "title": (ch.get("title") or "").strip(),
                "start": float(ch.get("start_time") or 0),
                "end": float(ch.get("end_time") or 0),
                "timestamp": hms(float(ch.get("start_time") or 0)),
                "link": deep_link(webpage_url, float(ch.get("start_time") or 0)),
            })
        except (TypeError, ValueError):
            continue

    return {
        "url": webpage_url,
        "video_id": (info.get("id") or "").strip(),
        "title": (info.get("title") or "").strip(),
        "uploader": (info.get("uploader") or info.get("channel") or "").strip(),
        "channel_url": (info.get("channel_url") or "").strip(),
        "upload_date": (info.get("upload_date") or "").strip(),
        "duration": info.get("duration"),
        "duration_hms": hms(info["duration"]) if info.get("duration") else "",
        "view_count": info.get("view_count"),
        "description": (info.get("description") or "").strip(),
        "chapters": chapters,
        "has_transcript": bool(blocks),
        "cue_count": len(cues),
        "block_seconds": block_seconds,
        "segments": [
            {
                "start": b["start"],
                "end": b["end"],
                "timestamp": hms(b["start"]),
                "link": deep_link(webpage_url, b["start"]),
                "text": b["text"],
            }
            for b in blocks
        ],
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def to_markdown(data: dict) -> str:
    """Render the extraction as a timestamped transcript document.

    This is the *raw* artifact — faithful captions with their clock, no synthesis. It is
    what gets deposited into sources/; the breakdown that interprets it belongs in wiki/.
    """
    lines: list[str] = []
    meta_bits = []
    if data.get("uploader"):
        meta_bits.append(f"**Channel:** {data['uploader']}")
    if data.get("duration_hms"):
        meta_bits.append(f"**Duration:** {data['duration_hms']}")
    if data.get("upload_date") and len(data["upload_date"]) == 8:
        d = data["upload_date"]
        meta_bits.append(f"**Published:** {d[:4]}-{d[4:6]}-{d[6:]}")
    if meta_bits:
        lines.append(" · ".join(meta_bits))
        lines.append("")

    if data.get("chapters"):
        lines.append("## Chapters (from the uploader)")
        lines.append("")
        for ch in data["chapters"]:
            lines.append(f"- [{ch['timestamp']}]({ch['link']}) — {ch['title']}")
        lines.append("")

    lines.append("## Transcript")
    lines.append("")
    if not data.get("segments"):
        lines.append("_No captions were available for this video._")
    else:
        for seg in data["segments"]:
            lines.append(f"**[{seg['timestamp']}]({seg['link']})** {seg['text']}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="brain_video.py",
        description="Extract a timestamped transcript + metadata from a video URL.",
    )
    ap.add_argument("url", help="a YouTube or Vimeo URL")
    fmt = ap.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_const", dest="fmt", const="json",
                     help="emit structured JSON (default)")
    fmt.add_argument("--markdown", action="store_const", dest="fmt", const="markdown",
                     help="emit the timestamped transcript as markdown")
    ap.add_argument("--block-seconds", type=int, default=DEFAULT_BLOCK_SECONDS,
                    help=f"transcript block size (default {DEFAULT_BLOCK_SECONDS}s)")
    ap.add_argument("--timeout", type=int, default=120,
                    help="per-yt-dlp-call timeout in seconds (default 120)")
    ap.add_argument("--out", type=Path, help="write to this path instead of stdout")
    args = ap.parse_args(argv)

    try:
        data = extract(args.url, block_seconds=args.block_seconds, timeout=args.timeout)
    except ExtractError as exc:
        print(f"brain_video: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"brain_video: {exc}", file=sys.stderr)
        return 2

    out = to_markdown(data) if args.fmt == "markdown" else json.dumps(data, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(out, encoding="utf-8")
        print(str(args.out))
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
