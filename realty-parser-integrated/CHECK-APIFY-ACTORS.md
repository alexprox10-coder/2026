# 🔍 Проверка и обновление Apify Actors

## 📋 Ваши Actors

Вы используете два Apify actors:

### Actor 1: Avito
- **ID в workflow**: `eiD1SmA4A6aojHvYl`
- **Ссылка**: https://console.apify.com/actors/eiD1SmA4A6aojHvYl/input
- **Используется в**: node "Запуск Авито"

### Actor 2 (новый):
- **ID**: `CBn1BidHkyYcqYpPd`
- **Ссылка**: https://console.apify.com/actors/CBn1BidHkyYcqYpPd/input
- **Статус**: Нужно проверить что это за actor

---

## ✅ Как проверить какой actor правильный

### Шаг 1: Откройте каждый actor в Apify Console

**Actor 1:**
```
https://console.apify.com/actors/eiD1SmA4A6aojHvYl/input
```

**Actor 2:**
```
https://console.apify.com/actors/CBn1BidHkyYcqYpPd/input
```

### Шаг 2: Проверьте информацию

Для каждого actor смотрите:

1. **Название** - что парсит этот actor?
2. **Описание** - для какого сайта?
3. **Input Parameters** - какие параметры принимает?
4. **Example Output** - какие данные возвращает?

### Шаг 3: Определите правильные actors

**Для Avito:**
- Actor должен парсить avito.ru
- Должен принимать `startUrls` с URL Avito
- Должен возвращать объявления с полями: title, price, url, address

**Для CIAN:**
- Actor должен парсить cian.ru
- Должен принимать location (город)
- Должен возвращать объявления с полями: title, price, url, address

---

## 🔧 Обновление Actor IDs в workflow

### Если нужно изменить Avito actor:

**Текущий workflow использует:**
```
Actor ID: eiD1SmA4A6aojHvYl
```

**Если правильный actor:** `CBn1BidHkyYcqYpPd`

**Тогда измените в workflow:**

1. Откройте файл: `user-workflow-FIXED.json`

2. Найдите node "Запуск Авито" (строка ~26-35):
```json
{
  "parameters": {
    "method": "POST",
    "url": "https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl/runs?token={{ $env.APIFY_API_TOKEN }}&waitForFinish=120",
    ...
  },
  "name": "Запуск Авито"
}
```

3. Замените actor ID в URL:
```json
"url": "https://api.apify.com/v2/acts/CBn1BidHkyYcqYpPd/runs?token={{ $env.APIFY_API_TOKEN }}&waitForFinish=120"
```

4. Сохраните файл

5. Ре-импортируйте workflow в n8n

---

## 🧪 Тест Actor через API

Вы можете проверить actor через API перед использованием в workflow:

### Тест Actor 1 (eiD1SmA4A6aojHvYl):

```bash
curl -X POST \
  "https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl/runs?token=YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "startUrls": [
      "https://www.avito.ru/amurskaya_oblast_blagoveschensk/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg"
    ],
    "limit": 5,
    "proxyConfiguration": {
      "useApifyProxy": true,
      "apifyProxyGroups": ["RESIDENTIAL"]
    }
  }'
```

### Тест Actor 2 (CBn1BidHkyYcqYpPd):

```bash
curl -X POST \
  "https://api.apify.com/v2/acts/CBn1BidHkyYcqYpPd/runs?token=YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "startUrls": [
      "https://www.avito.ru/amurskaya_oblast_blagoveschensk/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg"
    ],
    "limit": 5,
    "proxyConfiguration": {
      "useApifyProxy": true,
      "apifyProxyGroups": ["RESIDENTIAL"]
    }
  }'
```

**Замените YOUR_TOKEN на ваш Apify API token**

**Ожидаемый результат:**
```json
{
  "data": {
    "id": "...",
    "actId": "...",
    "status": "RUNNING",
    "defaultDatasetId": "..."
  }
}
```

---

## 📊 Сравнение Actors

Чтобы выбрать правильный actor, проверьте:

### Критерий 1: Функциональность
- ✅ Парсит нужный сайт (Avito или CIAN)
- ✅ Возвращает все нужные поля
- ✅ Поддерживает фильтры (город, тип недвижимости)

### Критерий 2: Цена
- Сколько credits потребляет за запуск?
- Используйте дешёвый actor если качество одинаковое

### Критерий 3: Надёжность
- Проверьте Last runs в Apify Console
- Какой % успешных запусков?
- Есть ли recent failures?

### Критерий 4: Актуальность
- Когда actor последний раз обновлялся?
- Есть ли active maintenance?

---

## 🎯 Рекомендация

### Если оба актора парсят Avito:

1. **Протестируйте оба** через API (см. выше)
2. **Сравните результаты**:
   - Какой возвращает больше данных?
   - Какой быстрее?
   - Какой дешевле?
3. **Выберите лучший**
4. **Обновите в workflow**

### Если CBn1BidHkyYcqYpPd для CIAN:

Тогда обновите CIAN actor в workflow:

**Текущий:**
```json
"url": "https://api.apify.com/v2/acts/igolaizola~cian-ru-scraper/runs?token={{ $env.APIFY_API_TOKEN }}&waitForFinish=120"
```

**Новый:**
```json
"url": "https://api.apify.com/v2/acts/CBn1BidHkyYcqYpPd/runs?token={{ $env.APIFY_API_TOKEN }}&waitForFinish=120"
```

---

## 📝 Где обновить Actor IDs в workflow

В файле `user-workflow-FIXED.json` есть 4 места где используются actor IDs:

### 1. Node "Запуск Авито" (строка ~28):
```json
"url": "=https://api.apify.com/v2/acts/eiD1SmA4A6aojHvYl/runs?token={{ $env.APIFY_API_TOKEN }}&waitForFinish=120"
```

### 2. Node "Запуск ЦИАН" (строка ~48):
```json
"url": "https://api.apify.com/v2/acts/igolaizola~cian-ru-scraper/runs?token={{ $env.APIFY_API_TOKEN }}&waitForFinish=120"
```

### 3. Node "Результаты Авито" (строка ~67):
```json
"url": "=https://api.apify.com/v2/datasets/{{ $json.data.defaultDatasetId }}/items?token={{ $env.APIFY_API_TOKEN }}"
```
*Здесь НЕ меняйте - это URL для получения результатов*

### 4. Node "Результаты ЦИАН" (строка ~81):
```json
"url": "=https://api.apify.com/v2/datasets/{{ $json.data.defaultDatasetId }}/items?token={{ $env.APIFY_API_TOKEN }}"
```
*Здесь НЕ меняйте - это URL для получения результатов*

---

## ❓ FAQ

**Q: Как узнать что за actor по ID?**

A:
1. Откройте в браузере: `https://console.apify.com/actors/[ACTOR_ID]/input`
2. Или через API: `curl "https://api.apify.com/v2/acts/[ACTOR_ID]?token=YOUR_TOKEN"`

**Q: Можно ли использовать разные actors для тестирования и production?**

A: Да, создайте две копии workflow с разными actor IDs.

**Q: Что делать если actor не работает?**

A:
1. Проверьте Last runs в Apify Console
2. Посмотрите Log для понимания ошибки
3. Попробуйте альтернативный actor
4. Напишите в Apify Support

**Q: Как найти лучший actor для Avito/CIAN?**

A:
1. Apify Store: https://apify.com/store
2. Поиск: "avito" или "cian"
3. Фильтр: Public, Most popular
4. Сравните ratings и reviews

---

## 🎯 Итог

**Ваши actors:**
1. `eiD1SmA4A6aojHvYl` - currently used for Avito
2. `CBn1BidHkyYcqYpPd` - new actor (нужно проверить)

**Что сделать:**
1. Откройте оба actors в Apify Console
2. Проверьте что каждый парсит (Avito или CIAN)
3. Протестируйте через API
4. Обновите workflow если нужно
5. Ре-импортируйте в n8n
6. Тест! ✅
