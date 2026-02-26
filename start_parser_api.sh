#!/bin/bash
# Startup script for Telegram Parser API

LOG_FILE="/var/log/telegram-parser-api.log"
PID_FILE="/var/run/telegram-parser-api.pid"
SCRIPT_DIR="/home/user/2026"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Telegram Parser API already running (PID: $PID)"
        exit 0
    fi
fi

# Start the API
cd "$SCRIPT_DIR"
nohup /usr/local/bin/python3 telegram_parser_api.py >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "Telegram Parser API started (PID: $!)"
