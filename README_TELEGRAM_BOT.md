# 🤖 Telegram Bot для управления парсером недвижимости

Полноценный Telegram-бот для управления парсером Авито и ЦИАН, работающий внутри n8n без внешних серверов.

## 📋 Оглавление

- [Возможности бота](#-возможности-бота)
- [Структура workflow](#-структура-workflow)
- [Установка и настройка](#-установка-и-настройка)
- [Переменные окружения](#-переменные-окружения)
- [Использование бота](#-использование-бота)
- [Технические детали](#-технические-детали)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Возможности бота

### Основные команды:

- `/start` - Главное меню с inline-клавиатурой

### Функции управления парсингом:

✅ **Ручной запуск парсинга:**
- 🟢 Парсить только Avito
- 🔵 Парсить только ЦИАН
- 🟣 Парсить оба источника

✅ **Автоматический режим:**
- ⏰ Настроить интервал авто-парсинга (1 мин - 6 часов)
- ▶️ Включить авто-парсинг
- ⏸️ Выключить авто-парсинг

✅ **Дополнительно:**
- ❓ Помощь - подробная справка
- 💬 Оставить отзыв - отправка отзыва администратору

---

## 🏗️ Структура workflow

### 26 нод в workflow:

```
📱 Telegram Trigger (получение сообщений и callback_query)
    ↓
🔒 Check User ID (проверка доступа: user_id === 7984101063)
    ↓
🔀 Message Router (Switch: /start, callback_query, other_message)
    ↓
    ├─→ 📨 Send Welcome (приветственное сообщение + клавиатура)
    │
    ├─→ 🔀 Callback Router (обработка нажатий кнопок)
    │   ├─→ 🟢 Run Avito Parser → ✅ Avito Success
    │   ├─→ 🔵 Run CIAN Parser → ✅ CIAN Success
    │   ├─→ 🟣 Run Both Parsers → ✅ Both Success
    │   ├─→ ⏰ Schedule Settings (выбор интервала)
    │   ├─→ ▶️ Enable Schedule → ✅ Schedule Enabled
    │   ├─→ ⏸️ Disable Schedule → ✅ Schedule Disabled
    │   ├─→ ❓ Help Message
    │   ├─→ 💬 Feedback Prompt → 🔧 Set Feedback Mode
    │   └─→ ⚙️ Calculate Interval → ⚙️ Update Schedule → ✅ Interval Updated
    │
    └─→ ✅ Feedback Received + 📨 Forward to Admin
```

### Callback Data коды кнопок:

| Кнопка | callback_data | Действие |
|--------|---------------|----------|
| Парсить только Avito | `parse_avito` | POST /workflows/{id}/run с {"source": "avito"} |
| Парсить только ЦИАН | `parse_cian` | POST /workflows/{id}/run с {"source": "cian"} |
| Парсить оба источника | `parse_both` | POST /workflows/{id}/run с {"source": "both"} |
| Настроить авто-парсинг | `schedule_settings` | Показать меню выбора интервала |
| Включить авто-парсинг | `enable_schedule` | PATCH /workflows/{id} → {"active": true} |
| Выключить авто-парсинг | `disable_schedule` | PATCH /workflows/{id} → {"active": false} |
| Помощь | `help` | Показать справочное сообщение |
| Оставить отзыв | `feedback` | Включить режим приёма отзывов |
| 1 минута | `set_interval_1` | Установить интервал 1 мин |
| 5 минут | `set_interval_5` | Установить интервал 5 мин |
| 10 минут | `set_interval_10` | Установить интервал 10 мин |
| 15 минут | `set_interval_15` | Установить интервал 15 мин |
| 30 минут | `set_interval_30` | Установить интервал 30 мин |
| 1 час | `set_interval_60` | Установить интервал 1 час |
| 2 часа | `set_interval_120` | Установить интервал 2 часа |
| 6 часов | `set_interval_360` | Установить интервал 6 часов |
| Назад | `back_to_menu` | Вернуться в главное меню |

---

## 🚀 Установка и настройка

### Шаг 1: Создание Telegram бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Введите имя бота (например: "Realtor Parser Bot")
4. Введите username бота (например: "realtor_parser_bot")
5. Получите **токен бота** (формат: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
6. Сохраните токен в безопасном месте

### Шаг 2: Создание учетных данных в n8n

#### 2.1 Telegram API Credentials

1. В n8n откройте **Settings → Credentials**
2. Нажмите **New Credential**
3. Выберите **Telegram API**
4. Введите:
   - **Name:** `Telegram Bot API`
   - **Access Token:** [ваш токен от BotFather]
5. Нажмите **Save**
6. Скопируйте **Credential ID** (понадобится для замены в JSON)

#### 2.2 n8n API Credentials

1. В n8n откройте **Settings → Credentials**
2. Нажмите **New Credential**
3. Выберите **n8n API**
4. Введите:
   - **Name:** `n8n API`
   - **API Key:** [создайте в Settings → API]
   - **Base URL:** `https://your-n8n-instance.com` (или `http://localhost:5678` для локальной установки)
5. Нажмите **Save**
6. Скопируйте **Credential ID**

### Шаг 3: Настройка переменных окружения

1. В n8n откройте **Settings → Environment Variables**
2. Добавьте переменную:
   - **Name:** `N8N_HOST`
   - **Value:** `https://your-n8n-instance.com` (или `http://localhost:5678`)

### Шаг 4: Импорт workflow

1. В n8n нажмите **Import from File**
2. Выберите файл `telegram_realtor_bot.json`
3. После импорта откройте workflow

### Шаг 5: Замена Credential IDs

Найдите и замените следующие значения во всех нодах:

- `YOUR_TELEGRAM_CREDENTIALS_ID` → ID ваших Telegram API Credentials
- `YOUR_N8N_API_CREDENTIALS_ID` → ID ваших n8n API Credentials
- `YOUR_ADMIN_CHAT_ID` → Ваш Telegram Chat ID (для получения отзывов)

**Как узнать свой Chat ID:**
1. Откройте [@userinfobot](https://t.me/userinfobot) в Telegram
2. Отправьте `/start`
3. Бот покажет ваш ID (например: `7984101063`)

**Ноды, где нужна замена:**

1. **📱 Telegram Trigger** → `credentials.telegramApi.id`
2. **⛔ Unauthorized** → `credentials.telegramApi.id`
3. **📨 Send Welcome** → `credentials.telegramApi.id`
4. **🟢 Run Avito Parser** → `credentials.n8nApi.id`
5. **🔵 Run CIAN Parser** → `credentials.n8nApi.id`
6. **🟣 Run Both Parsers** → `credentials.n8nApi.id`
7. **▶️ Enable Schedule** → `credentials.n8nApi.id`
8. **⏸️ Disable Schedule** → `credentials.n8nApi.id`
9. **✅ Avito Success** → `credentials.telegramApi.id`
10. **✅ CIAN Success** → `credentials.telegramApi.id`
11. **✅ Both Success** → `credentials.telegramApi.id`
12. **✅ Schedule Enabled** → `credentials.telegramApi.id`
13. **✅ Schedule Disabled** → `credentials.telegramApi.id`
14. **❓ Help Message** → `credentials.telegramApi.id`
15. **💬 Feedback Prompt** → `credentials.telegramApi.id`
16. **⏰ Schedule Settings** → `credentials.telegramApi.id`
17. **⚙️ Update Schedule** → `credentials.n8nApi.id`
18. **✅ Interval Updated** → `credentials.telegramApi.id`
19. **✅ Feedback Received** → `credentials.telegramApi.id`
20. **📨 Forward to Admin** → `credentials.telegramApi.id` + замените `chatId: "YOUR_ADMIN_CHAT_ID"` на ваш Chat ID

### Шаг 6: Активация workflow

1. Сохраните workflow (Ctrl+S / Cmd+S)
2. Нажмите **Active** в правом верхнем углу
3. Убедитесь, что появилась надпись "Workflow is active"

### Шаг 7: Тестирование

1. Откройте вашего бота в Telegram
2. Отправьте команду `/start`
3. Должно появиться приветственное сообщение с кнопками
4. Попробуйте нажать на кнопки для проверки работы

---

## 🔧 Переменные окружения

### Обязательные переменные в n8n:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `N8N_HOST` | URL вашего n8n инстанса | `https://n8n.example.com` |

### Как добавить переменные:

1. **n8n Cloud:**
   - Settings → Environment Variables → Add Variable

2. **Self-hosted (Docker):**
   ```bash
   docker run -d \
     -e N8N_HOST=https://your-n8n-instance.com \
     -e N8N_API_KEY=your_api_key \
     n8nio/n8n
   ```

3. **Self-hosted (.env файл):**
   ```env
   N8N_HOST=https://your-n8n-instance.com
   N8N_API_KEY=your_api_key
   ```

---

## 📱 Использование бота

### Команды пользователя:

#### 1. Запуск бота
```
/start
```
Показывает главное меню с кнопками управления.

#### 2. Запуск парсинга вручную

- **Парсить только Avito** - запускает сбор объявлений только с Авито
- **Парсить только ЦИАН** - запускает сбор объявлений только с ЦИАН
- **Парсить оба источника** - запускает парсинг обоих сайтов одновременно

После запуска придёт подтверждающее сообщение:
```
✅ Запущен парсинг Авито!

Бот начал собирать объявления с Авито.
Результаты будут отправлены в течение нескольких минут.
```

#### 3. Настройка автоматического парсинга

1. Нажмите **⏰ Настроить авто-парсинг**
2. Выберите интервал:
   - 1 минута (для тестирования)
   - 5 минут
   - 10 минут
   - 15 минут
   - 30 минут
   - 1 час
   - 2 часа
   - 6 часов

3. Бот подтвердит:
```
✅ Интервал изменён!

Авто-парсинг будет выполняться каждые 30 минут.
```

#### 4. Включение/Выключение авто-парсинга

- **▶️ Включить авто-парсинг** - активирует автоматический режим
- **⏸️ Выключить авто-парсинг** - останавливает автоматический режим

#### 5. Помощь

Нажмите **❓ Помощь** для получения полной справки по боту.

#### 6. Отправка отзыва

1. Нажмите **💬 Оставить отзыв**
2. Напишите ваш отзыв следующим сообщением
3. Отзыв будет отправлен администратору

---

## 🔍 Технические детали

### Архитектура бота

Бот работает на основе **n8n workflow** и использует следующие компоненты:

#### 1. Telegram Trigger
- **Тип:** `n8n-nodes-base.telegramTrigger`
- **Updates:** message, callback_query
- **Webhook:** автоматически регистрируется в Telegram API

#### 2. Авторизация
- **Проверка User ID:** `7984101063`
- **Метод:** IF ноды с проверкой `$json.message.from.id`
- **Защита:** Все неавторизованные пользователи получают сообщение "❌ У вас нет доступа"

#### 3. Роутинг сообщений
- **Switch нод** разделяет потоки на:
  - `/start` команда → Приветствие
  - `callback_query` → Обработка кнопок
  - Обычные сообщения → Отзывы

#### 4. HTTP Request к n8n API

**Запуск workflow:**
```http
POST /api/v1/workflows/iXAfySHKjPj3DPcm/run
Content-Type: application/json

{
  "source": "avito" | "cian" | "both"
}
```

**Активация/Деактивация workflow:**
```http
PATCH /api/v1/workflows/iXAfySHKjPj3DPcm
Content-Type: application/json

{
  "active": true | false
}
```

**Изменение расписания:**
```http
PATCH /api/v1/workflows/iXAfySHKjPj3DPcm
Content-Type: application/json

{
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "*/30 * * * *"
            }
          ]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger"
    }
  ]
}
```

#### 5. Inline Keyboard

Формат inline-клавиатуры:
```json
{
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
      }
    ]
  }
}
```

### Обработка ошибок

Все HTTP Request ноды имеют встроенную обработку ошибок:
- При ошибке запроса пользователь получит сообщение: "❌ Ошибка: не удалось выполнить операцию"
- Все ошибки логируются в n8n Execution Log

### Безопасность

1. **Проверка User ID** - доступ только для владельца (ID: 7984101063)
2. **n8n API Authentication** - использование Bearer Token или Basic Auth
3. **HTTPS** - все запросы к n8n API через HTTPS (для production)

---

## 🛠️ Troubleshooting

### Бот не отвечает на команды

**Причина:** Workflow не активирован или Telegram Trigger не настроен

**Решение:**
1. Проверьте, что workflow активен (зелёный индикатор)
2. Проверьте Telegram Trigger credentials
3. Проверьте webhook в BotFather: `/setwebhook`

### Ошибка "Unauthorized" при запросах к n8n API

**Причина:** Неверный API токен или URL

**Решение:**
1. Проверьте переменную окружения `N8N_HOST`
2. Проверьте n8n API credentials
3. Убедитесь, что API Key имеет права на запуск workflow

### Кнопки не работают (callback_query не обрабатывается)

**Причина:** Telegram Trigger не настроен на получение callback_query

**Решение:**
1. В ноде **📱 Telegram Trigger** проверьте параметр `updates`
2. Должны быть включены: `message` и `callback_query`

### Парсинг не запускается при нажатии кнопки

**Причина:** Неверный ID главного workflow или ошибка в HTTP Request

**Решение:**
1. Проверьте ID workflow в URL: `/api/v1/workflows/iXAfySHKjPj3DPcm/run`
2. Убедитесь, что главный workflow существует и активен
3. Проверьте логи в n8n Executions

### Отзывы не приходят администратору

**Причина:** Неверный Chat ID администратора

**Решение:**
1. В ноде **📨 Forward to Admin** проверьте `chatId: "YOUR_ADMIN_CHAT_ID"`
2. Замените на правильный Chat ID (узнать через @userinfobot)

### Ошибка при изменении интервала

**Причина:** Неправильный формат PATCH запроса или нода Schedule Trigger имеет другое имя

**Решение:**
1. Убедитесь, что в главном workflow есть нода с именем "Schedule Trigger"
2. Проверьте JSON формат в ноде **⚙️ Update Schedule**

---

## 📊 Мониторинг и логи

### Просмотр выполнений:

1. В n8n откройте **Executions**
2. Фильтруйте по workflow: "🤖 Telegram Bot - Realtor Parser Control"
3. Нажмите на выполнение для просмотра деталей

### Типичные логи:

**Успешный запуск парсинга:**
```json
{
  "node": "🟢 Run Avito Parser",
  "status": "success",
  "response": {
    "executionId": "abc123..."
  }
}
```

**Ошибка авторизации:**
```json
{
  "node": "🔒 Check User ID",
  "output": "false",
  "message": "User 12345678 is not authorized"
}
```

---

## 📞 Поддержка

Если у вас возникли вопросы:

1. Проверьте раздел [Troubleshooting](#-troubleshooting)
2. Посмотрите логи в n8n Executions
3. Свяжитесь с разработчиком: @your_username

---

## 📄 Лицензия

MIT License

---

## 🔄 Changelog

### v1.0.0 (2026-01-23)
- ✨ Первая версия Telegram-бота
- ✅ Поддержка ручного и автоматического парсинга
- ✅ Настройка интервалов от 1 минуты до 6 часов
- ✅ Система отзывов
- ✅ Проверка доступа по User ID
- ✅ Inline-клавиатура с 8 основными функциями

---

**Автор:** Claude AI
**Дата:** 23 января 2026
**Версия:** 1.0.0
