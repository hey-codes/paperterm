#!/bin/sh
#
# paperterm Dashboard Launcher
# Displays a terminal-style dashboard on Kindle e-ink display
#
# Features:
# - Full-screen takeover (stops framework)
# - Touch-to-exit (bottom-right corner)
# - Prevents sleep during display
# - Clean exit restores normal operation

# Configuration
DASHBOARD_URL="https://hey-codes.github.io/paperterm/dashboard.png"
REFRESH_RATE=300           # seconds between dashboard refreshes (5 min)
TOUCH_EXIT_ZONE=150        # pixels from edge for exit touch zone
DEBUG_MODE=false

# Paths
TMP_DIR="/tmp/paperterm"
DASHBOARD_IMG="$TMP_DIR/dashboard.png"
STATE_FILE="$TMP_DIR/state"
LOG_FILE="$TMP_DIR/paperterm.log"

# Display dimensions (Kindle PW 11th gen)
DISPLAY_WIDTH=1236
DISPLAY_HEIGHT=1648

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[$(date '+%H:%M:%S')] $1" >> "$LOG_FILE"
    fi
}

# -----------------------------------------------------------------------------
# Cleanup on exit
# -----------------------------------------------------------------------------
cleanup() {
    log "Cleaning up..."

    # Re-enable sleep
    lipc-set-prop com.lab126.powerd preventScreenSaver 0 2>/dev/null

    # Stop touch monitoring
    if [ -n "$TOUCH_PID" ] && kill -0 "$TOUCH_PID" 2>/dev/null; then
        kill "$TOUCH_PID" 2>/dev/null
    fi

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
    /etc/init.d/framework stop

    # Wait for framework to fully stop
    sleep 2

    # Clear the screen
    eips -c

    log "Framework stopped"
}

# -----------------------------------------------------------------------------
# Prevent screen from sleeping
# -----------------------------------------------------------------------------
prevent_sleep() {
    log "Preventing sleep..."
    lipc-set-prop com.lab126.powerd preventScreenSaver 1 2>/dev/null
}

# -----------------------------------------------------------------------------
# Display the dashboard image
# -----------------------------------------------------------------------------
display_dashboard() {
    log "Displaying dashboard..."

    # Use fbink if available (better quality), fallback to eips
    if command -v fbink >/dev/null 2>&1; then
        fbink -c -g file="$DASHBOARD_IMG" -f
    else
        # eips requires grayscale PNG
        eips -c
        eips -g "$DASHBOARD_IMG"
    fi

    log "Dashboard displayed"
}

# -----------------------------------------------------------------------------
# Fetch dashboard from server
# -----------------------------------------------------------------------------
fetch_dashboard() {
    log "Fetching dashboard from $DASHBOARD_URL"

    # Create temp directory if needed
    mkdir -p "$TMP_DIR"

    # Download with retry
    local attempts=0
    local max_attempts=3

    while [ $attempts -lt $max_attempts ]; do
        if curl -s -o "$DASHBOARD_IMG" --connect-timeout 10 --max-time 30 "$DASHBOARD_URL"; then
            log "Download successful"
            return 0
        fi
        attempts=$((attempts + 1))
        log "Download attempt $attempts failed, retrying..."
        sleep 2
    done

    log "Failed to download dashboard after $max_attempts attempts"
    return 1
}

# -----------------------------------------------------------------------------
# Monitor touch input for exit gesture
# Touch in bottom-right corner exits the dashboard
# -----------------------------------------------------------------------------
monitor_touch() {
    log "Starting touch monitor..."

    # Find touch input device
    TOUCH_DEV=""
    for dev in /dev/input/event*; do
        if [ -e "$dev" ]; then
            TOUCH_DEV="$dev"
            break
        fi
    done

    if [ -z "$TOUCH_DEV" ]; then
        log "No touch device found"
        return
    fi

    log "Touch device: $TOUCH_DEV"

    # Monitor touch events in background
    # Uses evtest or hexdump to read raw touch events
    (
        while true; do
            # Read touch coordinates
            # This is a simplified approach - real implementation may need evtest
            if command -v evtest >/dev/null 2>&1; then
                evtest "$TOUCH_DEV" 2>/dev/null | while read -r line; do
                    # Parse ABS_MT_POSITION_X and ABS_MT_POSITION_Y
                    case "$line" in
                        *ABS_MT_POSITION_X*)
                            touch_x=$(echo "$line" | grep -o 'value [0-9]*' | cut -d' ' -f2)
                            ;;
                        *ABS_MT_POSITION_Y*)
                            touch_y=$(echo "$line" | grep -o 'value [0-9]*' | cut -d' ' -f2)

                            # Check if touch is in exit zone (bottom-right corner)
                            if [ -n "$touch_x" ] && [ -n "$touch_y" ]; then
                                exit_x=$((DISPLAY_WIDTH - TOUCH_EXIT_ZONE))
                                exit_y=$((DISPLAY_HEIGHT - TOUCH_EXIT_ZONE))

                                if [ "$touch_x" -gt "$exit_x" ] && [ "$touch_y" -gt "$exit_y" ]; then
                                    log "Exit touch detected at $touch_x,$touch_y"
                                    echo "EXIT" > "$STATE_FILE"
                                fi
                            fi
                            ;;
                    esac
                done
            else
                # Fallback: just check for any touch as exit
                # In production, you'd want proper touch coordinate parsing
                hexdump -e '16/1 "%02x" "\n"' "$TOUCH_DEV" 2>/dev/null | while read -r line; do
                    # Any touch event triggers check
                    if [ -n "$line" ]; then
                        # For simplicity, treat any touch as potential exit
                        # A full implementation would parse coordinates
                        :
                    fi
                done
            fi
            sleep 1
        done
    ) &
    TOUCH_PID=$!

    log "Touch monitor started (PID: $TOUCH_PID)"
}

# -----------------------------------------------------------------------------
# Show exit zone indicator
# -----------------------------------------------------------------------------
show_exit_indicator() {
    # Draw a small visual indicator in the bottom-right corner
    # Using fbink text placement
    if command -v fbink >/dev/null 2>&1; then
        fbink -x -4 -y -2 -m "[EXIT]" 2>/dev/null
    fi
}

# -----------------------------------------------------------------------------
# Main loop
# -----------------------------------------------------------------------------
main() {
    log "paperterm starting..."

    # Initialize
    mkdir -p "$TMP_DIR"
    echo "RUNNING" > "$STATE_FILE"

    # Stop framework for full-screen control
    stop_framework

    # Prevent sleep
    prevent_sleep

    # Start touch monitoring
    monitor_touch

    # Initial fetch and display
    if fetch_dashboard; then
        display_dashboard
        show_exit_indicator
    else
        # Show error message on screen
        eips -c
        eips 10 10 "paperterm: Failed to load dashboard"
        eips 10 12 "Check network connection"
        eips 10 14 "Touch bottom-right to exit"
    fi

    # Main refresh loop
    last_refresh=$(date +%s)

    while true; do
        # Check for exit signal
        if [ -f "$STATE_FILE" ] && grep -q "EXIT" "$STATE_FILE" 2>/dev/null; then
            log "Exit signal received"
            break
        fi

        # Check if it's time to refresh
        current_time=$(date +%s)
        elapsed=$((current_time - last_refresh))

        if [ $elapsed -ge $REFRESH_RATE ]; then
            log "Refresh interval reached ($elapsed seconds)"
            if fetch_dashboard; then
                display_dashboard
                show_exit_indicator
            fi
            last_refresh=$current_time
        fi

        # Small sleep to prevent CPU spin
        sleep 5
    done

    log "Main loop ended"
}

# Run main
main
