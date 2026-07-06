#!/usr/bin/env bash
# Dev launcher for the FastAPI backend (apps/api). Binds :8787 so Vite's proxy works.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VENV="$ROOT/.venv/bin/python"
if [[ ! -x "$VENV" ]]; then
  echo "Missing .venv — run: python3 -m venv .venv && .venv/bin/pip install fastapi 'uvicorn[standard]' httpx pytest" >&2
  exit 1
fi

exec "$VENV" -m uvicorn apps.api.main:app --reload --port 8787
