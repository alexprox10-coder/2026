"""Конфигурационные настройки агента"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Базовые пути
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# Создаем директории если их нет
LOGS_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# API ключи
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Google Sheets
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "17Ll6-lvbJTGix5Y6uwh2Glr8CNT6FktnicRsuOWdhqA")
GOOGLE_CREDENTIALS_FILE = CONFIG_DIR / os.getenv("GOOGLE_CREDENTIALS_FILE", "google_credentials.json")

# Настройки листов Google Sheets
SHEET_NAMES = {
    "queries": "ЗАПРОСЫ",
    "sites": "САЙТЫ",
    "companies": "КОМПАНИИ",
    "letters": "ПИСЬМА"
}

# Региональные настройки
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
REGION = os.getenv("REGION", "Россия")

# Логирование
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "agent.log"

# Claude AI настройки
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
CLAUDE_MAX_TOKENS = 4096

# Целевые ниши
TARGET_NICHES = [
    "агентства недвижимости",
    "автосервисы",
    "стоматологии",
    "локальный бизнес"
]
