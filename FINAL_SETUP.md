# 🚀 БЫСТРАЯ НАСТРОЙКА - Telegram Бот для поиска лидов

## Что вы получите:
✅ Telegram бот который ищет компании через Google
✅ Автоматический сбор контактов с сайтов (AI)
✅ Генерация персональных коммерческих предложений (AI)
✅ Всё сохраняется в Google Sheets

---

## 📋 ШАГ 1: Подготовка Google Sheets

### 1.1 Создать новую таблицу
1. Откройте Google Sheets: https://sheets.google.com
2. Создайте новую таблицу: **"Лиды - База данных"**
3. Создайте 3 листа:
   - **CompanySites**
   - **CompanyInformation**
   - **EmailDrafts**

### 1.2 Настроить CompanySites
Вставьте заголовки в первую строку:
```
ID | URL | Company Name | Status | Created At | Updated At | Source
```

### 1.3 Настроить CompanyInformation
Вставьте заголовки в первую строку:
```
ID | Site ID | Company Name | INN | Address | Phone | Email | Description | Products/Services | Contact Person | Scraped At | Raw Data
```

### 1.4 Настроить EmailDrafts
Вставьте заголовки в первую строку:
```
ID | Site ID | Company Name | Email | Subject | Body | Generated At | Status
```

### 1.5 Скопировать ID таблицы
- Откройте вашу Google Sheets таблицу
- Скопируйте ID из URL (между `/d/` и `/edit`):
  ```
  https://docs.google.com/spreadsheets/d/ВАШ_ID_ЗДЕСЬ/edit
  ```
- **Сохраните этот ID!**

---

## 📋 ШАГ 2: Получить API ключи

### 2.1 Google Custom Search API

**Создать проект и получить API ключ:**
1. Перейдите: https://console.cloud.google.com/apis/credentials
2. Создайте новый проект: **"n8n-lead-search"**
3. Нажмите **Create Credentials → API Key**
4. Скопируйте ключ (выглядит как `AIzaSy...`)
5. **Сохраните API ключ!**

**Включить API:**
1. Перейдите: https://console.cloud.google.com/apis/library
2. Найдите: **"Custom Search API"**
3. Нажмите **Enable**

**Создать Search Engine:**
1. Перейдите: https://programmablesearchengine.google.com/
2. Нажмите **Add** → Создать новую поисковую систему
3. В поле "Sites to search" введите: `*` (поиск по всему интернету)
4. Название: **"Lead Search Russia"**
5. Язык: **Russian**
6. Создайте
7. На странице настроек скопируйте **Search engine ID** (cx)
8. **Сохраните Search Engine ID!**

### 2.2 Perplexity AI API

1. Перейдите: https://www.perplexity.ai/
2. Зарегистрируйтесь
3. Перейдите в Settings → API
4. Создайте новый API ключ
5. Скопируйте ключ (выглядит как `pplx-...`)
6. **Сохраните API ключ!** ($5 бесплатных кредитов)

### 2.3 Telegram Bot

1. Откройте Telegram → найдите **@BotFather**
2. Отправьте: `/newbot`
3. Придумайте название: **"Мой Лид Бот"**
4. Придумайте username: **`my_lead_bot`** (должен заканчиваться на `_bot`)
5. Скопируйте **токен** (выглядит как `123456789:ABC...`)
6. **Сохраните токен!**

---

## 📋 ШАГ 3: Импорт workflows в n8n

### 3.1 Импортировать 4 child workflows

**Импортируйте В ТАКОМ ПОРЯДКЕ:**

1. **FINAL_workflow_01_SearchCompanies.json**
   - Workflows → Import from File
   - Выберите файл → Import

2. **FINAL_workflow_02_AddSite.json**
   - Workflows → Import from File
   - Выберите файл → Import

3. **FINAL_workflow_03_ScrapData.json**
   - Workflows → Import from File
   - Выберите файл → Import

4. **FINAL_workflow_04_GenerateEmails.json**
   - Workflows → Import from File
   - Выберите файл → Import

5. **FINAL_MAIN_TelegramBot.json**
   - Workflows → Import from File
   - Выберите файл → Import

Теперь у вас 5 workflows в n8n.

---

## 📋 ШАГ 4: Настройка workflow 01 (Поиск компаний)

### 4.1 Открыть workflow
Откройте: **"01 - Поиск компаний (Google)"**

### 4.2 Настроить Google Custom Search
1. Откройте ноду: **"Google Custom Search"**
2. Найдите параметр `key` → вставьте ваш **Google API Key**
3. Найдите параметр `cx` → вставьте ваш **Search Engine ID**
4. Сохраните

### 4.3 Настроить Google Sheets
1. Откройте ноду: **"Сохранить в Google Sheets"**
2. В поле **Credential** нажмите **Create New**
3. Выберите **Google Sheets OAuth2 API**
4. Подключите ваш Google аккаунт
5. В поле **Document ID** вставьте ID вашей Google Sheets таблицы
6. В поле **Sheet Name** выберите: **CompanySites**
7. Сохраните

### 4.4 Активировать workflow
- Переключите **Inactive → Active** (вверху справа)

### 4.5 Скопировать Production URL
1. Кликните на ноду **"Webhook"** (первая нода)
2. Скопируйте **Production URL** (выглядит как `https://ваш-n8n.com/webhook/search-companies`)
3. **Сохраните этот URL!**

---

## 📋 ШАГ 5: Настройка workflow 02 (Добавить сайт)

### 5.1 Открыть workflow
Откройте: **"02 - Добавить сайт вручную"**

### 5.2 Настроить Google Sheets
1. Откройте ноду: **"Сохранить в Google Sheets"**
2. В поле **Credential** выберите созданный ранее credential
3. В поле **Document ID** вставьте ID вашей таблицы
4. В поле **Sheet Name** выберите: **CompanySites**
5. Сохраните

### 5.3 Активировать workflow
- Переключите **Inactive → Active**

### 5.4 Скопировать Production URL
1. Кликните на ноду **"Webhook"**
2. Скопируйте **Production URL**
3. **Сохраните URL!**

---

## 📋 ШАГ 6: Настройка workflow 03 (Сбор данных)

### 6.1 Открыть workflow
Откройте: **"03 - Сбор данных (Perplexity AI)"**

### 6.2 Настроить Google Sheets (3 ноды!)

**Нода 1: "Получить сайты (статус=0)"**
- Credential: выберите созданный
- Document ID: вставьте ID таблицы
- Sheet Name: **CompanySites**

**Нода 2: "Сохранить данные компании"**
- Credential: выберите созданный
- Document ID: вставьте ID таблицы
- Sheet Name: **CompanyInformation**

**Нода 3: "Обновить статус → 2"**
- Credential: выберите созданный
- Document ID: вставьте ID таблицы
- Sheet Name: **CompanySites**

### 6.3 Настроить Perplexity AI
1. Откройте ноду: **"Perplexity AI"**
2. В Headers → найдите **Authorization**
3. Замените `YOUR_PERPLEXITY_API_KEY` на ваш ключ (например: `Bearer pplx-abc123...`)
4. Сохраните

### 6.4 Активировать workflow
- Переключите **Inactive → Active**

### 6.5 Скопировать Production URL
1. Кликните на ноду **"Webhook"**
2. Скопируйте **Production URL**
3. **Сохраните URL!**

---

## 📋 ШАГ 7: Настройка workflow 04 (Генерация писем)

### 7.1 Открыть workflow
Откройте: **"04 - Генерация писем (Perplexity AI)"**

### 7.2 Настроить Google Sheets (2 ноды!)

**Нода 1: "Получить компании"**
- Credential: выберите созданный
- Document ID: вставьте ID таблицы
- Sheet Name: **CompanyInformation**

**Нода 2: "Сохранить письмо"**
- Credential: выберите созданный
- Document ID: вставьте ID таблицы
- Sheet Name: **EmailDrafts**

### 7.3 НАСТРОИТЬ ДАННЫЕ ВАШЕЙ КОМПАНИИ!
1. Откройте ноду: **"⚠️ НАСТРОЙТЕ ДАННЫЕ КОМПАНИИ"**
2. Найдите блок `YOUR_COMPANY` в коде
3. Замените на ваши данные:
```javascript
const YOUR_COMPANY = {
  name: 'ООО "Ваша Компания"',
  service: 'IT решения для автоматизации бизнеса',
  contact: 'Иван Иванов',
  position: 'Коммерческий директор',
  phone: '+7 (999) 123-45-67',
  email: 'info@yourcompany.ru'
};
```
4. Сохраните

### 7.4 Настроить Perplexity AI
1. Откройте ноду: **"Perplexity AI"**
2. В Headers → найдите **Authorization**
3. Замените `YOUR_PERPLEXITY_API_KEY` на ваш ключ
4. Сохраните

### 7.5 Активировать workflow
- Переключите **Inactive → Active**

### 7.6 Скопировать Production URL
1. Кликните на ноду **"Webhook"**
2. Скопируйте **Production URL**
3. **Сохраните URL!**

---

## 📋 ШАГ 8: Настройка главного Telegram workflow

### 8.1 Открыть workflow
Откройте: **"ГЛАВНЫЙ - Telegram Бот"**

### 8.2 Настроить Telegram credentials (3 ноды!)

**Нода 1: "Telegram Trigger"**
- В поле **Credential** нажмите **Create New**
- Выберите **Telegram API**
- Вставьте **токен бота** (из @BotFather)
- Сохраните

**Нода 2: "Отправить ответ"**
- В поле **Credential** выберите созданный Telegram credential

**Нода 3: "Показать справку"**
- В поле **Credential** выберите созданный Telegram credential

### 8.3 НАСТРОИТЬ WEBHOOK URLs!
1. Откройте ноду: **"⚠️ НАСТРОЙТЕ WEBHOOK URLs"**
2. Замените ВСЕ 4 URL на Production URLs из предыдущих шагов:

```javascript
webhook_search: "вставьте URL из workflow 01"
webhook_add: "вставьте URL из workflow 02"
webhook_scrape: "вставьте URL из workflow 03"
webhook_generate: "вставьте URL из workflow 04"
```

**Пример:**
```javascript
webhook_search: "https://n8n.yourserver.com/webhook/search-companies"
webhook_add: "https://n8n.yourserver.com/webhook/add-site"
webhook_scrape: "https://n8n.yourserver.com/webhook/scrape-data"
webhook_generate: "https://n8n.yourserver.com/webhook/generate-emails"
```

3. Сохраните

### 8.4 Активировать workflow
- Переключите **Inactive → Active**

---

## 🎉 ШАГ 9: ТЕСТИРОВАНИЕ!

### 9.1 Проверка 1 - Справка
1. Откройте Telegram
2. Найдите вашего бота (username который создали)
3. Нажмите **Start**
4. Отправьте: `привет`

**Ожидается:** Бот показывает список команд

### 9.2 Проверка 2 - Поиск компаний
Отправьте боту:
```
найди строительные компании
```

**Ожидается:**
- Бот ответит "Найдено X компаний"
- В Google Sheets → лист CompanySites появятся сайты

### 9.3 Проверка 3 - Сбор данных
Отправьте боту:
```
собери данные с сайтов
```

**Ожидается:**
- Бот ответит "Обработано X компаний"
- В Google Sheets → лист CompanyInformation появятся контакты

### 9.4 Проверка 4 - Генерация писем
Отправьте боту:
```
создай письма
```

**Ожидается:**
- Бот ответит "Создано писем: X"
- В Google Sheets → лист EmailDrafts появятся письма

### 9.5 Проверка 5 - Добавить сайт
Отправьте боту:
```
добавь сайт https://example.com
```

**Ожидается:**
- Бот ответит "Сайт добавлен"
- В Google Sheets → CompanySites появится новая строка

---

## ✅ ЧЕКЛИСТ ГОТОВНОСТИ

Перед использованием убедитесь:

**Google Sheets:**
- [ ] Таблица создана с 3 листами
- [ ] Все заголовки вставлены
- [ ] ID таблицы скопирован

**API Ключи:**
- [ ] Google API Key получен
- [ ] Google Search Engine ID получен
- [ ] Perplexity API Key получен
- [ ] Telegram Bot Token получен

**Workflows:**
- [ ] Все 5 workflows импортированы
- [ ] Workflow 01 настроен и активирован
- [ ] Workflow 02 настроен и активирован
- [ ] Workflow 03 настроен и активирован
- [ ] Workflow 04 настроен (ДАННЫЕ КОМПАНИИ!) и активирован
- [ ] Главный workflow настроен (WEBHOOK URLs!) и активирован

**Тестирование:**
- [ ] Справка работает
- [ ] Поиск работает
- [ ] Сбор данных работает
- [ ] Генерация писем работает
- [ ] Добавление сайта работает

**Если все галочки стоят - ВСЁ РАБОТАЕТ!** 🎉

---

## 💡 ПРИМЕРЫ КОМАНД ДЛЯ БОТА

### Поиск компаний:
```
найди агентства недвижимости
найти строительные компании
найти IT компании в Москве
поиск салоны красоты
```

### Добавить сайт:
```
добавь сайт https://example.ru
добавить https://company.com
```

### Сбор данных:
```
собери данные
собери информацию с сайтов
собрать контакты
```

### Генерация писем:
```
создай письма
создать коммерческие предложения
генерируй email
```

---

## 🔧 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

### Бот не отвечает
✅ Проверьте что главный workflow активирован
✅ Проверьте Telegram credential (правильный токен?)
✅ Посмотрите в Executions → есть ли ошибки

### Поиск не работает
✅ Проверьте Google API Key
✅ Проверьте Search Engine ID (cx)
✅ Убедитесь что Custom Search API включен в Google Cloud

### Сбор данных не работает
✅ Проверьте Perplexity API Key (начинается с pplx-)
✅ Проверьте баланс Perplexity (должно быть >$0)
✅ Убедитесь что есть сайты со статусом 0 в CompanySites

### Генерация писем не работает
✅ Проверьте что настроили данные компании в коде
✅ Проверьте Perplexity API Key
✅ Убедитесь что в CompanyInformation есть компании с email

### "Missing node to start execution"
✅ Проверьте что все 4 child workflows АКТИВИРОВАНЫ
✅ Проверьте webhook URLs в главном workflow (правильные Production URLs?)
✅ URLs должны быть БЕЗ trailing slash в конце

---

## 💰 СТОИМОСТЬ

### Google Custom Search:
- **Бесплатно: 100 запросов/день**
- $5 за 1000 запросов свыше лимита

### Perplexity AI:
- **$5 бесплатных кредитов**
- $0.20 за 1M токенов
- 1 компания ≈ 5000 токенов
- $5 = примерно 5000 компаний

**ИТОГО: Первые 5000 компаний почти БЕСПЛАТНО!** 🎉

---

## 🎯 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Сценарий 1: Поиск B2B клиентов в регионе
```
Telegram → "найди строительные компании"
→ Получено 50 сайтов

Telegram → "собери данные"
→ Получены контакты 50 компаний

Telegram → "создай письма"
→ Готовы 35 персональных писем

Google Sheets → EmailDrafts → копируете письма → отправляете
```

### Сценарий 2: Холодные продажи
```
День 1: "найди IT компании" → 100 компаний
День 2: "собери данные" → контакты 80 компаний
День 3: "создай письма" → 60 готовых писем
День 4-7: Отправка писем и отслеживание откликов
```

---

**ГОТОВО! Теперь у вас работающий Telegram бот для автоматизации поиска лидов!** 🚀

Удачи в продажах! 💼
