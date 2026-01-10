#!/usr/bin/env python3
"""
Скрипт для тестирования подключений к API и сервисам
"""
import sys
from pathlib import Path
import os

sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

print("=" * 60)
print("🔧 ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЙ")
print("=" * 60)

# Проверка переменных окружения
print("\n📋 Проверка переменных окружения:")
print("-" * 60)

env_vars = {
    "ANTHROPIC_API_KEY": "Anthropic API",
    "GOOGLE_SHEETS_ID": "Google Sheets ID",
    "GOOGLE_MAPS_API_KEY": "Google Maps API",
    "TELEGRAM_BOT_TOKEN": "Telegram Bot (опционально)",
    "TELEGRAM_CHAT_ID": "Telegram Chat ID (опционально)"
}

all_set = True
for var, name in env_vars.items():
    value = os.getenv(var)
    if value:
        if var in ["ANTHROPIC_API_KEY", "GOOGLE_MAPS_API_KEY", "TELEGRAM_BOT_TOKEN"]:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {name}: {masked}")
        else:
            print(f"✅ {name}: {value}")
    else:
        if var in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]:
            print(f"⚠️  {name}: не настроен (опционально)")
        else:
            print(f"❌ {name}: НЕ НАСТРОЕН")
            all_set = False

# Проверка Google Credentials
print("\n📄 Проверка Google Credentials:")
print("-" * 60)
creds_file = Path(__file__).parent / "config" / "google_credentials.json"
if creds_file.exists():
    print(f"✅ Файл найден: {creds_file}")
    try:
        import json
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
            client_email = creds_data.get('client_email', 'N/A')
            print(f"   Service Account: {client_email}")
    except Exception as e:
        print(f"⚠️  Ошибка чтения файла: {e}")
else:
    print(f"❌ Файл не найден: {creds_file}")
    all_set = False

# Тест Anthropic API
print("\n🤖 Тестирование Anthropic API:")
print("-" * 60)
try:
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Простой тестовый запрос
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=50,
        messages=[{"role": "user", "content": "Ответь одним словом: работает"}]
    )

    print(f"✅ Подключение успешно!")
    print(f"   Ответ: {response.content[0].text}")

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    all_set = False

# Тест Google Sheets
print("\n📊 Тестирование Google Sheets:")
print("-" * 60)
try:
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
    client = gspread.authorize(creds)

    sheets_id = os.getenv("GOOGLE_SHEETS_ID")
    spreadsheet = client.open_by_key(sheets_id)

    print(f"✅ Подключение успешно!")
    print(f"   Название таблицы: {spreadsheet.title}")
    print(f"   Количество листов: {len(spreadsheet.worksheets())}")

    worksheets = spreadsheet.worksheets()
    print(f"   Листы:")
    for ws in worksheets:
        print(f"      - {ws.title}")

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    all_set = False

# Тест Google Maps API
print("\n🗺️  Тестирование Google Maps API:")
print("-" * 60)
try:
    import requests

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    test_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': 'Москва',
        'key': api_key
    }

    response = requests.get(test_url, params=params, timeout=10)
    data = response.json()

    if data['status'] == 'OK':
        print(f"✅ API работает корректно!")
        print(f"   Тестовый запрос: геокодирование 'Москва'")
    else:
        print(f"⚠️  API вернул статус: {data['status']}")

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")

# Тест Telegram (опционально)
if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
    print("\n📱 Тестирование Telegram Bot:")
    print("-" * 60)
    try:
        from telegram import Bot
        import asyncio

        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        async def test_telegram():
            await bot.send_message(
                chat_id=chat_id,
                text="🧪 Тестовое сообщение от Lead Collection Agent"
            )

        asyncio.run(test_telegram())

        print(f"✅ Сообщение отправлено!")
        print(f"   Проверьте Telegram")

    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

# Итоги
print("\n" + "=" * 60)
if all_set:
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("\nМожно запускать агента:")
    print("   python agent.py")
else:
    print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
    print("\nПроверьте:")
    print("   1. Файл .env заполнен корректно")
    print("   2. google_credentials.json находится в config/")
    print("   3. Service account имеет доступ к таблице")
    print("   4. API ключи действительны")
print("=" * 60)
