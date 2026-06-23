#!/usr/bin/env python3
"""Second Brain — tidy: the deterministic, no-LLM maintenance pass.

This is the Claude-free half of /lint. It validates every page against the mechanical
subset of the CLAUDE.md schema and applies only the *safe, unambiguous* auto-fixes. It
makes NO judgment calls (contradictions, starved stubs, "is this claim supported") —
that is /lint's job, and it needs Claude.

It is both an importable SDK and a CLI. The SDK is three functions:

    find_violations(vault) -> list[Violation]   # check; Violation.severity in {FAIL, WARN}
    fix(vault, violations=None) -> list[Fix]    # apply ONLY the safe fixes; never writes sources/
    backlog(vault) -> list[str]                 # source ids with no recap (cron's gate before /sync)

CLI:
    brain_tidy.py            check, human-readable, exit 1 on any FAIL
    brain_tidy.py --quiet    only FAIL/WARN lines + summary (what the pre-commit shim calls)
    brain_tidy.py --fix      apply safe fixes, report what changed
    brain_tidy.py --backlog  print backlog ids, one per line
    brain_tidy.py --json     machine-readable output (CI / programmatic callers)

Stdlib only, by deliberate convention (see docs/adr/0001). Frontmatter is parsed by
hand because the schema is flat and simple — no PyYAML.

The three safe fixes, and ONLY these (see docs/adr/0001 for why the boundary is here):
  1. clamp `updated < created`  -> set updated = created
  2. case-only wikilink repair  -> [[Anthropic]] -> [[anthropic]] when exactly one page matches
  3. frontmatter list spacing   -> sources: [a,b] -> sources: [a, b]
Everything else is reported, never auto-fixed. tidy never writes to sources/.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path

SRC_TYPES = {"article", "pdf", "transcript", "screenshot", "note", "data"}
WIKI_TYPES = {"entity", "concept", "recap", "digest", "index"}
STATUSES = {"stub", "active", "stable"}

SRC_REQUIRED = ["id", "title", "type", "captured"]
WIKI_REQUIRED = ["type", "title", "created", "updated", "status", "sources", "tags"]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CITE_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2}-[a-z0-9-]+)\]")
# [[target]], [[target|alias]], [[target#anchor]] — group 1 = target, group 2 = suffix
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)((?:[#\|])[^\]]*)?\]\]")
LIST_FM_RE = re.compile(r"^(sources|tags|aliases):\s*\[(.*)\]\s*$")


@dataclass
class Violation:
    file: str
    line: int          # 1-based; 0 if not line-specific
    severity: str      # "FAIL" | "WARN"
    code: str          # short machine code, e.g. "missing-key", "dangling-link"
    message: str
    fixable: bool = False


@dataclass
class Fix:
    file: str
    code: str          # "clamp-updated" | "wikilink-case" | "list-spacing"
    detail: str


# --- frontmatter helpers ---------------------------------------------------

def split_frontmatter(text: str):
    """Return (frontmatter_lines, body_start_index_in_lines).

    Frontmatter is the lines strictly between the first and second `---`, and only
    when line 1 is exactly `---` (mirrors brain-validate.sh). Returns ([], 0) if absent.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], i + 1
    return [], 0  # unterminated frontmatter == none


def fmval(fm_lines, key):
    """Value of a flat `key: value` frontmatter line, quotes/whitespace stripped."""
    for ln in fm_lines:
        m = re.match(rf"^{re.escape(key)}:\s*(.*)$", ln)
        if m:
            v = m.group(1).strip()
            if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
                v = v[1:-1]
            return v
    return ""


def fm_list(fm_lines, key):
    """Parse a `key: [a, b]` list into stripped items."""
    raw = fmval(fm_lines, key)
    raw = raw.strip().lstrip("[").rstrip("]")
    return [x.strip() for x in raw.split(",") if x.strip()]


def strip_code_and_links(body: str) -> str:
    """Remove inline `code` and [[wikilinks]] so examples aren't read as citations."""
    body = re.sub(r"`[^`]*`", "", body)
    body = re.sub(r"\[\[[^\]]*\]\]", "", body)
    return body


# --- source id index -------------------------------------------------------

def source_ids(vault: Path):
    """Stems of every file under sources/ (README excluded; .meta.md sidecars folded)."""
    ids = set()
    sdir = vault / "sources"
    if not sdir.is_dir():
        return ids
    for f in sdir.rglob("*"):
        if not f.is_file():
            continue
        base = f.name
        if base == "README.md":
            continue
        stem = base[:-len(".meta.md")] if base.endswith(".meta.md") else f.stem
        ids.add(stem)
    return ids


def wiki_page_index(vault: Path):
    """Map lowercased 'path/without/ext' -> [actual relpaths] for every wiki page + index.

    Used for *case-sensitive* link resolution: we can't rely on Path.is_file(), because
    on a case-insensitive filesystem (default macOS) it reports wrong-case paths as
    existing, which would both hide dangling links and prevent the case-only fix.
    """
    idx = {}
    wdir = vault / "wiki"
    paths = []
    if wdir.is_dir():
        paths.extend(p for p in wdir.rglob("*.md") if p.is_file() and p.name != "README.md")
    rels = []
    for p in paths:
        rel = p.relative_to(wdir).with_suffix("").as_posix()
        rels.append(rel)
    if (vault / "index.md").is_file():
        rels.append("index")
    for rel in rels:
        idx.setdefault(rel.lower(), []).append(rel)
    return idx


# --- checks ----------------------------------------------------------------

def find_violations(vault) -> list:
    """Validate every source and wiki page. Returns a list of Violation."""
    vault = Path(vault)
    vs: list[Violation] = []
    ids = source_ids(vault)
    page_idx = wiki_page_index(vault)
    exact_pages = {r for rs in page_idx.values() for r in rs}  # case-sensitive existence

    def rel(p):
        return os.path.relpath(p, vault)

    # 1. sources/ frontmatter (sources are immutable; report only, never fix)
    sdir = vault / "sources"
    if sdir.is_dir():
        for f in sorted(sdir.rglob("*.md")):
            if not f.is_file() or f.name == "README.md":
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            fm, _ = split_frontmatter(text)
            if not fm:
                vs.append(Violation(rel(f), 1, "FAIL", "no-frontmatter", "missing frontmatter block"))
                continue
            base = f.name
            stem = base[:-len(".meta.md")] if base.endswith(".meta.md") else f.stem
            for key in SRC_REQUIRED:
                if not fmval(fm, key):
                    vs.append(Violation(rel(f), 0, "FAIL", "missing-key", f"missing required key '{key}'"))
            sid = fmval(fm, "id")
            if sid and sid != stem:
                vs.append(Violation(rel(f), 0, "FAIL", "id-stem", f"id '{sid}' != filename stem '{stem}'"))
            t = fmval(fm, "type")
            if t and t not in SRC_TYPES:
                vs.append(Violation(rel(f), 0, "FAIL", "bad-type", f"invalid source type '{t}'"))
            cap = fmval(fm, "captured")
            if cap and not DATE_RE.match(cap):
                vs.append(Violation(rel(f), 0, "FAIL", "bad-date", f"captured '{cap}' is not YYYY-MM-DD"))

    # 2. wiki/ pages + root index.md
    wiki_files = []
    wdir = vault / "wiki"
    if wdir.is_dir():
        wiki_files.extend(sorted(p for p in wdir.rglob("*.md") if p.is_file() and p.name != "README.md"))
    if (vault / "index.md").is_file():
        wiki_files.append(vault / "index.md")

    for f in wiki_files:
        text = f.read_text(encoding="utf-8", errors="replace")
        fm, body_start = split_frontmatter(text)
        if not fm:
            vs.append(Violation(rel(f), 1, "FAIL", "no-frontmatter", "missing frontmatter block"))
            continue
        slug = f.stem
        for key in WIKI_REQUIRED:
            if not fmval(fm, key):
                vs.append(Violation(rel(f), 0, "FAIL", "missing-key", f"missing required key '{key}'"))
        if not KEBAB_RE.match(slug):
            vs.append(Violation(rel(f), 0, "FAIL", "bad-slug", f"slug '{slug}' is not kebab-case"))
        t = fmval(fm, "type")
        if t and t not in WIKI_TYPES:
            vs.append(Violation(rel(f), 0, "FAIL", "bad-type", f"invalid type '{t}'"))
        st = fmval(fm, "status")
        if st and st not in STATUSES:
            vs.append(Violation(rel(f), 0, "FAIL", "bad-status", f"invalid status '{st}'"))
        cr, up = fmval(fm, "created"), fmval(fm, "updated")
        if cr and not DATE_RE.match(cr):
            vs.append(Violation(rel(f), 0, "FAIL", "bad-date", f"created '{cr}' is not YYYY-MM-DD"))
        if up and not DATE_RE.match(up):
            vs.append(Violation(rel(f), 0, "FAIL", "bad-date", f"updated '{up}' is not YYYY-MM-DD"))
        if DATE_RE.match(cr or "") and DATE_RE.match(up or "") and up < cr:
            vs.append(Violation(rel(f), 0, "FAIL", "updated-before-created",
                                f"updated ({up}) is before created ({cr})", fixable=True))
        for s in fm_list(fm, "sources"):
            if s not in ids:
                vs.append(Violation(rel(f), 0, "FAIL", "bad-source-ref",
                                    f"sources entry '{s}' has no file in sources/"))

        body = "\n".join(text.splitlines()[body_start:])
        cite_text = strip_code_and_links(body)
        for cid in sorted(set(CITE_RE.findall(cite_text))):
            if cid not in ids:
                vs.append(Violation(rel(f), 0, "FAIL", "unknown-cite", f"cites unknown source id '{cid}'"))

        link_text = re.sub(r"`[^`]*`", "", body)
        for m in WIKILINK_RE.finditer(link_text):
            tgt = m.group(1).strip()
            if not tgt:
                continue
            if tgt in exact_pages:  # case-sensitive: "index" is in the set if it exists
                continue
            cands = page_idx.get(tgt.lower(), [])
            cands = [c for c in cands if c != tgt]
            if len(cands) == 1:
                vs.append(Violation(rel(f), 0, "WARN", "dangling-link",
                                    f"dangling wikilink [[{tgt}]] — case fix to [[{cands[0]}]]?",
                                    fixable=True))
            else:
                vs.append(Violation(rel(f), 0, "WARN", "dangling-link",
                                    f"dangling wikilink [[{tgt}]] — page worth creating?"))
    return vs


# --- fixes (only the 3 safe ones; never touches sources/) -------------------

def fix(vault, violations=None) -> list:
    """Apply only the safe, unambiguous fixes. Returns a list of Fix describing changes."""
    vault = Path(vault)
    page_idx = wiki_page_index(vault)
    exact_pages = {r for rs in page_idx.values() for r in rs}  # case-sensitive existence
    fixes: list[Fix] = []

    wiki_files = []
    wdir = vault / "wiki"
    if wdir.is_dir():
        wiki_files.extend(sorted(p for p in wdir.rglob("*.md") if p.is_file() and p.name != "README.md"))
    if (vault / "index.md").is_file():
        wiki_files.append(vault / "index.md")

    for f in wiki_files:
        rel = os.path.relpath(f, vault)
        text = f.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines(keepends=False)
        fm, body_start = split_frontmatter(text)
        if not fm:
            continue
        changed = False

        # fix 1 + 3 operate on frontmatter lines (indices 1 .. body_start-2)
        created = fmval(fm, "created")
        for i in range(1, body_start - 1):
            ln = lines[i]
            # fix 1: clamp updated < created
            m = re.match(r"^updated:\s*(.*)$", ln)
            if m and DATE_RE.match(created or "") and DATE_RE.match(m.group(1).strip() or ""):
                up = m.group(1).strip()
                if up < created:
                    lines[i] = f"updated: {created}"
                    fixes.append(Fix(rel, "clamp-updated", f"updated {up} -> {created}"))
                    changed = True
                    continue
            # fix 3: normalize list spacing
            lm = LIST_FM_RE.match(ln)
            if lm:
                key, inner = lm.group(1), lm.group(2)
                items = [x.strip() for x in inner.split(",") if x.strip()]
                normalized = f"{key}: [{', '.join(items)}]"
                if normalized != ln:
                    lines[i] = normalized
                    fixes.append(Fix(rel, "list-spacing", f"normalized {key} list spacing"))
                    changed = True

        # fix 2: case-only wikilink repair (body only)
        body_lines = lines[body_start:]
        body = "\n".join(body_lines)

        def repl(m):
            nonlocal changed
            tgt, suffix = m.group(1).strip(), m.group(2) or ""
            if tgt in exact_pages:
                return m.group(0)
            cands = [c for c in page_idx.get(tgt.lower(), []) if c != tgt]
            if len(cands) == 1:
                fixes.append(Fix(rel, "wikilink-case", f"[[{tgt}]] -> [[{cands[0]}]]"))
                changed = True
                return f"[[{cands[0]}{suffix}]]"
            return m.group(0)

        # only rewrite outside inline code spans
        def repl_outside_code(text_block):
            parts = re.split(r"(`[^`]*`)", text_block)
            for j in range(0, len(parts), 2):  # even indices are outside code
                parts[j] = WIKILINK_RE.sub(repl, parts[j])
            return "".join(parts)

        new_body = repl_outside_code(body)
        if new_body != body:
            body_lines = new_body.split("\n")

        if changed:
            new_text = "\n".join(lines[:body_start] + body_lines)
            if text.endswith("\n") and not new_text.endswith("\n"):
                new_text += "\n"
            f.write_text(new_text, encoding="utf-8")

    return fixes


# --- backlog (deterministic sync gate) -------------------------------------

def backlog(vault) -> list:
    """Source ids with no wiki/recaps/<id>.md yet. Pure file-existence; no LLM."""
    vault = Path(vault)
    recaps = vault / "wiki" / "recaps"
    out = []
    for sid in sorted(source_ids(vault)):
        if not (recaps / f"{sid}.md").is_file():
            out.append(sid)
    return out


# --- CLI -------------------------------------------------------------------

def _vault_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _report(vs, quiet):
    fails = [v for v in vs if v.severity == "FAIL"]
    warns = [v for v in vs if v.severity == "WARN"]
    for v in vs:
        if quiet and v.severity not in ("FAIL", "WARN"):
            continue
        loc = f"{v.file}:{v.line}" if v.line else v.file
        print(f"  {v.severity}  {loc}: {v.message}")
    print("──────────────────────────────────────────────")
    print(f"{len(fails)} fail · {len(warns)} warn")
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    quiet = "--quiet" in argv
    as_json = "--json" in argv
    do_fix = "--fix" in argv
    do_backlog = "--backlog" in argv
    vault = _vault_root()

    if do_backlog:
        ids = backlog(vault)
        if as_json:
            print(json.dumps(ids))
        else:
            for sid in ids:
                print(sid)
        return 0

    applied = fix(vault, None) if do_fix else []
    vs = find_violations(vault)

    if as_json:
        print(json.dumps({
            "violations": [asdict(v) for v in vs],
            "fixes": [asdict(x) for x in applied],
            "fail": sum(1 for v in vs if v.severity == "FAIL"),
            "warn": sum(1 for v in vs if v.severity == "WARN"),
        }, indent=2))
        return 1 if any(v.severity == "FAIL" for v in vs) else 0

    if applied:
        print("fixed:")
        for x in applied:
            print(f"  {x.code}  {x.file}: {x.detail}")
    return _report(vs, quiet)


if __name__ == "__main__":
    sys.exit(main())
