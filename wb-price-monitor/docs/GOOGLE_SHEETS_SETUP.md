# 📊 Настройка Google Sheets для WB Price Monitor

---

## 🎯 Структура таблицы

Нужно создать **одну Google таблицу** с **двумя листами**:

1. **Products** - текущие товары на мониторинге
2. **Price_History** - полная история изменений цен

---

## 📝 Шаг 1: Создать Google Sheets

1. Откройте: https://docs.google.com/spreadsheets/
2. Нажмите **"Создать"** (зеленый плюс)
3. Назовите таблицу: **"WB Price Monitor - Database"**

---

## 📋 Шаг 2: Настроить лист "Products"

**Переименуйте Sheet1 → Products**

**Создайте заголовки** (первая строка):

| A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Timestamp | User_ID | User_Name | Chat_ID | Article_ID | Product_Name | Brand | Price | Previous_Price | Discount | Rating | Feedbacks | Seller | URL | Active |

**Формат столбцов:**

- **Timestamp** - Дата и время (формат: `17.01.2026 12:00:00`)
- **User_ID** - Число
- **User_Name** - Текст
- **Chat_ID** - Число
- **Article_ID** - Текст (важно! Не число, чтобы не терять ведущие нули)
- **Product_Name** - Текст
- **Brand** - Текст
- **Price** - Число (формат: `# ##0.00 ₽`)
- **Previous_Price** - Число (формат: `# ##0.00 ₽`)
- **Discount** - Число (формат: `0%`)
- **Rating** - Число (формат: `0.0`)
- **Feedbacks** - Число
- **Seller** - Текст
- **URL** - Текст
- **Active** - Чекбокс (TRUE/FALSE)

---

## 📋 Шаг 3: Создать лист "Price_History"

**Создать новый лист** (внизу + кнопка) → назвать **"Price_History"**

**Создайте заголовки:**

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| Timestamp | User_ID | Article_ID | Product_Name | Price | Previous_Price | Price_Change | Change_Percent | Notified |

**Формат столбцов:**

- **Timestamp** - Дата и время
- **User_ID** - Число
- **Article_ID** - Текст
- **Product_Name** - Текст
- **Price** - Число (`# ##0.00 ₽`)
- **Previous_Price** - Число (`# ##0.00 ₽`)
- **Price_Change** - Число (`+# ##0.00 ₽`) - может быть отрицательным
- **Change_Percent** - Число (`+0.0%`) - может быть отрицательным
- **Notified** - Чекбокс (TRUE/FALSE)

---

## 🔗 Шаг 4: Получить ID таблицы

**URL таблицы выглядит так:**
```
https://docs.google.com/spreadsheets/d/1ABC123XYZ456_THIS_IS_ID/edit#gid=0
                                    ^^^^^^^^^^^^^^^^^^^^^
                                    Это ID таблицы
```

**Скопируйте ID** и вставьте в workflow:
```json
"documentId": {
  "mode": "list",
  "value": "1ABC123XYZ456_THIS_IS_ID"
}
```

---

## 🔑 Шаг 5: Настроить OAuth2 в n8n

### В Google Cloud Console:

1. Откройте: https://console.cloud.google.com/
2. Создайте новый проект: **"WB Price Monitor"**
3. Включите **Google Sheets API**:
   - APIs & Services → Library
   - Найдите "Google Sheets API"
   - Нажмите Enable
4. Создайте OAuth2 credentials:
   - APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - Application type: Web application
   - Name: n8n WB Price Monitor
   - Authorized redirect URIs: `https://n8n.arendadom24.ru/rest/oauth2-credential/callback`
5. Сохраните:
   - **Client ID**
   - **Client Secret**

### В n8n:

1. Credentials → New
2. Выберите: **Google Sheets OAuth2 API**
3. Вставьте Client ID и Client Secret
4. Нажмите **Connect my account**
5. Авторизуйтесь через Google
6. Сохраните credential

---

## 📊 Шаг 6: Примеры данных (для тестирования)

**Добавьте в лист Products:**

| Timestamp | User_ID | User_Name | Chat_ID | Article_ID | Product_Name | Brand | Price | Previous_Price | Discount | Rating | Feedbacks | Seller | URL | Active |
|-----------|---------|-----------|---------|------------|--------------|-------|-------|----------------|----------|--------|-----------|--------|-----|--------|
| 17.01.2026 12:00 | 123456 | Ivan | 123456 | 12345678 | Наушники беспроводные | Apple | 2999 | 3499 | 14% | 4.8 | 1234 | ООО Поставщик | https://... | TRUE |

---

## 🔄 Логика работы с таблицей

### Добавление товара (/add):

1. Пользователь: `/add 12345678`
2. Бот запрашивает WB API
3. Сохраняет в **Products** с `Active = TRUE`
4. Сохраняет первую запись в **Price_History**

### Проверка цен (Cron каждый час):

1. Читает все строки из **Products** где `Active = TRUE`
2. Для каждой строки:
   - Запрашивает текущую цену WB API
   - Сравнивает с `Previous_Price`
   - Если изменилась:
     - Обновляет `Price` и `Previous_Price` в **Products**
     - Добавляет запись в **Price_History**
     - Отправляет уведомление пользователю

### Удаление товара (/remove):

1. Пользователь: `/remove 12345678`
2. Находит строку в **Products** по `Article_ID` и `User_ID`
3. Устанавливает `Active = FALSE`
4. (Не удаляет строку - для истории)

---

## 📈 Формулы Google Sheets (полезные)

### Подсчет активных товаров пользователя:

```
=COUNTIFS(Products!B:B, 123456, Products!O:O, TRUE)
```
Где `123456` - User_ID

### Средняя экономия на скидках:

```
=AVERAGE(Products!J:J)
```

### Топ-3 товара с наибольшим снижением цены:

```
=SORT(Price_History!A:I, 8, FALSE)
```
Сортирует по столбцу H (Change_Percent) по убыванию

---

## ✅ Проверка настройки

**Чек-лист:**

- ✅ Создана таблица "WB Price Monitor - Database"
- ✅ Лист "Products" с 15 столбцами
- ✅ Лист "Price_History" с 9 столбцами
- ✅ Скопирован ID таблицы
- ✅ Включен Google Sheets API
- ✅ Созданы OAuth2 credentials
- ✅ Подключено в n8n

---

## 🚀 Готово!

Теперь таблица готова для интеграции с n8n workflow!
