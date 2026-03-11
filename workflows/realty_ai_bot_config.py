"""
Конфигурация AI бота-прогрева для недвижимости
"""

# ============== СИСТЕМНЫЙ ПРОМПТ ==============

SYSTEM_PROMPT = """Ты — ассистент по подбору недвижимости в Москве и Московской области.

Цель: вежливо квалифицировать покупателя и собрать данные для передачи риелтору.

ПРАВИЛА:
1. Веди диалог короткими сообщениями, по одному вопросу за раз
2. Будь дружелюбным, но профессиональным
3. Не обсуждай юридические детали, цены и налоги — скажи, что этим занимается риелтор

Тебя интересуют (собирай по порядку):
1. Город/район (Москва, Мытищи, Балашиха, Химки, Реутов, Королёв, Люберцы и др.)
2. Тип объекта (квартира, комната, студия, дом, таунхаус, участок)
3. Количество комнат (для квартир)
4. Бюджет (общая сумма или диапазон)
5. Способ покупки (ипотека, наличные, смешанный)
6. Срок покупки (срочно до месяца, 1-3 месяца, позже)

Когда ВСЕ данные собраны — сделай резюме и предложи связаться с риелтором.

Если человек отказывается — поблагодари, мягко предложи бесплатную подборку 2-3 вариантов.
При повторном отказе — вежливо завершай.

ОТВЕЧАЙ В ФОРМАТЕ JSON:
{
  "response": "твой ответ клиенту",
  "extracted": {
    "city": "город если упомянут или null",
    "propertyType": "тип объекта или null",
    "rooms": "кол-во комнат или null",
    "budget": "бюджет или null",
    "paymentMethod": "способ оплаты или null",
    "timeline": "срок или null",
    "contact": "контакт если дал или null"
  },
  "isComplete": true/false,
  "isRefused": true/false
}"""

# ============== ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ ==============

GREETING = """Здравствуйте! 👋

Я помогаю с подбором недвижимости в Москве и Московской области.

Расскажите, пожалуйста, в каком городе или районе вы ищете жильё?"""

# ============== СТРУКТУРА GOOGLE SHEETS ==============

SHEETS_STRUCTURE = {
    "conversations": {
        "description": "История диалогов с пользователями",
        "columns": [
            "chat_id",           # ID чата Telegram
            "user_id",           # ID пользователя
            "username",          # @username
            "first_name",        # Имя
            "context_json",      # JSON с историей и собранными данными
            "updated_at",        # Время последнего обновления
            "is_complete",       # Воронка завершена
            "is_refused"         # Отказался
        ]
    },
    "qualified_leads": {
        "description": "Квалифицированные лиды",
        "columns": [
            "lead_id",           # Уникальный ID лида
            "chat_id",           # ID чата
            "user_id",           # ID пользователя
            "username",          # @username
            "first_name",        # Имя
            "city",              # Город/район
            "property_type",     # Тип объекта
            "rooms",             # Комнаты
            "budget",            # Бюджет
            "payment_method",    # Способ оплаты
            "timeline",          # Срок
            "contact",           # Контакт для связи
            "created_at",        # Время создания
            "status"             # Статус (new, contacted, closed)
        ]
    }
}

# ============== ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ==============

ENV_VARS = """
# AI Бот-прогрев
OPENROUTER_API_KEY=sk-or-v1-xxx     # API ключ OpenRouter
REALTOR_CHAT_ID=123456789           # Telegram ID риелтора
"""

# ============== ИНСТРУКЦИЯ ПО НАСТРОЙКЕ ==============

SETUP_GUIDE = """
## Настройка AI бота-прогрева недвижимости

### 1. Создай бота в Telegram
- Напиши @BotFather → /newbot
- Сохрани токен

### 2. Получи API ключ OpenRouter
- Зарегистрируйся на https://openrouter.ai
- Создай API key
- Пополни баланс (от $5)

### 3. Создай Google таблицу с листами:
- conversations (колонки: chat_id, user_id, username, first_name, context_json, updated_at, is_complete, is_refused)
- qualified_leads (колонки: lead_id, chat_id, user_id, username, first_name, city, property_type, rooms, budget, payment_method, timeline, contact, created_at, status)

### 4. Импортируй workflow в n8n:
- Settings → Import from File
- Выбери realty_ai_bot.json

### 5. Создай credentials в n8n:
- Telegram Bot API (токен бота)
- Google Sheets OAuth2
- HTTP Header Auth (для OpenRouter):
  - Header Name: Authorization
  - Header Value: Bearer sk-or-v1-xxx

### 6. Замени placeholder'ы в workflow:
- YOUR_TG_CRED_ID → ID Telegram credentials
- YOUR_SHEETS_CRED_ID → ID Google Sheets credentials
- YOUR_OPENROUTER_CRED_ID → ID HTTP Header Auth credentials
- YOUR_SHEET_ID → ID Google таблицы

### 7. Добавь переменные окружения в n8n:
- REALTOR_CHAT_ID=твой_telegram_id

### 8. Активируй workflow

### 9. Протестируй — напиши боту /start

## Архитектура

```
Telegram → Разбор → Контекст из Sheets → AI Agent → Ответ → Сохранение
                                                      ↓
                                              Лид готов? → Запись + Уведомление
```

## Модели OpenRouter (по цене)

| Модель | Цена за 1M токенов | Качество |
|--------|-------------------|----------|
| openai/gpt-4o-mini | $0.15/$0.60 | Отлично |
| anthropic/claude-3-haiku | $0.25/$1.25 | Отлично |
| google/gemini-flash-1.5 | $0.075/$0.30 | Хорошо |

Рекомендую gpt-4o-mini — оптимальное соотношение цена/качество.
"""

if __name__ == "__main__":
    print(SETUP_GUIDE)
