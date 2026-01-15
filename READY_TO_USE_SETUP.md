# 🚀 ГОТОВАЯ СИСТЕМА - Быстрая Установка

## Это самая простая инструкция для запуска системы!

---

## 📋 ШАГ 1: Создать Google Таблицу (5 минут)

### 1.1 Создать новую таблицу

1. Откройте: https://sheets.google.com
2. Нажмите **"+"** (Создать пустую таблицу)
3. Назовите: `Сбор Лидов 2026`

### 1.2 Импортировать 3 листа

**Лист 1: CompanySites**
1. В нижней части таблицы нажмите **"+"** → переименуйте в `CompanySites`
2. Нажмите **Файл → Импорт**
3. Выберите `READY_CompanySites.csv` из проекта
4. Настройки импорта:
   - Место импорта: **Заменить текущий лист**
   - Разделитель: **Автоопределение**
5. Нажмите **Импортировать**

**Лист 2: CompanyInformation**
1. Создайте новый лист **"+"** → переименуйте в `CompanyInformation`
2. **Файл → Импорт** → выберите `READY_CompanyInformation.csv`
3. Место импорта: **Заменить текущий лист**
4. Нажмите **Импортировать**

**Лист 3: EmailDrafts**
1. Создайте новый лист **"+"** → переименуйте в `EmailDrafts`
2. **Файл → Импорт** → выберите `READY_EmailDrafts.csv`
3. Место импорта: **Заменить текущий лист**
4. Нажмите **Импортировать**

### 1.3 Получить ID таблицы

Откройте таблицу → в адресной строке скопируйте ID:
```
https://docs.google.com/spreadsheets/d/ВАШ_ID_ЗДЕСЬ/edit
                                        ^^^^^^^^^
                                     Скопируйте это!
```

**Сохраните этот ID!** Он понадобится в workflow.

---

## 🔑 ШАГ 2: Получить API ключи (10 минут)

### 2.1 Google Custom Search API (БЕСПЛАТНО - 100 запросов/день)

**API ключ:**
1. Перейдите: https://console.cloud.google.com/
2. Создайте проект: `n8n Leads`
3. Включите API: **Custom Search API**
4. Создайте **API key** → скопируйте

**Search Engine ID:**
1. Перейдите: https://programmablesearchengine.google.com/
2. Нажмите **"Добавить"**
3. Настройки:
   - Название: `Поиск компаний`
   - Сайты для поиска: **"Поиск по всему Интернету"**
4. Создать → Скопируйте **Search Engine ID** (cx)

**Сохраните:**
- API key: `AIzaSy...`
- Search Engine ID (cx): `a1b2c3...`

### 2.2 Perplexity AI API ($5 бесплатных кредитов = 5000 компаний!)

1. Перейдите: https://www.perplexity.ai/
2. Нажмите **Sign Up** → войдите через Google
3. Откройте: https://www.perplexity.ai/settings/api
4. Нажмите **"Generate API Key"**
5. Скопируйте ключ (начинается с `pplx-...`)

**Сохраните:** `pplx-abcd1234...`

---

## 📥 ШАГ 3: Импортировать Workflows в n8n (5 минут)

### 3.1 Импортировать 4 файла

В n8n нажмите **Workflows → Import from File** и выберите:

1. `READY_workflow_01_SearchCompanies.json` (поиск)
2. `READY_workflow_02_AddSite.json` (ручное добавление)
3. `READY_workflow_03_ScrapData.json` (сбор данных)
4. `READY_workflow_04_GenerateEmails.json` (генерация писем)

### 3.2 Настроить каждый workflow

**В каждом из 4 workflows:**

1. Откройте workflow
2. Нажмите **Ctrl+F** (поиск)
3. Найдите: `YOUR_GOOGLE_SHEET_ID_HERE`
4. Замените на **ваш ID таблицы** (из Шага 1.3)
5. Нажмите **Save** (Сохранить)

**В workflow_01 (поиск):**
1. Откройте ноду **"🔍 Google Custom Search"**
2. Найдите параметры запроса:
   - `key` → вставьте ваш **API key** (из Шага 2.1)
   - `cx` → вставьте ваш **Search Engine ID** (из Шага 2.1)
3. Сохраните

**В workflow_03 и workflow_04 (AI):**
1. Откройте ноду **"🤖 Perplexity AI"**
2. В Headers найдите **Authorization**
3. Замените `YOUR_PERPLEXITY_API_KEY_HERE` на: `Bearer pplx-ваш_ключ`
   ```
   Было: Bearer YOUR_PERPLEXITY_API_KEY_HERE
   Стало: Bearer pplx-abcd1234efgh5678ijkl9012mnop3456
   ```
4. Сохраните

**В workflow_04 (генерация писем):**
1. Откройте ноду **"📝 Подготовить данные для шаблона"**
2. Найдите `yourCompanyInfo` в коде
3. Замените на данные вашей компании:
   ```javascript
   const yourCompanyInfo = {
     name: 'ВАша Компания',           // Ваше название
     service: 'ваш продукт',           // Что продаете
     benefits: 'ключевые преимущества', // Чем лучше
     contactPerson: 'Ваше Имя',
     position: 'Ваша Должность',
     phone: '+7 (999) 123-45-67',
     email: 'your@email.ru',
     website: 'https://your-site.ru'
   };
   ```
4. Сохраните

### 3.3 Настроить Google Sheets Credentials (один раз)

1. В n8n перейдите: **Settings → Credentials**
2. Нажмите **+ Add Credential**
3. Выберите **Google Sheets OAuth2 API**
4. Следуйте инструкциям для OAuth (n8n покажет как)
5. Сохраните credential

**В каждом workflow:**
1. Откройте ноды с Google Sheets (💾 иконки)
2. В поле **Credential** выберите созданный credential
3. Сохраните

---

## ✅ ШАГ 4: Активировать и протестировать (5 минут)

### 4.1 Активировать все workflows

В каждом из 4 workflows:
1. Откройте workflow
2. В правом верхнем углу переключите **Inactive → Active**
3. Должно стать зеленым

### 4.2 Получить webhook URLs

**Workflow 01 (поиск):**
- Откройте первую ноду (Webhook)
- Скопируйте **Production URL**
- Сохраните как: `URL_SEARCH`

**Workflow 02 (добавление):**
- Скопируйте Production URL
- Сохраните как: `URL_ADD`

**Workflow 03 (сбор данных):**
- Скопируйте Production URL
- Сохраните как: `URL_SCRAPE`

**Workflow 04 (генерация писем):**
- Скопируйте Production URL
- Сохраните как: `URL_GENERATE`

### 4.3 Тест 1: Поиск компаний

```bash
curl -X POST URL_SEARCH \
  -H "Content-Type: application/json" \
  -d '{
    "query": "агентство недвижимости",
    "city": "Благовещенск",
    "region": "Амурская область"
  }'
```

**Ожидаемый результат:**
```json
{
  "success": true,
  "websites_found": 10,
  "message": "Search completed"
}
```

**Проверьте:** Откройте Google Sheets → CompanySites → должны появиться сайты с Status=0

### 4.4 Тест 2: Сбор данных

```bash
curl -X POST URL_SCRAPE \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Ожидаемый результат:**
```json
{
  "success": true,
  "companies_processed": 10,
  "message": "Scraping completed"
}
```

**Проверьте:** CompanyInformation → должны появиться данные компаний

### 4.5 Тест 3: Генерация писем

```bash
curl -X POST URL_GENERATE \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Ожидаемый результат:**
```json
{
  "success": true,
  "emails_generated": 8,
  "message": "Proposals generated"
}
```

**Проверьте:** EmailDrafts → должны появиться черновики писем

---

## 🎉 ГОТОВО!

Теперь у вас работает **полная система**:

```
1. Поиск компаний в Google (100/день бесплатно)
   ↓
2. Сбор контактных данных с AI ($5 = 5000 компаний)
   ↓
3. Генерация персональных предложений (включено в $5)
   ↓
4. Готовые черновики писем для отправки!
```

---

## 🔧 Если что-то не работает:

### Ошибка "Missing node to start execution"
- ❌ НЕ нажимайте кнопку Execute на нодах!
- ✅ Используйте только webhook URLs через curl/Postman

### Ошибка с Google Sheets
- Проверьте что ID таблицы правильный
- Проверьте что Google Sheets Credentials настроены

### Ошибка с Perplexity API
- Проверьте что ключ вставлен с `Bearer ` в начале
- Проверьте баланс: https://www.perplexity.ai/settings/api

### Ошибка с Google Custom Search
- Убедитесь что включено "Поиск по всему Интернету"
- Проверьте что параметры `key` и `cx` правильные

---

## 📊 Что дальше?

1. **Найдите 100 компаний:** Запустите поиск несколько раз с разными запросами
2. **Соберите данные:** Запустите сбор данных
3. **Сгенерируйте письма:** Создайте персональные предложения
4. **Проверьте черновики:** Откройте EmailDrafts в Google Sheets
5. **Отправьте письма:** Используйте Gmail или почтовый клиент

---

## 💰 Стоимость:

- **Google Custom Search:** БЕСПЛАТНО (100 запросов/день)
- **Perplexity AI:** $5 бесплатных кредитов = ~5000 компаний
- **После $5:** ~$1 за 1000 компаний

**Итого:** Первые 5000 компаний - почти бесплатно! 🎉

---

**Удачи! Если возникнут вопросы - смотрите полную документацию в FILES_MAP.md**
