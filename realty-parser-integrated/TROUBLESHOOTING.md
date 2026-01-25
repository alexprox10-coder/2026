# 🔍 Диагностика: Почему бот молчит и workflow не работает

## ✅ Чек-лист диагностики

Пройдите по этим пунктам по порядку:

### 1. Workflow импортирован?

**Проверьте:**
```
n8n UI → Workflows → Есть ли workflow с названием "🏠 Парсер Недвижимости + Telegram Bot (Secure)"?
```

**Если НЕТ:**
- Импортируйте: `/home/user/2026/realty-parser-integrated/workflows/IMPORT-THIS-ONE.json`
- n8n UI → Workflows → Import from File → IMPORT-THIS-ONE.json

**Если ДА:**
- ✅ Переходите к пункту 2

---

### 2. Workflow активен?

**Проверьте:**
```
Откройте workflow → Смотрите в правый верхний угол → Есть ли переключатель "Active" в положении ON (зеленый)?
```

**Если НЕТ (Active OFF):**
- ❌ Workflow НЕ БУДЕТ РАБОТАТЬ!
- Причина: triggers (Schedule, Webhook) работают только когда workflow активен

**Исправление:**
```
1. Сначала исправьте все ошибки (см. пункты 3-5)
2. Потом включите Active
```

**Если ДА (Active ON):**
- ✅ Переходите к пункту 3

---

### 3. Environment Variables настроены?

**Проверьте:**
```
n8n UI → Settings → Environment Variables
```

**Должны быть эти 5 переменных:**
```
WEBHOOK_SECRET = <какое-то значение>
APIFY_API_TOKEN = apify_api_xxx
ALLOWED_CHAT_IDS = 7984101063
GOOGLE_SHEET_ID = 1IptmHSeKMRMAWB8QzYfyj1vjSJ2Pa0ZdrMq--fMuCW8
DEFAULT_CHAT_ID = 7984101063
```

**Если НЕТ или не все:**
- ❌ Workflow НЕ БУДЕТ РАБОТАТЬ!
- Причина: все nodes используют $env.XXX, если переменных нет → ошибка

**Исправление:**
```
Settings → Environment Variables → Add Variable

Добавьте каждую из 5 переменных:

1. Name: WEBHOOK_SECRET
   Value: <сгенерируйте: openssl rand -hex 32>

2. Name: APIFY_API_TOKEN
   Value: your_apify_api_token_here

3. Name: ALLOWED_CHAT_IDS
   Value: 7984101063

4. Name: GOOGLE_SHEET_ID
   Value: 1IptmHSeKMRMAWB8QzYfyj1vjSJ2Pa0ZdrMq--fMuCW8

5. Name: DEFAULT_CHAT_ID
   Value: 7984101063
```

**ВАЖНО:** После добавления переменных:
```
- Если n8n запущен через Docker: docker-compose restart
- Если через npm: перезапустите n8n
```

**Если ДА (все 5 переменных есть):**
- ✅ Переходите к пункту 4

---

### 4. Credentials настроены?

**Проверьте:**
```
Откройте workflow → Есть ли КРАСНЫЕ nodes (с красным индикатором ошибки)?
```

**Если ДА (есть красные nodes):**
- ❌ Workflow НЕ БУДЕТ РАБОТАТЬ!
- Причина: nodes требуют credentials для работы

**Красные nodes (обычно 3 штуки):**
1. **💾 Сохранить в Google Sheets** - требует Google Sheets credential
2. **📱 Отправить в Telegram** - требует Telegram credential
3. **📊 Итоговое сообщение** - требует Telegram credential

**Исправление для каждого красного node:**
```
1. Кликните на красный node
2. Посмотрите в Parameters → Credential to connect with
3. Если показывает "Select Credential":
   - Кликните на dropdown
   - Выберите ваш credential:
     - Для Google Sheets: "РАССЫЛКА КП +ПАРСЕР"
     - Для Telegram: "Telegram ЦИАН+АВИТО+ЯД"

4. Если credential НЕТ в списке - создайте новый:

   Telegram credential:
   - Credentials → Add Credential → Telegram API
   - Access Token: <ваш bot token от @BotFather>
   - Save

   Google Sheets credential:
   - Credentials → Add Credential → Google Sheets OAuth2 API
   - Пройдите OAuth авторизацию
   - Save

5. Save node
```

**Если НЕТ (все nodes зеленые):**
- ✅ Переходите к пункту 5

---

### 5. Проверка Executions (логи)

**Откройте:**
```
n8n UI → Executions (левое меню)
```

**Что вы видите?**

#### Вариант А: Executions ПУСТОЙ (нет ни одного запуска)

**Значит:**
- ❌ Workflow НИ РАЗУ НЕ ЗАПУСТИЛСЯ!

**Причины:**
1. Workflow не активен (см. пункт 2)
2. Schedule триггер не сработал (еще не прошло 30 минут)
3. Webhook не вызывался

**Тест запуска:**
```
1. Откройте workflow
2. Нажмите кнопку "Execute Workflow" (вверху справа)
3. Посмотрите результат
```

**Если при ручном Execute появляется ошибка:**
- Читайте ошибку внимательно
- Обычно это:
  - "Environment variable XXX is not defined" → вернитесь к пункту 3
  - "Missing credentials" → вернитесь к пункту 4
  - "Invalid Apify token" → проверьте APIFY_API_TOKEN
  - "Unauthorized chat_id" → проверьте ALLOWED_CHAT_IDS

---

#### Вариант Б: Есть Executions со статусом ERROR (красные)

**Откройте последний ERROR execution:**
```
Кликните на execution → Смотрите какой node красный → Кликните на красный node → Читайте ошибку
```

**Типичные ошибки:**

##### Ошибка: "Environment variable APIFY_API_TOKEN is not defined"
```
Исправление:
→ Settings → Environment Variables → Add Variable
→ Name: APIFY_API_TOKEN
→ Value: your_apify_api_token_here
→ Save
→ Перезапустите n8n
```

##### Ошибка: "401 Unauthorized" от Apify
```
Причина: Невалидный Apify API token

Исправление:
1. Зайдите в https://console.apify.com/
2. Settings → Integrations → API Token
3. Скопируйте токен
4. n8n → Settings → Environment Variables
5. Измените APIFY_API_TOKEN на правильный
6. Перезапустите n8n
```

##### Ошибка: "Insufficient credits" от Apify
```
Причина: На аккаунте Apify закончились credits

Исправление:
1. Зайдите в https://console.apify.com/
2. Billing → Пополните баланс
3. Запустите workflow заново
```

##### Ошибка: "Invalid credentials" на Telegram node
```
Причина: Telegram credential неправильный или отсутствует

Исправление:
1. Откройте красный Telegram node
2. Credentials → Create New
3. Access Token: <получите от @BotFather>
4. Save
```

##### Ошибка: "Chat not found" от Telegram
```
Причина: Bot не может отправить сообщение в chat

Исправление:
1. Откройте Telegram
2. Найдите вашего бота
3. Нажмите /start (ОБЯЗАТЕЛЬНО!)
4. Запустите workflow заново
```

##### Ошибка: "Unauthorized chat_id"
```
Причина: chat_id не в whitelist

Исправление:
→ Settings → Environment Variables
→ ALLOWED_CHAT_IDS = 7984101063
→ Убедитесь что ваш chat_id в списке (через запятую если несколько)
```

---

#### Вариант В: Есть Executions со статусом SUCCESS (зеленые)

**Если workflow выполняется успешно, но бот молчит:**

**Проверьте:**

1. **Вы запустили /start у бота?**
   ```
   Telegram → Найдите вашего бота → Нажмите /start
   ```

2. **Bot token правильный?**
   ```
   Credentials → Telegram API → Проверьте Access Token
   ```

3. **Chat ID правильный?**
   ```
   Откройте SUCCESS execution → Найдите Telegram node
   → Посмотрите какой chatId использовался
   → Должен быть 7984101063
   ```

4. **Telegram node выполнился?**
   ```
   Откройте SUCCESS execution
   → Прокрутите до Telegram nodes
   → Они должны быть ЗЕЛЕНЫЕ с галочкой
   → Если их нет - значит не дошло до отправки
   ```

5. **Есть ли данные для отправки?**
   ```
   Откройте SUCCESS execution
   → Node "✅ Финал"
   → Посмотрите output
   → Если там { empty: true } → нет новых объявлений
   ```

---

### 6. Тест Apify напрямую

Проверим работает ли Apify вообще:

```bash
# Замените YOUR_TOKEN на ваш токен
curl "https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl?token=YOUR_TOKEN"
```

**Если 401 Unauthorized:**
- Токен невалидный

**Если 200 OK:**
- Токен работает

**Если 403 Forbidden:**
- Проблема с аккаунтом Apify

---

### 7. Минимальный тест

Создайте ПРОСТОЙ тестовый workflow:

```
1. Workflows → Create New Workflow
2. Добавьте Schedule Trigger node
3. Настройте: Every 1 minute
4. Добавьте Code node
5. Code: return [{ json: { test: "works" } }];
6. Добавьте Telegram node
7. Credentials: ваш Telegram credential
8. Chat ID: 7984101063
9. Message: {{ $json.test }}
10. Соедините: Schedule → Code → Telegram
11. Save
12. Active ON
13. Подождите 1 минуту
```

**Если сообщение приходит:**
- ✅ Telegram работает, проблема в основном workflow

**Если сообщение НЕ приходит:**
- ❌ Проблема с Telegram credential или bot

---

## 🎯 Быстрая диагностика по симптомам

### Симптом: "Бот вообще никогда не писал"

**Вероятная причина:**
- Telegram credential неправильный
- Не нажали /start у бота
- Chat ID неправильный

**Проверка:**
1. Telegram → Найдите бота → /start
2. Получите ваш chat_id: https://t.me/userinfobot
3. Убедитесь что chat_id совпадает с DEFAULT_CHAT_ID

---

### Симптом: "Бот писал раньше, сейчас молчит"

**Вероятная причина:**
- Workflow деактивирован (Active OFF)
- Закончились Apify credits
- Schedule еще не сработал (нужно подождать 30 минут)

**Проверка:**
1. Workflow → Active ON?
2. Apify Console → Billing → Credits > 0?
3. Executions → Есть новые SUCCESS executions?

---

### Симптом: "Executions пустые, ничего не запускалось"

**Вероятная причина:**
- Workflow не активен
- Environment Variables не настроены
- Есть ошибки при активации

**Проверка:**
1. Workflow → Active?
2. Settings → Environment Variables → 5 переменных?
3. Workflow → Все nodes зеленые?

---

## 📊 Финальная проверка

Если ВСЁ настроено правильно:

✅ Workflow импортирован: "🏠 Парсер Недвижимости + Telegram Bot (Secure)"
✅ Workflow активен: Active ON
✅ Environment Variables: 5 переменных настроены
✅ Credentials: все nodes зеленые (нет красных)
✅ /start у бота: нажат
✅ Apify credits: > 0

**То workflow ДОЛЖЕН работать!**

Запустите ручной тест:
```
Workflow → Execute Workflow → Смотрите результат
```

---

## 🆘 Если ничего не помогло

**Пришлите мне:**

1. **Screenshot Executions:**
   ```
   n8n UI → Executions → Screenshot списка
   ```

2. **Screenshot последнего ERROR execution (если есть):**
   ```
   Executions → Кликните на красный → Screenshot
   ```

3. **Screenshot Environment Variables:**
   ```
   Settings → Environment Variables → Screenshot
   (можно скрыть значения токенов)
   ```

4. **Текст ошибки:**
   ```
   Если есть ошибка - скопируйте полный текст
   ```

С этой информацией я смогу точно определить проблему! 🔍
