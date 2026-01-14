# Инструкция по установке и настройке системы сбора данных о компаниях

## 📋 Подготовка Google Sheets

### Шаг 1: Создание Google Таблицы

1. Откройте [Google Sheets](https://sheets.google.com)
2. Создайте новую таблицу
3. Назовите её: **"Lead Company Database"**

### Шаг 2: Создание листа "CompanySites"

1. Переименуйте "Лист1" → "CompanySites"
2. Добавьте заголовки в первую строку (A1:G1):

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| **ID** | **URL** | **Company Name** | **Status** | **Created At** | **Updated At** | **Source** |

3. **Форматирование:**
   - Выделите первую строку
   - Установите жирный шрифт
   - Залейте фон серым цветом
   - Закрепите первую строку (Вид → Закрепить → 1 строку)

4. **Настройка столбцов:**
   - Столбец A (ID): Автоматическая нумерация
     - В ячейку A2 введите: `=ROW()-1`
     - Скопируйте формулу вниз на 1000 строк
   - Столбец B (URL): Ширина 300px
   - Столбец C (Company Name): Ширина 200px
   - Столбец D (Status): Ширина 80px, выравнивание по центру
   - Остальные: Ширина 150px

### Шаг 3: Создание листа "CompanyInformation"

1. Добавьте новый лист (кнопка + внизу)
2. Назовите его "CompanyInformation"
3. Добавьте заголовки в первую строку (A1:L1):

| A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **ID** | **Site ID** | **Company Name** | **INN** | **Address** | **Phone** | **Email** | **Description** | **Products/Services** | **Contact Person** | **Scraped At** | **Raw Data** |

4. **Форматирование:**
   - Выделите первую строку
   - Установите жирный шрифт
   - Залейте фон зелёным цветом
   - Закрепите первую строку

5. **Настройка столбцов:**
   - Столбец A (ID): Автоматическая нумерация (формула `=ROW()-1`)
   - Столбцы B-L: Автоширина или 150-200px

### Шаг 4: Получение ID таблицы

1. Скопируйте URL вашей таблицы из адресной строки браузера
2. URL выглядит так: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit`
3. Скопируйте часть между `/d/` и `/edit` - это ваш **SHEET_ID**
4. Сохраните его для следующих шагов

---

## 🔧 Установка workflows в n8n

### Шаг 1: Импорт workflow "AgentLeadAddSiteCompany"

1. Откройте n8n
2. Нажмите **"Import from File"**
3. Выберите файл `workflow_add_company_site.json`
4. Workflow будет импортирован

### Шаг 2: Настройка Google Sheets ID в "AgentLeadAddSiteCompany"

1. Откройте импортированный workflow
2. Найдите узлы с Google Sheets (их 2):
   - **🔍 Проверка дубликатов**
   - **💾 Добавить в Google Sheets**
3. В каждом узле:
   - Откройте параметр `documentId`
   - Замените `YOUR_GOOGLE_SHEET_ID_HERE` на ваш реальный SHEET_ID
4. Сохраните workflow (Ctrl+S)

### Шаг 3: Активация webhook

1. В узле **"📥 Webhook Trigger"** скопируйте URL
2. URL будет вида: `https://your-n8n-instance.com/webhook/add-company-site`
3. Сохраните этот URL для API запросов

### Шаг 4: Активация workflow

1. Нажмите кнопку **"Active"** в правом верхнем углу
2. Workflow теперь будет принимать запросы

---

### Шаг 5: Импорт workflow "AgentLeadScrapInformationCompany"

1. Нажмите **"Import from File"**
2. Выберите файл `workflow_scrap_company_info.json`
3. Workflow будет импортирован

### Шаг 6: Настройка Google Sheets ID в "AgentLeadScrapInformationCompany"

1. Откройте импортированный workflow
2. Найдите узлы с Google Sheets (их 5):
   - **📋 Получить сайты (статус=0)**
   - **📝 Статус → 1 (обработка)**
   - **💾 Сохранить в CompanyInformation**
   - **✅ Статус → 2 (успех)**
   - **⚠️ Статус → 3 (ошибка)**
3. В каждом узле замените `YOUR_GOOGLE_SHEET_ID_HERE` на ваш SHEET_ID
4. Сохраните workflow

### Шаг 7: Проверка credentials

Убедитесь, что настроены credentials:
- ✅ **Google Sheets OAuth2** (для доступа к таблице)
- ✅ **Anthropic API** (для AI-анализа)

Если credentials не настроены:
1. Перейдите в **Settings → Credentials**
2. Добавьте **Google Sheets OAuth2 API**
3. Добавьте **Anthropic API**

### Шаг 8: Активация workflow

1. Нажмите кнопку **"Active"**
2. Workflow будет запускаться каждые 6 часов автоматически

---

## 🧪 Тестирование системы

### Тест 1: Добавление сайта через API

Выполните запрос через curl или Postman:

```bash
curl -X POST https://your-n8n-instance.com/webhook/add-company-site \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example-company.ru",
    "company_name": "Тестовая компания",
    "source": "manual"
  }'
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "message": "Site added successfully",
  "url": "https://example-company.ru",
  "company_name": "Тестовая компания"
}
```

### Тест 2: Проверка добавления в Google Sheets

1. Откройте вашу Google Таблицу
2. Перейдите на лист **"CompanySites"**
3. Убедитесь, что появилась новая строка с данными:
   - URL: `https://example-company.ru`
   - Company Name: `Тестовая компания`
   - Status: `0`
   - Source: `manual`

### Тест 3: Ручной запуск сбора данных

1. Откройте workflow **"AgentLeadScrapInformationCompany"**
2. Нажмите **"Execute Workflow"**
3. Дождитесь завершения выполнения
4. Проверьте результаты:
   - Лист **"CompanySites"**: статус сайта изменился на `2` (успех) или `3` (ошибка)
   - Лист **"CompanyInformation"**: появилась новая строка с данными компании

---

## 🔄 Рабочий процесс

### Как добавлять сайты:

**Вариант 1: Через API (рекомендуется)**
```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://company-site.ru",
    "company_name": "Название компании",
    "source": "api"
  }'
```

**Вариант 2: Вручную через Google Sheets**
1. Откройте лист "CompanySites"
2. Добавьте новую строку:
   - URL: `https://company-site.ru`
   - Company Name: `Название компании`
   - Status: `0`
   - Created At: `2026-01-14T12:00:00.000Z`
   - Updated At: `2026-01-14T12:00:00.000Z`
   - Source: `manual`

**Вариант 3: Массовый импорт**
1. Подготовьте CSV файл с колонками: URL, Company Name, Source
2. Импортируйте в Google Sheets (Файл → Импорт)
3. Установите Status = 0 для всех строк

### Статусы сайтов:

| Статус | Значение | Описание |
|--------|----------|----------|
| **0** | Новый | Сайт добавлен, ожидает обработки |
| **1** | В обработке | Workflow начал сбор данных |
| **2** | Обработан | Данные успешно собраны |
| **3** | Ошибка | Не удалось загрузить сайт или извлечь данные |

### Повторная обработка:

Если нужно повторно собрать данные с сайта:
1. Откройте лист "CompanySites"
2. Найдите нужный сайт
3. Измените Status на `0`
4. При следующем запуске workflow сайт будет обработан снова

---

## 📊 Мониторинг и статистика

### Проверка статистики в Google Sheets:

**Общее количество сайтов:**
```
=COUNTA(CompanySites!B:B)-1
```

**Сайты в очереди (Status=0):**
```
=COUNTIF(CompanySites!D:D,0)
```

**Обработанные сайты (Status=2):**
```
=COUNTIF(CompanySites!D:D,2)
```

**Сайты с ошибками (Status=3):**
```
=COUNTIF(CompanySites!D:D,3)
```

**Процент успеха:**
```
=COUNTIF(CompanySites!D:D,2)/COUNTA(CompanySites!B:B)*100&"%"
```

---

## ⚠️ Решение проблем

### Проблема: "Workflow does not exist"

**Решение:**
1. Проверьте, что workflow импортирован в n8n
2. Убедитесь, что имя workflow точно совпадает:
   - `AgentLeadAddSiteCompany`
   - `AgentLeadScrapInformationCompany`
3. Активируйте workflow (кнопка "Active")

### Проблема: "The workflow did not return a response"

**Решение:**
1. Увеличьте timeout в узле **HTTP Request** до 60 секунд
2. Проверьте доступность сайта в браузере
3. Проверьте логи выполнения в n8n (вкладка "Executions")
4. Убедитесь, что AI модель (Claude) работает корректно

### Проблема: "Нет сайтов со статусом 0"

**Решение:**
1. Добавьте новые сайты через API или вручную
2. Проверьте, что столбец Status содержит число `0`, а не текст `"0"`
3. Сбросьте статус обработанных сайтов на 0 для повторной обработки

### Проблема: "Дубликаты в базе"

**Решение:**
1. Система автоматически проверяет дубликаты по URL
2. Если сайт уже существует, вы получите ответ:
```json
{
  "success": false,
  "message": "Site already exists in database"
}
```

### Проблема: "AI не извлекает данные корректно"

**Решение:**
1. Проверьте, что узел **🔧 JSON Parser** подключен к AI Agent
2. Убедитесь, что модель Claude Sonnet 4.5 доступна
3. Проверьте промпт в узле **🤖 AI Извлечение данных**
4. Увеличьте лимит текста в узле **🧹 Очистить HTML** (сейчас 15000 символов)

---

## 🚀 Расширенные возможности

### Интеграция с другими системами:

1. **CRM (AmoCRM, Bitrix24)**
   - Добавьте узел для отправки данных в CRM
   - Подключите webhook после узла "💾 Сохранить в CompanyInformation"

2. **Email рассылки**
   - Добавьте узел "Send Email" для уведомлений
   - Настройте отправку при статусе = 2

3. **Telegram уведомления**
   - Добавьте узел Telegram
   - Отправляйте статистику каждый день

### Масштабирование:

- **Для обработки > 100 сайтов в день:**
  - Уменьшите интервал запуска до 3 часов
  - Увеличьте лимит пакета с 20 до 50
  - Добавьте очередь (Queue) для распределённой обработки

- **Для сбора дополнительных данных:**
  - Модифицируйте промпт AI
  - Добавьте новые столбцы в "CompanyInformation"
  - Обновите JSON Schema в узле "🔧 JSON Parser"

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи выполнения в n8n (Executions)
2. Проверьте структуру Google Sheets
3. Убедитесь, что все credentials настроены
4. Проверьте доступность API Claude

Документация:
- [COMPANY_SCRAPER_SYSTEM.md](./COMPANY_SCRAPER_SYSTEM.md) - архитектура системы
- [WORKFLOW_FIXES.md](./WORKFLOW_FIXES.md) - исправления для новостного workflow
