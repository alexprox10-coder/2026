# ⚡ Быстрое исправление: access to env vars denied

## 🚨 Проблема
```
access to env vars denied
```

## ✅ Решение (3 шага)

### ШАГ 1: Остановите n8n
```bash
pkill n8n
```

### ШАГ 2: Запустите с правильной переменной
```bash
N8N_BLOCK_ENV_ACCESS_IN_NODE=false n8n start
```

### ШАГ 3: Установите токен в n8n UI
1. http://localhost:5678 → Settings → Environment Variables
2. Add Variable:
   - Name: `APIFY_API_TOKEN`
   - Value: ваш_токен (из https://console.apify.com/account/integrations)

**ГОТОВО!** ✅

---

## 🔄 Для постоянного использования

Добавьте в ~/.bashrc или ~/.zshrc:
```bash
export N8N_BLOCK_ENV_ACCESS_IN_NODE=false
```

Затем:
```bash
source ~/.bashrc
n8n start
```

---

## 📝 Проверка

Команда:
```bash
echo $N8N_BLOCK_ENV_ACCESS_IN_NODE
```

Должна вывести: `false`

---

## 🐳 Для Docker

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BLOCK_ENV_ACCESS_IN_NODE=false \
  -e APIFY_API_TOKEN=ваш_токен \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

---

## ❌ Если НЕ РАБОТАЕТ

Используйте workflow БЕЗ Environment Variables:

**Импортируйте:** `user-workflow-NO-ENV.json`

Но СНАЧАЛА замените в этом файле:
- `{{ $env.APIFY_API_TOKEN }}` → `ваш_реальный_токен`

Найдите все 4 места в файле и замените.

**⚠️ ВНИМАНИЕ:** Токен будет виден в workflow JSON (не рекомендуется).
