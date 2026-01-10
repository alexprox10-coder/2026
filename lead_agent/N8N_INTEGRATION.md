# 🔄 Интеграция с n8n

## Готовые Workflow файлы

В проекте есть 2 готовых n8n workflow:

### 1. `n8n_simple_workflow.json` - Простой вариант
Минималистичный workflow с webhook для быстрого старта

### 2. `n8n_lead_agent_workflow.json` - Полная автоматизация
Расширенный workflow с:
- Автоматическим запуском по расписанию (ежедневно)
- Webhook для ручного запуска
- Telegram уведомлениями
- Логированием в Google Sheets
- Обработкой ошибок

## 🚀 Быстрая установка (Простой вариант)

### Шаг 1: Импорт в n8n

1. Откройте n8n
2. Нажмите **"+"** → **"Import from File"**
3. Выберите файл `n8n_simple_workflow.json`
4. Workflow импортирован!

### Шаг 2: Настройка пути к агенту

В узле **"Execute Python Agent"** измените путь:

```bash
cd /home/user/2026/lead_agent && source venv/bin/activate && python3 -c "from agent import LeadCollectionAgent; agent = LeadCollectionAgent(); result = agent.process_message('{{ $json.body.message }}'); print(result)"
```

Замените `/home/user/2026/lead_agent` на ваш реальный путь.

### Шаг 3: Активация

1. Нажмите кнопку **"Active"** в правом верхнем углу
2. Скопируйте URL webhook
3. Готово!

### Шаг 4: Тестирование

Отправьте POST запрос на webhook URL:

```bash
curl -X POST https://your-n8n-instance.com/webhook/lead-agent-simple \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет"}'
```

Или используйте Postman, Insomnia и т.д.

## 🎯 Полная автоматизация

### Импорт

1. Импортируйте `n8n_lead_agent_workflow.json`
2. Настройте credentials

### Необходимые Credentials

#### 1. Telegram Bot API

```
Settings → Credentials → Add Credential → Telegram
```

Вам нужно:
- Bot Token (получите у @BotFather)
- Chat ID (узнайте у @userinfobot)

#### 2. Google Sheets OAuth2

```
Settings → Credentials → Add Credential → Google Sheets OAuth2 API
```

Следуйте инструкциям n8n для настройки OAuth2.

### Настройка узлов

#### 1. Execute Python Agent

Обновите путь к агенту:

```javascript
const agentPath = '/home/user/2026/lead_agent';  // ← Ваш путь
```

#### 2. Telegram Notifications

В узлах "📱 Уведомление START/SUCCESS/ERROR":
- Замените `@your_telegram_channel` на ваш канал/чат
- Выберите ваши Telegram credentials

#### 3. Google Sheets Log

В узле "📊 Лог в Google Sheets":
- Укажите ID вашей таблицы или выберите существующую
- Создайте лист "ЛОГИ" в таблице
- Выберите ваши Google Sheets credentials

### Триггеры

Workflow имеет 2 способа запуска:

#### 1. По расписанию (Schedule Trigger)
Узел "⏰ Ежедневный запуск"
- По умолчанию: каждые 24 часа
- Настройте по вашим нуждам

#### 2. Webhook
Узел "🔗 Webhook"
- Ручной запуск через API
- URL будет доступен после активации

### Активация

1. Сохраните все изменения
2. Активируйте workflow
3. Проверьте работу

## 📡 API Примеры

### Запрос через Webhook

```bash
curl -X POST https://your-n8n.com/webhook/lead-agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Собери стоматологии по Москве"
  }'
```

### Ответ

```json
{
  "success": true,
  "command": "Собери стоматологии по Москве",
  "response": "Создано 8 запросов. Найдено 52 компании...",
  "error": null,
  "timestamp": "2026-01-10T12:34:56.789Z"
}
```

## 🔧 Команды для агента

Примеры команд, которые можно отправлять:

```json
// Привет
{"message": "Привет"}

// Создание запросов
{"message": "Собери автосервисы по Санкт-Петербургу"}

// Проверка статуса
{"message": "Покажи невыполненные запросы"}

// Сбор сайтов
{"message": "Собери сайты компаний"}

// Парсинг данных
{"message": "Собери информацию с сайтов"}

// Генерация писем
{"message": "Создай письма для компаний"}

// Комплексная задача
{"message": "Найди стоматологии в Москве, собери их контакты и создай письма"}
```

## 📊 Структура workflow

### Простой workflow

```
Webhook → Execute Python → Respond
```

### Полный workflow

```
Schedule Trigger ────┐
                     ├─→ Prepare Command → Telegram Start
Webhook ─────────────┘                    ↓
                                          Execute Agent
                                          ↓
                                          Check Success
                                          ├─ Success → Telegram Success → Log to Sheets → Respond
                                          └─ Error → Telegram Error → Log to Sheets → Respond
```

## 🛠️ Кастомизация

### Изменение частоты запуска

В узле "⏰ Ежедневный запуск":

```javascript
{
  "rule": {
    "interval": [
      {
        "field": "hours",
        "hoursInterval": 24  // Измените на нужное значение
      }
    ]
  }
}
```

Варианты:
- `"field": "hours"` - каждые N часов
- `"field": "minutes"` - каждые N минут
- `"field": "days"` - каждые N дней

### Добавление фильтрации

Добавьте узел "IF" для условной обработки:

```javascript
if ($json.message.includes('срочно')) {
  // Приоритетная обработка
}
```

### Интеграция с другими сервисами

Добавьте узлы:
- **Slack** - уведомления в Slack
- **Discord** - уведомления в Discord
- **Email** - отправка результатов по email
- **Airtable** - сохранение в Airtable
- **Notion** - создание записей в Notion

## 🔒 Безопасность

### Защита Webhook

1. **Добавьте аутентификацию**

В узле Webhook включите Authentication:
- Basic Auth
- Header Auth
- JWT

2. **Используйте HTTPS**

Убедитесь что n8n работает через HTTPS.

3. **Ограничьте IP адреса**

Настройте firewall для ограничения доступа.

### Секреты

Используйте n8n Credentials для:
- API ключей
- Токенов
- Паролей

НЕ храните секреты в коде workflow!

## 📝 Логирование

### Google Sheets Logs

Workflow автоматически логирует в лист "ЛОГИ":

| Timestamp | Command | Success | Response | Error |
|-----------|---------|---------|----------|-------|
| 2026-01-10 12:00 | Привет | TRUE | Агент готов... | NULL |
| 2026-01-10 13:00 | Собери компании | TRUE | Найдено 45... | NULL |

### n8n Execution Log

Все выполнения сохраняются в n8n:
- Execution History → просмотр всех запусков
- Фильтрация по статусу (Success/Error)
- Детальная информация о каждом шаге

## 🐛 Отладка

### Тестирование узлов

1. Выберите узел
2. Нажмите "Execute Node"
3. Проверьте вывод

### Просмотр данных

Нажмите на узел для просмотра:
- Input Data - входные данные
- Output Data - выходные данные
- JSON - полный JSON

### Типичные ошибки

#### "Command not found"
Проверьте путь к агенту и virtualenv.

#### "Permission denied"
Дайте права на выполнение:
```bash
chmod +x /home/user/2026/lead_agent/agent.py
```

#### "Module not found"
Активируйте virtualenv перед запуском:
```bash
source /home/user/2026/lead_agent/venv/bin/activate
```

## 🚀 Расширенные сценарии

### Мультиагентная система

Создайте несколько workflow для разных задач:
- Workflow 1: Сбор лидов
- Workflow 2: Парсинг данных
- Workflow 3: Генерация писем
- Workflow 4: Мониторинг

### Интеграция с CRM

```
Agent → Parse Data → Format for CRM → Send to CRM API → Update Status
```

### Цепочка обработки

```
Generate Queries → Collect Sites → Scrape Data → Generate Emails → Send Emails
```

## 📞 Поддержка

Если workflow не работает:

1. Проверьте логи n8n
2. Проверьте логи агента (`logs/agent.log`)
3. Убедитесь что credentials настроены
4. Проверьте пути к файлам
5. Протестируйте агент отдельно

## 🎓 Дополнительные ресурсы

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [n8n Workflow Templates](https://n8n.io/workflows)

---

**Версия:** 1.0.0
**Совместимость:** n8n v1.0+
