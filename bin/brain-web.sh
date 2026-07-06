#!/usr/bin/env bash
# Launch the Second Brain web stack: FastAPI on :8787 + Vite on :5173.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  echo "Run: python3 -m venv .venv && .venv/bin/pip install fastapi 'uvicorn[standard]' httpx pytest" >&2
  exit 1
fi

if [[ ! -d "$ROOT/node_modules" ]]; then
  echo "Run: pnpm install" >&2
  exit 1
fi

exec pnpm dev
