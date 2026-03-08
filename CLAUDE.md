# Контекст проекта

## Что это
Telegram парсер для сбора крипто-лидов с интеграцией n8n workflow.

## Стек технологий
- **Python (Telethon)** — парсинг Telegram каналов
- **n8n** — автоматизация воркфлоу, триггеры, уведомления
- **Node.js** — Telegram бот (bot.js)

## Ключевые файлы

### Парсеры
- `telegram_parser_api.py` — основной API парсера (порт 8000)
- `telegram_parser_telethon.py` — парсер на Telethon
- `channel_finder_bot.py` — бот для поиска каналов
- `crypto_leads_parser.py` — парсер крипто-лидов

### Воркфлоу n8n
- `workflow_fixed.json` — актуальный рабочий воркфлоу
- `telegram_parser_pro_v4_dual_trigger.json` — версия с двойным триггером
- `lead_bot_v2_improved.json` — улучшенный бот для лидов

### Конфигурация
- `.env.example` — шаблон переменных окружения
- `requirements_channel_finder.txt` — Python зависимости
- `start_*.sh` — скрипты запуска

## Архитектура деплоя

```
[VPS сервер]
├── Python API (telegram_parser_api.py) → порт 8000
├── n8n → порт 5678
└── Telegram бот (bot.js)
```

## Требования к серверу
- VPS: 1 CPU, 1-2 GB RAM
- Ubuntu 20.04/22.04
- Python 3.9+
- Node.js 18+
- Открытые порты: 8000, 5678

## Переменные окружения
```
TELEGRAM_API_ID=xxx        # с my.telegram.org/apps
TELEGRAM_API_HASH=xxx      # с my.telegram.org/apps
TELEGRAM_PHONE=+7xxx       # номер для авторизации
TELEGRAM_WEBHOOK_URL=xxx   # URL бота для уведомлений
TELEGRAM_CHAT_ID=xxx       # ID чата для уведомлений
```

## Предпочтения
- Отвечай на русском языке
- Комментарии в коде на русском
- Предлагай простые решения без оверинжиниринга
- При ошибках сначала проверяй логи

## TODO
- [ ] Создать INSTALL_GUIDE.md — пошаговая инструкция установки
- [ ] Скрипт автоустановки install.sh для VPS
- [ ] Настройка systemd сервисов для автозапуска

## Частые команды
```bash
# Запуск парсера
python3 telegram_parser_api.py

# Запуск n8n
npx n8n

# Проверка логов
journalctl -u telegram-parser-api -f
```
