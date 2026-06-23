#!/bin/zsh
# Capture a source into the vault from anywhere, without opening the vault first.
# Usage:
#   brain-capture <url>
#   brain-capture /path/to/file.pdf
#   brain-capture "some pasted text to remember"
set -u
ARG="${*:?usage: brain-capture <url | file | \"text\">}"
exec "$(dirname "$0")/brain-run.sh" "/capture $ARG"
