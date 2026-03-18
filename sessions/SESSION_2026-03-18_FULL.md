# Сессия 2026-03-18 — Полная документация

## Сервер
- **IP**: 155.212.133.90
- **OS**: Ubuntu 24.04.3 LTS
- **Python файл**: `/root/telegram_parser_api.py` (PID: 293971)
- **Python порт**: 5000
- **n8n домен**: https://n8n.arendadom24.ru

---

## Архитектура системы

```
WF1 (Бот) → WF2 (Парсер) → WF3 (Smart Lead)
```

### WF1 — Бот поиск каналов
**Команды бота:**
- `/add_niche [ниша]` — добавить нишу и найти новые каналы в Telegram
- `/approve_sources` — показать каналы на одобрение (pending)
- `/start_parse` — запустить парсинг лидов из одобренных каналов
- `/leads` — горячие лиды за 24ч
- `/send_leads` — написать горячим лидам
- `/niches` — активные ниши
- `/status` — статус системы

**Логика `/add_niche`:**
1. Claude (Gemini) создаёт профиль ниши → ai_keywords
2. Python `/search_channels` ищет каналы в Telegram по ключевым словам
3. Claude оценивает каналы (score ≥ 0.8 → approved, 0.5-0.8 → pending, <0.5 → rejected)
4. Сохраняет в Google Sheets `sources`

### WF2 — AI Parser
- Читает одобренные каналы из `sources`
- Вызывает Python `/parse` — парсит посты по ключевым словам
- Claude анализирует каждый лид (приоритет A/B/C)
- Сохраняет в Google Sheets `leads`
- Уведомляет в Telegram при горячем лиде (A)

### WF3 — Smart Lead
- Читает A-лиды из `leads`
- Claude генерирует персональное сообщение
- Python `/send_message` отправляет первое сообщение
- Обновляет статус → contacted

---

## Python API эндпоинты (`/root/telegram_parser_api.py`)

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/health` | GET | Проверка работоспособности |
| `/status` | GET | Статус последнего парсинга |
| `/parse` | POST | Запуск парсинга каналов |
| `/results` | GET | Результаты парсинга |
| `/results/leads` | GET | Лиды из результатов |
| `/webhook/n8n` | POST | Webhook для n8n |
| `/search_channels` | POST | Поиск новых каналов по ключевым словам |

### `/search_channels` — тест:
```bash
curl -s -X POST http://172.17.0.1:5000/search_channels \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["аренда квартир москва"], "limit": 5, "min_subscribers": 100}'
# Возвращает 7 каналов — РАБОТАЕТ ✓
```

---

## Google Sheets

| Таблица | ID | Листы |
|---------|-----|-------|
| Sources/Ниши | `1lCyk_zZTwq0_Nssk8skUHETpelS6zmxg2a0p2-0N_sw` | `sources`, `ниши` |
| Leads | `1alr08qWL2TTVF-1nuDeU4NVXoGgyODgLKeTsa16_kxE` | `Telegram_Leads_Template` |

### Поля таблицы `sources`:
- `channel_url`, `channel_title`, `niche`, `score`, `status`, `added_at`, `username`
- **Статусы**: `approved`, `pending`, `rejected`, `auto_rejected`

---

## Credentials в n8n

| Сервис | Credential Name |
|--------|----------------|
| Telegram | `Telegram ПАРСЕР` (id: kkySYqFIPRx85OPe) |
| Google Sheets | `Google Sheets ТЕЛЕГРАМ ПАРС` (id: 3tw79kiICQ7OPZI8) |
| OpenRouter AI | Bearer token в HTTP Request нодах |

### ⚠️ OpenRouter API ключ (НУЖНО ЗАМЕНИТЬ):
- **Текущий**: `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` — **ИСТЁК**
- **Где заменить**: https://openrouter.ai/keys
- **Ноды где используется**: "Claude профиль ниши", "Claude скоринг каналов" (WF1), "Claude анализ лида" (WF2), "Claude генерирует сообщение" (WF3)
- **Модель**: `google/gemini-2.0-flash-lite`

---

## Webhooks n8n

| Webhook | URL |
|---------|-----|
| WF2 AI Parser trigger | `https://n8n.arendadom24.ru/webhook/ai-parse-trigger` |
| WF3 Smart Lead trigger | `https://n8n.arendadom24.ru/webhook/smart-lead-trigger` |

---

## Исправления сделанные в этой сессии

### WF1 — Бот (WF1_bot_search_channels_FIXED.json)
1. **Баг: текст после "укажи нишу" шёл в неправильный handler**
   - Добавлен Code node `Начать диалог ниши` — устанавливает state `waiting_niche`
   - В `Обработать текст диалога` добавлена обработка `waiting_niche` → routes to add_niche chain
   - Добавлен IF node `Это ниша?` — маршрутизирует на поиск каналов

### WF2 — Парсер (WF2_ai_parser_FIXED.json)
2. **Баг: "Получить ниши hasn't been executed"**
   - Исправлены параллельные соединения на последовательные:
   - `Нормализовать → Получить источники → Получить ниши → Сформировать запрос`

---

## Файлы воркфлоу

| Файл | Описание |
|------|----------|
| `WF1_bot_search_channels_FIXED.json` | Бот + поиск каналов |
| `WF2_ai_parser_FIXED.json` | AI парсер лидов |
| `WF3_smart_lead_FIXED.json` | Smart Lead рассылка |

---

## Команды для управления сервером

```bash
# Статус Python парсера
curl -s http://172.17.0.1:5000/status | python3 -m json.tool

# Перезапуск Python парсера
kill $(pgrep -f telegram_parser_api) && cd /root && python3 telegram_parser_api.py &

# Логи Python в реальном времени
tail -f /proc/$(pgrep -f telegram_parser_api)/fd/1

# Тест поиска каналов
curl -s -X POST http://172.17.0.1:5000/search_channels \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["аренда квартир москва"], "limit": 5, "min_subscribers": 100}' | python3 -m json.tool
```

---

## Правильный сценарий использования

```
1. Бот: /add_niche
2. Бот спрашивает нишу → пишешь: аренда квартир Москва
3. Бот: "Анализирую нишу..." → Claude → Python ищет каналы → сохраняет
4. Бот: "Найдено X каналов, Y одобрено автоматически"

5. /approve_sources → одобряешь pending каналы кнопками

6. /start_parse → вводишь кол-во дней → ключевые слова → парсинг запускается
7. При нахождении горячего лида → уведомление в Telegram

8. /send_leads → Claude генерирует сообщения → отправляет лидам
```

---

## Статус на 2026-03-18

| Компонент | Статус |
|-----------|--------|
| Python `/search_channels` | ✅ Работает |
| Python `/parse` | ✅ Работает |
| n8n WF1 бот | ✅ Исправлен |
| n8n WF2 парсер | ✅ Исправлен |
| n8n WF3 smart lead | ✅ Исправлен |
| OpenRouter API ключ | ❌ Нужно заменить |
| Каналы в sources | ⚠️ 2 из 3 каналов с ошибками username |
