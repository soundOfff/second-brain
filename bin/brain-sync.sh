#!/bin/zsh
# Nightly: tidy deterministically first, then reconcile the backlog with Claude — but
# only invoke Claude if there is actually a backlog (see docs/adr/0001). This keeps the
# mechanical cleanup free and spends tokens only when there are unprocessed sources.
set -u
VAULT="${0:A:h:h}"
export PATH="/Users/User/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
LOG="$VAULT/.brain/cron.log"
ts() { date "+%Y-%m-%d %H:%M:%S" }

# 1. Deterministic tidy pass (no Claude): apply safe fixes, log the result.
{
  echo "──────────────────────────────────────────────"
  echo "[$(ts)] TIDY (deterministic --fix)"
  python3 "$VAULT/bin/brain_tidy.py" --fix
} >>"$LOG" 2>&1

# 2. Only call Claude if there is unprocessed work.
backlog="$(python3 "$VAULT/bin/brain_tidy.py" --backlog)"
if [[ -z "$backlog" ]]; then
  echo "[$(ts)] SYNC: backlog empty — skipping Claude." >>"$LOG"
  exit 0
fi

n="$(print -r -- "$backlog" | grep -c .)"
echo "[$(ts)] SYNC: $n unprocessed source(s) — invoking Claude /sync." >>"$LOG"
"$VAULT/bin/brain-run.sh" "Run the /sync skill to reconcile any unprocessed sources into the wiki, then stop. If there is no backlog, do nothing and say so. Do NOT git commit or push — leave the changes in the working tree."

# 3. Open a PR with whatever the brain wrote, for the human to review and merge.
exec "$VAULT/bin/brain-pr.sh" sync
