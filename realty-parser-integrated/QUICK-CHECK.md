# ⚡ БЫСТРАЯ ПРОВЕРКА - Почему не работает?

## 5-минутный чеклист

Проверьте эти 5 вещей по порядку:

---

### ✅ 1. Workflow активен?

```
n8n UI → Workflows → Откройте workflow → Смотрите справа вверху
```

**Должно быть:** Переключатель "Active" = **ON** (зеленый)

**Если OFF:**
- Включите Active
- Если не включается - есть ошибки (см. пункты 3-4)

---

### ✅ 2. Environment Variables настроены?

```
n8n UI → Settings → Environment Variables
```

**Должны быть эти 5 переменных:**

| Name | Value |
|------|-------|
| WEBHOOK_SECRET | любое значение (32+ символов) |
| APIFY_API_TOKEN | your_apify_api_token_here |
| ALLOWED_CHAT_IDS | 7984101063 |
| GOOGLE_SHEET_ID | 1IptmHSeKMRMAWB8QzYfyj1vjSJ2Pa0ZdrMq--fMuCW8 |
| DEFAULT_CHAT_ID | 7984101063 |

**Если НЕТ всех 5:**
- Добавьте недостающие
- **ОБЯЗАТЕЛЬНО перезапустите n8n** после добавления!

---

### ✅ 3. Credentials настроены?

```
Откройте workflow → Есть ли КРАСНЫЕ nodes?
```

**Должно быть:** ВСЕ nodes ЗЕЛЕНЫЕ (нет красных маркеров)

**Если есть красные:**
```
Для каждого красного node:
1. Кликните на него
2. Credential to connect with → Select Credential
3. Выберите из списка:
   - Google Sheets: "РАССЫЛКА КП +ПАРСЕР"
   - Telegram: "Telegram ЦИАН+АВИТО+ЯД"
4. Если нет в списке - создайте новый
5. Save
```

---

### ✅ 4. Нажали /start у бота?

```
Telegram → Найдите вашего бота → Нажмите /start
```

**ОБЯЗАТЕЛЬНО!** Иначе бот не может отправлять сообщения.

---

### ✅ 5. Есть ли Apify credits?

```
Зайдите: https://console.apify.com/
→ Billing → Credits
```

**Должно быть:** Credits > 0

**Если 0:**
- Пополните баланс
- Или используйте free tier (есть бесплатные credits)

---

## 🧪 Тест запуска

Если все 5 пунктов ✅, запустите вручную:

```
1. Откройте workflow
2. Нажмите "Execute Workflow" (кнопка справа вверху)
3. Смотрите результат
```

**Если SUCCESS и бот написал:**
- 🎉 ВСЁ РАБОТАЕТ!
- Автопарсинг будет каждые 30 минут

**Если ERROR:**
- Смотрите какой node красный
- Читайте текст ошибки
- Исправляйте согласно ошибке

---

## 📋 Типичные ошибки

### "Environment variable XXX is not defined"

**Решение:**
```
Settings → Environment Variables → Add Variable
→ Добавьте недостающую переменную (см. пункт 2)
→ ПЕРЕЗАПУСТИТЕ n8n!
```

### "401 Unauthorized" от Apify

**Решение:**
```
Проверьте APIFY_API_TOKEN:
- Зайдите в https://console.apify.com/
- Settings → Integrations → API Token
- Скопируйте токен
- Замените в Environment Variables
```

### "Chat not found" от Telegram

**Решение:**
```
Telegram → Найдите бота → /start
(ОБЯЗАТЕЛЬНО нажмите /start!)
```

### "Insufficient credits" от Apify

**Решение:**
```
https://console.apify.com/ → Billing → Add credits
```

---

## 🔍 Где смотреть логи?

```
n8n UI → Executions (левое меню)
```

**Смотрите:**
- Последний execution
- Если ERROR (красный) - кликните и смотрите ошибку
- Если SUCCESS (зеленый) - workflow работает!

---

## ⚡ Ещё проще

**Минимальная проверка (30 секунд):**

1. ✅ Active ON?
2. ✅ 5 Environment Variables есть?
3. ✅ Нет красных nodes?
4. ✅ /start нажат?
5. ✅ Apify credits > 0?

**Если все ✅ → нажмите "Execute Workflow"**

**Работает? → Готово! 🎉**
**Не работает? → Откройте TROUBLESHOOTING.md для детальной диагностики**

---

## 📖 Полная диагностика

Если быстрая проверка не помогла:
```
/home/user/2026/realty-parser-integrated/TROUBLESHOOTING.md
```

Там подробный гайд по каждой ошибке.
