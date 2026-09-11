#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f "server/.env" ]; then
  cp "server/.env.example" "server/.env"
  echo "[SceneForge] Created server/.env"
  echo "Fill in DEEPSEEK_API_KEY, QWEN_API_KEY and MESHY_API_KEY, then run ./run.sh again."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "[SceneForge] Creating local Python environment..."
  python3 -m venv .venv
fi

echo "[SceneForge] Installing/updating dependencies..."
.venv/bin/python -m pip install -q -r server/requirements.txt

echo "[SceneForge] Starting at http://127.0.0.1:8000"
if command -v open >/dev/null 2>&1; then
  (sleep 1; open http://127.0.0.1:8000) &
elif command -v xdg-open >/dev/null 2>&1; then
  (sleep 1; xdg-open http://127.0.0.1:8000) &
fi
exec .venv/bin/python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
