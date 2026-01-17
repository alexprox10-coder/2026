# 📊 ChinaLeadBot - Telegram с Таблицей

## ✨ ЧТО НОВОГО

Вместо отдельных сообщений для каждой компании, бот теперь отправляет **одну красивую таблицу** со всеми поставщиками!

### Пример результата:

```
📊 Найдено 5 поставщиков: wireless headphones

⭐️ 1. Yiwu Wholesale Trading Co.
┣ 🎯 AI: 9/10 | ⭐️ 4.9/5
┣ 📦 MOQ: 200 шт | 💰 $3.80
┣ 📍 Zhejiang, China
┣ 📧 export@yiwu-wholesale.com
┣ 🌐 https://yiwu-wholesale.en.alibaba.com
┣ ✅ Высокий рейтинг, много транзакций
┗ ⚠️ Средний MOQ может быть проблемой

⭐️ 2. Shanghai Premium Exports Inc.
┣ 🎯 AI: 8/10 | ⭐️ 4.7/5
┣ 📦 MOQ: 300 шт | 💰 $6.50
...

_Все данные сохранены в Google Sheets_ 📝
```

---

## 🚀 НАСТРОЙКА (5 минут)

### Шаг 1: Импортируйте workflow

1. Откройте n8n
2. **Workflows → Import from File**
3. Выберите:
   ```
   /home/user/2026/china-lead-bot/workflows/telegram_with_table.json
   ```
4. Нажмите **Import**

---

### Шаг 2: Настройте Telegram Credential

1. Кликните на узел **"Telegram Trigger"**
2. В правой панели найдите **Credentials**
3. Нажмите **Create New Credential**
4. Выберите **"Telegram API"**

**Заполните:**
```
Access Token: 8385249886:AAE7zDQznQ3nKjmRGr9Ix7LsvJqqcp5tMLU
```

5. Нажмите **Save**
6. Примените этот credential ко всем Telegram узлам (Send Welcome, Send Help, Send Processing, Send Table to Telegram)

---

### Шаг 3: Настройте AI API Credential

**ВАЖНО:** Этот workflow использует **HTTP Request** вместо LangChain узла!

1. Кликните на узел **"AI Analyze (HTTP)"**
2. В **Credentials** нажмите **Create New Credential**
3. Выберите **"OpenAI API"** (даже если у вас aggregator)
4. Вставьте ваш API Key

**Если у вас API aggregator:**
В узле "AI Analyze (HTTP)" измените поле `url`:
```
{{ $json.api_url }}
```

На ваш endpoint, например:
```
https://your-api-aggregator.com/v1/chat/completions
```

**Модель уже настроена:**
```json
"model": "ANTHROPIC/CLAUDE-3.5-SONNET"
```

Если ваш aggregator использует другое название модели, измените его в поле `jsonBody`.

---

### Шаг 4: Настройте Google Sheets

1. Создайте таблицу на https://sheets.google.com
2. Назовите лист: **"Leads"**
3. В первую строку добавьте заголовки:
   ```
   Timestamp | User_ID | User_Name | Chat_ID | Category | Company | Rating | Years | MOQ | Price | Location | Email | URL | AI_Score | Recommended | Summary | Pros | Risks
   ```

4. Скопируйте ID таблицы из URL:
   ```
   https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit
                                          ^^^^^^^^^^^^^^^^^^^
                                          Это ваш Sheet ID
   ```

5. В n8n кликните узел **"Save to Google Sheets"**
6. **Credentials → Create New**
7. Выберите **"Google Sheets OAuth2 API"**
8. Нажмите **"Connect my account"** → войдите через Google
9. В поле **Document ID** замените `YOUR_SHEET_ID` на скопированный ID
10. **Sheet Name**: `Leads`
11. **Save**

---

### Шаг 5: АКТИВИРУЙТЕ Workflow

1. Вверху справа найдите переключатель **Inactive**
2. **Кликните** чтобы активировать
3. Должен стать **Active** (зелёный)

---

## ✅ ТЕСТИРОВАНИЕ

### 1. Откройте Telegram

Найдите вашего бота

### 2. Отправьте /start

Должен ответить приветствием

### 3. Попробуйте поиск

Напишите:
```
wireless headphones
```

Бот должен:
1. Отправить "🔍 Поиск запущен!"
2. Через 10-30 секунд вернуть **красивую таблицу с 5 компаниями**
3. Все данные сохранятся в Google Sheets

---

## 🔧 КАК РАБОТАЕТ

### Основной поток:

```
Telegram Trigger
   ↓
Parse Command (определяет команду)
   ↓
Send Processing ("Поиск запущен!")
   ↓
Generate Suppliers (создаёт 5 компаний)
   ↓
AI Analyze (HTTP) ← Использует HTTP Request для вашего API
   ↓
Parse AI Response (обрабатывает ответ AI)
   ↓
Save to Google Sheets (сохраняет все данные)
   ↓
Format as Table (форматирует как таблицу)
   ↓
Send Table to Telegram (отправляет ОДНО сообщение)
```

### Что делает узел "Format as Table":

```javascript
// Собирает все 5 компаний в одно сообщение
items.forEach((item, index) => {
  message += `⭐️ ${num}. ${company_name}\n`;
  message += `┣ 🎯 AI: ${ai_score}/10 | ⭐️ ${rating}/5\n`;
  message += `┣ 📦 MOQ: ${moq} | 💰 ${price}\n`;
  message += `┣ 📍 ${location}\n`;
  message += `┣ 📧 ${email}\n`;
  message += `┣ 🌐 ${url}\n`;
  message += `┣ ✅ ${pros}\n`;
  message += `┗ ⚠️ ${risks}\n\n`;
});
```

---

## 🆚 ОТЛИЧИЯ ОТ ПРЕДЫДУЩИХ ВЕРСИЙ

| Параметр | Старая версия | Новая версия |
|----------|--------------|--------------|
| **Формат вывода** | 5 отдельных сообщений | 1 таблица ✅ |
| **AI узел** | LangChain (не работает) | HTTP Request ✅ |
| **Совместимость** | Только OpenAI | Любой API aggregator ✅ |
| **Читаемость** | Сложно сравнить | Легко сравнить ✅ |
| **Telegram спам** | 5+ сообщений | 1 сообщение ✅ |

---

## 🎨 НАСТРОЙКА ТАБЛИЦЫ

### Изменить символы таблицы:

В узле "Format as Table" найдите:
```javascript
message += `┣ 🎯 AI: ${d.ai_score}/10\n`;
message += `┗ ⚠️ ${d.risks}\n\n`;
```

Можно заменить на:
```javascript
message += `├ 🎯 AI: ${d.ai_score}/10\n`;
message += `└ ⚠️ ${d.risks}\n\n`;
```

Или использовать простые символы:
```javascript
message += `- 🎯 AI: ${d.ai_score}/10\n`;
message += `- ⚠️ ${d.risks}\n\n`;
```

### Добавить больше полей:

```javascript
message += `┣ 📞 Response rate: ${d.response_rate}\n`;
message += `┣ 💼 Transactions: ${d.total_transactions}\n`;
```

### Изменить эмодзи:

```javascript
const star = d.recommended === 'YES' ? '✅' : '⚪️';
```

---

## 🐛 TROUBLESHOOTING

### Бот отправляет пустое сообщение

✅ Проверьте что все 5 компаний прошли через AI Analyze
✅ Проверьте логи в узле "Format as Table"
✅ Убедитесь что `items.length > 0`

### AI Analyze возвращает ошибку

✅ Проверьте что URL вашего API указан правильно
✅ Проверьте что модель `ANTHROPIC/CLAUDE-3.5-SONNET` поддерживается
✅ Проверьте баланс API

### Таблица не форматируется

✅ Убедитесь что Telegram parse_mode = "Markdown"
✅ Попробуйте HTML mode: `parse_mode: "HTML"` и замените `*` на `<b>`

### Google Sheets не сохраняет

✅ Проверьте что заголовки в Sheet совпадают с названиями колонок
✅ Проверьте OAuth credential
✅ Убедитесь что Document ID правильный

---

## 📊 ПРИМЕР ВЫВОДА В GOOGLE SHEETS

| Timestamp | User_ID | User_Name | Category | Company | AI_Score | Recommended | Summary | Pros | Risks |
|-----------|---------|-----------|----------|---------|----------|-------------|---------|------|-------|
| 2026-01-17 12:34 | 12345 | Ivan | wireless headphones | Yiwu Wholesale | 9 | YES | Отличный поставщик | Высокий рейтинг | Средний MOQ |

Все поиски пользователей сохраняются → можно анализировать!

---

## 🎉 ГОТОВО!

Теперь ваш бот отправляет красивые таблицы в Telegram!

**Преимущества:**
- ✅ Все данные в одном сообщении
- ✅ Легко сравнивать поставщиков
- ✅ Не спамит чат
- ✅ Работает с любым AI API
- ✅ Все сохраняется в Google Sheets

**Запускайте и тестируйте!** 🚀
