# n8n Workflows для Амурской области

Коллекция n8n workflows для автоматизации сбора новостей и информации о компаниях Амурской области.

## 📦 Состав проекта

### 1. Система агрегации новостей

**Workflow:** `workflow_fixed.json` - Амурские новости → Telegram

**Возможности:**
- Сбор новостей из 4 RSS источников
- Интеллектуальная фильтрация по ключевым словам
- AI-анализ и выбор топ-5 новостей
- Автоматическая отправка в Telegram канал
- Архивирование в Google Sheets

**Статус:** ✅ Исправлен и готов к использованию

**Документация:** [WORKFLOW_FIXES.md](./WORKFLOW_FIXES.md)

---

### 2. Система сбора лидов и генерации предложений 🆕

**Workflows (все работают ПО ЗАПРОСУ!):**
- `child_workflow_01_AgentLeadAddQuery_FIXED.json` - Автоматический поиск сайтов компаний ✅
- `child_workflow_02_AgentLeadAddSiteCompany_FIXED.json` - Ручное добавление сайтов ✅
- `child_workflow_03_AgentLeadScrapInformationCompany_FIXED_v2.json` - Сбор контактных данных ✅
- `child_workflow_04_AgentLeadMailGenerate.json` - Генерация персональных предложений ✅ **НОВЫЙ**

**Возможности:**
- 🔍 Автоматический поиск компаний через Google (SerpAPI)
- 📝 Добавление сайтов компаний через API или вручную
- 🤖 AI-сбор контактных данных **по вашему запросу** (Google Gemini - бесплатно!)
- ✉️ Генерация персональных коммерческих предложений
- 💾 Хранение всех данных в Google Sheets
- 🎯 Полный контроль: каждый этап запускается когда нужно

**Полный цикл:** Поиск компаний → Сбор контактов → Персональные предложения → Готовые черновики

**Статус:** ✅ Готова к использованию, работает на бесплатных API

**Документация:**
- [ON_DEMAND_WORKFLOW_GUIDE.md](./ON_DEMAND_WORKFLOW_GUIDE.md) - 🎯 **НАЧНИТЕ ЗДЕСЬ** - полная система по запросу
- [FILES_MAP.md](./FILES_MAP.md) - 🗺️ навигация по файлам
- [SEARCH_COMPANIES_GUIDE.md](./SEARCH_COMPANIES_GUIDE.md) - настройка автопоиска
- [COMPANY_SCRAPER_SYSTEM.md](./COMPANY_SCRAPER_SYSTEM.md) - архитектура системы
- [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md) - установка и настройка

---

## 🚀 Быстрый старт

### Для новостного workflow:

1. Импортируйте `workflow_fixed.json` в n8n
2. Замените Google Sheets ID на свой
3. Проверьте credentials (Telegram, Google Sheets, Anthropic)
4. Активируйте workflow

### Для системы сбора лидов (ПОЛНЫЙ ЦИКЛ):

1. **Сначала прочитайте:** [ON_DEMAND_WORKFLOW_GUIDE.md](./ON_DEMAND_WORKFLOW_GUIDE.md) - полная инструкция 🎯
2. Получите бесплатные API ключи:
   - Google Gemini API: https://aistudio.google.com/app/apikey
   - SerpAPI (100 запросов/месяц): https://serpapi.com
3. Создайте Google таблицу с 3 листами: CompanySites, CompanyInformation, EmailDrafts
4. Импортируйте все 4 workflows:
   - `child_workflow_01_AgentLeadAddQuery_FIXED.json` (поиск)
   - `child_workflow_02_AgentLeadAddSiteCompany_FIXED.json` (ручное добавление)
   - `child_workflow_03_AgentLeadScrapInformationCompany_FIXED_v2.json` (сбор данных)
   - `child_workflow_04_AgentLeadMailGenerate.json` (генерация предложений)
5. Замените `YOUR_GOOGLE_SHEET_ID_HERE` во всех узлах
6. Настройте ваши данные в workflow_04 (имя компании, услуги, контакты)
7. Активируйте все workflows
8. Запустите первый поиск через webhook `/add-search-query`

---

## 📚 Документация

| Файл | Описание |
|------|----------|
| [README.md](./README.md) | Этот файл - обзор проекта |
| [ON_DEMAND_WORKFLOW_GUIDE.md](./ON_DEMAND_WORKFLOW_GUIDE.md) | 🎯 **СИСТЕМА ПО ЗАПРОСУ** - полный цикл работы |
| [FILES_MAP.md](./FILES_MAP.md) | 🗺️ Навигация по всем файлам |
| [SEARCH_COMPANIES_GUIDE.md](./SEARCH_COMPANIES_GUIDE.md) | 🔍 Настройка автопоиска сайтов |
| [WORKFLOW_FIXES.md](./WORKFLOW_FIXES.md) | Исправления новостного workflow |
| [COMPANY_SCRAPER_SYSTEM.md](./COMPANY_SCRAPER_SYSTEM.md) | Архитектура системы сбора данных |
| [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md) | Пошаговая установка и настройка |
| [GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md) | Создание Google таблиц |
| [QUICK_FIX_EXISTING_TABLE.md](./QUICK_FIX_EXISTING_TABLE.md) | Адаптация существующей таблицы |

---

## 🔧 Технологии

- **n8n** - платформа автоматизации
- **Google Sheets** - база данных
- **Google Gemini API** - AI для извлечения данных (бесплатно!)
- **Anthropic Claude Sonnet 4.5** - AI для анализа новостей
- **SerpAPI** - поиск компаний в Google
- **Telegram API** - публикация новостей
- **RSS Feeds** - источники новостей

---

## 📊 Архитектура

### Новостной workflow

```
⏰ Таймер (8 часов)
  ↓
📰 RSS источники (4 ленты)
  ↓
🔗 Объединение
  ↓
✅ Проверка данных
  ↓
🔍 Фильтрация (геолокация, Китай, бизнес)
  ↓
🤖 AI Аналитик (топ-5 новостей)
  ↓
📤 Разделение постов
  ↓
📱 Telegram + 💾 Google Sheets
```

### Система сбора лидов (ВСЕ ПО ЗАПРОСУ!)

**Workflow 1: AgentLeadAddQuery (Поиск компаний) 🆕**
```
📥 Webhook (POST /add-search-query)
  ↓
📝 Подготовить поисковые запросы
  ↓
🔍 Google Search (SerpAPI)
  ↓
🌐 Извлечь сайты, фильтровать (соцсети, доски)
  ↓
💾 Добавление в CompanySites (status=0)
  ↓
📤 Ответ: найдено X сайтов
```

**Workflow 2: AgentLeadAddSiteCompany (Ручное добавление)**
```
📥 Webhook (POST /add-company-site)
  ↓
✅ Валидация URL
  ↓
🔍 Проверка дубликатов
  ↓
💾 Добавление в CompanySites (status=0)
  ↓
📤 Ответ API
```

**Workflow 3: AgentLeadScrapInformationCompany_v2 (Сбор данных) 🆕**
```
📥 Webhook (POST /start-scraping) - ПО ЗАПРОСУ!
  ↓
📋 Получить сайты (status=0, лимит 20)
  ↓
📝 Обновить status → 1
  ↓
🌐 Загрузить HTML
  ↓
🧹 Очистить HTML
  ↓
🤖 AI извлечение данных (Google Gemini)
  ↓
💾 Сохранить в CompanyInformation
  ↓
✅ Обновить status → 2 (успех) или 3 (ошибка)
```

**Workflow 4: AgentLeadMailGenerate (Генерация предложений) 🆕**
```
📥 Webhook (POST /generate-proposals) - ПО ЗАПРОСУ!
  ↓
📋 Получить компании из CompanyInformation
  ↓
📧 Фильтр: только с email
  ↓
🤖 AI генерирует для каждой компании:
   ├─ Персональную тему письма
   └─ Уникальный текст предложения
  ↓
💾 Сохранить черновики в EmailDrafts
  ↓
📤 Ответ: создано X черновиков
```

---

## 🎯 Примеры использования

### 1. Поиск компаний в Google:

```bash
curl -X POST https://your-n8n.com/webhook/add-search-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "агентство недвижимости",
    "city": "Благовещенск",
    "region": "Амурская область"
  }'
```

**Ответ:**
```json
{
  "success": true,
  "websites_found": 15,
  "message": "Search completed"
}
```

### 2. Ручное добавление сайта:

```bash
curl -X POST https://your-n8n.com/webhook/add-company-site \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://amur-company.ru",
    "company_name": "Амурская компания",
    "source": "manual"
  }'
```

**Ответ:**
```json
{
  "success": true,
  "message": "Site added successfully",
  "url": "https://amur-company.ru"
}
```

### 3. Запуск сбора данных:

```bash
curl -X POST https://your-n8n.com/webhook/start-scraping \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Ответ:**
```json
{
  "success": true,
  "companies_processed": 15,
  "message": "Scraping completed"
}
```

### 4. Генерация персональных предложений:

```bash
curl -X POST https://your-n8n.com/webhook/generate-proposals \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Ответ:**
```json
{
  "success": true,
  "emails_generated": 12,
  "message": "Proposals generated successfully"
}
```

---

## 📈 Статусы обработки

| Статус | Название | Описание |
|--------|----------|----------|
| **0** | Новый | Сайт добавлен, ожидает обработки |
| **1** | В обработке | Workflow начал сбор данных |
| **2** | Обработан | Данные успешно собраны и сохранены |
| **3** | Ошибка | Не удалось загрузить сайт или извлечь данные |

---

## ⚙️ Настройка

### Необходимые credentials в n8n:

- ✅ **Telegram API** - для отправки новостей
- ✅ **Google Sheets OAuth2** - для работы с таблицами
- ✅ **Anthropic API** - для AI-анализа

### Переменные окружения:

Замените в workflows:
- `YOUR_GOOGLE_SHEET_ID_HERE` → ID вашей Google таблицы
- `@blagoveshchensk2026_News` → ваш Telegram канал (опционально)

---

## 🐛 Решение проблем

### "Workflow does not exist"
→ Проверьте импорт и имя workflow в n8n

### "The workflow did not return a response"
→ Увеличьте timeout, проверьте логи

### "Нет сайтов со статусом 0"
→ Добавьте сайты через API или вручную

**Подробнее:** [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md#-решение-проблем)

---

## 🔐 Безопасность

- Все API ключи хранятся в n8n credentials (зашифрованы)
- Webhook защищены уникальными ID
- Валидация всех входящих URL
- Ограничение пакетной обработки (20 сайтов)

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте документацию
2. Проверьте логи в n8n (Executions)
3. Убедитесь в правильности настройки credentials
4. Проверьте структуру Google Sheets

---

## 📜 Лицензия

MIT License - свободное использование и модификация

---

## 🤝 Вклад

Предложения и улучшения приветствуются!

---

## 📅 История версий

### v2.0 (2026-01-14) 🆕
- ✅ **ПОЛНЫЙ ЦИКЛ:** поиск → сбор данных → персональные предложения
- ✅ Автоматический поиск компаний через Google (SerpAPI)
- ✅ Генерация персональных коммерческих предложений с AI
- ✅ Система работает **ПО ЗАПРОСУ** (webhook triggers)
- ✅ Переход на Google Gemini API (бесплатная альтернатива Claude)
- ✅ Добавлен лист EmailDrafts для черновиков писем
- ✅ Обновлена вся документация с примерами API запросов

### v1.0 (2026-01-14)
- ✅ Исправлен workflow агрегации новостей
- ✅ Добавлена система сбора данных о компаниях
- ✅ Полная документация и инструкции

---

## 🎓 Обучающие материалы

- [n8n Documentation](https://docs.n8n.io/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Anthropic Claude API](https://docs.anthropic.com/)

---

**Разработано для Амурской области 🇷🇺**
