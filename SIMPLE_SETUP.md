# 🚀 ПРОСТАЯ НАСТРОЙКА (Только Perplexity AI)

## Преимущества этого варианта:
✅ Только 1 API ключ (Perplexity) - никаких Google настроек!
✅ $5 бесплатных кредитов на Perplexity
✅ Быстрая настройка за 10 минут
✅ Perplexity ищет компании онлайн и сразу возвращает результаты

---

## 📋 ШАГ 1: Получить Perplexity API ключ

1. Перейдите: https://www.perplexity.ai/
2. Зарегистрируйтесь (можно через Google)
3. Перейдите в **Settings** → **API**
4. Нажмите **Generate API Key**
5. Скопируйте ключ (начинается с `pplx-...`)
6. **Сохраните ключ!** (У вас есть $5 бесплатных кредитов)

---

## 📋 ШАГ 2: Получить Telegram Bot Token

1. Откройте Telegram → найдите **@BotFather**
2. Отправьте: `/newbot`
3. Придумайте название: **"Мой Лид Бот"**
4. Придумайте username: **`my_lead_bot`** (должен заканчиваться на `_bot`)
5. Скопируйте **токен** (выглядит как `123456789:ABC...`)
6. **Сохраните токен!**

---

## 📋 ШАГ 3: Создать Google Sheets таблицу

### 3.1 Создать таблицу
1. Откройте: https://sheets.google.com
2. Создайте новую таблицу: **"Лиды - База данных"**
3. Создайте 3 листа: **CompanySites**, **CompanyInformation**, **EmailDrafts**

### 3.2 Настроить листы

**Лист CompanySites** - вставьте заголовки:
```
ID | URL | Company Name | Status | Created At | Updated At | Source
```

**Лист CompanyInformation** - вставьте заголовки:
```
ID | Site ID | Company Name | INN | Address | Phone | Email | Description | Products/Services | Contact Person | Scraped At | Raw Data
```

**Лист EmailDrafts** - вставьте заголовки:
```
ID | Site ID | Company Name | Email | Subject | Body | Generated At | Status
```

### 3.3 Скопировать ID таблицы
- URL выглядит так: `https://docs.google.com/spreadsheets/d/ВАШ_ID_ЗДЕСЬ/edit`
- Скопируйте ID (между `/d/` и `/edit`)
- **Сохраните ID!**

---

## 📋 ШАГ 4: Импортировать workflows в n8n

Импортируйте эти 5 файлов (в таком порядке):

1. **FIXED_workflow_01_SearchCompanies_Perplexity.json** ⚡ (новый!)
2. **FINAL_workflow_02_AddSite.json**
3. **FINAL_workflow_03_ScrapData.json**
4. **FINAL_workflow_04_GenerateEmails.json**
5. **FINAL_MAIN_TelegramBot.json**

Для каждого:
- Workflows → Import from File
- Выберите файл → Import

---

## 📋 ШАГ 5: Настроить workflow 01 (Поиск с Perplexity)

### 5.1 Открыть workflow
Откройте: **"01 - Поиск компаний (Perplexity AI)"**

### 5.2 Настроить Perplexity AI
1. Откройте ноду: **"Perplexity AI Search"**
2. В Headers → найдите **Authorization**
3. Замените `YOUR_PERPLEXITY_API_KEY` на ваш ключ:
   ```
   Bearer pplx-ваш-ключ-здесь
   ```
4. Сохраните

### 5.3 Настроить Google Sheets
1. Откройте ноду: **"Сохранить в Google Sheets"**
2. В поле **Credential** → Create New → Google Sheets OAuth2 API
3. Подключите Google аккаунт
4. В поле **Document ID** → вставьте ID таблицы
5. В поле **Sheet Name** → выберите **CompanySites**
6. Сохраните

### 5.4 Активировать и скопировать URL
1. Переключите **Inactive → Active**
2. Кликните на ноду **"Webhook"**
3. Скопируйте **Production URL**
4. **Сохраните URL!**

---

## 📋 ШАГ 6: Настроить workflows 02, 03, 04

### Workflow 02 (Добавить сайт):
1. Откройте workflow
2. Нода **"Сохранить в Google Sheets"**:
   - Credential: выберите созданный
   - Document ID: ваш ID таблицы
   - Sheet Name: **CompanySites**
3. Активируйте workflow
4. Скопируйте Production URL из ноды "Webhook"

### Workflow 03 (Сбор данных):
1. Откройте workflow
2. Настройте **3 ноды Google Sheets**:
   - "Получить сайты (статус=0)" → CompanySites
   - "Сохранить данные компании" → CompanyInformation
   - "Обновить статус → 2" → CompanySites
3. Настройте **Perplexity AI**:
   - В Headers → Authorization → `Bearer pplx-ваш-ключ`
4. Активируйте workflow
5. Скопируйте Production URL

### Workflow 04 (Генерация писем):
1. Откройте workflow
2. Настройте **2 ноды Google Sheets**:
   - "Получить компании" → CompanyInformation
   - "Сохранить письмо" → EmailDrafts
3. **ВАЖНО! Откройте ноду "⚠️ НАСТРОЙТЕ ДАННЫЕ КОМПАНИИ"**:
   - Измените данные вашей компании в коде:
   ```javascript
   const YOUR_COMPANY = {
     name: 'ООО "Ваша Компания"',
     service: 'ваши услуги',
     contact: 'Ваше Имя',
     position: 'Ваша Должность',
     phone: '+7 (999) 123-45-67',
     email: 'info@yourcompany.ru'
   };
   ```
4. Настройте **Perplexity AI**:
   - В Headers → Authorization → `Bearer pplx-ваш-ключ`
5. Активируйте workflow
6. Скопируйте Production URL

---

## 📋 ШАГ 7: Настроить главный Telegram workflow

### 7.1 Открыть workflow
Откройте: **"ГЛАВНЫЙ - Telegram Бот"**

### 7.2 Настроить Telegram (3 ноды!)
1. **"Telegram Trigger"**:
   - Credential → Create New → Telegram API
   - Вставьте токен бота
   - Сохраните
2. **"Отправить ответ"**:
   - Credential → выберите созданный
3. **"Показать справку"**:
   - Credential → выберите созданный

### 7.3 НАСТРОИТЬ WEBHOOK URLs!
1. Откройте ноду: **"⚠️ НАСТРОЙТЕ WEBHOOK URLs"**
2. Вставьте все 4 Production URLs:
   ```javascript
   webhook_search: "URL из workflow 01"
   webhook_add: "URL из workflow 02"
   webhook_scrape: "URL из workflow 03"
   webhook_generate: "URL из workflow 04"
   ```
3. Сохраните

### 7.4 Активировать
Переключите **Inactive → Active**

---

## 🎉 ШАГ 8: ТЕСТИРОВАНИЕ!

### Тест 1: Поиск компаний
Откройте Telegram бота и отправьте:
```
найди строительные компании
```

**Ожидается:**
- Бот ответит "Найдено X компаний"
- В Google Sheets → CompanySites появятся сайты

### Тест 2: Сбор данных
Отправьте:
```
собери данные с сайтов
```

**Ожидается:**
- Бот ответит "Обработано X компаний"
- В Google Sheets → CompanyInformation появятся контакты

### Тест 3: Генерация писем
Отправьте:
```
создай письма
```

**Ожидается:**
- Бот ответит "Создано писем: X"
- В Google Sheets → EmailDrafts появятся письма

---

## ✅ ЧЕКЛИСТ

Перед использованием проверьте:

**API Ключи:**
- [ ] Perplexity API Key получен ($5 бесплатно!)
- [ ] Telegram Bot Token получен

**Google Sheets:**
- [ ] Таблица создана с 3 листами
- [ ] Все заголовки вставлены
- [ ] ID таблицы скопирован

**Workflows:**
- [ ] Все 5 workflows импортированы
- [ ] Workflow 01 настроен (Perplexity API Key!)
- [ ] Workflow 02 настроен
- [ ] Workflow 03 настроен (Perplexity API Key!)
- [ ] Workflow 04 настроен (Perplexity API Key + данные компании!)
- [ ] Главный workflow настроен (Webhook URLs!)
- [ ] Все 5 workflows активированы

**Тестирование:**
- [ ] Поиск работает
- [ ] Сбор данных работает
- [ ] Генерация писем работает

---

## 💡 ПРИМЕРЫ КОМАНД

```
найди строительные компании
найти IT компании
найти агентства недвижимости в Москве

добавь сайт https://example.com

собери данные
собери информацию с сайтов

создай письма
создать коммерческие предложения
```

---

## 💰 СТОИМОСТЬ

### Perplexity AI:
- **$5 бесплатных кредитов** при регистрации
- Поиск компаний: ~$0.01 за запрос (100-200 запросов на $5)
- Сбор данных: ~$0.02 за компанию (100-200 компаний на $5)
- Генерация писем: ~$0.02 за письмо (100-200 писем на $5)

**ИТОГО: $5 бесплатно = примерно 100-200 полных циклов (поиск → сбор → письма)** 🎉

---

## 🔧 ЕСЛИ НЕ РАБОТАЕТ

### Бот не отвечает:
✅ Главный workflow активирован?
✅ Telegram credential правильный?
✅ Все 4 child workflows активированы?

### Поиск не работает:
✅ Perplexity API Key правильный? (начинается с pplx-)
✅ Баланс Perplexity > $0?

### Сбор данных не работает:
✅ В CompanySites есть сайты со статусом 0?
✅ Perplexity API Key настроен в workflow 03?

### Генерация писем не работает:
✅ В CompanyInformation есть компании с email?
✅ Данные вашей компании настроены в коде?
✅ Perplexity API Key настроен в workflow 04?

---

## 🎯 ПРЕИМУЩЕСТВА ЭТОГО ВАРИАНТА

✅ **Один API ключ** - только Perplexity (никаких Google Cloud настроек!)
✅ **$5 бесплатно** - хватит на 100-200 компаний
✅ **Онлайн поиск** - Perplexity ищет актуальные данные в реальном времени
✅ **Умный AI** - понимает запросы на русском языке
✅ **Простая настройка** - 10 минут вместо 30

---

**ГОТОВО! Начинайте использовать!** 🚀
