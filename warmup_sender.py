#!/usr/bin/env python3
"""
🔥 Отправщик первых сообщений лидам через Telethon

Логика:
1. Берёт лидов из Google Sheets (status=new, есть username)
2. Пишет первое сообщение через userbot
3. Сохраняет chat_id для дальнейшего прогрева AI ботом

Запуск:
python warmup_sender.py

Требования:
pip install telethon gspread oauth2client python-dotenv
"""

import asyncio
import os
import random
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

try:
    from telethon import TelegramClient
    from telethon.errors import (
        UserPrivacyRestrictedError,
        FloodWaitError,
        PeerFloodError,
        UsernameNotOccupiedError,
        UsernameInvalidError
    )
    import gspread
    from google.oauth2.credentials import Credentials
except ImportError:
    print("Установите зависимости:")
    print("pip install telethon gspread google-auth python-dotenv")
    exit(1)

load_dotenv()

# ============== КОНФИГУРАЦИЯ ==============
CONFIG = {
    # Telegram API
    "api_id": int(os.getenv("TELEGRAM_API_ID", "0")),
    "api_hash": os.getenv("TELEGRAM_API_HASH", ""),
    "phone": os.getenv("TELEGRAM_PHONE", ""),
    "session_name": "warmup_session",

    # Google Sheets
    "sheets_id": os.getenv("GOOGLE_SHEETS_ID", ""),
    "sheet_name": os.getenv("GOOGLE_SHEET_NAME", "Telegram_Leads_Template"),
    "service_account_file": os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json"),

    # Лимиты
    "daily_limit": int(os.getenv("WARMUP_DAILY_LIMIT", "20")),
    "delay_min": int(os.getenv("WARMUP_DELAY_MIN", "60")),
    "delay_max": int(os.getenv("WARMUP_DELAY_MAX", "180")),

    # Админ для уведомлений
    "admin_chat_id": os.getenv("ADMIN_CHAT_ID", ""),
    "bot_token": os.getenv("WARMUP_BOT_TOKEN", ""),
}

# Первое сообщение
FIRST_MESSAGE = """Здравствуйте! 👋

Видела ваше сообщение о недвижимости. Работаю напрямую с застройщиками, могу помочь с подбором!

✅ Без комиссии для покупателя
✅ Помощь с ипотекой
✅ Актуальные варианты

Интересно узнать подробнее?"""

# Альтернативные варианты сообщений (для разнообразия)
MESSAGES_VARIANTS = [
    """Добрый день! 👋

Заметила ваше сообщение про покупку недвижимости. Если ещё актуально — могу помочь с подбором вариантов.

Работаю без комиссии для покупателя, есть хорошие варианты от застройщиков.

Рассказать подробнее?""",

    """Привет! 🏠

Увидела ваш запрос о недвижимости. Если ещё ищете — есть интересные предложения.

Помогаю с подбором бесплатно, работаю напрямую с застройщиками.

Что именно ищете?""",

    """Здравствуйте!

Прочитала ваше сообщение о покупке. Могу предложить несколько хороших вариантов.

✅ Прямые цены от застройщика
✅ Помощь с документами и ипотекой

Интересно?"""
]


class WarmupSender:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.sheet = None
        self.stats = {
            "processed": 0,
            "sent": 0,
            "failed": 0,
            "skipped": 0
        }

    async def start(self):
        """Запуск Telethon клиента"""
        self.client = TelegramClient(
            self.config["session_name"],
            self.config["api_id"],
            self.config["api_hash"]
        )
        await self.client.start(phone=self.config["phone"])
        me = await self.client.get_me()
        print(f"✅ Telethon: подключено как {me.first_name} (@{me.username})")

    async def stop(self):
        """Остановка клиента"""
        if self.client:
            await self.client.disconnect()

    def connect_sheets(self):
        """Подключение к Google Sheets через OAuth"""
        import json

        token_file = Path("token.json")
        if not token_file.exists():
            print("❌ Файл token.json не найден!")
            print("Запусти: python auth_sheets.py")
            return False

        with open(token_file) as f:
            token_data = json.load(f)

        creds = Credentials(
            token=token_data['token'],
            refresh_token=token_data['refresh_token'],
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret']
        )

        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(self.config["sheets_id"])
        self.sheet = spreadsheet.worksheet(self.config["sheet_name"])

        print(f"✅ Google Sheets: подключено к {self.sheet.title}")
        return True

    def get_leads_to_warm(self):
        """Получение лидов для прогрева"""
        all_records = self.sheet.get_all_records()

        leads = []
        for idx, row in enumerate(all_records, start=2):  # +2 потому что заголовок + индекс с 1
            # Только новые лиды с username
            if row.get("status", "new") != "new":
                continue

            usernames = row.get("usernames", "")
            if not usernames:
                continue

            # Извлекаем первый username
            username = usernames.split(",")[0].strip().lstrip("@")
            if not username or len(username) < 5:
                continue

            leads.append({
                "row": idx,
                "username": username,
                "text": row.get("text", "")[:100],
                "channel": row.get("channel_title", ""),
                "post_url": row.get("post_url", ""),
                "niche": row.get("niche", ""),
            })

        return leads[:self.config["daily_limit"]]

    def get_random_message(self):
        """Случайный вариант первого сообщения"""
        all_messages = [FIRST_MESSAGE] + MESSAGES_VARIANTS
        return random.choice(all_messages)

    async def send_to_lead(self, lead):
        """Отправка сообщения одному лиду"""
        username = lead["username"]

        try:
            # Получаем сущность пользователя
            user = await self.client.get_entity(username)

            # Отправляем сообщение
            message = self.get_random_message()
            await self.client.send_message(user, message)

            # Получаем chat_id
            chat_id = str(user.id)

            print(f"✅ Отправлено @{username} (chat_id: {chat_id})")

            return {
                "success": True,
                "chat_id": chat_id,
                "user_id": str(user.id),
                "username": username
            }

        except UsernameNotOccupiedError:
            print(f"⚠️ @{username} - username не существует")
            return {"success": False, "error": "username_not_found"}

        except UsernameInvalidError:
            print(f"⚠️ @{username} - невалидный username")
            return {"success": False, "error": "invalid_username"}

        except UserPrivacyRestrictedError:
            print(f"⚠️ @{username} - приватность запрещает сообщения")
            return {"success": False, "error": "privacy_restricted"}

        except FloodWaitError as e:
            print(f"🚫 Flood wait: ждём {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
            return {"success": False, "error": f"flood_wait_{e.seconds}"}

        except PeerFloodError:
            print("🚫 PeerFlood: слишком много сообщений, остановка")
            return {"success": False, "error": "peer_flood", "stop": True}

        except Exception as e:
            print(f"❌ @{username} - ошибка: {e}")
            return {"success": False, "error": str(e)}

    def update_lead_status(self, row, status, chat_id=None, error=None):
        """Обновление статуса лида в таблице"""
        updates = {
            "status": status,
            "contacted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if chat_id:
            updates["chat_id"] = chat_id
            updates["user_id"] = chat_id  # Обычно совпадает

        if error:
            updates["warmup_error"] = error

        # Находим колонки
        headers = self.sheet.row_values(1)

        for col_name, value in updates.items():
            if col_name in headers:
                col_idx = headers.index(col_name) + 1
                self.sheet.update_cell(row, col_idx, value)

    async def process_leads(self):
        """Обработка всех лидов"""
        leads = self.get_leads_to_warm()

        if not leads:
            print("📭 Нет лидов для прогрева (status=new с username)")
            return

        print(f"\n📋 Найдено {len(leads)} лидов для прогрева\n")

        for i, lead in enumerate(leads, 1):
            self.stats["processed"] += 1

            print(f"[{i}/{len(leads)}] @{lead['username']} ({lead['channel']})")

            result = await self.send_to_lead(lead)

            if result.get("stop"):
                print("\n🛑 Остановка из-за ограничений Telegram")
                break

            if result["success"]:
                self.stats["sent"] += 1
                self.update_lead_status(
                    lead["row"],
                    "contacted",
                    chat_id=result["chat_id"]
                )
            else:
                self.stats["failed"] += 1
                error = result.get("error", "unknown")

                # Помечаем как пропущенный если username невалидный
                if error in ["username_not_found", "invalid_username"]:
                    self.update_lead_status(lead["row"], "skipped", error=error)
                    self.stats["skipped"] += 1
                elif error == "privacy_restricted":
                    self.update_lead_status(lead["row"], "privacy_blocked", error=error)

            # Задержка между сообщениями
            if i < len(leads):
                delay = random.randint(
                    self.config["delay_min"],
                    self.config["delay_max"]
                )
                print(f"   ⏳ Пауза {delay} сек...")
                await asyncio.sleep(delay)

        print(f"\n📊 Результат:")
        print(f"   Обработано: {self.stats['processed']}")
        print(f"   Отправлено: {self.stats['sent']}")
        print(f"   Ошибок: {self.stats['failed']}")
        print(f"   Пропущено: {self.stats['skipped']}")

    async def notify_admin(self):
        """Уведомление админа о результатах"""
        if not self.config["bot_token"] or not self.config["admin_chat_id"]:
            return

        from telethon import TelegramClient

        # Используем бота для уведомления
        import aiohttp

        text = f"""📊 Прогрев завершён

Обработано: {self.stats['processed']}
✅ Отправлено: {self.stats['sent']}
❌ Ошибок: {self.stats['failed']}
⏭ Пропущено: {self.stats['skipped']}

Время: {datetime.now().strftime('%H:%M:%S')}"""

        url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"

        async with aiohttp.ClientSession() as session:
            await session.post(url, json={
                "chat_id": self.config["admin_chat_id"],
                "text": text
            })


async def main():
    print("""
╔══════════════════════════════════════════════════╗
║      🔥 WARMUP SENDER - Отправка лидам 🔥        ║
║                                                  ║
║  Берёт лидов из таблицы и пишет им первым       ║
║  через Telethon userbot                          ║
╚══════════════════════════════════════════════════╝
    """)

    sender = WarmupSender(CONFIG)

    # Проверяем конфиг
    if not CONFIG["api_id"] or not CONFIG["api_hash"]:
        print("❌ Не заданы TELEGRAM_API_ID и TELEGRAM_API_HASH в .env")
        return

    if not CONFIG["sheets_id"]:
        print("❌ Не задан GOOGLE_SHEETS_ID в .env")
        return

    try:
        # Подключаемся к Google Sheets
        if not sender.connect_sheets():
            return

        # Запускаем Telethon
        await sender.start()

        # Обрабатываем лидов
        await sender.process_leads()

        # Уведомляем админа
        await sender.notify_admin()

    except KeyboardInterrupt:
        print("\n\n⛔ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        raise
    finally:
        await sender.stop()


if __name__ == "__main__":
    asyncio.run(main())
