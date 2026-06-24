#!/bin/zsh
# Second Brain — pull feeder (external tool #4). Thin wrapper over bin/brain-feed.py.
# Subscribes to feeds (feeds.toml) and deposits new material into sources/ (trusted) or
# .brain/review/ (queued) — no LLM; the nightly /sync folds it in. See docs/external-tools.md §4.
#
#   brain-feed.sh run [--dry-run] [--feed ID]   poll feeds, deposit/queue new items
#   brain-feed.sh review                         triage the queue (keep/drop/skip)
#   brain-feed.sh status                         show feeds, seen counts, queue size
set -u
exec python3 "${0:A:h}/brain-feed.py" "$@"
