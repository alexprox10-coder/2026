#!/bin/bash

# ChinaLeadBot Quick Setup Script
# Быстрая настройка бота за 5 минут

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Header
echo -e "${BLUE}${BOLD}"
echo "================================================================"
echo "  ChinaLeadBot - Quick Setup"
echo "================================================================"
echo -e "${NC}"

# Check if .env exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠  .env файл уже существует${NC}"
    read -p "Перезаписать? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo -e "${BLUE}Используем существующий .env${NC}"
    fi
fi

echo ""
echo -e "${BOLD}ШАГ 1: Telegram Bot Token${NC}"
echo "----------------------------------------"
echo ""
echo "1. Откройте Telegram"
echo "2. Найдите @BotFather"
echo "3. Отправьте /newbot"
echo "4. Следуйте инструкциям"
echo ""
read -p "Введите токен от BotFather: " bot_token

if [ -z "$bot_token" ]; then
    echo -e "${RED}✗ Токен не может быть пустым!${NC}"
    exit 1
fi

echo ""
echo -e "${BOLD}ШАГ 2: n8n Webhook URL${NC}"
echo "----------------------------------------"
echo ""
echo "1. Откройте n8n (http://localhost:5678 или app.n8n.cloud)"
echo "2. Импортируйте workflow v3 из:"
echo "   china-lead-bot/workflows/chinaleadbot_workflow_v3.json"
echo "3. АКТИВИРУЙТЕ workflow (переключатель Active)"
echo "4. Кликните узел 'Webhook Trigger'"
echo "5. Скопируйте 'Production URL'"
echo ""
read -p "Введите Webhook URL: " webhook_url

if [ -z "$webhook_url" ]; then
    echo -e "${RED}✗ Webhook URL не может быть пустым!${NC}"
    exit 1
fi

echo ""
echo -e "${BOLD}ШАГ 3 (Опционально): Google Sheets ID${NC}"
echo "----------------------------------------"
echo ""
echo "Если вы уже настроили Google Sheets в n8n, можете пропустить"
echo ""
read -p "Google Sheets ID (Enter чтобы пропустить): " sheets_id

echo ""
echo -e "${BOLD}ШАГ 4 (Опционально): Anthropic API Key${NC}"
echo "----------------------------------------"
echo ""
echo "Используется только для улучшения поисковых запросов"
echo "Можно пропустить - бот работает через n8n + OpenAI"
echo ""
read -p "Anthropic API Key (Enter чтобы пропустить): " anthropic_key

# Create .env file
echo ""
echo -e "${BLUE}Создаю .env файл...${NC}"

cat > .env << EOF
# ==========================================
# TELEGRAM BOT CONFIGURATION
# ==========================================
TELEGRAM_BOT_TOKEN=$bot_token

# ==========================================
# N8N WEBHOOK CONFIGURATION
# ==========================================
N8N_WEBHOOK_URL=$webhook_url

# ==========================================
# OPTIONAL SETTINGS
# ==========================================
ANTHROPIC_API_KEY=$anthropic_key
GOOGLE_SHEET_ID=$sheets_id

# ==========================================
# ADDITIONAL SETTINGS
# ==========================================
DATABASE_URL=sqlite:///china_lead_bot.db
ADMIN_USER_IDS=
DEFAULT_LANGUAGE=ru
MAX_FREE_LEADS=5

PLAN_BASIC_PRICE=2990
PLAN_BASIC_LEADS=50
PLAN_PRO_PRICE=7990
PLAN_PRO_LEADS=200
PLAN_ENTERPRISE_PRICE=19990
PLAN_ENTERPRISE_LEADS=999999

PRICE_QUALIFIED_LEAD=200
PRICE_WARM_LEAD=500
PRICE_MEETING_SCHEDULED=2000

ALIBABA_DELAY=2
MAX_RESULTS_PER_SEARCH=100
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
EOF

echo -e "${GREEN}✓ .env файл создан${NC}"

# Check if Python is installed
echo ""
echo -e "${BLUE}Проверяю Python...${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo -e "${GREEN}✓ Python3 найден${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo -e "${GREEN}✓ Python найден${NC}"
else
    echo -e "${RED}✗ Python не найден!${NC}"
    echo "Установите Python 3.8+ и попробуйте снова"
    exit 1
fi

# Check if venv exists
echo ""
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Создаю виртуальное окружение...${NC}"
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"
else
    echo -e "${BLUE}Виртуальное окружение уже существует${NC}"
fi

# Activate venv and install dependencies
echo ""
echo -e "${YELLOW}Устанавливаю зависимости...${NC}"
echo "Это займет 1-2 минуты..."

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}✓ Зависимости установлены${NC}"
else
    echo -e "${RED}✗ Не удалось активировать venv${NC}"
    echo "Установите зависимости вручную: pip install -r requirements.txt"
fi

# Run config check
echo ""
echo -e "${BLUE}Проверяю конфигурацию...${NC}"
echo ""

if [ -f "check_config.py" ]; then
    $PYTHON_CMD check_config.py
else
    echo -e "${YELLOW}⚠  check_config.py не найден, пропускаю проверку${NC}"
fi

# Final instructions
echo ""
echo -e "${GREEN}${BOLD}================================================================"
echo "  ✓ SETUP ЗАВЕРШЁН!"
echo "================================================================${NC}"
echo ""
echo -e "${BOLD}Следующие шаги:${NC}"
echo ""
echo "1. Активируйте виртуальное окружение:"
echo -e "   ${BLUE}source venv/bin/activate${NC}"
echo ""
echo "2. Запустите бота:"
echo -e "   ${BLUE}python bot/main.py${NC}"
echo ""
echo "3. Найдите бота в Telegram и отправьте /start"
echo ""
echo "4. Протестируйте поиск!"
echo ""
echo -e "${YELLOW}Для запуска в фоне используйте:${NC}"
echo -e "   ${BLUE}nohup python bot/main.py > bot.log 2>&1 &${NC}"
echo ""
echo -e "${BOLD}Документация:${NC}"
echo "  • Полная инструкция: docs/TELEGRAM_BOT_SETUP.md"
echo "  • Настройка workflow: workflows/WORKFLOW_V3_SETUP.md"
echo "  • Проверка config: python check_config.py"
echo ""
echo -e "${GREEN}Удачи! 🚀${NC}"
echo ""
