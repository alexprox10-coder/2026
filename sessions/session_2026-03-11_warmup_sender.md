# Сессия: Скрипт отправки первых сообщений лидам

**Дата:** 2026-03-11

## Задача
Создать скрипт который берёт лидов из таблицы парсера и пишет им первым через Telethon userbot.

## Проблема
Парсер собирает лидов из Telegram каналов, но там нет `chat_id` — только `username` извлечённый из текста сообщений. Telegram Bot API не позволяет писать первым по username, поэтому нужен userbot.

## Решение

### Архитектура
```
┌─────────────────────────────────────────────────────────────┐
│  ПАРСЕР → таблица (username, status=new)                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  warmup_sender.py (Telethon userbot)                       │
│  - Берёт лидов с username из таблицы                        │
│  - Пишет первое сообщение                                   │
│  - Сохраняет chat_id, status=contacted                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  AI Бот-прогрев (n8n workflow)                              │
│  - Ловит ответы лидов по chat_id                            │
│  - Ведёт диалог через AI                                    │
│  - Финал: status=ready или status=refused                   │
└─────────────────────────────────────────────────────────────┘
```

### Созданные файлы

1. **warmup_sender.py** — основной скрипт
   - Подключается к Google Sheets
   - Фильтрует лидов (status=new, есть username)
   - Отправляет первое сообщение через Telethon
   - Обновляет статус и сохраняет chat_id

2. **warmup_api.py** — FastAPI сервис
   - POST /warmup — запуск прогрева
   - GET /status — статус последнего запуска
   - GET /health — проверка работоспособности

3. **systemd/warmup-api.service** — автозапуск

### Настройки в .env
```
TELEGRAM_API_ID=39052174
TELEGRAM_API_HASH=abb12e0f8f025acdfbda295d6f3d8cd9
TELEGRAM_PHONE=+79145819661

GOOGLE_SHEETS_ID=1alr08qWL2TTVF-1nuDeU4NVXoGgyODgLKeTsa16_kxE
GOOGLE_SHEET_NAME=Telegram_Leads_Template
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json

WARMUP_DAILY_LIMIT=20
WARMUP_DELAY_MIN=60
WARMUP_DELAY_MAX=180
```

### Требуемые колонки в таблице
- `usernames` — username для связи (из парсера)
- `status` — статус лида (new → contacted → ready/refused)
- `chat_id` — ID чата (заполняется после первого сообщения)
- `user_id` — ID пользователя
- `contacted_at` — дата контакта
- `warmup_error` — ошибка если не удалось написать

### Запуск

```bash
# Разово
python warmup_sender.py

# Как сервис
sudo cp systemd/warmup-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable warmup-api
sudo systemctl start warmup-api

# Вызов из n8n
curl -X POST http://localhost:8001/warmup -H "Content-Type: application/json" -d '{"limit": 10}'
```

### Защита от банов
- Задержка 60-180 сек между сообщениями
- Лимит 20 сообщений в день
- Разные варианты текста первого сообщения
- Обработка FloodWait и PeerFlood ошибок

## Следующие шаги
1. Создать service_account.json для Google Sheets
2. Добавить колонки в таблицу если их нет
3. Запустить тест на 2-3 лидах
4. Настроить связку с AI ботом прогрева
