# Сессия: Исправление бота прогрева лидов
**Дата:** 2026-03-09

## Проблема
Бот молчит - не отвечает на сообщения пользователей.

## Диагностика
1. Проверили скриншот workflow ID#784 в n8n
2. n8n API недоступен извне (SSL/network error)
3. Нашли локальный файл: `workflows/realty_warmup_full.json`

## Причина
В роутере был `"fallbackOutput": -1` - это означает что неизвестные action отбрасываются.

Когда пользователь пишет любой текст (не `/start` и не callback от кнопки):
- Код разбора возвращает `action: 'unknown'`
- Роутер не находит правило для 'unknown'
- fallbackOutput = -1 = данные никуда не идут
- Бот молчит

## Исправление
Изменили `"fallbackOutput": -1` на `"fallbackOutput": 0`

Теперь любое сообщение направляется в ветку "Новый лид" (output 0).

**Файл:** `workflows/realty_warmup_full.json`
**Строка:** 75

## Что нужно сделать дальше
1. Импортировать исправленный JSON в n8n
2. Заменить placeholder'ы:
   - `YOUR_TG_CRED_ID` → ID Telegram credentials
   - `YOUR_SHEETS_CRED_ID` → ID Google Sheets credentials
   - `YOUR_SHEET_ID` → ID Google таблицы с лидами
3. Активировать workflow
4. Протестировать бота

## Структура workflow
```
🤖 Бот (Telegram Trigger)
    ↓
📋 Разбор (Code) - парсит callback_data или текст
    ↓
Callback? (If) - проверяет есть ли cbId
    ↓ true          ↓ false
    ✓ (answer)      🔀 Роутер
    ↓
🔀 Роутер ←─────────┘
    ↓ output 0: start/next_lead/unknown
📊 Новый лид (Google Sheets - читает status=new)
    ↓
Есть лид? (If)
    ↓ true              ↓ false
📱 Показать лида    📱 Нет лидов
```

## Переменные окружения (из .env)
- `N8N_URL`: https://n8n.arendadom24.ru
- `TELEGRAM_API_ID`: 39052174
- `TELEGRAM_PHONE`: +79145819661

## Коммит
```
fix: роутер теперь обрабатывает любые сообщения, не только /start
fallbackOutput изменен с -1 на 0
```

## Ключевые файлы
- `/home/user/2026/workflows/realty_warmup_full.json` - исправленный workflow
- `/home/user/2026/.env` - переменные окружения
- `/home/user/2026/CLAUDE.md` - инструкции проекта
