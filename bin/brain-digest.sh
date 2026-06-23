#!/bin/zsh
# Weekly: synthesize the last 7 days into a digest page.
exec "$(dirname "$0")/brain-run.sh" "Run the /digest skill for the last 7 days, then stop. If almost nothing changed since the previous digest, write a brief note instead of a full digest."
