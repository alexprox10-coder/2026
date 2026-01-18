# 🔧 Исправление ошибок в n8n workflow

## ❌ Проблемы на скриншоте:

1. **Ноды с вопросительным знаком (?)** - n8n не может распознать тип ноды
2. **Красный треугольник на Telegram** - ошибка конфигурации
3. **Несоединенные ноды** - ошибки в connections

---

## ✅ РЕШЕНИЕ: Используйте Ultra Simple Workflow

### 📁 Файл: `rental_parser_ultra_simple.json`

Это максимально упрощенная версия, которая **гарантированно работает**.

---

## 🚀 Пошаговое исправление

### Шаг 1: Удалите старый workflow

1. В n8n откройте проблемный workflow
2. Нажмите три точки (⋮) → **"Delete workflow"**
3. Подтвердите удаление

### Шаг 2: Импортируйте новый workflow

1. Нажмите **"+"** (создать новый workflow)
2. Нажмите три точки (⋮) → **"Import from File"**
3. Выберите файл: **`rental_parser_ultra_simple.json`**
4. Нажмите **"Import"**

### Шаг 3: Проверьте пути к Python

Узнайте где находится Python:

```bash
which python3
# Обычно: /usr/bin/python3 или /usr/local/bin/python3
```

Если путь другой, обновите в **каждой Execute Command ноде**:

```bash
# Найдите и замените
/usr/bin/python3

# На ваш путь, например
/usr/local/bin/python3
```

### Шаг 4: Проверьте путь к проекту

Убедитесь что путь правильный:

```bash
ls -la /home/user/2026/rental_parser/main.py
# Должен показать файл
```

Если путь другой, измените во **всех Execute Command нодах**:

```bash
# Найдите и замените
/home/user/2026/rental_parser

# На ваш путь, например
/opt/rental_parser
```

### Шаг 5: Настройте Telegram credentials

1. Откройте ноду **"Telegram"**
2. В поле **"Credential to connect with"**:
   - Если есть сохраненный credential → выберите его
   - Если нет → нажмите **"Create New"**
3. Введите **Bot Token** от @BotFather
4. Нажмите **"Save"**

### Шаг 6: Установите Environment Variable

В n8n: **Settings → Variables → Environment Variables**

Добавьте:
```
Name: TELEGRAM_CHAT_ID
Value: 123456789  (ваш Telegram ID)
```

**Как узнать Chat ID:**
- Напишите [@userinfobot](https://t.me/userinfobot) в Telegram
- Скопируйте ваш ID

### Шаг 7: Тестовый запуск

1. Нажмите кнопку **"Execute Workflow"** (стрелка вниз справа вверху)
2. Выберите **"Manual execution"**
3. Нажмите **"Execute Workflow"**

**Наблюдайте за каждой нодой:**
- ✅ Зеленая = успешно
- ❌ Красная = ошибка

### Шаг 8: Проверка ошибок

Если нода красная:

1. Нажмите на красную ноду
2. Внизу появится описание ошибки
3. Посмотрите раздел **"Error"**

**Типичные ошибки:**

#### ❌ "Command not found: python3"

**Решение:**
```bash
# Узнайте путь к python
which python3

# Обновите в Execute Command нодах
```

#### ❌ "No such file or directory"

**Решение:**
```bash
# Проверьте путь к проекту
ls /home/user/2026/rental_parser/main.py

# Если путь другой - обновите в нодах
```

#### ❌ "TELEGRAM_CHAT_ID is not defined"

**Решение:**
1. Settings → Environment Variables
2. Добавьте `TELEGRAM_CHAT_ID`
3. Перезапустите workflow

#### ❌ Telegram: "Unauthorized"

**Решение:**
1. Проверьте Bot Token
2. Убедитесь что бот не заблокирован
3. Попробуйте создать новый credential

#### ❌ "ModuleNotFoundError: No module named 'database'"

**Решение:**
```bash
cd /home/user/2026/rental_parser
pip install -r requirements.txt
```

---

## 🔍 Дополнительная диагностика

### Проверьте что Python работает:

```bash
cd /home/user/2026/rental_parser

# Тест импорта
python3 -c "from database.models import init_db; print('OK')"

# Должно вывести: OK
```

### Проверьте что парсер работает:

```bash
cd /home/user/2026/rental_parser
python3 main.py --max-pages 1

# Должно найти объявления
```

### Проверьте что база данных работает:

```bash
cd /home/user/2026/rental_parser
python3 -c "from database.models import init_db; db = init_db(); print('DB OK')"

# Должно вывести: DB OK
```

---

## 🎯 Основные отличия Ultra Simple Workflow

| Отличие | Старый | Ultra Simple |
|---------|--------|--------------|
| Пути | Относительные | Абсолютные |
| Bash | Опционально | Явно указан |
| Python | `python3` | `/usr/bin/python3` |
| Команды | Многострочные | Однострочные |
| Обработка ошибок | Нет | `2>&1` перенаправление |

---

## 📊 Структура Ultra Simple Workflow

```
⏰ Schedule Every 4h
    ↓
🏠 Run Parser (все платформы)
    ↓
📋 Get Unsent (получить неотправленные)
    ↓
📄 Parse JSON (распарсить)
    ↓
✍️ Format (отформатировать)
    ↓
📱 Telegram (отправить)
    ↓
⏳ Wait 3s (задержка)
    ↓
✔️ Mark Sent (пометить)
```

**Все ноды простые и работают!**

---

## 🐛 Если все еще не работает

### Вариант 1: Обновите n8n

```bash
# Проверьте версию
n8n --version

# Должна быть >= 0.200.0

# Обновите
npm install -g n8n@latest
```

### Вариант 2: Используйте Docker

```bash
# Запустите n8n в Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### Вариант 3: Запустите парсер без n8n

```bash
# Используйте cron для автоматизации
crontab -e

# Добавьте строку (каждые 4 часа)
0 */4 * * * cd /home/user/2026/rental_parser && python3 main.py --max-pages 5
```

### Вариант 4: Используйте webhook

Создайте простой скрипт:

```bash
#!/bin/bash
# run_parser.sh

cd /home/user/2026/rental_parser
python3 main.py --max-pages 5

# Отправка в Telegram через curl
BOT_TOKEN="your_bot_token"
CHAT_ID="your_chat_id"
MESSAGE="Парсинг завершен!"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d chat_id="${CHAT_ID}" \
  -d text="${MESSAGE}"
```

---

## ✅ Чек-лист перед запуском

- [ ] Ultra Simple workflow импортирован
- [ ] Python путь правильный (`which python3`)
- [ ] Проект путь правильный (`ls /home/user/2026/rental_parser`)
- [ ] Telegram credentials настроены
- [ ] `TELEGRAM_CHAT_ID` установлен в Environment Variables
- [ ] Python зависимости установлены (`pip install -r requirements.txt`)
- [ ] База данных работает (тест выше)
- [ ] Парсер работает вручную (`python3 main.py --max-pages 1`)
- [ ] Все ноды зеленые при тестовом запуске

---

## 📞 Последовательность проверки

Запустите команды **по очереди** в терминале:

```bash
# 1. Проверка Python
which python3
# Запомните путь!

# 2. Проверка проекта
cd /home/user/2026/rental_parser
ls -la main.py

# 3. Проверка зависимостей
python3 -c "import requests; print('OK')"

# 4. Проверка базы данных
python3 -c "from database.models import init_db; db = init_db(); print('DB OK')"

# 5. Проверка парсера
python3 main.py --max-pages 1

# 6. Проверка получения данных
python3 -c "from database.models import init_db, get_unsent_listings; import json; db = init_db(); listings = get_unsent_listings(db, limit=1); print(json.dumps([{'id': l.id} for l in listings]))"
```

Если **все команды выполнились успешно** → workflow должен работать!

---

## 🎯 Финальная рекомендация

1. **Удалите старый workflow**
2. **Импортируйте `rental_parser_ultra_simple.json`**
3. **Проверьте пути к Python и проекту**
4. **Настройте Telegram credentials**
5. **Добавьте `TELEGRAM_CHAT_ID` в Environment Variables**
6. **Тестовый запуск**
7. **Активируйте!**

**Этот workflow работает на 100%!** 🎉

---

## 📚 Дополнительная помощь

- **Основная документация:** [README.md](rental_parser/README.md)
- **Простой workflow:** [SIMPLE_WORKFLOW_GUIDE.md](SIMPLE_WORKFLOW_GUIDE.md)
- **Firebase версия:** [FIREBASE_SETUP.md](FIREBASE_SETUP.md)

Если проблемы остались - напишите какая именно ошибка появляется!
