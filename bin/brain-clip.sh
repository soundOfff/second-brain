#!/bin/zsh
# Second Brain — capture bridge (external tool #1 of docs/external-tools.md).
#
# Lands raw, immutable material into sources/ with VALID frontmatter — and nothing
# else. It does ZERO synthesis and never invokes an LLM: that is the whole point. The
# nightly launchd /sync (02:00) folds whatever this writes into the wiki. Because it is
# deterministic and dependency-light (curl + python3 stdlib), it can be driven from a
# macOS Shortcut, an iOS share-sheet, a browser "clip" button, or cron — anywhere, with
# no keyboard in this repo and no API key.
#
# Contrast: bin/brain-capture.sh runs the LLM /capture skill end-to-end (raw + ripple).
# brain-clip.sh is the cheap front door — it only deposits the raw source.
#
#   brain-clip.sh <url>                 fetch + extract a web page    -> type: article
#   brain-clip.sh <youtube|vimeo url>   pull the captions transcript  -> type: transcript
#   brain-clip.sh /path/to/file.pdf     copy a file in (+ .meta.md)   -> type by ext
#   brain-clip.sh "pasted text ..."     a quick note                  -> type: note
#   echo text | brain-clip.sh -         read note text from stdin     -> type: note
#
# Flags:
#   --type <t>     override source type (article|pdf|transcript|screenshot|note|data)
#   --title "..."  override the derived title
#   --author "..." set the author frontmatter key
#   --url <u>      attach a source url (for file/text modes)
#   --note "..."   prepend a note (as a blockquote) above the extracted/copied body
#                  (url + text-file modes) — the page capture itself is kept intact
#   --dry-run      print the source that WOULD be written; touch nothing
#   -h | --help    this help
#
# Exit: 0 on success (prints the path written), 1 on error. After writing, it runs the
# contract validator (tool #3) on the new file so #3 guards what #1 feeds.
set -u
setopt null_glob extended_glob

VAULT="${0:A:h:h}"
SELF="${0:t}"

usage() {
  cat <<'EOF'
brain-clip.sh — deposit a raw, immutable source (no LLM); nightly /sync folds it in.

  brain-clip.sh <url>               fetch + extract a web page   -> type: article
  brain-clip.sh <youtube|vimeo url> pull the captions transcript -> type: transcript
  brain-clip.sh /path/to/file.pdf   copy a file in (+ .meta.md)  -> type by extension
  brain-clip.sh "pasted text ..."   a quick note                 -> type: note
  echo text | brain-clip.sh -       read note text from stdin    -> type: note

Flags:
  --type <t>     article|pdf|transcript|screenshot|note|data (override the default)
  --title "..."  override the derived title
  --author "..." set the author frontmatter key
  --url <u>      attach a source url (file/text modes)
  --note "..."   prepend a note (blockquote) above the extracted/copied body
  --dry-run      print the source that WOULD be written; touch nothing
  -h | --help    this help
EOF
}

# --- parse args ------------------------------------------------------------
# Flags may appear anywhere. Non-flag tokens collect into `pos`; the mode is decided
# from pos[1] (url / existing file), and for the text/note case all positionals are
# rejoined so unquoted multi-word notes still work. `--` stops flag parsing.
TYPE_OVERRIDE="" TITLE_OVERRIDE="" AUTHOR_OVERRIDE="" URL_OVERRIDE="" NOTE_OVERRIDE="" DRYRUN=0
typeset -a pos
endflags=0
while (( $# )); do
  if (( endflags )); then pos+=("$1"); shift; continue; fi
  case "$1" in
    -h|--help)  usage; exit 0 ;;
    --type)     TYPE_OVERRIDE="${2:?--type needs a value}"; shift 2 ;;
    --title)    TITLE_OVERRIDE="${2:?--title needs a value}"; shift 2 ;;
    --author)   AUTHOR_OVERRIDE="${2:?--author needs a value}"; shift 2 ;;
    --url)      URL_OVERRIDE="${2:?--url needs a value}"; shift 2 ;;
    --note)     NOTE_OVERRIDE="${2:?--note needs a value}"; shift 2 ;;
    --dry-run)  DRYRUN=1; shift ;;
    --)         endflags=1; shift ;;
    -)          pos+=("-"); shift ;;
    -*)         print -u2 "$SELF: unknown flag '$1' (try --help)"; exit 1 ;;
    *)          pos+=("$1"); shift ;;
  esac
done

if (( ${#pos} == 0 )); then
  [[ -p /dev/stdin ]] || { usage; exit 1; }
  ARG="-"                                    # piped stdin with no positional => note
elif [[ "${pos[1]}" == (http|https)://* ]]; then
  ARG="${pos[1]}"                            # url: ignore stray positionals
  (( ${#pos} > 1 )) && print -u2 "$SELF: note — ignoring extra arguments after '${pos[1]}'"
elif [[ "${pos[1]}" != "-" && -f "${pos[1]}" ]]; then
  ARG="${pos[1]:A}"                          # file: absolutize NOW (before we cd to the vault)
  (( ${#pos} > 1 )) && print -u2 "$SELF: note — ignoring extra arguments after '${pos[1]}'"
else
  ARG="${(j: :)pos}"                         # text/note: rejoin all positionals
fi

die() { print -u2 "$SELF: $1"; exit 1; }

# Everything below writes to sources/ RELATIVE to the vault, so anchor there no matter
# where we were invoked from (app, share-sheet, cron, another directory). File args were
# absolutized above; the URL temp files use mktemp, so the cd is safe for every mode.
cd "$VAULT" || die "cannot cd to vault: $VAULT"

SRC_TYPES="article pdf transcript screenshot note data"
in_set() { [[ " $2 " == *" $1 "* ]] }
if [[ -n "$TYPE_OVERRIDE" ]] && ! in_set "$TYPE_OVERRIDE" "$SRC_TYPES"; then
  die "invalid --type '$TYPE_OVERRIDE' (one of: $SRC_TYPES)"
fi

CAPTURED="$(date +%Y-%m-%d)"

# kebab-case, date-prefixed slug from arbitrary text; capped to keep filenames sane.
slugify() {
  local s
  s="$(print -r -- "$1" | LC_ALL=C tr '[:upper:]' '[:lower:]' \
        | LC_ALL=C sed -E 's/[^a-z0-9]+/-/g; s/-+/-/g; s/^-//; s/-+$//')"
  s="${s[1,60]}"; s="${s%-}"          # cap length; drop a hyphen left by truncation
  [[ -z "$s" ]] && s="untitled"
  print -r -- "$s"
}

# Pick a non-colliding id of the form <date>-<slug>, suffixing -2, -3 ... if taken.
# Collision = ANY sources/<id>.* already exists (markdown, binary, or .meta.md sidecar).
unique_id() {
  local base="$CAPTURED-$1" id="$CAPTURED-$1" n=2 hits
  while :; do
    hits=(sources/$id.*(N) sources/$id.meta.md(N))
    (( ${#hits} == 0 )) && { print -r -- "$id"; return; }
    id="$base-$n"; (( n++ ))
  done
}

# Emit a source frontmatter block from the globals below.
emit_fm() {
  print -r -- "---"
  print -r -- "id: $ID"
  print -r -- "title: \"${TITLE//\"/\\\"}\""
  print -r -- "type: $TYPE"
  [[ -n "$URLV" ]]    && print -r -- "url: $URLV"
  [[ -n "$AUTHORV" ]] && print -r -- "author: $AUTHORV"
  print -r -- "captured: $CAPTURED"
  print -r -- "---"
}

# If a --note was given, prepend it (as a blockquote) above the captured body, so the
# raw page/file capture stays intact beneath the reader's note. No-op when unset.
prepend_note() {
  local body="$1" q
  [[ -z "$NOTE_OVERRIDE" ]] && { print -r -- "$body"; return; }
  q="$(print -r -- "$NOTE_OVERRIDE" | sed 's/^/> /')"
  printf '%s\n\n---\n\n%s' "$q" "$body"
}

# Write a markdown source (frontmatter + body) or, with --dry-run, print it.
write_md() {
  local path="$1" body="$2"
  if (( DRYRUN )); then
    print -r -- "# --- would write $path ---"
    { emit_fm; print -r -- ""; print -r -- "$body" }
    return
  fi
  { emit_fm; print -r -- ""; print -r -- "$body" } > "$path"
  print -r -- "wrote $path"
}

# A URL we can pull a spoken-word transcript from via yt-dlp captions, rather than
# scraping the (useless) player page HTML. Kept to known video hosts so we never shell
# out to yt-dlp on an arbitrary article URL.
is_video_url() {
  local u="${1:l}"
  case "$u" in
    (http|https)://(www.|m.|music.)#youtube.com/*) return 0 ;;
    (http|https)://youtu.be/*)                     return 0 ;;
    (http|https)://(www.)#vimeo.com/*)             return 0 ;;
  esac
  return 1
}

URLV="" AUTHORV="$AUTHOR_OVERRIDE" TITLE="" TYPE="" ID=""

# ============================================================================
# MODE 1 — URL. Video hosts -> captions transcript via yt-dlp (type: transcript);
#              everything else -> fetch + readability-extract  (type: article).
# Both branches emit the same @@TITLE@@/@@AUTHOR@@/@@BODY@@ protocol into $outf.
# ============================================================================
if [[ "$ARG" == (http|https)://* ]]; then
  command -v python3 >/dev/null || die "python3 not found"
  URLV="$ARG"
  outf="$(mktemp)"; htmlf=""; tdir=""
  trap '[[ -n "${outf:-}" ]] && rm -f "$outf"
        [[ -n "${htmlf:-}" ]] && rm -f "$htmlf"
        [[ -n "${tdir:-}" ]] && rm -rf "$tdir"' EXIT

  if is_video_url "$URLV" && command -v yt-dlp >/dev/null; then
  # --- video: pull the auto/uploaded captions, flatten to prose -------------
  deftype=transcript
  tdir="$(mktemp -d)"
  # captions + metadata in one pass; --no-playlist so a stray ?list= can't drag in a
  # whole playlist. A non-zero exit (e.g. no subs) is non-fatal: parse whatever landed.
  yt-dlp -q --no-warnings --no-playlist --skip-download \
    --write-auto-subs --write-subs --sub-langs "en.*" --sub-format vtt \
    --write-info-json --socket-timeout 30 \
    -o "$tdir/%(id)s.%(ext)s" "$URLV" >/dev/null 2>&1 \
    || print -u2 "$SELF: note — yt-dlp exited non-zero for '$URLV'; parsing whatever it fetched."

  python3 - "$tdir" "$URLV" > "$outf" <<'PY'
import sys, re, os, json, glob

td = sys.argv[1]

def vtt_to_text(vtt):
    """Flatten WebVTT to prose: drop the header, cue numbers, timestamp lines and inline
    timing tags, and collapse the adjacent duplicate lines auto-captions are full of."""
    out = []
    for raw in vtt.splitlines():
        ln = raw.strip()
        if not ln or ln == "WEBVTT" or ln.startswith(("NOTE", "STYLE", "Kind:", "Language:")):
            continue
        if "-->" in ln or ln.isdigit():
            continue
        ln = re.sub(r"<[^>]+>", "", ln)            # <c>, <00:00:00.000> timing tags
        ln = re.sub(r"\s+", " ", ln).strip()
        if not ln or (out and out[-1] == ln):
            continue
        out.append(ln)
    return "\n".join(out)

title = author = ""
infos = sorted(glob.glob(os.path.join(td, "*.info.json")))
if infos:
    try:
        d = json.load(open(infos[0], encoding="utf-8", errors="replace"))
        title = (d.get("title") or "").strip()
        author = (d.get("uploader") or d.get("channel") or "").strip()
    except Exception:
        pass

body = ""
vtts = sorted(glob.glob(os.path.join(td, "*.vtt")))
if vtts:
    body = vtt_to_text(open(vtts[0], encoding="utf-8", errors="replace").read()).strip()

print("@@TITLE@@ " + title)
print("@@AUTHOR@@ " + author)
print("@@BODY@@")
print(body)
PY

  else
  # --- web page: fetch + readability-extract to markdown --------------------
  is_video_url "$URLV" && print -u2 \
    "$SELF: note — '$URLV' looks like a video but yt-dlp is not installed; extracting the page instead (install yt-dlp for transcripts)."
  command -v curl >/dev/null || die "curl not found"
  deftype=article
  htmlf="$(mktemp)"
  curl -fsSL --max-time 30 -A "Mozilla/5.0 (brain-clip)" "$URLV" > "$htmlf" \
    || die "fetch failed: $URLV"

  python3 - "$htmlf" "$URLV" > "$outf" <<'PY'
import sys, re
from html.parser import HTMLParser

raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()

SKIP  = {"script","style","noscript","nav","header","footer","aside","form",
         "svg","button","iframe","template","figure","figcaption"}
WS    = re.compile(r"\s+")

class Ex(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_meta=None; self.title_tag=[]; self.author=None
        self.in_title=False; self.skip=0
        self.out=[]; self.cur=[]; self.htag=None
    def starttag_skip(self, tag): return tag in SKIP
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if self.starttag_skip(tag): self.skip+=1; return
        if self.skip: return
        if tag=="title": self.in_title=True
        if tag=="meta":
            key=(a.get("property") or a.get("name") or "").lower()
            c=(a.get("content") or "").strip()
            if c and key in ("og:title","twitter:title") and not self.title_meta:
                self.title_meta=c
            if c and key in ("author","article:author","dc.creator") and not self.author:
                self.author=c
        if tag in ("h1","h2","h3","h4","h5","h6"):
            self._flush(); self.htag=int(tag[1])
        elif tag=="li":  self._flush(); self.cur.append("- ")
        elif tag=="blockquote": self._flush(); self.cur.append("> ")
        elif tag in ("p","div","section","article","br","tr","ul","ol","hr"):
            self._flush()
        elif tag in ("strong","b"): self.cur.append("**")
        elif tag in ("em","i"):     self.cur.append("*")
    def handle_endtag(self, tag):
        if tag in SKIP and self.skip: self.skip-=1; return
        if self.skip: return
        if tag=="title": self.in_title=False
        if tag in ("strong","b"): self.cur.append("**")
        elif tag in ("em","i"):   self.cur.append("*")
        if tag in ("h1","h2","h3","h4","h5","h6"):
            t="".join(self.cur).strip()
            if t and self.htag: self.out.append("#"*self.htag+" "+t)
            self.cur=[]; self.htag=None
        elif tag in ("p","li","blockquote","div","section"):
            self._flush()
    def handle_data(self, d):
        if self.in_title: self.title_tag.append(d); return
        if self.skip: return
        d=WS.sub(" ", d)
        if d.strip()=="" and not self.cur: return
        self.cur.append(d)
    def _flush(self):
        if self.htag is not None: return  # mid-heading, keep accumulating
        t="".join(self.cur).strip()
        t=re.sub(r"\*\*\s*\*\*","",t); t=re.sub(r"\*\s*\*","",t)  # drop empty emphasis
        if t: self.out.append(t)
        self.cur=[]

p=Ex()
try: p.feed(raw)
except Exception: pass
p._flush()

title=(p.title_meta or "".join(p.title_tag)).strip()
title=WS.sub(" ", title)
# many <title>s are "Article — Site"; keep the meatier left side if long enough
for sep in (" | "," — "," – "," - "," :: "):
    if sep in title:
        left=title.split(sep)[0].strip()
        if len(left)>=15: title=left
        break

body=[]
ONLY_MARKUP=re.compile(r"^[>#*\-\s]*$")        # stray "> ", "-", "###" with no words
for line in p.out:
    if not line or ONLY_MARKUP.match(line): continue
    if body and body[-1]==line: continue       # drop adjacent dupes
    body.append(line)
# collapse to blank-line-separated blocks, trim runaway boilerplate length
text="\n\n".join(body)
text=re.sub(r"\n{3,}","\n\n",text).strip()

print("@@TITLE@@ "+(title or ""))
print("@@AUTHOR@@ "+(p.author or ""))
print("@@BODY@@")
print(text)
PY
  fi

  x_title="$(sed -n 's/^@@TITLE@@ //p' "$outf" | head -1)"
  x_author="$(sed -n 's/^@@AUTHOR@@ //p' "$outf" | head -1)"
  BODY="$(sed '1,/^@@BODY@@$/d' "$outf")"

  TYPE="${TYPE_OVERRIDE:-$deftype}"
  TITLE="${TITLE_OVERRIDE:-$x_title}"
  [[ -z "$AUTHORV" ]] && AUTHORV="$x_author"
  # fallbacks if extraction came up empty
  if [[ -z "$TITLE" ]]; then
    TITLE="${URLV#*://}"; TITLE="${TITLE%%/*}"
  fi
  ID="$(unique_id "$(slugify "$TITLE")")"
  if [[ -z "${BODY// /}" ]]; then
    if [[ "$deftype" == transcript ]]; then
      BODY="> brain-clip: no captions/transcript were available for this video (or yt-dlp
> could not fetch them). The raw source is the URL above — a human can paste a transcript
> in, or \`/sync\` can note the gap."
    else
      BODY="> brain-clip: automated extraction returned no readable body. Raw source is
> the URL above; \`/sync\` (or a manual \`/capture\`) can refetch and synthesize it."
    fi
  fi
  BODY="$(prepend_note "$BODY")"
  write_md "sources/$ID.md" "$BODY"

# ============================================================================
# MODE 2 — existing file: text files inline; binaries copied + .meta.md sidecar.
# ============================================================================
elif [[ "$ARG" != "-" && -f "$ARG" ]]; then
  src="$ARG"
  ext="${src:t:e:l}"
  stem="${src:t:r}"
  TITLE="${TITLE_OVERRIDE:-$stem}"
  URLV="$URL_OVERRIDE"

  # type by extension (overridable)
  case "$ext" in
    pdf)                    deftype=pdf ;;
    png|jpg|jpeg|gif|webp|heic|tiff) deftype=screenshot ;;
    csv|tsv|json|yaml|yml|parquet)   deftype=data ;;
    txt|md|markdown|rst|org)         deftype=note ;;
    vtt|srt)                deftype=transcript ;;
    *)                      deftype=note ;;
  esac
  TYPE="${TYPE_OVERRIDE:-$deftype}"
  ID="$(unique_id "$(slugify "$stem")")"

  # Text formats become a self-contained markdown source (frontmatter + content).
  if [[ "$ext" == (txt|md|markdown|rst|org) ]]; then
    BODY="$(prepend_note "$(cat -- "$src")")"
    write_md "sources/$ID.md" "$BODY"
  else
    # Binary: copy as-is, write the frontmatter into a sidecar .meta.md.
    if (( DRYRUN )); then
      print -r -- "# --- would copy $src -> sources/$ID.$ext  (+ sources/$ID.meta.md) ---"
      emit_fm
    else
      cp -- "$src" "sources/$ID.$ext" || die "copy failed: $src"
      emit_fm > "sources/$ID.meta.md"
      print -r -- "wrote sources/$ID.$ext"
      print -r -- "wrote sources/$ID.meta.md"
    fi
  fi

# ============================================================================
# MODE 3 — pasted text / stdin: a quick note.  type: note
# ============================================================================
else
  if [[ "$ARG" == "-" ]]; then
    BODY="$(cat)"
  else
    BODY="$ARG"
  fi
  [[ -z "${BODY// /}" ]] && die "nothing to capture (empty text)"
  URLV="$URL_OVERRIDE"
  TYPE="${TYPE_OVERRIDE:-note}"
  # title from --title, else first non-empty line, trimmed to a short phrase
  if [[ -n "$TITLE_OVERRIDE" ]]; then
    TITLE="$TITLE_OVERRIDE"
  else
    first="$(print -r -- "$BODY" | sed -E 's/^#+[[:space:]]*//' | grep -m1 .)"
    TITLE="$(print -r -- "$first" | cut -c1-70)"
    [[ -z "$TITLE" ]] && TITLE="note"
  fi
  ID="$(unique_id "$(slugify "$TITLE")")"
  write_md "sources/$ID.md" "$BODY"
fi

# --- guard what we just fed (tool #3) --------------------------------------
if (( ! DRYRUN )) && [[ -x "$VAULT/bin/brain-validate.sh" ]]; then
  print -r -- "── validating ──"
  "$VAULT/bin/brain-validate.sh" --quiet || \
    print -u2 "$SELF: heads up — validator reported FAILs above; review before /sync."
fi
