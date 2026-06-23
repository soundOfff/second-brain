#!/bin/zsh
# Weekly: synthesize the last 7 days into a digest page, then open a PR for review.
set -u
VAULT="${0:A:h:h}"
"$VAULT/bin/brain-run.sh" "Run the /digest skill for the last 7 days, then stop. If almost nothing changed since the previous digest, write a brief note instead of a full digest. Do NOT git commit or push — leave the changes in the working tree."
exec "$VAULT/bin/brain-pr.sh" digest
