# Changelog

## [1.0.0] - 2026-01-10

### Добавлено
- 🤖 Интеллектуальный агент на базе Claude AI (Sonnet 4.5)
- 📊 Полная интеграция с Google Sheets (4 листа: ЗАПРОСЫ, САЙТЫ, КОМПАНИИ, ПИСЬМА)
- 🗺️ Парсер Google Maps API для поиска компаний
- 🌐 Web scraper для извлечения данных с сайтов компаний
- 📱 Telegram уведомления о статусе работы
- ✉️ Генератор персонализированных писем с помощью Claude AI
- 🔧 Скрипт автоматической настройки Google Sheets
- 🧪 Скрипт тестирования всех подключений
- 📚 Подробная документация (README, QUICKSTART)
- 🔄 Интерактивный режим работы с агентом
- 🛠️ Инструменты для автоматизации:
  - TelegramMessage - отправка уведомлений
  - QuerySheets - получение запросов
  - AgentLeadAddQuery - создание запросов
  - SiteCompanySheets - получение сайтов
  - AgentLeadAddSiteCompany - сбор сайтов из Google Maps
  - AgentLeadScrapInformationCompany - парсинг данных компаний
  - AgentLeadMailGenerate - генерация писем

### Модули
- `modules/google_sheets.py` - работа с Google Sheets API
- `modules/telegram_bot.py` - Telegram Bot интеграция
- `modules/google_maps.py` - Google Maps API парсер
- `modules/scraper.py` - веб-скрейпер для сайтов
- `config/settings.py` - конфигурация приложения
- `agent.py` - главный файл агента

### Особенности
- Автоматическое определение намерений пользователя
- Цепочка вызовов инструментов (tool chaining)
- Обработка ошибок с подробными логами
- Поддержка различных целевых ниш (недвижимость, автосервисы, стоматологии)
- Фильтрация и валидация данных
- Управление статусами обработки данных

### Системные требования
- Python 3.8+
- Anthropic API ключ
- Google Cloud Project с включёнными API
- Google Sheets доступ
- Опционально: Telegram Bot

### Зависимости
- anthropic>=0.40.0
- gspread>=6.1.2
- python-telegram-bot>=21.7
- requests>=2.32.3
- beautifulsoup4>=4.12.3
- И другие (см. requirements.txt)
