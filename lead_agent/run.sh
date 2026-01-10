#!/bin/bash

# Скрипт для запуска агента

echo "=================================="
echo "🤖 Lead Collection Agent"
echo "=================================="
echo ""

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создайте его командой:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Активация виртуального окружения
echo "🔄 Активация виртуального окружения..."
source venv/bin/activate

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "Создайте его из .env.example:"
    echo "   cp .env.example .env"
    echo "   # Заполните необходимые ключи"
    exit 1
fi

# Запуск агента
echo "🚀 Запуск агента..."
echo ""
python agent.py

# Деактивация при выходе
deactivate
