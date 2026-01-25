# 🔧 Исправление ошибки импорта: "Cannot read properties of null (reading 'node')"

## 🎯 Быстрое решение

Используйте файл **БЕЗ** hardcoded credentials:

```
/home/user/2026/realty-parser-integrated/workflows/main-parser-fixed-no-credentials.json
```

Этот файл импортируется **БЕЗ ОШИБОК**, но потребует настройки credentials после импорта.

---

## 📋 Инструкция по импорту

### Шаг 1: Импортировать workflow

```
n8n UI → Workflows → Import from File
→ Выберите: main-parser-fixed-no-credentials.json
→ Import
```

✅ Импорт пройдет успешно!

### Шаг 2: Настроить Telegram Credentials

После импорта, откройте workflow и настройте Telegram credentials на следующих nodes:

1. **📱 Отправка в Telegram** (node для отправки объявлений)
2. **📊 Итоговое сообщение** (node для итоговой статистики)
3. **📭 Сообщение о пустых результатах** (node для уведомления о пустых результатах)
4. **🚨 Уведомление об ошибке** (node для ошибок)

**Для каждого node:**
```
1. Кликните на node
2. Credentials → Select Credential
3. Выберите ваш Telegram credential: "Telegram ЦИАН+АВИТО+ЯД"
   (или создайте новый, если его нет)
4. Save
```

### Шаг 3: Настроить Google Sheets Credentials

Настройте Google Sheets credentials на node:

**💾 Google Sheets** (node для сохранения в таблицу)

```
1. Кликните на node
2. Credentials → Select Credential
3. Выберите ваш Google Sheets credential: "РАССЫЛКА КП +ПАРСЕР"
   (или создайте новый OAuth2 credential)
4. Save
```

### Шаг 4: Настроить Environment Variables

**ВАЖНО:** Workflow использует Environment Variables, которые должны быть настроены ДО активации!

```
n8n UI → Settings → Environment Variables
```

Добавьте следующие переменные:

```bash
WEBHOOK_SECRET=<generate via: openssl rand -hex 32>
APIFY_API_TOKEN=your_apify_api_token_here
GOOGLE_SHEET_ID=1IptmHSeKMRMAWB8QzYfyj1vjSJ2Pa0ZdrMq--fMuCW8
DEFAULT_CHAT_ID=7984101063
ALLOWED_CHAT_IDS=7984101063
```

**Генерация WEBHOOK_SECRET:**
```bash
openssl rand -hex 32
# Скопируйте вывод и используйте как WEBHOOK_SECRET
```

### Шаг 5: Проверить все nodes

После настройки credentials, убедитесь что все nodes зеленые (без красных маркеров ошибок):

```
1. Откройте workflow
2. Проверьте каждый node на наличие ошибок
3. Если node красный - откройте его и исправьте
```

### Шаг 6: Активировать workflow

```
1. Убедитесь что все nodes зеленые
2. Нажмите "Active" в правом верхнем углу
3. Статус должен стать: ✅ Active
```

---

## 🔍 Причина ошибки

Ошибка **"Cannot read properties of null (reading 'node')"** возникает когда:

1. **Hardcoded Credential IDs** в workflow не существуют в вашем n8n
   - Workflow содержал: `"id": "i6jLoqevWyi5TP5S"` (Google Sheets)
   - Workflow содержал: `"id": "USF1FBru0jYO1wky"` (Telegram)
   - Эти IDs уникальны для каждого n8n instance

2. **n8n не может найти credentials** и возвращает null
   - Попытка прочитать `.node` из null → ошибка

---

## ✅ Решение

Файл `main-parser-fixed-no-credentials.json` имеет:

- ❌ **Удалены** все hardcoded credential IDs
- ✅ **Сохранена** вся логика workflow
- ✅ **Сохранены** все nodes и connections
- ✅ **Импортируется** без ошибок

После импорта вы настраиваете credentials вручную на нужных nodes.

---

## 📝 Какие nodes требуют credentials

### Telegram API (4 nodes):
1. 📱 **Отправка в Telegram** - отправка объявлений
2. 📊 **Итоговое сообщение** - статистика
3. 📭 **Сообщение о пустых результатах** - уведомление
4. 🚨 **Уведомление об ошибке** - ошибки

### Google Sheets OAuth2 (1 node):
1. 💾 **Google Sheets** - сохранение данных

**Всего:** 5 nodes требуют настройки credentials

---

## 🎯 Быстрый чеклист

```
✅ 1. Импортировать main-parser-fixed-no-credentials.json
✅ 2. Настроить Telegram credentials (4 nodes)
✅ 3. Настроить Google Sheets credentials (1 node)
✅ 4. Добавить Environment Variables (5 переменных)
✅ 5. Проверить что все nodes зеленые
✅ 6. Активировать workflow
✅ 7. Протестировать
```

---

## 🧪 Тестирование

### Test 1: Manual Execution

```
1. Откройте workflow
2. Нажмите "Execute Workflow" (вручную)
3. Проверьте результаты
```

### Test 2: Webhook Trigger

```bash
curl -X POST "https://your-n8n.com/webhook/realty-parser-secure/$WEBHOOK_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "7984101063", "trigger_source": "manual"}'
```

### Test 3: Schedule Trigger

```
1. Измените Schedule на "Every 1 minute"
2. Активируйте workflow
3. Подождите 1 минуту
4. Проверьте Executions
```

---

## 🆘 Если все еще ошибка

### Ошибка: "Missing credentials"

**Решение:**
```
1. Откройте красный node
2. Parameters → Credentials
3. Create New Credential
4. Настройте согласно типу (Telegram или Google Sheets)
5. Save
```

### Ошибка: "Environment variable XXX not defined"

**Решение:**
```
1. Settings → Environment Variables
2. Добавьте недостающую переменную
3. Перезапустите n8n (если Docker):
   docker-compose restart
```

### Ошибка: "Invalid webhook URL"

**Решение:**
```
1. Проверьте что WEBHOOK_SECRET добавлен в Environment Variables
2. Деактивируйте workflow
3. Активируйте заново (webhooks регистрируются при активации)
```

---

## 📂 Файлы

**Для импорта БЕЗ ошибок:**
```
/home/user/2026/realty-parser-integrated/workflows/main-parser-fixed-no-credentials.json
```

**Оригинал (с hardcoded credentials - вызывает ошибку):**
```
/home/user/2026/realty-parser-integrated/workflows/main-parser-fixed-optimized.json
```

**Используйте первый файл!** ✅

---

## 💡 Совет

После первого успешного импорта и настройки, вы можете экспортировать workflow обратно. Ваш экспорт будет содержать **ссылки** на credentials (не hardcoded IDs), и при следующем импорте credentials будут подхватываться автоматически если имена совпадают.

Удачи! 🚀
