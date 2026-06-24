#!/bin/zsh
# Manage the Second Brain pull-feeder schedule (macOS launchd).
#
#   brain-feed-schedule.sh install     symlink + load the feed agent into your user domain
#   brain-feed-schedule.sh uninstall   unload + remove the symlink
#   brain-feed-schedule.sh status      whether the agent is loaded + the feeder's own status
#   brain-feed-schedule.sh run         fire the feed poll once, now (kickstart)
#
# The plist lives in the repo (bin/launchd/com.secondbrain.feed.plist) and is the single
# source of truth; install symlinks it into ~/Library/LaunchAgents so repo edits take
# effect on the next reload. Schedule: poll daily at 01:30 — just before the 02:00 /sync,
# so trusted deposits ride the same night's fold and the review queue waits each morning.
#
# This agent runs plain python/shell — no `claude`, no bypassPermissions — so unlike the
# sync/digest agents it carries no special-privilege caveat. It is OPT-IN: the feeder is
# always hand-runnable via `bin/brain-feed.sh run`; install only if you want the cron.
set -u

VAULT="/Users/User/Tomi/second-brain"
SRC_DIR="$VAULT/bin/launchd"
LA_DIR="$HOME/Library/LaunchAgents"
DOMAIN="gui/$(id -u)"
LABEL="com.secondbrain.feed"

mkdir -p "$LA_DIR" "$VAULT/.brain"

install() {
  local src="$SRC_DIR/$LABEL.plist"
  local dst="$LA_DIR/$LABEL.plist"
  [[ -f "$src" ]] || { echo "ERROR: missing plist $src" >&2; return 1; }
  ln -sf "$src" "$dst"
  launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null
  if launchctl bootstrap "$DOMAIN" "$dst" 2>/dev/null; then
    echo "loaded  $LABEL"
  else
    launchctl unload "$dst" 2>/dev/null
    launchctl load "$dst" && echo "loaded  $LABEL (legacy)"
  fi
  echo "Done. feed → daily 01:30."
}

uninstall() {
  launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null \
    || launchctl unload "$LA_DIR/$LABEL.plist" 2>/dev/null
  rm -f "$LA_DIR/$LABEL.plist"
  echo "removed $LABEL"
}

status() {
  if launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; then
    echo "● $LABEL — loaded (daily 01:30)"
  else
    echo "○ $LABEL — not loaded"
  fi
  echo
  python3 "$VAULT/bin/brain-feed.py" status 2>/dev/null
  echo
  echo "Recent feed runs (.brain/feed.log):"
  tail -n 12 "$VAULT/.brain/feed.log" 2>/dev/null || echo "  (no runs yet)"
}

run_now() {
  launchctl kickstart -k "$DOMAIN/$LABEL" \
    && echo "kickstarted $LABEL — see .brain/feed.log"
}

case "${1:-status}" in
  install)   install ;;
  uninstall) uninstall ;;
  status)    status ;;
  run)       run_now ;;
  *) echo "usage: brain-feed-schedule.sh {install|uninstall|status|run}" >&2; exit 2 ;;
esac
