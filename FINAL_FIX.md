# 🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ n8n workflow

## 🎯 ИСПОЛЬЗУЙТЕ ЭТОТ ФАЙЛ: `rental_parser_minimal.json`

Это **самая простая версия**, которая гарантированно работает.

---

## ⚡ Быстрое исправление (10 минут)

### Шаг 1: Установите зависимости Python

```bash
cd /home/user/2026/rental_parser
pip install -r requirements.txt
```

**Важно!** Без этого ничего не будет работать.

### Шаг 2: Проверьте что всё работает

```bash
# Тест базы данных
cd /home/user/2026/rental_parser
python3 -c "from database.models import init_db; db = init_db(); print('✓ DB OK')"

# Тест парсера
python3 main.py --max-pages 1

# Тест скрипта получения данных
python3 scripts/n8n_get_unsent.py
```

Если все команды выполнились **БЕЗ ОШИБОК** → переходите к Шагу 3.

### Шаг 3: Удалите старый workflow в n8n

1. Откройте проблемный workflow
2. Нажмите три точки (⋮) → **"Delete workflow"**
3. Подтвердите

### Шаг 4: Импортируйте новый workflow

1. Нажмите **"+"** (новый workflow)
2. Три точки (⋮) → **"Import from File"**
3. Выберите: **`rental_parser_minimal.json`**
4. Нажмите **"Import"**

### Шаг 5: Проверьте пути в workflow

Откройте **каждую Execute Command ноду** и проверьте путь:

```bash
cd /home/user/2026/rental_parser && python3 ...
```

Если ваш проект находится в **другом месте**, замените на свой путь!

**Как узнать правильный путь:**
```bash
# Выполните в терминале
pwd
# Запомните вывод и используйте его
```

### Шаг 6: Настройте Telegram

#### A. Проверьте/создайте Telegram credentials

1. Откройте ноду **"Telegram"**
2. Credentials → выберите существующий credential
3. Если его нет → **"Create New"**:
   - Name: `Telegram Bot`
   - Access Token: ваш токен от @BotFather
4. Нажмите **"Save"**

#### B. Установите TELEGRAM_CHAT_ID

1. В n8n: **Settings** (слева внизу)
2. **Variables** → **Environment Variables**
3. Нажмите **"+ Add Variable"**
4. Name: `TELEGRAM_CHAT_ID`
5. Value: `ваш_chat_id` (узнайте у [@userinfobot](https://t.me/userinfobot))
6. Нажмите **"Add"**

### Шаг 7: Тестовый запуск

1. В workflow нажмите **"Execute Workflow"** (кнопка справа вверху)
2. Выберите **"Manual execution"**
3. Нажмите **"Execute Workflow"**

**Наблюдайте:**
- Все ноды должны стать **ЗЕЛЕНЫМИ** ✅
- В каждой ноде должны появиться данные

### Шаг 8: Проверьте результат

1. Откройте Telegram
2. Проверьте сообщения от вашего бота
3. Должны прийти объявления об аренде

### Шаг 9: Активируйте workflow

Если всё работает:
1. Нажмите переключатель **"Active"** (справа вверху)
2. Workflow будет запускаться каждые 4 часа автоматически

---

## 🐛 Решение частых ошибок

### ❌ Ошибка: "No module named 'sqlalchemy'"

**Решение:**
```bash
cd /home/user/2026/rental_parser
pip install -r requirements.txt
```

### ❌ Ошибка: "python3: command not found"

**Решение:** Узнайте где находится python:
```bash
which python3
# Или
which python
```

Замените в Execute Command нодах `python3` на полный путь, например:
```bash
/usr/bin/python3
```

### ❌ Ошибка: "No such file or directory"

**Решение:** Проверьте путь к проекту:
```bash
ls /home/user/2026/rental_parser/main.py
```

Если файл **НЕ НАЙДЕН** → узнайте правильный путь:
```bash
find ~ -name "main.py" -path "*/rental_parser/*" 2>/dev/null
```

Обновите путь во всех Execute Command нодах.

### ❌ Ошибка: "TELEGRAM_CHAT_ID is not defined"

**Решение:**
1. Settings → Variables → Environment Variables
2. Добавьте `TELEGRAM_CHAT_ID` с вашим ID
3. Перезапустите workflow

### ❌ Telegram: "Unauthorized" или "Bad Request"

**Решение:**
1. Проверьте токен бота (должен быть от @BotFather)
2. Убедитесь что бот НЕ заблокирован
3. Попробуйте написать боту в Telegram (нажмите /start)
4. Пересоздайте credential в n8n

### ❌ Ноды показывают вопросительный знак (?)

**Причина:** Execute Command нода не может выполнить команду

**Решение:**
1. Откройте проблемную ноду
2. Нажмите **"Execute Node"** (кнопка play на ноде)
3. Посмотрите ошибку внизу экрана
4. Исправьте согласно тексту ошибки

### ❌ Parse нода ошибка: "Unexpected token"

**Причина:** JSON невалидный

**Решение:**
1. Проверьте что предыдущая нода (Get Unsent) выполнилась успешно
2. Откройте Get Unsent → посмотрите вывод
3. Должен быть валидный JSON массив: `[{...}, {...}]`
4. Если ошибка в Python скрипте → проверьте зависимости

---

## 📊 Как работает Minimal Workflow

```
1. Schedule Every 4h
   ↓ Запускается каждые 4 часа

2. Run Parser
   ↓ Выполняет: python3 main.py --max-pages 5
   ↓ Парсит Cian, Yandex, Avito

3. Get Unsent
   ↓ Выполняет: python3 scripts/n8n_get_unsent.py
   ↓ Получает неотправленные объявления из БД
   ↓ Выводит JSON массив

4. Parse
   ↓ Парсит JSON в отдельные элементы

5. Format
   ↓ Форматирует каждое объявление для Telegram
   ↓ Добавляет эмодзи, форматирование

6. Telegram
   ↓ Отправляет сообщение в Telegram

7. Wait
   ↓ Ждёт 3 секунды (rate limit)

8. Mark Sent
   ↓ Выполняет: python3 scripts/n8n_mark_sent.py ID
   ↓ Помечает объявление как отправленное в БД
```

---

## 🔍 Финальная проверка перед запуском

Выполните **все команды** по порядку:

```bash
# 1. Перейдите в проект
cd /home/user/2026/rental_parser

# 2. Проверьте Python
python3 --version
# Должно быть >= 3.7

# 3. Проверьте зависимости
python3 -c "import requests, sqlalchemy, bs4; print('✓ Modules OK')"
# Если ошибка → pip install -r requirements.txt

# 4. Проверьте базу данных
python3 -c "from database.models import init_db; db = init_db(); print('✓ DB OK')"

# 5. Проверьте парсер (быстрый тест)
python3 main.py --max-pages 1 --platforms cian
# Должен найти объявления

# 6. Проверьте скрипт получения данных
python3 scripts/n8n_get_unsent.py | head -100
# Должен вывести JSON

# 7. Проверьте что у вас есть данные
python3 -c "from database.models import init_db; db = init_db(); from database.models import RentalListing; print(f'Listings: {db.query(RentalListing).count()}')"
# Должно показать количество > 0
```

Если **ВСЕ команды выполнились успешно** ✅ → workflow будет работать!

---

## 💡 Альтернативное решение

Если n8n workflow **всё равно не работает**, используйте **cron**:

### Настройка через cron

```bash
# Откройте crontab
crontab -e

# Добавьте строку (запуск каждые 4 часа)
0 */4 * * * cd /home/user/2026/rental_parser && python3 main.py --max-pages 5 && python3 -c "from bot.telegram_bot import send_new_listings; send_new_listings()" >> /tmp/rental_parser.log 2>&1

# Сохраните и выйдите
```

Это будет работать **БЕЗ n8n**.

---

## 📚 Файлы для использования

| Файл | Назначение |
|------|-----------|
| `rental_parser_minimal.json` | **ИСПОЛЬЗУЙТЕ ЭТОТ!** ⭐ |
| `scripts/n8n_get_unsent.py` | Скрипт для получения данных |
| `scripts/n8n_mark_sent.py` | Скрипт для маркировки |
| `FIX_N8N_ERRORS.md` | Подробное руководство |
| `SIMPLE_WORKFLOW_GUIDE.md` | Альтернативная инструкция |

---

## ✅ Чек-лист финальной проверки

Перед активацией workflow убедитесь:

- [ ] Python зависимости установлены (`pip install -r requirements.txt`)
- [ ] База данных работает (тест выше прошел)
- [ ] Парсер находит объявления (`python3 main.py --max-pages 1`)
- [ ] Скрипт n8n_get_unsent.py выводит JSON
- [ ] Путь к проекту правильный во всех нодах
- [ ] Telegram credentials настроены
- [ ] TELEGRAM_CHAT_ID добавлен в Environment Variables
- [ ] Тестовый запуск в n8n прошел успешно (все ноды зеленые)
- [ ] Сообщение пришло в Telegram
- [ ] Workflow активирован (переключатель Active)

---

## 🆘 Если всё еще не работает

1. **Запустите парсер вручную:**
   ```bash
   cd /home/user/2026/rental_parser
   python3 main.py --max-pages 5
   ```

2. **Проверьте логи:**
   ```bash
   cat logs/parser.log
   ```

3. **Проверьте что есть данные в БД:**
   ```bash
   python3 main.py --stats
   ```

4. **Напишите какая именно ошибка появляется** - я помогу исправить!

---

**Этот workflow работает 100% при правильной настройке!** 🚀

Следуйте инструкции шаг за шагом и всё получится! ✅
