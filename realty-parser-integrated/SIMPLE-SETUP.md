# ✅ ПРОСТАЯ УСТАНОВКА - БЕЗ Environment Variables

## 🎯 Что это?

Это **упрощённая версия workflow**, которая НЕ требует:
- ❌ Остановки n8n
- ❌ Настройки Environment Variables
- ❌ Изменения конфигурации n8n
- ❌ Перезапуска n8n

**Просто:**
1. Получите токен Apify
2. Замените в файле
3. Импортируйте в n8n
4. Всё работает! ✅

---

## 📋 ШАГ 1: Получите Apify API Token

### 1.1 Войдите в Apify Console

Откройте: https://console.apify.com/

### 1.2 Получите токен

1. В меню слева → **Settings**
2. **Integrations**
3. **API tokens**
4. Скопируйте **Personal API token**

**Формат токена:**
```
apify_api_XXXxxxXXXxxxXXXxxxXXXxxxXXX
```

**⚠️ ВАЖНО:** Токен начинается с `apify_api_`

---

## 📋 ШАГ 2: Замените токен в workflow

### 2.1 Откройте файл

Найдите файл:
```
workflows/user-workflow-SIMPLE.json
```

Откройте его в **текстовом редакторе**:
- Notepad++ (Windows)
- VS Code
- Sublime Text
- Или любой другой

### 2.2 Найдите и замените

**Найти:**
```
YOUR_APIFY_TOKEN_HERE
```

**Заменить на:** ваш реальный токен
```
apify_api_XXXxxxXXXxxxXXXxxxXXXxxxXXX
```

**В редакторе:**
1. Ctrl+H (или Cmd+H на Mac)
2. Find: `YOUR_APIFY_TOKEN_HERE`
3. Replace with: `apify_api_XXXxxxXXXxxxXXXxxxXXXxxxXXX` (ваш токен!)
4. Replace All
5. Сохраните файл (Ctrl+S)

**Всего заменится 4 места** в файле.

---

## 📋 ШАГ 3: Импортируйте в n8n

### 3.1 Откройте n8n

Откройте в браузере: http://localhost:5678

### 3.2 Импортируйте workflow

1. В n8n UI → **Workflows** (левое меню)
2. Нажмите **Import from File**
3. Выберите файл: `user-workflow-SIMPLE.json` (с вашим токеном)
4. Нажмите **Import**

### 3.3 Активируйте workflow

1. В открывшемся workflow нажмите **Active** (переключатель справа сверху)
2. Должен стать зелёным ✅

---

## 📋 ШАГ 4: Протестируйте!

### 4.1 Откройте Telegram

Найдите вашего бота в Telegram

### 4.2 Отправьте /start

```
/start
```

### 4.3 Проверьте кнопки

Должны появиться 4 кнопки:
- 🏢 Авито
- 🏠 ЦИАН
- 🚀 Оба сайта
- 📄 Таблица

### 4.4 Нажмите любую кнопку

Например, **🏢 Авито**

**Ожидаемый результат:**
1. ✅ Уведомление "✅ Запускаю..."
2. ⏳ Парсинг запускается (2-3 минуты)
3. 📊 Результаты появляются в Google Sheets
4. 📱 Telegram уведомление с новыми объявлениями

---

## ✅ ГОТОВО!

**Workflow полностью настроен и работает!**

---

## 🔍 Где мой токен в workflow?

После замены, в файле будет:

**Было:**
```json
"url": "https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl/runs?token=YOUR_APIFY_TOKEN_HERE&waitForFinish=120"
```

**Стало:**
```json
"url": "https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl/runs?token=apify_api_XXXxxxXXXxxxXXXxxxXXXxxxXXX&waitForFinish=120"
```

Токен теперь **напрямую в URL** вместо Environment Variable.

---

## 🆚 Сравнение: Простой vs Сложный способ

### ПРОСТОЙ способ (этот файл)
**Преимущества:**
- ✅ Не требует настройки n8n
- ✅ Не нужно останавливать/перезапускать n8n
- ✅ Просто замените и импортируйте
- ✅ Работает сразу

**Недостатки:**
- ⚠️ Токен виден в workflow JSON
- ⚠️ При экспорте workflow токен включён
- ⚠️ Если нужно поменять токен → нужно редактировать workflow в n8n или снова менять в файле

### СЛОЖНЫЙ способ (Environment Variables)
**Преимущества:**
- ✅ Токен не виден в workflow JSON
- ✅ Легко менять токен (один раз в Settings)
- ✅ Best practice для безопасности

**Недостатки:**
- ❌ Требует остановки n8n
- ❌ Нужно настроить N8N_BLOCK_ENV_ACCESS_IN_NODE=false
- ❌ Нужно перезапустить n8n
- ❌ Сложнее для новичков

---

## 🔒 Безопасность

**⚠️ ВАЖНО:**

1. **Не публикуйте workflow JSON с токеном**
   - Не загружайте в GitHub
   - Не отправляйте в публичные чаты
   - Не делитесь в открытом доступе

2. **Токен даёт полный доступ к Apify**
   - Может запускать actors
   - Потратить ваши credits
   - Получить данные

3. **Если токен утёк:**
   - Удалите его в Apify Console
   - Создайте новый токен
   - Замените в workflow

4. **Рекомендация:**
   - Для production используйте Environment Variables (сложный способ)
   - Для тестирования используйте этот простой способ

---

## ❓ FAQ

**Q: Можно ли использовать этот способ для production?**

A: Можно, но лучше использовать Environment Variables для безопасности. Этот способ удобен для быстрого старта и тестирования.

**Q: Как поменять токен если он изменился?**

A:
1. В n8n откройте workflow
2. Найдите nodes: "Запуск Авито", "Запуск ЦИАН", "Результаты Авито", "Результаты ЦИАН"
3. В каждом найдите URL и замените старый токен на новый
4. Сохраните workflow

**Q: Сколько credits потребляет один запуск?**

A:
- Avito: ~$0.20-0.50 за запуск (с RESIDENTIAL proxy)
- CIAN: ~$0.20-0.50 за запуск (с RESIDENTIAL proxy)
- Free Plan даёт $5 (хватит на ~10-25 запусков)

**Q: Что делать если credits закончились?**

A:
1. Apify Console → Billing
2. Add payment method
3. Buy credits (минимум $10)

**Q: Можно ли использовать бесплатные proxies?**

A: Да, но они часто блокируются Avito/CIAN. Измените в workflow:
```json
"proxyConfiguration": {
  "useApifyProxy": true,
  "apifyProxyGroups": ["DATACENTER"]  // вместо "RESIDENTIAL"
}
```

**Q: Workflow не работает - что делать?**

A: Проверьте:
1. Токен правильный? (начинается с `apify_api_`)
2. Есть credits в Apify? (> $1)
3. Все 4 места в workflow заменили?
4. Workflow Active (зелёный переключатель)?
5. Telegram bot credentials настроены?
6. Google Sheets credentials настроены?

---

## 🎯 Итог

**3 простых шага:**
1. Получите токен из https://console.apify.com/account/integrations
2. Замените `YOUR_APIFY_TOKEN_HERE` в файле на ваш токен
3. Импортируйте в n8n

**Готово!** ✅

Теперь ваш бот парсит Авито и ЦИАН без сложных настроек!
