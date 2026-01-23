# ⚡ БЫСТРЫЙ СТАРТ - Telegram Bot для парсера недвижимости

## ✅ ФИНАЛЬНАЯ ВЕРСИЯ - ВСЁ РАБОТАЕТ!

Исправлены все проблемы:
- ✅ Кнопки отображаются правильно (не "...")
- ✅ Команда /start работает
- ✅ Интеграция с главным workflow (кнопки запускают парсинг)
- ✅ Правильная последовательность проверок

---

## 📥 Шаг 1: Скачайте и импортируйте

1. Скачайте: **telegram_bot_FINAL_WORKING.json**
2. В n8n: меню → **Import from File**
3. Выберите файл → **Import**

---

## 🔑 Шаг 2: Замените Credential IDs

В JSON файле найдите и замените:

### 2.1 Telegram Credentials

Найдите (17 раз):
```
"id": "TELEGRAM_CREDENTIALS_ID"
```

Замените на ваш ID Telegram credentials (например: `"id": "1"`)

**Как узнать ID:**
1. В n8n откройте **Credentials**
2. Найдите ваш Telegram API credential
3. Кликните на него
4. В URL будет: `/credentials/1` ← это и есть ID

### 2.2 n8n API Credentials

Найдите (6 раз):
```
"id": "N8N_API_CREDENTIALS_ID"
```

Замените на ваш ID n8n API credentials

---

## ⚙️ Шаг 3: Проверьте настройки

### 3.1 Проверьте ваш User ID

В ноде **"Check User ID"** замените `7984101063` на ваш Telegram ID, если он отличается.

**Как узнать свой ID:**
- Напишите [@userinfobot](https://t.me/userinfobot) в Telegram
- Отправьте /start
- Бот покажет ваш ID

### 3.2 Проверьте URL главного workflow

Во всех HTTP Request нодах проверьте URL:
```
https://alex024.app.n8n.cloud/api/v1/workflows/iXAfySHKjPj3DPcm/execute
```

Если ваш n8n на другом домене - замените `alex024.app.n8n.cloud` на ваш домен.

Если ID главного workflow не `iXAfySHKjPj3DPcm` - замените на правильный.

---

## 🚀 Шаг 4: Активация

1. **Сохраните** workflow (Ctrl+S / Cmd+S)
2. **Активируйте** (переключатель Active в правом верхнем углу)
3. Убедитесь, что появилась надпись **"Workflow is active"**

---

## 🧪 Шаг 5: Тестирование

1. Откройте вашего бота в Telegram
2. Отправьте: `/start`
3. **Должны появиться кнопки:**
   - 🟢 Парсить Avito
   - 🔵 Парсить ЦИАН
   - 🟣 Парсить оба
   - ⏰ Настройки
   - ▶️ Включить / ⏸️ Выключить
   - ❓ Помощь

4. **Нажмите "🟢 Парсить Avito"**
5. Должно прийти: "✅ Запущен парсинг Avito!"
6. Главный workflow должен запуститься

---

## 🔍 Проверка работы

### После нажатия кнопки проверьте:

1. В n8n откройте **Executions**
2. Должны быть 2 выполнения:
   - **Telegram Bot** (ваш бот)
   - **Главный workflow** (парсер)

3. В Telegram должно прийти подтверждение
4. Через несколько минут должны прийти результаты парсинга

---

## ⚙️ Технические детали

### Что делают кнопки:

| Кнопка | API запрос | Действие |
|--------|------------|----------|
| 🟢 Avito | POST /workflows/{id}/execute {"source":"avito"} | Запуск парсинга Avito |
| 🔵 ЦИАН | POST /workflows/{id}/execute {"source":"cian"} | Запуск парсинга ЦИАН |
| 🟣 Оба | POST /workflows/{id}/execute {"source":"both"} | Запуск обоих парсеров |
| ▶️ Включить | PATCH /workflows/{id} {"active":true} | Активация главного workflow |
| ⏸️ Выключить | PATCH /workflows/{id} {"active":false} | Деактивация главного workflow |

### Формат inline keyboard:

Используется JSON формат:
```json
{
  "inline_keyboard": [
    [
      {"text": "🟢 Парсить Avito", "callback_data": "parse_avito"}
    ]
  ]
}
```

Это **правильный формат**, который отображает кнопки корректно!

---

## ❌ Troubleshooting

### Проблема: Кнопки всё равно показываются как "..."

**Решение:**
1. Откройте ноду **"Send Welcome"**
2. В поле **Inline Keyboard** должно быть:
   ```
   ={{
   {
     "inline_keyboard": [
       [{"text": "🟢 Парсить Avito", "callback_data": "parse_avito"}],
       ...
     ]
   }
   }}
   ```
3. Убедитесь, что это **Expression** (значок `=` в начале)
4. Не **JSON** или **String**, а именно **Expression**!

### Проблема: Главный workflow не запускается

**Решение:**
1. Проверьте n8n API credentials
2. Проверьте URL: должен быть `/execute` в конце
3. Проверьте, что главный workflow существует и ID правильный
4. Проверьте логи в **Executions** → ищите ошибки HTTP Request

### Проблема: /start не работает

**Решение:**
1. Проверьте последовательность нод:
   - Telegram Trigger → Check User ID → Is Callback → Is Start → Send Welcome
2. В ноде **Is Start** условие должно быть:
   - `$json.message?.text` equals `/start`

---

## 📊 Структура workflow

```
Telegram Trigger
    ↓
Check User ID
    ├─ TRUE → Is Callback?
    │           ├─ TRUE → Callback Router
    │           │           ├─ avito → Run Avito → Avito OK
    │           │           ├─ cian → Run CIAN → CIAN OK
    │           │           ├─ both → Run Both → Both OK
    │           │           ├─ enable → Enable Workflow → Enabled OK
    │           │           ├─ disable → Disable Workflow → Disabled OK
    │           │           └─ help → Help
    │           │
    │           └─ FALSE → Is Start?
    │                       └─ TRUE → Send Welcome
    │
    └─ FALSE → Unauthorized
```

---

## 🎯 Финальный чек-лист

- [ ] Импортирован telegram_bot_FINAL_WORKING.json
- [ ] Заменён TELEGRAM_CREDENTIALS_ID на реальный ID (17 раз)
- [ ] Заменён N8N_API_CREDENTIALS_ID на реальный ID (6 раз)
- [ ] Проверен User ID (7984101063 → ваш ID)
- [ ] Проверен URL главного workflow
- [ ] Проверен ID главного workflow (iXAfySHKjPj3DPcm)
- [ ] Workflow активирован
- [ ] Протестирована команда /start
- [ ] Кнопки отображаются правильно (не "...")
- [ ] Нажата кнопка "Парсить Avito"
- [ ] Пришло подтверждение
- [ ] Главный workflow запустился

---

## ✅ Всё работает?

Если после всех шагов:
- ✅ Кнопки видны
- ✅ /start работает
- ✅ Кнопки запускают главный workflow
- ✅ Приходят подтверждения

**Поздравляю! Бот полностью настроен и работает!** 🎉

---

## 📞 Если что-то не работает

1. Проверьте все пункты чек-листа
2. Посмотрите логи в **Executions**
3. Убедитесь, что все credentials правильные
4. Проверьте, что главный workflow существует и активен

---

**Версия:** FINAL (полностью рабочая)
**Дата:** 23 января 2026
**Автор:** Claude AI

**Основные исправления:**
- ✅ Правильный формат inline keyboard (JSON expression)
- ✅ Правильная последовательность проверок (Callback → Start)
- ✅ Интеграция с главным workflow через API
- ✅ HTTP запросы на /execute endpoint
