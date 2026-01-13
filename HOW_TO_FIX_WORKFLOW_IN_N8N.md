# Пошаговая инструкция: Как исправить workflow в n8n

## Проблема на скриншоте

В красной секции "Цикл записи и проверки запросов":
- Узел Google Sheets1 проверяет дубликаты через API
- Это вызывает rate limiting
- Запросы не добавляются в таблицу

## Решение: Упростить workflow

### ШАГ 1: Откройте workflow
1. n8n → Workflows
2. Откройте "АГЕНТ ЛИДЫ+КП 2026_v2.0"

### ШАГ 2: Найдите узел "Loop Over Items"
1. Это узел в начале красной секции
2. Он имеет 2 выхода (две стрелки)

### ШАГ 3: Найдите узел "Google Sheets" (который делает append)
1. Это ВТОРОЙ узел Google Sheets в красной секции
2. Он находится ПОСЛЕ узлов: Google Sheets1 → If → Wait
3. Его operation = "append" (добавление запросов)

### ШАГ 4: Переподключите поток

**Текущее подключение:**
```
Loop Over Items (второй выход)
  → Google Sheets1
  → If
  → Wait
  → Google Sheets (append)
```

**НОВОЕ подключение:**
```
Loop Over Items (первый выход)
  → Google Sheets (append)
```

**Как это сделать:**
1. Кликните на узел **Google Sheets** (append)
2. Удалите входящую связь от узла Wait
3. Перетащите связь от **Loop Over Items** → **первый выход** (там где сейчас идёт к Edit Fields)
4. Или измените настройку: Loop Over Items → Connections → Output 1 → Google Sheets

### ШАГ 5: Удалите ненужные узлы
Удалите следующие узлы (они больше не нужны):
1. **Google Sheets1** (проверка дубликатов)
2. **If** (условие)
3. **Wait** (задержка)
4. **Edit Fields** (если он не используется больше нигде)

### ШАГ 6: Проверьте узел Google Sheets (append)

Откройте узел **Google Sheets** (append) и убедитесь:

**Parameters:**
- Operation: `Append`
- Document: `Лиды компаний`
- Sheet: `Запросы` (gid=1305865408)
- Columns:
  - Запросы: `={{ $('Loop Over Items').item.json.contentArray }}`
  - Статус выполнения: `0`

**ВАЖНО:** Проверьте откуда берётся значение `contentArray`:
- Если из узла Code - укажите: `={{ $json.contentArray }}`
- Если из Loop Over Items - укажите: `={{ $('Loop Over Items').item.json.contentArray }}`

### ШАГ 7: Сохраните и протестируйте

1. Нажмите **Save** (Ctrl+S)
2. Нажмите **Execute Workflow**
3. Проверьте в Google Sheets лист "Запросы" - должны появиться запросы

---

## Почему это работает?

### Дубликаты УЖЕ убраны!
В верхней синей секции есть узел **"Remove Duplicates"**:
```
Code (генерация запросов)
  → Remove Duplicates (убирает дубликаты в ПАМЯТИ)
  → Split Out
  → Loop Over Items
```

### Поэтому НЕ НУЖНО проверять через Google Sheets!
- Remove Duplicates убрал дубликаты ДО цикла
- Loop Over Items обрабатывает только уникальные запросы
- Google Sheets (append) просто добавляет их в таблицу
- Никаких лишних запросов к API!

---

## Альтернатива: Если нужно обязательно проверять дубликаты в Google Sheets

Если вы хотите проверять дубликаты именно в Google Sheets (не доверяете Remove Duplicates):

### Вариант A: Прочитать ВСЕ запросы ОДИН раз

**ДО цикла Loop Over Items:**

1. **Добавьте узел Google Sheets (read) ПЕРЕД Loop Over Items:**
   - Operation: `Read`
   - Sheet: `Запросы`
   - Options → Output: "Automatically detect value types"
   - Это прочитает ВСЕ существующие запросы ОДИН раз

2. **Добавьте Code node для фильтрации:**
```javascript
// Получаем существующие запросы из Google Sheets (из предыдущего узла)
const existingQueries = $('Read Google Sheets').all()
  .map(item => item.json['Запросы'])
  .filter(q => q); // убираем пустые

// Получаем новые запросы из Remove Duplicates
const newItems = $('Remove Duplicates').all();

// Фильтруем - оставляем только те, которых нет в таблице
const filtered = newItems.filter(item => {
  const query = item.json.contentArray;
  return !existingQueries.includes(query);
});

console.log(`Existing queries: ${existingQueries.length}`);
console.log(`New unique queries: ${filtered.length}`);

return filtered;
```

3. **Новый поток:**
```
Remove Duplicates
  → Read Google Sheets (читает ВСЕ запросы ОДИН раз)
  → Code (фильтрует дубликаты)
  → Split Out
  → Loop Over Items
  → Google Sheets (append)
```

**Преимущества:**
- ✅ Только ОДИН запрос к Google Sheets (вместо 100)
- ✅ Нет rate limiting
- ✅ Проверяет дубликаты с учётом уже существующих в таблице

---

## Рекомендация

**Используйте ПЕРВОЕ решение** - просто удалите лишние узлы.

Remove Duplicates достаточно для удаления дубликатов в рамках одного выполнения workflow.

Если нужна защита от дубликатов между разными выполнениями - используйте **Вариант A** (читать все запросы один раз).

**НЕ используйте** текущий подход с проверкой каждого запроса отдельно - это гарантированно вызывает rate limiting!
