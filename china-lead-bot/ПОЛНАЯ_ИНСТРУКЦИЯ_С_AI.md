# 🚀 ПОЛНАЯ ВЕРСИЯ с AI и Google Sheets

## ✅ ДВА ФАЙЛА - ДВА ВАРИАНТА

### 1. **FINAL_WORKING_100_PERCENT.json** - ПРОСТАЯ (начните с неё)
- Без AI
- Без Google Sheets
- Работает сразу после настройки Telegram
- **Используйте для теста!**

### 2. **FINAL_WITH_AI_AND_SHEETS.json** - ПОЛНАЯ (когда простая заработает)
- С AI анализом (OpenRouter)
- С сохранением в Google Sheets
- Требует больше настройки
- **Используйте когда простая заработает!**

---

## 📋 ПЛАН ДЕЙСТВИЙ

### СНАЧАЛА:
1. ✅ Импортируйте `FINAL_WORKING_100_PERCENT.json`
2. ✅ Настройте Telegram
3. ✅ Протестируйте - должно работать!

### ПОТОМ (когда простая заработает):
4. ✅ Импортируйте `FINAL_WITH_AI_AND_SHEETS.json`
5. ✅ Настройте OpenRouter API
6. ✅ Настройте Google Sheets
7. ✅ Протестируйте полную версию

---

## 🎯 НАСТРОЙКА ПОЛНОЙ ВЕРСИИ

### Шаг 1: Telegram (5 узлов)

Токен: `8385249886:AAE7zDQznQ3nKjmRGr9Ix7LsvJqqcp5tMLU`

Примените к:
- Telegram Trigger
- Send Welcome
- Send Help
- Send Processing
- Send Result

---

### Шаг 2: OpenRouter API

**Кликните узел "AI Analyze"**

В разделе Headers найдите:
```
Authorization: Bearer ВАШ_OPENROUTER_API_KEY
```

**Замените на ваш ключ:**
1. Откройте credential "OpenAI_ВК_ПАРСЕР_ЛИД"
2. Скопируйте API Key (начинается с `sk-or-v1-...`)
3. Вставьте вместо `ВАШ_OPENROUTER_API_KEY`

Должно стать:
```
Authorization: Bearer sk-or-v1-ваш-реальный-ключ
```

---

### Шаг 3: Google Sheets

**3.1. Создайте таблицу:**
1. https://sheets.google.com
2. Создайте новую таблицу
3. Назовите лист: `Leads`

**3.2. Добавьте заголовки (первая строка):**
```
Timestamp | User_ID | User_Name | Chat_ID | Category | Company | Rating | MOQ | Price | Location | Email | URL | AI_Score | Recommended | Pros | Risks
```

**3.3. Скопируйте ID таблицы:**
URL выглядит так:
```
https://docs.google.com/spreadsheets/d/1ABC123XYZ789/edit
                                          ^^^^^^^^^^^^
                                          Это ваш Sheet ID
```

**3.4. В n8n:**
- Кликните узел "Save to Google Sheets"
- Document ID: вставьте ваш ID вместо `ВАШ_GOOGLE_SHEET_ID`
- Sheet Name: `Leads`
- Credentials: создайте Google Sheets OAuth2
- Нажмите "Connect my account" и войдите через Google

---

## ✅ АКТИВАЦИЯ

```
Вверху справа: Inactive → Active
```

---

## 🧪 ТЕСТИРОВАНИЕ

Отправьте боту:
```
wireless headphones
```

**Через 20 секунд получите:**

```
📊 wireless headphones (3 компаний)

⭐️ 1. Yiwu Wholesale Trading Co.
🎯 AI: 9/10 | 📊 4.9/5
📦 200 шт | 💰 $3.80
📍 Zhejiang
📧 export@yiwu-wholesale.com
🌐 yiwu-wholesale.en.alibaba.com
✅ Высокий рейтинг, быстрый ответ
⚠️ Средний MOQ

⭐️ 2. Shanghai Premium Exports
🎯 AI: 8/10 | 📊 4.7/5
...

_Сохранено в Google Sheets_ 📝
```

**Проверьте Google Sheets** - должно быть 3 новые строки с данными!

---

## 🔍 КАК ПРОВЕРИТЬ ЧТО ВСЁ РАБОТАЕТ

### 1. Проверка Generate Suppliers

Откройте n8n → Executions → последнее выполнение

Кликните узел **"Generate Suppliers"**

OUTPUT должен быть:
```json
[
  {
    "company_name": "Yiwu Wholesale Trading Co.",
    "rating": 4.9,
    "chat_id": 7984101063,
    ...
  },
  {
    "company_name": "Shanghai Premium Exports",
    ...
  },
  {
    "company_name": "Shenzhen Tech Electronics",
    ...
  }
]
```

✅ Если видите 3 объекта с данными - работает!

---

### 2. Проверка AI Analyze

Кликните узел **"AI Analyze"**

OUTPUT должен быть:
```json
{
  "id": "gen-...",
  "choices": [{
    "message": {
      "content": "{\"ai_score\": 9, \"recommended\": \"YES\", ...}"
    }
  }]
}
```

✅ Если видите `choices` и `content` - AI работает!

---

### 3. Проверка Merge Company and AI Data

Кликните узел **"Merge Company and AI Data"**

OUTPUT должен быть:
```json
{
  "company_name": "Yiwu Wholesale Trading Co.",
  "rating": 4.9,
  "moq": "200 шт",
  "chat_id": 7984101063,
  "ai_score": 9,
  "recommended": "YES",
  "pros": "Высокий рейтинг",
  "risks": "Средний MOQ"
}
```

✅ Если видите И company_name И ai_score - данные объединяются!

---

### 4. Проверка Google Sheets

Откройте вашу таблицу

Должны быть строки с **РЕАЛЬНЫМИ** данными:
```
2026-01-17 | 12345 | Александр | 7984101063 | wireless headphones | Yiwu Wholesale | 4.9 | ...
```

✅ Если данные реальные (не {{ $json... }}) - всё работает!

---

### 5. Проверка Format Message

Кликните узел **"Format Message"**

OUTPUT должен быть:
```json
{
  "chat_id": 7984101063,
  "message": "📊 *wireless headphones* (3 компаний)\n\n⭐️ 1. Yiwu..."
}
```

✅ Если есть И chat_id И message - форматирование работает!

---

## 🐛 TROUBLESHOOTING

### Ошибка: "Authorization failed" в AI Analyze

✅ Проверьте OpenRouter API key в Headers
✅ Ключ должен начинаться с `sk-or-v1-`
✅ Header должен быть: `Authorization: Bearer sk-or-v1-...`

---

### Ошибка: Google Sheets сохраняет {{ $json.company_name }}

✅ Проверьте узел "Merge Company and AI Data"
✅ Убедитесь что он ВОЗВРАЩАЕТ все поля
✅ Код должен содержать:
```javascript
return {
  json: {
    company_name: company.company_name,
    ai_score: ai.ai_score,
    // ... все остальные поля
  }
};
```

---

### Ошибка: "chat_id отсутствует"

✅ Узел "Format Message" берёт chat_id из:
```javascript
const chatId = items[0].json.chat_id;
```

✅ Проверьте что узел "Merge Company and AI Data" возвращает chat_id

---

## 📊 СТРУКТУРА WORKFLOW

```
Telegram Trigger
  ↓
Parse Command
  ↓
Is Start? → Send Welcome
  ↓
Is Help? → Send Help
  ↓
Send Processing ("Поиск запущен!")
  ↓
Generate Suppliers (3 компании с данными)
  ↓
AI Analyze (OpenRouter → Claude 3.5 Sonnet)
  ↓
Merge Company and AI Data ⭐ (ОБЪЕДИНЯЕТ данные!)
  ↓
Save to Google Sheets (сохраняет 16 полей)
  ↓
Format Message (создаёт таблицу)
  ↓
Send Result (отправляет в Telegram)
```

---

## 🎯 КЛЮЧЕВЫЕ ОТЛИЧИЯ ОТ ПРЕДЫДУЩИХ ВЕРСИЙ

### ❌ Старая проблема:
- Данные терялись между узлами
- chat_id не передавался
- AI response заменял данные компании

### ✅ Как исправлено:

**1. Узел "Merge Company and AI Data":**
```javascript
const company = $node["Generate Suppliers"].json[index];
const aiResp = $input.item.json;

return {
  json: {
    ...company,  // ВСЕ данные компании
    ...ai        // + AI анализ
  }
};
```

**2. Узел "Format Message":**
```javascript
const chatId = items[0].json.chat_id;  // Берёт из объединённых данных

return {
  json: {
    chat_id: chatId,  // ОБЯЗАТЕЛЬНО!
    message: message
  }
};
```

---

## 🎉 ГОТОВО!

Теперь у вас **ДВА WORKFLOW**:

1. **Простой** (без AI, без Sheets) - для быстрого теста
2. **Полный** (с AI, с Sheets) - для продакшена

**НАЧНИТЕ С ПРОСТОГО**, когда он заработает - переходите к полному!

---

## 📝 ФАЙЛЫ

```
/home/user/2026/china-lead-bot/workflows/FINAL_WORKING_100_PERCENT.json
/home/user/2026/china-lead-bot/workflows/FINAL_WITH_AI_AND_SHEETS.json
```

**ИСПОЛЬЗУЙТЕ ИХ В ТАКОМ ПОРЯДКЕ!** 🚀
