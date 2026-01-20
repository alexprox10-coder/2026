# Настройка Workflow с Firecrawl

## Что исправлено в вашем workflow

### ❌ Проблемы в старом workflow:
1. **Bad request в Send to Telegram** - неправильный формат данных
2. Нет дедупликации - одни и те же объявления отправляются повторно
3. Парсится только Cian - нет Yandex и Avito
4. Нет извлечения деталей (цена, телефон, адрес)

### ✅ Что добавлено в новом:
1. **Парсинг 3 платформ**: Cian, Yandex, Avito
2. **Извлечение деталей**: цена, телефон, адрес, площадь, фото
3. **Дедупликация через SQLite**: не отправляет повторы
4. **Правильный формат Telegram**: красивое форматирование с эмодзи
5. **Автозапуск каждые 3 минуты**

## Установка

### Шаг 1: Создать базу данных

Выполните в терминале:

```bash
sqlite3 /home/user/2026/rental_parser.db <<EOF
CREATE TABLE IF NOT EXISTS sent_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id TEXT UNIQUE NOT NULL,
    platform TEXT NOT NULL,
    url TEXT NOT NULL,
    sent_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_listing_id ON sent_listings(listing_id);
EOF
```

### Шаг 2: Импортировать workflow

1. Откройте n8n
2. Нажмите **Import from File**
3. Выберите `/home/user/2026/rental_parser_firecrawl_workflow.json`
4. Нажмите **Import**

### Шаг 3: Настроить credentials

#### 3.1. SQLite Database

1. Откройте любой SQLite node
2. Нажмите **Create New Credential**
3. Укажите путь к базе:
   ```
   /home/user/2026/rental_parser.db
   ```
4. Сохраните

#### 3.2. Telegram Bot

1. Откройте node "Send to Telegram"
2. Нажмите **Create New Credential**
3. Вставьте ваш **Bot Token** от @BotFather
4. Сохраните

### Шаг 4: Указать Chat ID

В node "Send to Telegram" замените `YOUR_CHAT_ID` на ваш Telegram Chat ID.

Получить Chat ID:
```bash
# Отправьте /start вашему боту, затем выполните:
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
# В ответе найдите "chat":{"id":123456789}
```

### Шаг 5: Обновить Firecrawl ключ (опционально)

Если ваш ключ изменился, обновите его во всех HTTP Request nodes:
- Scrape Cian
- Scrape Yandex
- Scrape Avito
- Get Details

Замените в Header "Authorization":
```
Bearer fc-df32f6aa72994d6839e7a87df954d885f
```

## Как работает workflow

```
┌─────────────────┐
│ Every 3 Minutes │ Запускается каждые 3 минуты
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Config      │ Настройки: город, платформы
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Build URLs    │ Создает URL для парсинга
└────┬────┬───┬───┘
     │    │   │
     ▼    ▼   ▼
  ┌──────────────┐
  │ Scrape 3x    │ Firecrawl парсит Cian, Yandex, Avito
  └──────┬───────┘
         │
         ▼
┌─────────────────┐
│Extract Listings │ Находит ссылки на объявления
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Get Details    │ Firecrawl получает детали каждого объявления
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Parse Details   │ Извлекает: цену, телефон, адрес
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Filter Duplicates│ Проверяет SQLite, убирает дубли
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Send to Telegram │ Отправляет красивое сообщение
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Mark as Sent   │ Сохраняет в SQLite, чтобы не повторять
└─────────────────┘
```

## Формат сообщения в Telegram

```
🏠 1-комн 45 м²

💰 Цена: 35000 ₽/мес
📍 Адрес: ул. Ленина, д. 10
📞 Телефон: +79991234567
🔗 Платформа: Cian

[Открыть объявление](https://cian.ru/...)
```

## Настройка города

В node "Config" измените значение `city`:
- `moskva` - Москва
- `sankt-peterburg` - Санкт-Петербург
- `blagoveshchensk` - Благовещенск
- `ekaterinburg` - Екатеринбург
- `novosibirsk` - Новосибирск
- `kazan` - Казань

## Настройка платформ

В node "Config" измените массив `platforms`:
```javascript
// Все платформы
['cian', 'yandex', 'avito']

// Только Cian
['cian']

// Cian + Yandex
['cian', 'yandex']
```

## Ограничения Firecrawl

⚠️ **Стоимость**: Firecrawl - платный сервис
- **Free tier**: 500 requests/месяц
- **Starter**: $20/мес - 5,000 requests
- **Pro**: $100/мес - 50,000 requests

**Расчет для этого workflow:**
- 3 платформы × 20 объявлений/платформа = 60 объявлений
- 60 × 4 запроса (1 список + 1 детали на объявление) = 240 запросов
- 240 запросов × 20 запусков/час × 24 часа = **115,200 запросов/день** 💸

### Рекомендации по экономии:

1. **Увеличьте интервал**: с 3 минут до 15-30 минут
2. **Уменьшите количество объявлений**: в "Extract Listings" измените `.slice(0, 10)` на `.slice(0, 5)`
3. **Используйте бесплатное решение**: Flask API + BeautifulSoup (без Firecrawl)

## Бесплатная альтернатива

Если Firecrawl дорого, используйте мое решение:
- **Файл**: `/home/user/2026/rental_parser_full_workflow.json`
- **Гайд**: `/home/user/2026/FULL_WORKFLOW_GUIDE.md`
- **Стоимость**: 0₽ (без платных API)

## Тестирование

1. Откройте workflow
2. Нажмите **Execute Workflow** (вручную)
3. Проверьте Output каждого node
4. Убедитесь что сообщения пришли в Telegram
5. Активируйте workflow (переключатель вверху)

## Troubleshooting

### Ошибка "Bad request" в Telegram

**Причина**: Неправильный формат данных или отсутствует Chat ID

**Решение**:
1. Проверьте Chat ID в node "Send to Telegram"
2. Убедитесь что бот добавлен в чат
3. Проверьте Telegram credentials

### Firecrawl возвращает пустой ответ

**Причина**: Сайт заблокировал Firecrawl или требует авторизацию

**Решение**:
1. Проверьте URL в браузере
2. Увеличьте `waitFor` до 5000-10000ms
3. Добавьте cookies в Firecrawl запрос

### Дублируются объявления

**Причина**: База данных SQLite не подключена или не создана

**Решение**:
1. Проверьте путь к БД: `/home/user/2026/rental_parser.db`
2. Пересоздайте таблицу (см. Шаг 1)
3. Проверьте credentials в SQLite nodes

### Нет телефонов в объявлениях

**Причина**: Сайты прячут телефоны за кнопкой "Показать телефон"

**Решение**:
- Используйте мое Flask API решение с полноценным парсером
- Или используйте Firecrawl с `actions` для клика на кнопку (платная функция)

## Поддержка

Если есть вопросы:
1. Проверьте логи в Output каждого node
2. Убедитесь что Firecrawl ключ валиден
3. Проверьте лимиты Firecrawl аккаунта
