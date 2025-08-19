#!/bin/sh

TARGET_URL="${TARGET_URL:-http://server:8080/ping/}"
INTERVAL="${CHECK_INTERVAL:-60}"

echo "[watchdog] Starting health check loop..."
echo "[watchdog] Target URL: $TARGET_URL"
echo "[watchdog] Check interval: $INTERVAL seconds"

while true; do
    echo "[watchdog] Checking server health..."
    
    # Use curl with timeout and proper error handling
    if curl -fs --max-time 10 "$TARGET_URL" > /dev/null 2>&1; then
        echo "[watchdog] Server is healthy ✓"
    else
        echo "[watchdog] Health check failed! Attempting to restart server..."
        
        # Try to restart the server container
        if docker restart server > /dev/null 2>&1; then
            echo "[watchdog] Server restart initiated successfully"
        else
            echo "[watchdog] Failed to restart server container"
        fi
        
        # Wait a bit before next check to allow restart to complete
        sleep 30
    fi
    
    echo "[watchdog] Waiting $INTERVAL seconds before next check..."
    sleep "$INTERVAL"
done
