# n8n Workflows — Telegram Leads Automation
**Дата последнего обновления:** 2026-03-17
**Версия:** FIXED (исправленные воркфлоу)
**Репозиторий:** https://github.com/alexprox10-coder/2026/tree/claude/telegram-leads-table-01U6txiEdxnVLHQBH6muGShs/n8n-workflows/fixed

---

## Общая архитектура

```
Пользователь пишет нишу в Telegram боту
       ↓
WF1 — AI Agent Bot
  • Claude (OpenRouter) создаёт профиль ниши
  • Python API ищет Telegram-каналы
  • Claude оценивает (скоринг) каналы
  • Сохраняет каналы в Google Sheets (Sources)
  • Бот показывает карточки каналов с кнопками ✅/❌
       ↓
[Кнопка: Поиск лидов из найденных каналов]
  • Диалог: "Сколько дней назад парсить?" → вводишь число
  • Диалог: "Введи ключевые слова" → вводишь слова
       ↓
WF2 — AI Parser
  • Получает список одобренных каналов из Sheets
  • Python API парсит посты из каналов
  • Claude (Gemini via OpenRouter) анализирует каждый лид
  • Сохраняет лиды в Google Sheets (Leads)
  • Отправляет 1 итоговый отчёт в бот
       ↓
[Кнопка: Написать лидам]
       ↓
WF3 — Smart Lead Messenger
  • Читает горячих лидов (A) из Sheets
  • Claude генерирует персональное сообщение для каждого
  • Python API отправляет сообщения каждому лиду
  • Обновляет статус лида в таблице → "contacted"
  • Итоговый отчёт в бот
```

---

## WF1 — AI Agent Bot

**Файл:** `01_ai_agent_bot_FIXED.json`
**Назначение:** Telegram-бот управления. Добавление ниш, поиск и одобрение каналов, запуск парсинга.

### Триггер
- **TG Trigger** — webhook от Telegram Bot API

### Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие + список команд |
| `/add_niche [ниша]` | Добавить нишу и найти каналы |
| `/approve_sources` | Показать каналы на утверждение (карточки с кнопками) |
| `/start_parse` | Запустить диалог → дни → ключевые слова → WF2 |
| `/view_leads` | Показать горячих лидов (A) |
| `/status` | Статус каналов (одобрено/ожидает) |
| `/niches` | Список активных ниш |

### Callback-кнопки

| Action | Описание |
|--------|----------|
| `approve_<channel_id>` | Одобрить канал → статус "yes" в Sheets |
| `reject_<channel_id>` | Отклонить канал → статус "no" в Sheets |
| `sent_<lead_id>` | Отметить лид как отправленный |

### Поток `/add_niche`

```
1. Извлечь команду (code node)
   └─ читает msg.text, выделяет cmd и args
2. Есть аргумент?
   ├─ НЕТ → "Укажи нишу после команды"
   └─ ДА →
3. Уведомление о старте → "Анализирую нишу..."
4. Подготовить запрос Claude ниша
   └─ промпт: создать профиль ниши как JSON
      {name, description, ai_keywords, target_audience, ...}
5. Claude профиль ниши [OpenRouter API]
   └─ URL: https://openrouter.ai/api/v1/chat/completions
6. Парсинг профиля ниши → извлекает JSON из ответа
7. Сохранить нишу → Google Sheets (Niches tab)
8. Уведомление → "Ниша создана, ищу каналы..."
9. Подготовить запрос поиска → берёт ai_keywords (до 15 штук)
10. Поиск каналов [Python API]
    └─ URL: http://172.17.0.1:5000/search_channels
    └─ payload: {keywords: [...], chat_id: <твой_chat_id>}
11. Подготовить запрос скоринга → Claude оценивает до 30 каналов
12. Claude скоринг каналов [OpenRouter API]
13. Объединить оценки → мёрдж данных поиска + AI-оценок
14. Сохранить источники → Google Sheets (Sources tab)
    └─ appendOrUpdate по ключу channel_id
15. Итог ниши → формирует список топ-8 pending каналов
16. Итоговое уведомление → показывает карточки каналов
```

### Поток `/start_parse` (диалог)

```
1. Начать диалог парсинга (code node)
   └─ state[`dialog_${chatId}`] = { step: 'waiting_days' }
2. Спросить дни → "Сколько дней назад искать?"
---
(пользователь вводит текст, WF1 снова триггерится)
3. Обработать текст диалога (code node)
   └─ if step == 'waiting_days':
        сохранить days, step → 'waiting_keywords'
        вернуть reply: "Введи ключевые слова"
   └─ if step == 'waiting_keywords':
        сохранить keywords, шаг завершён
        вернуть action: 'run', days, keywords
4. Диалог завершён?
   ├─ НЕТ (action != 'run') → Ответить диалог (промежуточный ответ)
   └─ ДА →
5. Запустить парсинг → HTTP POST к WF2 webhook
   └─ URL: https://n8n.arendadom24.ru/webhook/ai-parse-trigger
   └─ payload: {days_back, keywords, chat_id}
6. Уведомление → "Парсинг запущен!"
```

### Ключевые исправления WF1

| Проблема | Было | Стало |
|----------|------|-------|
| Чтение ниши | `payload.niche` (всегда undefined) | `msg.text` / `args` из сообщения |
| chat_id | Захардкожен "7984101063" | Читается из `msg.chat.id` |
| Ввод дней | Воспринимался как новая ниша | Диалоговый state machine |
| После дней | Поток обрывался | Запрашивает ключевые слова |
| Ввод ключевых слов | Обработчика не было | Новая нода сохраняет и передаёт в WF2 |

### Внешние сервисы WF1

| Сервис | URL / Настройка |
|--------|----------------|
| Telegram Bot API | Credential: Telegram Bot (токен бота) |
| OpenRouter (Claude) | `https://openrouter.ai/api/v1/chat/completions` — credential: OpenRouter API Key |
| Python Parser API | `http://172.17.0.1:5000/search_channels` |
| Google Sheets — Niches | Spreadsheet ID + лист "Niches" |
| Google Sheets — Sources | Spreadsheet ID + лист "Sources" |
| Google Sheets — Leads | Spreadsheet ID + лист "Leads" |
| WF2 Webhook | `https://n8n.arendadom24.ru/webhook/ai-parse-trigger` |

---

## WF2 — AI Parser

**Файл:** `02_ai_parser_FIXED.json`
**Назначение:** Парсинг постов из Telegram-каналов, AI-анализ каждого лида, сохранение в Sheets.

### Триггеры
- **Webhook Trigger** — вызывается WF1 с параметрами `{days_back, keywords, chat_id}`
- **Schedule Trigger (6ч)** — автоматический запуск каждые 6 часов

### Полный поток

```
1. Нормализовать входные данные (code node)
   └─ читает из body: days_back (default 7), keywords (default []), chat_id
   └─ обрабатывает как webhook payload, так и schedule trigger

2. Параллельно:
   ├─ Получить источники (approved) → Google Sheets, фильтр: approved == "approved"
   └─ Получить ниши → Google Sheets, все активные ниши

3. Сформировать запрос парсера (code node)
   └─ берёт каналы из Sources, ниши, days_back, keywords
   └─ считает total_channels

4. Есть каналы?
   ├─ НЕТ (total == 0) → "Ошибка: нет одобренных каналов"
   └─ ДА →

5. Вызов парсера (Python) [HTTP POST]
   └─ URL: http://172.17.0.1:5000/parse
   └─ payload: {channels: [...], days_back, keywords, niches: [...]}

6. Подготовить лиды (code node)
   └─ извлекает posts/messages/results из ответа парсера
   └─ нормализует поля: text, author, username, channel, date, post_url

7. Фильтр пустых лидов
   └─ убирает записи без текста

8. [LOOP по каждому лиду]
   Claude анализ лида (Gemini) [HTTP POST → OpenRouter]
   └─ модель: google/gemini-2.0-flash-001 (или настроенная)
   └─ анализирует: is_lead (bool), priority (A/B/C), reason, contact_intent

9. Парсинг AI ответа (code node)
   └─ FIX: использует $('Фильтр пустых лидов').item.json
      (не .first() — привязка к текущему лиду, а не первому)

10. Сохранить лид → Google Sheets (Leads tab)
    └─ appendOrUpdate по post_id

11. Горячий лид A?
    ├─ ДА → Уведомление горячего лида (немедленно в Telegram)
    └─ НЕТ → продолжить

12. Агрегировать все лиды (code node)
    └─ FIX: собирает ВСЕ лиды за запуск в один отчёт
    └─ считает hot_a, warm_b, cold_c, total_posts

13. Отправить итоговый отчёт → 1 сообщение в Telegram
    └─ "Парсинг завершён! Обработано: X, Горячих (A): Y, Тёплых (B): Z, Холодных (C): W"
```

### Ключевые исправления WF2

| Проблема | Было | Стало |
|----------|------|-------|
| Привязка данных лида | AI-ответ лида №5 → данные лида №1 | `.item.json` вместо `.first().json` |
| Отчёт | 50 отдельных сообщений | 1 итоговый отчёт через агрегацию |
| Фильтр каналов | Без фильтра по статусу | `approved == "approved"` |

### Структура лида в Google Sheets (Leads)

| Колонка | Описание |
|---------|----------|
| post_id | Уникальный ID поста |
| text | Текст поста |
| author | Имя автора |
| username | @username для отправки |
| channel | Название/ссылка канала |
| date | Дата поста |
| post_url | Ссылка на пост |
| is_lead | true/false |
| ai_priority | A / B / C |
| ai_reason | Причина классификации |
| contact_intent | Намерение связаться |
| status | new / contacted / rejected |

### Внешние сервисы WF2

| Сервис | URL / Настройка |
|--------|----------------|
| Telegram Bot API | Credential: Telegram Bot |
| OpenRouter (Gemini) | `https://openrouter.ai/api/v1/chat/completions` |
| Python Parser API | `http://172.17.0.1:5000/parse` |
| Google Sheets — Sources | Фильтр: approved == "approved" |
| Google Sheets — Niches | Все активные ниши |
| Google Sheets — Leads | appendOrUpdate по post_id |

---

## WF3 — Smart Lead Messenger

**Файл:** `03_smart_lead_FIXED.json`
**Назначение:** AI-генерация персональных сообщений для горячих лидов и автоматическая отправка.

### Триггеры
- **Webhook Trigger (превью)** — показать предварительный список лидов с превью сообщений
- **Webhook Execute (отправка)** — реально отправить сообщения всем лидам

### Поток "Превью" (preview)

```
1. Нормализовать chat_id (превью) → читает chat_id из body или дефолт
2. Читать каналы из sources → Google Sheets (Sources)
3. Подготовить запрос → формирует список channel_url/username
4. ВЫЗВАТЬ ПАРСЕР [HTTP → Python API]
   └─ URL: http://172.17.0.1:5000/webhook/n8n
5. Извлечь лиды → из results/leads/raw_data
6. Записать лиды → Google Sheets (Leads) — appendOrUpdate
7. Получить A-лиды (превью) → из Leads, фильтр priority == A
8. Сформировать превью (code node)
   └─ фильтрует только лидов с username
   └─ формирует previewText — список лидов для отправки
9. Есть лиды для отправки?
   ├─ НЕТ → "Нет горячих лидов с username"
   └─ ДА → Отправить превью в Telegram
```

### Поток "Execute" (отправка)

```
1. Нормализовать chat_id (execute)
2. Получить A-лиды (execute) → из Leads, фильтр priority == A, status == new
3. Фильтровать лидов с username (code node)
   └─ убирает без username
4. Проверить наличие лидов (execute)
   ├─ НЕТ → "Нет лидов для отправки"
   └─ ДА →

5. [LOOP по каждому лиду]
   Claude генерирует сообщение [HTTP POST → OpenRouter]
   └─ промпт: написать персональное сообщение под конкретный пост лида
   └─ учитывает: текст поста, имя автора, нишу

6. Извлечь сгенерированное сообщение (code node)
   └─ FIX: использует $('Фильтровать лидов с username').item.json
      (привязка к текущему лиду)

7. Отправить сообщение (Python) [HTTP POST]
   └─ URL: http://172.17.0.1:5000/send_message
   └─ payload: {username, message_text}

8. Проверить результат отправки (code node)
   └─ FIX: использует $('Извлечь сгенерированное сообщение').item.json

9. Обновить статус → contacted → Google Sheets (Leads)
   └─ FIX: обновляет текущего лида (не только первого)

10. Собрать статистику отправки → total, successful, errors
11. Итоговый отчёт рассылки → "Рассылка завершена! Написал X лидам"
```

### Ключевые исправления WF3

| Проблема | Было | Стало |
|----------|------|-------|
| Фильтр каналов | `" approved"` (с пробелом) — 0 каналов | `"approved"` — работает |
| Запись лидов | В таблицу Sources (каналов) | В таблицу Leads |
| Генерация сообщений | Одно сообщение для лида №1 → всем 50 | `.item.json` — каждый лид своё |
| Обновление статуса | Только лид №1 | Каждый отправленный лид |

### Внешние сервисы WF3

| Сервис | URL / Настройка |
|--------|----------------|
| Telegram Bot API | Credential: Telegram Bot |
| OpenRouter (Claude) | `https://openrouter.ai/api/v1/chat/completions` |
| Python Parser API (send) | `http://172.17.0.1:5000/send_message` |
| Python Parser API (parse) | `http://172.17.0.1:5000/webhook/n8n` |
| Google Sheets — Sources | Читает каналы |
| Google Sheets — Leads | Читает A-лиды, обновляет статус |

---

## Google Sheets — Структура таблиц

### Лист: Niches
| niche_id | name | description | ai_keywords | target_audience | active | created_at |
|----------|------|-------------|-------------|-----------------|--------|------------|

### Лист: Sources (каналы)
| channel_id | channel_url | title | description | subscribers | ai_score | ai_reasons | approved | niche_id | added_at |
|------------|-------------|-------|-------------|-------------|----------|------------|----------|----------|----------|

**Значения поля `approved`:**
- `pending` — ожидает одобрения
- `approved` — одобрен (используется в WF2 и WF3)
- `no` — отклонён

### Лист: Leads
| post_id | text | author | username | channel | date | post_url | is_lead | ai_priority | ai_reason | contact_intent | status | niche_id | parsed_at |
|---------|------|--------|----------|---------|------|----------|---------|-------------|-----------|----------------|--------|----------|-----------|

**Значения поля `ai_priority`:**
- `A` — горячий лид (контактирует в посте)
- `B` — тёплый лид (интерес есть)
- `C` — холодный

**Значения поля `status`:**
- `new` — новый
- `contacted` — написали
- `rejected` — отклонён

---

## Python API — Эндпоинты

| Метод | URL | Payload | Ответ |
|-------|-----|---------|-------|
| POST | `/search_channels` | `{keywords: [], chat_id}` | `{channels: [{title, url, subscribers, ...}]}` |
| POST | `/parse` | `{channels: [], days_back, keywords, niches}` | `{posts: [{text, author, username, channel, date, post_url}]}` |
| POST | `/send_message` | `{username, message_text}` | `{success: bool, error?}` |
| POST | `/webhook/n8n` | `{channels: []}` | `{results: [{...}]}` |

**Базовый URL:** `http://172.17.0.1:5000` (Docker host на сервере n8n)

---

## OpenRouter — Модели и настройки

| Воркфлоу | Нода | Модель |
|----------|------|--------|
| WF1 | Claude профиль ниши | `anthropic/claude-3.5-sonnet` (или настроенная) |
| WF1 | Claude скоринг каналов | `anthropic/claude-3.5-sonnet` |
| WF2 | Claude анализ лида | `google/gemini-2.0-flash-001` |
| WF3 | Claude генерирует сообщение | `anthropic/claude-3.5-sonnet` |

**API URL:** `https://openrouter.ai/api/v1/chat/completions`
**Header:** `Authorization: Bearer <OPENROUTER_API_KEY>`

---

## Credentials в n8n

| Название | Тип | Где используется |
|----------|-----|-----------------|
| Telegram Bot | Telegram API | WF1, WF2, WF3 |
| OpenRouter API Key | HTTP Header Auth | WF1, WF2, WF3 |
| Google Sheets | OAuth2 / Service Account | WF1, WF2, WF3 |

---

## Webhook URLs

| Воркфлоу | Путь | Кто вызывает |
|----------|------|--------------|
| WF2 | `/webhook/ai-parse-trigger` | WF1 (команда /start_parse) |
| WF3 preview | `/webhook/smart-lead-preview` | WF1 (кнопка "Написать лидам") |
| WF3 execute | `/webhook/smart-lead-execute` | WF1 или прямой вызов |

---

## Исправления — Сводная таблица

### WF1 — AI Agent Bot

| # | Проблема | Исправление |
|---|----------|------------|
| 1 | Ниша читалась из `payload.niche` (всегда пустой) | Читает из текста сообщения через `Извлечь команду` |
| 2 | chat_id "7984101063" захардкожен | Берётся из `msg.chat.id` |
| 3 | Ввод числа дней → запускал поиск каналов | State machine: `dialog_${chatId}.step` |
| 4 | После дней поток обрывался | Добавлена нода "Спросить ключевые слова" |
| 5 | Ввод ключевых слов не обрабатывался | Новая нода сохраняет ключевые слова |
| 6 | Ключевые слова не передавались в WF2 | Передаются в payload при вызове WF2 |

### WF2 — AI Parser

| # | Проблема | Исправление |
|---|----------|------------|
| 1 | AI-ответ лида №5 → данные лида №1 | `.item.json` вместо `.first().json` в "Парсинг AI ответа" |
| 2 | 50 отдельных отчётов вместо одного | Нода "Агрегировать все лиды" + один финальный отчёт |

### WF3 — Smart Lead

| # | Проблема | Исправление |
|---|----------|------------|
| 1 | Фильтр `" approved"` (пробел) → 0 каналов | `"approved"` без пробела |
| 2 | Лиды записывались в Sources вместо Leads | Исправлен spreadsheet/sheet в "Записать лиды" |
| 3 | Одно сообщение для лида №1 → всем | `.item.json` в "Извлечь сгенерированное сообщение" |
| 4 | Статус обновлялся только у лида №1 | `.item.json` в "Проверить результат отправки" |

---

## Запуск и тестирование

### Минимальный тест WF1
1. Открой Telegram-бота
2. Отправь: `/add_niche аренда квартир Москва`
3. Ожидай: "Анализирую нишу..." → "Ниша создана, ищу каналы..." → карточки каналов

### Минимальный тест диалога парсинга
1. Отправь: `/start_parse`
2. Бот спросит: "Сколько дней назад искать?"
3. Введи: `5`
4. Бот спросит: "Введи ключевые слова"
5. Введи: `сниму квартиру, ищу жильё`
6. Ожидай: "Парсинг запущен!"

### Минимальный тест WF2
- Проверить что в Sheets (Sources) есть каналы со статусом `approved`
- Вручную вызвать webhook WF2 с payload: `{"days_back": 3, "keywords": ["аренда"], "chat_id": "ВАШ_CHAT_ID"}`

### Минимальный тест WF3
- Проверить что в Sheets (Leads) есть лиды с `ai_priority = A` и `username != ""`
- Вызвать webhook WF3 execute

---

## Файлы в репозитории

```
n8n-workflows/
├── fixed/
│   ├── 01_ai_agent_bot_FIXED.json      — WF1 исправленный
│   ├── 02_ai_parser_FIXED.json         — WF2 исправленный
│   └── 03_smart_lead_FIXED.json        — WF3 исправленный
└── WORKFLOWS_DOCUMENTATION.md          — этот файл
```

---

*Документация сгенерирована: 2026-03-17*
