# Настройка агента прогрева лидов

## Архитектура

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Telegram Bot   │────▶│  Warmup Agent    │────▶│  Google Sheets  │
│  (управление)   │     │  (Telethon)      │     │  (лиды)         │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   OpenRouter AI  │
                        │   (диалоги)      │
                        └──────────────────┘
```

## Шаг 1: Создать Telegram бота

1. Открой @BotFather в Telegram
2. Отправь `/newbot`
3. Придумай имя (например: `Warmup Manager Bot`)
4. Придумай username (например: `warmup_manager_bot`)
5. Скопируй токен бота

## Шаг 2: Создать Google Service Account

1. Открой https://console.cloud.google.com
2. Создай новый проект или выбери существующий
3. Включи Google Sheets API:
   - APIs & Services → Enable APIs → Google Sheets API
4. Создай Service Account:
   - APIs & Services → Credentials → Create Credentials → Service Account
   - Имя: `warmup-bot`
   - Роль: Editor
5. Создай ключ:
   - Нажми на созданный Service Account
   - Keys → Add Key → Create new key → JSON
   - Скачай файл
6. Переименуй в `service_account.json` и положи в папку проекта
7. **Важно!** Открой Google Sheets таблицу и добавь email Service Account (из JSON файла) как редактора:
   - Поделиться → добавить email вида `xxx@xxx.iam.gserviceaccount.com`

## Шаг 3: Получить OpenRouter API Key

1. Открой https://openrouter.ai
2. Зарегистрируйся
3. Settings → API Keys → Create Key
4. Скопируй ключ

## Шаг 4: Настроить .env

Открой `.env` и заполни:

```bash
# Telegram Bot (из шага 1)
WARMUP_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Твой Telegram ID (напиши @userinfobot чтобы узнать)
ADMIN_CHAT_ID=7984101063

# OpenRouter (из шага 3)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Google Sheets (уже заполнено)
GOOGLE_SHEETS_ID=1alr08qWL2TTVF-1nuDeU4NVXoGgyODgLKeTsa16_kxE
GOOGLE_SHEET_NAME=Telegram_Leads_Template
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json

# Настройки прогрева (можно оставить по умолчанию)
WARMUP_DELAY_MIN=60      # Минимальная пауза между сообщениями (сек)
WARMUP_DELAY_MAX=180     # Максимальная пауза (сек)
WARMUP_DAILY_LIMIT=20    # Лимит сообщений в день
```

## Шаг 5: Добавить колонку status в таблицу

В Google Sheets добавь колонку `status` (если нет).

Значения:
- `new` или пустое — новый лид
- `warming` — в процессе прогрева
- `qualified` — квалифицирован (готов к покупке)
- `refused` — отказался
- `unreachable` — не удалось написать

## Шаг 6: Установить зависимости

```bash
pip install -r requirements_warmup.txt
```

## Шаг 7: Запустить бота

```bash
python warmup_bot.py
```

## Использование

1. Напиши боту `/start`
2. Нажми "🔥 Прогреть 5" — отправит 5 сообщений лидам
3. Агент будет ждать ответы и вести AI-диалог
4. Результаты появятся в таблице

## Важные ограничения

- **Лимит 20 сообщений в день** — чтобы не забанили аккаунт
- **Пауза 60-180 сек между сообщениями** — имитация живого общения
- Пишем только тем у кого есть **username**
- Пропускаем посты с пометкой **is_ad=true**

## Логи

Логи сохраняются в `warmup_agent.log`

```bash
tail -f warmup_agent.log
```

## Запуск как сервис (systemd)

```bash
sudo nano /etc/systemd/system/warmup-bot.service
```

```ini
[Unit]
Description=Warmup Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDir=/root/2026
ExecStart=/usr/bin/python3 warmup_bot.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable warmup-bot
sudo systemctl start warmup-bot
sudo systemctl status warmup-bot
```

## Troubleshooting

### "Не удалось подключиться к Google Sheets"
- Проверь что файл `service_account.json` существует
- Проверь что email Service Account добавлен в таблицу как редактор

### "UserPrivacyRestrictedError"
- Пользователь закрыл личку, нельзя написать
- Статус автоматически станет `unreachable`

### "FloodWaitError"
- Telegram ограничил отправку
- Агент автоматически подождёт указанное время

### Не приходят ответы
- Убедись что Telethon сессия активна (`telegram_session.session`)
- Проверь что агент запущен и слушает сообщения
