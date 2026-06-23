#!/bin/zsh
# Second Brain — watched-inbox processor (capture-bridge GUI surface #2).
#
# Drives bin/brain-clip.sh over every file dropped into an inbox folder, then archives
# the original into <inbox>/_done/ so it is not reprocessed. Wired to a launchd
# WatchPaths agent (bin/launchd/com.secondbrain.clip.plist) so a Finder drag — or a
# share-sheet "Save to folder" pointed at the inbox — auto-captures with no keyboard in
# the repo. Idempotent and serialized by a lock, since WatchPaths can fire several times
# for one batch of drops.
#
#   brain-clip-watch.sh [<inbox-dir>]      default: ~/Brain Inbox
set -u
setopt null_glob extended_glob

VAULT="${0:A:h:h}"
CLIP="$VAULT/bin/brain-clip.sh"
INBOX="${1:-$HOME/Brain Inbox}"
DONE="$INBOX/_done"
LOG="$VAULT/.brain/clip-inbox.log"

mkdir -p "$INBOX" "$DONE" "$VAULT/.brain"
log() { print -r -- "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG" }

# Serialize: if another run holds the lock, exit (it will sweep what we see too).
LOCK="$VAULT/.brain/clip-inbox.lock"
if ! ( set -o noclobber; : > "$LOCK" ) 2>/dev/null; then
  exit 0
fi
trap 'rm -f "$LOCK"' EXIT

# A .webloc (plist) or .url (INI) holds a link → clip the URL, not the file.
extract_url() {
  local f="$1"
  case "${f:e:l}" in
    webloc) /usr/bin/plutil -extract URL raw -o - "$f" 2>/dev/null ;;
    url)    grep -iE '^URL=' "$f" | head -1 | sed -E 's/^URL=//I; s/[[:space:]]*$//' ;;
  esac
}

processed=0
for f in "$INBOX"/*(.N); do          # regular files in the top level only
  base="${f:t}"
  [[ "$base" == .* || "$base" == _* ]] && continue   # skip dotfiles / our own markers

  url="$(extract_url "$f")"
  if [[ -n "$url" ]]; then
    out="$("$CLIP" "$url" 2>&1)"
  else
    out="$("$CLIP" "$f" 2>&1)"
  fi
  rc=$?

  if (( rc == 0 )); then
    # Archive the original under a timestamp so re-drops of the same name don't clash.
    mv -f "$f" "$DONE/$(date '+%Y%m%d-%H%M%S')-$base" 2>/dev/null
    log "OK   $base -> ${url:-file}; $(print -r -- "$out" | grep '^wrote' | head -1)"
    (( processed++ ))
  else
    log "FAIL $base: $(print -r -- "$out" | tail -1)"
  fi
done

(( processed > 0 )) && log "swept $processed item(s)"
exit 0
