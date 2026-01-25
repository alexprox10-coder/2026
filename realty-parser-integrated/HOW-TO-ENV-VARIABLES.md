# 🔧 Как настроить Environment Variables

## 📋 Что нужно настроить

Workflow требует **5 переменных окружения**:

| Переменная | Описание | Ваше значение |
|-----------|----------|---------------|
| `WEBHOOK_SECRET` | Секрет для защиты webhook | Сгенерировать (см. ниже) |
| `APIFY_API_TOKEN` | Токен Apify API | Ваш токен (см. ниже) |
| `ALLOWED_CHAT_IDS` | Разрешенные Telegram chat IDs | `7984101063` |
| `GOOGLE_SHEET_ID` | ID Google таблицы | `1IptmHSeKMRMAWB8QzYfyj1vjSJ2Pa0ZdrMq--fMuCW8` |
| `DEFAULT_CHAT_ID` | Telegram chat ID по умолчанию | `7984101063` |

---

## ⚡ Способ 1: Через n8n UI (САМЫЙ ПРОСТОЙ)

### Шаг 1: Откройте Settings

```
n8n UI → Settings (иконка шестеренки слева внизу) → Environments
```

**Или прямой URL:**
```
http://localhost:5678/settings/environments
```
(замените localhost:5678 на ваш адрес n8n)

### Шаг 2: Добавьте переменные

Для каждой переменной:

1. **Нажмите "Add Variable"**

2. **Введите Name и Value:**

#### Переменная 1: WEBHOOK_SECRET
```
Name:  WEBHOOK_SECRET
Value: <вставьте результат команды ниже>
```

**Сгенерируйте secret:**
```bash
openssl rand -hex 32
```
**Пример вывода:** `a7f3c9e1b2d4f6a8c0e2f4b6d8a1c3e5f7b9d1c3e5a7f9b1d3e5c7a9b1d3e5f7`

Скопируйте и вставьте в Value.

#### Переменная 2: APIFY_API_TOKEN
```
Name:  APIFY_API_TOKEN
Value: <ваш Apify API токен>
```

**Где взять Apify токен:**
1. Зайдите в https://console.apify.com/
2. Если нет аккаунта - зарегистрируйтесь (есть бесплатный tier)
3. Settings → Integrations → API Token
4. Скопируйте токен (начинается с `apify_api_`)
5. Вставьте в Value

#### Переменная 3: ALLOWED_CHAT_IDS
```
Name:  ALLOWED_CHAT_IDS
Value: 7984101063
```

#### Переменная 4: GOOGLE_SHEET_ID
```
Name:  GOOGLE_SHEET_ID
Value: 1IptmHSeKMRMAWB8QzYfyj1vjSJ2Pa0ZdrMq--fMuCW8
```

#### Переменная 5: DEFAULT_CHAT_ID
```
Name:  DEFAULT_CHAT_ID
Value: 7984101063
```

3. **Нажмите "Save"** для каждой переменной

### Шаг 3: Проверьте

После добавления всех 5 переменных вы должны видеть:

```
Environment Variables (5)

✅ WEBHOOK_SECRET = a7f3c9e1... (скрыто)
✅ APIFY_API_TOKEN = apify_api_1IOts... (скрыто)
✅ ALLOWED_CHAT_IDS = 7984101063
✅ GOOGLE_SHEET_ID = 1IptmHSeKMRMAWB8QzYfyj1vjSJ2Pa0ZdrMq--fMuCW8
✅ DEFAULT_CHAT_ID = 7984101063
```

### Шаг 4: Перезапустите n8n (ВАЖНО!)

**Если n8n запущен через Docker:**
```bash
docker-compose restart
```

**Если через npm:**
```bash
# Остановите n8n (Ctrl+C)
# Запустите заново
n8n start
```

**Если через PM2:**
```bash
pm2 restart n8n
```

---

## 🐳 Способ 2: Через Docker Compose

Если используете Docker Compose:

### Шаг 1: Откройте docker-compose.yml

```bash
nano docker-compose.yml
# или
vim docker-compose.yml
```

### Шаг 2: Добавьте environment в n8n service

Найдите секцию `services.n8n` и добавьте:

```yaml
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=yourpassword
      # ДОБАВЬТЕ ЭТИ СТРОКИ:
      - WEBHOOK_SECRET=a7f3c9e1b2d4f6a8c0e2f4b6d8a1c3e5f7b9d1c3e5a7f9b1d3e5c7a9b1d3e5f7
      - APIFY_API_TOKEN=your_apify_api_token_here
      - ALLOWED_CHAT_IDS=7984101063
      - GOOGLE_SHEET_ID=1IptmHSeKMRMAWB8QzYfyj1vjSJ2Pa0ZdrMq--fMuCW8
      - DEFAULT_CHAT_ID=7984101063
    volumes:
      - ~/.n8n:/home/node/.n8n
```

### Шаг 3: Сгенерируйте WEBHOOK_SECRET

```bash
openssl rand -hex 32
```

Скопируйте вывод и замените `a7f3c9e1b2d4f6a8c0e2f4b6d8a1c3e5f7b9d1c3e5a7f9b1d3e5c7a9b1d3e5f7` на ваше значение.

### Шаг 4: Сохраните и перезапустите

```bash
# Сохраните файл (Ctrl+O, Enter, Ctrl+X для nano)

# Перезапустите контейнер
docker-compose down
docker-compose up -d
```

---

## 📄 Способ 3: Через .env файл

### Шаг 1: Создайте .env файл

```bash
# В папке с n8n создайте файл .env
cd /path/to/n8n
nano .env
```

### Шаг 2: Добавьте переменные

Вставьте в файл:

```bash
# Workflow Environment Variables
WEBHOOK_SECRET=a7f3c9e1b2d4f6a8c0e2f4b6d8a1c3e5f7b9d1c3e5a7f9b1d3e5c7a9b1d3e5f7
APIFY_API_TOKEN=your_apify_api_token_here
ALLOWED_CHAT_IDS=7984101063
GOOGLE_SHEET_ID=1IptmHSeKMRMAWB8QzYfyj1vjSJ2Pa0ZdrMq--fMuCW8
DEFAULT_CHAT_ID=7984101063
```

**Замените:**
- `WEBHOOK_SECRET` на сгенерированное значение
- `APIFY_API_TOKEN` на ваш токен из https://console.apify.com/

### Шаг 3: Сгенерируйте WEBHOOK_SECRET

```bash
openssl rand -hex 32
```

Замените значение `WEBHOOK_SECRET` на сгенерированное.

### Шаг 4: Загрузите .env при запуске

**Если Docker Compose:**

Добавьте в `docker-compose.yml`:

```yaml
services:
  n8n:
    env_file:
      - .env
```

**Если npm:**

```bash
# Установите dotenv
npm install -g dotenv-cli

# Запустите n8n с .env
dotenv n8n start
```

---

## 🧪 Проверка настройки

### Способ 1: Через n8n UI

```
1. Settings → Environments
2. Должны видеть 5 переменных
```

### Способ 2: Через тестовый workflow

Создайте простой workflow:

```
1. Workflows → Create New
2. Добавьте Code node
3. Code:
   return [{
     json: {
       webhook_secret: $env.WEBHOOK_SECRET ? 'OK' : 'MISSING',
       apify_token: $env.APIFY_API_TOKEN ? 'OK' : 'MISSING',
       allowed_chats: $env.ALLOWED_CHAT_IDS ? 'OK' : 'MISSING',
       sheet_id: $env.GOOGLE_SHEET_ID ? 'OK' : 'MISSING',
       default_chat: $env.DEFAULT_CHAT_ID ? 'OK' : 'MISSING'
     }
   }];
4. Execute Workflow
5. Смотрите output
```

**Должно быть:**
```json
{
  "webhook_secret": "OK",
  "apify_token": "OK",
  "allowed_chats": "OK",
  "sheet_id": "OK",
  "default_chat": "OK"
}
```

---

## ❓ FAQ

### Нужно ли перезапускать n8n после добавления переменных?

**ДА!** Обязательно перезапустите:
- Docker: `docker-compose restart`
- npm: остановите (Ctrl+C) и запустите заново
- PM2: `pm2 restart n8n`

### Где хранятся переменные добавленные через UI?

В базе данных n8n (SQLite или PostgreSQL в зависимости от настройки).

### Можно ли изменить переменные без перезапуска?

**НЕТ**. После изменения переменных нужен перезапуск n8n.

### Безопасно ли хранить токены в переменных?

**ДА**, если:
- Используете n8n UI (переменные в БД)
- .env файл в .gitignore (не коммитится в git)
- Docker secrets для production

### Как скрыть значения переменных в UI?

n8n автоматически скрывает переменные с названиями:
- Содержащими `SECRET`
- Содержащими `TOKEN`
- Содержащими `PASSWORD`

### Что делать если переменная не видна в workflow?

1. Проверьте что переменная добавлена: Settings → Environments
2. Перезапустите n8n
3. Проверьте синтаксис: `$env.VARIABLE_NAME` (без кавычек)

---

## ✅ Готово!

После настройки всех 5 переменных:

1. ✅ Перезапустите n8n
2. ✅ Откройте workflow
3. ✅ Все nodes должны быть зеленые
4. ✅ Можно активировать (Active ON)

**Проблемы?** Смотрите: `/home/user/2026/realty-parser-integrated/TROUBLESHOOTING.md`
