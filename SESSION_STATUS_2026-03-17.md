# Статус проекта — 2026-03-17

## Проект
**Бот:** ПРОГРЕВ ЛИДОВ НЕДВ 👆
**Username:** @TelePars24_bot
**Пользователь:** Александр (Alex_Chat24)
**Chat ID:** 7984101063

---

## Архитектура системы

```
Пользователь → /add_niche <ниша>
       ↓
WF1 (01_ai_agent_bot_V6.json)
  Claude создаёт профиль ниши
  Python API /search_channels → ищет Telegram-каналы
  Claude скоринг (0-1): score >= 0.65 = auto-approved, < 0.65 = pending
  Сохраняет в Google Sheets (1lCyk_...) → лист "sources"
  Бот показывает карточки каналов с кнопками ✅/❌
       ↓
[Кнопка: запустить поиск лидов]
  Диалог: количество дней → ключевые слова
  WF1 вызывает WF2 через https://n8n.arendadom24.ru/webhook/ai-parse-trigger
       ↓
WF2 (02_ai_parser_V5.json)
  Читает approved каналы из Google Sheets (1lCyk_...) → sources
  Python API /parse → парсит посты каналов
  Claude/Gemini анализирует каждый лид → приоритет A/B/C
  Сохраняет лиды в Google Sheets (1alr08_...) → leads
  Merge-нода ждёт все ветки → итоговый отчёт
       ↓
WF3 (03_smart_lead_V2.json)
  Webhook (превью/execute) → читает A-лиды из 1alr08_... (status=new)
  Claude генерирует персонализированное сообщение
  Python API /send_message → отправляет через Telegram userbot
  Обновляет статус лида → "contacted"
```

---

## Google Sheets

| Таблица | ID | Листы |
|---------|----|----|
| Источники (каналы) | `1lCyk_zZTwq0_Nssk8skUHETpelS6zmxg2a0p2-0N_sw` | `sources`, `ниши` |
| Лиды | `1alr08qWL2TTVF-1nuDeU4NVXoGgyODgLKeTsa16_kxE` | leads (`gid=1925947783`) |

### Структура листа sources (1lCyk_...)
| url | title | username | subscribers | description | score | status | niche |
|-----|-------|----------|-------------|-------------|-------|--------|-------|
| t.me/... | Название | @channel | 1500 | Описание | 0.82 | approved | аренда квартир |

### Структура листа leads (1alr08_...)
| username | post_url | text | ai_priority | is_lead | status | ... |
|----------|----------|------|-------------|---------|--------|-----|
| @user123 | t.me/... | текст | A | true | new | ... |

---

## Python API (telethon_api.py)

**Путь:** `/home/user/2026/telethon_api.py`
**Порт:** 5000
**Запуск:** `python3 /home/user/2026/telethon_api.py`

### Существующие эндпоинты

| Эндпоинт | Метод | Статус | Описание |
|----------|-------|--------|----------|
| `/health` | GET | ✅ Работает | Проверка подключения |
| `/send` | POST | ✅ Работает | Отправка сообщения по username |
| `/search_channels` | POST | ✅ Работает | Поиск Telegram-каналов по ключевым словам |

### ❌ ОТСУТСТВУЮЩИЕ эндпоинты

| Эндпоинт | Кто вызывает | Что должен делать |
|----------|-------------|-------------------|
| `/parse` | WF2, нода "Вызов парсера (Python)" | Парсинг постов из списка каналов |
| `/send_message` | WF3, нода "Отправить сообщение (Python)" | То же что `/send`, но WF3 вызывает с другим URL |

---

## Версии воркфлоу

| Файл | Версия | Статус |
|------|--------|--------|
| `01_ai_agent_bot_V6.json` | V6 | ✅ Актуальная — все ID таблиц и листов исправлены |
| `02_ai_parser_V5.json` | V5 | ⚠️ Актуальная, но /parse endpoint отсутствует |
| `03_smart_lead_V2.json` | V2 | ⚠️ Актуальная, но /send_message endpoint отсутствует + баг в ВЫЗВАТЬ ПАРСЕР |

### Ссылки для скачивания

- **WF1 V6:** https://raw.githubusercontent.com/alexprox10-coder/2026/claude/telegram-leads-table-01U6txiEdxnVLHQBH6muGShs/n8n-workflows/fixed/01_ai_agent_bot_V6.json
- **WF2 V5:** https://raw.githubusercontent.com/alexprox10-coder/2026/claude/telegram-leads-table-01U6txiEdxnVLHQBH6muGShs/n8n-workflows/fixed/02_ai_parser_V5.json
- **WF3 V2:** https://raw.githubusercontent.com/alexprox10-coder/2026/claude/telegram-leads-table-01U6txiEdxnVLHQBH6muGShs/n8n-workflows/fixed/03_smart_lead_V2.json

---

## Что исправлено по всем версиям (полная история)

| # | Воркфлоу | Версия | Проблема | Решение |
|---|----------|--------|----------|---------|
| 1 | WF1 | V2 | URL начинался с `=` → HTTP запрос не срабатывал | Убран `=` из URL |
| 2 | WF1 | V4 | username канала не сохранялся → WF2 не мог найти каналы | Добавлено поле username |
| 3 | WF1+WF2 | V4/V5 | Keywords шли строкой, не массивом | Преобразование в массив |
| 4 | WF1 | V4 | Таймаут 10 сек → WF1 падал при запуске WF2 | Увеличен таймаут |
| 5 | WF2 | V5 | Гонка параллельных веток → лиды собирались неполностью | Добавлена Merge-нода |
| 6 | WF2 | V5 | Webhook ждал ответа → timeout | Async-ответ |
| 7 | WF1 | V5 | Auto-approve каналов score >= 0.65 | Добавлена логика авто-утверждения |
| 8 | WF1 | V6 | Неправильные ID таблиц (писало в таблицу лидов вместо sources) | Все ID исправлены на 1lCyk_... |
| 9 | WF1 | V6 | Листы назывались по-английски (niches вместо ниши) | Переименованы на русские |
| 10 | WF1 | V6 | `Объединить оценки`: при ошибке Claude писал `{error:true}` в Sheets | `return []` вместо error-объекта |
| 11 | telethon_api.py | — | Отсутствовал `/search_channels` endpoint | Добавлен endpoint |
| 12 | telethon_api.py | — | Порт был 5555 вместо 5000 | Исправлен на 5000 |

---

## Оставшиеся проблемы — ЧТО ДЕЛАТЬ ДАЛЬШЕ

### Проблема 1 (КРИТИЧЕСКАЯ) — /parse endpoint отсутствует

**Кто вызывает:** WF2, нода `Вызов парсера (Python)`
**URL:** `http://172.17.0.1:5000/parse`
**Тело запроса:**
```json
{
  "channels": ["username1", "username2"],
  "days_back": 7,
  "keywords": ["аренда", "снять"],
  "limit_per_channel": 50
}
```
**Ожидаемый ответ:**
```json
{
  "posts": [
    {
      "channel": "username1",
      "post_id": 123,
      "text": "текст поста",
      "date": "2026-03-10",
      "views": 500,
      "url": "https://t.me/username1/123"
    }
  ]
}
```
**Действие:** Добавить `/parse` endpoint в `telethon_api.py` который через Telethon читает посты из каналов за N дней.

---

### Проблема 2 (ВЫСОКАЯ) — /send_message endpoint отсутствует

**Кто вызывает:** WF3, нода `Отправить сообщение (Python)`
**URL:** `http://172.17.0.1:5000/send_message`
**Тело запроса:**
```json
{
  "username": "someuser",
  "message": "текст сообщения",
  "post_url": "https://t.me/channel/123"
}
```
**Действие:** Добавить `/send_message` как алиас `/send` в `telethon_api.py`.
Разница: WF3 передаёт `message` вместо `text`, и добавляет `post_url`.

---

### Проблема 3 (СРЕДНЯЯ) — Баг в WF3 нода ВЫЗВАТЬ ПАРСЕР

**Текущий URL:** `http://172.17.0.1:5000/webhook/n8n`
**Проблема:** Порт 5000 — это Python API, а не n8n. n8n работает на порту 5678.
**Вероятно должно быть:** `http://172.17.0.1:5678/webhook/ai-parse-trigger` (или убрать этот нод совсем — WF3 не должен вызывать парсер)

---

### Проблема 4 (НИЗКАЯ) — WF1 не импортирован в n8n (V6)

После создания V6 нужно импортировать файл в n8n:
1. n8n → Workflows → Import
2. Выбрать файл `01_ai_agent_bot_V6.json`
3. Деактивировать старый WF1 и активировать V6

---

## Внешние credentials (нужны в n8n)

| Сервис | Credential в n8n | Где используется |
|--------|-----------------|-----------------|
| Telegram Bot | `Telegram ПАРСЕР` | WF1 (TG Trigger + отправка сообщений) |
| Google Sheets | `Google Sheets account` | WF1, WF2, WF3 (чтение/запись) |
| OpenRouter (Claude) | `OpenRouter API` | WF1 профиль ниши + скоринг |
| OpenRouter (Gemini) | `OpenRouter API` | WF2 анализ лидов |
| Python API | Без credentials | `http://172.17.0.1:5000` (внутренняя сеть Docker) |

---

## Порядок запуска

```bash
# 1. На сервере 155.212.133.90
ssh root@155.212.133.90

# 2. Запустить Python API
cd /home/user/2026
python3 telethon_api.py &

# 3. Проверить что работает
curl http://localhost:5000/health
# Ожидаемо: {"connected": true, "status": "ok"}
```

После импорта WF1 V6 в n8n:
```
/add_niche аренда квартир Москва
```
→ бот должен ответить и найти каналы.

---

## Файлы проекта

| Файл | Путь на сервере | Описание |
|------|----------------|----------|
| `telethon_api.py` | `/home/user/2026/telethon_api.py` | Python HTTP API для Telethon userbot |
| `.env` | `/home/user/2026/.env` | TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE |
| WF1 V6 | `n8n-workflows/fixed/01_ai_agent_bot_V6.json` | Поиск каналов (актуальная версия) |
| WF2 V5 | `n8n-workflows/fixed/02_ai_parser_V5.json` | Парсинг лидов |
| WF3 V2 | `n8n-workflows/fixed/03_smart_lead_V2.json` | Рассылка сообщений |
