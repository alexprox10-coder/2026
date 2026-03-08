# Установка Telegram парсера

## Требования
- VPS: 1 CPU, 1-2 GB RAM
- Ubuntu 20.04/22.04
- Python 3.9+

---

## Шаг 1: Подготовка сервера

```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git -y
```

---

## Шаг 2: Клонирование проекта

```bash
cd /home/user
git clone <URL_РЕПОЗИТОРИЯ> 2026
cd 2026
```

---

## Шаг 3: Установка зависимостей

```bash
pip3 install telethon aiohttp beautifulsoup4 lxml fastapi uvicorn python-dotenv
```

Или через requirements:
```bash
pip3 install -r requirements_channel_finder.txt
```

---

## Шаг 4: Получение Telegram API ключей

1. Открой https://my.telegram.org/apps
2. Авторизуйся по номеру телефона
3. Создай приложение (любое название)
4. Скопируй **API_ID** и **API_HASH**

---

## Шаг 5: Настройка .env

```bash
cp .env.example .env
nano .env
```

Заполни:
```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+79001234567
```

---

## Шаг 6: Первый запуск (авторизация)

```bash
python3 telegram_parser_api.py
```

При первом запуске:
1. Введи код из Telegram
2. Если есть 2FA — введи пароль
3. Создастся файл сессии `.session`

**Не удаляй `.session` файл!** Иначе придётся авторизоваться заново.

---

## Шаг 7: Настройка автозапуска (systemd)

```bash
cp telegram-parser-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable telegram-parser-api
systemctl start telegram-parser-api
```

Проверка:
```bash
systemctl status telegram-parser-api
```

---

## Шаг 8: Проверка работы

```bash
curl http://localhost:8000/health
```

Должен вернуть `{"status": "ok"}`

---

## Полезные команды

```bash
# Логи в реальном времени
journalctl -u telegram-parser-api -f

# Или напрямую
tail -f /var/log/telegram-parser-api.log

# Перезапуск
systemctl restart telegram-parser-api

# Остановка
systemctl stop telegram-parser-api
```

---

## Частые проблемы

| Проблема | Решение |
|----------|---------|
| `PHONE_NUMBER_INVALID` | Формат: +79001234567 (с плюсом и кодом страны) |
| `SESSION_REVOKED` | Удали `.session` файл, авторизуйся заново |
| `FLOOD_WAIT_X` | Подожди X секунд, Telegram ограничил запросы |
| Порт 8000 занят | `lsof -i :8000` → `kill -9 <PID>` |
| Сервис не стартует | Проверь путь к Python: `which python3` |

---

## Интеграция с n8n (опционально)

1. Установи n8n: `npm install -g n8n`
2. Запусти: `npx n8n`
3. Открой http://localhost:5678
4. Импортируй `workflow_fixed.json`
5. В HTTP Request ноде укажи `http://localhost:8000/parse`
