#!/usr/bin/env bash
# ==============================================================================
# MEDIX — Connecting Care. Saving Lives.
# Master Prototype Launcher (Backend + Frontend)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "  MEDIX — Healthcare Hackathon Prototype Launcher"
echo "  Connecting Care. Saving Lives."
echo "=========================================================="

BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Determine Python binary
if [ -d "$SCRIPT_DIR/../backend/.venv" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/../backend/.venv/bin/python3"
    UVICORN_EXEC="$SCRIPT_DIR/../backend/.venv/bin/uvicorn"
elif [ -d "$BACKEND_DIR/.venv" ]; then
    PYTHON_EXEC="$BACKEND_DIR/.venv/bin/python3"
    UVICORN_EXEC="$BACKEND_DIR/.venv/bin/uvicorn"
else
    PYTHON_EXEC="python3"
    UVICORN_EXEC="uvicorn"
fi

echo "[*] Using Python: $($PYTHON_EXEC --version)"

cleanup() {
    echo ""
    echo "[!] Shutting down MEDIX prototype services..."
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo "[✓] All servers stopped."
    exit 0
}

trap cleanup INT TERM

# 1. Start Backend Server
echo "[1/2] Launching FastAPI Backend on http://127.0.0.1:8000..."
cd "$BACKEND_DIR"
$UVICORN_EXEC app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait briefly for backend startup
sleep 2

# 2. Start Frontend HTTP Server on Port 3001
FRONTEND_PORT=3001
echo "[2/2] Launching Frontend Web Server on http://localhost:${FRONTEND_PORT}..."
echo "[*] Serving new prototype frontend from: ${FRONTEND_DIR}"
cd "$FRONTEND_DIR"
$PYTHON_EXEC -m http.server "${FRONTEND_PORT}" &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

echo ""
echo "=========================================================="
echo "  MEDIX PROTOTYPE RUNNING SUCCESSFULLY!"
echo "=========================================================="
echo "  • Frontend Web App:  http://localhost:${FRONTEND_PORT}"
echo "  • Backend API:       http://127.0.0.1:8000"
echo "  • Swagger UI Docs:   http://127.0.0.1:8000/docs"
echo "=========================================================="
echo "Press Ctrl+C to terminate both servers."
echo ""

wait
