#!/bin/zsh
# Open a pull request for whatever the autonomous brain just wrote.
#
# The scheduled /sync and /digest runs edit the wiki with nobody at the keyboard. We do
# NOT want those edits landing on main unreviewed — the human reads the synthesized
# content and decides whether it is faithful. So instead of committing to main, this
# script moves the working-tree changes onto a fresh branch and opens a PR for review.
#
#   brain-pr.sh sync      # branch brain/sync-<stamp>   -> PR
#   brain-pr.sh digest    # branch brain/digest-<stamp> -> PR
#
# Safety: it validates the contract first (same checks as the pre-commit hook). If the
# brain produced something that breaks the schema, it leaves the edits uncommitted on
# the current branch and logs loudly rather than pushing broken content.
#
# Note: each run opens its own PR. Merge promptly — if a sync PR is still open at the
# next nightly run, the same sources are still "unprocessed" on main and will be
# reconciled again into a second PR.
set -u
VAULT="${0:A:h:h}"
export PATH="/Users/User/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
cd "$VAULT" || { print -u2 "ERROR: cannot cd to $VAULT"; exit 2; }
LOG="$VAULT/.brain/cron.log"
ts() { date "+%Y-%m-%d %H:%M:%S" }

KIND="${1:?usage: brain-pr.sh <sync|digest>}"

# Nothing changed -> nothing to review.
if [[ -z "$(git status --porcelain)" ]]; then
  echo "[$(ts)] PR($KIND): no changes — skipping." >>"$LOG"
  exit 0
fi

# Validate before touching git. On failure, leave the edits where they are for a human.
if ! python3 "$VAULT/bin/brain_tidy.py" --quiet >>"$LOG" 2>&1; then
  echo "[$(ts)] PR($KIND): validation FAILED — leaving edits uncommitted for manual review." >>"$LOG"
  exit 1
fi

# Resolve the base branch (origin/HEAD, falling back to main).
default="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"
default="${default:-main}"

stamp="$(date "+%Y%m%d-%H%M%S")"
branch="brain/$KIND-$stamp"
title="brain($KIND): content update $stamp"

# Create the branch (carries the uncommitted edits with it) and stage everything.
git switch -c "$branch" >>"$LOG" 2>&1 || { echo "[$(ts)] PR($KIND): branch create failed." >>"$LOG"; exit 1; }
git add -A >>"$LOG" 2>&1

files="$(git diff --cached --name-only)"
n="$(print -r -- "$files" | grep -c .)"

if ! git commit -m "$title" \
      -m "Autonomous /$KIND run on $(ts). $n file(s) changed. Review the wiki content before merging." \
      >>"$LOG" 2>&1; then
  echo "[$(ts)] PR($KIND): commit failed — leaving branch $branch for inspection." >>"$LOG"
  exit 1
fi

if ! git push -u origin "$branch" >>"$LOG" 2>&1; then
  echo "[$(ts)] PR($KIND): push failed for $branch." >>"$LOG"
  git switch "$default" >>"$LOG" 2>&1
  exit 1
fi

body="$(printf 'Autonomous `/%s` run on %s.\n\n## Files changed (%s)\n\n```\n%s\n```\n\nReview the synthesized wiki content, then merge if it reads faithfully.\n' \
  "$KIND" "$(ts)" "$n" "$files")"

if gh pr create --base "$default" --head "$branch" --title "$title" --body "$body" >>"$LOG" 2>&1; then
  echo "[$(ts)] PR($KIND): opened for $branch ($n file(s))." >>"$LOG"
else
  echo "[$(ts)] PR($KIND): gh pr create failed for $branch (pushed, open the PR manually)." >>"$LOG"
fi

# Return to the base branch so the next run starts from a clean main.
git switch "$default" >>"$LOG" 2>&1
