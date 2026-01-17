# 🚀 ChinaLeadBot - Быстрый Старт

## За 5 минут до работающего бота!

### 📋 Что у вас должно быть:

- [ ] n8n (cloud или self-hosted)
- [ ] Python 3.8+ установлен
- [ ] Telegram аккаунт
- [ ] OpenAI API key (для n8n workflow)

---

## ⚡ Метод 1: Автоматическая установка (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Запустите setup скрипт

```bash
cd /home/user/2026/china-lead-bot
./quick_setup.sh
```

Скрипт спросит:
1. **Telegram Bot Token** - получите от @BotFather
2. **n8n Webhook URL** - скопируйте из активного workflow v3
3. **Google Sheets ID** (опционально)
4. **Anthropic API Key** (опционально)

### Шаг 2: Запустите бота

```bash
source venv/bin/activate
python bot/main.py
```

**Готово!** Найдите бота в Telegram и отправьте `/start`

---

## 🔧 Метод 2: Ручная настройка

### Шаг 1: Создайте Telegram бота

1. Откройте **@BotFather** в Telegram
2. Отправьте `/newbot`
3. Придумайте имя и username
4. **Скопируйте токен**

### Шаг 2: Настройте n8n workflow

1. Откройте n8n
2. **Import workflow:**
   ```
   china-lead-bot/workflows/chinaleadbot_workflow_v3.json
   ```
3. **Настройте OpenAI credential** в узле "OpenAI Chat Model"
4. **Настройте Google Sheets** (опционально)
5. **АКТИВИРУЙТЕ workflow** (переключатель Active)
6. Кликните "Webhook Trigger" → **Скопируйте Production URL**

### Шаг 3: Создайте .env файл

```bash
cd /home/user/2026/china-lead-bot
cp .env.example .env
nano .env
```

Заполните обязательные поля:

```bash
TELEGRAM_BOT_TOKEN=ваш_токен_от_botfather
N8N_WEBHOOK_URL=ваш_production_url_из_n8n
```

Сохраните: `Ctrl+O` → `Enter` → `Ctrl+X`

### Шаг 4: Установите зависимости

```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 5: Проверьте конфигурацию

```bash
python check_config.py
```

Если всё ✓ зелёное - готово к запуску!

### Шаг 6: Запустите бота

```bash
python bot/main.py
```

Вы должны увидеть:

```
INFO - Bot started successfully
INFO - Username: @your_bot_name
INFO - Bot is running...
```

---

## ✅ Тестирование

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте `/start`
4. Нажмите **🔍 Найти поставщиков**
5. Введите категорию: `wireless headphones`
6. Выберите MOQ и цену
7. Получите результаты! 🎉

---

## 🔄 Архитектура

```
┌─────────────┐
│ Telegram    │
│ User        │
└──────┬──────┘
       │ /start, /search
       ↓
┌─────────────┐
│ Python Bot  │  ← bot/main.py (запущен локально)
└──────┬──────┘
       │ HTTP POST
       ↓
┌─────────────┐
│ n8n         │  ← workflow v3 (активирован)
│ Workflow    │
└──────┬──────┘
       │
       ├─→ Generate Suppliers Data
       ├─→ AI Agent + OpenAI GPT-4
       ├─→ Save to Google Sheets
       └─→ Return JSON
       ↓
┌─────────────┐
│ Python Bot  │
│ (Response)  │
└──────┬──────┘
       │ Formatted results
       ↓
┌─────────────┐
│ Telegram    │
│ User        │
└─────────────┘
```

---

## 🐛 Проблемы?

### Бот не запускается

```bash
# Проверьте конфигурацию
python check_config.py

# Проверьте зависимости
pip install -r requirements.txt

# Проверьте логи
tail -f bot.log
```

### Ошибка при поиске

1. ✅ Workflow **Active** в n8n?
2. ✅ OpenAI credential настроен?
3. ✅ Баланс OpenAI положительный?
4. ✅ Webhook URL правильный?

Запустите:
```bash
python check_config.py
```

### Timeout при поиске

Увеличьте timeout в `bot/main.py` строка 315:

```python
response = requests.post(
    N8N_WEBHOOK_URL,
    json=search_params,
    timeout=300  # Было 120, увеличьте до 300
)
```

---

## 📚 Полная документация

- **Настройка бота:** [docs/TELEGRAM_BOT_SETUP.md](docs/TELEGRAM_BOT_SETUP.md)
- **Настройка workflow:** [workflows/WORKFLOW_V3_SETUP.md](workflows/WORKFLOW_V3_SETUP.md)
- **Установка:** [docs/INSTALLATION.md](docs/INSTALLATION.md)
- **Монетизация:** [docs/MONETIZATION_STRATEGY.md](docs/MONETIZATION_STRATEGY.md)

---

## 🚀 Production деплой

### Запуск в фоне (screen)

```bash
screen -S chinaleadbot
source venv/bin/activate
python bot/main.py

# Отключиться: Ctrl+A, затем D
# Вернуться: screen -r chinaleadbot
```

### Запуск в фоне (nohup)

```bash
nohup python bot/main.py > bot.log 2>&1 &

# Проверить
ps aux | grep main.py

# Остановить
pkill -f main.py
```

### Автозапуск (systemd)

См. подробную инструкцию в [docs/TELEGRAM_BOT_SETUP.md](docs/TELEGRAM_BOT_SETUP.md)

---

## 🎯 Чеклист готовности

```
☐ Создан бот через @BotFather
☐ Получен токен
☐ Workflow v3 импортирован в n8n
☐ OpenAI credential настроен
☐ Workflow активирован (Active)
☐ Webhook URL скопирован
☐ .env файл создан и заполнен
☐ Python зависимости установлены
☐ check_config.py прошел успешно
☐ Бот запущен без ошибок
☐ Бот отвечает на /start
☐ Поиск работает
☐ Готов! 🚀
```

---

## 💰 Следующие шаги

После успешного запуска:

1. **Протестируйте все функции:**
   - /start - приветствие
   - Поиск поставщиков
   - Просмотр баланса
   - Помощь

2. **Настройте продакшн:**
   - Real scraping (см. `workflows/REAL_SCRAPING_NODE.md`)
   - Production деплой (systemd/docker)
   - Мониторинг и логи

3. **Начните монетизацию:**
   - Добавьте платежную систему (YooKassa)
   - Настройте подписки
   - Привлеките первых пользователей

4. **Масштабирование:**
   - Оптимизация OpenAI расходов
   - Кэширование результатов
   - Аналитика и метрики

---

## 🎉 Готово!

Ваш AI-агент для поиска китайских поставщиков готов к работе!

**Вопросы?** См. [docs/TELEGRAM_BOT_SETUP.md](docs/TELEGRAM_BOT_SETUP.md) для полной инструкции.

**Удачи! 🚀**
