#!/usr/bin/env python3
"""Second Brain — read-only wiki server (external tool #2 of docs/external-tools.md).

Serves wiki/**.md + index.md as a browsable site: resolves [[wikilinks]] into real
navigation, renders inline [src-id] citations as links to the immutable source, shows a
backlinks panel per page, and surfaces `status: stub` pages and dangling links.

It does NO LLM work and NO writes — it only renders what the agent precomputed, re-read
from disk on every request so live edits show immediately. Stdlib only.

    bin/brain-serve.sh [port]      # default 8765
"""
import html
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

VAULT = Path(__file__).resolve().parent.parent
WIKI = VAULT / "wiki"
SOURCES = VAULT / "sources"

WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
CITATION = re.compile(r"\[(\d{4}-\d{2}-\d{2}-[a-z0-9-]+)\]")
MDLINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
ITALIC = re.compile(r"(?<![\*])\*(?!\s)([^*]+?)\*(?![\*])")


# --- model -----------------------------------------------------------------
def parse_frontmatter(text):
    """Flat YAML subset: `key: scalar` or `key: [a, b]`. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    meta = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key, rest = key.strip(), rest.strip()
        if rest.startswith("[") and rest.endswith("]"):
            items = [x.strip().strip('"').strip("'") for x in rest[1:-1].split(",")]
            meta[key] = [x for x in items if x]
        else:
            meta[key] = rest.strip('"').strip("'")
    return meta, body


def source_ids():
    ids = set()
    if not SOURCES.exists():
        return ids
    for f in SOURCES.iterdir():
        if not f.is_file() or f.name == "README.md":
            continue
        stem = f.name[:-8] if f.name.endswith(".meta.md") else f.stem
        ids.add(stem)
    return ids


def load_pages():
    """slug -> {meta, body, path}. slug is path under wiki/ w/o .md; 'index' = root."""
    pages = {}
    for f in sorted(WIKI.rglob("*.md")):
        if f.name == "README.md":
            continue
        slug = str(f.relative_to(WIKI).with_suffix(""))
        meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
        pages[slug] = {"meta": meta, "body": body, "path": f}
    idx = VAULT / "index.md"
    if idx.exists():
        meta, body = parse_frontmatter(idx.read_text(encoding="utf-8"))
        pages["index"] = {"meta": meta, "body": body, "path": idx}
    return pages


def link_targets(body):
    out = []
    for m in WIKILINK.finditer(body):
        out.append(m.group(1).split("|")[0].split("#")[0].strip())
    return out


def backlinks(pages):
    bl = {slug: [] for slug in pages}
    for slug, pg in pages.items():
        for tgt in link_targets(pg["body"]):
            if tgt in bl and tgt != slug:
                bl[tgt].append(slug)
    return {k: sorted(set(v)) for k, v in bl.items()}


def source_citers(pages):
    cited = {}
    for slug, pg in pages.items():
        body_no_links = WIKILINK.sub("", pg["body"])
        for m in CITATION.finditer(body_no_links):
            cited.setdefault(m.group(1), set()).add(slug)
    return cited


# --- inline + block rendering ----------------------------------------------
def render_inline(text, pages, srcids):
    text = html.escape(text)
    spans, codes = [], re.compile(r"`([^`]+)`")
    text = codes.sub(lambda m: spans.append(m.group(1)) or f"\x00{len(spans)-1}\x00", text)

    def wikilink(m):
        raw = m.group(1)
        target = raw.split("|")[0].split("#")[0].strip()
        label = raw.split("|")[1].strip() if "|" in raw else target
        if target == "index":
            return f'<a href="/">{html.escape(label)}</a>'
        if target in pages:
            return f'<a href="/wiki/{target}">{html.escape(label)}</a>'
        return (f'<a class="missing" title="page not created yet" '
                f'href="/wiki/{target}">{html.escape(label)}</a>')

    def citation(m):
        sid = m.group(1)
        if sid in srcids:
            return f'<a class="cite" href="/source/{sid}">[{sid}]</a>'
        return f'<span class="cite missing" title="unknown source">[{sid}]</span>'

    text = WIKILINK.sub(wikilink, text)
    text = MDLINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    text = CITATION.sub(citation, text)
    text = BOLD.sub(r"<strong>\1</strong>", text)
    text = ITALIC.sub(r"<em>\1</em>", text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{html.escape(spans[int(m.group(1))])}</code>", text)
    return text


def render_body(body, pages, srcids):
    out, i, lines = [], 0, body.splitlines()
    inline = lambda s: render_inline(s, pages, srcids)
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
        elif re.match(r"#{1,6} ", line):
            n = len(line) - len(line.lstrip("#"))
            out.append(f"<h{n}>{inline(line[n+1:].strip())}</h{n}>")
        elif line.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(inline(lines[i].lstrip(">").strip()))
                i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>")
            continue
        elif re.match(r"[-*] ", line):
            buf = []
            while i < len(lines) and re.match(r"[-*] ", lines[i]):
                buf.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(buf) + "</ul>")
            continue
        elif re.match(r"\d+\. ", line):
            buf = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i]):
                buf.append(f"<li>{inline(re.sub(r'^\d+\. ', '', lines[i]))}</li>")
                i += 1
            out.append("<ol>" + "".join(buf) + "</ol>")
            continue
        elif line.strip() == "":
            pass
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(r"(#{1,6} |[-*] |\d+\. |> |```)", lines[i]):
                buf.append(inline(lines[i]))
                i += 1
            out.append("<p>" + " ".join(buf) + "</p>")
            continue
        i += 1
    return "\n".join(out)


# --- HTML shell ------------------------------------------------------------
CSS = """
:root{--fg:#1c1c1c;--mut:#6a6a6a;--line:#e4e4e4;--accent:#3a5bd9;--bg:#fbfbfa}
*{box-sizing:border-box}body{margin:0;font:16px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;color:var(--fg);background:var(--bg)}
.wrap{display:grid;grid-template-columns:260px 1fr;min-height:100vh}
aside{border-right:1px solid var(--line);padding:20px 18px;background:#f5f5f3;position:sticky;top:0;height:100vh;overflow:auto}
aside h1{font-size:15px;margin:0 0 14px}aside a{color:var(--fg);text-decoration:none}
.grp{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin:16px 0 6px}
.navitem{display:block;padding:3px 0;font-size:14px}.navitem:hover{color:var(--accent)}
.badge{font-size:10px;color:#b06a00;border:1px solid #e3c08a;border-radius:3px;padding:0 4px;margin-left:5px}
main{padding:34px 46px;max-width:820px}
a{color:var(--accent)}a.missing{color:#c0392b;border-bottom:1px dotted #c0392b;text-decoration:none}
a.cite{font-size:.82em;color:var(--mut);text-decoration:none}a.cite:hover{color:var(--accent)}
.cite.missing{color:#c0392b}
.meta{color:var(--mut);font-size:13px;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:8px}
.meta .tag{display:inline-block;background:#ececea;border-radius:3px;padding:0 6px;margin-right:4px;font-size:12px}
h1,h2,h3{line-height:1.25}h1{font-size:28px}blockquote{border-left:3px solid var(--line);margin:0;padding:2px 14px;color:#444}
pre{background:#f0f0ee;padding:12px 14px;border-radius:6px;overflow:auto;font-size:13px}
code{background:#ececea;padding:1px 4px;border-radius:3px;font-size:.88em}pre code{background:none;padding:0}
.panel{margin-top:38px;border-top:1px solid var(--line);padding-top:14px;font-size:14px}
.panel h3{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin:0 0 8px}
.empty{color:var(--mut);font-style:italic}
"""


def sidebar(pages):
    by_dir = {}
    for slug in pages:
        if slug == "index":
            continue
        d = slug.split("/")[0] if "/" in slug else "_"
        by_dir.setdefault(d, []).append(slug)
    out = ['<aside><h1><a href="/">🧠 Second Brain</a></h1>']
    out.append('<a class="navitem" href="/">Map of content</a>')
    for d in sorted(by_dir):
        out.append(f'<div class="grp">{html.escape(d)}</div>')
        for slug in sorted(by_dir[d]):
            meta = pages[slug]["meta"]
            title = html.escape(meta.get("title", slug))
            badge = ' <span class="badge">stub</span>' if meta.get("status") == "stub" else ""
            out.append(f'<a class="navitem" href="/wiki/{slug}">{title}{badge}</a>')
    out.append("</aside>")
    return "".join(out)


def shell(title, pages, body_html):
    return (f"<!doctype html><html><head><meta charset=utf-8>"
            f"<meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(title)} · Second Brain</title><style>{CSS}</style></head>"
            f"<body><div class=wrap>{sidebar(pages)}<main>{body_html}</main></div></body></html>")


def meta_line(meta):
    bits = []
    if meta.get("type"):
        bits.append(f'<span class="tag">{html.escape(meta["type"])}</span>')
    if meta.get("status"):
        bits.append(f'<span class="tag">{html.escape(meta["status"])}</span>')
    if meta.get("updated"):
        bits.append(f'updated {html.escape(meta["updated"])}')
    for t in meta.get("tags", []):
        bits.append(f"#{html.escape(t)}")
    return '<div class="meta">' + " · ".join(bits) + "</div>" if bits else ""


def panel(title, items):
    if not items:
        inner = '<span class="empty">none</span>'
    else:
        inner = " · ".join(items)
    return f'<div class="panel"><h3>{title}</h3>{inner}</div>'


# --- request handling ------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def send_html(self, body, code=200):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = unquote(self.path.split("?")[0])
        pages = load_pages()
        srcids = source_ids()
        bl = backlinks(pages)
        citers = source_citers(pages)

        if path == "/":
            return self.render_page("index", pages, srcids, bl)
        if path.startswith("/wiki/"):
            return self.render_page(path[len("/wiki/"):], pages, srcids, bl)
        if path.startswith("/source/"):
            return self.render_source(path[len("/source/"):], pages, srcids, citers)
        self.send_html(shell("404", pages, "<h1>404</h1><p>No such page.</p>"), 404)

    def render_page(self, slug, pages, srcids, bl):
        if slug not in pages:
            self.send_html(shell("missing", pages,
                f'<h1 class="missing">{html.escape(slug)}</h1>'
                f'<p>This page is linked but not yet created — a candidate worth writing.</p>'), 404)
            return
        pg = pages[slug]
        body = render_body(pg["body"], pages, srcids)
        back = [f'<a href="/wiki/{s}">{html.escape(pages[s]["meta"].get("title", s))}</a>' for s in bl.get(slug, [])]
        srcs = []
        for sid in pg["meta"].get("sources", []):
            cls = "" if sid in srcids else ' class="missing"'
            srcs.append(f'<a{cls} href="/source/{sid}">{sid}</a>')
        html_body = meta_line(pg["meta"]) + body + panel("Linked from", back) + panel("Sources", srcs)
        self.send_html(shell(pg["meta"].get("title", slug), pages, html_body))

    def render_source(self, sid, pages, srcids, citers):
        f = SOURCES / f"{sid}.md"
        if not f.exists():
            f = SOURCES / f"{sid}.meta.md"
        if not f.exists():
            self.send_html(shell("source", pages, f"<h1>Source not found</h1><p>{html.escape(sid)}</p>"), 404)
            return
        raw = f.read_text(encoding="utf-8")
        cited = [f'<a href="/wiki/{s}">{html.escape(pages[s]["meta"].get("title", s))}</a>'
                 for s in sorted(citers.get(sid, []))]
        body = (f"<h1>Source · {html.escape(sid)}</h1>"
                f'<p class="meta">raw immutable source — sources/{html.escape(f.name)}</p>'
                f"<pre>{html.escape(raw)}</pre>" + panel("Cited by", cited))
        self.send_html(shell(sid, pages, body))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    n = len(load_pages())
    print(f"Second Brain wiki → http://127.0.0.1:{port}  ({n} pages, read-only)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
