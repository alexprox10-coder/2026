# 🤖 ChinaLeadBot - Telegram Trigger Workflow

## ✨ БЕЗ PYTHON БОТА! Всё работает в n8n!

Этот workflow использует **Telegram Trigger** напрямую в n8n.
**Python бот больше НЕ НУЖЕН!** 🎉

---

## 🎯 Архитектура

**Старый способ (сложный):**
```
Telegram → Python Bot → Webhook → n8n → AI → Response → Python Bot → Telegram
```

**Новый способ (простой):**
```
Telegram → n8n → AI → Response → Telegram
```

---

## 🚀 НАСТРОЙКА (5 минут)

### Шаг 1: Импортируйте workflow

1. Откройте n8n
2. **Workflows → Import from File**
3. Выберите:
   ```
   /home/user/2026/china-lead-bot/workflows/chinaleadbot_telegram_trigger.json
   ```
4. Нажмите **Import**

---

### Шаг 2: Настройте Telegram Credential

1. Кликните на узел **"Telegram Trigger"** (самый первый)
2. В правой панели найдите **Credentials**
3. Нажмите **Create New Credential**
4. Выберите **"Telegram API"**

**Заполните:**
```
Access Token: 8385249886:AAE7zDQznQ3nKjmRGr9Ix7LsvJqqcp5tMLU
```

5. Нажмите **Save**

---

### Шаг 3: Примените credential ко всем Telegram узлам

В workflow есть несколько Telegram узлов:
- Telegram Trigger
- Send Welcome Message
- Send Help Message
- Send Processing Message
- Send Results

**Для каждого:**
1. Кликните на узел
2. В **Credentials** выберите созданный credential
3. Сохраните

---

### Шаг 4: Настройте OpenAI Credential

1. Кликните на узел **"OpenAI Analyze"**
2. В **Credentials** нажмите **Create New Credential**
3. Выберите **"OpenAI API"**
4. Вставьте ваш **OpenAI API Key**
5. Нажмите **Save**

---

### Шаг 5: АКТИВИРУЙТЕ Workflow

1. Вверху справа найдите переключатель **Inactive**
2. **Кликните** чтобы активировать
3. Должен стать **Active** (зелёный)

**ВАЖНО:** Без активации бот не будет отвечать!

---

## ✅ ТЕСТИРОВАНИЕ

### 1. Проверьте что workflow активен

Вверху должно быть **Active** (зелёный переключатель)

### 2. Откройте Telegram

Найдите вашего бота (от @BotFather)

### 3. Отправьте /start

Должен ответить приветствием:
```
🇨🇳 Добро пожаловать в ChinaLeadBot!

Я помогу найти надёжных китайских поставщиков...
```

### 4. Попробуйте поиск

Напишите:
```
wireless headphones
```

Или:
```
/search LED lights
```

Бот должен:
1. Отправить "🔍 Поиск запущен!"
2. Через 10-30 секунд вернуть **5 проанализированных компаний**

---

## 🎮 ДОСТУПНЫЕ КОМАНДЫ

### Команды бота:

| Команда | Описание |
|---------|----------|
| **/start** | Приветствие и инструкция |
| **/search <категория>** | Поиск поставщиков |
| **/help** | Справка |
| **любой текст** | Воспринимается как поисковый запрос |

### Примеры:

```
wireless headphones
bluetooth speaker
LED lights
phone case
backpack
```

---

## 🔧 КАК РАБОТАЕТ WORKFLOW

### 1. Telegram Trigger
Слушает сообщения от пользователей

### 2. Parse Command
Определяет тип команды (/start, /search, или просто текст)

### 3. Ветвление:

**Если /start:**
- Отправляет приветствие

**Если /help:**
- Отправляет справку

**Если поиск:**
- Send Processing Message
- Generate Suppliers Data (5 компаний)
- OpenAI Analyze (для каждой)
- Parse AI Response
- Format Results
- Send Results

---

## 📊 ЧТО ВОЗВРАЩАЕТ БОТ

Для каждой компании:
```
🏢 #1: Yiwu Wholesale Trading Co.
⭐️ Рейтинг: 4.9/5
📊 AI-оценка: 9/10
✅ Рекомендуется

📍 Zhejiang, China
📦 MOQ: 200 pieces
💰 Цена: $3.8

📧 export@yiwu-wholesale.com
🌐 https://yiwu-wholesale.en.alibaba.com

💬 Резюме AI:
Отличная надёжная компания...

✅ Плюсы: высокий рейтинг, много сделок
⚠️ Риски: средний MOQ может быть проблемой
```

---

## 💰 СТОИМОСТЬ РАБОТЫ

### OpenAI расходы (GPT-4):

**На 1 поиск:**
- 5 компаний × ~200 tokens = ~$0.006

**На месяц:**
- 100 поисков = $0.60
- 1,000 поисков = $6.00

**Экономия:**
- Можно использовать **gpt-3.5-turbo** (в 10 раз дешевле)
- В узле "OpenAI Analyze" измените model на `gpt-3.5-turbo`

---

## 🆙 УЛУЧШЕНИЯ

### Добавить Google Sheets

После узла "Parse AI Response" добавьте:

1. **Google Sheets** узел
2. **Operation**: Append
3. **Document ID**: ваш sheet ID
4. **Sheet Name**: Leads
5. Мапинг полей

### Добавить подписки

Добавьте узлы для:
- Проверки лимитов пользователя
- Обработки платежей (YooKassa)
- Управления подписками

### Добавить реальный парсинг

Замените "Generate Suppliers Data" на:
- HTTP Request к Alibaba
- Парсинг HTML через Cheerio
- Или интеграцию с ScraperAPI

---

## 🐛 TROUBLESHOOTING

### Бот не отвечает

✅ Проверьте что workflow **Active**
✅ Проверьте что Telegram credential настроен
✅ Проверьте логи выполнения в n8n

### OpenAI ошибка

✅ Проверьте баланс: https://platform.openai.com/usage
✅ Проверьте API key в credential
✅ Пополните счет минимум на $5

### Неправильный формат ответа

✅ В узле "Parse AI Response" есть fallback на дефолтные значения
✅ Проверьте логи AI Response
✅ Попробуйте увеличить maxTokens до 500

---

## 🆚 СРАВНЕНИЕ С WEBHOOK ВЕРСИЕЙ

| Параметр | Webhook v3 | Telegram Trigger |
|----------|-----------|------------------|
| **Python бот** | Нужен | НЕ нужен ✅ |
| **VPS для бота** | Нужен | НЕ нужен ✅ |
| **Настройка** | Сложнее | Проще ✅ |
| **Точек отказа** | Больше | Меньше ✅ |
| **Зависимостей** | Больше | Меньше ✅ |
| **Стоимость** | VPS + n8n | Только n8n ✅ |

**Рекомендация:** Используйте **Telegram Trigger** - это проще!

---

## ✅ ЧЕКЛИСТ ГОТОВНОСТИ

```
☐ Workflow импортирован
☐ Telegram credential настроен
☐ Telegram credential применён ко всем узлам
☐ OpenAI credential настроен
☐ Workflow активирован (Active)
☐ Протестировано через /start
☐ Протестирован поиск
☐ Бот работает! 🎉
```

---

## 🎉 ГОТОВО!

Ваш AI-агент полностью работает в n8n!

**Python бот больше не нужен!**

Просто активируйте workflow и пользуйтесь! 🚀

---

## 📞 НУЖНА ПОМОЩЬ?

- Проверьте логи выполнения в n8n
- Убедитесь что все credentials настроены
- Проверьте что workflow Active

**Удачи!** 🎊
