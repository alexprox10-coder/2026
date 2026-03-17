# Итог сессий — WF1, WF2, WF3
**Дата:** 2026-03-17
**Проект:** ПРОГРЕВ ЛИДОВ НЕДВ 👆
**Бот:** @TelePars24_bot
**Пользователь:** Александр (Alex_Chat24) — Chat ID: 7984101063

---

## Ссылки для скачивания (последние версии)

| Воркфлоу | Версия | Ссылка |
|----------|--------|--------|
| **WF1** — Поиск каналов | V5 | https://raw.githubusercontent.com/alexprox10-coder/2026/claude/telegram-leads-table-01U6txiEdxnVLHQBH6muGShs/n8n-workflows/fixed/01_ai_agent_bot_V5.json |
| **WF2** — Парсинг лидов | V5 | https://raw.githubusercontent.com/alexprox10-coder/2026/claude/telegram-leads-table-01U6txiEdxnVLHQBH6muGShs/n8n-workflows/fixed/02_ai_parser_V5.json |
| **WF3** — Отправка сообщений | V2 | https://raw.githubusercontent.com/alexprox10-coder/2026/claude/telegram-leads-table-01U6txiEdxnVLHQBH6muGShs/n8n-workflows/fixed/03_smart_lead_V2.json |

---

## Логика системы

```
Пользователь пишет нишу в Telegram боту
       ↓
WF1 — Поиск каналов (01_ai_agent_bot_V5.json)
  • Claude создаёт профиль ниши
  • Python API ищет Telegram-каналы
  • Claude оценивает (скоринг) каналы
  • score >= 0.65 → статус "approved" (авто)
  • score < 0.65  → статус "pending" (кнопки ✅/❌)
  • Сохраняет каналы в Google Sheets (sources)
       ↓
[Кнопка: Поиск лидов] → диалог: дни + ключевые слова
       ↓
WF2 — Парсинг лидов (02_ai_parser_V5.json)
  • Читает из sources только status = "approved"
  • Python API парсит посты из каналов
  • Claude (Gemini) анализирует каждый лид
  • Сохраняет лиды в Google Sheets (leads)
  • Итоговый отчёт в бот
       ↓
[Кнопка: Написать лидам]
       ↓
WF3 — Отправка сообщений (03_smart_lead_V2.json)
  • Читает горячих лидов (A) из sheets
  • Claude генерирует персональное сообщение
  • Python API отправляет сообщения
  • Обновляет статус → "contacted"
```

---

## Все исправления по версиям

| # | Проблема | Воркфлоу | Версия |
|---|----------|----------|--------|
| 1 | URL начинался с `=` → HTTP запрос не срабатывал | WF1 | V2 |
| 2 | Dual-path aggregation → отчёт всегда неполный | WF2 | V2 |
| 3 | `username` канала не сохранялся → WF2 не мог найти каналы | WF1 | V4 |
| 4 | Keywords шли строкой, не массивом | WF1 + WF2 | V4/V5 |
| 5 | Таймаут 10 сек → WF1 падал при запуске WF2 | WF1 | V4 |
| 6 | Гонка параллельных веток → лиды собирались неполностью | WF2 | V5 |
| 7 | Webhook ждал ответа → timeout у WF1 | WF2 | V5 |
| 8 | Auto-approve каналов score >= 0.65 | WF1 | V5 |
| 9 | min_subscribers снижен 300 → 100 (больше каналов) | WF1 | V5 |

---

## Структура Google Sheets

### sources (каналы)
| Колонка | Значения |
|---------|---------|
| channel_url | https://t.me/... |
| channel_title | название |
| username | @username |
| niche | название ниши |
| score | 0.0 — 1.0 |
| status | `pending` / `approved` / `rejected` |
| added_at | дата |

### leads (лиды)
| Колонка | Значения |
|---------|---------|
| post_id | id поста |
| text | текст поста |
| author | имя |
| username | @username |
| channel | канал |
| date | дата |
| post_url | ссылка |
| ai_priority | `A` горячий / `B` тёплый / `C` холодный |
| ai_reason | причина оценки |
| status | `new` / `contacted` / `rejected` |

---

## Внешние сервисы

| Сервис | URL / Credential |
|--------|-----------------|
| Telegram Bot | credential: Telegram ПАРСЕР |
| OpenRouter | https://openrouter.ai/api/v1/chat/completions |
| Python Parser API | http://172.17.0.1:5000 |
| Google Sheets | ID: 1lCyk_zZTwq0_Nssk8skUHETpelS6zmxg2a0p2-0N_sw |
| n8n instance | https://n8n.arendadom24.ru |

## Webhook URLs

| Воркфлоу | Путь |
|----------|------|
| WF2 trigger | /webhook/ai-parse-trigger |
| WF3 preview | /webhook/smart-lead-preview |
| WF3 execute | /webhook/smart-lead-execute |

## OpenRouter модели

| Воркфлоу | Нода | Модель |
|----------|------|--------|
| WF1 | Claude профиль ниши | anthropic/claude-3.5-sonnet |
| WF1 | Claude скоринг каналов | anthropic/claude-3.5-sonnet |
| WF2 | Claude анализ лида | google/gemini-2.0-flash-001 |
| WF3 | Claude генерирует сообщение | anthropic/claude-3.5-sonnet |

---

## Инструкция по импорту в n8n

1. Скачать файл по ссылке выше
2. В n8n: **Settings → Import workflow**
3. Импортировать WF1, WF2, WF3
4. В Google Sheets (вкладка `sources`) убедиться что есть колонка `username`
5. **Активировать WF2** (зелёный тумблер) — он должен быть активен, ждать вебхук от WF1
6. Запустить: написать боту `/add_niche аренда квартиры`
