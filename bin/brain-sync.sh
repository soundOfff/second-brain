#!/bin/zsh
# Nightly: reconcile any sources dropped into sources/ since the last run.
exec "$(dirname "$0")/brain-run.sh" "Run the /sync skill to reconcile any unprocessed sources into the wiki, then stop. If there is no backlog, do nothing and say so."
