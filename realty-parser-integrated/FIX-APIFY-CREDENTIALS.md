# 🔧 Исправление ошибки "Авторизация не удалась" в Apify nodes

## ❌ Проблема

**Ошибка в nodes "Запуск Авито" / "Запуск ЦИАН":**
```
Авторизация не удалась — проверьте свои учетные данные
```

**Причина:**
API токен Apify неправильный, истёк или не имеет доступа к нужным actors.

---

## ✅ Решение: Получите правильный Apify API Token

### Шаг 1: Войдите в Apify Console

1. Откройте: https://console.apify.com/
2. Войдите в свой аккаунт

### Шаг 2: Получите API Token

1. В Apify Console → Settings (левое меню)
2. Integrations
3. API tokens
4. **Скопируйте Personal API token**
   - Он начинается с `apify_api_`
   - Пример: `apify_api_XXXxxxXXXxxxXXXxxxXXXxxxXXX`

### Шаг 3: Проверьте что токен имеет доступ к actors

Ваш workflow использует 2 actors:
1. **Avito Actor**: `eiD1SmA4A6aojHvYl`
2. **CIAN Actor**: `igolaizola~cian-ru-scraper`

**Проверка доступа:**

```bash
# Замените YOUR_TOKEN на ваш токен
curl "https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl?token=YOUR_TOKEN"
```

**Ожидаемый результат:** JSON с информацией об actor

**Если ошибка 401/403:** Токен неправильный или нет доступа

### Шаг 4: Обновите Environment Variable в n8n

```
1. n8n UI → Settings → Environment Variables
2. Найдите: APIFY_API_TOKEN
3. Нажмите Edit
4. Вставьте НОВЫЙ токен
5. Save
```

### Шаг 5: Проверьте баланс Apify

Apify требует credits для запуска actors:

1. Apify Console → Account → Usage & Billing
2. Проверьте: **Free Credits** или **Paid Credits**
3. Если 0 credits → пополните баланс

**Free Plan:**
- $5 free credits при регистрации
- Residential proxies потребляют много credits (~$0.20-0.50 за запуск)

### Шаг 6: Перезапустите workflow

1. Деактивируйте workflow (Active OFF)
2. Активируйте снова (Active ON)
3. Тест: Telegram → /start → нажмите кнопку

---

## 🔍 Диагностика проблем с Apify

### Проблема 1: Токен истёк или удалён

**Симптом:** "Авторизация не удалась" на всех Apify nodes

**Решение:**
1. Создайте новый API token в Apify Console
2. Обновите в n8n Environment Variables

### Проблема 2: Недостаточно credits

**Симптом:** Авторизация OK, но запуск fails с "insufficient funds"

**Решение:**
1. Apify Console → Billing
2. Add payment method
3. Buy credits ($10 минимум)

### Проблема 3: Actor не существует или приватный

**Симптом:** "Actor not found" или "Access denied"

**Для Avito actor (eiD1SmA4A6aojHvYl):**
- Это публичный actor, должен работать

**Для CIAN actor (igolaizola~cian-ru-scraper):**
1. Проверьте что actor публичный: https://apify.com/igolaizola/cian-ru-scraper
2. Если приватный → используйте другой публичный CIAN actor

**Альтернативные CIAN actors:**
- `bebity/cian-scraper`
- `drobnikj/cian-scraper`

### Проблема 4: Rate limiting

**Симптом:** "Too many requests" или 429 error

**Решение:**
- Подождите 1-5 минут
- Уменьшите частоту запусков
- Используйте платный план для higher limits

---

## 🧪 Тест API токена

### Тест через curl:

```bash
# Замените YOUR_TOKEN на ваш токен
TOKEN="apify_api_XXXxxxXXXxxxXXX"

# Тест 1: Проверка токена
curl "https://api.apify.com/v2/user?token=$TOKEN"

# Должно вернуть ваш username и email

# Тест 2: Проверка Avito actor
curl "https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl?token=$TOKEN"

# Должно вернуть информацию об actor

# Тест 3: Проверка CIAN actor
curl "https://api.apify.com/v2/acts/igolaizola~cian-ru-scraper?token=$TOKEN"

# Должно вернуть информацию об actor
```

### Тест через n8n:

1. Создайте тестовый workflow
2. Добавьте HTTP Request node
3. URL: `https://api.apify.com/v2/user?token={{ $env.APIFY_API_TOKEN }}`
4. Execute Node
5. Должен вернуть ваш user profile

---

## 📝 Правильная настройка Apify в n8n

### Вариант 1: Environment Variables (текущий)

**Преимущества:**
- ✅ Один токен для всех nodes
- ✅ Легко менять

**Недостатки:**
- ❌ Требует N8N_BLOCK_ENV_ACCESS_IN_NODE=false

**Настройка:**
```
Settings → Environment Variables
Name:  APIFY_API_TOKEN
Value: apify_api_XXXxxxXXXxxxXXX
```

**В nodes используйте:**
```
https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl/runs?token={{ $env.APIFY_API_TOKEN }}&waitForFinish=120
```

### Вариант 2: HTTP Request Header Authentication

**Преимущества:**
- ✅ Не требует N8N_BLOCK_ENV_ACCESS_IN_NODE=false
- ✅ Можно использовать n8n Credentials

**Недостатки:**
- ❌ Нужно настраивать в каждом node

**Настройка:**

1. **URL без токена:**
   ```
   https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl/runs?waitForFinish=120
   ```

2. **HTTP Request node → Options → Headers:**
   ```json
   {
     "Authorization": "Bearer apify_api_XXXxxxXXXxxxXXX"
   }
   ```

---

## 🎯 Чеклист для решения проблемы

- [ ] Получен правильный Apify API token из console.apify.com
- [ ] Токен начинается с `apify_api_`
- [ ] Обновлён в n8n Settings → Environment Variables
- [ ] Проверен баланс credits в Apify (должно быть > $1)
- [ ] Workflow деактивирован и активирован снова
- [ ] Протестировано: Execute Node на "Запуск Авито"
- [ ] Протестировано: Telegram → /start → нажать кнопку

---

## ❓ FAQ

**Q: Где найти мой Apify API token?**

A: https://console.apify.com/account/integrations

**Q: Можно ли использовать бесплатный план Apify?**

A: Да, но:
- Только $5 free credits (хватит на ~10-25 запусков)
- После этого нужно платить
- Residential proxies дорогие (~$0.20-0.50 за запуск)

**Q: Что делать если credits закончились?**

A:
1. Apify Console → Billing → Add payment method
2. Buy credits (минимум $10)
3. Или переключитесь на бесплатные datacenter proxies (но они часто блокируются)

**Q: Как использовать бесплатные proxies вместо residential?**

A: В workflow JSON измените:
```json
"proxyConfiguration": {
  "useApifyProxy": true,
  "apifyProxyGroups": ["DATACENTER"]  // вместо "RESIDENTIAL"
}
```

**Но:** Datacenter proxies часто блокируются Avito/CIAN.

**Q: Actor не найден - что делать?**

A: Проверьте:
1. Actor существует: https://apify.com/store
2. Actor публичный (не private)
3. Используйте correct actor ID

---

## 🔒 Безопасность

**⚠️ ВАЖНО:**

1. **Никогда не делитесь API токеном**
   - Не публикуйте в GitHub
   - Не отправляйте в чаты
   - Используйте Environment Variables

2. **Ротация токенов**
   - Меняйте токен каждые 3-6 месяцев
   - Создавайте отдельные токены для разных проектов

3. **Мониторинг использования**
   - Проверяйте Apify usage каждую неделю
   - Установите billing alerts

---

## 🎯 Итог

**Проблема:** Авторизация не удалась

**Главная причина:** Неправильный или истёкший API токен

**Решение:**
1. Получите новый токен из https://console.apify.com/account/integrations
2. Обновите в n8n Settings → Environment Variables
3. Проверьте баланс credits
4. Перезапустите workflow
5. Тест! ✅
