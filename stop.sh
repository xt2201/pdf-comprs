#!/bin/bash
# =============================================================================
# PDF Compression Tool - Stop Script
# =============================================================================
# Stops both backend and frontend servers
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$SCRIPT_DIR/.pids"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================================"
echo "  PDF Compression Tool - Stopping"
echo "============================================================"

# Function to kill process and its children
kill_process_tree() {
    local pid=$1
    local name=$2
    
    if ps -p $pid > /dev/null 2>&1; then
        # Kill child processes first
        pkill -P $pid 2>/dev/null || true
        # Kill the main process
        kill $pid 2>/dev/null || true
        sleep 1
        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null || true
        fi
        echo -e "${GREEN}✓ $name stopped (PID: $pid)${NC}"
    else
        echo -e "${YELLOW}⚠ $name was not running${NC}"
    fi
}

# Function to kill all processes on a port
kill_port() {
    local port=$1
    local name=$2
    local pids=$(lsof -t -i:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        echo "$pids" | xargs -r kill -9 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}✓ Cleaned up all processes on port $port ($name)${NC}"
    fi
}

# Stop Backend
if [ -f "$PID_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$PID_DIR/backend.pid")
    kill_process_tree $BACKEND_PID "Backend"
    rm -f "$PID_DIR/backend.pid"
else
    echo -e "${YELLOW}⚠ Backend PID file not found${NC}"
fi

# Stop Frontend
if [ -f "$PID_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
    kill_process_tree $FRONTEND_PID "Frontend"
    rm -f "$PID_DIR/frontend.pid"
else
    echo -e "${YELLOW}⚠ Frontend PID file not found${NC}"
fi

# Ensure all processes on ports are killed
kill_port 8007 "Backend"
kill_port 3007 "Frontend"

echo ""
echo "============================================================"
echo -e "${GREEN}✓ Application stopped${NC}"
echo "============================================================"
