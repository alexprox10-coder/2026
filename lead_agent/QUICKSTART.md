# 🚀 Быстрый Старт

## За 5 минут до первого запуска

### Шаг 1: Установка (1 минута)

```bash
cd lead_agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 2: Настройка .env (2 минуты)

```bash
cp .env.example .env
nano .env  # или используйте любой текстовый редактор
```

Минимальная конфигурация:

```env
ANTHROPIC_API_KEY=sk-ant-xxxx  # Получить на console.anthropic.com
GOOGLE_MAPS_API_KEY=AIzaxxxx   # Получить в Google Cloud Console
GOOGLE_SHEETS_ID=17Ll6-lvbJTGix5Y6uwh2Glr8CNT6FktnicRsuOWdhqA
```

### Шаг 3: Google Credentials (2 минуты)

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте Service Account
3. Скачайте JSON ключ
4. Сохраните как `config/google_credentials.json`
5. Откройте вашу [Google таблицу](https://docs.google.com/spreadsheets/d/17Ll6-lvbJTGix5Y6uwh2Glr8CNT6FktnicRsuOWdhqA)
6. Нажмите "Share" и добавьте email из JSON файла (поле "client_email")

### Шаг 4: Создание листов в Google Sheets

Откройте вашу таблицу и создайте 4 листа с точными названиями:

1. **ЗАПРОСЫ** - для поисковых запросов
2. **САЙТЫ** - для списка компаний
3. **КОМПАНИИ** - для детальной информации
4. **ПИСЬМА** - для черновиков писем

### Шаг 5: Запуск!

```bash
python agent.py
```

## Первые команды

После запуска попробуйте:

```
Привет
```
Агент расскажет о своих возможностях.

```
Собери автосервисы по Москве
```
Агент создаст запросы, найдёт компании и соберёт данные.

```
Покажи невыполненные запросы
```
Посмотрите список запросов в работе.

```
Собери информацию с сайтов
```
Начнётся парсинг данных с сайтов компаний.

```
Создай письма для компаний
```
Claude сгенерирует персонализированные письма.

## Опционально: Telegram уведомления

Если хотите получать уведомления в Telegram:

1. Найдите [@BotFather](https://t.me/botfather)
2. Создайте бота: `/newbot`
3. Получите токен
4. Узнайте Chat ID через [@userinfobot](https://t.me/userinfobot)
5. Добавьте в `.env`:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## Устранение проблем

### "ANTHROPIC_API_KEY не настроен"
Проверьте `.env` файл, убедитесь что ключ скопирован полностью.

### "Ошибка подключения к Google Sheets"
- Проверьте `google_credentials.json` в папке `config/`
- Убедитесь что service account email добавлен в таблицу с правами редактора
- Проверьте правильность GOOGLE_SHEETS_ID

### "Google Maps API вернул ошибку"
- Проверьте что API ключ активен
- Включите Places API и Geocoding API в Google Cloud Console
- Проверьте квоты использования API

### Агент не находит модули
```bash
# Убедитесь что вы в правильной директории и виртуальное окружение активно
cd lead_agent
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## Следующие шаги

1. Изучите `README.md` для подробной документации
2. Настройте дополнительные параметры в `config/settings.py`
3. Попробуйте различные команды и запросы
4. Проверьте данные в Google Sheets

## Полезные ссылки

- [Anthropic Console](https://console.anthropic.com/) - для получения API ключа
- [Google Cloud Console](https://console.cloud.google.com/) - для настройки API
- [Ваша Google Таблица](https://docs.google.com/spreadsheets/d/17Ll6-lvbJTGix5Y6uwh2Glr8CNT6FktnicRsuOWdhqA)

---

Если что-то не работает - проверьте логи в `logs/agent.log`
