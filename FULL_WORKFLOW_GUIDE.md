# 🚀 Полный Workflow - Rental Parser PRO

## ✨ Возможности

**Ваш полнофункциональный бот для риелторов!**

### 📋 Что умеет:

✅ **Парсинг 3 платформ одновременно:**
- 🔵 Cian.ru
- 🔴 Yandex.Realty
- 🟢 Avito.ru

✅ **Telegram бот с меню:**
- 🏙️ Выбор города (Москва, СПб, Благовещенск и др.)
- 🔍 Выбор платформ (все вместе или по отдельности)
- ⚙️ Настройки парсера
- 🤖 AI консультант по аренде
- ❓ FAQ для пользователей
- ✍️ Система отзывов

✅ **Автоматическая работа:**
- ⏰ Парсинг каждые 3 минуты
- 📸 Отправка с ФОТО + цена + адрес + телефон
- 🔄 Дедупликация (без повторов!)
- 📞 Автонабор телефонов (опционально)

✅ **Только долгосрочная аренда:**
- ❌ Исключены посуточные
- ❌ Исключена продажа
- ✅ Только месячная аренда

---

## 📦 Установка (10 минут)

### Шаг 1: Убедитесь что API работает

```bash
# Проверка
curl http://localhost:5555/health

# Если не работает - запустите
cd /home/user/2026/rental_parser
nohup python3 api_server.py > api_server.log 2>&1 &
```

### Шаг 2: Настройте .env

```bash
cd /home/user/2026/rental_parser
nano .env
```

**Минимальная конфигурация:**

```bash
# ОБЯЗАТЕЛЬНО!
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
TELEGRAM_CHAT_IDS=ваш_chat_id

# Опционально
CITY=москва
MAX_PAGES=5
AUTO_DIAL_ENABLED=true
DIALER_BACKEND=mock
```

### Шаг 3: Импортируйте workflow в n8n

**Файл:** `/home/user/2026/rental_parser_full_workflow.json`

**В n8n:**
1. Нажмите **"+"** (новый workflow)
2. Три точки **⋮** → **"Import from File"**
3. Выберите файл: `rental_parser_full_workflow.json`
4. Нажмите **"Import"**

### Шаг 4: Настройте Telegram credentials

**В импортированном workflow:**

1. Откройте любую **Telegram** ноду
2. Нажмите на **"Credentials"**
3. Создайте новые credentials:
   - **Bot Token:** ваш токен от @BotFather
   - **Name:** Rental Bot (или любое имя)
4. Сохраните

**Обновите все Telegram ноды:**
- "Telegram Bot"
- "Send Message"
- "Send Photo"

Везде выберите созданные credentials.

### Шаг 5: Настройте Chat ID

**В ноде "Format Listing" найдите строку:**

```javascript
const chatIds = $getWorkflowStaticData('global').subscribedUsers || ['7984101063'];
```

**Замените** `7984101063` на **ваш Chat ID**.

Или в **Static Data workflow** добавьте:

```json
{
  "global": {
    "subscribedUsers": ["ваш_chat_id"]
  }
}
```

### Шаг 6: Тестовый запуск

1. Нажмите **"Execute Workflow"**
2. Напишите боту **/start** в Telegram
3. Должно появиться меню с кнопками! ✅

### Шаг 7: Активируйте workflow

1. Включите переключатель **"Active"** вверху справа
2. Теперь парсер работает автоматически каждые 3 минуты!

---

## 🎯 Как использовать бот

### Команды:

- `/start` или `/menu` - Главное меню

### Кнопки главного меню:

| Кнопка | Описание |
|--------|----------|
| 🏙️ Выбрать город | Выбор города для парсинга (Москва, СПб, и др.) |
| 🔍 Выбрать платформы | Включение/выключение Cian, Yandex, Avito |
| ⚙️ Настройки | Просмотр текущих настроек |
| 🤖 AI Консультант | Задать вопрос об аренде квартир |
| ❓ FAQ | Частые вопросы |
| ✍️ Отзыв | Оставить отзыв о боте |

### Выбор города:

1. Нажмите **"🏙️ Выбрать город"**
2. Выберите город из списка
3. Парсер начнет искать квартиры в этом городе

**Доступные города:**
- Москва
- Санкт-Петербург
- Благовещенск
- Екатеринбург
- Новосибирск
- Казань

### Выбор платформ:

1. Нажмите **"🔍 Выбрать платформы"**
2. Включите/выключите нужные:
   - ✅ Cian
   - ✅ Yandex
   - ✅ Avito
3. Или нажмите **"✅ Все"** чтобы включить все

### AI Консультант:

1. Нажмите **"🤖 AI Консультант"**
2. Напишите любой вопрос, например:
   - "Как проверить квартиру перед арендой?"
   - "На что обратить внимание при осмотре?"
   - "Какие документы нужны для аренды?"
3. Получите ответ от AI!

---

## 📊 Как работает workflow

### Структура:

```
┌────────────────────────────────────────────────┐
│             TELEGRAM BOT (меню)                │
│  - Выбор города                                │
│  - Выбор платформ                              │
│  - AI консультант                              │
│  - FAQ, отзывы                                 │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│          АВТОМАТИЧЕСКИЙ ПАРСИНГ                │
│          (каждые 3 минуты)                     │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│    HTTP POST → API /parse-async                │
│    (запускает парсинг в фоне)                  │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│         Ожидание 10 секунд                     │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│    HTTP GET → API /get-unsent?limit=50         │
│    (получить неотправленные объявления)        │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│         Split Listings                         │
│         (разбить на отдельные)                 │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│         Format Listing                         │
│    - Добавить эмодзи по платформе              │
│    - Форматировать цену, адрес                 │
│    - Создать caption для Telegram              │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│      Send Photo в Telegram                     │
│    🔵/🔴/🟢 Платформа                           │
│    💰 Цена                                     │
│    🏠 Комнаты, площадь                         │
│    📍 Адрес                                    │
│    📞 Телефон                                  │
│    🔗 Ссылка                                   │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│    Пауза 2 секунды между объявлениями          │
└────────────────────────────────────────────────┘
```

### Пример сообщения в Telegram:

```
🔵 Cian

2-комн квартира

💰 45 000 ₽/мес
🏠 2-комн, 65 м²
📍 Москва, ул. Тверская, 10
📞 +79991234567

🔗 Открыть объявление
```

---

## ⚙️ Настройка

### Изменить интервал парсинга:

**В ноде "Schedule 3min":**

```json
{
  "interval": [
    {
      "field": "minutes",
      "minutesInterval": 5  // Изменить на 5 минут
    }
  ]
}
```

Или измените `"minutes"` на `"hours"`:

```json
{
  "interval": [
    {
      "field": "hours",
      "hoursInterval": 1  // Каждый час
    }
  ]
}
```

### Изменить количество объявлений за раз:

**В ноде "Get Unsent Listings":**

Измените URL:
```
http://localhost:5555/get-unsent?limit=100
```

### Добавить свои города:

**В ноде "Router" найдите:**

```javascript
else if (callback === 'select_city') {
  // Добавьте свои города
  response.keyboard = {
    inline_keyboard: [
      [{text: 'Москва', callback_data: 'city_москва'}],
      [{text: 'Ваш город', callback_data: 'city_вашгород'}],
      // ...
    ]
  };
}
```

### Изменить Chat ID для отправки:

**Вариант 1: В Static Data workflow**

```json
{
  "global": {
    "subscribedUsers": ["123456789", "987654321"]
  }
}
```

**Вариант 2: В ноде "Format Listing"**

```javascript
const chatIds = ['123456789', '987654321'];
```

---

## 🔧 API Endpoints

Ваш API сервер предоставляет:

### GET /health
**Проверка здоровья API**

```bash
curl http://localhost:5555/health
```

Ответ:
```json
{
  "status": "ok",
  "message": "API server is running"
}
```

### GET /status
**Статус и конфигурация**

```bash
curl http://localhost:5555/status
```

Ответ:
```json
{
  "status": "running",
  "telegram_configured": true,
  "city": "москва",
  "max_pages": "5",
  "auto_dial_enabled": "true"
}
```

### GET /get-unsent?limit=20
**Получить неотправленные объявления**

```bash
curl "http://localhost:5555/get-unsent?limit=20"
```

Ответ:
```json
[
  {
    "id": 1,
    "platform": "cian",
    "url": "https://cian.ru/rent/...",
    "title": "2-комн квартира",
    "price": 45000,
    "address": "Москва, Тверская, 10",
    "phone": "+79991234567",
    "rooms": 2,
    "area": 65
  }
]
```

### POST /parse-async
**Запустить парсинг в фоне**

```bash
curl -X POST http://localhost:5555/parse-async
```

Ответ:
```json
{
  "success": true,
  "message": "Parser started in background",
  "pid": 12345
}
```

---

## 🐛 Решение проблем

### ❌ Бот не отвечает в Telegram

**Причина:** Не настроены Telegram credentials

**Решение:**
1. Откройте любую Telegram ноду
2. Создайте credentials с вашим Bot Token
3. Примените ко всем Telegram нодам

### ❌ Не приходят объявления

**Причина 1:** API сервер не запущен

```bash
curl http://localhost:5555/health
# Если ошибка - запустите:
cd /home/user/2026/rental_parser
nohup python3 api_server.py > api_server.log 2>&1 &
```

**Причина 2:** Не настроен .env

```bash
nano .env
# Убедитесь что указаны:
# TELEGRAM_BOT_TOKEN
# TELEGRAM_CHAT_IDS
```

**Причина 3:** Нет новых объявлений

```bash
# Проверьте вручную
curl "http://localhost:5555/get-unsent?limit=10"
# Если пусто [] - нужно запустить парсинг:
curl -X POST http://localhost:5555/parse-async
```

### ❌ AI консультант не работает

**Причина:** Не настроены OpenAI credentials

**Решение:**
1. Получите API ключ на [platform.openai.com](https://platform.openai.com)
2. В n8n: Settings → Credentials → Add New
3. Тип: OpenAI
4. Вставьте ваш API ключ
5. В ноде "AI Request" выберите созданные credentials

Или используйте **OpenRouter** (как в вашем старом workflow):
- Уже настроен в текущем workflow
- Нужен API key от [openrouter.ai](https://openrouter.ai)

### ❌ Дублируются объявления

**Причина:** Дедупликация работает на уровне БД, но нужно проверить

**Решение:**

```bash
cd /home/user/2026/rental_parser

# Проверка дубликатов
python3 -c "
from database.models import init_db, RentalListing
db = init_db()
total = db.query(RentalListing).count()
unique = db.query(RentalListing.listing_id).distinct().count()
print(f'Total: {total}, Unique: {unique}')
"
```

### ❌ Отправляет старые объявления

**Причина:** Не помечаются как отправленные

**Проверка:**

```bash
# API должен автоматически помечать через run_once.py
# Проверьте что парсинг проходит успешно:
tail -f /home/user/2026/rental_parser/api_server.log
```

---

## 📊 Мониторинг

### Проверить что API работает:

```bash
curl http://localhost:5555/health
```

### Проверить процесс API:

```bash
ps aux | grep api_server.py
```

### Логи API:

```bash
tail -f /home/user/2026/rental_parser/api_server.log
```

### Статистика парсинга:

```bash
curl http://localhost:5555/status
```

### Проверить workflow в n8n:

1. Откройте workflow
2. Нажмите **"Executions"** (история)
3. Смотрите успешные/неуспешные выполнения

---

## ✅ Чек-лист готовности

- [ ] Python зависимости установлены (`pip install -r requirements.txt`)
- [ ] `.env` файл настроен (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS)
- [ ] API сервер запущен (`curl http://localhost:5555/health` → OK)
- [ ] Workflow импортирован в n8n
- [ ] Telegram credentials настроены во всех нодах
- [ ] Chat ID указан в "Format Listing" ноде
- [ ] Тестовый запуск выполнен (Execute Workflow)
- [ ] Бот отвечает на /start в Telegram
- [ ] Workflow активирован (Active = ON)
- [ ] Парсинг запускается каждые 3 минуты

---

## 🎉 Готово!

Теперь у вас **полнофункциональный бот для риелторов** со всеми возможностями:

✅ Парсинг 3 платформ
✅ Выбор города и платформ
✅ AI консультант
✅ FAQ и отзывы
✅ Отправка с фото и деталями
✅ Дедупликация
✅ Автонабор (опционально)

**Файлы:**
- Workflow: `/home/user/2026/rental_parser_full_workflow.json`
- API: `/home/user/2026/rental_parser/api_server.py`
- Парсер: `/home/user/2026/rental_parser/run_once.py`

**Вопросы?** Смотрите также:
- [IMPLEMENTATION_MAP.md](IMPLEMENTATION_MAP.md) - карта реализации
- [SIMPLE_N8N_SETUP.md](SIMPLE_N8N_SETUP.md) - простая установка
- [AGENT_SETUP.md](AGENT_SETUP.md) - автономный агент
