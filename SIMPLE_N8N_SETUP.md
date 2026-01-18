# 🚀 Простая установка в n8n (Code Node)

## ✨ Что это?

Простое решение для запуска парсера из n8n через **Python Code Node**.

**Преимущества:**
- ✅ Один скрипт `run_once.py` - парсит и отправляет всё сразу
- ✅ Работает через Code node в n8n (не нужны Execute Command ноды)
- ✅ Простой workflow - всего 3 ноды
- ✅ Автоматический запуск каждые 4 часа
- ✅ Автонабор телефонов встроен (webhook/Asterisk/Twilio)
- ✅ Можно запускать вручную для тестирования

---

## 📦 Установка (5 минут)

### Шаг 1: Установите зависимости

```bash
cd /home/user/2026/rental_parser

# Установите все зависимости
pip install -r requirements.txt
```

### Шаг 2: Настройте конфигурацию

```bash
# Создайте .env файл
cp .env.example .env

# Отредактируйте конфигурацию
nano .env
```

**Минимальная конфигурация в `.env`:**

```bash
# ОБЯЗАТЕЛЬНЫЕ параметры
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_IDS=123456789,987654321

# Опциональные
CITY=москва
MAX_PAGES=5
SEND_LIMIT=20

# Автонабор (опционально)
AUTO_DIAL_ENABLED=true  # true/false
DIALER_BACKEND=mock  # mock/webhook/asterisk/twilio
```

### Шаг 3: Протестируйте скрипт

Перед добавлением в n8n, проверьте что скрипт работает:

```bash
cd /home/user/2026/rental_parser

# Запустите скрипт
python3 run_once.py
```

**Вы должны увидеть:**

```
============================================================
RENTAL PARSER - ONE TIME RUN
============================================================

City: москва
Max pages: 5
Send limit: 20

============================================================
STARTING PARSING
============================================================
Parsing cian...
cian: Found 50, new 12
Parsing yandex...
yandex: Found 45, new 8
Parsing avito...
avito: Found 38, new 5
============================================================
PARSING COMPLETED: 25 new listings
============================================================

============================================================
SENDING TO TELEGRAM
============================================================
Auto-dial enabled: mock
Found 25 unsent listings
Sent listing 1 (cian)
Auto-dialed: +79991234567
Sent listing 2 (yandex)
Auto-dialed: +79997654321
...
============================================================
SENDING COMPLETED: 20 sent, 0 failed
============================================================

============================================================
RESULTS:
============================================================
{
  "success": true,
  "timestamp": "2026-01-18T10:00:00.000000",
  "parsing": {
    "cian": {"found": 50, "new": 12},
    "yandex": {"found": 45, "new": 8},
    "avito": {"found": 38, "new": 5}
  },
  "sending": {
    "sent": 20,
    "failed": 0
  },
  "summary": {
    "total_new": 25,
    "total_sent": 20
  }
}
============================================================
```

✅ Если видите такой вывод - всё работает!

### Шаг 4: Импортируйте workflow в n8n

1. Откройте n8n в браузере
2. Нажмите **"+"** (создать новый workflow)
3. Нажмите **три точки (⋮)** → **"Import from File"**
4. Выберите файл: `/home/user/2026/rental_parser_simple_workflow.json`
5. Нажмите **"Import"**

### Шаг 5: Проверьте настройки

В импортированном workflow проверьте:

**1. Code Node "Run Parser Script":**
- Должен быть установлен Python
- Путь к скрипту: `/home/user/2026/rental_parser/run_once.py`

**2. Schedule Node "Every 4 Hours":**
- Интервал: каждые 4 часа (можно изменить)

### Шаг 6: Тестовый запуск

1. В n8n нажмите **"Execute Workflow"** (кнопка внизу)
2. Подождите выполнения (может занять 1-2 минуты)
3. Все ноды должны стать зелеными ✅
4. В Telegram должны прийти новые объявления!

### Шаг 7: Активируйте workflow

1. Нажмите переключатель **"Active"** вверху справа
2. Теперь парсер будет запускаться автоматически каждые 4 часа!

---

## 📊 Структура workflow

```
┌─────────────────────┐
│  Every 4 Hours      │  ← Schedule Trigger (каждые 4 часа)
│  (Schedule)         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Run Parser Script  │  ← Python Code Node (запускает run_once.py)
│  (Code Node)        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Format Summary     │  ← Форматирует результат
│  (Set Node)         │
└─────────────────────┘
```

**Что происходит:**
1. **Schedule** - каждые 4 часа запускает workflow
2. **Code Node** - запускает `python3 run_once.py`, который:
   - Парсит Cian, Yandex, Avito
   - Сохраняет в БД
   - Отправляет новые объявления в Telegram
3. **Format Summary** - форматирует результат для просмотра в n8n

---

## 🎯 Альтернативные варианты запуска

### Вариант 1: Ручной запуск

Просто запустите скрипт когда нужно:

```bash
cd /home/user/2026/rental_parser
python3 run_once.py
```

### Вариант 2: Cron (системное расписание)

Добавьте в crontab для запуска каждые 4 часа:

```bash
# Откройте crontab
crontab -e

# Добавьте строку (запуск каждые 4 часа)
0 */4 * * * cd /home/user/2026/rental_parser && python3 run_once.py >> /var/log/rental_parser.log 2>&1
```

### Вариант 3: n8n Webhook

Запуск через HTTP запрос (можно вызвать из любого места):

1. В n8n добавьте **Webhook Trigger** вместо Schedule
2. Настройте webhook URL
3. Вызывайте парсер через `curl`:

```bash
curl -X POST https://your-n8n.com/webhook/rental-parser
```

---

## 📞 Настройка автонабора

Скрипт **автоматически набирает номер телефона** сразу после отправки объявления менеджеру в Telegram.

### По умолчанию (Mock режим)

```bash
# В .env
AUTO_DIAL_ENABLED=true
DIALER_BACKEND=mock
```

Логи покажут: `Auto-dialed: +79991234567` но реальных звонков не будет (для тестирования).

### Webhook интеграция

Если у вас есть система телефонии с HTTP API:

```bash
# В .env
AUTO_DIAL_ENABLED=true
DIALER_BACKEND=webhook
DIALER_WEBHOOK_URL=https://your-telephony.com/api/dial
```

При каждом объявлении будет POST запрос:

```json
{
  "phone": "+79991234567",
  "listing_url": "https://cian.ru/rent/123456",
  "listing_id": 42
}
```

### Asterisk AMI

Для интеграции с Asterisk PBX:

```bash
# В .env
AUTO_DIAL_ENABLED=true
DIALER_BACKEND=asterisk
ASTERISK_HOST=192.168.1.100
ASTERISK_PORT=5038
ASTERISK_USER=admin
ASTERISK_PASSWORD=secret123
```

Установите библиотеку: `pip install asterisk.ami`

### Twilio

Для облачной телефонии:

```bash
# В .env
AUTO_DIAL_ENABLED=true
DIALER_BACKEND=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+15551234567
```

Установите библиотеку: `pip install twilio`

### Выключить автонабор

```bash
# В .env
AUTO_DIAL_ENABLED=false
```

---

## 🔧 Настройка параметров

### Изменить интервал парсинга:

В n8n откройте **Schedule node** → измените `hours: 4` на нужное значение.

### Изменить количество страниц для парсинга:

В `.env` файле:

```bash
MAX_PAGES=10  # Вместо 5
```

### Изменить лимит отправки в Telegram:

В `.env` файле:

```bash
SEND_LIMIT=50  # Вместо 20 за раз
```

### Изменить город:

В `.env` файле:

```bash
CITY=санкт-петербург  # или другой город
```

---

## 📱 Проверка работы

### В Telegram:

Должны приходить сообщения вида:

```
🔵 Cian

2-комн квартира в центре

💰 45 000 ₽
🏠 2-комн, 65 м²
📍 Москва, ул. Тверская, 10
📞 +79991234567

🔗 Открыть объявление
```

### В n8n:

1. Откройте workflow
2. Нажмите **"Executions"** (история выполнения)
3. Должны быть успешные выполнения (зеленые)

### В логах скрипта:

```bash
cd /home/user/2026/rental_parser

# Если запускали вручную
cat rental_agent.log

# Если через cron
cat /var/log/rental_parser.log
```

---

## 🐛 Решение проблем

### ❌ Code Node показывает ошибку "Python not found"

**Решение:** Установите Python в n8n:

```bash
# На сервере с n8n
apt install python3 python3-pip
```

Или измените в Code node путь:

```python
['python3', script_path]  # Попробуйте 'python' вместо 'python3'
```

### ❌ Скрипт не находит модули

**Решение:** Установите зависимости глобально или укажите путь к venv:

```bash
# Глобально
pip3 install -r requirements.txt

# Или создайте venv
cd /home/user/2026/rental_parser
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ Не приходят сообщения в Telegram

**Решение:** Проверьте настройки:

```bash
# Проверьте .env
cat .env | grep TELEGRAM

# Убедитесь что боту написали /start
# Проверьте Chat ID - должен быть верным
```

Тестовый запуск:

```bash
cd /home/user/2026/rental_parser
python3 -c "
from telegram_sender import TelegramSender
import os
from dotenv import load_dotenv
load_dotenv()
sender = TelegramSender(os.getenv('TELEGRAM_BOT_TOKEN'), os.getenv('TELEGRAM_CHAT_IDS').split(','))
print('Testing...')
if sender.test_connection():
    print('✓ Bot OK')
    sender.send_notification('Test message!')
"
```

### ❌ Дублируются объявления

**Решение:** Проверьте базу данных:

```bash
cd /home/user/2026/rental_parser

# Проверка дубликатов
python3 -c "
from database.models import init_db, RentalListing
db = init_db()
total = db.query(RentalListing).count()
unique = db.query(RentalListing.listing_id).distinct().count()
print(f'Total: {total}, Unique: {unique}')
if total > unique:
    print('WARNING: Duplicates found!')
"
```

---

## 📊 Мониторинг

### Проверить последний запуск:

```bash
cd /home/user/2026/rental_parser

# Если есть логи
tail -50 rental_agent.log | grep "RESULTS:"
```

### Статистика базы данных:

```bash
cd /home/user/2026/rental_parser

python3 -c "
from database.models import init_db, RentalListing, get_unsent_listings
db = init_db()
total = db.query(RentalListing).count()
sent = db.query(RentalListing).filter(RentalListing.sent_to_manager == True).count()
unsent = len(get_unsent_listings(db, limit=999))
print(f'Total listings: {total}')
print(f'Sent: {sent}')
print(f'Unsent: {unsent}')
"
```

---

## ✅ Чек-лист установки

- [ ] Python 3 установлен
- [ ] Зависимости установлены (`pip install -r requirements.txt`)
- [ ] Файл `.env` создан и настроен
- [ ] `TELEGRAM_BOT_TOKEN` указан
- [ ] `TELEGRAM_CHAT_IDS` указан
- [ ] Тестовый запуск успешен (`python3 run_once.py`)
- [ ] Сообщения приходят в Telegram
- [ ] Workflow импортирован в n8n
- [ ] Тестовый запуск в n8n успешен
- [ ] Workflow активирован (Active = ON)

---

## 🎉 Готово!

Теперь у вас работает **автоматический парсер квартир**, который:

1. ✅ Запускается каждые 4 часа через n8n
2. ✅ Парсит 3 платформы (Cian, Yandex, Avito)
3. ✅ Автоматически отправляет в Telegram
4. ✅ Не дублирует объявления
5. ✅ Возвращает подробную статистику

**Это самое простое решение для n8n!** 🚀

Вопросы? Смотрите также:
- **Автономный агент:** [AGENT_SETUP.md](AGENT_SETUP.md)
- **Flask API решение:** [API_SOLUTION.md](API_SOLUTION.md)
- **Основная документация:** [README.md](rental_parser/README.md)
