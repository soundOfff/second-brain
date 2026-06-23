#!/bin/zsh
# Manage the Second Brain launchd schedule (macOS).
#
#   brain-schedule.sh install     symlink + load both agents into your user domain
#   brain-schedule.sh uninstall   unload + remove the symlinks
#   brain-schedule.sh status      show whether each agent is loaded and its last run
#   brain-schedule.sh run sync     fire the sync agent once, now (kickstart)
#   brain-schedule.sh run digest   fire the digest agent once, now (kickstart)
#
# The plists live in the repo (bin/launchd/*.plist) and are the single source of
# truth; install symlinks them into ~/Library/LaunchAgents so edits in the repo take
# effect on the next reload. Schedule: sync nightly 02:00, digest Mondays 09:00.
set -u

VAULT="/Users/User/Tomi/second-brain"
SRC_DIR="$VAULT/bin/launchd"
LA_DIR="$HOME/Library/LaunchAgents"
DOMAIN="gui/$(id -u)"
AGENTS=(com.secondbrain.sync com.secondbrain.digest)

mkdir -p "$LA_DIR" "$VAULT/.brain"

install() {
  for label in $AGENTS; do
    local src="$SRC_DIR/$label.plist"
    local dst="$LA_DIR/$label.plist"
    if [[ ! -f "$src" ]]; then
      echo "ERROR: missing plist $src" >&2; return 1
    fi
    ln -sf "$src" "$dst"
    # Replace any previously-loaded copy, then load fresh.
    launchctl bootout "$DOMAIN/$label" 2>/dev/null
    if launchctl bootstrap "$DOMAIN" "$dst" 2>/dev/null; then
      echo "loaded  $label"
    else
      # Fallback for older macOS.
      launchctl unload "$dst" 2>/dev/null
      launchctl load "$dst" && echo "loaded  $label (legacy)"
    fi
  done
  echo "Done. sync → nightly 02:00, digest → Mondays 09:00."
}

uninstall() {
  for label in $AGENTS; do
    launchctl bootout "$DOMAIN/$label" 2>/dev/null \
      || launchctl unload "$LA_DIR/$label.plist" 2>/dev/null
    rm -f "$LA_DIR/$label.plist"
    echo "removed $label"
  done
}

status() {
  for label in $AGENTS; do
    if launchctl print "$DOMAIN/$label" >/dev/null 2>&1; then
      echo "● $label — loaded"
    else
      echo "○ $label — not loaded"
    fi
  done
  echo
  echo "Recent headless runs (.brain/cron.log):"
  tail -n 12 "$VAULT/.brain/cron.log" 2>/dev/null || echo "  (no runs yet)"
}

run_now() {
  local which="${1:?usage: brain-schedule.sh run <sync|digest>}"
  local label="com.secondbrain.$which"
  launchctl kickstart -k "$DOMAIN/$label" \
    && echo "kickstarted $label — see .brain/cron.log"
}

case "${1:-status}" in
  install)   install ;;
  uninstall) uninstall ;;
  status)    status ;;
  run)       run_now "${2:-}" ;;
  *) echo "usage: brain-schedule.sh {install|uninstall|status|run <sync|digest>}" >&2; exit 2 ;;
esac
