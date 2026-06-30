#!/usr/bin/env python3
"""Second Brain — brain-feed: the pull feeder (external tool #4 of docs/external-tools.md).

Where brain-clip.sh is *push* (you clip one thing, deliberately, now), brain-feed is
*pull* — it subscribes to feeds and fetches new material UNATTENDED. It does the same
zero-synthesis deposit as the clipper (in fact it reuses it) and never invokes an LLM:
the nightly /sync (02:00) folds whatever it deposits into the wiki.

The deliberate act moves up one level, from per-item to per-subscription:
  • per-feed trust — a curated feed is `trust = "auto"` (flows straight into sources/);
    a noisy one is `trust = "queue"` (lands in .brain/review/ for `brain-feed review`).
  • per-feed daily cap (`n`) — even a trusted feed contributes at most n items/day; the
    overflow is deferred (left unseen) and drains over following days. Bounded, so no
    single feed can flood the brain.

Architecture — one core, four adapters:

    feeds.toml ─┐
                ├─► [poller core] ─per item─► dedup ─► cap ─► (trust?)
     adapters:  │        │                              ├─auto──► sources/
      rss ──────┤  .brain/feed-state.db (sqlite)        └─queue─► .brain/review/
      list ─────┤  seen GUIDs + per-feed daily counts          │
      yt  ──────┤                               brain-feed review (k/d/s)
      email ────┘                                     keep ──► sources/

Deposit reuses tool #1: the core calls `brain-clip.sh --dry-run` to RENDER a contract-
valid source, injects provenance (`via:`, `tags:`) into its frontmatter, then *places*
the file into sources/ (trusted) or .brain/review/ (queued) itself — so all the
slug/frontmatter/extraction logic stays in one place and tool #3 still guards what lands.

Stdlib only for the core (rss, list). The heavyweight adapters degrade gracefully:
  • yt    — needs `yt-dlp` on PATH for transcripts; else falls back to the feed summary.
  • email — needs an IMAP app-password in the macOS Keychain; else the adapter disables
            itself and logs why. The one secret is never on disk or in git.

CLI:
    brain-feed.py run [--dry-run] [--feed ID]   poll feeds, deposit/queue new items
    brain-feed.py review                         triage .brain/review/ (keep/drop/skip)
    brain-feed.py status                         feeds, seen counts, queue size

See docs/external-tools.md §4 for the full design.
"""
from __future__ import annotations

import email as emaillib
import email.header
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import tomllib
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
CLIP = VAULT / "bin" / "brain-clip.sh"
SOURCES = VAULT / "sources"
BRAIN = VAULT / ".brain"
DB_PATH = BRAIN / "feed-state.db"
REVIEW_DIR = BRAIN / "review"
CONFIG = VAULT / "feeds.toml"
LOG = BRAIN / "feed.log"

UA = "Mozilla/5.0 (brain-feed)"
DEFAULT_CAP = 5


# --- small utilities -------------------------------------------------------

def today_str() -> str:
    """Today as YYYY-MM-DD. BRAIN_FEED_TODAY overrides it (used by the test harness)."""
    return os.environ.get("BRAIN_FEED_TODAY") or date.today().isoformat()


def now_stamp() -> str:
    return os.environ.get("BRAIN_FEED_TODAY") or date.today().isoformat()


def log(msg: str) -> None:
    """Append to .brain/feed.log AND echo to stdout (so interactive runs are visible)."""
    line = f"[{now_stamp()}] {msg}"
    print(line)
    try:
        BRAIN.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def localname(tag: str) -> str:
    """Strip an XML namespace: '{http://...}entry' -> 'entry'."""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def fetch_url(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (trusted feeds)
        return resp.read()


# --- config ----------------------------------------------------------------

def load_config(path: Path) -> dict:
    """Parse feeds.toml -> {default_cap, feeds:[...]}. Missing file => no feeds."""
    if not path.is_file():
        return {"default_cap": DEFAULT_CAP, "feeds": []}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    feeds = data.get("feed", [])
    if isinstance(feeds, dict):  # a single [feed] table rather than [[feed]]
        feeds = [feeds]
    return {"default_cap": int(data.get("default_cap", DEFAULT_CAP)), "feeds": feeds}


# --- sqlite state ----------------------------------------------------------

def db_connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE IF NOT EXISTS seen "
        "(feed TEXT, guid TEXT, url TEXT, ts TEXT, PRIMARY KEY(feed, guid))"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS daily "
        "(feed TEXT, day TEXT, count INTEGER, PRIMARY KEY(feed, day))"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS decisions "
        "(feed_id TEXT NOT NULL, item_id TEXT NOT NULL, "
        " action TEXT NOT NULL, timestamp INTEGER NOT NULL, "
        " PRIMARY KEY(item_id, timestamp))"
    )
    con.commit()
    return con


def is_seen(con, feed: str, guid: str) -> bool:
    cur = con.execute("SELECT 1 FROM seen WHERE feed=? AND guid=?", (feed, guid))
    return cur.fetchone() is not None


def mark_seen(con, feed: str, guid: str, url: str | None) -> None:
    con.execute(
        "INSERT OR IGNORE INTO seen (feed, guid, url, ts) VALUES (?,?,?,?)",
        (feed, guid, url or "", today_str()),
    )


def day_count(con, feed: str, day: str) -> int:
    cur = con.execute("SELECT count FROM daily WHERE feed=? AND day=?", (feed, day))
    row = cur.fetchone()
    return row[0] if row else 0


def bump_day(con, feed: str, day: str) -> None:
    con.execute(
        "INSERT INTO daily (feed, day, count) VALUES (?,?,1) "
        "ON CONFLICT(feed, day) DO UPDATE SET count = count + 1",
        (feed, day),
    )


# --- keep/drop decision log (powers the Feed Stats keep-rate) ----------------

def log_decision(con, feed_id: str, item_id: str, action: str,
                 ts: int | None = None) -> int:
    """Record one keep/drop decision; return the unix timestamp used (so a caller can
    store it and undo the exact row later). INSERT OR IGNORE so a same-second re-decision
    of the same item never crashes triage. Does NOT commit — the caller owns the txn."""
    if ts is None:
        ts = int(time.time())
    con.execute(
        "INSERT OR IGNORE INTO decisions (feed_id, item_id, action, timestamp) "
        "VALUES (?,?,?,?)",
        (feed_id or "", item_id, action, ts),
    )
    return ts


def delete_decision(con, item_id: str, ts: int) -> None:
    """Remove the exact decision row logged for (item_id, ts). Used by the GUI's undo so a
    reversed keep/drop does not inflate keep-rate. Idempotent; does NOT commit."""
    con.execute(
        "DELETE FROM decisions WHERE item_id=? AND timestamp=?",
        (item_id, ts),
    )


def compute_keep_rate(con, feed_id: str, min_decisions: int = 10) -> float | None:
    """Fraction kept among (kept + dropped) decisions for one feed. Returns None ('N/A')
    when fewer than `min_decisions` decisions exist. Only keep/drop are ever logged
    (skip is not), so kept + dropped == total."""
    row = con.execute(
        "SELECT "
        "  SUM(CASE WHEN action='keep' THEN 1 ELSE 0 END), "
        "  SUM(CASE WHEN action='drop' THEN 1 ELSE 0 END) "
        "FROM decisions WHERE feed_id=?",
        (feed_id,),
    ).fetchone()
    kept = row[0] or 0
    dropped = row[1] or 0
    total = kept + dropped
    if total < min_decisions:
        return None
    return kept / total


# --- dedup against material already in sources/ ----------------------------

def _frontmatter_url(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        m = re.match(r"^url:\s*(\S+)", ln)
        if m:
            return m.group(1).strip()
    return None


def existing_source_urls(vault: Path) -> set[str]:
    """Every `url:` already recorded under sources/ — so a hand-clip is never re-pulled."""
    urls: set[str] = set()
    sdir = vault / "sources"
    if not sdir.is_dir():
        return urls
    for f in sdir.rglob("*.md"):
        if not f.is_file():
            continue
        u = _frontmatter_url(f.read_text(encoding="utf-8", errors="replace"))
        if u:
            urls.add(u)
    return urls


# --- deposit: render via brain-clip, inject provenance, place --------------

def render_via_clip(item: dict) -> tuple[str | None, str | None, str]:
    """Run brain-clip.sh --dry-run for one item. Returns (proposed_path, content, stderr).

    URL items go through the clipper's URL fetch+extract; text items (yt transcripts,
    emails) are piped to stdin with an explicit --type/--title/--url.
    """
    if item["source_kind"] == "url":
        args = [str(CLIP), "--dry-run"]
        if item.get("title"):
            args += ["--title", item["title"]]
        args += [item["url"]]
        proc = subprocess.run(args, capture_output=True, text=True, timeout=90)
    else:  # text
        args = [str(CLIP), "--dry-run"]
        if item.get("type"):
            args += ["--type", item["type"]]
        if item.get("title"):
            args += ["--title", item["title"]]
        if item.get("url"):
            args += ["--url", item["url"]]
        args += ["-"]
        proc = subprocess.run(
            args, input=item.get("body") or "", capture_output=True, text=True, timeout=90
        )
    path, content = parse_dryrun(proc.stdout)
    return path, content, proc.stderr


def parse_dryrun(out: str) -> tuple[str | None, str | None]:
    """Split brain-clip --dry-run stdout into (proposed_path, source_content)."""
    lines = out.splitlines()
    if not lines:
        return None, None
    m = re.match(r"^# --- would write (.+?) ---$", lines[0])
    if not m:
        return None, None
    content = "\n".join(lines[1:]).lstrip("\n")
    if content and not content.endswith("\n"):
        content += "\n"
    return m.group(1), content


def inject_provenance(content: str, feed_id: str, tags: list[str]) -> str:
    """Add `via: <feed-id>` (and `tags:` if the feed defines them) to the frontmatter."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return content
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return content
    fm = lines[1:end]
    if not any(re.match(r"^via:\s", l) for l in fm):
        fm.append(f"via: {feed_id}")
    if tags and not any(re.match(r"^tags:\s", l) for l in fm):
        fm.append("tags: [" + ", ".join(tags) + "]")
    new = ["---", *fm, "---", *lines[end + 1:]]
    out = "\n".join(new)
    if content.endswith("\n"):
        out += "\n"
    return out


def _stem_taken(vault: Path, stem: str, check_review: bool) -> bool:
    if list((vault / "sources").glob(f"{stem}.*")):
        return True
    if (vault / "sources" / f"{stem}.meta.md").exists():
        return True
    if check_review and list((vault / ".brain" / "review").glob(f"{stem}.*")):
        return True
    return False


def unique_stem(vault: Path, stem: str, check_review: bool = True) -> str:
    """A stem free in sources/ (and, when check_review, in the review pen too) so two
    items in one run can't collide and the contract id == filename stem stays intact.
    `review` keep passes check_review=False — the file being kept lives in the pen."""
    if not _stem_taken(vault, stem, check_review):
        return stem
    n = 2
    while _stem_taken(vault, f"{stem}-{n}", check_review):
        n += 1
    return f"{stem}-{n}"


def place(content: str, proposed_path: str, dest_dir: Path, vault: Path,
          check_review: bool = True) -> Path:
    """Write the rendered source into dest_dir, keeping id == filename stem on collision."""
    stem = Path(proposed_path).stem
    final = unique_stem(vault, stem, check_review)
    if final != stem:
        content = re.sub(r"^id:.*$", f"id: {final}", content, count=1, flags=re.M)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{final}.md"
    dest.write_text(content, encoding="utf-8")
    return dest


# ===========================================================================
# Adapters — each returns a list of normalized items. The core does dedup,
# cap, trust-routing and deposit, so adapters stay thin.
#
# Normalized item:
#   guid        stable per-feed dedup key
#   url         canonical url (also used for cross-source dedup), or None
#   title       entry title, or None
#   body        text to deposit (text items), or None to let brain-clip fetch a url
#   type        source type override, or None
#   source_kind "url" | "text"
#   _line       (list adapter only) index of the source line to comment out on deposit
# ===========================================================================

def _txt(el) -> str:
    return (el.text or "").strip() if el is not None else ""


def parse_feed_xml(xml_bytes: bytes) -> list[dict]:
    """Parse RSS 2.0 or Atom bytes into [{guid,url,title,summary}]. Namespace-agnostic."""
    root = ET.fromstring(xml_bytes)
    items: list[dict] = []
    nodes = [e for e in root.iter() if localname(e.tag) in ("item", "entry")]
    for node in nodes:
        children: dict[str, list] = {}
        for c in node:
            children.setdefault(localname(c.tag), []).append(c)

        title = _txt(children.get("title", [None])[0])

        # link: RSS <link>text</link>; Atom <link href=...> (prefer rel=alternate)
        url = ""
        link_els = children.get("link", [])
        atom = [le for le in link_els if le.get("href")]
        if atom:
            alt = [le for le in atom if (le.get("rel") or "alternate") == "alternate"]
            url = (alt[0] if alt else atom[0]).get("href", "").strip()
        elif link_els:
            url = _txt(link_els[0])

        guid = (
            _txt(children.get("guid", [None])[0])
            or _txt(children.get("id", [None])[0])
            or url
            or title
        )

        summary = (
            _txt(children.get("description", [None])[0])
            or _txt(children.get("summary", [None])[0])
            or _txt(children.get("content", [None])[0])
        )
        items.append({"guid": guid, "url": url or None, "title": title or None,
                      "summary": summary or None})
    return items


def adapter_rss(feed: dict) -> list[dict]:
    raw = fetch_url(feed["url"])
    out = []
    for e in parse_feed_xml(raw):
        if not e["url"]:
            continue  # an item with no link can't be fetched
        out.append({"guid": e["guid"], "url": e["url"], "title": e["title"],
                    "body": None, "type": None, "source_kind": "url"})
    return out


_URL_RE = re.compile(r"https?://\S+")


def adapter_list(feed: dict) -> tuple[list[dict], dict | None]:
    """Drain URLs from a markdown list file. Returns (items, ctx) where ctx carries the
    file lines so deposited URLs can be commented out (`# done: ...`) after the run."""
    path = Path(os.path.expanduser(feed["path"]))
    if not path.is_file():
        log(f"[{feed['id']}] list: file not found: {path}")
        return [], None
    lines = path.read_text(encoding="utf-8").splitlines()
    items = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s or s.startswith("#"):  # blank or already commented / "# done:"
            continue
        m = _URL_RE.search(ln)
        if not m:
            continue
        url = m.group(0).rstrip(".,);]")
        items.append({"guid": url, "url": url, "title": None, "body": None,
                      "type": None, "source_kind": "url", "_line": i})
    return items, {"path": path, "lines": lines}


# --- yt: rss + an optional transcript fetch --------------------------------

def has_ytdlp() -> bool:
    return shutil.which("yt-dlp") is not None


def vtt_to_text(vtt: str) -> str:
    """Flatten a WebVTT subtitle file to plain prose: drop the header, cue numbers,
    timestamp lines and inline tags, and collapse the consecutive duplicate lines that
    auto-generated captions are full of."""
    out: list[str] = []
    for raw in vtt.splitlines():
        ln = raw.strip()
        if not ln or ln == "WEBVTT" or ln.startswith(("NOTE", "STYLE", "Kind:", "Language:")):
            continue
        if "-->" in ln:
            continue
        if ln.isdigit():
            continue
        ln = re.sub(r"<[^>]+>", "", ln)            # <c>, <00:00:00.000> timing tags
        ln = re.sub(r"\s+", " ", ln).strip()
        if not ln:
            continue
        if out and out[-1] == ln:                   # drop adjacent dupes
            continue
        out.append(ln)
    return "\n".join(out)


def fetch_transcript(url: str) -> str | None:
    """Best-effort transcript via yt-dlp. Returns plain text, or None on any failure."""
    try:
        with tempfile.TemporaryDirectory() as td:
            cmd = [
                "yt-dlp", "--skip-download", "--write-auto-subs", "--write-subs",
                "--sub-langs", "en.*", "--sub-format", "vtt",
                "-o", str(Path(td) / "%(id)s.%(ext)s"), url,
            ]
            subprocess.run(cmd, capture_output=True, timeout=180)
            vtts = sorted(Path(td).glob("*.vtt"))
            if not vtts:
                return None
            text = vtt_to_text(vtts[0].read_text(encoding="utf-8", errors="replace"))
            return text or None
    except Exception:
        return None


def adapter_yt(feed: dict) -> list[dict]:
    raw = fetch_url(feed["url"])
    have = has_ytdlp()
    if not have:
        log(f"[{feed['id']}] yt: yt-dlp not on PATH — falling back to feed summaries")
    out = []
    for e in parse_feed_xml(raw):
        if not e["url"]:
            continue
        transcript = fetch_transcript(e["url"]) if have else None
        if transcript:
            out.append({"guid": e["guid"], "url": e["url"], "title": e["title"],
                        "body": transcript, "type": "transcript", "source_kind": "text"})
        else:
            # fallback: deposit the feed summary as an article (design default)
            body = e["summary"] or f"(no transcript or summary available)\n\n{e['url']}"
            out.append({"guid": e["guid"], "url": e["url"], "title": e["title"],
                        "body": body, "type": "article", "source_kind": "text"})
    return out


# --- email: IMAP poll of a Gmail label; secret stays in the Keychain -------

def keychain_password(account: str, service: str) -> str | None:
    if not shutil.which("security"):
        return None
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-a", account, "-s", service, "-w"],
            capture_output=True, text=True, timeout=15,
        )
    except Exception:
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _decode_header(value: str | None) -> str:
    if not value:
        return ""
    parts = email.header.decode_header(value)
    out = []
    for txt, enc in parts:
        if isinstance(txt, bytes):
            out.append(txt.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(txt)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def email_body_text(msg) -> str:
    """Extract a plain-text body: prefer text/plain; else crudely strip a text/html part."""
    plain, htmls = [], []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition", "").lower().startswith("attachment"):
                continue
            ctype = part.get_content_type()
            try:
                payload = part.get_payload(decode=True)
            except Exception:
                continue
            if payload is None:
                continue
            charset = part.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if ctype == "text/plain":
                plain.append(text)
            elif ctype == "text/html":
                htmls.append(text)
    else:
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset() or "utf-8"
        text = payload.decode(charset, errors="replace") if payload else ""
        (plain if msg.get_content_type() == "text/plain" else htmls).append(text)

    if plain:
        return "\n".join(plain).strip()
    if htmls:
        stripped = re.sub(r"<[^>]+>", " ", "\n".join(htmls))
        return re.sub(r"[ \t]+", " ", stripped).strip()
    return ""


def adapter_email(feed: dict) -> list[dict]:
    user = feed.get("user")
    if not user:
        log(f"[{feed['id']}] email: disabled — no `user` in feeds.toml")
        return []
    service = feed.get("keychain_service", "brain-feed-imap")
    pw = keychain_password(user, service)
    if not pw:
        log(f"[{feed['id']}] email: disabled — no Keychain password "
            f"(add: security add-generic-password -a {user} -s {service} -w)")
        return []
    host = feed.get("host", "imap.gmail.com")
    mailbox = feed.get("mailbox") or feed.get("label") or "INBOX"
    out = []
    try:
        import imaplib
        M = imaplib.IMAP4_SSL(host)
        M.login(user, pw)
        M.select(f'"{mailbox}"', readonly=True)
        typ, data = M.search(None, "ALL")
        ids = data[0].split() if data and data[0] else []
        for num in ids[-50:]:  # newest 50; cap+dedup bound the actual deposits
            typ, msgdata = M.fetch(num, "(RFC822)")
            if not msgdata or not msgdata[0]:
                continue
            msg = emaillib.message_from_bytes(msgdata[0][1])
            guid = (msg.get("Message-ID") or f"{feed['id']}:{num.decode()}").strip()
            subject = _decode_header(msg.get("Subject")) or "(no subject)"
            body = email_body_text(msg)
            sender = _decode_header(msg.get("From"))
            full = f"From: {sender}\n\n{body}" if sender else body
            out.append({"guid": guid, "url": None, "title": subject,
                        "body": full, "type": "note", "source_kind": "text"})
        M.logout()
    except Exception as e:
        log(f"[{feed['id']}] email: poll failed — {e}")
        return []
    return out


ADAPTERS = {"rss": adapter_rss, "list": adapter_list, "yt": adapter_yt, "email": adapter_email}


def collect(feed: dict) -> tuple[list[dict], dict | None]:
    """Dispatch to the adapter. Returns (items, ctx); ctx is non-None only for `list`."""
    a = feed.get("adapter")
    if a == "list":
        return adapter_list(feed)
    fn = ADAPTERS.get(a)
    if not fn:
        raise ValueError(f"unknown adapter '{a}'")
    return fn(feed), None


# ===========================================================================
# Core poll loop
# ===========================================================================

def run(dry_run: bool = False, only_feed: str | None = None) -> int:
    cfg = load_config(CONFIG)
    if not cfg["feeds"]:
        log("no feeds configured (edit feeds.toml). nothing to do.")
        return 0
    con = db_connect(DB_PATH)
    day = today_str()
    existing_urls = existing_source_urls(VAULT)
    deposited_urls: set[str] = set()
    total_dep = total_q = 0

    for feed in cfg["feeds"]:
        fid, adapter = feed.get("id"), feed.get("adapter")
        if not fid or not adapter:
            log(f"skipping malformed feed entry (need id + adapter): {feed!r}")
            continue
        if only_feed and fid != only_feed:
            continue
        cap = int(feed.get("n", cfg["default_cap"]))
        trust = feed.get("trust", "queue")
        tags = feed.get("tags", []) or []

        try:
            items, ctx = collect(feed)
        except Exception as e:
            log(f"[{fid}] adapter error: {e}")
            continue

        already = day_count(con, fid, day)
        dep = queued = deferred = skipped = failed = 0

        for it in items:
            guid, url = it["guid"], it.get("url")
            if is_seen(con, fid, guid):
                skipped += 1
                continue
            if url and (url in existing_urls or url in deposited_urls):
                if not dry_run:
                    mark_seen(con, fid, guid, url)
                skipped += 1
                continue
            if already + dep + queued >= cap:
                deferred += 1          # leave UNSEEN: it drains on a future day
                continue

            proposed, content, stderr = render_via_clip(it)
            if not content:
                failed += 1
                snippet = (stderr or "").strip().splitlines()[-1:] or [""]
                log(f"[{fid}] render failed: {url or it.get('title')} — {snippet[0][:160]}")
                if not dry_run:                  # mark seen so a dead item isn't retried forever
                    mark_seen(con, fid, guid, url)
                continue

            content = inject_provenance(content, fid, tags)
            dest_dir = SOURCES if trust == "auto" else REVIEW_DIR
            verb = "deposit" if trust == "auto" else "queue"

            if dry_run:
                log(f"[{fid}] would {verb}: {Path(proposed).name}")
            else:
                dest = place(content, proposed, dest_dir, VAULT)
                mark_seen(con, fid, guid, url)
                bump_day(con, fid, day)
                log(f"[{fid}] {verb}: {dest.relative_to(VAULT)}")
                if ctx is not None and "_line" in it:
                    ctx.setdefault("done", set()).add(it["_line"])

            if trust == "auto":
                dep += 1
            else:
                queued += 1
            if url:
                deposited_urls.add(url)

        # list: comment out the lines we drained (record, don't delete)
        if ctx is not None and not dry_run and ctx.get("done"):
            lines = ctx["lines"]
            for i in sorted(ctx["done"]):
                if not lines[i].lstrip().startswith("#"):
                    lines[i] = f"# done: {lines[i]}"
            ctx["path"].write_text("\n".join(lines) + "\n", encoding="utf-8")

        dl, ql = ("would-deposit", "would-queue") if dry_run else ("deposited", "queued")
        parts = [f"{dep} {dl}", f"{queued} {ql}", f"{deferred} deferred",
                 f"{skipped} skipped"]
        if failed:
            parts.append(f"{failed} failed")
        log(f"[{fid}] {', '.join(parts)} (cap {cap}, {already} earlier today)")
        total_dep += dep
        total_q += queued

    if not dry_run:
        con.commit()
    con.close()
    tail = " (dry-run, nothing written)" if dry_run else ""
    log(f"done: {total_dep} deposited, {total_q} queued{tail}")
    return 0


# ===========================================================================
# review — interactive triage of the queue
# ===========================================================================

def _preview(text: str, n: int = 8) -> tuple[dict, list[str]]:
    lines = text.splitlines()
    fm = {}
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                body_start = i + 1
                break
            m = re.match(r"^(\w+):\s*(.*)$", lines[i])
            if m:
                fm[m.group(1)] = m.group(2).strip().strip('"')
    body = [l for l in lines[body_start:] if l.strip()][:n]
    return fm, body


def _safe_log(con, feed_id: str, item_id: str, action: str) -> None:
    """Log a decision without ever aborting a triage session on a db hiccup."""
    try:
        log_decision(con, feed_id, item_id, action)
        con.commit()
    except Exception as e:  # noqa: BLE001 (logging must not break triage)
        log(f"decision log failed ({action} {item_id}): {e}")


def review() -> int:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    queue = sorted(REVIEW_DIR.glob("*.md"))
    if not queue:
        print("review queue empty (.brain/review/).")
        return 0
    con = db_connect(DB_PATH)
    print(f"{len(queue)} item(s) queued. [k]eep -> sources/  [d]rop  [s]kip  [q]uit\n")
    kept = dropped = 0
    for f in queue:
        text = f.read_text(encoding="utf-8", errors="replace")
        fm, body = _preview(text)
        feed_id = fm.get("via", "")
        item_id = f.stem
        print("─" * 70)
        print(f"  {fm.get('title', f.stem)}")
        if fm.get("via"):
            print(f"  via: {fm['via']}   type: {fm.get('type', '?')}")
        if fm.get("url"):
            print(f"  {fm['url']}")
        print()
        for bl in body:
            print(f"  {bl[:100]}")
        print()
        try:
            choice = input("  [k/d/s/q]? ").strip().lower()
        except EOFError:
            print("\n(end of input — stopping)")
            break
        if choice == "q":
            break
        if choice == "k":
            dest = place(text, f.name, SOURCES, VAULT, check_review=False)
            f.unlink()
            _safe_log(con, feed_id, item_id, "keep")
            kept += 1
            print(f"  kept -> {dest.relative_to(VAULT)}\n")
        elif choice == "d":
            f.unlink()
            _safe_log(con, feed_id, item_id, "drop")
            dropped += 1
            print("  dropped\n")
        else:
            print("  skipped\n")
    con.close()
    print("─" * 70)
    print(f"{kept} kept, {dropped} dropped, {len(list(REVIEW_DIR.glob('*.md')))} still queued.")
    if kept:
        print("Run /sync (or wait for the 02:00 agent) to fold the kept sources in.")
    return 0


# ===========================================================================
# feed stats — per-feed counts + keep-rate (read-only; powers the GUI Stats tab)
# ===========================================================================

def _queued_counts() -> dict[str, int]:
    """Count queued files in REVIEW_DIR grouped by their `via:` feed id. Files with no
    `via:` land under "" and so match no configured feed."""
    counts: dict[str, int] = {}
    if not REVIEW_DIR.is_dir():
        return counts
    for p in sorted(REVIEW_DIR.glob("*.md")):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm, _ = _preview(text, n=0)  # frontmatter only
        fid = fm.get("via", "")
        counts[fid] = counts.get(fid, 0) + 1
    return counts


def feed_stats(con, cfg: dict, day: str | None = None) -> list[dict]:
    """One dict per configured feed: id, adapter, trust, cap, total_seen, today_seen,
    queued, keep_rate. Sorted by keep_rate descending with N/A (None) last, id-stable."""
    if day is None:
        day = today_str()
    queued_by_feed = _queued_counts()
    rows = []
    for feed in cfg.get("feeds", []):
        fid = feed.get("id")
        if not fid:
            continue
        total_seen = con.execute(
            "SELECT COUNT(*) FROM seen WHERE feed=?", (fid,)
        ).fetchone()[0]
        rows.append({
            "id": fid,
            "adapter": feed.get("adapter", "?"),
            "trust": feed.get("trust", "queue"),
            "cap": int(feed.get("n", cfg.get("default_cap", DEFAULT_CAP))),
            "total_seen": total_seen,
            "today_seen": day_count(con, fid, day),
            "queued": queued_by_feed.get(fid, 0),
            "keep_rate": compute_keep_rate(con, fid),
        })
    rows.sort(key=lambda r: (r["keep_rate"] is None, -(r["keep_rate"] or 0.0), r["id"]))
    return rows


# ===========================================================================
# status
# ===========================================================================

def status() -> int:
    cfg = load_config(CONFIG)
    con = db_connect(DB_PATH)
    day = today_str()
    print(f"feeds.toml — default daily cap {cfg['default_cap']}")
    if not cfg["feeds"]:
        print("  (no feeds configured)")
    for feed in cfg["feeds"]:
        fid = feed.get("id", "?")
        cap = feed.get("n", cfg["default_cap"])
        seen_n = con.execute("SELECT COUNT(*) FROM seen WHERE feed=?", (fid,)).fetchone()[0]
        today_n = day_count(con, fid, day)
        kr = compute_keep_rate(con, fid)
        kr_s = "keep N/A" if kr is None else f"keep {kr*100:.0f}%"
        print(f"  • {fid:<22} {feed.get('adapter','?'):<6} "
              f"{feed.get('trust','queue'):<6} cap {cap:<3} "
              f"— {seen_n} seen, {today_n} today, {kr_s}")
    con.close()
    q = len(list(REVIEW_DIR.glob("*.md"))) if REVIEW_DIR.is_dir() else 0
    src = len([p for p in SOURCES.glob("*.md") if p.name != "README.md"]) if SOURCES.is_dir() else 0
    print(f"\nqueue (.brain/review/): {q} awaiting triage")
    print(f"sources/: {src} markdown source(s)")
    return 0


# ===========================================================================
# CLI
# ===========================================================================

USAGE = """brain-feed — the pull feeder (external tool #4). Polls feeds, deposits new
material into sources/ (trusted) or .brain/review/ (queued); no LLM. /sync folds it in.

  brain-feed.py run [--dry-run] [--feed ID]   poll feeds and deposit/queue new items
  brain-feed.py review                         triage the queue (keep/drop/skip)
  brain-feed.py status                         show feeds, seen counts, queue size

Config: feeds.toml (committed). State: .brain/feed-state.db. See docs/external-tools.md §4.
"""


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "status"
    rest = argv[1:]
    if cmd in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    if cmd == "run":
        dry = "--dry-run" in rest
        only = None
        if "--feed" in rest:
            i = rest.index("--feed")
            only = rest[i + 1] if i + 1 < len(rest) else None
        return run(dry_run=dry, only_feed=only)
    if cmd == "review":
        return review()
    if cmd == "status":
        return status()
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
