#!/bin/zsh
# Second Brain — capture-bridge GUI installer.
#
# Builds/installs the graphical front ends that all funnel into bin/brain-clip.sh, so
# you can capture from anywhere without opening this repo. Four surfaces:
#
#   app      "Clip to Brain.app" — double-click clips the clipboard / a URL (or prompts);
#            drag files & PDFs onto it. Built with osacompile into ~/Applications.
#   folder   ~/Brain Inbox — a launchd WatchPaths agent auto-clips anything dropped in.
#   service  right-click ▸ Services ▸ "Clip to Brain" — an Automator Quick Action.
#   browser  a localhost helper (launchd) + an unpacked Chrome "Clip to Brain" extension.
#
# Usage:
#   brain-clip-gui.sh install            app + folder + service + browser helper
#   brain-clip-gui.sh app|folder|service|browser    install just that surface
#   brain-clip-gui.sh status             what's installed / loaded
#   brain-clip-gui.sh uninstall [which]  remove one surface, or all
#
# The launchd plists (bin/launchd/com.secondbrain.{clip,clipserver}.plist) and the
# extension / workflow / applescript sources live in the repo and are the source of
# truth; this just deploys them. Mirrors bin/brain-schedule.sh.
set -u

VAULT="${0:A:h:h}"
BIN="$VAULT/bin"
GUI="$BIN/gui"
SRC_LAUNCHD="$BIN/launchd"
LA_DIR="$HOME/Library/LaunchAgents"
DOMAIN="gui/$(id -u)"

APP_DEST="$HOME/Applications"
INBOX="$HOME/Brain Inbox"
SERVICES_DIR="$HOME/Library/Services"
CLIP_PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

mkdir -p "$LA_DIR" "$VAULT/.brain"

note() { print -r -- "$@" }
ok()   { print -r -- "  ✓ $*" }
warn() { print -r -- "  ! $*" >&2 }

# --- launchd helpers (same approach as brain-schedule.sh) ------------------
load_agent() {
  local label="$1" src="$SRC_LAUNCHD/$1.plist" dst="$LA_DIR/$1.plist"
  [[ -f "$src" ]] || { warn "missing plist $src"; return 1 }
  ln -sf "$src" "$dst"
  launchctl bootout "$DOMAIN/$label" 2>/dev/null
  if launchctl bootstrap "$DOMAIN" "$dst" 2>/dev/null; then ok "loaded $label"
  else launchctl load "$dst" 2>/dev/null && ok "loaded $label (legacy)" || warn "could not load $label — run: launchctl bootstrap $DOMAIN $dst"
  fi
}
unload_agent() {
  local label="$1"
  launchctl bootout "$DOMAIN/$label" 2>/dev/null || launchctl unload "$LA_DIR/$label.plist" 2>/dev/null
  rm -f "$LA_DIR/$label.plist"
  ok "removed $label"
}

# --- surface: app ----------------------------------------------------------
install_app() {
  note "▸ app — Clip to Brain.app"
  command -v osacompile >/dev/null || { warn "osacompile not found"; return 1 }
  mkdir -p "$APP_DEST"
  local tmp="$(mktemp -t cliptobrain).applescript"
  sed -e "s#@@SCRIPT@@#$BIN/brain-clip.sh#g" -e "s#@@PATH@@#$CLIP_PATH#g" \
      "$GUI/clip-to-brain.applescript" > "$tmp"
  local app="$APP_DEST/Clip to Brain.app"
  rm -rf "$app"
  if osacompile -o "$app" "$tmp" 2>/dev/null; then
    ok "built $app"
    note "    → double-click it, or drag it into the Dock / Finder toolbar."
    note "    → first run: macOS will ask to allow notifications — allow it."
  else
    warn "osacompile failed"
  fi
  rm -f "$tmp"
}
uninstall_app() { rm -rf "$APP_DEST/Clip to Brain.app" && ok "removed Clip to Brain.app" }

# --- surface: folder -------------------------------------------------------
install_folder() {
  note "▸ folder — ~/Brain Inbox"
  mkdir -p "$INBOX/_done"
  load_agent com.secondbrain.clip
  note "    → drag any file/URL into: $INBOX"
  note "    → captured items are archived to: $INBOX/_done"
}
uninstall_folder() { note "▸ folder"; unload_agent com.secondbrain.clip; note "    (left $INBOX in place — delete it yourself if you want)" }

# --- surface: service ------------------------------------------------------
install_service() {
  note "▸ service — right-click ▸ Services ▸ Clip to Brain"
  mkdir -p "$SERVICES_DIR"
  local dst="$SERVICES_DIR/Clip to Brain.workflow"
  rm -rf "$dst"
  cp -R "$GUI/clip-service/Clip to Brain.workflow" "$dst" || { warn "copy failed"; return 1 }
  ok "installed $dst"
  /System/Library/CoreServices/pbs -flush 2>/dev/null
  note "    → enable under  System Settings ▸ Keyboard ▸ Keyboard Shortcuts ▸ Services ▸ Text"
  note "    → then: select text/a link anywhere ▸ right-click ▸ Services ▸ Clip to Brain"
}
uninstall_service() { note "▸ service"; rm -rf "$SERVICES_DIR/Clip to Brain.workflow" && ok "removed Quick Action"; /System/Library/CoreServices/pbs -flush 2>/dev/null }

# --- surface: browser ------------------------------------------------------
install_browser() {
  note "▸ browser — localhost helper + Chrome extension"
  load_agent com.secondbrain.clipserver
  note "    helper: http://127.0.0.1:8766  (launchd keeps it alive)"
  note "    load the extension once:"
  note "      1. chrome://extensions  →  enable Developer mode"
  note "      2. Load unpacked  →  select:"
  note "         $GUI/chrome-extension"
  note "      3. pin “Clip to Brain”, click it on any page → Clip page"
  note "         (on a YouTube/Vimeo tab the button becomes “Clip transcript”)"
}
uninstall_browser() { note "▸ browser"; unload_agent com.secondbrain.clipserver; note "    (remove the unpacked extension from chrome://extensions yourself)" }

# --- status ----------------------------------------------------------------
status() {
  local app="$APP_DEST/Clip to Brain.app"
  [[ -d "$app" ]] && note "● app      — built ($app)" || note "○ app      — not built"
  if launchctl print "$DOMAIN/com.secondbrain.clip" >/dev/null 2>&1; then
    note "● folder   — watching $INBOX"
  else note "○ folder   — agent not loaded"; fi
  [[ -d "$SERVICES_DIR/Clip to Brain.workflow" ]] && note "● service  — installed (enable in System Settings ▸ Services)" || note "○ service  — not installed"
  if launchctl print "$DOMAIN/com.secondbrain.clipserver" >/dev/null 2>&1; then
    note "● browser  — helper loaded on :8766"
  else note "○ browser  — helper not loaded"; fi
  note ""
  note "Inbox log:  $VAULT/.brain/clip-inbox.log"
  note "Helper log: $VAULT/.brain/launchd.clipserver.log"
}

# --- dispatch --------------------------------------------------------------
case "${1:-status}" in
  install)   install_app; install_folder; install_service; install_browser
             note ""; note "All four surfaces deployed. Each just calls bin/brain-clip.sh." ;;
  app)       install_app ;;
  folder)    install_folder ;;
  service)   install_service ;;
  browser)   install_browser ;;
  status)    status ;;
  uninstall)
    case "${2:-all}" in
      app)     uninstall_app ;;
      folder)  uninstall_folder ;;
      service) uninstall_service ;;
      browser) uninstall_browser ;;
      all)     uninstall_app; uninstall_folder; uninstall_service; uninstall_browser ;;
      *) warn "unknown surface '${2:-}'"; exit 2 ;;
    esac ;;
  *) print -u2 "usage: brain-clip-gui.sh {install|app|folder|service|browser|status|uninstall [which]}"; exit 2 ;;
esac
