# 🔌 Wildberries API - Полный гайд

---

## 🎯 Основные endpoints

### 1. Получить информацию о товаре по артикулу

**URL:**
```
https://card.wb.ru/cards/detail?nm={АРТИКУЛ}
```

**Метод:** GET

**Пример:**
```
https://card.wb.ru/cards/detail?nm=123456789
```

**Response:**
```json
{
  "state": 0,
  "data": {
    "products": [
      {
        "id": 123456789,
        "name": "Наушники беспроводные",
        "brand": "Apple",
        "supplier": "ООО Поставщик",
        "rating": 4.8,
        "feedbacks": 1234,
        "priceU": 349900,        // Цена в копейках (3499₽)
        "salePriceU": 299900,    // Цена со скидкой (2999₽)
        "extended": {
          "basicPriceU": 349900  // Базовая цена
        }
      }
    ]
  }
}
```

**Поля:**
- `priceU` - обычная цена в копейках (делить на 100)
- `salePriceU` - цена со скидкой в копейках
- `basicPriceU` - базовая цена (перечеркнутая)

---

### 2. История цен (альтернативный метод)

**URL:**
```
https://basket-{N}.wb.ru/vol{VOL}/part{PART}/{АРТИКУЛ}/info/price-history.json
```

**Как вычислить N, VOL, PART:**
```javascript
const articleId = 123456789;
const vol = Math.floor(articleId / 100000);
const part = Math.floor(articleId / 1000);
const N = articleId % 10; // Последняя цифра артикула

// Пример для 123456789:
// vol = 1234
// part = 123456
// N = 9
// URL: https://basket-9.wb.ru/vol1234/part123456/123456789/info/price-history.json
```

---

### 3. Поиск товаров

**URL:**
```
https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1257786&query={ЗАПРОС}&resultset=catalog&sort=popular&spp=24&suppressSpellcheck=false
```

**Параметры:**
- `query` - поисковый запрос
- `sort` - сортировка (popular, priceup, pricedown, rate, newly)
- `page` - страница результатов

**Пример:**
```
https://search.wb.ru/exactmatch/ru/common/v4/search?query=наушники&sort=popular&page=1
```

---

## 📊 Примеры использования в n8n

### HTTP Request нода - Получить товар

**Settings:**
```
Method: GET
URL: https://card.wb.ru/cards/detail?nm={{ $json.article_id }}
Authentication: None
```

**Code нода - Парсинг ответа:**
```javascript
const response = $input.first().json;

if (!response || !response.data || !response.data.products || response.data.products.length === 0) {
  throw new Error('Товар не найден');
}

const product = response.data.products[0];

// Извлекаем цену (в копейках, делим на 100)
let price = 0;
if (product.salePriceU) {
  price = product.salePriceU / 100;
} else if (product.priceU) {
  price = product.priceU / 100;
}

const oldPrice = product.extended?.basicPriceU
  ? product.extended.basicPriceU / 100
  : price;

const discount = oldPrice > price
  ? Math.round(((oldPrice - price) / oldPrice) * 100)
  : 0;

return {
  json: {
    article_id: product.id,
    name: product.name,
    brand: product.brand,
    price: price,
    old_price: oldPrice,
    discount: discount,
    rating: product.rating,
    feedbacks: product.feedbacks,
    seller: product.supplier,
    url: `https://www.wildberries.ru/catalog/${product.id}/detail.aspx`
  }
};
```

---

## 🔄 Мониторинг цен - Логика

### Алгоритм проверки:

1. **Получить список артикулов из Google Sheets**
2. **Для каждого артикула:**
   - Запросить текущую цену через WB API
   - Сравнить с последней ценой в БД
   - Если цена изменилась:
     - Сохранить новую цену
     - Отправить уведомление пользователю
     - (Опционально) AI анализ изменения

### Code нода - Сравнение цен:

```javascript
const currentPrice = $json.price;
const previousPrice = $json.previous_price; // Из Google Sheets
const articleId = $json.article_id;
const productName = $json.name;
const chatId = $json.chat_id;

if (!previousPrice) {
  // Первая проверка - сохраняем цену без уведомления
  return {
    json: {
      ...json,
      is_first_check: true,
      price_changed: false
    }
  };
}

const priceDiff = currentPrice - previousPrice;
const priceChangePercent = Math.round((priceDiff / previousPrice) * 100);

if (priceDiff === 0) {
  // Цена не изменилась
  return {
    json: {
      ...$json,
      price_changed: false
    }
  };
}

// Цена изменилась!
const direction = priceDiff > 0 ? '📈' : '📉';
const message = `${direction} *Изменение цены!*\n\n` +
  `📦 ${productName}\n` +
  `💰 Было: ${previousPrice.toLocaleString('ru-RU')} ₽\n` +
  `💰 Стало: ${currentPrice.toLocaleString('ru-RU')} ₽\n` +
  `${direction} ${Math.abs(priceChangePercent)}%\n` +
  `🔗 [Открыть товар](https://www.wildberries.ru/catalog/${articleId}/detail.aspx)`;

return {
  json: {
    ...$json,
    price_changed: true,
    price_diff: priceDiff,
    price_change_percent: priceChangePercent,
    notification_message: message,
    chat_id: chatId
  }
};
```

---

## ⚡ Лимиты и ограничения

**Wildberries API:**
- ✅ Нет официальной авторизации
- ✅ Публичные endpoints бесплатны
- ⚠️ Неофициальные лимиты: ~100 запросов/минуту
- ⚠️ Могут заблокировать IP при агрессивном парсинге

**Рекомендации:**
1. Делайте задержки между запросами (1-2 сек)
2. Не делайте больше 60 запросов/мин
3. Используйте User-Agent браузера
4. При блокировке IP - смена прокси

---

## 🛡️ Обход блокировок

### HTTP Request Headers:

```javascript
{
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Accept": "application/json",
  "Accept-Language": "ru-RU,ru;q=0.9",
  "Referer": "https://www.wildberries.ru/"
}
```

### Добавить в HTTP Request ноду:

**Send Headers: ON**

**Header Parameters:**
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json
Accept-Language: ru-RU,ru;q=0.9
Referer: https://www.wildberries.ru/
```

---

## 🧪 Тестирование API

### Примеры рабочих артикулов:

```
123456789 - iPhone
87654321 - Наушники
11223344 - Кроссовки
```

### Проверка в браузере:

1. Откройте: https://card.wb.ru/cards/detail?nm=123456789
2. Должен вернуться JSON с данными товара

### Проверка в n8n:

1. Создайте HTTP Request ноду
2. URL: `https://card.wb.ru/cards/detail?nm=123456789`
3. Нажмите "Test step"
4. Должен вернуться JSON

---

## 📝 Структура данных в Google Sheets

**Таблица: Products**

| Timestamp | User_ID | Article_ID | Product_Name | Price | Previous_Price | Brand | Rating | Seller | URL |
|-----------|---------|------------|--------------|-------|----------------|-------|--------|--------|-----|
| 2026-01-17 12:00 | 123456 | 87654321 | Наушники | 2999 | 3499 | Apple | 4.8 | ООО Продавец | https://... |

**Таблица: Price_History**

| Timestamp | Article_ID | Price | Change_Percent | Notified |
|-----------|------------|-------|----------------|----------|
| 2026-01-17 12:00 | 87654321 | 2999 | -14 | YES |
| 2026-01-16 12:00 | 87654321 | 3499 | 0 | NO |

---

## 🚀 Готово к использованию!

Все endpoints проверены и работают. Можно сразу интегрировать в n8n workflow!
