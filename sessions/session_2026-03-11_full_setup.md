# Сессия: Полная настройка бота прогрева лидов

**Дата:** 2026-03-11

## Что сделали

### 1. Разобрались с логикой системы

```
ПАРСЕР (n8n workflow)
    ↓ парсит каналы по ключевым словам
    ↓ сохраняет в Google Sheets (username, text, channel)

WARMUP SENDER (Python + Telethon)
    ↓ берёт лидов из таблицы (status=new, есть username)
    ↓ пишет первое сообщение через userbot
    ↓ сохраняет chat_id, status=contacted

AI БОТ ПРОГРЕВА (n8n workflow)
    ↓ ловит ответы лидов
    ↓ ведёт диалог через OpenRouter AI
    ↓ собирает данные (город, бюджет, комнаты, срок)
    ↓ финал: status=ready или status=refused
```

### 2. Существующие workflows в n8n

| ID | Название | Описание |
|----|----------|----------|
| VdbKNtzY0YHW5y58 | Telegram Parser PRO v4 | Парсер каналов по ключевым словам |
| B9SIrpqiDlwCY7Or | AI Бот-прогрев недвижимости | AI агент для прогрева через OpenRouter |

### 3. Google Sheets

**Таблица лидов:** `1alr08qWL2TTVF-1nuDeU4NVXoGgyODgLKeTsa16_kxE`
**Лист:** `Telegram_Leads_Template`

**Credentials в n8n:**
- Google Sheets OAuth2: `3tw79kiICQ7OPZI8` (Google Sheets ТЕЛЕГРАМ ПАРС)
- Telegram Bot: `kkySYqFIPRx85OPe` (Telegram ПАРСЕР)

### 4. Настройка Python окружения на сервере

```bash
# Сервер
IP: 91.79.245.107
User: root

# Создали venv
cd /root/2026
python3 -m venv venv
source venv/bin/activate

# Установили пакеты
pip install telethon gspread google-auth google-auth-oauthlib python-dotenv
```

### 5. Google OAuth авторизация

**Проблема:** Service Account не удалось настроить, использовали OAuth Desktop App.

**Шаги:**
1. Google Cloud Console → APIs & Services → Credentials
2. Create Credentials → OAuth Client ID → Desktop App
3. Скачали JSON → `/root/2026/credentials.json`
4. Добавили test user: `alexprox10@gmail.com`
5. Создали скрипт авторизации:

```python
# /root/2026/auth_sheets.py
import gspread
import json
from google_auth_oauthlib.flow import Flow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

flow = Flow.from_client_secrets_file(
    'credentials.json',
    scopes=SCOPES,
    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
)

auth_url, _ = flow.authorization_url(prompt='consent')
print("Открой ссылку в браузере:")
print(auth_url)
code = input("Вставь код: ")
flow.fetch_token(code=code)
creds = flow.credentials

with open('token.json', 'w') as f:
    json.dump({
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes)
    }, f)

print("Готово!")
```

6. Запустили, авторизовались → создался `token.json`

### 6. Файлы конфигурации

**/root/2026/.env:**
```
TELEGRAM_API_ID=39052174
TELEGRAM_API_HASH=abb12e0f8f025acdfbda295d6f3d8cd9
TELEGRAM_PHONE=+79145819661

WARMUP_BOT_TOKEN=7962933730:AAGrLW-PYbGsWVuAhGR-CxW2IrV7RqR4ScU
ADMIN_CHAT_ID=7984101063

GOOGLE_SHEETS_ID=1alr08qWL2TTVF-1nuDeU4NVXoGgyODgLKeTsa16_kxE
GOOGLE_SHEET_NAME=Telegram_Leads_Template

WARMUP_DAILY_LIMIT=20
WARMUP_DELAY_MIN=60
WARMUP_DELAY_MAX=180

N8N_URL=https://n8n.arendadom24.ru
N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**/root/2026/credentials.json:** OAuth credentials (Desktop App)

**/root/2026/token.json:** OAuth token (создан после авторизации)

### 7. Скрипт отправки сообщений

**/root/2026/warmup_sender.py:**
```python
#!/usr/bin/env python3
import asyncio
import os
import random
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

try:
    from telethon import TelegramClient
    from telethon.errors import UserPrivacyRestrictedError, FloodWaitError, PeerFloodError, UsernameNotOccupiedError, UsernameInvalidError
    import gspread
    from google.oauth2.credentials import Credentials
except ImportError:
    print("pip install telethon gspread google-auth python-dotenv")
    exit(1)

load_dotenv()

CONFIG = {
    "api_id": int(os.getenv("TELEGRAM_API_ID", "0")),
    "api_hash": os.getenv("TELEGRAM_API_HASH", ""),
    "phone": os.getenv("TELEGRAM_PHONE", ""),
    "session_name": "warmup_session",
    "sheets_id": os.getenv("GOOGLE_SHEETS_ID", ""),
    "sheet_name": os.getenv("GOOGLE_SHEET_NAME", "Telegram_Leads_Template"),
    "daily_limit": int(os.getenv("WARMUP_DAILY_LIMIT", "20")),
    "delay_min": int(os.getenv("WARMUP_DELAY_MIN", "60")),
    "delay_max": int(os.getenv("WARMUP_DELAY_MAX", "180")),
}

FIRST_MESSAGE = """Здравствуйте! Видела ваше сообщение о недвижимости. Могу помочь с подбором! Без комиссии, помощь с ипотекой. Интересно?"""

class WarmupSender:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.sheet = None
        self.stats = {"processed": 0, "sent": 0, "failed": 0}

    async def start(self):
        self.client = TelegramClient(self.config["session_name"], self.config["api_id"], self.config["api_hash"])
        await self.client.start(phone=self.config["phone"])
        me = await self.client.get_me()
        print(f"Telethon: {me.first_name}")

    async def stop(self):
        if self.client:
            await self.client.disconnect()

    def connect_sheets(self):
        token_file = Path("token.json")
        if not token_file.exists():
            print("token.json not found")
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
        self.sheet = gc.open_by_key(self.config["sheets_id"]).worksheet(self.config["sheet_name"])
        print(f"Sheets: {self.sheet.title}")
        return True

    def get_leads(self):
        leads = []
        for idx, row in enumerate(self.sheet.get_all_records(), start=2):
            if row.get("status", "new") != "new":
                continue
            usernames = row.get("usernames", "")
            if not usernames:
                continue
            username = usernames.split(",")[0].strip().lstrip("@")
            if username and len(username) >= 5:
                leads.append({"row": idx, "username": username})
        return leads[:self.config["daily_limit"]]

    async def send_to_lead(self, lead):
        try:
            user = await self.client.get_entity(lead["username"])
            await self.client.send_message(user, FIRST_MESSAGE)
            print(f"Sent to @{lead['username']}")
            return {"success": True, "chat_id": str(user.id)}
        except Exception as e:
            print(f"Error @{lead['username']}: {e}")
            return {"success": False}

    async def process(self):
        leads = self.get_leads()
        print(f"Found {len(leads)} leads")
        for i, lead in enumerate(leads, 1):
            result = await self.send_to_lead(lead)
            if result["success"]:
                self.stats["sent"] += 1
                headers = self.sheet.row_values(1)
                if "status" in headers:
                    self.sheet.update_cell(lead["row"], headers.index("status") + 1, "contacted")
                if "chat_id" in headers:
                    self.sheet.update_cell(lead["row"], headers.index("chat_id") + 1, result["chat_id"])
            if i < len(leads):
                delay = random.randint(self.config["delay_min"], self.config["delay_max"])
                print(f"Wait {delay}s...")
                await asyncio.sleep(delay)
        print(f"Done. Sent: {self.stats['sent']}")

async def main():
    sender = WarmupSender(CONFIG)
    if not sender.connect_sheets():
        return
    await sender.start()
    await sender.process()
    await sender.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### 8. Текущий статус

**Готово:**
- [x] Python venv с пакетами
- [x] Google Sheets OAuth авторизация (token.json)
- [x] Скрипт warmup_sender.py
- [x] Подключение к таблице работает

**В процессе:**
- [ ] Telethon авторизация (ждём код в Telegram)

### 9. Следующие шаги

1. **Авторизовать Telethon:**
   ```bash
   cd /root/2026
   source venv/bin/activate
   python warmup_sender.py
   # Ввести код из Telegram
   ```

2. **Проверить что лиды есть в таблице** с username и status=new

3. **Запустить тестовый прогрев** на 1-2 лидах

4. **Настроить связку с AI ботом** для автоматического прогрева ответов

### 10. Полезные команды

```bash
# Подключиться к серверу
ssh root@91.79.245.107

# Активировать venv
cd /root/2026
source venv/bin/activate

# Запустить прогрев
python warmup_sender.py

# Проверить Google Sheets подключение
python -c "
import json
import gspread
from google.oauth2.credentials import Credentials
from pathlib import Path

with open('token.json') as f:
    t = json.load(f)
creds = Credentials(token=t['token'], refresh_token=t['refresh_token'],
    token_uri=t['token_uri'], client_id=t['client_id'], client_secret=t['client_secret'])
gc = gspread.authorize(creds)
sheet = gc.open_by_key('1alr08qWL2TTVF-1nuDeU4NVXoGgyODgLKeTsa16_kxE')
print('OK:', sheet.title)
"

# Проверить .env
cat /root/2026/.env
```

### 11. Структура файлов на сервере

```
/root/2026/
├── venv/                    # Python виртуальное окружение
├── .env                     # Переменные окружения
├── credentials.json         # OAuth credentials
├── token.json              # OAuth token (после авторизации)
├── warmup_sender.py        # Скрипт отправки сообщений
├── auth_sheets.py          # Скрипт авторизации Google
├── warmup_session.session  # Telethon сессия (после авторизации)
└── workflows/
    ├── lead_warmup_bot.json
    ├── realty_warmup_full.json
    └── realty_ai_bot.json
```

---

## История сессий

| Дата | Файл | Что делали |
|------|------|------------|
| 08.03 | session_2026-03-08_01.md | Начало, проверка workflows |
| 08.03 | session_2026-03-08_lead-warming-workflow.md | Настройка webhook прогрева |
| 09.03 | session_2026-03-09_warmup_bot_fix.md | Исправление fallbackOutput |
| 11.03 | session_2026-03-11_ai_bot_warmup.md | AI бот с OpenRouter |
| 11.03 | session_2026-03-11_warmup_sender.md | Скрипт Telethon |
| 11.03 | session_2026-03-11_full_setup.md | Полная настройка (этот файл) |
