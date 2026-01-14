# Настройка Perplexity API (Простая альтернатива!)

## 🎯 Что это?

**Perplexity AI API** - простая и дешевая альтернатива Google Gemini для извлечения данных.

**Преимущества:**
- ✅ **$5 бесплатных кредитов** при регистрации
- ✅ Простая регистрация (через Google)
- ✅ Отличное качество извлечения данных
- ✅ API как у OpenAI (проще в использовании чем Gemini)
- ✅ Дешевле чем Claude API

---

## 📋 Шаг 1: Регистрация

### 1.1 Создать аккаунт

1. Перейдите: https://www.perplexity.ai/
2. Нажмите **"Sign Up"** в правом верхнем углу
3. Выберите **"Continue with Google"** (самый быстрый способ)
4. Подтвердите доступ к аккаунту Google

**Готово!** Вы зарегистрированы.

---

## 📋 Шаг 2: Получить API ключ

### 2.1 Перейти в настройки API

1. После входа в аккаунт нажмите на иконку профиля (правый верхний угол)
2. Выберите **"Settings"** (Настройки)
3. В левом меню найдите **"API"**

**Прямая ссылка:** https://www.perplexity.ai/settings/api

### 2.2 Сгенерировать ключ

1. На странице API нажмите **"Generate API Key"**
2. Скопируйте ключ (начинается с `pplx-...`)
3. **Сохраните этот ключ в безопасном месте!**

Пример ключа:
```
pplx-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
```

---

## 📋 Шаг 3: Настроить workflows в n8n

### 3.1 Импортировать workflows

1. Откройте n8n
2. Нажмите **"Import from File"**
3. Импортируйте:
   - `child_workflow_01_AgentLeadAddQuery_GoogleCSE.json` (поиск компаний)
   - `child_workflow_02_AgentLeadAddSiteCompany_FIXED.json` (ручное добавление)
   - `child_workflow_03_AgentLeadScrapInformationCompany_Perplexity.json` ⭐ **ЭТОТ**
   - `child_workflow_04_AgentLeadMailGenerate_Perplexity.json` ⭐ **ЭТОТ**

### 3.2 Вставить API ключ Perplexity

#### В workflow_03 (сбор данных):

1. Откройте ноду **"🤖 Perplexity AI"**
2. Найдите в Headers параметр **"Authorization"**
3. Замените `YOUR_PERPLEXITY_API_KEY_HERE` на ваш ключ:
   ```
   Bearer pplx-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
   ```

#### В workflow_04 (генерация писем):

1. Откройте ноду **"🤖 Perplexity AI"**
2. Найдите в Headers параметр **"Authorization"**
3. Замените `YOUR_PERPLEXITY_API_KEY_HERE` на ваш ключ:
   ```
   Bearer pplx-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
   ```

### 3.3 Заменить Google Sheets ID

В **ВСЕХ** workflow заменить `YOUR_GOOGLE_SHEET_ID_HERE` на ID вашей таблицы Google Sheets.

### 3.4 Настроить данные компании (workflow_04)

В workflow_04 откройте ноду **"📝 Подготовить данные для шаблона"** и измените:

```javascript
const yourCompanyInfo = {
  name: 'Ваша Компания',                    // Название вашей компании
  service: 'ваша услуга/продукт',           // Что вы предлагаете
  benefits: 'ключевые преимущества',        // Чем вы лучше конкурентов
  contactPerson: 'Ваше Имя',                // Ваше имя
  position: 'Ваша Должность',               // Ваша должность
  phone: '+7 (999) 123-45-67',              // Ваш телефон
  email: 'your@email.ru',                   // Ваш email
  website: 'https://your-company.ru'        // Ваш сайт
};
```

**Пример:**
```javascript
const yourCompanyInfo = {
  name: 'ИТ Решения',
  service: 'разработка CRM систем',
  benefits: 'быстрая интеграция, поддержка 24/7, окупаемость за 3 месяца',
  contactPerson: 'Иван Петров',
  position: 'Коммерческий директор',
  phone: '+7 (924) 555-12-34',
  email: 'ivan@it-solutions.ru',
  website: 'https://it-solutions.ru'
};
```

---

## 💰 Стоимость

| Модель | Стоимость | Когда использовать |
|--------|-----------|-------------------|
| **llama-3.1-sonar-small-128k-online** | **$0.20** за 1M токенов | ⭐ **Для всего** - лучший выбор |
| llama-3.1-sonar-large-128k-online | $1.00 за 1M токенов | Только для очень сложных задач |
| llama-3.1-sonar-huge-128k-online | $5.00 за 1M токенов | Не нужен для наших задач |

**Рекомендация:** Используйте `llama-3.1-sonar-small-128k-online` (уже установлен в workflows)

**Расчет стоимости:**
- 1 компания ≈ 5,000 токенов (запрос + ответ)
- 1000 компаний ≈ 5M токенов = **$1**
- **$5 бесплатных кредитов = ~5000 компаний!** 🎉

---

## 🧪 Шаг 4: Тестирование

### Тест 1: Сбор данных компаний

```bash
curl -X POST https://your-n8n.com/webhook/start-scraping \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "companies_processed": 10,
  "message": "Scraping completed"
}
```

### Тест 2: Генерация предложений

```bash
curl -X POST https://your-n8n.com/webhook/generate-proposals \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "emails_generated": 8,
  "message": "Proposals generated successfully"
}
```

---

## 🔧 Структура запроса к Perplexity API

Если вы хотите настроить что-то вручную, вот структура:

```json
{
  "model": "llama-3.1-sonar-small-128k-online",
  "messages": [
    {
      "role": "system",
      "content": "Ты эксперт по извлечению данных..."
    },
    {
      "role": "user",
      "content": "Проанализируй текст и извлеки данные..."
    }
  ],
  "temperature": 0.2,
  "max_tokens": 1000
}
```

**Параметры:**
- `temperature`: 0.2 для извлечения данных, 0.7 для генерации текстов
- `max_tokens`: 1000 для данных, 1500 для писем
- `model`: всегда `llama-3.1-sonar-small-128k-online`

---

## ❓ Частые вопросы

### Сколько бесплатно?

**$5 кредитов** при регистрации = ~5000 компаний обработать бесплатно!

### Где посмотреть баланс?

https://www.perplexity.ai/settings/api → вкладка "Usage"

### Что делать когда кредиты закончатся?

Добавить платежную карту в настройках. Стоимость очень низкая:
- 1000 компаний = ~$1
- 10000 компаний = ~$10

### Можно ли использовать без карты?

Да! Первые $5 бесплатны без карты.

### Perplexity лучше чем Gemini?

**Для наших задач - ДА!**
- ✅ Проще настроить (не нужен Google Cloud Console)
- ✅ Дешевле ($0.20 vs Gemini бесплатно, но с лимитами)
- ✅ Более стабильное качество извлечения данных
- ✅ Лучше понимает русский язык

---

## 🆚 Сравнение AI провайдеров

| | Perplexity | Google Gemini | Anthropic Claude |
|---|---|---|---|
| **Цена** | $0.20 / 1M токенов | Бесплатно* | $3 / 1M токенов |
| **Бесплатные кредиты** | $5 | Лимиты API | Нет |
| **Качество для русского** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Простота настройки** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Скорость** | Быстро | Очень быстро | Быстро |

*Gemini бесплатный, но есть rate limits: 60 запросов/минуту

**Вывод:** Perplexity - идеальный баланс цены, качества и простоты! ⭐

---

## 🚀 Что дальше?

После настройки у вас будет **ПОЛНОСТЬЮ БЕСПЛАТНАЯ** система (с $5 кредитами):

```
1. Google Custom Search → Поиск компаний (100/день бесплатно)
   ↓
2. Perplexity AI → Сбор данных (~5000 компаний на $5)
   ↓
3. Perplexity AI → Генерация писем (включено в $5)
   ↓
4. Готовые персональные предложения! 🎉
```

**Все workflows готовы к использованию!**

---

## 📞 Поддержка

Если что-то не работает:
1. Проверьте API ключ (должен начинаться с `pplx-`)
2. Убедитесь что ключ вставлен с `Bearer ` в начале
3. Проверьте баланс: https://www.perplexity.ai/settings/api
4. Посмотрите логи выполнения в n8n

**Документация Perplexity API:** https://docs.perplexity.ai/

---

**✅ Готово! Теперь у вас есть профессиональная система на Perplexity AI!**
