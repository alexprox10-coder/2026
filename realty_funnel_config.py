"""
Конфигурация воронки прогрева для недвижимости
Все тексты сообщений в одном месте для удобного редактирования
"""

# Переменные окружения которые нужно добавить в .env
ENV_VARS = """
# Воронка недвижимости
REALTOR_CHAT_ID=123456789  # Telegram ID риелтора для получения лидов
REALTOR_NAME=Имя           # Имя риелтора для сообщений
REALTOR_PHONE=+7xxx        # Телефон риелтора (опционально)
"""

# ============== ТЕКСТЫ СООБЩЕНИЙ ==============

MESSAGES = {
    # Первое сообщение при получении лида
    "first_contact": """Здравствуйте! 👋

Видел ваше сообщение - вы ищете недвижимость. Могу помочь с подбором!

✅ Работаю напрямую с застройщиками и собственниками
✅ Без комиссии для покупателя
✅ Помогу с ипотекой под низкий %

Подскажите, что именно ищете?""",

    # После выбора типа недвижимости
    "ask_rooms": "Отлично! Сколько комнат вам нужно?",

    # После выбора комнат
    "ask_budget": "Хорошо! Какой у вас бюджет?",

    # После выбора бюджета
    "ask_urgency": "Понял! Насколько срочно нужна квартира?",

    # Предложение связать с риелтором
    "offer_realtor": """Отлично! 🎯

У меня есть несколько подходящих вариантов для вас.

Могу связать вас с риелтором, который:
✅ Покажет объекты лично
✅ Поможет с документами и ипотекой
✅ Без комиссии для вас

Связаться сейчас?""",

    # Подтверждение передачи риелтору
    "confirm_handoff": """Отлично! ✅

Сейчас с вами свяжется наш специалист.

Он подберет лучшие варианты под ваш запрос и ответит на все вопросы.

⏰ Обычно отвечаем в течение 15 минут в рабочее время.""",

    # Если человек сказал "не интересно"
    "not_interested": """Понял, без проблем!

Если в будущем понадобится помощь с недвижимостью — напишите /start

Удачи! 🙌""",

    # Сообщение риелтору о новом лиде
    "realtor_notification": """🔥 ГОРЯЧИЙ ЛИД!

👤 {username}
📞 {phone}

📋 Анкета:
• Тип: {property_type}
• Комнат: {rooms}
• Бюджет: {budget}
• Срочность: {urgency}

💬 Исходное сообщение:
{original_message}

📌 Источник: {source_channel}
⏰ Время: {created_at}""",

    # Лид без username - сразу риелтору
    "lead_no_username": """📥 Новый лид без username

Телефон: {phone}
Канал: {source_channel}

Сообщение:
{original_message}"""
}

# ============== КНОПКИ ==============

BUTTONS = {
    "property_type": [
        {"text": "🏢 Квартира в новостройке", "callback": "type_new"},
        {"text": "🏠 Вторичка", "callback": "type_secondary"},
        {"text": "🏡 Дом/Таунхаус", "callback": "type_house"},
        {"text": "❌ Не интересно", "callback": "not_interested"}
    ],

    "rooms": [
        {"text": "Студия", "callback": "rooms_studio"},
        {"text": "1 комн", "callback": "rooms_1"},
        {"text": "2 комн", "callback": "rooms_2"},
        {"text": "3 комн", "callback": "rooms_3"},
        {"text": "4+ комн", "callback": "rooms_4plus"}
    ],

    "budget": [
        {"text": "До 3 млн", "callback": "budget_3m"},
        {"text": "3-5 млн", "callback": "budget_3_5m"},
        {"text": "5-8 млн", "callback": "budget_5_8m"},
        {"text": "8-15 млн", "callback": "budget_8_15m"},
        {"text": "15+ млн", "callback": "budget_15m_plus"}
    ],

    "urgency": [
        {"text": "🔥 Срочно (до 2 недель)", "callback": "urgency_urgent"},
        {"text": "📅 В течение месяца", "callback": "urgency_month"},
        {"text": "🗓 В течение 3 месяцев", "callback": "urgency_3months"},
        {"text": "🔍 Просто смотрю варианты", "callback": "urgency_looking"}
    ],

    "contact_realtor": [
        {"text": "✅ Да, свяжите меня", "callback": "contact_realtor"},
        {"text": "📸 Сначала покажите варианты", "callback": "show_options"}
    ]
}

# ============== СКОРИНГ ЛИДОВ ==============

SCORING = {
    # Баллы за срочность
    "urgency": {
        "urgent": 30,      # Срочно - самые горячие
        "month": 20,       # В течение месяца
        "3months": 10,     # 3 месяца
        "looking": 5       # Просто смотрит
    },

    # Баллы за бюджет (чем выше бюджет - тем интереснее для риелтора)
    "budget": {
        "3m": 10,
        "3_5m": 15,
        "5_8m": 20,
        "8_15m": 25,
        "15m_plus": 30
    },

    # Баллы за тип (новостройки обычно проще продавать)
    "property_type": {
        "new": 15,
        "secondary": 10,
        "house": 20
    },

    # Порог для "горячего" лида
    "hot_threshold": 50
}

# ============== КАНАЛЫ ДЛЯ ПАРСИНГА ==============

# Примеры каналов где ищут недвижимость (заполни своими)
CHANNELS_TO_PARSE = [
    # Чаты по недвижимости города
    # "@nedvizhimost_msk",
    # "@kvartiry_spb",

    # Районные чаты
    # "@chat_district_name",

    # Чаты новостроек
    # "@jk_name_chat",
]

# ============== ИНСТРУКЦИЯ ПО НАСТРОЙКЕ ==============

SETUP_INSTRUCTIONS = """
## Как настроить воронку недвижимости

### 1. Добавь переменные в .env:
```
REALTOR_CHAT_ID=123456789
```

### 2. Импортируй workflow в n8n:
- Открой n8n
- Settings → Import from File
- Выбери realty_funnel_workflow.json

### 3. Настрой credentials в n8n:
- Telegram Bot API (токен бота)
- Google Sheets (для хранения лидов)

### 4. Создай Google таблицу с колонками:
lead_id | username | phone | user_id | original_message | source_channel |
funnel_stage | created_at | property_type | rooms | budget | urgency |
qualification_score | ready_for_realtor

### 5. Замени в workflow:
- REPLACE_WITH_GOOGLE_SHEET_ID → ID твоей таблицы
- REPLACE_WITH_GOOGLE_CRED_ID → ID credentials Google
- REPLACE_WITH_TELEGRAM_CRED_ID → ID credentials Telegram

### 6. Активируй workflow (toggle справа вверху)

### 7. Запусти парсер с нишей realty_buyers:
POST http://localhost:5000/parse
{
    "channels": ["@channel1", "@channel2"],
    "keywords": [],
    "niche": "realty_buyers",
    "limit": 100
}

Лиды автоматически пойдут в воронку!
"""

if __name__ == "__main__":
    print(SETUP_INSTRUCTIONS)
