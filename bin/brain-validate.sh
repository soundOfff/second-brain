#!/bin/zsh
# Second Brain — contract validator.
#
#   bin/brain-validate.sh            validate the whole repo
#   bin/brain-validate.sh --quiet    print only FAIL/WARN lines + summary
#
# Checks the DETERMINISTIC subset of the CLAUDE.md schema — the mechanical rules a
# headless `claude -p` run could break silently. It does NOT make judgment calls
# (contradictions, starved stubs, stale dates) — that is /lint's job. Pair this with a
# git pre-commit hook so malformed pages never land.
#
# Exit status: 0 if no FAILs (WARNs allowed), 1 if any FAIL.
#
# FAIL  = a hard contract violation (missing/invalid frontmatter, bad slug, broken
#         citation, id != filename stem, updated < created).
# WARN  = a dangling [[wikilink]]. CLAUDE.md ALLOWS these — they signal a page worth
#         creating — so they never fail the build, only surface.
set -u
setopt null_glob

VAULT="${0:A:h:h}"
cd "$VAULT" || { print -u2 "ERROR: cannot cd to $VAULT"; exit 2; }

QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1

FAILS=0 WARNS=0 NFILES=0
fail() { print -r -- "  FAIL  $1"; ((FAILS++)) }
warn() { print -r -- "  WARN  $1"; ((WARNS++)) }
ok()   { (( QUIET )) || print -r -- "  ok    $1" }

# --- helpers ---------------------------------------------------------------
# Lines strictly between the first and second `---` (empty if no leading `---`).
frontmatter() { awk 'NR==1 && $0!="---"{exit} /^---$/{c++; next} c==1{print} c==2{exit}' "$1" }
# Body after the closing `---`, with inline `code` and [[wikilinks]] details preserved.
body()        { awk '/^---$/{c++; next} c>=2{print}' "$1" }
# Value of a flat `key: value` frontmatter line, quotes/whitespace stripped.
fmval() { grep -E "^$2:" <<<"$1" | head -1 | sed -E "s/^$2:[[:space:]]*//; s/^\"(.*)\"\$/\1/; s/[[:space:]]*\$//" }

is_date()  { [[ "$1" =~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' ]] }
is_kebab() { [[ "$1" =~ '^[a-z0-9]+(-[a-z0-9]+)*$' ]] }
in_set()   { [[ " $2 " == *" $1 "* ]] }

SRC_TYPES="article pdf transcript screenshot note data"
WIKI_TYPES="entity concept recap digest index"
STATUSES="stub active stable"

# --- 1. build the set of known source IDs ----------------------------------
typeset -A SRCIDS
for f in sources/**/*(.); do
  base="${f:t}"
  [[ "$base" == README.md ]] && continue
  if [[ "$base" == *.meta.md ]]; then stem="${base%.meta.md}"; else stem="${base%.*}"; fi
  SRCIDS[$stem]=1
done

# --- 2. validate sources/ frontmatter --------------------------------------
(( QUIET )) || print -r -- "sources/"
for f in sources/**/*.md(.); do
  base="${f:t}"
  [[ "$base" == README.md ]] && continue
  ((NFILES++))
  fm="$(frontmatter "$f")"
  if [[ -z "$fm" ]]; then fail "$f: missing frontmatter block"; continue; fi
  if [[ "$base" == *.meta.md ]]; then stem="${base%.meta.md}"; else stem="${base%.md}"; fi
  before=$FAILS
  for key in id title type captured; do
    [[ -n "$(fmval "$fm" "$key")" ]] || fail "$f: missing required key '$key'"
  done
  id="$(fmval "$fm" id)"
  [[ -n "$id" && "$id" != "$stem" ]] && fail "$f: id '$id' != filename stem '$stem'"
  t="$(fmval "$fm" type)"
  [[ -n "$t" ]] && ! in_set "$t" "$SRC_TYPES" && fail "$f: invalid source type '$t'"
  cap="$(fmval "$fm" captured)"
  [[ -n "$cap" ]] && ! is_date "$cap" && fail "$f: captured '$cap' is not YYYY-MM-DD"
  (( FAILS == before )) && ok "$f"
done

# --- 3. validate wiki/ pages (+ root index.md) -----------------------------
(( QUIET )) || print -r -- "wiki/"
wiki_files=(wiki/**/*.md(.))
[[ -f index.md ]] && wiki_files+=(index.md)
for f in $wiki_files; do
  base="${f:t}"
  [[ "$base" == README.md ]] && continue
  ((NFILES++))
  slug="${base%.md}"
  fm="$(frontmatter "$f")"
  if [[ -z "$fm" ]]; then fail "$f: missing frontmatter block"; continue; fi
  before=$FAILS bwarn=$WARNS

  for key in type title created updated status sources tags; do
    [[ -n "$(fmval "$fm" "$key")" ]] || fail "$f: missing required key '$key'"
  done
  is_kebab "$slug" || fail "$f: slug '$slug' is not kebab-case"

  t="$(fmval "$fm" type)"
  [[ -n "$t" ]] && ! in_set "$t" "$WIKI_TYPES" && fail "$f: invalid type '$t'"
  st="$(fmval "$fm" status)"
  [[ -n "$st" ]] && ! in_set "$st" "$STATUSES" && fail "$f: invalid status '$st'"

  cr="$(fmval "$fm" created)"; up="$(fmval "$fm" updated)"
  [[ -n "$cr" ]] && ! is_date "$cr" && fail "$f: created '$cr' is not YYYY-MM-DD"
  [[ -n "$up" ]] && ! is_date "$up" && fail "$f: updated '$up' is not YYYY-MM-DD"
  if is_date "$cr" && is_date "$up" && [[ "$up" < "$cr" ]]; then
    fail "$f: updated ($up) is before created ($cr)"
  fi

  # frontmatter `sources: [...]` must each map to a real source file
  srcs="$(fmval "$fm" sources)"; srcs="${srcs//[\[\]]/}"
  for s in ${(s:,:)srcs}; do
    s="${s// /}"; [[ -z "$s" ]] && continue
    [[ -n "${SRCIDS[$s]:-}" ]] || fail "$f: sources entry '$s' has no file in sources/"
  done

  # body: strip inline `code` and [[wikilinks]] so examples aren't read as citations
  bd="$(body "$f")"
  cite_text="$(print -r -- "$bd" | sed -E 's/`[^`]*`//g; s/\[\[[^]]*\]\]//g')"
  for c in ${(f)"$(print -r -- "$cite_text" | grep -oE '\[[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+\]' | sort -u)"}; do
    cid="${c//[\[\]]/}"
    [[ -n "${SRCIDS[$cid]:-}" ]] || fail "$f: cites unknown source id '$cid'"
  done

  # body: dangling wikilinks -> WARN only (strip inline code first)
  link_text="$(print -r -- "$bd" | sed -E 's/`[^`]*`//g')"
  for l in ${(f)"$(print -r -- "$link_text" | grep -oE '\[\[[^]]+\]\]' | sort -u)"}; do
    tgt="${l//[\[\]]/}"; tgt="${tgt%%|*}"; tgt="${tgt%%#*}"
    [[ -z "$tgt" ]] && continue
    if [[ "$tgt" == "index" ]]; then
      [[ -f index.md || -f wiki/index.md ]] || warn "$f: dangling wikilink [[$tgt]]"
    else
      [[ -f "wiki/$tgt.md" ]] || warn "$f: dangling wikilink [[$tgt]] — page worth creating?"
    fi
  done

  (( FAILS == before && WARNS == bwarn )) && ok "$f"
done

# --- summary ---------------------------------------------------------------
print -r -- "──────────────────────────────────────────────"
print -r -- "$NFILES files · $FAILS fail · $WARNS warn"
(( FAILS > 0 )) && exit 1 || exit 0
