# 📊 Визуальная схема Unified Workflow

## Общий обзор

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                    🏠 UNIFIED RENTAL PARSER WORKFLOW                     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

                              ⏰ ТРИГГЕРЫ
                     ┌────────────┬────────────┐
                     │            │            │
                 Schedule     Manual      Auto
              (Every 4h)    Webhook    (External)
                     │            │            │
                     └────────────┴────────────┘
                              │
                              ↓
                    ╔═══════════════════╗
                    ║   СТАРТ ПАРСИНГА  ║
                    ╚═══════════════════╝
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ↓                 ↓                 ↓
     ┏━━━━━━━━━━┓      ┏━━━━━━━━━━┓      ┏━━━━━━━━━━┓
     ┃          ┃      ┃          ┃      ┃          ┃
     ┃   🔵     ┃      ┃   🔴     ┃      ┃   🟢     ┃
     ┃  CIAN    ┃      ┃ YANDEX   ┃      ┃  AVITO   ┃
     ┃          ┃      ┃          ┃      ┃          ┃
     ┃ ~5 pages ┃      ┃ ~5 pages ┃      ┃ ~5 pages ┃
     ┃ 3-6 sec  ┃      ┃ 4-7 sec  ┃      ┃ 5-8 sec  ┃
     ┗━━━━━━━━━━┛      ┗━━━━━━━━━━┛      ┗━━━━━━━━━━┛
            │                 │                 │
            │   ~20 listings  │  ~15 listings   │  ~25 listings
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                              ↓
                    ╔═══════════════════╗
                    ║  MERGE PLATFORMS  ║
                    ║   ~60 listings    ║
                    ╚═══════════════════╝
                              │
                              ↓
                    ┌─────────────────┐
                    │ 💾 SAVE TO DB   │
                    │  (Deduplication)│
                    └─────────────────┘
                              │
                  Existing: 45 │ New: 15
                              │
                              ↓
                    ┌─────────────────┐
                    │ ✅ CHECK NEW?   │
                    └─────────────────┘
                         /        \
                    YES /          \ NO
                       /            \
                      ↓              ↓
           ┏━━━━━━━━━━━━━┓    ┌──────────────┐
           ┃  SEND TO    ┃    │ No Listings  │
           ┃  MANAGER    ┃    │   Notice     │
           ┗━━━━━━━━━━━━━┛    └──────────────┘
                  │
                  │ For each listing (15)
                  ↓
        ┌──────────────────┐
        │ 📤 SPLIT         │
        │  15 → 1+1+1...   │
        └──────────────────┘
                  │
                  ↓
        ┌──────────────────┐
        │ ✍️ FORMAT        │
        │  🔵 Cian: ...    │
        │  🔴 Yandex: ...  │
        │  🟢 Avito: ...   │
        └──────────────────┘
                  │
                  ↓
        ┌──────────────────┐
        │ 📱 TELEGRAM      │
        │  Send message    │
        └──────────────────┘
                  │
                  ↓
        ┌──────────────────┐
        │ ⏳ WAIT 3s       │
        │  (Rate limit)    │
        └──────────────────┘
                  │
                  ↓
        ┌──────────────────┐
        │ 📞 HAS PHONE?    │
        └──────────────────┘
              /        \
         YES /          \ NO
            /            \
           ↓              ↓
    ┌──────────┐    ┌──────────┐
    │ AUTODIAL │    │   SKIP   │
    │ Webhook  │    │          │
    └──────────┘    └──────────┘
           │              │
           └──────┬───────┘
                  ↓
        ┌──────────────────┐
        │ ✔️ MARK SENT     │
        │  sent_at=now()   │
        └──────────────────┘
                  │
                  ↓
        ┌──────────────────┐
        │ 💾 SAVE SHEETS   │
        │  (Optional)      │
        └──────────────────┘
                  │
                  ↓
              ┏━━━━━━━━┓
              ┃  DONE  ┃
              ┗━━━━━━━━┛
```

---

## 🔄 Детальный поток данных

### 1. Входные данные (Input)

**Триггер:**
```
Schedule: Every 4 hours
OR
Webhook: POST /rental-parser-manual
```

**Конфигурация:**
```json
{
  "city": "москва",
  "max_pages": 5,
  "platforms": ["cian", "yandex", "avito"]
}
```

---

### 2. Парсинг (Parallel)

#### 🔵 Cian.ru
```python
CianParser('москва').parse(max_pages=5)
↓
[
  {
    "platform": "cian",
    "listing_id": "cian_abc123",
    "url": "https://cian.ru/rent/...",
    "title": "2-комн квартира, 55 м²",
    "price": 45000,
    "rooms": 2,
    "area": 55,
    "phone": "+79991234567"
  },
  ... (~20 listings)
]
```

#### 🔴 Yandex.Realty
```python
YandexRealtyParser('москва').parse(max_pages=5)
↓
[
  {
    "platform": "yandex",
    "listing_id": "yandex_xyz789",
    ...
  },
  ... (~15 listings)
]
```

#### 🟢 Avito.ru
```python
AvitoParser('москва').parse(max_pages=5)
↓
[
  {
    "platform": "avito",
    "listing_id": "avito_def456",
    ...
  },
  ... (~25 listings)
]
```

**Время выполнения:**
- Cian: ~2-3 минуты
- Yandex: ~2-4 минуты
- Avito: ~3-5 минут

**Параллельное выполнение:** ~3-5 минут (вместо ~10 минут последовательно)

---

### 3. Объединение (Merge)

```javascript
all_listings = [
  ...cian_listings,    // 20
  ...yandex_listings,  // 15
  ...avito_listings    // 25
]
// Total: 60 listings
```

---

### 4. Сохранение в БД (Deduplication)

```python
db = init_db()
new_listings = []

for listing in all_listings:
    if not exists(listing_id):
        db.add(RentalListing(**listing))
        new_listings.append(listing)

db.commit()
```

**Результат:**
```
Total: 60 listings
Existing: 45 listings (already in DB)
New: 15 listings (to be sent)
```

---

### 5. Проверка новых объявлений

```javascript
if (new_listings.length > 0) {
  // Send to manager
} else {
  // Send "No new listings" notice
}
```

---

### 6. Отправка менеджеру

#### Разделение на отдельные объявления
```javascript
[listing1, listing2, ..., listing15]
↓
listing1 → Process
listing2 → Process
...
listing15 → Process
```

#### Форматирование сообщения
```
🔵 Новое объявление - Cian.ru

*2-комн квартира, 55 м²*

💰 45,000 ₽/мес
🏠 2-комн, 55 м²
📍 Москва, ул. Ленина, 10
📞 `+79991234567`

🔗 [Открыть объявление](https://cian.ru/...)

_Площадка: Cian.ru_
```

#### Отправка в Telegram
```
→ Send message
→ Wait 3 seconds (rate limit)
→ Next message
```

---

### 7. Автодозвон (Optional)

**Если телефон указан:**
```http
POST https://your-telephony.com/webhook
Content-Type: application/json

{
  "phone": "+79991234567",
  "listing_id": "cian_abc123",
  "platform": "cian",
  "url": "https://cian.ru/..."
}
```

**Телефония инициирует:**
1. Звонок менеджеру
2. После ответа - соединение с клиентом

---

### 8. Маркировка

```python
listing.sent_to_manager = True
listing.sent_at = datetime.utcnow()
listing.manager_id = 'n8n_workflow'
db.commit()
```

---

### 9. Сохранение в Google Sheets

```
| Timestamp           | Platform | URL              | Title      | Price | Phone        | Sent |
|---------------------|----------|------------------|------------|-------|--------------|------|
| 2026-01-17 14:35:22 | cian     | https://cian...  | 2-комн...  | 45000 | +7999123...  | TRUE |
| 2026-01-17 14:35:25 | yandex   | https://yandex...| 1-комн...  | 35000 | +7999456...  | TRUE |
...
```

---

## 📊 Статистика выполнения

### Уведомление о завершении

**При наличии новых объявлений:**
```
✅ Парсинг завершен!

📊 Статистика:
🔵 Cian: 20 объявлений
🔴 Yandex: 15 объявлений
🟢 Avito: 25 объявлений

🆕 Новых: 15

⏰ Время: 17.01.2026, 14:35:22
```

**Без новых объявлений:**
```
😔 Новых объявлений не найдено

Все объявления уже были отправлены ранее.

⏰ Время: 17.01.2026, 14:35:22
```

---

## ⚡ Производительность

### Скорость обработки

| Этап                    | Время       | Примечание                |
|-------------------------|-------------|---------------------------|
| Парсинг (параллельно)   | 3-5 мин     | Все 3 платформы сразу     |
| Сохранение в БД         | 1-2 сек     | SQLite                    |
| Отправка в Telegram     | 3 сек/объявление | Rate limit          |
| Автодозвон              | 1-2 сек     | Webhook                   |
| Сохранение в Sheets     | 0.5 сек     | Google API                |

**Общее время:** ~5-10 минут для 15 новых объявлений

### Оптимизация

- ✅ Параллельный парсинг: **экономия 50% времени**
- ✅ Дедупликация в БД: **не обрабатываем дубли**
- ✅ Rate limiting: **защита от банов**
- ✅ Batch Google Sheets: **все за 1 запрос**

---

## 🎯 Ключевые преимущества Unified Workflow

1. **Параллелизм** - все платформы парсятся одновременно
2. **Визуализация** - видно процесс каждой платформы
3. **Гибкость** - легко отключить/настроить любую платформу
4. **Мониторинг** - отдельная статистика по каждой платформе
5. **Отказоустойчивость** - ошибка в одной платформе не блокирует другие
6. **Масштабируемость** - легко добавить новые платформы

---

## 🔧 Настройка под себя

### Изменить город
```python
# В Execute Command нодах
CianParser('санкт-петербург')
YandexRealtyParser('новосибирск')
AvitoParser('екатеринбург')
```

### Изменить количество страниц
```python
# Больше объявлений
parser.parse(max_pages=10)

# Меньше нагрузки
parser.parse(max_pages=3)
```

### Отключить платформу
Просто удалите или деактивируйте соответствующие ноды:
- 🔵 Parse Cian
- 🏷️ Label Cian

### Добавить фильтры
В ноде перед Split Listings:
```javascript
$json.new_listings.filter(listing =>
  listing.price >= 20000 &&
  listing.price <= 80000 &&
  listing.rooms >= 2
)
```

---

## 📈 Масштабирование

### Для большого потока объявлений

1. **Увеличьте частоту парсинга:**
   ```
   Каждые 2 часа вместо 4
   ```

2. **Парсите больше страниц:**
   ```python
   max_pages=10  # Вместо 5
   ```

3. **Добавьте прокси:**
   ```bash
   --proxy-file proxies.txt
   ```

4. **Используйте PostgreSQL вместо SQLite:**
   ```python
   DATABASE_URL=postgresql://user:pass@localhost/rental
   ```

5. **Добавьте кэширование:**
   ```python
   # Redis для хранения уже обработанных listing_id
   ```

---

Подробнее см. [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)
