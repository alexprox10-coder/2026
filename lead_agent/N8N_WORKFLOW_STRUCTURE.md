# ✅ Правильная структура n8n workflow для Lead Agent

## 📊 Схема узлов (nodes):

```
┌─────────────────────────────────────────────────────────────┐
│                    ОСНОВНОЙ ПОТОК                            │
└─────────────────────────────────────────────────────────────┘

1. [Telegram Bot Trigger] ────────→ 2. [Extract Message Data]
                                              │
                                              ↓
                                    3. [Execute Lead Agent]
                                         (CODE node)
                                              │
                                              ↓
                                    4. [Analyze Response]
                                         (CODE node)
                                              │
                                              ↓
                                    5. [Need Buttons?]
                                         (IF node)
                                         ↙        ↘
                        YES ────→ 6. [Send with Buttons]
                        NO  ────→ 7. [Send Simple Message]


┌─────────────────────────────────────────────────────────────┐
│                  ОБРАБОТКА КНОПОК                            │
└─────────────────────────────────────────────────────────────┘

8. [Telegram Callback Handler] ──→ 9. [Process Button Click]
                                         (CODE node)
                                              │
                                              ↓
                                   10. [Answer Callback Query]
                                              │
                                              ↓
                                   11. [Should Execute?]
                                         (IF node)
                                    ↙              ↘
                YES ────→ 12. [Notify Processing]
                                    │
                                    ↓
                          13. [Execute Callback Command]
                                 (CODE node)
                                    │
                                    ↓
                          14. [Send Result]

                NO  ────→ 15. [Send Skip Message]
```

## 🔧 Детальное описание узлов:

### **1. Telegram Bot Trigger**
- **Тип:** `n8n-nodes-base.telegramTrigger`
- **Updates:** `message` ✅
- **Credentials:** Telegram Bot API

### **2. Extract Message Data**
- **Тип:** `n8n-nodes-base.set`
- **Поля:**
  - `user_message` = `{{ $json.message.text }}`
  - `chat_id` = `{{ $json.message.chat.id }}`
  - `user_name` = `{{ $json.message.from.first_name }}`

### **3. Execute Lead Agent** (CODE)
- **Тип:** `n8n-nodes-base.code`
- **Код:**
```javascript
const { exec } = require('child_process');
const agentPath = '/home/user/2026/lead_agent'; // ← ВАШ ПУТЬ!

const pythonScript = `
import sys
import json
sys.path.append('${agentPath}')

from agent import LeadCollectionAgent
agent = LeadCollectionAgent()
response = agent.process_message("${escapedMessage}")
print(json.dumps({"success": True, "response": response}))
`;

// Выполнение через bash
```

### **4. Analyze Response** (CODE)
- **Тип:** `n8n-nodes-base.code`
- **Логика:**
```javascript
// Проверяет текст ответа на ключевые слова
if (response.includes('сайт') && response.includes('собран')) {
  buttonType = 'collect_data';
}
if (response.includes('данные собраны')) {
  buttonType = 'generate_letters';
}
```

### **5. Need Buttons?** (IF)
- **Условие:** `$json.needs_buttons === true`
- **TRUE:** → Send with Buttons
- **FALSE:** → Send Simple Message

### **6. Send with Buttons**
- **Тип:** `n8n-nodes-base.telegram`
- **Reply Markup:** `inlineKeyboard`
- **Кнопки:**
  - `collect_data` → "✅ Собрать контактные данные"
  - `generate_letters` → "📧 Создать КП"
  - `skip` → "❌ Пропустить"

### **7. Send Simple Message**
- **Тип:** `n8n-nodes-base.telegram`
- Просто отправляет текст без кнопок

### **8. Telegram Callback Handler**
- **Тип:** `n8n-nodes-base.telegramTrigger`
- **Updates:** `callback_query` ✅
- Слушает нажатия на кнопки

### **9. Process Button Click** (CODE)
- Преобразует `callback_data` в команды:
  - `collect_data` → "Собери информацию с сайтов"
  - `generate_letters` → "Создай коммерческие предложения"

### **10. Answer Callback Query**
- **Тип:** `n8n-nodes-base.telegram`
- **Query ID:** `{{ $json.callback_query_id }}`
- Подтверждает получение клика

### **11. Should Execute?** (IF)
- Проверяет: `command !== 'skip' && command !== 'complete'`

### **12. Notify Processing**
- Отправляет: "⏳ Выполняю команду..."

### **13. Execute Callback Command** (CODE)
- Запускает агента с командой из кнопки
- Аналогично узлу #3

### **14. Send Result**
- Отправляет результат выполнения

### **15. Send Skip Message**
- Отправляет: "✅ Операция пропущена"

---

## 🎯 Критически важные настройки:

### ✅ **Что ОБЯЗАТЕЛЬНО должно быть:**

1. **ДВА Telegram Trigger:**
   - Первый для `message` (текстовые сообщения)
   - Второй для `callback_query` (нажатия кнопок)

2. **Два CODE узла с агентом:**
   - Один для основных сообщений
   - Один для команд от кнопок

3. **Путь к агенту в ДВУХ местах:**
   ```javascript
   const agentPath = '/home/user/2026/lead_agent';
   ```

4. **Все Telegram узлы с одним credential:**
   - Один и тот же Telegram Bot Token

5. **IF узлы для условий:**
   - "Need Buttons?" - проверка нужны ли кнопки
   - "Should Execute?" - проверка нужно ли выполнять

---

## ❌ Частые ошибки:

1. **Забыли второй Telegram Trigger для callback_query**
   → Кнопки не работают

2. **Разные credentials в узлах**
   → Ошибки отправки

3. **Неправильный путь к агенту**
   → "Module not found"

4. **Не экранированы кавычки в сообщении**
   → Ошибки выполнения Python

5. **Не настроен Answer Callback Query**
   → Telegram показывает ошибку при клике

---

## 🧪 Как проверить работоспособность:

### **Тест 1: Простое сообщение**
```
Вы → Боту: "Привет"
Ожидаем: Ответ от агента без кнопок
```

### **Тест 2: Сбор сайтов**
```
Вы: "Собери агентства недвижимости Москва"
Ожидаем:
1. Агент создаёт запросы
2. Парсит Google Maps
3. Отвечает с кнопкой [✅ Собрать контактные данные]
```

### **Тест 3: Нажатие кнопки**
```
Вы: Нажимаете [✅ Собрать контактные данные]
Ожидаем:
1. "⏳ Выполняю команду..."
2. Агент парсит сайты
3. Отвечает с кнопкой [📧 Создать КП]
```

---

## 📋 Чеклист перед запуском:

- [ ] Создан Telegram Bot через @BotFather
- [ ] Токен бота добавлен в n8n Credentials
- [ ] Python агент установлен и работает
- [ ] Путь к агенту указан правильно (в ДВУХ узлах!)
- [ ] Все Telegram узлы используют один credential
- [ ] Два Telegram Trigger (message + callback_query)
- [ ] Workflow активирован (кнопка Active)
- [ ] Тестовое сообщение боту отправлено

---

Покажите мне ваш JSON или опишите что у вас настроено, и я скажу правильно ли! 🚀
