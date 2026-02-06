#!/bin/sh
#
# paperterm Dashboard Launcher
# Displays a terminal-style dashboard on Kindle e-ink display

# Configuration
DASHBOARD_URL="https://hey-codes.github.io/paperterm/dashboard.png"
REFRESH_RATE=300           # seconds between dashboard refreshes (5 min)
DEBUG_MODE=true            # Enable logging for debugging

# Paths
TMP_DIR="/tmp/paperterm"
DASHBOARD_IMG="$TMP_DIR/dashboard.png"
STATE_FILE="$TMP_DIR/state"
LOG_FILE="$TMP_DIR/paperterm.log"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
log() {
    echo "[$(date '+%H:%M:%S')] $1" >> "$LOG_FILE"
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "$1"
    fi
}

# -----------------------------------------------------------------------------
# Cleanup on exit
# -----------------------------------------------------------------------------
cleanup() {
    log "Cleaning up..."

    # Re-enable sleep
    lipc-set-prop com.lab126.powerd preventScreenSaver 0 2>/dev/null

    # Restart framework
    log "Restarting framework..."
    /etc/init.d/framework start

    # Clear temp files
    rm -rf "$TMP_DIR"

    log "Cleanup complete"
    exit 0
}

trap cleanup EXIT INT TERM

# -----------------------------------------------------------------------------
# Stop Kindle framework for full-screen control
# -----------------------------------------------------------------------------
stop_framework() {
    log "Stopping framework..."

    # Stop the framework
    /etc/init.d/framework stop
    sleep 1

    # Kill specific UI processes that might redraw the screen
    killall -9 cvm 2>/dev/null
    killall -9 mesquite 2>/dev/null
    killall -9 lipc-wait-event 2>/dev/null

    # Wait for processes to die
    sleep 2

    # Clear the screen completely (only done on initial startup)
    eips -c
    eips -c

    log "Framework stopped"
}

# -----------------------------------------------------------------------------
# Prevent screen from sleeping
# -----------------------------------------------------------------------------
prevent_sleep() {
    log "Preventing sleep..."
    lipc-set-prop com.lab126.powerd preventScreenSaver 1 2>/dev/null
    # Also try to disable screensaver
    lipc-set-prop com.lab126.powerd -i deferScreenSaver 300 2>/dev/null
}

# -----------------------------------------------------------------------------
# Display the dashboard image
# Note: Does NOT clear screen first - just overwrites directly to prevent flash
# -----------------------------------------------------------------------------
display_dashboard() {
    log "Displaying dashboard..."

    if [ ! -f "$DASHBOARD_IMG" ]; then
        log "ERROR: Dashboard image not found at $DASHBOARD_IMG"
        return 1
    fi

    # Check file size
    filesize=$(stat -c%s "$DASHBOARD_IMG" 2>/dev/null || stat -f%z "$DASHBOARD_IMG" 2>/dev/null)
    log "Dashboard file size: $filesize bytes"

    # Display the image directly without clearing first (prevents flash)
    # -g = grayscale image, draws directly over existing content
    # DO NOT use -c (clear) or -f (flash/full refresh) here
    eips -g "$DASHBOARD_IMG"

    log "Dashboard displayed"
}

# -----------------------------------------------------------------------------
# Fetch dashboard from server
# Downloads to a temp file first, then atomically moves to final location
# This prevents partial images from being displayed during refresh
# -----------------------------------------------------------------------------
fetch_dashboard() {
    log "Fetching dashboard from $DASHBOARD_URL"

    # Create temp directory if needed
    mkdir -p "$TMP_DIR"

    # Download with retry - use temp file to prevent partial display
    attempts=0
    max_attempts=3
    TEMP_IMG="${DASHBOARD_IMG}.new"

    while [ $attempts -lt $max_attempts ]; do
        if curl -s -o "$TEMP_IMG" --connect-timeout 10 --max-time 30 "$DASHBOARD_URL"; then
            # Verify the download succeeded and file exists
            if [ -f "$TEMP_IMG" ] && [ -s "$TEMP_IMG" ]; then
                # Atomically move temp file to final location
                mv "$TEMP_IMG" "$DASHBOARD_IMG"
                log "Download successful"
                return 0
            else
                log "Download produced empty or missing file"
                rm -f "$TEMP_IMG" 2>/dev/null
            fi
        fi
        attempts=$((attempts + 1))
        log "Download attempt $attempts failed, retrying..."
        sleep 2
    done

    # Clean up any failed temp file
    rm -f "$TEMP_IMG" 2>/dev/null
    log "Failed to download dashboard after $max_attempts attempts"
    return 1
}

# -----------------------------------------------------------------------------
# Show error on screen
# -----------------------------------------------------------------------------
show_error() {
    eips -c
    eips 5 10 "paperterm: $1"
    eips 5 12 "Check $LOG_FILE for details"
    eips 5 14 "Press power button to exit"
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
main() {
    # Initialize
    mkdir -p "$TMP_DIR"
    echo "" > "$LOG_FILE"
    log "========================================="
    log "paperterm starting..."
    log "========================================="

    # Stop framework for full-screen control
    stop_framework

    # Prevent sleep
    prevent_sleep

    # Initial fetch and display
    if fetch_dashboard; then
        display_dashboard
    else
        show_error "Failed to load dashboard"
        sleep 10
        exit 1
    fi

    # Main refresh loop
    log "Entering main loop (refresh every $REFRESH_RATE seconds)"
    last_refresh=$(date +%s)

    while true; do
        # Check if it's time to refresh
        current_time=$(date +%s)
        elapsed=$((current_time - last_refresh))

        if [ $elapsed -ge $REFRESH_RATE ]; then
            log "Refresh interval reached ($elapsed seconds)"
            if fetch_dashboard; then
                display_dashboard
            fi
            last_refresh=$current_time
        fi

        # Small sleep to prevent CPU spin
        sleep 10
    done
}

# Run main
main
