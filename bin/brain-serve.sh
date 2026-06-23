#!/bin/zsh
# Serve the wiki read-only in a browser (external tool #2). Usage: brain-serve.sh [port]
# Renders wiki/**.md + index.md, resolves [[wikilinks]] and [src-id] citations, shows
# backlinks, surfaces stubs + dangling links. No writes, no LLM. Ctrl-C to stop.
set -u
exec python3 "${0:A:h}/brain-serve.py" "$@"
