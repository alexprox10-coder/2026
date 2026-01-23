# 🏗️ Структура n8n Workflow: Telegram Bot для парсера недвижимости

## 📊 Обзор workflow

**Название:** 🤖 Telegram Bot - Realtor Parser Control
**ID Workflow:** (генерируется при импорте)
**Главный Workflow ID:** `iXAfySHKjPj3DPcm`
**Количество нод:** 26
**Тип триггера:** Telegram Trigger (Webhook)

---

## 🗺️ Полная диаграмма workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     📱 Telegram Trigger                                 │
│                  (получение message + callback_query)                   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        🔒 Check User ID                                 │
│                (user_id === 7984101063 ?)                               │
└──────────┬──────────────────────────────────────────┬───────────────────┘
           │                                          │
      ✅ TRUE                                    ❌ FALSE
           │                                          │
           ▼                                          ▼
┌──────────────────────┐              ┌───────────────────────────────────┐
│  🔀 Message Router   │              │      ⛔ Unauthorized              │
│   (Switch Node)      │              │   "❌ У вас нет доступа"          │
└──────┬───────────────┘              └───────────────────────────────────┘
       │
       ├─────────────────────┬──────────────────────┬─────────────────────┐
       │                     │                      │                     │
  /start command      callback_query         other_message               │
       │                     │                      │                     │
       ▼                     ▼                      ▼                     │
┌─────────────────┐   ┌──────────────────┐   ┌─────────────────────┐    │
│ 📨 Send Welcome │   │ 🔀 Callback      │   │ ✅ Feedback         │    │
│  + Клавиатура   │   │    Router        │   │    Received         │    │
└─────────────────┘   │  (Switch Node)   │   └──────────┬──────────┘    │
                      └────┬─────────────┘              │               │
                           │                            ▼               │
                           │              ┌──────────────────────────┐  │
                           │              │ 📨 Forward to Admin      │  │
                           │              │  (отправка отзыва)       │  │
                           │              └──────────────────────────┘  │
                           │                                            │
    ┌──────────────────────┼────────────────────────────────────────────┘
    │                      │
    ▼                      ▼
[Обработчики callback_query]

┌─────────────────────────────────────────────────────────────────────────┐
│                      ОБРАБОТЧИКИ КНОПОК                                 │
└─────────────────────────────────────────────────────────────────────────┘

1️⃣ parse_avito:
   🟢 Run Avito Parser → ✅ Avito Success

2️⃣ parse_cian:
   🔵 Run CIAN Parser → ✅ CIAN Success

3️⃣ parse_both:
   🟣 Run Both Parsers → ✅ Both Success

4️⃣ schedule_settings:
   ⏰ Schedule Settings (показ меню интервалов)

5️⃣ enable_schedule:
   ▶️ Enable Schedule → ✅ Schedule Enabled

6️⃣ disable_schedule:
   ⏸️ Disable Schedule → ✅ Schedule Disabled

7️⃣ help:
   ❓ Help Message

8️⃣ feedback:
   💬 Feedback Prompt → 🔧 Set Feedback Mode

9️⃣ set_interval_* (1, 5, 10, 15, 30, 60, 120, 360):
   ⚙️ Calculate Interval → ⚙️ Update Schedule → ✅ Interval Updated
```

---

## 📋 Детальное описание каждой ноды

### 1. 📱 Telegram Trigger

**Тип:** `n8n-nodes-base.telegramTrigger`
**Версия:** 1.2

**Функция:** Получение сообщений и callback запросов от Telegram

**Параметры:**
```json
{
  "updates": ["message", "callback_query"]
}
```

**Credentials:** Telegram API

**Выходные данные:**
```json
{
  "message": {
    "message_id": 123,
    "from": {
      "id": 7984101063,
      "first_name": "User",
      "username": "username"
    },
    "chat": {
      "id": 7984101063,
      "type": "private"
    },
    "text": "/start"
  }
}
```

или для callback:
```json
{
  "callback_query": {
    "id": "abc123",
    "from": {
      "id": 7984101063,
      "first_name": "User"
    },
    "message": {
      "chat": {
        "id": 7984101063
      }
    },
    "data": "parse_avito"
  }
}
```

---

### 2. 🔒 Check User ID

**Тип:** `n8n-nodes-base.if`
**Версия:** 2

**Функция:** Проверка доступа пользователя

**Параметры:**
```json
{
  "conditions": {
    "string": [
      {
        "value1": "={{ $json.message?.from?.id || $json.callback_query?.from?.id }}",
        "value2": "7984101063"
      }
    ]
  }
}
```

**Выходы:**
- **TRUE** → пользователь авторизован → `🔀 Message Router`
- **FALSE** → неавторизованный пользователь → `⛔ Unauthorized`

---

### 3. ⛔ Unauthorized

**Тип:** `n8n-nodes-base.telegram`
**Версия:** 1.2

**Функция:** Отправка сообщения об отказе в доступе

**Параметры:**
```json
{
  "chatId": "={{ $json.message?.chat?.id || $json.callback_query?.message?.chat?.id }}",
  "text": "❌ У вас нет доступа к этому боту."
}
```

---

### 4. 🔀 Message Router

**Тип:** `n8n-nodes-base.switch`
**Версия:** 3

**Функция:** Маршрутизация входящих сообщений по типу

**Параметры:**
```json
{
  "mode": "rules",
  "rules": {
    "values": [
      {
        "conditions": {
          "conditions": [
            {
              "leftValue": "={{ $json.message?.text }}",
              "rightValue": "/start",
              "operator": { "type": "string", "operation": "equals" }
            }
          ]
        },
        "outputKey": "start_command"
      },
      {
        "conditions": {
          "conditions": [
            {
              "leftValue": "={{ $json.callback_query }}",
              "operator": { "type": "object", "operation": "exists" }
            }
          ]
        },
        "outputKey": "callback_query"
      },
      {
        "conditions": {
          "conditions": [
            {
              "leftValue": "={{ $json.message?.text }}",
              "rightValue": "/start",
              "operator": { "type": "string", "operation": "notEquals" }
            }
          ]
        },
        "outputKey": "other_message"
      }
    ]
  }
}
```

**Выходы:**
1. **start_command** → `/start` → `📨 Send Welcome`
2. **callback_query** → нажатие кнопки → `🔀 Callback Router`
3. **other_message** → любое другое сообщение → `✅ Feedback Received` + `📨 Forward to Admin`

---

### 5. 📨 Send Welcome

**Тип:** `n8n-nodes-base.telegram`
**Версия:** 1.2

**Функция:** Отправка приветственного сообщения с клавиатурой

**Параметры:**
```json
{
  "chatId": "={{ $json.message.chat.id }}",
  "text": "Привет! 👋\n\n*Это бот управления парсером недвижимости*...",
  "additionalFields": {
    "parse_mode": "Markdown",
    "replyMarkup": "inlineKeyboard",
    "inlineKeyboard": {
      "rows": [
        {
          "row": {
            "buttons": [
              {
                "text": "🟢 Парсить только Avito",
                "callbackData": "parse_avito"
              }
            ]
          }
        },
        {
          "row": {
            "buttons": [
              {
                "text": "🔵 Парсить только ЦИАН",
                "callbackData": "parse_cian"
              }
            ]
          }
        },
        {
          "row": {
            "buttons": [
              {
                "text": "🟣 Парсить оба источника",
                "callbackData": "parse_both"
              }
            ]
          }
        },
        {
          "row": {
            "buttons": [
              {
                "text": "⏰ Настроить авто-парсинг",
                "callbackData": "schedule_settings"
              }
            ]
          }
        },
        {
          "row": {
            "buttons": [
              {
                "text": "▶️ Включить авто-парсинг",
                "callbackData": "enable_schedule"
              },
              {
                "text": "⏸️ Выключить авто-парсинг",
                "callbackData": "disable_schedule"
              }
            ]
          }
        },
        {
          "row": {
            "buttons": [
              {
                "text": "❓ Помощь",
                "callbackData": "help"
              },
              {
                "text": "💬 Оставить отзыв",
                "callbackData": "feedback"
              }
            ]
          }
        }
      ]
    }
  }
}
```

---

### 6. 🔀 Callback Router

**Тип:** `n8n-nodes-base.switch`
**Версия:** 3

**Функция:** Маршрутизация callback_query по data

**Параметры:**
```json
{
  "mode": "rules",
  "rules": {
    "values": [
      { "leftValue": "={{ $json.callback_query.data }}", "rightValue": "parse_avito", "outputKey": "parse_avito" },
      { "leftValue": "={{ $json.callback_query.data }}", "rightValue": "parse_cian", "outputKey": "parse_cian" },
      { "leftValue": "={{ $json.callback_query.data }}", "rightValue": "parse_both", "outputKey": "parse_both" },
      { "leftValue": "={{ $json.callback_query.data }}", "rightValue": "schedule_settings", "outputKey": "schedule_settings" },
      { "leftValue": "={{ $json.callback_query.data }}", "rightValue": "enable_schedule", "outputKey": "enable_schedule" },
      { "leftValue": "={{ $json.callback_query.data }}", "rightValue": "disable_schedule", "outputKey": "disable_schedule" },
      { "leftValue": "={{ $json.callback_query.data }}", "rightValue": "help", "outputKey": "help" },
      { "leftValue": "={{ $json.callback_query.data }}", "rightValue": "feedback", "outputKey": "feedback" },
      { "leftValue": "={{ $json.callback_query.data }}", "rightValue": "", "operator": "startsWith", "outputKey": "set_interval_" }
    ]
  }
}
```

**Выходы:** 9 различных веток для каждого типа кнопки

---

### 7-9. Парсинг: 🟢 Run Avito / 🔵 Run CIAN / 🟣 Run Both Parsers

**Тип:** `n8n-nodes-base.httpRequest`
**Версия:** 4.2

**Функция:** Запуск главного workflow парсера через n8n API

**Параметры (для Avito):**
```json
{
  "method": "POST",
  "url": "={{ $env.N8N_HOST }}/api/v1/workflows/iXAfySHKjPj3DPcm/run",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "n8nApi",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      {
        "name": "source",
        "value": "avito"  // или "cian", или "both"
      }
    ]
  }
}
```

**Credentials:** n8n API

**Ответ API:**
```json
{
  "data": {
    "executionId": "abc123..."
  }
}
```

---

### 10-12. Success Messages: ✅ Avito / CIAN / Both Success

**Тип:** `n8n-nodes-base.telegram`
**Версия:** 1.2

**Функция:** Подтверждение запуска парсинга

**Параметры (для Avito):**
```json
{
  "chatId": "={{ $json.callback_query.message.chat.id }}",
  "text": "✅ *Запущен парсинг Авито!*\n\nБот начал собирать объявления с Авито. Результаты будут отправлены в течение нескольких минут.",
  "additionalFields": {
    "parse_mode": "Markdown"
  }
}
```

---

### 13-14. Schedule Management: ▶️ Enable / ⏸️ Disable Schedule

**Тип:** `n8n-nodes-base.httpRequest`
**Версия:** 4.2

**Функция:** Активация/деактивация главного workflow

**Параметры (Enable):**
```json
{
  "method": "PATCH",
  "url": "={{ $env.N8N_HOST }}/api/v1/workflows/iXAfySHKjPj3DPcm",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "n8nApi",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={\n  \"active\": true\n}"  // или false для Disable
}
```

---

### 15-16. Schedule Confirmations: ✅ Schedule Enabled / Disabled

**Тип:** `n8n-nodes-base.telegram`
**Версия:** 1.2

**Функция:** Подтверждение включения/выключения авто-парсинга

**Параметры (Enabled):**
```json
{
  "chatId": "={{ $json.callback_query.message.chat.id }}",
  "text": "▶️ *Авто-парсинг включен!*\n\nБот будет автоматически парсить объявления каждые 30 минут.",
  "additionalFields": {
    "parse_mode": "Markdown"
  }
}
```

---

### 17. ❓ Help Message

**Тип:** `n8n-nodes-base.telegram`
**Версия:** 1.2

**Функция:** Справочное сообщение

**Параметры:**
```json
{
  "chatId": "={{ $json.callback_query.message.chat.id }}",
  "text": "❓ *Справка по боту парсера недвижимости*\n\n*Основные функции:*\n\n🟢 *Парсить только Avito*...",
  "additionalFields": {
    "parse_mode": "Markdown"
  }
}
```

---

### 18. 💬 Feedback Prompt

**Тип:** `n8n-nodes-base.telegram`
**Версия:** 1.2

**Функция:** Запрос на отправку отзыва

**Параметры:**
```json
{
  "chatId": "="{{ $json.callback_query.message.chat.id }}",
  "text": "💬 *Оставить отзыв*\n\nНапишите ваш отзыв или предложение следующим сообщением...",
  "additionalFields": {
    "parse_mode": "Markdown"
  }
}
```

---

### 19. ⏰ Schedule Settings

**Тип:** `n8n-nodes-base.telegram`
**Версия:** 1.2

**Функция:** Меню выбора интервала

**Параметры:**
```json
{
  "chatId": "={{ $json.callback_query.message.chat.id }}",
  "text": "⏰ *Настройка интервала авто-парсинга*\n\nВыберите интервал для автоматического парсинга:",
  "additionalFields": {
    "parse_mode": "Markdown",
    "replyMarkup": "inlineKeyboard",
    "inlineKeyboard": {
      "rows": [
        {
          "row": {
            "buttons": [
              { "text": "1 минута", "callbackData": "set_interval_1" },
              { "text": "5 минут", "callbackData": "set_interval_5" }
            ]
          }
        },
        {
          "row": {
            "buttons": [
              { "text": "10 минут", "callbackData": "set_interval_10" },
              { "text": "15 минут", "callbackData": "set_interval_15" }
            ]
          }
        },
        {
          "row": {
            "buttons": [
              { "text": "30 минут", "callbackData": "set_interval_30" },
              { "text": "1 час", "callbackData": "set_interval_60" }
            ]
          }
        },
        {
          "row": {
            "buttons": [
              { "text": "2 часа", "callbackData": "set_interval_120" },
              { "text": "6 часов", "callbackData": "set_interval_360" }
            ]
          }
        },
        {
          "row": {
            "buttons": [
              { "text": "« Назад", "callbackData": "back_to_menu" }
            ]
          }
        }
      ]
    }
  }
}
```

---

### 20. ⚙️ Calculate Interval

**Тип:** `n8n-nodes-base.code`
**Версия:** 2

**Функция:** Преобразование выбранного интервала в cron-выражение

**JavaScript код:**
```javascript
// Получаем callback data
const callbackData = $input.item.json.callback_query.data;

// Извлекаем интервал из callback_data (например: "set_interval_30" -> 30)
const interval = callbackData.replace('set_interval_', '');

// Переводим в cron формат (для n8n)
let cronExpression;
if (interval <= 60) {
  // Минуты
  cronExpression = `*/${interval} * * * *`;
} else {
  // Часы
  const hours = interval / 60;
  cronExpression = `0 */${hours} * * *`;
}

return {
  json: {
    interval: parseInt(interval),
    cronExpression: cronExpression,
    chat_id: $input.item.json.callback_query.message.chat.id
  }
};
```

**Выходные данные:**
```json
{
  "interval": 30,
  "cronExpression": "*/30 * * * *",
  "chat_id": 7984101063
}
```

---

### 21. ⚙️ Update Schedule

**Тип:** `n8n-nodes-base.httpRequest`
**Версия:** 4.2

**Функция:** Обновление расписания в главном workflow

**Параметры:**
```json
{
  "method": "PATCH",
  "url": "={{ $env.N8N_HOST }}/api/v1/workflows/iXAfySHKjPj3DPcm",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "n8nApi",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={\n  \"nodes\": [\n    {\n      \"parameters\": {\n        \"rule\": {\n          \"interval\": [\n            {\n              \"field\": \"cronExpression\",\n              \"expression\": \"{{ $json.cronExpression }}\"\n            }\n          ]\n        }\n      },\n      \"name\": \"Schedule Trigger\",\n      \"type\": \"n8n-nodes-base.scheduleTrigger\"\n    }\n  ]\n}"
}
```

---

### 22. ✅ Interval Updated

**Тип:** `n8n-nodes-base.telegram`
**Версия:** 1.2

**Функция:** Подтверждение изменения интервала

**Параметры:**
```json
{
  "chatId": "={{ $json.chat_id }}",
  "text": "=✅ *Интервал изменён!*\n\nАвто-парсинг будет выполняться каждые {{ $('⚙️ Calculate Interval').item.json.interval }} {{ ... }}.",
  "additionalFields": {
    "parse_mode": "Markdown"
  }
}
```

---

### 23. ✅ Feedback Received

**Тип:** `n8n-nodes-base.telegram`
**Версия:** 1.2

**Функция:** Подтверждение получения отзыва

**Параметры:**
```json
{
  "chatId": "={{ $json.message.chat.id }}",
  "text": "📝 *Спасибо за ваше сообщение!*\n\nВаш отзыв был передан администратору.",
  "additionalFields": {
    "parse_mode": "Markdown"
  }
}
```

---

### 24. 📨 Forward to Admin

**Тип:** `n8n-nodes-base.telegram`
**Версия:** 1.2

**Функция:** Пересылка отзыва администратору

**Параметры:**
```json
{
  "chatId": "YOUR_ADMIN_CHAT_ID",
  "text": "=💬 *Новый отзыв от пользователя*\n\n*От:* {{ $json.message.from.first_name }} {{ $json.message.from.last_name || '' }} (@{{ $json.message.from.username || 'нет username' }})\n*ID:* {{ $json.message.from.id }}\n\n*Сообщение:*\n{{ $json.message.text }}",
  "additionalFields": {
    "parse_mode": "Markdown"
  }
}
```

---

### 25. 🔧 Set Feedback Mode

**Тип:** `n8n-nodes-base.set`
**Версия:** 3.4

**Функция:** Установка режима приёма отзывов

**Параметры:**
```json
{
  "assignments": {
    "assignments": [
      {
        "id": "feedback_mode",
        "name": "feedback_mode",
        "value": "true",
        "type": "boolean"
      }
    ]
  }
}
```

---

### 26. 🔙 Check Back

**Тип:** `n8n-nodes-base.if`
**Версия:** 2

**Функция:** Проверка кнопки "Назад"

**Параметры:**
```json
{
  "conditions": {
    "string": [
      {
        "value1": "={{ $json.callback_query.data }}",
        "value2": "back_to_menu"
      }
    ]
  }
}
```

---

## 🔄 Потоки данных (Connections)

### Основной поток:

```
📱 Telegram Trigger
  → 🔒 Check User ID [TRUE]
    → 🔀 Message Router
```

### Ветка /start:

```
🔀 Message Router [start_command]
  → 📨 Send Welcome
```

### Ветка callback_query:

```
🔀 Message Router [callback_query]
  → 🔀 Callback Router
    ├─ [parse_avito] → 🟢 Run Avito Parser → ✅ Avito Success
    ├─ [parse_cian] → 🔵 Run CIAN Parser → ✅ CIAN Success
    ├─ [parse_both] → 🟣 Run Both Parsers → ✅ Both Success
    ├─ [schedule_settings] → ⏰ Schedule Settings
    ├─ [enable_schedule] → ▶️ Enable Schedule → ✅ Schedule Enabled
    ├─ [disable_schedule] → ⏸️ Disable Schedule → ✅ Schedule Disabled
    ├─ [help] → ❓ Help Message
    ├─ [feedback] → 💬 Feedback Prompt → 🔧 Set Feedback Mode
    └─ [set_interval_*] → ⚙️ Calculate Interval → ⚙️ Update Schedule → ✅ Interval Updated
```

### Ветка other_message (отзывы):

```
🔀 Message Router [other_message]
  ├─ → ✅ Feedback Received
  └─ → 📨 Forward to Admin
```

### Ветка неавторизованного доступа:

```
🔒 Check User ID [FALSE]
  → ⛔ Unauthorized
```

---

## 🎯 Callback Data справочник

| Callback Data | Обработчик | Действие |
|---------------|------------|----------|
| `parse_avito` | 🟢 Run Avito Parser | POST /workflows/{id}/run {"source":"avito"} |
| `parse_cian` | 🔵 Run CIAN Parser | POST /workflows/{id}/run {"source":"cian"} |
| `parse_both` | 🟣 Run Both Parsers | POST /workflows/{id}/run {"source":"both"} |
| `schedule_settings` | ⏰ Schedule Settings | Показать меню интервалов |
| `enable_schedule` | ▶️ Enable Schedule | PATCH /workflows/{id} {"active":true} |
| `disable_schedule` | ⏸️ Disable Schedule | PATCH /workflows/{id} {"active":false} |
| `help` | ❓ Help Message | Показать справку |
| `feedback` | 💬 Feedback Prompt | Включить режим отзывов |
| `set_interval_1` | ⚙️ Calculate Interval | Установить 1 минуту |
| `set_interval_5` | ⚙️ Calculate Interval | Установить 5 минут |
| `set_interval_10` | ⚙️ Calculate Interval | Установить 10 минут |
| `set_interval_15` | ⚙️ Calculate Interval | Установить 15 минут |
| `set_interval_30` | ⚙️ Calculate Interval | Установить 30 минут |
| `set_interval_60` | ⚙️ Calculate Interval | Установить 1 час |
| `set_interval_120` | ⚙️ Calculate Interval | Установить 2 часа |
| `set_interval_360` | ⚙️ Calculate Interval | Установить 6 часов |
| `back_to_menu` | 🔙 Check Back | Вернуться в меню |

---

## 🔐 Безопасность

### 1. Проверка доступа

- **Нода:** 🔒 Check User ID
- **Метод:** Сравнение `user_id` с белым списком
- **Белый список:** `7984101063`

### 2. API аутентификация

- **Тип:** n8n API Credentials
- **Метод:** Bearer Token или Basic Auth
- **Переменная:** `N8N_API_KEY`

### 3. HTTPS для API запросов

- **Production:** Обязательно HTTPS
- **Development:** Допустимо HTTP (localhost)

---

## 📈 Мониторинг и отладка

### Логирование в n8n

Все выполнения workflow сохраняются в **Executions** с полными данными:

1. Входящий payload от Telegram
2. Результат каждой ноды
3. Ошибки и исключения
4. Время выполнения

### Важные метрики

- **Время ответа бота:** < 2 секунды
- **Успешность запросов к n8n API:** > 95%
- **Процент неавторизованных попыток:** метрика безопасности

---

## 🚀 Оптимизация

### 1. Кэширование

- **n8n API responses:** Встроенный кэш n8n
- **Telegram messages:** Нет необходимости (webhook)

### 2. Параллельное выполнение

- Отзывы отправляются параллельно (пользователю + админу)
- Независимые HTTP Request можно выполнять параллельно

### 3. Обработка ошибок

Рекомендуется добавить Error Workflow для:
- Логирования критических ошибок
- Уведомления администратора при сбоях
- Автоматической перезагрузки при timeout

---

## 📝 Примечания

1. **ID нод** в JSON файле уникальны и генерируются автоматически
2. **Позиции нод** (координаты) можно изменить в визуальном редакторе n8n
3. **Credentials ID** нужно заменить на свои после импорта
4. **Webhook URL** генерируется автоматически при активации Telegram Trigger

---

**Версия:** 1.0.0
**Дата:** 23 января 2026
**Автор:** Claude AI
