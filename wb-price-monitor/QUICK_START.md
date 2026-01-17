# 🚀 Quick Start - Запуск за 30 минут

---

## ✅ Чек-лист перед запуском

- [ ] Есть аккаунт n8n
- [ ] Есть Telegram бот (токен)
- [ ] Есть Google аккаунт
- [ ] Есть OpenRouter API ключ (для AI)

---

## 📋 Шаг 1: Создать Telegram бота (5 мин)

1. Откройте Telegram
2. Найдите **@BotFather**
3. Отправьте: `/newbot`
4. Введите название: `WB Price Monitor Bot`
5. Введите username: `your_wb_monitor_bot`
6. **Сохраните токен:** `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

**Настройте бота:**
```
/setdescription - Мониторинг цен конкурентов на Wildberries
/setabouttext - Автоматические уведомления при изменении цен
/setuserpic - Загрузите иконку (можно пропустить)
```

---

## 📊 Шаг 2: Создать Google Sheets (5 мин)

1. Откройте: https://docs.google.com/spreadsheets/
2. Создайте новую таблицу: **"WB Price Monitor - Database"**

**Лист 1: Products**

Заголовки (первая строка):
```
Timestamp | User_ID | User_Name | Chat_ID | Article_ID | Product_Name | Brand | Price | Previous_Price | Discount | Rating | Feedbacks | Seller | URL | Active
```

**Лист 2: Price_History**

Заголовки:
```
Timestamp | User_ID | Article_ID | Product_Name | Price | Previous_Price | Price_Change | Change_Percent | Notified
```

**Сохраните ID таблицы** из URL:
```
https://docs.google.com/spreadsheets/d/1ABC123XYZ456/edit
                                        ^^^^^^^^^^^^^ ID
```

---

## 🔑 Шаг 3: Настроить OAuth2 (10 мин)

### Google Cloud Console:

1. https://console.cloud.google.com/
2. Создайте проект: "WB Price Monitor"
3. **APIs & Services** → **Library**
4. Найдите и включите: **Google Sheets API**
5. **Credentials** → **Create Credentials** → **OAuth client ID**
6. Application type: **Web application**
7. Authorized redirect URIs: `https://n8n.arendadom24.ru/rest/oauth2-credential/callback`
8. Сохраните:
   - Client ID
   - Client Secret

### В n8n:

1. **Credentials** → **New**
2. Тип: **Google Sheets OAuth2 API**
3. Вставьте Client ID и Client Secret
4. **Connect my account** → авторизуйтесь
5. Сохраните credential

---

## 🔌 Шаг 4: Импортировать workflow в n8n (5 мин)

1. Откройте файл: `workflows/WB_PRICE_MONITOR_MAIN.json`
2. В n8n: **Import from File**
3. Выберите файл
4. **Откройте workflow**

**Замените в нодах:**

### Telegram Trigger нода:
```json
"credentials": {
  "telegramApi": {
    "id": "ВАШ_CREDENTIAL_ID",
    "name": "Telegram Bot"
  }
}
```

### Google Sheets нода:
```json
"documentId": {
  "value": "ВАШ_GOOGLE_SHEET_ID"
}
```

### HTTP Request (AI) нода:
```json
"Authorization": "Bearer ВАШ_OPENROUTER_API_KEY"
```

---

## 🧪 Шаг 5: Протестировать (5 мин)

1. **Активируйте workflow** (переключатель Active)
2. Откройте бота в Telegram
3. Отправьте: `/start`
4. Должно прийти приветственное сообщение!

**Тест добавления товара:**

1. Найдите любой товар на WB
2. Скопируйте артикул (из URL или со страницы)
3. Отправьте боту: `/add 123456789`
4. Должна прийти информация о товаре!
5. Проверьте Google Sheets - там должна появиться строка!

---

## ✅ Готово!

Ваш WB Price Monitor работает! 🎉

### Что дальше:

1. **Тестируйте** на разных артикулах
2. **Добавьте Cron** для автоматической проверки (отдельный workflow)
3. **Настройте AI анализ** (импортируйте WB_AI_ANALYSIS.json)
4. **Пригласите друзей** на бета-тест

---

## 🐛 Troubleshooting

### Бот не отвечает:
- ✅ Проверьте что workflow **Active**
- ✅ Проверьте Telegram credential в n8n
- ✅ Проверьте токен бота правильный

### Ошибка "Sheet not found":
- ✅ Проверьте ID таблицы правильный
- ✅ Проверьте названия листов: "Products" и "Price_History"
- ✅ Проверьте OAuth2 credential подключен

### Ошибка "Article not found":
- ✅ Проверьте артикул правильный (только цифры)
- ✅ Проверьте товар существует на WB
- ✅ Попробуйте другой артикул

### AI не работает:
- ✅ Проверьте OpenRouter API ключ
- ✅ Проверьте баланс на OpenRouter
- ✅ Проверьте model: `anthropic/claude-3.5-sonnet`

---

## 📞 Поддержка

Если что-то не работает - проверьте:
1. Логи workflow в n8n (Executions)
2. Документацию в `/docs/`
3. README.md

Удачи! 🚀
