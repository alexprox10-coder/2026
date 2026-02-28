#!/bin/bash

# Channel Finder Bot Startup Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Channel Finder Bot...${NC}"

# Check if BOT_TOKEN is set
if [ -z "$BOT_TOKEN" ]; then
    echo -e "${RED}ERROR: BOT_TOKEN is not set!${NC}"
    echo "Please set it using: export BOT_TOKEN='your_bot_token'"
    echo "Get your token from @BotFather in Telegram"
    exit 1
fi

# Optional: Telegram API for channel validation
if [ -z "$TELEGRAM_API_ID" ] || [ -z "$TELEGRAM_API_HASH" ]; then
    echo -e "${YELLOW}WARNING: TELEGRAM_API_ID or TELEGRAM_API_HASH not set${NC}"
    echo "Channel validation will be limited"
    echo "Get API credentials at: https://my.telegram.org"
fi

# Install dependencies if needed
if ! python3 -c "import telegram" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip3 install -r requirements_channel_finder.txt
fi

# Run the bot
cd "$(dirname "$0")"
python3 channel_finder_bot.py
