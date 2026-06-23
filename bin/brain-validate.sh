#!/bin/zsh
# Second Brain — contract validator (compatibility shim).
#
# The deterministic checks now live in bin/brain_tidy.py (the single source of truth —
# importable SDK + CLI; see docs/adr/0001). This script stays as a thin wrapper so the
# pre-commit hook, the README, and muscle memory keep working.
#
#   bin/brain-validate.sh                 validate the whole repo (exit 1 on any FAIL)
#   bin/brain-validate.sh --quiet         only FAIL/WARN lines + summary (pre-commit hook)
#   bin/brain-validate.sh --install-hook  symlink the repo's pre-commit hook into .git
#
# For the auto-fix half (`tidy --fix`) and the backlog gate, call brain_tidy.py directly.
set -u
VAULT="${0:A:h:h}"
cd "$VAULT" || { print -u2 "ERROR: cannot cd to $VAULT"; exit 2; }

if [[ "${1:-}" == "--install-hook" ]]; then
  [[ -d "$VAULT/.git" ]] || { print -u2 "ERROR: $VAULT is not a git repo"; exit 2; }
  mkdir -p "$VAULT/.git/hooks"
  ln -sf "../../bin/hooks/pre-commit" "$VAULT/.git/hooks/pre-commit"
  print -r -- "installed pre-commit hook -> bin/hooks/pre-commit"
  exit 0
fi

exec python3 "$VAULT/bin/brain_tidy.py" "$@"
