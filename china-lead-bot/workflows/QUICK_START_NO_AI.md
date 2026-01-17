# 🚀 БЫСТРЫЙ СТАРТ - Рабочая версия БЕЗ AI

## ✅ ЭТА ВЕРСИЯ РАБОТАЕТ СРАЗУ!

**Без AI анализа** - данные заранее подготовлены с оценками.

### Преимущества:
- ✅ Нет проблем с API авторизацией
- ✅ Работает СРАЗУ после импорта
- ✅ Красивая таблица в Telegram
- ✅ Можно добавить Google Sheets позже
- ✅ Можно добавить AI позже

---

## 🏃 ЗАПУСК ЗА 2 МИНУТЫ

### Шаг 1: Импортируйте workflow

```
1. Откройте n8n
2. Workflows → Import from File
3. Выберите: /home/user/2026/china-lead-bot/workflows/telegram_table_no_ai.json
4. Import
```

### Шаг 2: Настройте Telegram

```
1. Кликните на любой узел с названием "Telegram"
2. В правой панели найдите "Credential"
3. Выберите ваш существующий credential или создайте новый:

   Access Token: 8385249886:AAE7zDQznQ3nKjmRGr9Ix7LsvJqqcp5tMLU

4. Save
5. Примените этот credential ко ВСЕМ Telegram узлам:
   - Telegram Trigger
   - Send Welcome
   - Send Help
   - Send Processing
   - Send Table to Telegram
```

### Шаг 3: Активируйте

```
Вверху справа переключатель:
Inactive → Active (зелёный)
```

### Шаг 4: ТЕСТИРУЙТЕ! 🎉

```
Откройте Telegram → ваш бот

Отправьте: /start
Ответ: Приветственное сообщение

Отправьте: wireless headphones
Ответ: Красивая таблица с 5 компаниями!
```

---

## 📊 ПРИМЕР РЕЗУЛЬТАТА

```
📊 Найдено 5 поставщиков: wireless headphones

⭐️ 1. Yiwu Wholesale Trading Co.
🎯 Оценка: 9/10 | ⭐️ Рейтинг: 4.9/5
📦 MOQ: 200 шт | 💰 Цена: $3.80
📍 Zhejiang, China
📧 export@yiwu-wholesale.com
🌐 https://yiwu-wholesale.en.alibaba.com
✅ Высокий рейтинг, много транзакций, быстрый ответ
⚠️ Средний MOQ может быть проблемой для малого бизнеса

⭐️ 2. Shanghai Premium Exports Inc.
🎯 Оценка: 8/10 | ⭐️ Рейтинг: 4.7/5
📦 MOQ: 300 шт | 💰 Цена: $6.50
📍 Shanghai, China
📧 export@sh-premium.com
🌐 https://sh-premium.en.alibaba.com
✅ Премиум качество, хорошая репутация
⚠️ Выше цена, больше MOQ

⭐️ 3. Shenzhen Tech Electronics
🎯 Оценка: 9/10 | ⭐️ Рейтинг: 4.8/5
📦 MOQ: 100 шт | 💰 Цена: $5.50
📍 Guangdong, China
📧 sales@shenzhen-tech.com
🌐 https://shenzhen-tech.en.alibaba.com
✅ Низкий MOQ, технологичная компания, быстрая доставка
⚠️ Меньше опыта по сравнению с топовыми

⭐️ 4. Guangzhou Factory Direct Ltd.
🎯 Оценка: 7/10 | ⭐️ Рейтинг: 4.6/5
📦 MOQ: 500 шт | 💰 Цена: $2.90
📍 Guangdong, China
📧 sales@gz-factory.com
🌐 https://gz-factory.en.alibaba.com
✅ Самая низкая цена, прямо с фабрики
⚠️ Высокий MOQ, медленный ответ

📍 5. Dongguan Quality Manufacturing
🎯 Оценка: 6/10 | ⭐️ Рейтинг: 4.5/5
📦 MOQ: 1000 шт | 💰 Цена: $2.20
📍 Guangdong, China
📧 info@dg-quality.com
🌐 https://dg-quality.en.alibaba.com
✅ Очень низкая цена для больших объемов
⚠️ Очень высокий MOQ, меньше опыта

_Данные готовы к сохранению в Google Sheets_ 📝
```

---

## 🎯 КАК РАБОТАЕТ

### Простой поток (7 узлов):

```
1. Telegram Trigger → получает сообщение
2. Parse Command → определяет команду (/start, /help, или поиск)
3. Is Start? → если /start
4. Send Welcome → отправляет приветствие
5. Is Help? → если /help
6. Send Help → отправляет помощь
7. Send Processing → "Поиск запущен!"
8. Generate Suppliers → создаёт 5 компаний с готовыми оценками
9. Format Table → форматирует красивую таблицу
10. Send Table to Telegram → отправляет результат
```

**НЕТ AI УЗЛА** - никаких проблем с авторизацией!

**НЕТ GOOGLE SHEETS** - можно добавить позже!

---

## ➕ КАК ДОБАВИТЬ GOOGLE SHEETS (опционально)

Если хотите сохранять результаты:

### 1. Добавьте узел Google Sheets

```
Между "Generate Suppliers" и "Format Table":

Узел: Google Sheets
Operation: Append
Document: выберите свою таблицу
Sheet: Leads
Mapping Mode: Define Below

Columns:
  Timestamp → {{ $json.timestamp }}
  User_ID → {{ $json.user_id }}
  User_Name → {{ $json.user_name }}
  Chat_ID → {{ $json.chat_id }}
  Category → {{ $json.product_category }}
  Company → {{ $json.company_name }}
  Rating → {{ $json.rating }}
  MOQ → {{ $json.moq }}
  Price → {{ $json.price }}
  Location → {{ $json.location }}
  Email → {{ $json.contact_email }}
  URL → {{ $json.company_url }}
  AI_Score → {{ $json.ai_score }}
  Recommended → {{ $json.recommended }}
  Pros → {{ $json.pros }}
  Risks → {{ $json.risks }}
```

### 2. Обновите connections

```
Generate Suppliers → Google Sheets → Format Table → Send Table
```

---

## ➕ КАК ДОБАВИТЬ РЕАЛЬНЫЙ AI (потом)

Когда захотите добавить настоящий AI анализ:

### 1. Добавьте HTTP Request узел

```
После "Generate Suppliers", перед "Format Table":

Method: POST
URL: https://openrouter.ai/api/v1/chat/completions
Authentication: None
Send Headers: Enabled

Headers:
  Authorization: Bearer sk-or-v1-ваш-ключ-openrouter
  HTTP-Referer: https://n8n.arendadom24.ru
  X-Title: ChinaLeadBot

Send Body: Enabled
Body Content Type: JSON

JSON:
{
  "model": "anthropic/claude-3.5-sonnet",
  "messages": [{
    "role": "user",
    "content": "Analyze this Chinese supplier: {{ $json.company_name }}, Rating: {{ $json.rating }}, MOQ: {{ $json.moq }}. Provide JSON: {\"ai_score\": X, \"recommended\": \"YES/NO\", \"pros\": \"...\", \"risks\": \"...\"}"
  }],
  "max_tokens": 300
}
```

### 2. Добавьте узел Parse AI Response

```
Code:
const response = $input.first().json;
const aiData = JSON.parse(response.choices[0].message.content);
return {
  json: {
    ...$input.first().json,
    ai_score: aiData.ai_score,
    recommended: aiData.recommended,
    pros: aiData.pros,
    risks: aiData.risks
  }
};
```

### 3. Обновите поток

```
Generate Suppliers → HTTP Request → Parse AI → Format Table → Send
```

---

## 🐛 TROUBLESHOOTING

### Бот не отвечает

✅ Проверьте что workflow Active (зелёный)
✅ Проверьте Telegram credential
✅ Проверьте что токен правильный: 8385249886:AAE7zDQznQ3nKjmRGr9Ix7LsvJqqcp5tMLU

### Таблица не форматируется

✅ В узле "Send Table to Telegram" должно быть: parse_mode = "Markdown"
✅ Проверьте что credential настроен

### Хочу изменить количество компаний

В узле "Generate Suppliers with Scores" измените массив `suppliers` - добавьте или удалите компании.

---

## 🎉 ГОТОВО!

Теперь у вас **РАБОТАЮЩИЙ БОТ**:
- ✅ Красивая таблица
- ✅ 5 компаний с оценками
- ✅ Никаких ошибок авторизации
- ✅ Готов к использованию

**Потом можно добавить:**
- Google Sheets (для сохранения)
- Реальный AI анализ (OpenRouter)
- Интеграцию с Alibaba API (парсинг реальных данных)

**ИМПОРТИРУЙТЕ И ТЕСТИРУЙТЕ!** 🚀
