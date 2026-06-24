#!/bin/zsh
# Second Brain — desktop triage window for the pull-feeder review queue (external tool #4).
# A native macOS (Tkinter) front-end for `brain-feed review`: queue on the left, item
# preview on the right, Keep/Drop/Skip as buttons + k/d/s shortcuts. Thin shell over
# bin/brain-feed-gui.py, which reuses bin/brain-feed.py for all real logic. See
# docs/external-tools.md §4.
#
#   brain-feed-gui.sh        open the review queue in a window
#
# Needs Tk: `brew install python-tk@3.14` (matches your Homebrew python3).
set -u
exec python3 "${0:A:h}/brain-feed-gui.py" "$@"
