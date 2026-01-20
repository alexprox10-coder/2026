# 🚀 Простая установка БЕЗ Docker

## ✅ Что уже готово:

- API сервер запущен на `http://localhost:5555` ✅
- Workflow настроен для работы без Docker ✅
- Все 3 платформы работают (Cian, Yandex, Avito) ✅
- База данных создана ✅

## 📥 Установка за 3 шага:

### Шаг 1: Импортируйте workflow

1. Откройте n8n в браузере (обычно https://n8n.arendadom24.ru)
2. Нажмите **☰** (меню) → **Import from File** или **Settings** → **Import from File**
3. Загрузите файл: `/home/user/2026/rental_parser_full_workflow.json`
4. Нажмите **Import**

### Шаг 2: Настройте Telegram

#### 2.1. Добавьте Bot Token:

1. В импортированном workflow найдите любой **Telegram** node (например "Send Response")
2. В поле **Credentials** нажмите **Create New**
3. Выберите **Telegram API**
4. Вставьте ваш **Bot Token** от @BotFather
   - Если нет бота: напишите @BotFather в Telegram → `/newbot` → следуйте инструкциям
5. Нажмите **Save**

#### 2.2. Укажите Chat ID:

1. Откройте node **"Format Listing"** (двойной клик)
2. В коде найдите строку:
   ```javascript
   chatId: 'YOUR_CHAT_ID_HERE'
   ```
3. Замените `YOUR_CHAT_ID_HERE` на ваш Telegram Chat ID

**Как получить Chat ID:**
```bash
# 1. Отправьте /start вашему боту в Telegram
# 2. Выполните (замените YOUR_BOT_TOKEN на токен от BotFather):
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"

# 3. В ответе найдите:
"chat":{"id":123456789}
#             ^^^^^^^^^ это ваш Chat ID
```

### Шаг 3: Протестируйте и активируйте

1. **Тест подключения к API:**
   - Откройте node **"Run Parser API"**
   - Нажмите **Execute Node** (внизу справа)
   - Должен быть успех ✅ с ответом `{"success": true}`

2. **Тест всего workflow:**
   - Нажмите **Execute Workflow** (вверху)
   - Проверьте что каждый node прошёл успешно
   - В Telegram должны прийти новые объявления

3. **Активируйте автозапуск:**
   - Переключатель **Active** (вверху справа) → **ON**
   - Теперь workflow работает автоматически каждые 3 минуты ⏱️

## ✅ Готово! Что умеет бот:

### 🤖 Команды бота в Telegram:

Напишите боту `/start` - появится меню:

- **🏙️ Выбрать город** - Москва, СПб, Благовещенск, Екатеринбург и др.
- **🔍 Выбрать платформы** - включить/выключить Cian, Yandex, Avito
- **⚙️ Настройки** - посмотреть текущую конфигурацию
- **🤖 AI Консультант** - задать вопрос об аренде недвижимости
- **❓ FAQ** - частые вопросы
- **✍️ Отзыв** - оставить отзыв

### 📱 Автоматическая работа:

Каждые 3 минуты бот:
1. Парсит новые объявления с выбранных платформ
2. Извлекает: цену, адрес, телефон, фото
3. Отправляет только **новые** объявления (без дублей)
4. Автоматически звонит на указанный телефон (если настроено)

### 💬 Формат сообщений:

```
🏠 2-комн 65 м²

💰 Цена: 45000 ₽/мес
📍 Москва, ул. Ленина, 15
📞 Телефон: +79991234567
🔗 Платформа: Cian

[Открыть объявление](https://cian.ru/...)
```

## 🔧 Проверка статуса

### API сервер работает?

```bash
curl http://localhost:5555/health
# Должен вернуть: {"status":"ok","message":"API server is running"}
```

### Конфигурация парсера:

```bash
curl http://localhost:5555/status
# Покажет: город, включен ли Telegram, автонабор и т.д.
```

### Посмотреть собранные объявления:

```bash
sqlite3 /home/user/2026/rental_parser/rental_parser.db \
  "SELECT COUNT(*) as total FROM listings;"

sqlite3 /home/user/2026/rental_parser/rental_parser.db \
  "SELECT platform, COUNT(*) FROM listings GROUP BY platform;"
```

## ⚙️ Изменить настройки

Файл конфигурации: `/home/user/2026/rental_parser/.env`

```bash
# Редактировать:
nano /home/user/2026/rental_parser/.env

# После изменений перезапустить API:
pkill -f api_server.py
cd /home/user/2026/rental_parser && python3 api_server.py > /tmp/api_server.log 2>&1 &
```

**Основные настройки:**

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_IDS=123456789,987654321  # Несколько ID через запятую

# Город (латиницей)
CITY=moskva  # или: sankt-peterburg, blagoveshchensk, ekaterinburg

# Максимум страниц для парсинга
MAX_PAGES=5

# Автонабор
AUTO_DIAL_ENABLED=true
AUTO_DIAL_BACKEND=mock  # или: webhook, asterisk, twilio
```

## 🐛 Решение проблем

### ❌ Ошибка "Connection refused" в n8n

**Причина:** API сервер не запущен

**Решение:**
```bash
# Проверить:
ps aux | grep api_server.py

# Если не запущен:
cd /home/user/2026/rental_parser
python3 api_server.py > /tmp/api_server.log 2>&1 &

# Проверить что работает:
curl http://localhost:5555/health
```

### ❌ Нет сообщений в Telegram

**Причина 1:** Неправильный Chat ID

**Решение:**
- Проверьте что в node "Format Listing" указан правильный Chat ID
- Проверьте что вы отправили боту `/start`

**Причина 2:** Неправильный Bot Token

**Решение:**
- Проверьте Telegram credentials в n8n
- Получите новый токен у @BotFather если нужно

**Причина 3:** Бот не может писать первым

**Решение:**
- Сначала напишите боту `/start`
- Только после этого бот сможет отправлять сообщения

### ❌ Дублируются объявления

**Причина:** База данных не работает

**Решение:**
```bash
# Проверить базу:
ls -lh /home/user/2026/rental_parser/rental_parser.db

# Если нет - создать:
cd /home/user/2026/rental_parser
python3 -c "from database.models import init_db; init_db('rental_parser.db')"
```

### ❌ Workflow не активируется

**Причина:** Не все nodes настроены

**Решение:**
1. Выполните workflow вручную (Execute Workflow)
2. Посмотрите какой node выдал ошибку (красный)
3. Откройте этот node и исправьте проблему
4. Обычно проблема в Telegram credentials или Chat ID

## 💰 Стоимость

**Полностью бесплатно! 0₽**

- Нет платных API
- Неограниченные запросы
- Парсит напрямую с сайтов

## 📊 Статистика работы

### Логи API сервера:
```bash
tail -f /tmp/api_server.log
```

### Логи парсера:
```bash
tail -f /home/user/2026/rental_parser/parser.log
```

### База данных:
```bash
sqlite3 /home/user/2026/rental_parser/rental_parser.db

# В SQLite выполните:
SELECT COUNT(*) FROM listings;
SELECT * FROM listings ORDER BY created_at DESC LIMIT 10;
.quit
```

## 🎉 Готово!

Теперь у вас работает полностью автоматический парсер аренды:

✅ Парсит Cian + Yandex + Avito
✅ Telegram бот с меню
✅ AI консультант
✅ Выбор города и платформ
✅ Автонабор телефонов
✅ Без дублей
✅ Полностью бесплатно

Нужна помощь? Проверьте логи или напишите!
