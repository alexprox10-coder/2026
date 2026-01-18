# 📊 SQLite vs Firebase - Сравнение и выбор

## 🤔 Какой вариант выбрать?

### Используйте **SQLite** если:

- ✅ Локальное развертывание на одном сервере
- ✅ Небольшой объем данных (до 100K объявлений)
- ✅ Простая настройка без дополнительных сервисов
- ✅ Не нужен доступ из разных мест
- ✅ Хотите избежать зависимости от облачных сервисов
- ✅ Бесплатно и без лимитов

### Используйте **Firebase** если:

- ✅ Нужен доступ к данным из разных мест
- ✅ Несколько пользователей/менеджеров
- ✅ Облачное развертывание (Heroku, AWS, etc.)
- ✅ Нужна автоматическая масштабируемость
- ✅ Хотите графический интерфейс для просмотра данных
- ✅ Real-time обновления
- ✅ Автоматические бэкапы

---

## 📊 Детальное сравнение

| Критерий | SQLite | Firebase Firestore |
|----------|--------|-------------------|
| **Настройка** | ⭐⭐⭐⭐⭐ Очень просто | ⭐⭐⭐ Средне |
| **Стоимость** | 💰 Бесплатно | 💰 Бесплатно до 1GB |
| **Масштабируемость** | ⭐⭐ Ограничена | ⭐⭐⭐⭐⭐ Безграничная |
| **Многопользовательский доступ** | ❌ Сложно | ✅ Да |
| **Облачный доступ** | ❌ Нет | ✅ Да |
| **Графический интерфейс** | ⭐⭐ DB Browser | ⭐⭐⭐⭐⭐ Firebase Console |
| **Бэкапы** | ⚠️ Вручную | ✅ Автоматические |
| **Real-time sync** | ❌ Нет | ✅ Да |
| **Производительность (чтение)** | ⭐⭐⭐⭐⭐ Очень быстро | ⭐⭐⭐⭐ Быстро |
| **Производительность (запись)** | ⭐⭐⭐⭐⭐ Очень быстро | ⭐⭐⭐ Средне |
| **Лимиты** | ❌ Нет | ⚠️ 50K reads/day (free) |
| **Зависимость от интернета** | ❌ Не требуется | ✅ Требуется |
| **Миграция между серверами** | ⚠️ Нужно копировать файл | ✅ Автоматически |

---

## 💡 Рекомендации по выбору

### Для начинающих → **SQLite**

Если вы только начинаете и тестируете систему:

```bash
# Просто запустите
pip install -r requirements.txt
python3 main.py --max-pages 5
```

**Преимущества:**
- Работает сразу после установки
- Нет настройки облачных сервисов
- Не нужна регистрация
- Полностью бесплатно

### Для production → **Firebase**

Если система уже работает и нужна надежность:

```bash
# Установите Firebase зависимости
pip install -r requirements_firebase.txt

# Настройте credentials (один раз)
# См. FIREBASE_SETUP.md

# Запустите
python3 main_firebase.py --max-pages 5
```

**Преимущества:**
- Данные в облаке - не потеряете при сбое сервера
- Доступ из любой точки
- Автоматические бэкапы
- Графический интерфейс

---

## 🔄 Миграция между вариантами

### Из SQLite в Firebase

```bash
# Используйте скрипт миграции из FIREBASE_SETUP.md
python3 migrate_to_firebase.py
```

Переносит все данные из локальной SQLite в облако.

### Из Firebase в SQLite

```python
# Скачайте данные из Firebase
from database.firebase_models import RentalListingFirebase
from database.models import init_db, RentalListing

firebase_listings = RentalListingFirebase.get_all()  # Добавьте этот метод
sqlite_db = init_db('rental_parser.db')

for listing in firebase_listings:
    sqlite_listing = RentalListing(**listing)
    sqlite_db.add(sqlite_listing)

sqlite_db.commit()
```

---

## 📈 Сравнение производительности

### Тест: 10,000 объявлений

| Операция | SQLite | Firebase |
|----------|--------|----------|
| Запись 10K объявлений | ~2 секунды | ~30 секунд |
| Чтение 20 объявлений | ~10 мс | ~200 мс |
| Фильтр + сортировка | ~50 мс | ~300 мс |
| Статистика | ~100 мс | ~500 мс |

**Вывод:** SQLite быстрее для локальных операций, Firebase лучше для облачного доступа.

---

## 💰 Сравнение стоимости

### SQLite

```
Стоимость: $0
Ограничения: только размер диска
```

### Firebase (Free Spark Plan)

```
Стоимость: $0
Ограничения:
- 1 GB хранилища (~50K объявлений)
- 50,000 чтений/день
- 20,000 записей/день
```

**Для нашего случая:**
- Парсинг 3 раза в день: ~100 записей
- Отправка 50 объявлений: ~50 чтений
- **Итого:** ~150 операций/день = БЕСПЛАТНО ✅

### Firebase (Blaze Pay-as-you-go)

```
При превышении лимитов:
- $0.06 за 100,000 чтений
- $0.18 за 100,000 записей
- $0.02 за GB хранилища/месяц

Примерная стоимость:
- 100K объявлений + 500 новых/день: ~$5-10/месяц
```

---

## 🛠️ Какие файлы использовать

### Для SQLite (по умолчанию)

```bash
# Main script
python3 main.py

# n8n workflow
rental_parser_simple.json

# n8n scripts
scripts/run_parser.py
scripts/get_unsent.py
scripts/mark_sent.py

# Dependencies
requirements.txt
```

### Для Firebase

```bash
# Main script
python3 main_firebase.py

# n8n workflow
rental_parser_firebase.json

# n8n scripts
scripts/firebase_run_parser.py
scripts/firebase_get_unsent.py
scripts/firebase_mark_sent.py

# Dependencies
requirements_firebase.txt

# Setup guide
FIREBASE_SETUP.md
```

---

## 📝 Пошаговая миграция SQLite → Firebase

### Шаг 1: Настройте Firebase

Следуйте инструкции в [FIREBASE_SETUP.md](FIREBASE_SETUP.md):
- Создайте проект
- Скачайте credentials
- Установите зависимости

### Шаг 2: Перенесите данные (опционально)

```bash
python3 migrate_to_firebase.py
```

### Шаг 3: Обновите n8n workflow

1. Деактивируйте старый workflow (SQLite)
2. Импортируйте новый: `rental_parser_firebase.json`
3. Настройте Environment Variable: `FIREBASE_CREDENTIALS_PATH`
4. Активируйте новый workflow

### Шаг 4: Тестирование

```bash
# Тест парсинга
python3 main_firebase.py --max-pages 1

# Тест статистики
python3 main_firebase.py --stats

# Проверьте данные в Firebase Console
```

---

## 🎯 Итоговая рекомендация

### Начните с SQLite

```bash
cd rental_parser
pip install -r requirements.txt
python3 main.py --max-pages 5
```

### Переходите на Firebase когда:

- ✅ Система работает стабильно
- ✅ Нужен доступ с разных серверов
- ✅ Данные критичны (нужны бэкапы)
- ✅ Появились другие пользователи
- ✅ Нужен графический интерфейс

---

## 📚 Дополнительные ресурсы

- **SQLite Setup:** [README.md](rental_parser/README.md)
- **Firebase Setup:** [FIREBASE_SETUP.md](FIREBASE_SETUP.md)
- **n8n Simple Workflow:** [SIMPLE_WORKFLOW_GUIDE.md](SIMPLE_WORKFLOW_GUIDE.md)
- **Firebase Pricing:** [firebase.google.com/pricing](https://firebase.google.com/pricing)

---

**Выбирайте SQLite для простоты, Firebase для масштаба!** 🚀
