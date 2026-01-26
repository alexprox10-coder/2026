# 🔧 Исправление ошибки "Доступ к переменным окружения запрещен"

## ❌ Проблема

**Ошибка в node "Запуск Авито":**
```
Доступ к переменным окружения запрещен
```

**Причина:**
В n8n по умолчанию включена защита от использования Environment Variables в nodes для безопасности. Workflow использует `{{ $env.APIFY_API_TOKEN }}`, но n8n блокирует доступ.

---

## ✅ Решение 1: Включить доступ к Environment Variables (РЕКОМЕНДУЮ)

### Шаг 1: Остановите n8n

```bash
# Если n8n запущен как процесс
pkill n8n

# Если n8n в Docker
docker stop n8n
```

### Шаг 2: Добавьте переменную окружения

**Вариант A: Через .env файл**

Найдите файл `.env` в директории n8n и добавьте:
```bash
N8N_BLOCK_ENV_ACCESS_IN_NODE=false
```

**Вариант B: Через команду запуска**

```bash
N8N_BLOCK_ENV_ACCESS_IN_NODE=false n8n start
```

**Вариант C: Для Docker**

В `docker-compose.yml`:
```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    environment:
      - N8N_BLOCK_ENV_ACCESS_IN_NODE=false
      - APIFY_API_TOKEN=YOUR_APIFY_API_TOKEN_HERE
```

Или через команду:
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BLOCK_ENV_ACCESS_IN_NODE=false \
  -e APIFY_API_TOKEN=YOUR_APIFY_API_TOKEN_HERE \
  n8nio/n8n
```

### Шаг 3: Установите Environment Variable для Apify

В n8n UI:
```
Settings → Environment Variables → Add Variable

Name:  APIFY_API_TOKEN
Value: YOUR_APIFY_API_TOKEN_HERE
```

### Шаг 4: Перезапустите n8n

```bash
n8n start
```

### Шаг 5: Проверьте workflow

1. Откройте workflow
2. Node "Запуск Авито" должен работать без ошибок
3. Протестируйте: нажмите Execute Node

---

## ✅ Решение 2: Использовать токен напрямую в URL (НЕ РЕКОМЕНДУЮ)

**⚠️ ВНИМАНИЕ:** Это менее безопасно, токен будет виден в workflow JSON.

### Вариант A: Замените в workflow вручную

В каждом HTTP Request node (Запуск Авито, Запуск ЦИАН, Результаты Авито, Результаты ЦИАН):

**Было:**
```
https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl/runs?token={{ $env.APIFY_API_TOKEN }}&waitForFinish=120
```

**Стало:**
```
https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl/runs?token=YOUR_APIFY_API_TOKEN_HERE&waitForFinish=120
```

**Проблемы:**
- ❌ Токен виден в workflow JSON
- ❌ При экспорте workflow токен будет включён
- ❌ Security риск

### Вариант B: Использовать HTTP Request Header Authentication

Этот вариант более безопасен, но требует изменения всех HTTP Request nodes.

**Для каждого Apify HTTP Request node:**

1. **URL без токена:**
   ```
   https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl/runs?waitForFinish=120
   ```

2. **Добавьте Header:**
   - Go to node settings
   - Options → Add Header
   - Name: `Authorization`
   - Value: `Bearer YOUR_APIFY_API_TOKEN_HERE`

**Преимущества:**
- ✅ Токен не в URL
- ✅ Можно использовать n8n Credentials для Authorization header

---

## 🎯 Рекомендация

**Используйте Решение 1:**
1. Включите `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`
2. Установите Environment Variable `APIFY_API_TOKEN`
3. Используйте `user-workflow-FIXED.json` как есть

**Почему:**
- ✅ Безопасно (токены не в workflow JSON)
- ✅ Легко менять токены (один раз в Environment Variables)
- ✅ Best practice для n8n
- ✅ Workflow остаётся portable

---

## 📋 Пошаговая инструкция (полная)

### 1. Остановите n8n

```bash
# Найдите процесс n8n
ps aux | grep n8n

# Остановите
pkill n8n
```

### 2. Установите переменную окружения

**Для Linux/Mac:**
```bash
export N8N_BLOCK_ENV_ACCESS_IN_NODE=false
export APIFY_API_TOKEN=YOUR_APIFY_API_TOKEN_HERE
```

Добавьте в `~/.bashrc` или `~/.zshrc` для постоянного использования:
```bash
echo 'export N8N_BLOCK_ENV_ACCESS_IN_NODE=false' >> ~/.bashrc
echo 'export APIFY_API_TOKEN=YOUR_APIFY_API_TOKEN_HERE' >> ~/.bashrc
source ~/.bashrc
```

**Для Windows:**
```powershell
$env:N8N_BLOCK_ENV_ACCESS_IN_NODE = "false"
$env:APIFY_API_TOKEN = "YOUR_APIFY_API_TOKEN_HERE"
```

### 3. Запустите n8n

```bash
n8n start
```

### 4. Проверьте в n8n UI

```
1. Settings → Environment Variables
2. Добавьте переменную (если ещё не добавили):
   Name:  APIFY_API_TOKEN
   Value: YOUR_APIFY_API_TOKEN_HERE
```

### 5. Импортируйте workflow

```
1. Workflows → Import from File
2. Выберите: user-workflow-FIXED.json
3. Active ON
```

### 6. Протестируйте

```
Telegram → /start → нажмите любую кнопку
```

---

## 🔍 Проверка что всё работает

### Тест 1: Проверьте доступ к Environment Variables

1. Откройте node "Запуск Авито"
2. В URL должно быть: `{{ $env.APIFY_API_TOKEN }}`
3. Execute Node
4. ✅ Должен запуститься БЕЗ ошибки "Доступ к переменным окружения запрещен"

### Тест 2: Полный тест workflow

1. Telegram → /start
2. Нажмите "🏢 Авито"
3. ✅ Парсинг запускается
4. ✅ Результаты в Google Sheets
5. ✅ Telegram уведомление

---

## ❓ FAQ

**Q: Безопасно ли N8N_BLOCK_ENV_ACCESS_IN_NODE=false?**

A: Да, если вы доверяете всем workflows в вашем n8n instance. Эта настройка позволяет workflows читать Environment Variables. Если у вас multi-user setup, будьте осторожны.

**Q: Можно ли использовать разные токены для разных workflows?**

A: Да, вы можете установить несколько Environment Variables с разными именами:
- `APIFY_API_TOKEN_PROD`
- `APIFY_API_TOKEN_DEV`

И использовать в разных workflows.

**Q: Что делать если я забыл токен?**

A: Токен можно найти в Apify:
1. https://console.apify.com/
2. Settings → Integrations → API tokens
3. Скопируйте API token

**Q: Нужно ли перезапускать n8n после изменения Environment Variables?**

A: Да, после изменения системных Environment Variables нужно перезапустить n8n. Но если вы меняете через n8n UI (Settings → Environment Variables), перезапуск не нужен.

---

## 🎯 Итог

**Проблема:** Доступ к Environment Variables запрещён

**Решение:**
1. Установите `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`
2. Установите `APIFY_API_TOKEN` в Environment Variables
3. Перезапустите n8n
4. Импортируйте `user-workflow-FIXED.json`
5. Всё работает! ✅
