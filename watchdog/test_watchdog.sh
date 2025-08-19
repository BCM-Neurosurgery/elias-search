#!/bin/bash

echo "Testing watchdog functionality..."

# Test 1: Check if the watchdog script is executable
if [ -x "./watchdog.sh" ]; then
    echo "✓ watchdog.sh is executable"
else
    echo "✗ watchdog.sh is not executable"
    chmod +x ./watchdog.sh
    echo "  Made watchdog.sh executable"
fi

# Test 2: Check if required environment variables are set
echo "Environment variables:"
echo "  TARGET_URL: ${TARGET_URL:-http://server:8080/ping/}"
echo "  CHECK_INTERVAL: ${CHECK_INTERVAL:-60}"

# Test 3: Test the ping endpoint (if server is running)
echo "Testing ping endpoint..."
if curl -fs --max-time 5 "http://localhost:8080/ping/" > /dev/null 2>&1; then
    echo "✓ Ping endpoint is responding"
    curl -s "http://localhost:8080/ping/" | jq . 2>/dev/null || curl -s "http://localhost:8080/ping/"
else
    echo "✗ Ping endpoint is not responding (server might not be running)"
fi

echo "Watchdog setup verification complete!"
