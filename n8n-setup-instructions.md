# Инструкция по импорту и настройке Company Data Assistant в n8n

## 📥 Импорт workflow

1. Откройте n8n в браузере
2. Нажмите на кнопку **"+ Add workflow"** или **"Workflows"** → **"Import from File"**
3. Выберите файл `company-data-assistant-n8n-workflow.json`
4. Workflow будет импортирован со всеми узлами

## 🔧 Необходимые настройки

### 1. Настройка Telegram Bot API

**Создание бота:**
1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Получите **API Token** (формат: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Настройка в n8n:**
1. В n8n перейдите в **Settings** → **Credentials**
2. Нажмите **"Create New"** → **"Telegram API"**
3. Вставьте ваш API Token
4. Сохраните с именем "Telegram Bot API"

### 2. Настройка OpenAI API (для AI Agent)

1. Получите API ключ на [platform.openai.com](https://platform.openai.com/api-keys)
2. В n8n перейдите в **Settings** → **Credentials**
3. Нажмите **"Create New"** → **"OpenAI API"**
4. Вставьте ваш API ключ
5. Сохраните с именем "OpenAI API"

### 3. Подключение учетных данных к узлам

После импорта вам нужно подключить учетные данные к следующим узлам:

- **Telegram Trigger** → выберите "Telegram Bot API"
- **TelegramMessage - Start Notification** → выберите "Telegram Bot API"
- **Telegram Response** → выберите "Telegram Bot API"
- **Greeting Response** → выберите "Telegram Bot API"
- **AI Agent** → выберите "OpenAI API"

## 📊 Интеграция с Google Sheets или Excel

Для работы с Excel файлами вам нужно настроить хранилище данных. Есть несколько вариантов:

### Вариант 1: Google Sheets (рекомендуется)

1. Создайте Google таблицу с листами:
   - **Queries** (колонки: id, topic, city, status, created_at)
   - **Companies** (колонки: id, query_id, name, website, status, created_at)
   - **CompanyData** (колонки: id, company_id, email, phone, description, status, created_at)
   - **EmailDrafts** (колонки: id, company_id, subject, body, created_at)

2. Настройте Google Sheets API:
   - Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
   - Создайте новый проект
   - Включите Google Sheets API
   - Создайте Service Account и скачайте JSON ключ

3. Добавьте credential в n8n:
   - **Settings** → **Credentials** → **"Create New"** → **"Google Sheets OAuth2 API"**
   - Загрузите JSON файл с ключом

### Вариант 2: Локальный Excel через File System

Используйте узел **"Spreadsheet File"** в n8n для работы с локальными Excel файлами.

## 🔨 Замена заглушек на реальную логику

В workflow созданы Code узлы с заглушками. Вам нужно заменить их на реальную логику:

### Execute: Create Queries
```javascript
// Пример интеграции с Google Sheets
const topic = $input.item.json.topic;
const city = $input.item.json.city;

// Здесь добавьте логику записи в Google Sheets
// Используйте узел Google Sheets или HTTP Request

return {
  json: {
    success: true,
    message: `✅ Запросы успешно созданы!\\n\\n📍 Город: ${city}\\n🏷 Тема: ${topic}`,
    topic: topic,
    city: city
  }
};
```

### Execute: Collect Sites
```javascript
// Интеграция с Google Maps API или Serper API
// Пример: используйте HTTP Request узел для вызова API

return {
  json: {
    success: true,
    message: '🔍 Сбор сайтов начат...'
  }
};
```

### Execute: Scrape Data
```javascript
// Используйте HTML Extract узел или HTTP Request
// для парсинга сайтов компаний

return {
  json: {
    success: true,
    message: '📊 Сбор данных начат...'
  }
};
```

## 🚀 Активация workflow

1. Убедитесь, что все учетные данные подключены
2. Нажмите кнопку **"Active"** в правом верхнем углу
3. Workflow начнет прослушивать сообщения из Telegram

## 📱 Тестирование

1. Откройте Telegram и найдите вашего бота
2. Отправьте сообщение "привет" - должна прийти инструкция
3. Попробуйте команды:
   - "Собери запросы по стоматологиям в Москве"
   - "Собери сайты по запросам"
   - "Какие запросы ещё не обработаны?"

## 🔍 Отладка

Если что-то не работает:

1. Проверьте логи в n8n (кнопка **"Executions"**)
2. Убедитесь, что все credentials правильно настроены
3. Проверьте, что Telegram бот активен (зеленая галочка в BotFather)
4. Проверьте баланс OpenAI API

## 📝 Дополнительные рекомендации

### Добавление новых функций

Вы можете добавить дополнительные Tool узлы для новых функций:

1. Добавьте новый узел **"Tool Workflow"**
2. Опишите функцию в поле "description"
3. Создайте соответствующий Execute узел с логикой
4. Подключите к AI Agent

### Улучшение AI Agent

Вы можете настроить параметры модели:
- **Model**: gpt-4o (более точный) или gpt-3.5-turbo (быстрее и дешевле)
- **Temperature**: 0.3-0.7 (для более предсказуемых ответов)
- **Max Tokens**: 1000-2000

### Добавление уведомлений

Добавьте узлы для отправки уведомлений о завершении длительных процессов:
- Email уведомления
- Webhook для интеграции с другими системами
- Запись логов в базу данных

## ⚠️ Важные замечания

1. **Безопасность**: Никогда не делитесь API ключами
2. **Лимиты**: Следите за лимитами API (OpenAI, Google Maps)
3. **Резервные копии**: Регулярно экспортируйте workflow
4. **Тестирование**: Тестируйте на малых объемах данных перед масштабированием

## 🆘 Поддержка

Если возникли проблемы:
- Проверьте документацию n8n: [docs.n8n.io](https://docs.n8n.io)
- Форум сообщества: [community.n8n.io](https://community.n8n.io)
- GitHub Issues: [github.com/n8n-io/n8n](https://github.com/n8n-io/n8n)

---

**Успешного использования! 🚀**
