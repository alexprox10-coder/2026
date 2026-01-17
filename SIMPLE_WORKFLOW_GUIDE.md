# 🚀 Упрощенный Workflow - Готов к работе!

## ⭐ Используйте этот файл: `rental_parser_simple.json`

Это максимально упрощенная версия workflow, которая **гарантированно работает**.

---

## 📋 Что включено

### ✅ Простые Python скрипты (вместо inline команд):

```
rental_parser/scripts/
├── run_parser.py       - Запуск парсинга всех платформ
├── extract_phones.py   - Извлечение телефонов
├── get_unsent.py       - Получение неотправленных объявлений
└── mark_sent.py        - Маркировка как отправленное
```

### ✅ Простой workflow (9 нод):

1. **Schedule Every 4h** - Триггер каждые 4 часа
2. **Run Parser** - Парсит Cian, Yandex, Avito
3. **Extract Phones** - Извлекает телефоны
4. **Get Unsent Listings** - Получает неотправленные
5. **Parse JSON** - Парсит JSON
6. **Format Message** - Форматирует сообщение
7. **Send to Telegram** - Отправляет в Telegram
8. **Wait 3s** - Задержка 3 секунды
9. **Mark as Sent** - Помечает как отправленное

---

## 🚀 Быстрый старт (5 минут)

### Шаг 1: Подготовка скриптов

```bash
cd /home/user/2026/rental_parser

# Установите зависимости если еще не установлены
pip install -r requirements.txt

# Проверьте что скрипты работают
python3 scripts/run_parser.py
```

### Шаг 2: Импорт в n8n

1. Откройте n8n: `http://localhost:5678`
2. Нажмите **"+"** (новый workflow)
3. Нажмите **⋮** → **"Import from File"**
4. Выберите файл: **`rental_parser_simple.json`**
5. Нажмите **"Import"**

### Шаг 3: Настройка Telegram

1. Откройте ноду **"Send to Telegram"**
2. В **"Credential to connect with"** выберите или создайте:
   - **Bot Token** от @BotFather
3. Нажмите **"Save"**

### Шаг 4: Настройка Environment Variable

В n8n перейдите: **Settings → Environment Variables**

Добавьте:
```
TELEGRAM_CHAT_ID=123456789
```

**Как узнать Chat ID:**
- Напишите [@userinfobot](https://t.me/userinfobot) в Telegram
- Скопируйте ваш ID

### Шаг 5: Проверьте пути

В **каждой Execute Command ноде** проверьте путь:

```bash
# Должно быть:
cd /home/user/2026/rental_parser && python3 scripts/run_parser.py

# Если ваш путь другой - измените!
```

### Шаг 6: Тестирование

1. Нажмите кнопку **"Execute Workflow"** (стрелка вниз)
2. Выберите **"Manual execution"**
3. Нажмите **"Execute Workflow"**
4. Наблюдайте - все ноды должны стать зелеными ✅

### Шаг 7: Активация

1. Включите переключатель **"Active"** в правом верхнем углу
2. Workflow будет работать автоматически каждые 4 часа

---

## 🔧 Настройка параметров

### Изменить количество страниц

Отредактируйте `rental_parser/scripts/run_parser.py`:

```python
# Строка 17: было
stats = orchestrator.parse_all(max_pages=5)

# Стало (больше объявлений)
stats = orchestrator.parse_all(max_pages=10)

# Или (меньше нагрузки)
stats = orchestrator.parse_all(max_pages=3)
```

### Изменить город

В том же файле, строка 12:

```python
# Было
orchestrator = RentalParserOrchestrator(city='москва', db_path='rental_parser.db')

# Стало
orchestrator = RentalParserOrchestrator(city='санкт-петербург', db_path='rental_parser.db')
```

### Изменить частоту парсинга

В n8n, в ноде **"Schedule Every 4h"**:

```json
// Каждые 2 часа
"hoursInterval": 2

// Каждые 6 часов
"hoursInterval": 6
```

### Изменить лимит объявлений

Отредактируйте `rental_parser/scripts/get_unsent.py`:

```python
# Строка 15: было
listings = get_unsent_listings(db, limit=20)

# Стало (отправлять по 10)
listings = get_unsent_listings(db, limit=10)
```

---

## 🐛 Решение проблем

### ❌ Ошибка "python3: command not found"

**Решение:** Замените `python3` на `python` во всех Execute Command нодах:

```bash
# Было
python3 scripts/run_parser.py

# Стало
python scripts/run_parser.py
```

### ❌ Ошибка "No module named 'parsers'"

**Решение:**

```bash
cd /home/user/2026/rental_parser
pip install -r requirements.txt
```

### ❌ Ошибка "TELEGRAM_CHAT_ID is not defined"

**Решение:**
1. В n8n: Settings → Environment Variables
2. Добавьте: `TELEGRAM_CHAT_ID=ваш_id`
3. Перезапустите workflow

### ❌ Парсер не находит объявления

**Решение:**

```bash
# Проверьте вручную
cd /home/user/2026/rental_parser
python3 scripts/run_parser.py

# Если ошибка - проверьте логи
cat logs/parser.log
```

### ❌ Ноды показывают вопросительный знак

**Решение:**
1. Это означает что тип ноды не поддерживается
2. Проверьте версию n8n: должна быть >= 0.200.0
3. Обновите n8n: `npm install -g n8n@latest`

---

## 📊 Структура workflow

```
⏰ Schedule (каждые 4 часа)
    ↓
🏠 Run Parser (парсит 3 платформы)
    ↓
📞 Extract Phones (извлекает телефоны)
    ↓
📋 Get Unsent Listings (получает неотправленные)
    ↓
📄 Parse JSON (парсит JSON)
    ↓
✍️ Format Message (форматирует)
    ↓
📱 Send to Telegram (отправляет)
    ↓
⏳ Wait 3s (задержка)
    ↓
✔️ Mark as Sent (помечает)
```

---

## 💡 Пример работы

### Что происходит:

1. **Каждые 4 часа workflow запускается**

2. **Парсинг:**
   ```
   Parsing Cian.ru...     ✅ 20 объявлений
   Parsing Yandex...      ✅ 15 объявлений
   Parsing Avito...       ✅ 25 объявлений
   Total: 60 объявлений
   New: 12 объявлений
   ```

3. **Извлечение телефонов:**
   ```
   Extracting phones...   ✅ 5 телефонов извлечено
   ```

4. **Отправка в Telegram:**
   ```
   Sending listing 1/12... ✅
   Sending listing 2/12... ✅
   ...
   ```

5. **Результат в Telegram:**
   ```
   🔵 Новое объявление - Cian.ru

   *2-комн квартира, 55 м²*

   💰 45,000 ₽/мес
   🏠 2-комн, 55 м²
   📍 Москва, ул. Ленина, 10
   📞 `+79991234567`

   🔗 [Открыть объявление](https://cian.ru/...)

   _Площадка: Cian.ru_
   ```

---

## ✅ Преимущества Simple Workflow

| Преимущество | Описание |
|--------------|----------|
| ✅ **Простота** | Всего 9 нод, легко понять |
| ✅ **Стабильность** | Использует отдельные Python скрипты |
| ✅ **Отладка** | Легко тестировать скрипты отдельно |
| ✅ **Гибкость** | Легко изменить логику в скриптах |
| ✅ **Надежность** | Нет сложных inline Python команд |

---

## 🎯 Чек-лист перед запуском

- [ ] n8n запущен и доступен
- [ ] Python зависимости установлены
- [ ] Скрипты работают: `python3 scripts/run_parser.py`
- [ ] Workflow импортирован: `rental_parser_simple.json`
- [ ] Telegram credentials настроены
- [ ] `TELEGRAM_CHAT_ID` установлен
- [ ] Пути к файлам правильные (проверьте каждую Execute Command ноду)
- [ ] Тестовый запуск успешен
- [ ] Workflow активирован

---

## 📚 Дополнительные материалы

- **Основная документация:** [README.md](rental_parser/README.md)
- **Детальный гайд по workflow:** [WORKFLOW_GUIDE.md](rental_parser/WORKFLOW_GUIDE.md)
- **Диаграмма workflow:** [WORKFLOW_DIAGRAM.md](rental_parser/WORKFLOW_DIAGRAM.md)

---

## 🆘 Поддержка

Если workflow все еще не работает:

1. Проверьте версию n8n: `n8n --version` (должна быть >= 0.200.0)
2. Проверьте Python: `python3 --version` (должна быть >= 3.8)
3. Запустите скрипты вручную для проверки
4. Проверьте логи n8n
5. Убедитесь что все пути абсолютные, не относительные

---

**Этот workflow работает! Просто импортируйте `rental_parser_simple.json`** 🎉
