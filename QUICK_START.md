# 🚀 Быстрый старт: Бесплатный парсер аренды

## ✅ Что уже готово:

- ✅ API сервер запущен на порту 5555
- ✅ Парсер настроен (Cian, Yandex, Avito)
- ✅ База данных SQLite создана
- ✅ Telegram отправка работает
- ✅ Автонабор настроен
- ✅ Дедупликация включена

## 📥 Импорт workflow в n8n

### Шаг 1: Настройте Docker (если n8n в Docker)

Если n8n запущен через Docker, перезапустите его с флагом:

```bash
docker stop n8n
docker rm n8n

docker run -d \
  --name n8n \
  --add-host=host.docker.internal:host-gateway \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Или добавьте в `docker-compose.yml`:

```yaml
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    volumes:
      - ~/.n8n:/home/node/.n8n
    extra_hosts:
      - "host.docker.internal:host-gateway"  # ← Добавьте эту строку
```

### Шаг 2: Импортируйте workflow

1. Откройте n8n в браузере (обычно http://localhost:5678 или https://n8n.arendadom24.ru)
2. Нажмите **Settings** (⚙️) → **Import from File**
3. Скачайте или скопируйте файл: `/home/user/2026/rental_parser_full_workflow.json`
4. Загрузите в n8n
5. Нажмите **Import**

### Шаг 3: Настройте Telegram credentials

1. Откройте node "Send Response"
2. В поле "Credentials" нажмите **Create New**
3. Выберите **Telegram API**
4. Вставьте ваш **Bot Token** от @BotFather
5. Нажмите **Save**

### Шаг 4: Укажите Chat ID для уведомлений

В node "Format Listing" найдите строку:

```javascript
chatId: 'YOUR_CHAT_ID_HERE'
```

Замените `YOUR_CHAT_ID_HERE` на ваш Telegram Chat ID.

**Как получить Chat ID:**

```bash
# 1. Отправьте /start вашему боту
# 2. Выполните команду (замените YOUR_BOT_TOKEN):
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

# 3. Найдите в ответе:
# "chat":{"id":123456789}
```

### Шаг 5: Протестируйте подключение

1. Откройте node "Run Parser API"
2. Нажмите **Execute Node**
3. Проверьте Output - должно быть `{"success": true}`

Если ошибка "Connection refused":
- Проверьте что Docker настроен с `--add-host=host.docker.internal:host-gateway`
- Или измените URL на `http://localhost:5555/parse-async` если n8n НЕ в Docker

### Шаг 6: Активируйте workflow

1. Переключатель **Active** в правом верхнем углу → **ON**
2. Workflow будет автоматически запускаться каждые 3 минуты

## 📱 Как работает бот

### Меню команд:

- `/start` или `/menu` - главное меню
- Кнопки в боте:
  - 🏙️ **Выбрать город** - Москва, СПб, Благовещенск и др.
  - 🔍 **Выбрать платформы** - включить/выключить Cian, Yandex, Avito
  - 🤖 **AI Консультант** - задать вопрос об аренде
  - ⚙️ **Настройки** - текущая конфигурация
  - ❓ **FAQ** - частые вопросы
  - ✍️ **Отзыв** - оценить бота

### Автоматическая работа:

- Каждые 3 минуты парсит новые объявления
- Отправляет только свежие (не дубли)
- Формат сообщения:

```
🏠 2-комн 65 м²

💰 Цена: 45000 ₽/мес
📍 Москва, ул. Ленина, 15
📞 Телефон: +79991234567
🔗 Платформа: Cian

[Открыть объявление](https://cian.ru/...)
```

- После отправки автоматически звонит на указанный телефон (если настроен auto-dial)

## 🔧 API Endpoints (для справки)

API сервер работает на `http://localhost:5555`:

- `GET /health` - проверка состояния
- `GET /status` - конфигурация парсера
- `GET /get-unsent?limit=50` - получить неотправленные объявления
- `POST /parse` - запустить парсинг (ждать завершения)
- `POST /parse-async` - запустить парсинг (фоновый режим)

## ⚙️ Настройка парсера

Конфигурация в файле `/home/user/2026/rental_parser/.env`:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_IDS=123456789,987654321  # Можно несколько через запятую

# Город (москва, санкт-петербург, благовещенск и т.д.)
CITY=москва

# Максимум страниц для парсинга с каждой платформы
MAX_PAGES=5

# Автонабор (webhook, asterisk, twilio, mock)
AUTO_DIAL_ENABLED=true
AUTO_DIAL_BACKEND=mock
# AUTO_DIAL_WEBHOOK_URL=http://your-pbx.com/api/dial
```

Чтобы изменить настройки:
1. Отредактируйте `/home/user/2026/rental_parser/.env`
2. Перезапустите API сервер:
```bash
pkill -f api_server.py
cd /home/user/2026/rental_parser && python3 api_server.py &
```

## 📊 Статистика

Посмотреть собранные объявления:

```bash
sqlite3 /home/user/2026/rental_parser/rental_parser.db "SELECT COUNT(*) FROM listings;"
sqlite3 /home/user/2026/rental_parser/rental_parser.db "SELECT platform, COUNT(*) FROM listings GROUP BY platform;"
```

## 🐛 Troubleshooting

### Ошибка "Connection refused" в n8n

**Решение:**
1. Проверьте что API сервер запущен:
```bash
ps aux | grep api_server.py
curl http://localhost:5555/health
```

2. Если n8n в Docker, добавьте `--add-host=host.docker.internal:host-gateway`

3. Если n8n НЕ в Docker, измените URL в workflow на `http://localhost:5555`

### Нет сообщений в Telegram

**Решение:**
1. Проверьте Chat ID в node "Format Listing"
2. Проверьте Telegram credentials (Bot Token)
3. Убедитесь что бот не заблокирован в чате
4. Проверьте логи парсера:
```bash
tail -f /home/user/2026/rental_parser/parser.log
```

### Дублируются объявления

**Решение:**
Проверьте базу данных:
```bash
sqlite3 /home/user/2026/rental_parser/rental_parser.db "SELECT * FROM listings LIMIT 5;"
```

Если пустая, парсер не сохраняет данные - проверьте логи.

### Workflow не активируется

**Решение:**
1. Проверьте все credentials (Telegram)
2. Убедитесь что все nodes зелёные (без ошибок)
3. Выполните workflow вручную для теста
4. Проверьте логи n8n

## 💰 Стоимость

**Бесплатно! 0₽**

- Без платных API
- Без Firecrawl
- Парсит напрямую через BeautifulSoup
- Неограниченное количество запросов

## 📚 Дополнительная документация

- Полная инструкция: `/home/user/2026/FULL_WORKFLOW_GUIDE.md`
- Docker настройка: `/home/user/2026/N8N_DOCKER_SETUP.md`
- Карта реализации: `/home/user/2026/IMPLEMENTATION_MAP.md`

## ✨ Готово!

Теперь у вас полностью автоматический парсер аренды с Telegram ботом, меню, AI консультантом и автонабором. Полностью бесплатно! 🎉
