# Сессия: Настройка воркфлоу прогрева лидов
**Дата:** 2026-03-08

## Контекст
Настраиваем n8n воркфлоу для автоматического прогрева крипто/недвижимость лидов из Telegram.

## Архитектура воркфлоу

### Ветка 1: Входящий лид
```
Webhook (Новый лид от парсера)
  → Code (Извлечь данные лида)
  → Google Sheets (Сохранить лид в таблицу) [НЕ НАСТРОЕНО]
  → IF (Есть username?)
    → ДА: HTTP Request (Первое сообщение) → Webhook Response
    → НЕТ: Уведомить риелтора
```

### Ветка 2: Обработка ответов
```
Telegram Trigger (Telegram ответы)
  → Code (Обработать ответ)
  → Telegram (Answer Callback)
  → Switch (Роутер по этапу)
    → Спросить бюджет
    → Спросить срочность
    → Спросить комнаты
    → Предложить риелтора
      → Google Sheets (Получить данные лида)
      → HTTP Request (Отправить риелтору)
      → Telegram (Подтверждение пользователю)
```

---

## Что настроили

### 1. Webhook "Новый лид от парсера"
**URL:** `https://n8n.arendadom24.ru/webhook/realty-lead`
**Метод:** POST

**TODO:**
- [ ] Добавить Header Auth (сейчас None — небезопасно)
- [ ] Переключить на Production URL после активации

---

### 2. Code "Извлечь данные лида"
**Рекомендованный код:**
```javascript
// Извлекаем данные лида от парсера
const lead = $input.first().json;

// Валидация — без username или phone не работаем
if (!lead.username && !lead.phone && !lead.user_id) {
  throw new Error('Лид без контактов: нет username, phone или user_id');
}

// Формируем данные для воронки
return [{
  json: {
    // Контактные данные
    leadId: lead.message_id || Date.now(),
    username: lead.username || '',
    phone: lead.phone || '',
    userId: lead.user_id || '',
    chatId: lead.chat_id || lead.user_id || '', // ВАЖНО: для отправки сообщений

    // Исходное сообщение
    originalMessage: lead.text || lead.message || '',
    sourceChannel: lead.channel || lead.source || '',
    messageDate: lead.date || new Date().toISOString(),

    // Статус воронки
    funnelStage: 'new',
    createdAt: new Date().toISOString(),

    // Флаги
    hasUsername: !!lead.username,
    hasPhone: !!lead.phone
  }
}];
```

---

### 3. HTTP Request "Первое сообщение"
**URL:** `https://api.telegram.org/bot{{ $env.TELEGRAM_BOT_TOKEN }}/sendMessage`

**Рекомендованный JSON body:**
```json
{
  "chat_id": "{{ $json.chatId }}",
  "text": "Здравствуйте! 👋\n\nВидел ваше сообщение — вы ищете недвижимость. Могу помочь с подбором!\n\n✅ Работаю напрямую с застройщиками\n✅ Без комиссии для покупателя\n✅ Помогу с ипотекой\n\nХотите узнать подробнее?",
  "parse_mode": "HTML",
  "reply_markup": {
    "inline_keyboard": [
      [
        {"text": "Да, интересно 👍", "callback_data": "interested_yes"},
        {"text": "Не сейчас", "callback_data": "interested_no"}
      ]
    ]
  }
}
```

**ВАЖНО:** `reply_markup` нужно передавать как строку (Stringify) или использовать Telegram ноду вместо HTTP Request.

---

## Что осталось настроить

- [ ] Google Sheets "Сохранить лид в таблицу"
- [ ] Telegram Trigger для ответов
- [ ] Code "Обработать ответ"
- [ ] Switch "Роутер по этапу"
- [ ] Все ноды опроса (бюджет, срочность, комнаты)
- [ ] Логика передачи риелтору
- [ ] Уведомления риелтору

---

## MCP доступ к воркфлоу
Для появления в MCP списке воркфлоу должен:
1. Быть опубликован (активен)
2. Иметь триггер: webhook, form, schedule или chat trigger

---

## Важные замечания
- Парсер должен отправлять `chat_id` (числовой) — без него бот не сможет писать лиду
- Для безопасности webhook нужна аутентификация
- Inline кнопки обязательны для интерактивной воронки
