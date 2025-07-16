#!/bin/sh

TARGET_URL="${TARGET_URL:-http://web:8000/ping/}"
INTERVAL="${CHECK_INTERVAL:-60}"

echo "[watchdog] Starting health check loop..."
while true; do
    if ! curl -fs "$TARGET_URL" > /dev/null; then
        echo "[watchdog] Health check failed. Restarting django server..."
        docker restart server
    else
        echo "[watchdog] django server is healthy."
    fi
    sleep "$INTERVAL"
done
