#!/bin/bash
# Stop Playwright MCP server
# Usage: ./stop-server.sh [port]

PORT=${1:-8808}
PID_FILE="/tmp/playwright-mcp-${PORT}.pid"
SCRIPT_DIR="$(dirname "$0")"

cleanup_all() {
    local killed=0

    # Kill by PID file
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            # First close the browser gracefully
            python3 "$SCRIPT_DIR/mcp-client.py" call -u "http://localhost:${PORT}" -t browser_close -p '{}' 2>/dev/null || true
            sleep 0.5

            # Then kill the server
            kill "$PID" 2>/dev/null
            sleep 1

            # Force kill if still running
            kill -9 "$PID" 2>/dev/null || true
            killed=1
        fi
        rm -f "$PID_FILE"
    fi

    # Kill by process name (catches orphaned processes)
    if pkill -f "@playwright/mcp.*--port.*${PORT}" 2>/dev/null; then
        killed=1
    fi

    # Kill any process holding the port
    local pids=$(lsof -ti:"$PORT" 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs -r kill -9 2>/dev/null
        killed=1
    fi

    if [ $killed -eq 1 ]; then
        echo "Playwright MCP stopped (port $PORT)"
    else
        echo "Playwright MCP not running (port $PORT)"
    fi
}

cleanup_all
