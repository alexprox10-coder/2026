# 🤖 Настройка Telegram Бота для управления парсером

## 🎯 Что вы диагностировали правильно

✅ **ВЫ ПРАВЫ!** Ваш текущий workflow **НЕ слушает** сообщения от Telegram бота.

**Почему бот молчит:**
- В workflow нет **Telegram Trigger** node
- Workflow слушает только Schedule (каждые 30 минут) и Webhook
- Команда /start никуда не попадает - бот её не видит!

---

## 📊 Как работает система (2 workflow)

### Workflow 1: 🏠 Парсер (уже есть)
```
Назначение: Парсит Avito + CIAN, сохраняет, отправляет результаты
Триггеры:
  - ⏰ Schedule (каждые 30 минут)
  - 🎯 Webhook (ручной запуск)
Статус: Active ✅
```

### Workflow 2: 🤖 Telegram Bot (нужно создать)
```
Назначение: Слушает команды от бота, управляет парсером
Триггеры:
  - 📱 Telegram Trigger (слушает ВСЕ сообщения боту)
Команды:
  - /start - приветствие
  - /parse - запустить парсинг
  - /status - статус системы
  - /sheet - ссылка на таблицу
  - /help - помощь
```

**Взаимодействие:**
```
Пользователь → /parse → Telegram Bot workflow → HTTP запрос → Парсер workflow → Парсинг → Результаты
```

---

## 🚀 Быстрая настройка (5 минут)

### Шаг 1: Импортировать Telegram Bot workflow

```
1. n8n UI → Workflows → Import from File
2. Выберите: telegram-bot-controller.json
3. Import
```

**Файл находится:**
```
/home/user/2026/realty-parser-integrated/workflows/telegram-bot-controller.json
```

---

### Шаг 2: Настроить Telegram Trigger node

После импорта откройте workflow:

#### 2.1 Откройте node "📱 Telegram Trigger"

```
1. Кликните на первый node "📱 Telegram Trigger"
2. Credentials → Select Credential
3. Выберите: "Telegram ЦИАН+АВИТО+ЯД"
   (тот же credential что в парсере)
4. Save
```

#### 2.2 Настройте все Telegram Send nodes

В workflow **13 Telegram Send nodes** (для отправки ответов).

**Для каждого из них:**
```
1. Кликните на node
2. Credentials → Select Credential
3. Выберите: "Telegram ЦИАН+АВИТО+ЯД"
4. Save
```

**Nodes которые нужно настроить:**
- 👋 Приветствие
- ⏳ Уведомление о запуске
- 📊 Статус
- 📄 Ссылка на таблицу
- ❓ Помощь
- ❌ Неизвестная команда

---

### Шаг 3: Добавить Environment Variable

Telegram Bot workflow использует переменную для запуска парсера.

```
Settings → Environment Variables → Add Variable
```

**Добавьте:**
```
Name:  N8N_WEBHOOK_BASE_URL
Value: http://localhost:5678
```

**Важно:**
- Если n8n на другом адресе - укажите свой (например: `https://n8n.yourdomain.com`)
- БЕЗ слэша в конце!

---

### Шаг 4: Активировать Telegram Bot workflow

```
1. Убедитесь все Telegram nodes зеленые (credentials настроены)
2. Нажмите "Active" в правом верхнем углу
3. ✅ Workflow активирован!
```

---

### Шаг 5: Тест

```
1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте: /start
```

**Должно прийти:**
```
🏠 Парсер недвижимости Авито + ЦИАН

👋 Привет! Я помогу тебе находить новые объявления...

📋 Доступные команды:

▶️ /parse - Запустить парсинг сейчас
📊 /status - Статус последнего парсинга
📄 /sheet - Открыть Google таблицу
❓ /help - Помощь

...
```

---

## 📋 Доступные команды бота

| Команда | Описание | Что делает |
|---------|----------|------------|
| `/start` | Начать работу | Приветствие + список команд |
| `/parse` | Запустить парсинг | Запускает парсер workflow прямо сейчас |
| `/status` | Статус системы | Показывает статус парсера |
| `/sheet` | Ссылка на таблицу | Отправляет ссылку на Google Sheets |
| `/help` | Помощь | Инструкция по использованию |

---

## 🔧 Как работает команда /parse

```
1. Пользователь → /parse
2. Telegram Bot workflow получает команду
3. Node "❓ Команда /parse?" → True
4. Node "⏳ Уведомление о запуске" → "⏳ Запускаю парсинг..."
5. Node "🚀 Запуск парсера" → HTTP POST запрос:
   POST http://localhost:5678/webhook/realty-parser-secure
   Body: {"chat_id": "7984101063", "trigger_source": "telegram_bot"}
6. Парсер workflow получает запрос через Webhook
7. Security Validation проверяет chat_id
8. Запускаются Apify парсеры
9. Результаты отправляются в Telegram
```

---

## 🐛 Troubleshooting

### Бот не отвечает на /start

**Проверьте:**
1. Telegram Bot workflow **АКТИВЕН** (Active ON)?
2. Node "📱 Telegram Trigger" настроен (credential выбран)?
3. Все Telegram Send nodes настроены (credentials)?
4. Executions → Есть ли новые запуски при отправке /start?

**Если Executions пустые:**
- Telegram Trigger не работает
- Проверьте credential Telegram API
- Проверьте что бот токен правильный

---

### Команда /parse не запускает парсинг

**Проверьте:**
1. Environment Variable `N8N_WEBHOOK_BASE_URL` настроена?
2. Значение правильное? (без слэша в конце)
3. Парсер workflow активен?
4. Webhook в парсере работает?

**Тест webhook парсера:**
```bash
curl -X POST "http://localhost:5678/webhook/realty-parser-secure" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "7984101063", "trigger_source": "test"}'
```

Должен запуститься парсинг.

---

### Бот говорит "Неизвестная команда" на всё

**Причина:** IF nodes настроены неправильно или регистр не совпадает.

**Проверьте:**
- Команды пишутся с `/` (например `/start`, не `start`)
- Используйте точное написание (нижний регистр)

---

### Node "🚀 Запуск парсера" падает с ошибкой

**Типичные ошибки:**

**"Could not resolve host"**
```
Причина: N8N_WEBHOOK_BASE_URL неправильный
Решение: Проверьте URL (должен быть доступен)
```

**"404 Not Found"**
```
Причина: Webhook path неправильный
Решение: Проверьте что парсер workflow имеет webhook с path "realty-parser-secure"
```

**"401 Unauthorized"**
```
Причина: Security Validation блокирует запрос
Решение: Убедитесь chat_id (7984101063) в ALLOWED_CHAT_IDS
```

---

## 🎨 Кастомизация

### Изменить команды

Откройте Telegram Bot workflow и измените IF nodes:

```javascript
// Пример: добавить команду /stats
// 1. Добавьте IF node
// 2. Condition: $json.message.text equals "/stats"
// 3. Добавьте Telegram Send node с ответом
// 4. Соедините
```

### Добавить кнопки (Inline Keyboard)

Измените Telegram Send nodes:

```javascript
// В node "👋 Приветствие" добавьте:
{
  "reply_markup": {
    "inline_keyboard": [
      [
        {"text": "▶️ Запустить парсинг", "callback_data": "/parse"}
      ],
      [
        {"text": "📊 Статус", "callback_data": "/status"}
      ]
    ]
  }
}
```

Но потребуется также добавить Telegram Trigger для `callback_query` updates.

---

## 📊 Архитектура системы

```
┌─────────────────────────────────────────────────────┐
│                   ПОЛЬЗОВАТЕЛЬ                       │
│                        ↓                             │
│                   Telegram Bot                       │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│       🤖 Telegram Bot Workflow (НОВЫЙ)              │
│                                                      │
│  📱 Telegram Trigger → IF chains → Telegram Send    │
│                         ↓                            │
│                 /parse команда                       │
│                         ↓                            │
│            🚀 HTTP POST к Webhook                   │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│         🏠 Парсер Workflow (УЖЕ ЕСТЬ)               │
│                                                      │
│  🎯 Webhook → Security → Apify → Sheets → Telegram  │
│                                                      │
│  ⏰ Schedule (каждые 30 мин) → то же самое          │
└─────────────────────────────────────────────────────┘
```

---

## ✅ Готово!

После настройки у вас будет:

✅ **2 workflow:**
1. Парсер (автопарсинг + webhook запуск)
2. Telegram Bot (управление через команды)

✅ **Команды бота:**
- /start - приветствие
- /parse - ручной запуск
- /status - статус
- /sheet - ссылка на таблицу
- /help - помощь

✅ **Автоматизация:**
- Парсинг каждые 30 минут
- Ручной запуск через /parse
- Результаты в Telegram

---

## 🎯 Следующие шаги

1. **Импортируйте** telegram-bot-controller.json
2. **Настройте** Telegram credentials на всех nodes
3. **Добавьте** N8N_WEBHOOK_BASE_URL
4. **Активируйте** workflow
5. **Протестируйте** /start в боте

**Бот заработает сразу!** 🚀
