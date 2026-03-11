# Сессия: AI Бот-прогрев недвижимости

**Дата:** 2026-03-11

## Задача
Создать бота-прогрева с AI-агентом для квалификации лидов недвижимости.

## Что сделано

### 1. Создан workflow `workflows/realty_ai_bot.json`

Структура:
```
Telegram Trigger → Разбор сообщения → Получить контекст из Sheets
       ↓
Подготовка контекста (история + собранные данные)
       ↓
AI Агент (OpenRouter API) → Обработка ответа
       ↓
Отправить ответ → Сохранить контекст
       ↓
Лид готов? → Записать лида → Уведомить риелтора
```

### 2. Создан конфиг `workflows/realty_ai_bot_config.py`

- Системный промпт для AI
- Структура Google Sheets
- Инструкция по настройке

## Особенности реализации

### Память диалога
- Контекст хранится в Google Sheets (лист conversations)
- История последних 10 сообщений
- JSON с собранными данными

### AI извлекает параметры:
- city — город/район
- propertyType — тип объекта
- rooms — комнаты
- budget — бюджет
- paymentMethod — способ оплаты
- timeline — срок
- contact — контакт

### Завершение воронки
Когда все данные собраны:
1. Лид записывается в qualified_leads
2. Риелтор получает уведомление

## Настройка

### Credentials в n8n:
1. **Telegram Bot API** — токен бота
2. **Google Sheets OAuth2** — доступ к таблицам
3. **HTTP Header Auth** (OpenRouter):
   - Header Name: `Authorization`
   - Header Value: `Bearer sk-or-v1-xxx`

### Переменные окружения:
```
REALTOR_CHAT_ID=123456789
```

### Google Sheets:
- Лист `conversations`: chat_id, user_id, username, first_name, context_json, updated_at, is_complete, is_refused
- Лист `qualified_leads`: lead_id, chat_id, user_id, username, first_name, city, property_type, rooms, budget, payment_method, timeline, contact, created_at, status

## Файлы
- `/home/user/2026/workflows/realty_ai_bot.json` — workflow
- `/home/user/2026/workflows/realty_ai_bot_config.py` — конфиг и инструкция

## Следующие шаги
1. Импортировать workflow в n8n
2. Создать credentials
3. Создать Google таблицу
4. Протестировать бота
