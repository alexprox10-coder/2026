# ⚡ Quick Start Guide - 10 минут до запуска

## Шаг 1: Установка зависимостей (2 минуты)

```bash
cd rental_parser
pip install -r requirements.txt
```

## Шаг 2: Настройка Telegram бота (3 минуты)

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Создайте нового бота:
   ```
   /newbot
   Rental Parser Bot
   rental_parser_bot
   ```
3. Скопируйте токен (например: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

4. Узнайте свой Chat ID:
   - Напишите боту [@userinfobot](https://t.me/userinfobot)
   - Скопируйте ваш ID (например: `123456789`)

## Шаг 3: Создание конфигурации (1 минута)

```bash
cp .env.example .env
nano .env
```

Заполните минимально необходимые параметры:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

Сохраните (Ctrl+O, Enter, Ctrl+X)

## Шаг 4: Первый запуск парсера (2 минуты)

```bash
# Создайте директорию для логов
mkdir -p logs

# Запустите парсер (парсит только первую страницу для теста)
python main.py --max-pages 1
```

Вы увидите:
```
[HH:MM:SS] Starting parser for CIAN
[HH:MM:SS] Parsing Cian.ru page 1/1
[HH:MM:SS] Found 20 listings on page 1
✓ CIAN: Found 20 listings, 20 new
...
```

## Шаг 5: Проверка результатов (1 минута)

```bash
# Посмотреть статистику
python main.py --stats
```

Результат:
```
DATABASE STATISTICS
==================================================
Total listings: 60
Unsent listings: 60

By platform:
  Cian: 20
  Yandex: 20
  Avito: 20
==================================================
```

## Шаг 6: Запуск Telegram бота (1 минута)

```bash
# В отдельном терминале
cd bot
python telegram_bot.py
```

Откройте Telegram и напишите вашему боту:
```
/start
/get 5
```

Вы получите 5 объявлений!

## 🎉 Готово!

Теперь у вас работает:
- ✅ Парсер трех площадок
- ✅ База данных SQLite
- ✅ Telegram бот для получения объявлений

## 🚀 Следующие шаги

### 1. Настройка автоматического запуска

#### Вариант A: Через cron (Linux/Mac)
```bash
crontab -e
```

Добавьте строку (каждые 4 часа):
```
0 */4 * * * cd /path/to/rental_parser && python main.py --max-pages 5
```

#### Вариант B: Через n8n (рекомендуется)
1. Установите n8n:
   ```bash
   npm install -g n8n
   n8n start
   ```
2. Откройте http://localhost:5678
3. Импортируйте `rental_parser_workflow.json`
4. Активируйте workflow

### 2. Добавление прокси (опционально)

```bash
cp proxies.example.txt proxies.txt
nano proxies.txt
```

Добавьте свои прокси:
```
http://user:pass@proxy1.example.com:8080
http://user:pass@proxy2.example.com:8080
```

Запустите с прокси:
```bash
python main.py --max-pages 5 --proxy-file proxies.txt
```

### 3. Извлечение телефонов

```bash
python main.py --extract-phones --phone-limit 20
```

## 📱 Команды Telegram бота

- `/start` - Регистрация в системе
- `/get 10` - Получить 10 новых объявлений
- `/stats` - Статистика базы данных
- `/help` - Полная справка

## 🛟 Помощь

**Ошибка "ModuleNotFoundError"**:
```bash
pip install -r requirements.txt
```

**Бот не отвечает**:
- Проверьте токен в `.env`
- Убедитесь, что бот запущен: `python bot/telegram_bot.py`

**Парсер не находит объявления**:
- Проверьте интернет-соединение
- Попробуйте использовать прокси
- Проверьте логи: `cat logs/parser.log`

## 📊 Пример полного workflow

```bash
# Утром: запустить парсер
python main.py --max-pages 5

# Извлечь телефоны для новых объявлений
python main.py --extract-phones --phone-limit 30

# Получить объявления через Telegram
# (откройте Telegram и напишите боту /get 20)

# Вечером: повторить
python main.py --max-pages 3
```

## 🎯 Рекомендации

1. **Частота парсинга**: Каждые 4-6 часов оптимально
2. **Страниц за раз**: 3-5 страниц для стабильной работы
3. **Прокси**: Обязательно для production
4. **Мониторинг**: Проверяйте логи ежедневно

---

**Все работает? Отлично! 🎉**

Теперь вы можете:
- Настроить автоматический запуск через n8n
- Добавить больше менеджеров в Telegram бота
- Настроить фильтры по цене и районам
- Интегрировать автодозвон

Подробнее смотрите в [README.md](README.md)
