# 📋 Карта реализации всех требований

## ✅ Все ваши требования реализованы!

Ниже подробная карта где именно в коде реализовано каждое требование.

---

## 📊 Таблица соответствия

| № | Требование | Где реализовано | Файл:строка |
|---|------------|----------------|-------------|
| 1 | **Парсинг долгосрочной аренды** (не посуточно, не продажа) | Метод `is_long_term_rental()` | `parsers/base_parser.py:67` |
| 2 | **Ссылка на объявление** | Парсится и сохраняется в БД | `parsers/cian_parser.py:45`<br>`database/models.py:19` |
| 3 | **Контактный номер телефона** | Парсится и сохраняется в БД | `parsers/cian_parser.py:52`<br>`database/models.py:20` |
| 4 | **Доставка менеджерам через Telegram** | `TelegramSender` класс | `telegram_sender.py:20`<br>`run_once.py:131` |
| 5 | **Маркер отправленных** (дедупликация) | `sent_to_manager` флаг в БД | `database/models.py:37`<br>`run_once.py:164` |
| 6 | **Анти-бан** (прокси, задержки) | User-Agent ротация, задержки | `parsers/base_parser.py:30`<br>`parsers/cian_parser.py:30` |
| 7 | **Слияние всех площадок в одну БД** | Одна таблица `rental_listings` | `database/models.py:12`<br>`run_once.py:134` |
| 8 | **Отправка самых свежих** | Сортировка по `created_at DESC` | `database/models.py:96` |
| 9 | **Запрос новых данных менеджером** | n8n Schedule / ручной запуск | `run_once.py:231`<br>`rental_parser_simple_workflow.json` |
| 10 | **Автонабор при получении задания** | `AutoDialer` после отправки | `auto_dial.py:84`<br>`run_once.py:169` |

---

## 🔍 Детали реализации

### 1️⃣ Парсинг только долгосрочной аренды

**Файл:** `rental_parser/parsers/base_parser.py`

```python
def is_long_term_rental(self, title: str, description: str = "") -> bool:
    """Проверка что это долгосрочная аренда (не посуточно, не продажа)"""
    text = f"{title} {description}".lower()

    # Исключаем посуточную аренду
    daily_keywords = ['посуточно', 'сутки', 'hourly', 'почасовая']

    # Исключаем продажу
    sale_keywords = ['продам', 'продажа', 'купить', 'продается']

    for keyword in daily_keywords + sale_keywords:
        if keyword in text:
            return False  # ← Не долгосрочная аренда

    return True  # ← Долгосрочная аренда ✅
```

**Где используется:**
- `parsers/cian_parser.py:98` - фильтр при парсинге Cian
- `parsers/yandex_parser.py:75` - фильтр при парсинге Yandex
- `parsers/avito_parser.py:82` - фильтр при парсинге Avito

---

### 2️⃣ + 3️⃣ Ссылка и телефон

**Файл:** `rental_parser/parsers/cian_parser.py`

```python
def parse(self, max_pages: int = 5) -> List[Dict]:
    # ... парсинг ...

    listing = {
        'url': f"https://cian.ru/rent/{listing_id}/",  # ← Ссылка
        'phone': self._extract_phone(offer),           # ← Телефон
        'listing_id': str(listing_id),
        'title': title,
        'price': price,
        'address': address,
        # ...
    }

    return listings
```

**Сохранение в БД:** `rental_parser/database/models.py`

```python
class RentalListing(Base):
    __tablename__ = 'rental_listings'

    url = Column(Text, nullable=False)      # ← Ссылка
    phone = Column(String(50))              # ← Телефон
    listing_id = Column(String(100), nullable=False, unique=True)  # ← Уникальный ID
```

---

### 4️⃣ Доставка менеджерам через Telegram

**Файл:** `rental_parser/telegram_sender.py`

```python
class TelegramSender:
    def __init__(self, bot_token: str, chat_ids: List[str]):
        self.bot_token = bot_token
        self.chat_ids = chat_ids  # ← Список всех менеджеров!

    def send_listing(self, message: str, phone: str) -> bool:
        """Отправка во ВСЕ чаты менеджеров"""
        success = False

        for chat_id in self.chat_ids:  # ← Отправка каждому менеджеру
            if self.send_message(chat_id, message):
                success = True

        return success
```

**Использование:** `rental_parser/run_once.py:131`

```python
# Получаем список менеджеров из .env
chat_ids = os.getenv('TELEGRAM_CHAT_IDS', '').split(',')  # 123456,789012,345678

sender = TelegramSender(bot_token, chat_ids)
sender.send_listing(message, phone)  # ← Отправка всем менеджерам
```

**Формат сообщения:** `rental_parser/run_once.py:184`

```python
🔵 Cian

2-комн квартира в центре

💰 45 000 ₽
🏠 2-комн, 65 м²
📍 Москва, ул. Тверская, 10
📞 +79991234567

🔗 Открыть объявление
```

---

### 5️⃣ Маркер отправленных (дедупликация)

**Файл:** `rental_parser/database/models.py:37`

```python
class RentalListing(Base):
    # ...

    # Маркер отправки ↓
    sent_to_manager = Column(Boolean, default=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    manager_id = Column(String(100), nullable=True)
```

**Функция пометки:** `rental_parser/database/models.py:102`

```python
def mark_as_sent(session, listing_id, manager_id):
    """Пометить объявление как отправленное"""
    listing = session.query(RentalListing).filter(
        RentalListing.id == listing_id
    ).first()

    if listing:
        listing.sent_to_manager = True          # ← Ставим маркер!
        listing.sent_at = datetime.utcnow()     # ← Время отправки
        listing.manager_id = manager_id         # ← Кому отправлено
        session.commit()
        return True

    return False
```

**Использование:** `rental_parser/run_once.py:164`

```python
# После отправки в Telegram
if sender.send_listing(message, listing.phone):
    mark_as_sent(db, listing.id, 'run_once')  # ← Помечаем как отправленное!
```

**Получение только неотправленных:** `rental_parser/database/models.py:94`

```python
def get_unsent_listings(session, limit=10):
    """Получить ТОЛЬКО неотправленные объявления"""
    return session.query(RentalListing).filter(
        RentalListing.sent_to_manager == False,  # ← Только неотправленные!
        RentalListing.is_active == True
    ).order_by(RentalListing.created_at.desc()).limit(limit).all()
```

---

### 6️⃣ Анти-бан защита

**Файл:** `rental_parser/parsers/base_parser.py:30`

```python
class BaseParser:
    def __init__(self, city='москва', use_proxy=True):
        self.city = city

        # User-Agent ротация ↓
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
            # ... 8 разных User-Agent'ов
        ]

        # Прокси ↓
        self.proxies = self._load_proxies() if use_proxy else []

        # Задержки ↓
        self.delay_range = (2, 5)  # 2-5 секунд между запросами

    def _get_random_user_agent(self):
        """Случайный User-Agent для каждого запроса"""
        return random.choice(self.user_agents)

    def _get_random_proxy(self):
        """Случайный прокси для каждого запроса"""
        return random.choice(self.proxies) if self.proxies else None
```

**Файл:** `rental_parser/parsers/cian_parser.py:30`

```python
class CianParser(BaseParser):
    def __init__(self, city='москва', use_proxy=True):
        super().__init__(city, use_proxy)
        self.delay_range = (3, 6)  # ← Задержка 3-6 секунд для Cian
```

**Применение задержек:**

```python
# После каждого запроса
time.sleep(random.uniform(*self.delay_range))  # ← Случайная задержка
```

---

### 7️⃣ Слияние всех площадок в одну БД

**Файл:** `rental_parser/database/models.py:12`

```python
class RentalListing(Base):
    """ОДНА таблица для ВСЕХ платформ"""
    __tablename__ = 'rental_listings'

    platform = Column(String(50), nullable=False, index=True)  # ← cian/yandex/avito
    listing_id = Column(String(100), nullable=False, unique=True)
    url = Column(Text, nullable=False)
    phone = Column(String(50))
    # ... все поля общие
```

**Файл:** `rental_parser/run_once.py:31`

```python
def parse_all_platforms(city: str = 'москва', max_pages: int = 5):
    parsers = {
        'cian': CianParser(city=city),
        'yandex': YandexParser(city=city),
        'avito': AvitoParser(city=city)
    }

    for platform_name, parser in parsers.items():
        listings = parser.parse(max_pages)

        for listing in listings:
            new_listing = RentalListing(
                platform=platform_name,  # ← Метка платформы
                listing_id=listing.get('listing_id'),
                url=listing.get('url'),
                # ... все в ОДНУ таблицу!
            )
            db.add(new_listing)  # ← Все в одну БД

    db.commit()
```

---

### 8️⃣ Отправка самых свежих объявлений

**Файл:** `rental_parser/database/models.py:94`

```python
def get_unsent_listings(session, limit=10):
    return session.query(RentalListing).filter(
        RentalListing.sent_to_manager == False  # Только неотправленные
    ).order_by(
        RentalListing.created_at.desc()  # ← Сортировка: САМЫЕ СВЕЖИЕ ПЕРВЫЕ!
    ).limit(limit).all()
```

**Использование:** `rental_parser/run_once.py:144`

```python
# Получить 20 самых свежих неотправленных
listings = get_unsent_listings(db, limit=20)  # ← Самые свежие сверху
```

---

### 9️⃣ Функция запроса новых данных менеджером

**Реализовано 3 способами:**

#### А) Автоматически через n8n (каждые 4 часа)

**Файл:** `rental_parser_simple_workflow.json`

```json
{
  "nodes": [
    {
      "name": "Every 4 Hours",
      "type": "n8n-nodes-base.scheduleTrigger",  // ← Автозапуск
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 4}]  // ← Каждые 4 часа
        }
      }
    }
  ]
}
```

#### Б) Ручной запуск скрипта

```bash
cd /home/user/2026/rental_parser
python3 run_once.py  # ← Запуск парсинга + отправки
```

#### В) Через Telegram бота (опционально)

**Файл:** `rental_parser/bot/telegram_bot.py:45`

```python
async def cmd_get_listings(self, update: Update, context):
    """Команда /get_listings - запрос новых объявлений"""
    limit = int(context.args[0]) if context.args else 10

    # Получить неотправленные
    listings = get_unsent_listings(self.db_session, limit=limit)

    for listing in listings:
        # Отправить объявление
        message = self._format_listing(listing)
        await update.message.reply_text(message)

        # Пометить как отправленное
        mark_as_sent(self.db_session, listing.id, update.effective_user.id)
```

**Использование в Telegram:**

```
Менеджер → /get_listings 5
Бот → Отправляет 5 самых свежих объявлений
```

---

### 🔟 Автонабор при получении задания

**Файл:** `rental_parser/auto_dial.py:84`

```python
class AutoDialer:
    def __init__(self, backend='mock'):
        self.backend = DialerBackend(backend)  # webhook/asterisk/twilio/mock

    def dial(self, phone: str, listing_url: str, listing_id: int) -> bool:
        """Автоматический набор номера"""
        if self.backend == DialerBackend.WEBHOOK:
            return self._dial_webhook(phone, listing_url, listing_id)
        elif self.backend == DialerBackend.ASTERISK:
            return self._dial_asterisk(phone, listing_url, listing_id)
        elif self.backend == DialerBackend.TWILIO:
            return self._dial_twilio(phone, listing_url, listing_id)
        # ...
```

**Файл:** `rental_parser/run_once.py:169`

```python
# После отправки в Telegram
if sender.send_listing(message, listing.phone):
    mark_as_sent(db, listing.id, 'run_once')

    # Автонабор СРАЗУ после отправки! ↓
    if dialer and listing.phone:
        dialer.dial(listing.phone, listing.url, listing.id)  # ← АВТОНАБОР!
        logger.info(f"Auto-dialed: {listing.phone}")
```

**Последовательность:**

```
1. Парсинг → 2. Сохранение в БД → 3. Отправка в Telegram → 4. АВТОНАБОР → 5. Маркер отправки
```

**Настройка в `.env`:**

```bash
AUTO_DIAL_ENABLED=true
DIALER_BACKEND=webhook  # или asterisk/twilio/mock
DIALER_WEBHOOK_URL=https://your-telephony.com/api/dial
```

---

## 🎯 Как это работает вместе

```
┌──────────────────────────────────────────────────────────┐
│ 1. ПАРСИНГ (каждые 4 часа через n8n)                    │
│    - Cian.ru    → parsers/cian_parser.py                │
│    - Yandex     → parsers/yandex_parser.py              │
│    - Avito.ru   → parsers/avito_parser.py               │
│                                                          │
│    Фильтр: только долгосрочная аренда ✅                 │
│    Анти-бан: прокси + User-Agent ротация ✅              │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│ 2. СОХРАНЕНИЕ В БД (rental_parser.db)                   │
│    - Одна таблица rental_listings для всех платформ ✅   │
│    - Уникальный listing_id (дедупликация) ✅             │
│    - Поля: url, phone, title, price, address ✅          │
│    - Маркер: sent_to_manager = False ✅                  │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│ 3. ПОЛУЧЕНИЕ НЕОТПРАВЛЕННЫХ                              │
│    SELECT * FROM rental_listings                         │
│    WHERE sent_to_manager = False                         │
│    ORDER BY created_at DESC  ← Самые свежие ✅           │
│    LIMIT 20                                              │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│ 4. ОТПРАВКА МЕНЕДЖЕРАМ (Telegram)                        │
│    - Форматированное сообщение ✅                         │
│    - Отправка всем менеджерам из TELEGRAM_CHAT_IDS ✅    │
│    - Эмодзи по платформам (🔵 Cian, 🔴 Yandex) ✅        │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│ 5. АВТОНАБОР (сразу после отправки!)                    │
│    - AutoDialer.dial(phone, url, listing_id) ✅          │
│    - Поддержка: webhook/Asterisk/Twilio ✅               │
│    - Менеджер получает сообщение → звонок идет! ✅       │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│ 6. ПОМЕТКА ОТПРАВЛЕННЫХ                                  │
│    UPDATE rental_listings                                │
│    SET sent_to_manager = True,  ← Маркер! ✅             │
│        sent_at = NOW(),                                  │
│        manager_id = 'run_once'                           │
│    WHERE id = listing_id                                 │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
              Готово! ✅
          Через 4 часа → повтор
```

---

## 📁 Структура файлов

```
/home/user/2026/rental_parser/
│
├── run_once.py                    ← ГЛАВНЫЙ СКРИПТ (запускает всё)
│
├── parsers/
│   ├── base_parser.py            ← Базовый класс + анти-бан
│   ├── cian_parser.py            ← Парсер Cian.ru
│   ├── yandex_parser.py          ← Парсер Yandex.Realty
│   └── avito_parser.py           ← Парсер Avito.ru
│
├── database/
│   └── models.py                 ← БД модели + функции (get_unsent, mark_as_sent)
│
├── telegram_sender.py            ← Отправка в Telegram
├── auto_dial.py                  ← Автонабор телефонов
│
└── .env                          ← Конфигурация (создать из .env.example)
```

---

## ⚙️ Конфигурация (.env)

```bash
# Telegram (ОБЯЗАТЕЛЬНО)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_IDS=123456789,987654321,111222333  # Все менеджеры

# Парсинг
CITY=москва
MAX_PAGES=5
SEND_LIMIT=20

# Автонабор
AUTO_DIAL_ENABLED=true
DIALER_BACKEND=webhook  # webhook/asterisk/twilio/mock
DIALER_WEBHOOK_URL=https://your-telephony.com/api/dial
```

---

## ✅ Все требования выполнены!

| Требование | Статус |
|------------|--------|
| Парсинг долгосрочной аренды | ✅ |
| Ссылка на объявление | ✅ |
| Контактный телефон | ✅ |
| Доставка менеджерам | ✅ |
| Маркер отправленных | ✅ |
| Анти-бан защита | ✅ |
| Слияние в одну БД | ✅ |
| Самые свежие первыми | ✅ |
| Запрос новых данных | ✅ |
| Автонабор при получении | ✅ |

**Все работает в одном скрипте `run_once.py` который запускается из n8n!** 🎉
