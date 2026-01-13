# Решение: Немедленный поиск компаний

## Проблема

**Текущая ситуация:**
- Workflow AgentLeadAddQuery только добавляет запрос в таблицу
- Возвращает текст запроса вместо компаний
- Компании должны появляться через 10-15 минут (Cycle 2)
- НО Cycle 2 отключен и не работает!

**Что видит пользователь:**

| query | status | message |
|-------|--------|---------|
| Подготовить запросы на тему строительные компании, город Москва | prepared | Запрос подготовлен: ... |

❌ **Нет компаний!**

## Исправление

### Вариант 1: Активировать Cycle 2 (быстрое решение)

**Шаги в n8n:**

1. Откройте workflow "Цикл 2 - Поиск сайтов компаний"
2. Добавьте Perplexity API ключ (строка 85):
   ```json
   "value": "Bearer pplx-ВАШ_API_КЛЮЧ_ЗДЕСЬ"
   ```
3. Активируйте workflow (кнопка "Active")
4. Компании появятся в таблице "Компании" через 10 минут

**Минусы:**
- Надо ждать 10 минут
- Нужен API ключ Perplexity
- Компании приходят в другую вкладку таблицы

---

### Вариант 2: Модифицировать AgentLeadAddQuery (РЕКОМЕНДУЕТСЯ)

Изменить workflow чтобы он сразу искал компании и возвращал результат.

**Новая структура workflow:**

```
When Executed
  ↓
Извлечь параметры (query, city, theme)
  ↓
Построить поисковый запрос
  ↓
🆕 Perplexity AI - Поиск компаний
  ↓
🆕 Извлечь данные компаний (name, website, city, phone, email)
  ↓
Сохранить в Google Sheets "Компании"
  ↓
Вернуть список компаний (НЕ текст запроса!)
```

**Преимущества:**
- ✅ Немедленный результат (1-2 секунды)
- ✅ Возвращает реальные компании
- ✅ Не нужно ждать Cycle 2
- ✅ Можно использовать разные AI API (Perplexity, Claude, OpenAI)

---

### Вариант 3: Использовать альтернативный поиск БЕЗ Perplexity

Если нет API ключа Perplexity, можно использовать:

1. **Google Custom Search API** (бесплатно до 100 запросов/день)
2. **SerpAPI** (поиск в Google)
3. **Claude API** (с tool use для веб-поиска)
4. **OpenAI GPT-4** (с function calling)

---

## Какой вариант выбрать?

| Вариант | Скорость | Сложность | API ключ | Рекомендация |
|---------|----------|-----------|----------|--------------|
| 1. Активировать Cycle 2 | 10 минут | Низкая | Perplexity | Если есть API ключ |
| 2. Модифицировать workflow | 1-2 секунды | Средняя | Perplexity/Claude/OpenAI | **✅ РЕКОМЕНДУЕТСЯ** |
| 3. Альтернативный поиск | 2-5 секунд | Средняя | Google/SerpAPI | Если нет Perplexity |

---

## Реализация Варианта 2 (рекомендуется)

### Шаг 1: Выберите AI API

**Опция A: Perplexity AI** (лучше для поиска компаний)
- Специализируется на веб-поиске
- Возвращает актуальные данные
- Стоимость: ~$0.001 за запрос

**Опция B: Claude API** (универсальный)
- Можно использовать с инструментом WebSearch
- Стоимость: ~$0.003 за запрос
- Нужен промпт для извлечения компаний

**Опция C: OpenAI GPT-4**
- С function calling для веб-поиска
- Стоимость: ~$0.03 за запрос

### Шаг 2: Добавьте узлы в workflow

1. **HTTP Request (Perplexity AI)**
   ```json
   {
     "model": "sonar-pro",
     "messages": [
       {
         "role": "system",
         "content": "Найди компании по запросу и верни JSON: {\"companies\": [{\"name\": \"...\", \"website\": \"...\", \"city\": \"...\", \"phone\": \"...\", \"email\": \"...\"}]}"
       },
       {
         "role": "user",
         "content": "{{ $json.query }}"
       }
     ]
   }
   ```

2. **Code node - Извлечь компании**
   ```javascript
   const response = $input.first().json;
   const content = response.choices[0].message.content;
   const data = JSON.parse(content);

   return data.companies.map(company => ({
     json: {
       company_name: company.name,
       website: company.website,
       city: company.city,
       phone: company.phone || '',
       email: company.email || '',
       source_query: $json.query,
       found_date: new Date().toISOString()
     }
   }));
   ```

3. **Google Sheets - Сохранить компании**
   - Sheet: "Компании" (gid=0)
   - Columns: Компания, Сайт, Город, Телефон, Почта

4. **Set node - Вернуть результат**
   ```json
   {
     "success": true,
     "companies_found": "{{ $('Code').all().length }}",
     "companies": "{{ $('Code').all() }}"
   }
   ```

### Шаг 3: Удалите старые узлы

Удалите:
- ❌ "Обработать запрос" (возвращает только текст)
- ❌ "Добавить запрос в Google Sheets" (в лист Запросы)
- ❌ "Сформировать ответ" (возвращает query_text)

---

## Итоговый результат

**Было (текст запроса):**
```json
{
  "success": true,
  "message": "Запрос успешно добавлен: ...",
  "query_text": "Подготовить запросы на тему строительные компании, город Москва"
}
```

**Стало (реальные компании):**
```json
{
  "success": true,
  "companies_found": 8,
  "companies": [
    {
      "company_name": "СтройМастер",
      "website": "https://stroymaster-msk.ru",
      "city": "Москва",
      "phone": "+7 495 123-45-67",
      "email": "info@stroymaster-msk.ru"
    },
    {
      "company_name": "МосСтрой",
      "website": "https://mosstroy.com",
      "city": "Москва",
      "phone": "+7 495 987-65-43",
      "email": "contact@mosstroy.com"
    }
    // ... ещё 6 компаний
  ]
}
```

---

## Нужна помощь с реализацией?

Выберите что делать:

1. ✅ **Создать готовый JSON workflow** для импорта в n8n
2. ✅ **Настроить API ключи** (Perplexity/Claude/OpenAI)
3. ✅ **Протестировать поиск** компаний

Дайте знать какой вариант вы выбираете!
