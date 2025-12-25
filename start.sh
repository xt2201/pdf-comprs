#!/bin/bash
# =============================================================================
# PDF Compression Tool - Start Script
# =============================================================================
# Starts both backend and frontend servers
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
PID_DIR="$SCRIPT_DIR/.pids"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create PID directory
mkdir -p "$PID_DIR"

echo "============================================================"
echo "  PDF Compression Tool - Starting"
echo "============================================================"

# Source uv environment if available
if [ -f "$HOME/.local/bin/env" ]; then
    source "$HOME/.local/bin/env"
fi

# Check if already running
if [ -f "$PID_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$PID_DIR/backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Backend already running (PID: $BACKEND_PID)${NC}"
    else
        rm "$PID_DIR/backend.pid"
    fi
fi

if [ -f "$PID_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Frontend already running (PID: $FRONTEND_PID)${NC}"
    else
        rm "$PID_DIR/frontend.pid"
    fi
fi

# Start Backend
if [ ! -f "$PID_DIR/backend.pid" ]; then
    echo -e "${GREEN}🚀 Starting backend server...${NC}"
    cd "$BACKEND_DIR"
    nohup uv run uvicorn src.main:app --host 0.0.0.0 --port 8007 --reload > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PID_DIR/backend.pid"
    echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
    echo "  Logs: $SCRIPT_DIR/logs/backend.log"
fi

# Start Frontend
if [ ! -f "$PID_DIR/frontend.pid" ]; then
    echo -e "${GREEN}🎨 Starting frontend server...${NC}"
    cd "$FRONTEND_DIR"
    nohup npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PID_DIR/frontend.pid"
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo "  Logs: $SCRIPT_DIR/logs/frontend.log"
fi

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

echo ""
echo "============================================================"
echo -e "${GREEN}✓ Application started successfully!${NC}"
echo "============================================================"
echo ""
echo "  Frontend: http://localhost:3007"
echo "  Backend:  http://localhost:8007"
echo "  API Docs: http://localhost:8007/api/docs"
echo ""
echo "  To stop: ./stop.sh"
echo "  Logs:    ./logs/"
echo ""
