# 🤖 Подключение Telegram Бота к Workflow v3

## 📋 Содержание

1. [Создание бота через BotFather](#1-создание-бота-через-botfather)
2. [Настройка окружения](#2-настройка-окружения)
3. [Установка зависимостей](#3-установка-зависимостей)
4. [Настройка интеграции с n8n](#4-настройка-интеграции-с-n8n)
5. [Запуск бота](#5-запуск-бота)
6. [Тестирование](#6-тестирование)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Создание бота через BotFather

### Шаг 1.1: Откройте BotFather

1. Откройте Telegram
2. Найдите бота **@BotFather**
3. Нажмите **Start**

### Шаг 1.2: Создайте нового бота

В чате с BotFather введите команды:

```
/newbot
```

BotFather спросит имя бота:

```
Придумайте имя (например):
ChinaLeadBot

Или любое другое имя для вашего бота
```

Затем BotFather попросит username (обязательно должен заканчиваться на 'bot'):

```
Примеры username:
chinaleadbot
china_lead_bot
my_lead_finder_bot

ВАЖНО: Username должен быть уникальным!
```

### Шаг 1.3: Сохраните токен

После создания BotFather даст вам **токен**:

```
Done! Congratulations on your new bot. You will find it at t.me/chinaleadbot.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890

Keep your token secure and store it safely...
```

**ВАЖНО:** Скопируйте этот токен! Он понадобится в следующих шагах.

### Шаг 1.4: Настройте описание бота (опционально)

```
/setdescription
Выберите вашего бота → Введите описание:

🇨🇳 ChinaLeadBot - AI-агент для поиска китайских поставщиков

Находим надёжных производителей на Alibaba и 1688 с помощью ИИ-анализа.

Возможности:
✅ Поиск по категориям товаров
✅ Фильтрация по MOQ и цене
✅ AI-оценка надёжности
✅ Контакты проверенных поставщиков
```

```
/setabouttext
Выберите вашего бота → Введите короткий текст:

AI-поиск китайских поставщиков с умным анализом надёжности
```

### Шаг 1.5: Добавьте команды (опционально)

```
/setcommands
Выберите вашего бота → Введите список команд:

start - Начать работу
search - Найти поставщиков
balance - Проверить баланс поисков
help - Помощь
```

---

## 2. Настройка окружения

### Шаг 2.1: Перейдите в папку проекта

```bash
cd /home/user/2026/china-lead-bot
```

### Шаг 2.2: Создайте .env файл

```bash
# Скопируйте шаблон
cp .env.example .env

# Откройте для редактирования
nano .env
```

### Шаг 2.3: Заполните .env

Вставьте следующие данные:

```bash
# ==========================================
# TELEGRAM BOT CONFIGURATION
# ==========================================
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
# ↑ Ваш токен от BotFather

# ==========================================
# N8N WEBHOOK CONFIGURATION
# ==========================================
N8N_WEBHOOK_URL=https://app.n8n.cloud/webhook/chinaleadbot-search
# ↑ Ваш Production Webhook URL из n8n
# Как получить:
# 1. Откройте workflow v3 в n8n
# 2. Кликните на узел "Webhook Trigger"
# 3. Скопируйте "Production URL"

# ==========================================
# GOOGLE SHEETS (ОПЦИОНАЛЬНО)
# ==========================================
GOOGLE_SHEET_ID=1a2b3c4d5e6f7g8h9i0j
# ↑ ID вашей Google Sheets таблицы (из URL)
# Не обязательно, если уже настроено в n8n

# ==========================================
# OPENAI (НЕ ИСПОЛЬЗУЕТСЯ БОТОМ)
# ==========================================
# Бот НЕ вызывает OpenAI напрямую!
# OpenAI используется только в n8n workflow
# Этот ключ можно не указывать
ANTHROPIC_API_KEY=
```

**Сохраните файл:**
- Нажмите `Ctrl + O` (записать)
- Нажмите `Enter`
- Нажмите `Ctrl + X` (выйти)

---

## 3. Установка зависимостей

### Шаг 3.1: Проверьте Python

```bash
python --version
# Должно быть Python 3.8+

# Или попробуйте:
python3 --version
```

### Шаг 3.2: Создайте виртуальное окружение (рекомендуется)

```bash
cd /home/user/2026/china-lead-bot

# Создайте виртуальное окружение
python -m venv venv

# Или для Python 3:
python3 -m venv venv

# Активируйте его
source venv/bin/activate

# В терминале появится (venv) в начале строки
```

### Шаг 3.3: Установите зависимости

```bash
# Убедитесь что вы в папке china-lead-bot и venv активирован
pip install -r requirements.txt

# Или для Python 3:
pip3 install -r requirements.txt
```

**Будут установлены:**
- `python-telegram-bot==20.7` - Telegram Bot API
- `python-dotenv==1.0.0` - Загрузка .env
- `requests==2.31.0` - HTTP запросы к n8n
- И другие зависимости...

**Ожидаемое время:** 1-2 минуты

---

## 4. Настройка интеграции с n8n

### Шаг 4.1: Получите Webhook URL из n8n

1. Откройте n8n (http://localhost:5678 или app.n8n.cloud)
2. Откройте workflow **"ChinaLeadBot v3"**
3. Убедитесь что workflow **Active** (переключатель вверху)
4. Кликните на узел **"Webhook Trigger"** (самый первый узел)
5. Справа в панели настроек найдите:

```
Production URL
https://app.n8n.cloud/webhook/chinaleadbot-search
                                    ^^^^^^^^^^^^
                                    Это path из настроек
```

6. **Скопируйте весь URL**

### Шаг 4.2: Проверьте что workflow активен

В n8n вверху справа должно быть:

```
✅ Active
```

Если написано **Inactive** - кликните на переключатель чтобы активировать.

### Шаг 4.3: Проверьте путь webhook

В узле "Webhook Trigger" в настройках должно быть:

```
HTTP Method: POST
Path: chinaleadbot-search
Response Mode: Using 'Respond to Webhook' Node
```

---

## 5. Запуск бота

### Шаг 5.1: Проверьте структуру файлов

```bash
cd /home/user/2026/china-lead-bot

# Проверьте что файлы на месте
ls -la

# Должны быть:
# bot/main.py          ← Главный файл бота
# .env                 ← Конфигурация
# requirements.txt     ← Зависимости
# venv/                ← Виртуальное окружение (если создали)
```

### Шаг 5.2: Запустите бота

**Вариант A: С виртуальным окружением (рекомендуется)**

```bash
cd /home/user/2026/china-lead-bot

# Активируйте venv если еще не активирован
source venv/bin/activate

# Запустите бота
python bot/main.py
```

**Вариант B: Без виртуального окружения**

```bash
cd /home/user/2026/china-lead-bot
python bot/main.py

# Или
python3 bot/main.py
```

### Шаг 5.3: Проверьте что бот запустился

В терминале должно появиться:

```
2026-01-17 12:00:00,123 - INFO - Bot started successfully
2026-01-17 12:00:00,124 - INFO - Username: @chinaleadbot
2026-01-17 12:00:00,125 - INFO - Webhook URL: https://app.n8n.cloud/webhook/chinaleadbot-search
2026-01-17 12:00:00,126 - INFO - Bot is running... Press Ctrl+C to stop
```

**Если видите это - всё отлично! Бот работает!** ✅

### Шаг 5.4: Оставьте бота работать

**ВАЖНО:** Не закрывайте терминал! Бот должен работать постоянно.

**Для запуска в фоне** (опционально):

```bash
# Запуск с nohup (продолжит работать после закрытия терминала)
nohup python bot/main.py > bot.log 2>&1 &

# Проверить что работает
ps aux | grep main.py

# Остановить
pkill -f main.py
```

---

## 6. Тестирование

### Тест 1: Проверьте что бот онлайн

1. Откройте Telegram
2. Найдите вашего бота (по username, например @chinaleadbot)
3. Должна быть **зелёная точка** рядом с именем (бот онлайн)

### Тест 2: Отправьте /start

В чате с ботом введите:

```
/start
```

**Ожидаемый ответ:**

```
🇨🇳 Добро пожаловать в ChinaLeadBot!

Я помогу найти надёжных китайских поставщиков на Alibaba и 1688.

🔍 Что я умею:
✅ Поиск поставщиков по категориям товаров
✅ Фильтрация по MOQ и ценовому диапазону
✅ AI-анализ надёжности компаний
✅ Контактные данные проверенных поставщиков

💎 У вас доступно: 5 поисков (FREE тариф)

Что хотите сделать?

[Кнопки:]
🔍 Найти поставщиков | 💰 Баланс
❓ Помощь
```

### Тест 3: Выполните поиск

1. Нажмите кнопку **🔍 Найти поставщиков**
2. Бот спросит категорию товара:

```
🔍 ПОИСК ПОСТАВЩИКОВ

Введите категорию товара или продукт:
Примеры: wireless headphones, backpack, LED lights
```

3. Введите, например:

```
wireless headphones
```

4. Бот спросит про MOQ:

```
📦 Какой минимальный объём заказа (MOQ) вам подходит?

[Кнопки:]
Любой | До 100 шт
До 500 шт | До 1000 шт
```

5. Выберите **Любой**

6. Бот спросит про цену:

```
💰 Какой ценовой диапазон вас интересует?

[Кнопки:]
Любая | До $1
$1-5 | $5-10
$10-50
```

7. Выберите **Любая**

8. Бот начнет поиск:

```
🔄 Ищу поставщиков...

Отправляю запрос в AI-систему анализа...
```

### Тест 4: Проверьте результаты

**Если всё настроено правильно**, бот вернёт:

```
✅ НАЙДЕНО 10 ПОСТАВЩИКОВ

📊 Отсортировано по надёжности

━━━━━━━━━━━━━━━━━━━━

🏢 #1: Yiwu Wholesale Trading Co.
⭐️ Рейтинг: 4.9/5
📊 AI-оценка: 9/10
✅ Рекомендуется: Да

📍 Zhejiang, China
📦 MOQ: 200 pieces
💰 Цена: $3.8

📧 export@yiwu-wholesale.com
🌐 https://yiwu-wholesale.en.alibaba.com

💬 Резюме AI:
Отличная надёжная компания с большим опытом работы...

✅ Плюсы: высокий рейтинг, много сделок, verified
⚠️ Риски: средний MOQ может быть проблемой

━━━━━━━━━━━━━━━━━━━━

[еще 9 компаний...]

🎯 Осталось поисков: 4
```

**Если видите такой результат - всё работает! 🎉**

---

## 7. Troubleshooting

### Проблема 1: Бот не запускается

**Ошибка:**
```
telegram.error.InvalidToken: Invalid token
```

**Решение:**
1. Проверьте токен в `.env`
2. Убедитесь что скопировали полностью от BotFather
3. Нет лишних пробелов в начале/конце
4. Формат: `1234567890:ABCdefGH...`

---

### Проблема 2: Бот не отвечает на команды

**Симптомы:**
- Бот онлайн (зелёная точка)
- Но не отвечает на /start

**Решение:**
1. Проверьте логи в терминале
2. Перезапустите бота:
   ```bash
   Ctrl+C  # Остановить
   python bot/main.py  # Запустить снова
   ```
3. Проверьте что нет ошибок в коде `bot/main.py`

---

### Проблема 3: Бот возвращает ошибку при поиске

**Ошибка в боте:**
```
❌ Ошибка при поиске поставщиков

Не удалось подключиться к системе анализа.
Попробуйте позже.
```

**Возможные причины:**

#### 3.1: n8n workflow не активен

**Решение:**
1. Откройте n8n
2. Найдите workflow v3
3. Активируйте его (переключатель Active)

#### 3.2: Неправильный Webhook URL

**Решение:**
1. Проверьте URL в `.env`
2. Должен совпадать с Production URL в n8n
3. Должен начинаться с `http://` или `https://`
4. Не должно быть лишних пробелов

#### 3.3: n8n недоступен

**Решение:**
```bash
# Проверьте доступность
curl -X POST "ВАШ_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Если ошибка - n8n недоступен
```

#### 3.4: Ошибка в workflow

**Решение:**
1. Откройте n8n
2. Посмотрите логи выполнения workflow
3. Найдите узел с ошибкой (красный)
4. Проверьте настройки этого узла

---

### Проблема 4: Timeout при поиске

**Ошибка:**
```
⏱ Превышено время ожидания ответа
```

**Причина:** n8n workflow работает дольше 120 секунд

**Решение:**
1. В `bot/main.py` увеличьте timeout:
   ```python
   # Найдите строку:
   response = requests.post(N8N_WEBHOOK_URL, json=search_params, timeout=120)

   # Измените на:
   response = requests.post(N8N_WEBHOOK_URL, json=search_params, timeout=300)
   ```

2. В n8n проверьте что узлы выполняются быстро:
   - Generate Suppliers Data: <1 сек
   - AI Agent: 5-30 сек (зависит от OpenAI)
   - Google Sheets: 1-5 сек

---

### Проблема 5: Данные не сохраняются в Google Sheets

**Симптомы:**
- Бот работает
- Результаты приходят
- Но в таблице пусто

**Решение:**
1. Откройте n8n
2. Проверьте узел "Save to Google Sheets"
3. Проверьте что:
   - Google Sheets credential подключен
   - Document ID правильный
   - Sheet Name = "Leads"
   - Таблица имеет правильные заголовки

4. Выполните тест в n8n:
   - Execute workflow
   - Проверьте что узел "Save to Google Sheets" зелёный
   - Проверьте таблицу

---

### Проблема 6: OpenAI API error

**Ошибка в логах n8n:**
```
OpenAI API error: Insufficient funds
```

**Решение:**
1. Проверьте баланс: https://platform.openai.com/usage
2. Пополните счет минимум на $5
3. Проверьте API key в credential

---

### Проблема 7: Бот работает, но медленно

**Оптимизация:**

1. **Уменьшите количество компаний** в Generate Suppliers Data:
   ```javascript
   // Измените topSuppliers с 10 на 5
   const topSuppliers = filtered.slice(0, 5);
   ```

2. **Используйте GPT-3.5** вместо GPT-4:
   - В OpenAI Chat Model
   - Model: `gpt-3.5-turbo`

3. **Уменьшите max_tokens**:
   - В OpenAI Chat Model
   - Max Tokens: 300 (вместо 500)

---

## 8. Запуск в Production

### Вариант A: Screen (простой)

```bash
# Установите screen
sudo apt-get install screen  # Linux
brew install screen          # Mac

# Запустите бота в screen
screen -S chinaleadbot
cd /home/user/2026/china-lead-bot
source venv/bin/activate
python bot/main.py

# Отключитесь (бот продолжит работать):
Ctrl+A, затем D

# Вернуться к боту:
screen -r chinaleadbot

# Остановить бота:
screen -r chinaleadbot
Ctrl+C
```

### Вариант B: Systemd (для серверов)

Создайте service файл:

```bash
sudo nano /etc/systemd/system/chinaleadbot.service
```

Вставьте:

```ini
[Unit]
Description=ChinaLeadBot Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/2026/china-lead-bot
Environment="PATH=/home/user/2026/china-lead-bot/venv/bin"
ExecStart=/home/user/2026/china-lead-bot/venv/bin/python bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запустите:

```bash
sudo systemctl daemon-reload
sudo systemctl enable chinaleadbot
sudo systemctl start chinaleadbot

# Проверить статус
sudo systemctl status chinaleadbot

# Логи
sudo journalctl -u chinaleadbot -f
```

### Вариант C: Docker (продвинутый)

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bot/ ./bot/
COPY .env .

CMD ["python", "bot/main.py"]
```

Запустите:

```bash
docker build -t chinaleadbot .
docker run -d --name chinaleadbot --restart always chinaleadbot
```

---

## 9. Мониторинг

### Проверка работы бота

```bash
# Проверить что процесс запущен
ps aux | grep main.py

# Проверить логи
tail -f bot.log

# Проверить webhook
curl -X POST "http://localhost:5000/health"
```

### Логи в реальном времени

В `bot/main.py` уже настроено логирование:

```python
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
```

Смотрите логи в терминале где запущен бот.

---

## 10. Чеклист готовности

```
☐ Создан бот через @BotFather
☐ Получен токен бота
☐ Создан .env файл
☐ Заполнен TELEGRAM_BOT_TOKEN
☐ Заполнен N8N_WEBHOOK_URL
☐ Workflow v3 импортирован в n8n
☐ Workflow v3 активирован (Active)
☐ OpenAI credential настроен в n8n
☐ Google Sheets настроен в n8n
☐ Python зависимости установлены
☐ Бот запускается без ошибок
☐ Бот отвечает на /start
☐ Поиск работает и возвращает результаты
☐ Данные сохраняются в Google Sheets
☐ Бот запущен в production режиме
☐ Готов к использованию! 🚀
```

---

## 11. Полная архитектура

```
┌─────────────────┐
│  TELEGRAM USER  │
└────────┬────────┘
         │ /start, /search
         ↓
┌─────────────────┐
│  TELEGRAM BOT   │  ← bot/main.py
│   (Python)      │    (запущен локально)
└────────┬────────┘
         │ HTTP POST
         │ {category, moq, price}
         ↓
┌─────────────────┐
│   N8N WEBHOOK   │  ← workflow v3
│   (Cloud/Local) │    (активирован)
└────────┬────────┘
         │
         ├─→ Generate Suppliers Data
         ├─→ AI Agent + OpenAI
         ├─→ Save to Google Sheets
         └─→ Return JSON
         ↓
┌─────────────────┐
│  TELEGRAM BOT   │
│  (Response)     │
└────────┬────────┘
         │ Форматированный ответ
         ↓
┌─────────────────┐
│  TELEGRAM USER  │
│   (Результаты)  │
└─────────────────┘
```

---

## 🎯 Итог

После выполнения всех шагов у вас будет:

✅ Telegram бот, подключенный к n8n
✅ AI-анализ через OpenAI GPT-4
✅ Автосохранение лидов в Google Sheets
✅ Готовая система для монетизации

**Следующий шаг:** Тестирование и привлечение первых пользователей! 🚀

---

## 📞 Дополнительные ресурсы

- **Документация python-telegram-bot:** https://docs.python-telegram-bot.org/
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **n8n Documentation:** https://docs.n8n.io/
- **OpenAI API:** https://platform.openai.com/docs/

---

**Готово! Теперь ваш бот подключен к workflow v3!** 🎉
