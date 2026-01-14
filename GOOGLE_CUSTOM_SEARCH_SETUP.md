# Настройка Google Custom Search API (Бесплатно!)

## 🎯 Что это?

**Google Custom Search API** - бесплатная альтернатива SerpAPI от самого Google.

**Лимиты:**
- ✅ **100 запросов в день** - бесплатно навсегда
- ✅ Без кредитной карты
- ✅ Официальный API от Google

---

## 📋 Шаг 1: Получить API ключ

### 1.1 Создать проект в Google Cloud

1. Перейдите: https://console.cloud.google.com/
2. Нажмите **"Создать проект"** (Create Project)
3. Введите название: `n8n Lead Generation`
4. Нажмите **"Создать"**

### 1.2 Включить Custom Search API

1. В боковом меню выберите: **APIs & Services → Library**
2. Найдите: `Custom Search API`
3. Нажмите на карточку **"Custom Search API"**
4. Нажмите **"Enable"** (Включить)

### 1.3 Создать API ключ

1. Перейдите: **APIs & Services → Credentials**
2. Нажмите **"+ CREATE CREDENTIALS"**
3. Выберите **"API key"**
4. Скопируйте ключ (он выглядит так: `AIzaSyC-xxxxxxxxxxxxxxxxxxxxxxxxxxx`)
5. **Сохраните этот ключ!**

**Прямая ссылка:** https://console.cloud.google.com/apis/credentials

---

## 📋 Шаг 2: Создать Custom Search Engine

### 2.1 Создать поисковик

1. Перейдите: https://programmablesearchengine.google.com/
2. Нажмите **"Начать"** или **"Добавить"**
3. Заполните форму:

   **Сайты для поиска:** Выберите **"Поиск по всему Интернету"**

   **Название поисковика:** `Поиск компаний Амурская область`

   **Язык:** Русский

4. Нажмите **"Создать"**

### 2.2 Включить поиск по всему интернету

1. После создания откройте ваш поисковик
2. В левом меню нажмите **"Настройки"** → **"Основные"**
3. Найдите раздел **"Сайты для поиска"**
4. Включите опцию: ✅ **"Поиск по всему Интернету"**
5. Нажмите **"Обновить"**

### 2.3 Получить Search Engine ID (CX)

1. В настройках найдите раздел **"Основные"**
2. Найдите поле **"Идентификатор поисковика"** или **"Search engine ID"**
3. Скопируйте ID (выглядит так: `a1b2c3d4e5f6g7h8i`)
4. **Сохраните этот ID!**

**Прямая ссылка:** https://programmablesearchengine.google.com/controlpanel/all

---

## 📋 Шаг 3: Настроить workflow в n8n

### 3.1 Импортировать workflow

1. Откройте n8n
2. Нажмите **"Import from File"**
3. Выберите: `child_workflow_01_AgentLeadAddQuery_GoogleCSE.json`
4. Нажмите **"Import"**

### 3.2 Вставить ключи

Откройте ноду **"🔍 Google Custom Search"**:

1. Найдите параметр **`key`**
   - Вставьте ваш API ключ: `AIzaSyC-xxxxxxxxxxxxxxxxxxxxxxxxxxx`

2. Найдите параметр **`cx`**
   - Вставьте ваш Search Engine ID: `a1b2c3d4e5f6g7h8i`

3. В ноде **"💾 Save to CompanySites"**:
   - Замените `YOUR_GOOGLE_SHEET_ID_HERE` на ID вашей таблицы

### 3.3 Активировать workflow

1. Нажмите **"Active"** в правом верхнем углу
2. Workflow готов к работе! ✅

---

## 🧪 Шаг 4: Тестирование

### Тест через Postman или cURL:

```bash
curl -X POST https://your-n8n-instance.com/webhook/add-search-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "агентство недвижимости",
    "city": "Благовещенск",
    "region": "Амурская область"
  }'
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "websites_found": 8,
  "message": "Search completed, websites added to database",
  "query": "агентство недвижимости"
}
```

---

## 🔧 Настройки ноды в n8n

Вот что нужно заполнить в ноде **"🔍 Google Custom Search"**:

```
Метод: GET
URL: https://www.googleapis.com/customsearch/v1
Аутентификация: None

Query Parameters:
├─ key = YOUR_GOOGLE_API_KEY_HERE
├─ cx = YOUR_SEARCH_ENGINE_ID_HERE
├─ q = {{ $json.query }}
├─ lr = lang_ru
├─ gl = ru
└─ num = 10
```

---

## ❓ Частые вопросы

### Сколько это стоит?
**Бесплатно!** 100 запросов в день навсегда. Не требует кредитной карты.

### Что если нужно больше 100 запросов?
Создайте несколько проектов в Google Cloud с разными API ключами. Каждый проект = +100 запросов.

### Где посмотреть лимиты?
https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas

### Работает ли поиск только по России?
Да, параметр `gl=ru` и `lr=lang_ru` настраивают поиск по российским сайтам на русском языке.

### Можно ли фильтровать результаты?
Да, в коде уже есть фильтр, который исключает:
- Социальные сети (VK, Facebook, Instagram)
- Доски объявлений (Avito, 2GIS)
- Отзовики и Wikipedia

---

## 🆚 Сравнение с SerpAPI

| Параметр | Google Custom Search | SerpAPI |
|----------|---------------------|---------|
| **Цена** | Бесплатно (100/день) | $50/мес (5000 запросов) |
| **Регистрация** | Без карты | Требует карту |
| **Качество** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Скорость** | Быстро | Очень быстро |
| **Лимиты** | 100/день | 5000/мес или 100/день |

**Вывод:** Для малого бизнеса Google Custom Search идеален!

---

## 🚀 Что дальше?

После настройки у вас будет **полный цикл**:

```
1. Поиск компаний (Google Custom Search) ✅
   ↓
2. Сбор контактных данных (Google Gemini) ✅
   ↓
3. Генерация персональных предложений (AI) ✅
   ↓
4. Готовые черновики писем для отправки ✅
```

**Все бесплатно!**

---

## 📞 Поддержка

Если что-то не работает:
1. Проверьте, что API включен в Google Cloud Console
2. Проверьте лимиты: https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas
3. Убедитесь что Search Engine настроен на "Поиск по всему Интернету"
4. Проверьте логи выполнения workflow в n8n

---

**✅ Готово! Теперь у вас есть бесплатная система поиска компаний!**
