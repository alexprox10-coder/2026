# 🌐 API РЕШЕНИЕ - Работает 100%!

## ✅ Почему это работает:

Execute Command ноды **НЕ РАБОТАЮТ** в вашей версии n8n.

**РЕШЕНИЕ:** Использовать Flask API + HTTP Request ноды!

---

## 🚀 Установка (10 минут)

### Шаг 1: Установите зависимости

```bash
cd /home/user/2026/rental_parser

# Установите все зависимости
pip install -r requirements.txt
pip install Flask==3.0.0
```

### Шаг 2: Запустите API сервер

```bash
cd /home/user/2026/rental_parser

# Запустите сервер (он будет работать постоянно)
python3 api_server.py
```

Вы увидите:
```
Starting Rental Parser API...
API will be available at: http://localhost:5555

Endpoints:
  GET  /health - Health check
  POST /parse - Run parser
  GET  /unsent?limit=20 - Get unsent listings
  POST /mark-sent/<id> - Mark listing as sent
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5555
```

**Не закрывайте этот терминал!** Сервер должен работать постоянно.

### Шаг 3: Проверьте что API работает

Откройте **новый терминал** и выполните:

```bash
# Проверка health
curl http://localhost:5555/health

# Должно вывести: {"status":"ok"}
```

Если вывело `{"status":"ok"}` → API работает! ✅

### Шаг 4: Импортируйте workflow в n8n

1. В n8n нажмите **"+"** (новый workflow)
2. Три точки (⋮) → **"Import from File"**
3. Выберите: **`rental_parser_api.json`**
4. Нажмите **"Import"**

### Шаг 5: Настройте Telegram

1. Откройте ноду **"Telegram"**
2. Credentials → выберите существующий или создайте новый
3. В n8n: **Settings → Variables → Environment Variables**
4. Добавьте: `TELEGRAM_CHAT_ID` = `ваш_id`

### Шаг 6: Тестовый запуск

1. В workflow нажмите **"Execute Workflow"**
2. Выберите **"Manual execution"**
3. Нажмите **"Execute Workflow"**

**Все ноды должны стать ЗЕЛЕНЫМИ!** ✅

Если зеленые - проверьте Telegram, должно прийти сообщение.

### Шаг 7: Активируйте workflow

Нажмите переключатель **"Active"** - готово! 🎉

---

## 📊 Структура API решения

```
Flask API Server (постоянно работает на порту 5555)
    ↕️ HTTP
n8n Workflow (вызывает API через HTTP Request ноды)
```

### Преимущества:

- ✅ HTTP Request ноды работают везде
- ✅ API можно тестировать отдельно
- ✅ Никаких проблем с Execute Command
- ✅ Легко отлаживать
- ✅ Можно использовать из других приложений

---

## 🔍 Как работает workflow

```
1. Schedule Every 4h
   ↓ Запускается каждые 4 часа

2. Run Parser (HTTP Request)
   ↓ POST http://localhost:5555/parse
   ↓ API запускает парсинг

3. Get Unsent (HTTP Request)
   ↓ GET http://localhost:5555/unsent?limit=20
   ↓ API возвращает JSON массив

4. Split Items (Code)
   ↓ Разбивает массив на отдельные элементы

5. Format (Code)
   ↓ Форматирует сообщение для Telegram

6. Telegram
   ↓ Отправляет сообщение

7. Wait
   ↓ Ждёт 3 секунды

8. Mark Sent (HTTP Request)
   ↓ POST http://localhost:5555/mark-sent/ID
   ↓ API помечает как отправленное
```

---

## 🧪 Тестирование API

### Проверка всех endpoints:

```bash
# 1. Health check
curl http://localhost:5555/health

# 2. Запуск парсера
curl -X POST http://localhost:5555/parse \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 1}'

# 3. Получение неотправленных
curl http://localhost:5555/unsent?limit=5

# 4. Маркировка (замените 1 на реальный ID)
curl -X POST http://localhost:5555/mark-sent/1
```

---

## 🔧 Запуск API сервера в фоне

### Вариант 1: screen (рекомендуется)

```bash
# Установите screen если нет
sudo apt-get install screen  # Ubuntu/Debian
# или
sudo yum install screen      # CentOS/RHEL

# Запустите в screen сессии
screen -S rental-api
cd /home/user/2026/rental_parser
python3 api_server.py

# Нажмите Ctrl+A затем D чтобы выйти из screen
# API будет работать в фоне!

# Вернуться к сессии:
screen -r rental-api

# Посмотреть все сессии:
screen -ls
```

### Вариант 2: systemd service

Создайте файл `/etc/systemd/system/rental-api.service`:

```ini
[Unit]
Description=Rental Parser API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/user/2026/rental_parser
ExecStart=/usr/bin/python3 /home/user/2026/rental_parser/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запустите:

```bash
sudo systemctl daemon-reload
sudo systemctl start rental-api
sudo systemctl enable rental-api

# Проверка статуса
sudo systemctl status rental-api

# Логи
sudo journalctl -u rental-api -f
```

### Вариант 3: nohup

```bash
cd /home/user/2026/rental_parser
nohup python3 api_server.py > api.log 2>&1 &

# Проверить что работает
ps aux | grep api_server

# Посмотреть логи
tail -f api.log

# Остановить
pkill -f api_server.py
```

---

## 🐛 Решение проблем

### ❌ API не запускается: "Address already in use"

Порт 5555 занят. Измените порт:

```python
# В файле api_server.py, последняя строка:
app.run(host='0.0.0.0', port=5556, debug=False)  # Изменили на 5556
```

И в n8n workflow измените URL во всех HTTP Request нодах:
```
http://localhost:5555 → http://localhost:5556
```

### ❌ n8n: "Connection refused"

API сервер не запущен. Проверьте:

```bash
# API запущен?
ps aux | grep api_server

# Если нет - запустите
cd /home/user/2026/rental_parser
python3 api_server.py
```

### ❌ n8n: "404 Not Found"

Проверьте URL в HTTP Request ноде. Должно быть:
```
http://localhost:5555/parse
http://localhost:5555/unsent
http://localhost:5555/mark-sent/{{ $json.id }}
```

### ❌ API: "Module not found"

```bash
cd /home/user/2026/rental_parser
pip install -r requirements.txt
pip install Flask==3.0.0
```

### ❌ API работает, но парсер не находит данные

```bash
# Проверьте вручную
cd /home/user/2026/rental_parser
python3 main.py --max-pages 1

# Если ошибка - установите зависимости
pip install -r requirements.txt
```

---

## 📈 Мониторинг

### Проверка что API работает:

```bash
# Простой способ
curl http://localhost:5555/health

# Должно вывести: {"status":"ok"}
```

### Логирование:

API выводит логи в stdout. Если запущен через screen/systemd:

```bash
# screen
screen -r rental-api

# systemd
sudo journalctl -u rental-api -f

# nohup
tail -f api.log
```

---

## 🔥 Дополнительные возможности API

### Запуск парсера вручную через curl:

```bash
# Парсинг только Cian, 3 страницы
curl -X POST http://localhost:5555/parse \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 3, "platforms": ["cian"]}'
```

### Webhook интеграция:

API можно вызывать из других приложений:

```python
import requests

# Запуск парсинга
response = requests.post('http://localhost:5555/parse',
                        json={'max_pages': 5})
print(response.json())

# Получение данных
response = requests.get('http://localhost:5555/unsent?limit=10')
listings = response.json()
```

---

## ✅ Преимущества API решения

| Преимущество | Описание |
|--------------|----------|
| ✅ Работает везде | HTTP Request ноды стабильны |
| ✅ Легко тестировать | curl/Postman для тестирования |
| ✅ Переиспользуемость | API можно вызывать откуда угодно |
| ✅ Отладка | Логи API в одном месте |
| ✅ Независимость | API и n8n работают отдельно |

---

## 🎯 Финальный чек-лист

- [ ] Python зависимости установлены
- [ ] Flask установлен (`pip install Flask==3.0.0`)
- [ ] API сервер запущен (`python3 api_server.py`)
- [ ] API отвечает (`curl http://localhost:5555/health`)
- [ ] Workflow импортирован (`rental_parser_api.json`)
- [ ] Telegram credentials настроены
- [ ] `TELEGRAM_CHAT_ID` добавлен
- [ ] Тестовый запуск workflow успешен
- [ ] API настроен для работы в фоне (screen/systemd)
- [ ] Workflow активирован

---

## 📚 Файлы

| Файл | Назначение |
|------|-----------|
| `api_server.py` | Flask API сервер |
| `rental_parser_api.json` | n8n workflow с HTTP Request |
| `requirements_api.txt` | Зависимости для API |
| `API_SOLUTION.md` | Эта инструкция |

---

## 🚀 Готово!

1. **Запустите API:** `python3 api_server.py`
2. **Импортируйте workflow:** `rental_parser_api.json`
3. **Тестируйте:** Execute Workflow
4. **Активируйте:** переключатель Active

**Это решение работает 100%!** 🎉

Никаких Execute Command нод - только HTTP Request! ✅
