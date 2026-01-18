# 🔥 Firebase Setup - Полное руководство

## ☁️ Преимущества Firebase

| Преимущество | Описание |
|--------------|----------|
| ☁️ **Облачное хранилище** | Данные доступны из любой точки мира |
| 🚀 **Масштабируемость** | Автоматическое масштабирование |
| 💰 **Бесплатный план** | До 1GB хранилища и 50K чтений/день |
| 🔒 **Безопасность** | Встроенная аутентификация и правила доступа |
| 🔄 **Real-time синхронизация** | Данные обновляются в реальном времени |
| 📊 **Удобный интерфейс** | Firebase Console для просмотра данных |

---

## 🚀 Быстрый старт (15 минут)

### Шаг 1: Создание Firebase проекта

1. Перейдите на [Firebase Console](https://console.firebase.google.com/)
2. Нажмите **"Добавить проект"** (Add project)
3. Введите название: `rental-parser`
4. Отключите Google Analytics (не обязательно)
5. Нажмите **"Создать проект"**

### Шаг 2: Создание Firestore Database

1. В левом меню выберите **"Firestore Database"**
2. Нажмите **"Создать базу данных"**
3. Выберите режим:
   - **"Начать в тестовом режиме"** (для начала)
   - Или **"Начать в production режиме"** (безопаснее)
4. Выберите регион: **europe-west1** (Бельгия) или ближайший
5. Нажмите **"Включить"**

### Шаг 3: Получение Service Account ключа

1. В Firebase Console нажмите ⚙️ (Settings) → **"Настройки проекта"**
2. Перейдите на вкладку **"Service accounts"**
3. Нажмите **"Создать новый закрытый ключ"**
4. Подтвердите и скачайте файл **`rental-parser-firebase-credentials.json`**

⚠️ **ВАЖНО:** Этот файл содержит секретные ключи! Не публикуйте его!

### Шаг 4: Установка зависимостей

```bash
cd /home/user/2026/rental_parser

# Установите Firebase зависимости
pip install -r requirements_firebase.txt
```

### Шаг 5: Настройка credentials

Разместите скачанный JSON файл:

```bash
# Вариант 1: В корне проекта (рекомендуется для разработки)
cp ~/Downloads/rental-parser-firebase-credentials.json /home/user/2026/rental_parser/firebase-credentials.json

# Вариант 2: В безопасном месте
cp ~/Downloads/rental-parser-firebase-credentials.json ~/.config/rental-parser/firebase-creds.json

# Установите переменную окружения
export FIREBASE_CREDENTIALS_PATH=/home/user/2026/rental_parser/firebase-credentials.json
```

### Шаг 6: Проверка подключения

```bash
cd /home/user/2026/rental_parser

# Тест подключения
python3 -c "from database.firebase_config import init_firebase; init_firebase(); print('✓ Firebase connected!')"
```

Если вывод: `✓ Firebase connected!` - все работает!

### Шаг 7: Первый запуск парсера

```bash
# Запустите парсер
python3 main_firebase.py --max-pages 1

# Проверьте статистику
python3 main_firebase.py --stats
```

### Шаг 8: Проверка данных в Firebase Console

1. Откройте [Firebase Console](https://console.firebase.google.com/)
2. Выберите ваш проект
3. Перейдите в **"Firestore Database"**
4. Вы увидите коллекции:
   - `rental_listings` - объявления
   - `parsing_sessions` - сессии парсинга
   - `managers` - менеджеры

---

## 📁 Структура данных в Firestore

### Collection: `rental_listings`

```json
{
  "listing_id": "cian_abc123",
  "platform": "cian",
  "url": "https://cian.ru/...",
  "title": "2-комн квартира, 55 м²",
  "price": 45000,
  "phone": "+79991234567",
  "address": "Москва, ул. Ленина, 10",
  "rooms": 2,
  "area": 55,
  "floor": 5,
  "total_floors": 12,
  "description": "...",
  "raw_data": "{...}",
  "created_at": "2026-01-17T14:35:22Z",
  "sent_to_manager": false,
  "sent_at": null,
  "manager_id": null,
  "is_active": true,
  "last_seen": "2026-01-17T14:35:22Z"
}
```

### Collection: `parsing_sessions`

```json
{
  "platform": "cian",
  "started_at": "2026-01-17T14:35:22Z",
  "completed_at": "2026-01-17T14:37:15Z",
  "status": "completed",
  "listings_found": 20,
  "listings_new": 5,
  "error_message": null
}
```

### Collection: `managers`

```json
{
  "telegram_id": "123456789",
  "name": "John Doe",
  "is_active": true,
  "created_at": "2026-01-17T14:35:22Z",
  "city": "москва",
  "max_price": 80000,
  "min_rooms": 2
}
```

---

## 🔧 Настройка n8n с Firebase

### Импорт workflow

1. Откройте n8n
2. Import → выберите **`rental_parser_firebase.json`**
3. Нажмите **"Import"**

### Настройка Environment Variables

В n8n: **Settings → Environment Variables**

```env
TELEGRAM_CHAT_ID=123456789
FIREBASE_CREDENTIALS_PATH=/home/user/2026/rental_parser/firebase-credentials.json
```

### Проверка путей в нодах

Убедитесь что в **Execute Command** нодах указаны правильные скрипты:

```bash
# Run Parser
python3 scripts/firebase_run_parser.py

# Get Unsent
python3 scripts/firebase_get_unsent.py

# Mark Sent
python3 scripts/firebase_mark_sent.py {{ $json.listing_id }}
```

---

## 🔒 Security Rules для Firestore

Настройте правила доступа в Firebase Console:

### Для разработки (тестовый режим):

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

### Для production (рекомендуется):

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Только сервисный аккаунт может писать
    match /rental_listings/{listing} {
      allow read: if true;
      allow write: if request.auth != null;
    }

    match /parsing_sessions/{session} {
      allow read: if true;
      allow write: if request.auth != null;
    }

    match /managers/{manager} {
      allow read, write: if request.auth != null;
    }
  }
}
```

Опубликуйте правила в: **Firestore Database → Rules → Publish**

---

## 📊 Индексы для оптимизации

Firestore автоматически создает индексы, но для оптимизации создайте composite indexes:

### Index 1: Unsent listings

```
Collection: rental_listings
Fields:
  - sent_to_manager (Ascending)
  - is_active (Ascending)
  - created_at (Descending)
```

### Index 2: Platform statistics

```
Collection: rental_listings
Fields:
  - platform (Ascending)
  - created_at (Descending)
```

Создайте в: **Firestore Database → Indexes → Create Index**

---

## 💰 Ценовые планы Firebase

### Free Spark Plan (Бесплатно)

- ✅ 1 GB хранилища
- ✅ 50,000 чтений/день
- ✅ 20,000 записей/день
- ✅ 20,000 удалений/день

**Этого хватит для:**
- ~10,000-50,000 объявлений
- ~100-500 новых объявлений/день
- Несколько парсингов в день

### Blaze Plan (Pay as you go)

- Оплата только за использование
- $0.06 за 100,000 чтений
- $0.18 за 100,000 записей
- $0.02 за GB хранилища/месяц

**Примерная стоимость:**
- 100,000 объявлений: ~$2-5/месяц
- 1,000 новых объявлений/день: ~$5-10/месяц

[Подробнее о ценах](https://firebase.google.com/pricing)

---

## 🔄 Миграция из SQLite в Firebase

Если у вас уже есть данные в SQLite:

```python
#!/usr/bin/env python3
"""
Migrate from SQLite to Firebase
"""
from database.models import init_db as init_sqlite
from database.firebase_config import init_firebase
from database.firebase_models import RentalListingFirebase

# Connect to both databases
sqlite_db = init_sqlite('rental_parser.db')
init_firebase('firebase-credentials.json')

# Get all listings from SQLite
from database.models import RentalListing
listings = sqlite_db.query(RentalListing).all()

# Migrate to Firebase
for listing in listings:
    data = {
        'listing_id': listing.listing_id,
        'platform': listing.platform,
        'url': listing.url,
        'title': listing.title,
        'price': listing.price,
        'phone': listing.phone,
        'address': listing.address,
        'rooms': listing.rooms,
        'area': listing.area,
        'floor': listing.floor,
        'total_floors': listing.total_floors,
        'description': listing.description,
        'raw_data': listing.raw_data,
        'sent_to_manager': listing.sent_to_manager,
        'is_active': listing.is_active
    }

    RentalListingFirebase.create(data)
    print(f"✓ Migrated {listing.listing_id}")

print(f"\n✅ Migration complete! Migrated {len(listings)} listings")
```

Сохраните как `migrate_to_firebase.py` и запустите:

```bash
python3 migrate_to_firebase.py
```

---

## 🐛 Решение проблем

### ❌ Ошибка "Could not automatically determine credentials"

**Решение:**

```bash
# Установите переменную окружения
export FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json

# Или укажите явно в коде
init_firebase('/path/to/firebase-credentials.json')
```

### ❌ Ошибка "Permission denied"

**Решение:**

1. Проверьте Security Rules в Firebase Console
2. Убедитесь что используете правильный service account
3. Проверьте что файл credentials.json не поврежден

### ❌ Ошибка "Quota exceeded"

**Решение:**

1. Проверьте использование в Firebase Console → Usage
2. Увеличьте лимиты или перейдите на Blaze Plan
3. Оптимизируйте запросы (используйте индексы)

### ❌ Медленные запросы

**Решение:**

1. Создайте composite indexes (см. выше)
2. Уменьшите limit в запросах
3. Используйте кэширование

---

## 📈 Мониторинг

### Firebase Console

1. Откройте [Firebase Console](https://console.firebase.google.com/)
2. Выберите проект
3. Перейдите в **"Usage and billing"**
4. Смотрите:
   - Количество запросов
   - Использование хранилища
   - Количество активных соединений

### Alerts

Настройте уведомления:

1. Firebase Console → **"Alerts"**
2. Создайте alert:
   - **"Database reads > 40,000/day"** → Email уведомление
   - **"Storage > 900 MB"** → Email уведомление

---

## ✅ Преимущества Firebase версии

| Преимущество | SQLite | Firebase |
|--------------|--------|----------|
| Облачное хранилище | ❌ | ✅ |
| Доступ из любой точки | ❌ | ✅ |
| Автоматические бэкапы | ❌ | ✅ |
| Масштабируемость | ❌ | ✅ |
| Real-time обновления | ❌ | ✅ |
| Графический интерфейс | ❌ | ✅ |
| Бесплатный план | ✅ | ✅ |
| Простота настройки | ✅ | ⚠️ |

---

## 🎯 Чек-лист готовности

- [ ] Firebase проект создан
- [ ] Firestore Database включен
- [ ] Service Account ключ скачан
- [ ] `firebase-credentials.json` размещен
- [ ] `requirements_firebase.txt` установлены
- [ ] Тестовое подключение успешно
- [ ] Security Rules настроены
- [ ] Индексы созданы
- [ ] n8n workflow импортирован
- [ ] Environment Variables установлены
- [ ] Первый парсинг запущен

---

## 📚 Дополнительные ресурсы

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Guide](https://firebase.google.com/docs/firestore)
- [Python Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Pricing Calculator](https://firebase.google.com/pricing)

---

**Firebase версия готова! Следуйте инструкциям выше** 🔥
