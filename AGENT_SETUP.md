# 🤖 Автономный Python Агент - Полное Решение

## ✨ Что это?

**Standalone Python Agent** - это полностью автономное решение для парсинга аренды квартир, которое:

- ✅ **Работает без n8n** - простой Python процесс
- ✅ **Автоматический парсинг** - каждые 4 часа (настраивается)
- ✅ **Автоматическая отправка в Telegram** - новые объявления сразу менеджерам
- ✅ **Автонабор телефонов** - интеграция с Asterisk/Twilio/webhook
- ✅ **Дедупликация** - отправляет каждое объявление только один раз
- ✅ **Логирование** - полные логи всех операций
- ✅ **Системный сервис** - работает в фоне автоматически

---

## 🚀 Быстрый старт (10 минут)

### Шаг 1: Установка зависимостей

```bash
cd /home/user/2026/rental_parser

# Установите все зависимости
pip install -r requirements.txt
```

### Шаг 2: Настройка конфигурации

```bash
# Создайте .env файл из примера
cp .env.example .env

# Отредактируйте конфигурацию
nano .env
```

**Минимальная конфигурация в `.env`:**

```bash
# ОБЯЗАТЕЛЬНЫЕ параметры
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz  # От @BotFather
TELEGRAM_CHAT_IDS=123456789,987654321  # Ваши chat ID (через запятую)

# Опциональные (есть значения по умолчанию)
CITY=москва
PARSE_INTERVAL_HOURS=4
MAX_PAGES=5
AUTO_DIAL_ENABLED=true
DIALER_BACKEND=mock  # mock/webhook/asterisk/twilio
```

**Как получить Telegram Bot Token:**
1. Напишите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен

**Как узнать Chat ID:**
1. Напишите [@userinfobot](https://t.me/userinfobot) в Telegram
2. Скопируйте ваш ID
3. Для нескольких менеджеров - укажите через запятую

### Шаг 3: Запуск агента

```bash
cd /home/user/2026/rental_parser

# Запуск через скрипт (рекомендуется)
./start_agent.sh

# Или напрямую через Python
python3 agent.py
```

**Вывод при запуске:**

```
=====================================
  Rental Parser Agent - Startup
=====================================

✓ Python 3 found: Python 3.10.0
✓ .env configuration found
✓ All dependencies installed
✓ Telegram configuration OK
✓ Database found: rental_parser.db

=====================================
  Starting Agent
=====================================

Configuration:
  City: москва
  Parse interval: 4 hours
  Max pages: 5 per platform
  Auto-dial: true
  Dialer backend: mock

Press Ctrl+C to stop

============================================================
RENTAL PARSER AGENT STARTED
============================================================
Schedule: Every 4 hours
Next run: 2026-01-18 14:00:00
============================================================

Running initial cycle...
============================================================
STARTING FULL PARSING CYCLE
============================================================
Starting parsing: cian
cian: Found 50 listings, 12 new
Starting parsing: yandex
yandex: Found 45 listings, 8 new
Starting parsing: avito
avito: Found 38 listings, 5 new
============================================================
PARSING COMPLETED: 25 new listings total
Stats: {'cian': 12, 'yandex': 8, 'avito': 5}
============================================================

Fetching up to 20 unsent listings...
Found 25 unsent listings, sending to Telegram...
Sent listing 1 (cian)
Auto-dialed: +79991234567
Sent listing 2 (yandex)
...
Successfully sent 20/25 listings
============================================================
CYCLE COMPLETED: Parsed 25 new, sent 20
============================================================
```

### Шаг 4: Проверка в Telegram

Откройте Telegram - должны прийти сообщения с новыми объявлениями! ✅

---

## 🔧 Настройка автонабора

Агент поддерживает автоматический набор номеров при отправке объявления менеджеру.

### Вариант 1: Mock режим (для тестирования)

```bash
# В .env
DIALER_BACKEND=mock
AUTO_DIAL_ENABLED=true
```

Логи покажут: `[MOCK] Would dial +79991234567` - реальных звонков не будет.

### Вариант 2: Webhook

Если у вас есть система телефонии с HTTP API:

```bash
# В .env
DIALER_BACKEND=webhook
DIALER_WEBHOOK_URL=https://your-telephony.com/api/dial
AUTO_DIAL_ENABLED=true
```

Агент отправит POST запрос:

```json
{
  "phone": "+79991234567",
  "listing_url": "https://cian.ru/rent/123456",
  "listing_id": 42
}
```

### Вариант 3: Asterisk AMI

Для интеграции с Asterisk PBX:

```bash
# В .env
DIALER_BACKEND=asterisk
ASTERISK_HOST=192.168.1.100
ASTERISK_PORT=5038
ASTERISK_USER=admin
ASTERISK_PASSWORD=secret123
AUTO_DIAL_ENABLED=true
```

**Установка библиотеки:**

```bash
pip install asterisk.ami
```

### Вариант 4: Twilio

Для облачной телефонии через Twilio:

```bash
# В .env
DIALER_BACKEND=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+15551234567
AUTO_DIAL_ENABLED=true
```

**Установка библиотеки:**

```bash
pip install twilio
```

---

## 📊 Запуск как системный сервис

Для автоматического запуска при старте системы используйте systemd.

### Установка сервиса:

```bash
# Скопируйте файл сервиса
sudo cp /home/user/2026/rental_parser/rental-agent.service /etc/systemd/system/

# Перезагрузите systemd
sudo systemctl daemon-reload

# Запустите сервис
sudo systemctl start rental-agent

# Проверьте статус
sudo systemctl status rental-agent

# Включите автозапуск при старте системы
sudo systemctl enable rental-agent
```

### Управление сервисом:

```bash
# Запуск
sudo systemctl start rental-agent

# Остановка
sudo systemctl stop rental-agent

# Перезапуск
sudo systemctl restart rental-agent

# Статус
sudo systemctl status rental-agent

# Логи в реальном времени
sudo journalctl -u rental-agent -f

# Логи за последний час
sudo journalctl -u rental-agent --since "1 hour ago"

# Все логи
sudo journalctl -u rental-agent
```

### Проверка работы:

```bash
# Статус должен показывать "active (running)"
sudo systemctl status rental-agent

# Вывод:
● rental-agent.service - Rental Parser Agent - Automatic apartment parser
     Loaded: loaded (/etc/systemd/system/rental-agent.service; enabled)
     Active: active (running) since Sat 2026-01-18 10:00:00 UTC; 2h ago
   Main PID: 12345 (python3)
      Tasks: 2 (limit: 4915)
     Memory: 85.2M
```

---

## 🔍 Логирование

Агент ведет подробные логи всех операций.

### Файловые логи:

```bash
# Просмотр логов
tail -f /home/user/2026/rental_parser/rental_agent.log

# Последние 100 строк
tail -n 100 rental_agent.log

# Поиск ошибок
grep ERROR rental_agent.log

# Поиск по платформе
grep "cian" rental_agent.log
```

### Системные логи (если запущен как сервис):

```bash
# Все логи
sudo journalctl -u rental-agent

# Последние 50 строк
sudo journalctl -u rental-agent -n 50

# В реальном времени
sudo journalctl -u rental-agent -f

# Только ошибки
sudo journalctl -u rental-agent -p err

# За последние 2 часа
sudo journalctl -u rental-agent --since "2 hours ago"
```

---

## ⚙️ Настройка параметров

Все параметры настраиваются через `.env` файл:

### Основные параметры:

| Параметр | Значение по умолчанию | Описание |
|----------|----------------------|----------|
| `CITY` | `москва` | Город для парсинга |
| `PARSE_INTERVAL_HOURS` | `4` | Интервал парсинга (часы) |
| `MAX_PAGES` | `5` | Макс страниц на платформу |
| `DB_PATH` | `rental_parser.db` | Путь к базе данных |

### Telegram:

| Параметр | Обязательный | Описание |
|----------|--------------|----------|
| `TELEGRAM_BOT_TOKEN` | ✅ Да | Токен от @BotFather |
| `TELEGRAM_CHAT_IDS` | ✅ Да | Chat ID через запятую |

### Автонабор:

| Параметр | Значение | Описание |
|----------|----------|----------|
| `AUTO_DIAL_ENABLED` | `true`/`false` | Включить автонабор |
| `DIALER_BACKEND` | `mock`/`webhook`/`asterisk`/`twilio` | Тип системы |

---

## 📈 Мониторинг

### Проверка что агент работает:

```bash
# Проверка процесса
ps aux | grep agent.py

# Должен показать:
# root  12345  0.5  1.2  123456  78910 ?  Ss  10:00  0:05 python3 agent.py
```

### Проверка последнего парсинга:

```bash
# Смотрим логи
tail -n 50 rental_agent.log | grep "CYCLE COMPLETED"

# Вывод:
# 2026-01-18 10:00:00 - CYCLE COMPLETED: Parsed 25 new, sent 20
# 2026-01-18 14:00:00 - CYCLE COMPLETED: Parsed 12 new, sent 12
```

### Проверка базы данных:

```bash
cd /home/user/2026/rental_parser

# Количество всего объявлений
python3 -c "from database.models import init_db; db = init_db(); print('Total:', db.query('SELECT COUNT(*) FROM rental_listings').fetchone()[0])"

# Количество отправленных
python3 -c "from database.models import init_db; db = init_db(); print('Sent:', db.query('SELECT COUNT(*) FROM rental_listings WHERE sent_to_manager=1').fetchone()[0])"

# Количество неотправленных
python3 -c "from database.models import init_db, get_unsent_listings; db = init_db(); print('Unsent:', len(get_unsent_listings(db, limit=999)))"
```

---

## 🐛 Решение проблем

### ❌ Агент не запускается

```bash
# Проверьте зависимости
pip install -r requirements.txt

# Проверьте .env файл
cat .env | grep TELEGRAM_BOT_TOKEN

# Запустите с выводом ошибок
python3 agent.py
```

### ❌ Не приходят сообщения в Telegram

```bash
# Проверьте конфигурацию
cat .env | grep TELEGRAM

# Проверьте что бот имеет доступ
# Напишите боту /start в Telegram

# Тест отправки
python3 -c "
from telegram_sender import TelegramSender
import os
from dotenv import load_dotenv
load_dotenv()
sender = TelegramSender(os.getenv('TELEGRAM_BOT_TOKEN'), os.getenv('TELEGRAM_CHAT_IDS').split(','))
print('Testing connection...')
if sender.test_connection():
    print('✓ Bot OK')
    sender.send_notification('Test message from agent')
    print('✓ Message sent')
"
```

### ❌ Не находит новые объявления

```bash
# Проверьте парсинг вручную
cd /home/user/2026/rental_parser
python3 main.py --max-pages 1

# Если ошибка - проверьте прокси
# Если сайты банят - настройте прокси в proxies.txt
```

### ❌ Дублируются объявления

```bash
# Проверьте что база данных не повреждена
cd /home/user/2026/rental_parser
python3 -c "from database.models import init_db; db = init_db(); print('DB OK')"

# Проверьте уникальные constraint
python3 -c "
from database.models import init_db
db = init_db()
result = db.query('SELECT COUNT(*), COUNT(DISTINCT listing_id) FROM rental_listings').fetchone()
print(f'Total: {result[0]}, Unique: {result[1]}')
"
```

### ❌ Агент падает

```bash
# Смотрим логи ошибок
grep -A 5 "ERROR" rental_agent.log

# Или в systemd логах
sudo journalctl -u rental-agent -p err

# Увеличиваем уровень логирования
# В .env добавьте:
LOG_LEVEL=DEBUG

# Перезапустите агента
```

---

## 🔄 Обновление

### Обновление кода:

```bash
cd /home/user/2026/rental_parser

# Остановите агента
sudo systemctl stop rental-agent

# Обновите код (если используете git)
git pull

# Обновите зависимости
pip install -r requirements.txt --upgrade

# Запустите агента
sudo systemctl start rental-agent
```

### Миграция базы данных:

```bash
# Бэкап текущей базы
cp rental_parser.db rental_parser.db.backup

# Если нужно пересоздать структуру
python3 -c "from database.models import init_db, create_tables; db = init_db(); create_tables(db)"
```

---

## 📊 Архитектура решения

```
┌─────────────────────────────────────────┐
│         Rental Parser Agent             │
│         (agent.py)                      │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Scheduler (schedule library)    │   │
│  │ Every 4 hours                   │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐   │
│  │ Parse All Platforms             │   │
│  │  - Cian Parser                  │   │
│  │  - Yandex Parser                │   │
│  │  - Avito Parser                 │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐   │
│  │ SQLite Database                 │   │
│  │ Deduplication by listing_id     │   │
│  │ sent_to_manager flag            │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐   │
│  │ Get Unsent Listings (limit 20)  │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐   │
│  │ Telegram Sender                 │   │
│  │ (telegram_sender.py)            │   │
│  │ Send to all chat_ids            │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐   │
│  │ Auto Dialer (optional)          │   │
│  │ (auto_dial.py)                  │   │
│  │ Webhook/Asterisk/Twilio/Mock    │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐   │
│  │ Mark as Sent                    │   │
│  │ Update database                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Wait 4 hours and repeat...             │
└─────────────────────────────────────────┘
```

---

## ✅ Преимущества автономного агента

| Преимущество | Описание |
|--------------|----------|
| ✅ **Простота** | Один Python процесс, никаких внешних зависимостей |
| ✅ **Независимость** | Не нужен n8n, работает автономно |
| ✅ **Надежность** | Автоматический перезапуск через systemd |
| ✅ **Логирование** | Подробные логи всех операций |
| ✅ **Гибкость** | Настройка через .env, легко менять параметры |
| ✅ **Автонабор** | Встроенная поддержка разных телефонных систем |
| ✅ **Мониторинг** | Легко отслеживать через journalctl |

---

## 🎯 Чек-лист установки

- [ ] Python 3 установлен (`python3 --version`)
- [ ] Зависимости установлены (`pip install -r requirements.txt`)
- [ ] Создан `.env` файл из `.env.example`
- [ ] `TELEGRAM_BOT_TOKEN` настроен
- [ ] `TELEGRAM_CHAT_IDS` настроен
- [ ] Тестовый запуск выполнен (`./start_agent.sh`)
- [ ] Сообщения приходят в Telegram
- [ ] (Опционально) Systemd сервис настроен
- [ ] (Опционально) Автонабор настроен
- [ ] Логи пишутся корректно
- [ ] Агент работает в фоне

---

## 📚 Дополнительная информация

### Файлы агента:

| Файл | Назначение |
|------|-----------|
| `agent.py` | Основной агент с расписанием |
| `telegram_sender.py` | Модуль отправки в Telegram |
| `auto_dial.py` | Модуль автонабора |
| `start_agent.sh` | Скрипт запуска |
| `rental-agent.service` | Systemd сервис |
| `.env` | Конфигурация (создать из .env.example) |
| `rental_agent.log` | Файл логов |

### Связанные руководства:

- **Основная документация:** [README.md](rental_parser/README.md)
- **API решение:** [API_SOLUTION.md](API_SOLUTION.md)
- **Firebase версия:** [FIREBASE_SETUP.md](FIREBASE_SETUP.md)
- **n8n интеграция:** [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)

---

## 🚀 Готово!

Теперь у вас есть **полностью автономный Python агент**, который:

1. ✅ Парсит 3 платформы каждые 4 часа
2. ✅ Автоматически отправляет новые объявления в Telegram
3. ✅ Не дублирует отправки
4. ✅ Поддерживает автонабор телефонов
5. ✅ Работает как системный сервис
6. ✅ Ведет подробные логи

**Это самое простое и надежное решение!** 🎉

Не нужен n8n, не нужны Execute Command ноды - только Python! ✨
