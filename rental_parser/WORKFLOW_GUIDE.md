# 📊 Руководство по n8n Workflow

## Доступные Workflows

### 1. `rental_parser_unified_workflow.json` ⭐ (Рекомендуется)
Объединенный workflow со всеми платформами в одном потоке.

### 2. `rental_parser_workflow.json`
Базовый workflow с запуском через main.py.

---

## 🎯 Unified Workflow - Подробное описание

### Архитектура

```
                    ⏰ Триггер (каждые 4 часа)
                              |
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
   🔵 Parse Cian        🔴 Parse Yandex       🟢 Parse Avito
        ↓                     ↓                     ↓
   🏷️ Label Cian       🏷️ Label Yandex      🏷️ Label Avito
        └─────────────────────┼─────────────────────┘
                              ↓
                      🔗 Merge All Platforms
                              ↓
                      📊 Parse All JSON
                              ↓
                      💾 Save to Database
                              ↓
                      🆕 Parse New Listings
                              ↓
                      ✅ Has New Listings?
                        /              \
                   YES /                \ NO
                      ↓                  ↓
              📤 Split Listings    📭 No Listings Notice
                      ↓
              ✍️ Format Message
                      ↓
              📱 Send to Telegram
                      ↓
              ⏳ Rate Limit (3s)
                      ↓
              📞 Has Phone?
                /          \
           YES /            \ NO
              ↓              ↓
     📞 Auto-Dial    ✔️ Mark as Sent
              ↓              ↓
     ✔️ Mark as Sent  💾 Save to Sheets
              ↓
     💾 Save to Sheets
```

### Узлы (Nodes)

#### 1. **Триггеры**

**⏰ Schedule (Every 4 hours)**
- Тип: `scheduleTrigger`
- Расписание: Каждые 4 часа
- Запускает параллельный парсинг всех платформ

**🔧 Manual Webhook Trigger**
- Тип: `webhook`
- Path: `/rental-parser-manual`
- Позволяет запустить парсинг вручную через HTTP POST

#### 2. **Парсинг платформ** (параллельно)

**🔵 Parse Cian.ru**
```python
from parsers import CianParser
parser = CianParser('москва')
listings = parser.parse(max_pages=5)
```

**🔴 Parse Yandex.Realty**
```python
from parsers import YandexRealtyParser
parser = YandexRealtyParser('москва')
listings = parser.parse(max_pages=5)
```

**🟢 Parse Avito.ru**
```python
from parsers import AvitoParser
parser = AvitoParser('москва')
listings = parser.parse(max_pages=5)
```

#### 3. **Обработка данных**

**🏷️ Label Platform** (x3)
- Добавляет метку платформы к результатам
- Подготавливает данные для объединения

**🔗 Merge All Platforms**
- Тип: `merge`
- Режим: `mergeByPosition`
- Объединяет результаты всех трех парсеров

**📊 Parse All JSON**
- Парсит JSON из всех платформ
- Создает массив `all_listings`

**💾 Save to Database**
- Сохраняет в SQLite
- Автоматическая дедупликация по `listing_id`
- Возвращает только новые объявления

**🆕 Parse New Listings**
- Извлекает массив новых объявлений
- Передает далее для отправки

#### 4. **Проверка и разделение**

**✅ Has New Listings?**
- Тип: `if`
- Условие: `new_listings.length > 0`
- YES → отправка в Telegram
- NO → уведомление "Нет новых объявлений"

**📤 Split Listings**
- Тип: `splitOut`
- Разделяет массив на отдельные объявления
- Каждое обрабатывается индивидуально

#### 5. **Отправка менеджеру**

**✍️ Format Message**
- Форматирует сообщение для Telegram
- Эмодзи по платформе: 🔵 Cian, 🔴 Yandex, 🟢 Avito
- Markdown форматирование

**📱 Send to Telegram**
- Отправка в Telegram
- Использует `TELEGRAM_CHAT_ID` из env
- Markdown mode включен

**⏳ Rate Limit (3s)**
- Задержка 3 секунды между сообщениями
- Защита от rate limit Telegram (30 msg/sec)

#### 6. **Автодозвон (опционально)**

**📞 Has Phone?**
- Проверяет наличие телефона
- YES → триггер автодозвона
- NO → пропуск

**📞 Trigger Auto-Dial**
- HTTP POST на `AUTO_DIAL_WEBHOOK_URL`
- Payload: `{phone, listing_id, platform, url}`
- Интеграция с телефонией

#### 7. **Финализация**

**✔️ Mark as Sent**
- Помечает объявление как отправленное
- `sent_to_manager = True`
- `sent_at = now()`
- `manager_id = 'n8n_workflow'`

**💾 Save to Google Sheets**
- Сохраняет в Google Sheets
- Sheet: `RentalListings`
- Колонки: Timestamp, Platform, URL, Title, Price, Rooms, Area, Address, Phone, Sent

#### 8. **Уведомления**

**✅ Completion Notice**
- Отправляется при наличии новых объявлений
- Статистика по каждой платформе
- Общее количество новых

**📭 No Listings Notice**
- Отправляется если новых нет
- Информирует о том, что все уже отправлено

---

## 🚀 Установка и настройка

### Шаг 1: Установка n8n

```bash
# Через npm
npm install -g n8n

# Через Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### Шаг 2: Импорт workflow

1. Откройте n8n: http://localhost:5678
2. Нажмите **"Add workflow"** → **"Import from file"**
3. Выберите `rental_parser_unified_workflow.json`
4. Workflow будет импортирован

### Шаг 3: Настройка креденшиалов

#### Telegram API
1. Нажмите на ноду **"📱 Send to Telegram"**
2. Credentials → **"Telegram account"**
3. Введите ваш `Bot Token` от @BotFather
4. Сохраните

#### Google Sheets (опционально)
1. Нажмите на ноду **"💾 Save to Google Sheets"**
2. Credentials → **"Google Sheets OAuth2"**
3. Пройдите OAuth авторизацию
4. Выберите документ и лист

### Шаг 4: Настройка переменных окружения

В n8n Settings → Environment Variables:

```env
TELEGRAM_CHAT_ID=123456789
GOOGLE_SHEET_ID=your_sheet_id_here
AUTO_DIAL_WEBHOOK_URL=https://your-telephony.com/webhook
```

Как узнать `TELEGRAM_CHAT_ID`:
1. Напишите боту [@userinfobot](https://t.me/userinfobot)
2. Скопируйте ваш ID

### Шаг 5: Активация workflow

1. Нажмите **"Active"** в правом верхнем углу
2. Workflow начнет работать по расписанию

---

## 🔧 Настройка параметров

### Изменить город

В нодах парсинга замените `'москва'` на нужный город:

```python
# Было
parser = CianParser('москва')

# Стало
parser = CianParser('санкт-петербург')
```

Доступные города:
- `москва`
- `санкт-петербург`
- `новосибирск`
- `екатеринбург`
- И другие крупные города

### Изменить количество страниц

Замените `max_pages=5` на нужное значение:

```python
# 3 страницы для быстрого парсинга
listings = parser.parse(max_pages=3)

# 10 страниц для глубокого парсинга
listings = parser.parse(max_pages=10)
```

**Рекомендации:**
- 3-5 страниц: быстро, мало нагрузки
- 5-10 страниц: оптимально для production
- 10+ страниц: риск бана без прокси

### Изменить частоту запуска

В ноде **"⏰ Schedule"**:

```json
// Каждые 2 часа
"hoursInterval": 2

// Каждые 6 часов
"hoursInterval": 6

// Ежедневно в 9:00
"cronExpression": "0 9 * * *"
```

### Отключить автодозвон

Удалите или деактивируйте ноду **"📞 Trigger Auto-Dial"**.

### Отключить Google Sheets

Удалите или деактивируйте ноду **"💾 Save to Google Sheets"**.

---

## 🎛️ Ручной запуск через Webhook

### Получить Webhook URL

1. Откройте ноду **"🔧 Manual Webhook Trigger"**
2. Скопируйте **Production URL**
3. Примерно так: `https://your-n8n.com/webhook/rental-parser-manual`

### Запустить через curl

```bash
curl -X POST https://your-n8n.com/webhook/rental-parser-manual
```

### Запустить через браузер

Откройте URL в браузере или используйте Postman.

### Ответ

```json
{
  "success": true,
  "message": "Парсинг запущен вручную",
  "timestamp": "2026-01-17T12:00:00.000Z"
}
```

---

## 📊 Мониторинг

### Просмотр выполнений

1. В n8n перейдите в **"Executions"**
2. Выберите workflow **"Unified Rental Parser"**
3. Смотрите историю запусков

### Проверка ошибок

Если workflow упал:
1. Откройте failed execution
2. Найдите красную ноду
3. Посмотрите error message
4. Проверьте логи: `logs/parser.log`

### Статистика в Telegram

После каждого запуска приходит уведомление:

```
✅ Парсинг завершен!

📊 Статистика:
🔵 Cian: 45 объявлений
🔴 Yandex: 38 объявлений
🟢 Avito: 52 объявлений

🆕 Новых: 12

⏰ Время: 17.01.2026, 14:35:22
```

---

## 🐛 Устранение проблем

### Ошибка "Module not found"

Убедитесь что Python пути правильные:

```bash
cd /home/user/2026/rental_parser
python3 -c "from parsers import CianParser; print('OK')"
```

### Ошибка "Database is locked"

SQLite не поддерживает параллельные записи. Если несколько workflow запущены одновременно:

```bash
# Подождите завершения других процессов
ps aux | grep python | grep rental

# Или используйте PostgreSQL вместо SQLite
```

### Парсер ничего не находит

1. Проверьте интернет соединение
2. Сайты могли изменить структуру HTML
3. Попробуйте с прокси
4. Проверьте логи

### Telegram не отправляет

1. Проверьте `TELEGRAM_BOT_TOKEN`
2. Проверьте `TELEGRAM_CHAT_ID`
3. Убедитесь что бот не заблокирован
4. Проверьте rate limit (max 30 msg/sec)

### Google Sheets не сохраняет

1. Проверьте OAuth токен
2. Убедитесь что лист называется `RentalListings`
3. Проверьте права доступа к документу

---

## 💡 Советы по оптимизации

### 1. Используйте прокси

Добавьте `--proxy-file` в команды парсинга:

```python
# В Execute Command ноде
python3 main.py --platforms cian --max-pages 5 --proxy-file proxies.txt
```

### 2. Парсите в разное время

Запускайте платформы в разное время для снижения нагрузки:

- Cian: каждые 4 часа в 00:00, 04:00, 08:00...
- Yandex: каждые 4 часа в 01:00, 05:00, 09:00...
- Avito: каждые 4 часа в 02:00, 06:00, 10:00...

### 3. Ограничьте количество объявлений

В ноде **"📤 Split Listings"** добавьте limit:

```javascript
// Отправлять максимум 20 объявлений за раз
$json.new_listings.slice(0, 20)
```

### 4. Добавьте фильтры

Фильтруйте по цене, комнатам, району:

```javascript
// В ноде Set перед Split
$json.new_listings.filter(l =>
  l.price >= 20000 &&
  l.price <= 80000 &&
  l.rooms >= 1 &&
  l.rooms <= 3
)
```

### 5. Группируйте отправки

Отправляйте несколько объявлений в одном сообщении:

```javascript
// Группировать по 5 объявлений
const grouped = [];
for(let i = 0; i < items.length; i += 5) {
  grouped.push(items.slice(i, i + 5));
}
return grouped;
```

---

## 📚 Дополнительные ресурсы

- [n8n Documentation](https://docs.n8n.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Python-telegram-bot](https://python-telegram-bot.org/)

---

## 🆘 Поддержка

Если workflow не работает:

1. Проверьте все ноды по очереди (Execute Node)
2. Посмотрите логи: `rental_parser/logs/parser.log`
3. Проверьте переменные окружения
4. Убедитесь что все креденшиалы настроены

**Важно:** Не забывайте активировать workflow после импорта!
