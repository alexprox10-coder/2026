# 🚀 Установка и настройка ChinaLeadBot

## Полное руководство по запуску AI Lead Generation агента

---

## 📋 Предварительные требования

### Необходимые аккаунты:

1. **Telegram Bot** - создайте через @BotFather
2. **Anthropic Claude API** - https://console.anthropic.com
3. **Google Account** - для Google Sheets
4. **n8n** - self-hosted или n8n.cloud
5. **Юкасса** (опционально) - для приема платежей

### Технические требования:

- Python 3.10+
- Node.js 18+ (для n8n)
- 1GB RAM минимум
- VPS/сервер (можно Heroku, Railway, DigitalOcean)

---

## ⚙️ ЭТАП 1: Создание Telegram бота

### 1.1 Создайте бота через BotFather

```
1. Откройте Telegram → найдите @BotFather
2. Отправьте /newbot
3. Введите имя: ChinaLeadBot
4. Введите username: china_lead_bot (или ваш вариант)
5. Сохраните токен: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 1.2 Настройте команды бота

Отправьте @BotFather команду `/setcommands` и выберите вашего бота:

```
start - Начать работу
find - Найти поставщиков
settings - Настройки поиска
status - Статус поисков
leads - Мои лиды
subscribe - Управление подпиской
help - Справка
```

### 1.3 Настройте описание

```
/setdescription - AI-агент для поиска китайских поставщиков. Автоматический поиск, квалификация и контакт с проверенными производителями.

/setabouttext - 🇨🇳🇷🇺 ChinaLeadBot - ваш AI помощник в поиске надежных китайских поставщиков на Alibaba, 1688 и Made-in-China
```

---

## 🤖 ЭТАП 2: Настройка Claude API

### 2.1 Получите API ключ

1. Перейдите на https://console.anthropic.com
2. Зарегистрируйтесь / войдите
3. Перейдите в API Keys
4. Создайте новый ключ → сохраните

### 2.2 Пополните баланс

- Минимум: $5 для тестирования
- Рекомендуется: $20-50 для первого месяца
- Стоимость: ~$0.003 за 1 анализ компании

**Расчет затрат:**
```
100 поисков × 10 лидов × $0.003 = $3/мес
1000 поисков = $30/мес
```

---

## 📊 ЭТАП 3: Настройка Google Sheets

### 3.1 Создайте Google таблицу

1. Перейдите на https://sheets.google.com
2. Создайте новую таблицу "ChinaLeadBot Leads"
3. Создайте лист "Leads" со столбцами:

```
Timestamp | Company | Rating | MOQ | Price | Location | Years |
Email | URL | AI_Score | Recommended | Summary | Pros | Risks
```

4. Скопируйте ID таблицы из URL:
   `https://docs.google.com/spreadsheets/d/[ВАШ_ID]/edit`

### 3.2 Настройте Google API

1. Перейдите на https://console.cloud.google.com
2. Создайте новый проект "ChinaLeadBot"
3. Включите API:
   - Google Sheets API
   - Google Drive API
4. Создайте Service Account:
   - IAM & Admin → Service Accounts → Create
   - Скачайте JSON ключ
   - Сохраните как `config/google_credentials.json`

5. Дайте доступ к таблице:
   - Откройте Google Sheets
   - Share → добавьте email service account
   - Права: Editor

---

## 🔧 ЭТАП 4: Установка n8n

### Вариант A: Docker (рекомендуется)

```bash
# Создайте docker-compose.yml
docker-compose up -d

# n8n будет доступен на http://localhost:5678
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_password
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

### Вариант B: npm установка

```bash
npm install -g n8n
n8n start
```

### 4.1 Импорт workflow

1. Откройте n8n → http://localhost:5678
2. Войдите (admin / your_password)
3. Workflows → Import from File
4. Выберите `workflows/lead_generation.json`
5. Workflow импортирован!

### 4.2 Настройка credentials в n8n

**Claude API:**
1. Credentials → Add Credential
2. Выберите "Anthropic API"
3. Вставьте API Key
4. Save

**Google Sheets:**
1. Credentials → Add Credential
2. Выберите "Google Sheets OAuth2 API"
3. Следуйте инструкциям OAuth
4. Или загрузите Service Account JSON

### 4.3 Настройка workflow

1. Откройте импортированный workflow
2. Найдите узел "💾 Save to Google Sheets"
3. В параметре "documentId" → вставьте ID вашей таблицы
4. В узле "✨ Claude AI" → выберите ваш credential
5. Activate workflow (переключатель вверху)

### 4.4 Получите Webhook URL

1. Откройте узел "🎯 Webhook Trigger"
2. Скопируйте Production URL
3. Пример: `https://your-n8n.com/webhook/lead-search`
4. Сохраните для .env файла

---

## 🐍 ЭТАП 5: Установка Python бота

### 5.1 Клонируйте репозиторий

```bash
cd china-lead-bot
```

### 5.2 Создайте виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 5.3 Установите зависимости

```bash
pip install -r requirements.txt
```

### 5.4 Настройте .env файл

```bash
cp .env.example .env
nano .env
```

Заполните все переменные:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Claude
ANTHROPIC_API_KEY=sk-ant-api03-...

# n8n
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/lead-search

# Google Sheets
GOOGLE_SHEET_ID=ваш_id_таблицы
GOOGLE_CREDENTIALS_FILE=config/google_credentials.json

# Остальное по желанию
```

### 5.5 Запустите бота

```bash
cd bot
python main.py
```

Вы должны увидеть:
```
INFO - ChinaLeadBot started!
```

---

## 💳 ЭТАП 6: Настройка платежей (опционально)

### 6.1 Юкасса

1. Зарегистрируйтесь на https://yookassa.ru
2. Получите Shop ID и Secret Key
3. Добавьте в .env:
```bash
YOOKASSA_SHOP_ID=123456
YOOKASSA_SECRET_KEY=live_...
```

### 6.2 Создайте обработчик платежей

```python
# В bot/payments.py добавьте логику подписок
```

---

## 🧪 ЭТАП 7: Тестирование

### 7.1 Проверьте Telegram бота

1. Найдите бота в Telegram
2. Отправьте /start
3. Должны увидеть приветственное сообщение

### 7.2 Тестовый поиск

1. Нажмите "🔍 Найти поставщиков"
2. Введите категорию: "наушники"
3. Выберите MOQ: "Любой"
4. Выберите цену: "Любая"
5. Подтвердите поиск

### 7.3 Проверьте n8n

1. Откройте n8n → Executions
2. Должно появиться новое выполнение
3. Проверьте что все узлы зеленые ✅

### 7.4 Проверьте Google Sheets

1. Откройте вашу таблицу
2. Должны появиться строки с лидами
3. Проверьте AI анализ в столбце Summary

---

## 🚀 ЭТАП 8: Деплой в продакшн

### Вариант A: VPS (DigitalOcean, Hetzner)

```bash
# 1. Подключитесь к VPS
ssh root@your-server-ip

# 2. Установите Python, Docker
apt update && apt install python3 python3-pip docker.io docker-compose

# 3. Загрузите код
git clone your-repo
cd china-lead-bot

# 4. Запустите n8n через Docker
docker-compose up -d

# 5. Запустите бота через systemd
sudo nano /etc/systemd/system/chinaleadbot.service

[Unit]
Description=ChinaLeadBot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/china-lead-bot/bot
ExecStart=/root/china-lead-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target

# 6. Запустите сервис
sudo systemctl enable chinaleadbot
sudo systemctl start chinaleadbot
sudo systemctl status chinaleadbot
```

### Вариант B: Heroku

```bash
# 1. Установите Heroku CLI
# 2. Создайте приложение
heroku create china-lead-bot

# 3. Добавьте buildpacks
heroku buildpacks:add heroku/python

# 4. Настройте env variables
heroku config:set TELEGRAM_BOT_TOKEN=...
heroku config:set ANTHROPIC_API_KEY=...
# и т.д.

# 5. Деплой
git push heroku main
```

---

## 📈 ЭТАП 9: Мониторинг

### 9.1 Логи бота

```bash
# Просмотр логов
tail -f logs/bot.log

# Или через systemd
journalctl -u chinaleadbot -f
```

### 9.2 Метрики n8n

1. Откройте n8n Dashboard
2. Executions → смотрите статистику
3. Проверяйте ошибки

### 9.3 Google Sheets аналитика

Создайте второй лист "Analytics" с формулами:
```
=QUERY(Leads!A:N, "SELECT COUNT(A) WHERE A IS NOT NULL LABEL COUNT(A) 'Total Leads'")
=AVERAGE(Leads!J:J)  # Средний AI Score
=COUNTIF(Leads!K:K, TRUE)  # Recommended leads
```

---

## 🎯 ЭТАП 10: Первые клиенты

### 10.1 Подготовьте промо-материалы

1. Скриншоты интерфейса
2. Примеры найденных лидов
3. Видео-демо (1 минута)

### 10.2 Где искать клиентов

**Telegram:**
- Каналы предпринимателей
- Группы импортеров
- Чаты по бизнесу с Китаем

**Facebook:**
- Группы "Бизнес с Китаем"
- "Импорт из Китая"
- "Поставщики Alibaba"

**Форумы:**
- ММВБ: importforum.ru
- China-bazar.ru

### 10.3 Первое предложение

```
🇨🇳 Ищете надежных поставщиков в Китае?

ChinaLeadBot - AI-агент который:
✅ Автоматически ищет на Alibaba/1688
✅ Проверяет рейтинги и сертификаты
✅ Генерирует персонализированные запросы
✅ Экономит 10+ часов в неделю

🎁 Первые 5 поисков БЕСПЛАТНО!
👉 @your_bot_username
```

---

## 💰 МОНЕТИЗАЦИЯ

### План доходов (первые 3 месяца)

**Месяц 1:**
```
5 бета-тестеров (бесплатно) → отзывы
3 клиента × 2,990₽ = 8,970₽
```

**Месяц 2:**
```
10 × Basic (2,990₽) = 29,900₽
5 × Pro (7,990₽) = 39,950₽
= 69,850₽/мес
```

**Месяц 3:**
```
20 × среднее 5,000₽ = 100,000₽
+ доп услуги = 30,000₽
= 130,000₽/мес 💰
```

### Стратегия роста

1. **Week 1-2:** Бета-тест, собираем отзывы
2. **Week 3-4:** Запуск платных тарифов
3. **Month 2:** Масштабирование рекламы
4. **Month 3:** Партнерская программа (20% комиссия)

---

## 🆘 Troubleshooting

### Бот не отвечает
```bash
# Проверьте статус
systemctl status chinaleadbot

# Проверьте логи
tail -f logs/bot.log

# Проверьте токен
curl https://api.telegram.org/bot<TOKEN>/getMe
```

### n8n workflow не запускается
- Проверьте что workflow активирован
- Проверьте credentials
- Проверьте webhook URL доступен

### Claude API ошибки
- Проверьте баланс на console.anthropic.com
- Проверьте API key
- Проверьте rate limits

### Google Sheets не обновляется
- Проверьте что service account имеет доступ
- Проверьте credentials в n8n
- Проверьте ID таблицы

---

## 📞 Поддержка

- Email: support@chinaleadbot.ru
- Telegram: @chinaleadbot_support
- Документация: docs/

---

**Готово! Ваш AI Lead Generation агент запущен! 🚀**

Следующий шаг: создайте landing page и начните привлекать клиентов!
