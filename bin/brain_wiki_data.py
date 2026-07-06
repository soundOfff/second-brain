"""Wiki data model, extracted from bin/brain-serve.py.

Everything HTML-rendering was left behind in `brain-serve.py`; this module only
loads pages, parses frontmatter, and computes wikilink/citation graph relations.
The React app (via apps/api) consumes raw markdown plus these adjacency maps and
does its own rendering client-side.

All lookups accept explicit `vault` and `wiki_dir` paths so tests can point them
at a temp directory without mutating module state.
"""
from __future__ import annotations

import re
from pathlib import Path


_DEFAULT_VAULT = Path(__file__).resolve().parent.parent

WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
CITATION = re.compile(r"\[(\d{4}-\d{2}-\d{2}-[a-z0-9-]+)\]")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Flat YAML subset: `key: scalar` or `key: [a, b]`. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    meta: dict = {}
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


def source_ids(vault: Path | None = None) -> set[str]:
    """Every source id present under sources/, including .meta.md sidecars."""
    v = vault or _DEFAULT_VAULT
    ids: set[str] = set()
    sources = v / "sources"
    if not sources.exists():
        return ids
    for f in sources.iterdir():
        if not f.is_file() or f.name == "README.md":
            continue
        stem = f.name[:-8] if f.name.endswith(".meta.md") else f.stem
        ids.add(stem)
    return ids


def load_pages(vault: Path | None = None) -> dict:
    """slug -> {meta, body, path}. slug is path under wiki/ without .md.
    The vault-root `index.md` is stored under the reserved slug "index"."""
    v = vault or _DEFAULT_VAULT
    wiki = v / "wiki"
    pages: dict = {}
    if wiki.exists():
        for f in sorted(wiki.rglob("*.md")):
            if f.name == "README.md":
                continue
            slug = str(f.relative_to(wiki).with_suffix(""))
            meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
            pages[slug] = {"meta": meta, "body": body, "path": f}
    idx = v / "index.md"
    if idx.exists():
        meta, body = parse_frontmatter(idx.read_text(encoding="utf-8"))
        pages["index"] = {"meta": meta, "body": body, "path": idx}
    return pages


def link_targets(body: str) -> list[str]:
    out = []
    for m in WIKILINK.finditer(body):
        out.append(m.group(1).split("|")[0].split("#")[0].strip())
    return out


def backlinks(pages: dict) -> dict[str, list[str]]:
    bl: dict[str, list[str]] = {slug: [] for slug in pages}
    for slug, pg in pages.items():
        for tgt in link_targets(pg["body"]):
            if tgt in bl and tgt != slug:
                bl[tgt].append(slug)
    return {k: sorted(set(v)) for k, v in bl.items()}


def source_citers(pages: dict) -> dict[str, set[str]]:
    """Which wiki pages cite each source id (inline `[src-id]` outside wikilinks)."""
    cited: dict[str, set[str]] = {}
    for slug, pg in pages.items():
        body_no_links = WIKILINK.sub("", pg["body"])
        for m in CITATION.finditer(body_no_links):
            cited.setdefault(m.group(1), set()).add(slug)
    return cited


def find_source_file(vault: Path, sid: str) -> Path | None:
    """Locate the file backing a source id — .md or .meta.md sidecar."""
    p = vault / "sources" / f"{sid}.md"
    if p.exists():
        return p
    p = vault / "sources" / f"{sid}.meta.md"
    return p if p.exists() else None
