# 📦 Руководство по импорту n8n Workflow

## 🔧 Доступные версии workflow

### 1. `rental_parser_unified_fixed.json` ⭐ (Рекомендуется)
**Упрощенная и рабочая версия**
- Запускает `main.py` который парсит все платформы
- Простая структура, легко отлаживать
- Все ноды правильно соединены
- Готов к работе сразу после импорта

### 2. `rental_parser_workflow.json`
Базовая версия с минимальным функционалом

---

## 🚀 Пошаговая инструкция по импорту

### Шаг 1: Подготовка

1. Убедитесь что n8n запущен:
   ```bash
   n8n start
   # Или через docker
   docker-compose up -d n8n
   ```

2. Откройте n8n в браузере:
   ```
   http://localhost:5678
   ```

### Шаг 2: Импорт workflow

1. В n8n нажмите кнопку **"+"** (создать workflow)
2. Нажмите **три точки** (⋮) в правом верхнем углу
3. Выберите **"Import from File..."**
4. Выберите файл `rental_parser_unified_fixed.json`
5. Нажмите **"Import"**

### Шаг 3: Настройка креденшиалов

#### 🔵 Telegram Bot

1. Откройте ноду **"📱 Send to Telegram"**
2. В поле **"Credential to connect with"** нажмите **"Create New"**
3. Введите ваш **Bot Token** от @BotFather
4. Нажмите **"Save"**
5. Повторите для нод:
   - **"📭 No Listings"**
   - **"✅ Completion Notice"**

#### 🟢 Google Sheets (опционально)

1. Откройте ноду **"💾 Google Sheets"**
2. В поле **"Credential to connect with"** нажмите **"Create New"**
3. Пройдите OAuth авторизацию
4. Выберите документ и лист
5. Нажмите **"Save"**

Если не используете Google Sheets - просто удалите или деактивируйте эту ноду.

### Шаг 4: Настройка переменных окружения

В n8n перейдите в **Settings → Environment Variables** и добавьте:

```env
TELEGRAM_CHAT_ID=123456789
GOOGLE_SHEET_ID=your_sheet_id_here
AUTO_DIAL_WEBHOOK_URL=https://your-telephony.com/webhook
```

#### Как узнать TELEGRAM_CHAT_ID:

**Вариант 1: Через бота @userinfobot**
1. Откройте Telegram
2. Найдите [@userinfobot](https://t.me/userinfobot)
3. Нажмите **Start**
4. Скопируйте ваш **Id** (например: `123456789`)

**Вариант 2: Через API**
1. Напишите что-то вашему боту
2. Откройте в браузере:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Найдите `"chat":{"id":123456789}`

### Шаг 5: Проверка путей к файлам

Во всех нодах **Execute Command** проверьте пути:

```bash
# Должно быть
cd /home/user/2026/rental_parser && python3 main.py

# Если ваш путь другой, измените на
cd /path/to/your/rental_parser && python3 main.py
```

### Шаг 6: Тестирование

1. Нажмите **"Execute Workflow"** (кнопка со стрелкой вниз)
2. Выберите **"Manual"**
3. Нажмите **"Execute Workflow"**
4. Наблюдайте за выполнением каждой ноды

Если все зеленое ✅ - workflow работает!

### Шаг 7: Активация

1. Включите переключатель **"Active"** в правом верхнем углу
2. Workflow будет запускаться автоматически каждые 4 часа

---

## 🔍 Описание нод

### 📋 Основной поток

| Нода | Тип | Описание |
|------|-----|----------|
| ⏰ Schedule Every 4h | Schedule Trigger | Запуск каждые 4 часа |
| 🏠 Run Parser | Execute Command | Парсит все 3 платформы |
| 📞 Extract Phones | Execute Command | Извлекает телефоны |
| 📋 Get Unsent Listings | Execute Command | Получает неотправленные |
| Parse JSON Output | Code | Парсит JSON в массив |
| ✅ Has Listings? | IF | Проверка наличия объявлений |
| ✍️ Format Message | Code | Форматирует сообщение |
| 📱 Send to Telegram | Telegram | Отправка в Telegram |
| ⏳ Wait 3s | Wait | Задержка 3 секунды |
| 📞 Has Phone? | IF | Проверка наличия телефона |
| 📞 Auto-Dial Webhook | HTTP Request | Webhook для автодозвона |
| ✔️ Mark as Sent | Execute Command | Помечает как отправленное |
| 💾 Google Sheets | Google Sheets | Сохранение в таблицу |

### 🔄 Альтернативный поток

| Нода | Тип | Описание |
|------|-----|----------|
| 📭 No Listings | Telegram | Уведомление "Нет новых" |

### 🔧 Ручной запуск

| Нода | Тип | Описание |
|------|-----|----------|
| 🔧 Manual Webhook | Webhook | Webhook для ручного запуска |
| 📤 Webhook Response | Respond to Webhook | Ответ на webhook |
| 📊 Get Stats | Execute Command | Статистика БД |
| ✅ Completion Notice | Telegram | Уведомление о завершении |

---

## ⚙️ Настройка параметров

### Изменить частоту парсинга

В ноде **"⏰ Schedule Every 4h"**:

```json
// Каждые 2 часа
"hoursInterval": 2

// Каждые 6 часов
"hoursInterval": 6

// Каждый день в 9:00
"cronExpression": "0 9 * * *"
```

### Изменить количество страниц

В ноде **"🏠 Run Parser"**:

```bash
# Было
python3 main.py --max-pages 5

# Меньше нагрузки (3 страницы)
python3 main.py --max-pages 3

# Больше объявлений (10 страниц)
python3 main.py --max-pages 10
```

### Парсить только определенные платформы

В ноде **"🏠 Run Parser"**:

```bash
# Только Cian
python3 main.py --platforms cian --max-pages 5

# Только Cian и Yandex
python3 main.py --platforms cian yandex --max-pages 5

# Все платформы (по умолчанию)
python3 main.py --platforms cian yandex avito --max-pages 5
```

### Изменить город

В ноде **"🏠 Run Parser"**:

```bash
python3 main.py --city санкт-петербург --max-pages 5
```

### Изменить лимит отправки

В ноде **"📋 Get Unsent Listings"** замените `limit=20` на нужное значение:

```python
# Было
get_unsent_listings(db, limit=20)

# Отправлять по 10
get_unsent_listings(db, limit=10)

# Отправлять по 50
get_unsent_listings(db, limit=50)
```

### Добавить прокси

В ноде **"🏠 Run Parser"**:

```bash
python3 main.py --max-pages 5 --proxy-file /path/to/proxies.txt
```

---

## 🐛 Решение проблем

### ❌ Ошибка "Command not found: python3"

**Решение:** Измените `python3` на `python` во всех Execute Command нодах:

```bash
# Было
python3 main.py

# Стало
python main.py
```

### ❌ Ошибка "No module named 'parsers'"

**Решение:** Проверьте путь к проекту и установите зависимости:

```bash
cd /home/user/2026/rental_parser
pip install -r requirements.txt
```

### ❌ Ошибка "TELEGRAM_CHAT_ID is not defined"

**Решение:**
1. Перейдите в **Settings → Environment Variables**
2. Добавьте переменную `TELEGRAM_CHAT_ID`
3. Перезапустите workflow

### ❌ Ноды не соединены

**Решение:**
1. Удалите текущий workflow
2. Импортируйте заново `rental_parser_unified_fixed.json`
3. Убедитесь что все connections установлены

### ❌ Ошибка "Database is locked"

**Решение:** SQLite не поддерживает параллельные записи:
1. Убедитесь что не запущено несколько workflow одновременно
2. Или переключитесь на PostgreSQL

### ❌ Парсер не находит объявления

**Решение:**
1. Проверьте интернет соединение
2. Запустите вручную: `python3 main.py --max-pages 1`
3. Проверьте логи: `cat logs/parser.log`
4. Добавьте прокси если нужно

---

## 🔐 Безопасность

### Защита креденшиалов

- ✅ Все токены хранятся в n8n Credentials (зашифрованы)
- ✅ Используйте Environment Variables для чувствительных данных
- ❌ НЕ храните токены в коде нод

### Защита Webhook

Добавьте аутентификацию к webhook:

1. Откройте ноду **"🔧 Manual Webhook"**
2. В разделе **"Authentication"** выберите **"Header Auth"**
3. Задайте имя заголовка: `X-Api-Key`
4. Задайте значение: `your_secret_key`

Теперь для запуска нужен заголовок:
```bash
curl -X POST \
  -H "X-Api-Key: your_secret_key" \
  https://your-n8n.com/webhook/rental-manual
```

---

## 📊 Мониторинг

### Просмотр истории выполнений

1. В n8n перейдите в **"Executions"** (левое меню)
2. Выберите ваш workflow
3. Смотрите все запуски с деталями

### Настройка уведомлений об ошибках

Добавьте ноду **Error Trigger**:

1. Добавьте новую ноду: **Error Trigger**
2. Подключите к ней **Telegram** ноду
3. Настройте сообщение об ошибке

Теперь при ошибке вы получите уведомление в Telegram!

---

## 🚀 Ручной запуск через Webhook

### Получить URL

1. Откройте ноду **"🔧 Manual Webhook"**
2. Нажмите **"Copy Test URL"** или **"Copy Production URL"**
3. URL примерно: `https://your-n8n.com/webhook/rental-manual`

### Запустить

```bash
# Простой запуск
curl -X POST https://your-n8n.com/webhook/rental-manual

# С аутентификацией
curl -X POST \
  -H "X-Api-Key: your_secret_key" \
  https://your-n8n.com/webhook/rental-manual

# С параметрами (если настроено)
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["cian", "yandex"], "max_pages": 3}' \
  https://your-n8n.com/webhook/rental-manual
```

### Ответ

```json
{
  "success": true,
  "message": "Parser started",
  "time": "2026-01-17T14:35:22.000Z"
}
```

---

## 📚 Дополнительные ресурсы

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Credentials](https://docs.n8n.io/credentials/)
- [n8n Execute Command Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)
- [n8n Code Node](https://docs.n8n.io/code/builtin/code/)

---

## ✅ Чек-лист готовности

Перед активацией убедитесь:

- [ ] n8n запущен и доступен
- [ ] Workflow импортирован
- [ ] Telegram credentials настроены
- [ ] Environment Variables установлены (`TELEGRAM_CHAT_ID`)
- [ ] Пути к файлам правильные
- [ ] Тестовый запуск прошел успешно
- [ ] Получены тестовые сообщения в Telegram
- [ ] Workflow активирован (переключатель "Active")

---

**Готово!** Ваш rental parser теперь работает автоматически 🎉
