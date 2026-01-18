#!/bin/bash
# Скрипт для запуска Rental Parser Agent

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Rental Parser Agent - Startup${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Переход в директорию скрипта
cd "$(dirname "$0")" || exit 1

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found!${NC}"
    echo "Please install Python 3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Проверка наличия .env файла
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} .env file not found!"
    echo "Creating from .env.example..."

    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠${NC} Please edit .env file with your configuration!"
        echo "  Required: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS"
        exit 1
    else
        echo -e "${RED}❌ .env.example not found!${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓${NC} .env configuration found"

# Проверка зависимостей
echo ""
echo "Checking dependencies..."

if ! python3 -c "import schedule" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Dependencies not installed!"
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt || {
        echo -e "${RED}❌ Failed to install dependencies!${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✓${NC} All dependencies installed"

# Проверка Telegram конфигурации
echo ""
echo "Checking Telegram configuration..."

source .env

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ TELEGRAM_BOT_TOKEN not set in .env!${NC}"
    exit 1
fi

if [ -z "$TELEGRAM_CHAT_IDS" ]; then
    echo -e "${RED}❌ TELEGRAM_CHAT_IDS not set in .env!${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Telegram configuration OK"

# Проверка базы данных
echo ""
echo "Checking database..."

DB_PATH="${DB_PATH:-rental_parser.db}"

if [ ! -f "$DB_PATH" ]; then
    echo -e "${YELLOW}⚠${NC} Database not found, will be created on first run"
else
    echo -e "${GREEN}✓${NC} Database found: $DB_PATH"
fi

# Запуск агента
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Starting Agent${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Configuration:"
echo "  City: ${CITY:-москва}"
echo "  Parse interval: ${PARSE_INTERVAL_HOURS:-4} hours"
echo "  Max pages: ${MAX_PAGES:-5} per platform"
echo "  Auto-dial: ${AUTO_DIAL_ENABLED:-true}"
echo "  Dialer backend: ${DIALER_BACKEND:-mock}"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Запуск с передачей всех аргументов
python3 agent.py "$@"
