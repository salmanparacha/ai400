#!/bin/bash
# Start Playwright MCP server for browsing-with-playwright skill
# Usage: ./start-server.sh [port] [--headed]
#
# Options:
#   --headed    Force visible browser window (overrides auto-detection)
#
# Auto-detects headless environments (WSL, SSH, CI) and configures appropriately

PORT=${1:-8808}
FORCE_HEADED=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --headed)
            FORCE_HEADED=true
            ;;
    esac
done
PID_FILE="/tmp/playwright-mcp-${PORT}.pid"
SCRIPT_DIR="$(dirname "$0")"

# --- Environment Detection ---

detect_headless() {
    # Check for display
    [ -z "$DISPLAY" ] && return 0
    # Check for WSL
    grep -qi microsoft /proc/version 2>/dev/null && return 0
    # Check for SSH session
    [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ] && return 0
    # Check for CI environments
    [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ] && return 0
    return 1
}

find_chromium() {
    # Check common Playwright cache locations
    local playwright_cache="$HOME/.cache/ms-playwright"

    # Look for chromium executable in Playwright cache
    if [ -d "$playwright_cache" ]; then
        # Find the latest chromium version
        local chromium_dir=$(ls -d "$playwright_cache"/chromium-* 2>/dev/null | sort -V | tail -1)
        if [ -n "$chromium_dir" ]; then
            # Check both possible paths
            for subdir in "chrome-linux64" "chrome-linux"; do
                local exec_path="$chromium_dir/$subdir/chrome"
                if [ -x "$exec_path" ]; then
                    echo "$exec_path"
                    return 0
                fi
            done
        fi
    fi

    # Check system paths
    for cmd in chromium chromium-browser google-chrome google-chrome-stable; do
        if command -v "$cmd" &>/dev/null; then
            command -v "$cmd"
            return 0
        fi
    done

    return 1
}

# --- Cleanup ---

cleanup_port() {
    # Kill any existing process on the port
    local pids=$(lsof -ti:"$PORT" 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "Cleaning up existing processes on port $PORT..."
        echo "$pids" | xargs -r kill -9 2>/dev/null
        sleep 1
    fi

    # Also kill by process name
    pkill -f "@playwright/mcp.*--port.*$PORT" 2>/dev/null || true

    # Clean stale PID file
    rm -f "$PID_FILE"
}

# --- Main ---

# Check if already running and healthy
if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    # Verify it's actually responding
    if python3 "$SCRIPT_DIR/verify.py" 2>/dev/null; then
        echo "Playwright MCP already running on port $PORT (PID: $(cat $PID_FILE))"
        exit 0
    else
        echo "Stale server detected, restarting..."
        cleanup_port
    fi
fi

# Clean up any orphaned processes
cleanup_port

# Build command with appropriate flags
CMD="npx @playwright/mcp@latest --port $PORT --shared-browser-context"

# Detect headless environment (unless --headed was specified)
if [ "$FORCE_HEADED" = true ]; then
    echo "Headed mode requested - browser window will be visible"
elif detect_headless; then
    echo "Headless environment detected, adding --headless flag"
    echo "  (use --headed flag to force visible browser)"
    CMD="$CMD --headless"
fi

# Linux-specific: add no-sandbox if not root
if [ "$(uname)" = "Linux" ] && [ "$(id -u)" != "0" ]; then
    CMD="$CMD --no-sandbox"
fi

# Try to find and use Chromium executable
CHROMIUM_PATH=$(find_chromium)
if [ -n "$CHROMIUM_PATH" ]; then
    echo "Using browser: $CHROMIUM_PATH"
    CMD="$CMD --executable-path $CHROMIUM_PATH"
else
    echo "Warning: No browser found. Will attempt to use default (may fail)."
    echo "Run 'npx playwright install chromium' to install a browser."
fi

# Start server
echo "Starting: $CMD"
$CMD &
SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"

# Wait for server to be ready
echo "Waiting for server to start..."
for i in {1..10}; do
    sleep 1
    if python3 "$SCRIPT_DIR/verify.py" 2>/dev/null; then
        echo "Playwright MCP started on port $PORT (PID: $SERVER_PID)"
        exit 0
    fi
done

# Check if process is still running
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "Playwright MCP started on port $PORT (PID: $SERVER_PID) - verify manually"
    exit 0
else
    echo "Failed to start Playwright MCP"
    rm -f "$PID_FILE"
    exit 1
fi
