#!/bin/bash
# Запуск Crypto Leads Parser на Telethon

cd "$(dirname "$0")"

# Проверка .env
if [ ! -f .env ]; then
    echo "Создайте .env файл из .env.example"
    echo "cp .env.example .env"
    exit 1
fi

# Загрузка переменных
source .env

# Проверка обязательных переменных
if [ -z "$TELEGRAM_API_ID" ] || [ -z "$TELEGRAM_API_HASH" ]; then
    echo "Установите TELEGRAM_API_ID и TELEGRAM_API_HASH в .env"
    echo "Получите их на https://my.telegram.org/apps"
    exit 1
fi

# Запуск
python3 crypto_leads_telethon.py
