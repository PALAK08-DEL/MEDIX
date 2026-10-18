#!/usr/bin/env bash
# ==============================================================================
# MEDIX Prototype — Backend Launch Script
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Starting MEDIX Prototype Backend ==="

# Check for Python 3 virtual environment
if [ -d ".venv" ]; then
    PYTHON_EXEC=".venv/bin/python3"
    UVICORN_EXEC=".venv/bin/uvicorn"
elif [ -d "../../backend/.venv" ]; then
    PYTHON_EXEC="../../backend/.venv/bin/python3"
    UVICORN_EXEC="../../backend/.venv/bin/uvicorn"
else
    echo "[!] Creating local virtual environment in .venv..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
    PYTHON_EXEC=".venv/bin/python3"
    UVICORN_EXEC=".venv/bin/uvicorn"
fi

echo "[*] Using Python: $($PYTHON_EXEC --version)"
echo "[*] Launching Uvicorn on http://127.0.0.1:8000..."
echo "[*] Interactive Swagger UI: http://127.0.0.1:8000/docs"

exec $UVICORN_EXEC app.main:app --host 127.0.0.1 --port 8000 --reload
