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

### 2. Система сбора данных о компаниях

**Workflows:**
- `child_workflow_02_AgentLeadAddSiteCompany_FIXED.json` - AgentLeadAddSiteCompany ✅ **ИСПОЛЬЗУЙТЕ ЭТОТ**
- `child_workflow_03_AgentLeadScrapInformationCompany_FIXED.json` - AgentLeadScrapInformationCompany ✅ **ИСПОЛЬЗУЙТЕ ЭТОТ**

**Возможности:**
- Добавление сайтов компаний через API или вручную
- Автоматический сбор информации с сайтов компаний
- AI-извлечение структурированных данных
- Хранение в Google Sheets
- Управление статусами обработки

**Статус:** ✅ Новый функционал, готов к использованию

**Документация:**
- [FILES_MAP.md](./FILES_MAP.md) - 🗺️ **НАЧНИТЕ ЗДЕСЬ** - навигация по файлам
- [COMPANY_SCRAPER_SYSTEM.md](./COMPANY_SCRAPER_SYSTEM.md) - архитектура системы
- [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md) - установка и настройка

---

## 🚀 Быстрый старт

### Для новостного workflow:

1. Импортируйте `workflow_fixed.json` в n8n
2. Замените Google Sheets ID на свой
3. Проверьте credentials (Telegram, Google Sheets, Anthropic)
4. Активируйте workflow

### Для системы сбора данных о компаниях:

1. **Сначала прочитайте:** [FILES_MAP.md](./FILES_MAP.md) - карта всех файлов проекта
2. Создайте Google таблицу (инструкция в [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md))
3. Импортируйте оба workflow (используйте версии с _FIXED):
   - `child_workflow_02_AgentLeadAddSiteCompany_FIXED.json`
   - `child_workflow_03_AgentLeadScrapInformationCompany_FIXED.json`
4. Замените Google Sheets ID во всех узлах
5. Активируйте workflows
6. Добавьте первый сайт через API или вручную

---

## 📚 Документация

| Файл | Описание |
|------|----------|
| [README.md](./README.md) | Этот файл - обзор проекта |
| [FILES_MAP.md](./FILES_MAP.md) | 🗺️ **НАЧНИТЕ ЗДЕСЬ** - навигация по всем файлам |
| [WORKFLOW_FIXES.md](./WORKFLOW_FIXES.md) | Исправления новостного workflow |
| [COMPANY_SCRAPER_SYSTEM.md](./COMPANY_SCRAPER_SYSTEM.md) | Архитектура системы сбора данных о компаниях |
| [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md) | Пошаговая установка и настройка |

---

## 🔧 Технологии

- **n8n** - платформа автоматизации
- **Google Sheets** - база данных
- **Anthropic Claude Sonnet 4.5** - AI для анализа
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

### Система сбора данных о компаниях

**Workflow 1: AgentLeadAddSiteCompany**
```
📥 Webhook (POST /add-company-site)
  ↓
✅ Валидация URL
  ↓
🔍 Проверка дубликатов
  ↓
💾 Добавление в Google Sheets (status=0)
  ↓
📤 Ответ API
```

**Workflow 2: AgentLeadScrapInformationCompany**
```
⏰ Таймер (6 часов)
  ↓
📋 Получить сайты (status=0)
  ↓
📝 Обновить status → 1
  ↓
🌐 Загрузить HTML
  ↓
🧹 Очистить HTML
  ↓
🤖 AI извлечение данных
  ↓
💾 Сохранить в CompanyInformation
  ↓
✅ Обновить status → 2 (успех) или 3 (ошибка)
```

---

## 🎯 Примеры использования

### Добавление сайта компании через API:

```bash
curl -X POST https://your-n8n-instance.com/webhook/add-company-site \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://amur-company.ru",
    "company_name": "Амурская компания",
    "source": "api"
  }'
```

**Ответ:**
```json
{
  "success": true,
  "message": "Site added successfully",
  "url": "https://amur-company.ru",
  "company_name": "Амурская компания"
}
```

### Массовый импорт сайтов:

1. Подготовьте CSV:
```csv
URL,Company Name,Source
https://company1.ru,Компания 1,import
https://company2.ru,Компания 2,import
https://company3.ru,Компания 3,import
```

2. Импортируйте в Google Sheets (лист CompanySites)
3. Установите Status = 0 для всех строк
4. Workflow автоматически обработает их

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
