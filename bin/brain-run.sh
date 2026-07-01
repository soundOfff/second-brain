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

# Resolve the model for this unattended run: an explicit BRAIN_MODEL env var wins;
# otherwise the `model` key in .brain/config.json (set from the GUI Settings screen).
# Empty => pass no --model, so `claude` falls back to the user's own default.
MODEL="${BRAIN_MODEL:-}"
if [[ -z "$MODEL" && -f "$VAULT/.brain/config.json" ]]; then
  MODEL="$(python3 -c 'import json,sys
try: print((json.load(open(sys.argv[1])).get("model") or "").strip())
except Exception: pass' "$VAULT/.brain/config.json" 2>/dev/null)"
fi

cmd=(claude -p "$PROMPT" --permission-mode bypassPermissions)
if [[ -n "$MODEL" ]]; then
  cmd+=(--model "$MODEL")
  echo "[$ts] MODEL: $MODEL" >>"$LOG"
fi

"${cmd[@]}" >>"$LOG" 2>&1
status=$?

echo "[$(date "+%Y-%m-%d %H:%M:%S")] EXIT $status" >>"$LOG"
exit $status
