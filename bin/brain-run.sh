#!/bin/zsh
# Run one second-brain skill headlessly. Used by cron and the shell aliases.
# Usage: brain-run.sh "<prompt for claude>"   e.g.  brain-run.sh "/sync"
#
# Runs `claude` non-interactively in the vault with permissions bypassed, because
# nobody is at the keyboard to approve edits during a scheduled run. Output is appended
# to .brain/cron.log so every autonomous run is auditable.

set -u
VAULT="/Users/User/Tomi/second-brain"
export PATH="/Users/User/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

PROMPT="${1:?usage: brain-run.sh \"<prompt>\"}"
LOG="$VAULT/.brain/cron.log"
ts="$(date "+%Y-%m-%d %H:%M:%S")"

cd "$VAULT" || { echo "[$ts] ERROR: cannot cd to $VAULT" >>"$LOG"; exit 1; }

{
  echo "──────────────────────────────────────────────"
  echo "[$ts] RUN: $PROMPT"
} >>"$LOG"

claude -p "$PROMPT" \
  --permission-mode bypassPermissions \
  >>"$LOG" 2>&1
status=$?

echo "[$(date "+%Y-%m-%d %H:%M:%S")] EXIT $status" >>"$LOG"
exit $status
