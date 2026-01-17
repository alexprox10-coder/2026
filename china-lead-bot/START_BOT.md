# 🚀 ФИНАЛЬНАЯ НАСТРОЙКА - Осталось 2 шага!

## ✅ ВСЁ ГОТОВО:

- ✅ Python зависимости установлены
- ✅ Виртуальное окружение создано
- ✅ Workflow v3 готов к импорту
- ✅ Конфигурация подготовлена
- ✅ Скрипты проверки настроены

---

## ⚠️ МНЕ НУЖНЫ ОТ ВАС ТОЛЬКО 2 ТОКЕНА:

Я не могу получить их автоматически, поэтому вам нужно:

### 1️⃣ Telegram Bot Token (2 минуты)

**Откройте Telegram → @BotFather:**

```
1. Отправьте: /newbot
2. Имя: ChinaLeadBot (или любое другое)
3. Username: chinaleadbot (или любой другой, заканчивающийся на 'bot')
4. СКОПИРУЙТЕ ТОКЕН (формат: 1234567890:ABCdefGH...)
```

---

### 2️⃣ n8n Webhook URL (3 минуты)

**Откройте n8n (app.n8n.cloud или localhost:5678):**

```
1. Workflows → Import from File
2. Выберите: /home/user/2026/china-lead-bot/workflows/chinaleadbot_workflow_v3.json
3. Нажмите Import
4. Настройте OpenAI credential:
   - Кликните узел "OpenAI Chat Model"
   - Credentials → Create New
   - Вставьте OpenAI API Key (https://platform.openai.com/api-keys)
   - Save
5. АКТИВИРУЙТЕ workflow (переключатель Active вверху)
6. Кликните узел "Webhook Trigger"
7. СКОПИРУЙТЕ "Production URL"
```

---

## 📝 ВАРИАНТ А: Используйте Quick Setup (РЕКОМЕНДУЕТСЯ)

Самый простой способ:

```bash
cd /home/user/2026/china-lead-bot
./quick_setup.sh
```

Скрипт спросит:
- ✅ Telegram Bot Token → Вставьте токен из шага 1
- ✅ n8n Webhook URL → Вставьте URL из шага 2
- ⚪ Google Sheets ID → Нажмите Enter (пропустить)
- ⚪ Anthropic API Key → Нажмите Enter (пропустить)

Скрипт автоматически:
- Создаст .env с вашими данными
- Проверит конфигурацию
- Готов к запуску!

---

## 📝 ВАРИАНТ Б: Ручная настройка

Если предпочитаете вручную:

```bash
cd /home/user/2026/china-lead-bot
nano .env
```

Найдите и замените две строки:

```bash
TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН_ИЗ_ШАГА_1
N8N_WEBHOOK_URL=ВАШ_URL_ИЗ_ШАГА_2
```

Сохраните: `Ctrl+O` → `Enter` → `Ctrl+X`

Проверьте конфигурацию:

```bash
python check_config.py
```

---

## 🎯 ЗАПУСК БОТА

После того как ввели токены:

```bash
cd /home/user/2026/china-lead-bot
source venv/bin/activate
python bot/main.py
```

Вы увидите:

```
INFO - Bot started successfully
INFO - Username: @your_bot_name
INFO - Webhook URL: https://...
INFO - Bot is running...
```

---

## ✅ ТЕСТИРОВАНИЕ

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте `/start`
4. Нажмите **🔍 Найти поставщиков**
5. Введите категорию (например: `wireless headphones`)
6. Выберите MOQ и цену
7. **Получите 10 AI-проанализированных компаний!** 🎉

---

## 🔧 АЛЬТЕРНАТИВА: Дайте мне токены

Если хотите, можете просто дать мне эти два значения:

1. **Telegram Bot Token:** (из @BotFather)
2. **n8n Webhook URL:** (из n8n workflow)

И я сразу настрою .env и запущу проверку!

---

## 💡 СПРАВКА

**Проверить конфигурацию в любой момент:**
```bash
python check_config.py
```

**Посмотреть логи:**
```bash
tail -f bot.log
```

**Остановить бота:**
```bash
Ctrl+C
```

**Документация:**
- Быстрый старт: `QUICKSTART.md`
- Настройка бота: `docs/TELEGRAM_BOT_SETUP.md`
- Настройка workflow: `workflows/WORKFLOW_V3_SETUP.md`

---

## 🎯 ИТОГО:

Осталось только:
1. ✅ Получить Telegram Bot Token (2 мин)
2. ✅ Получить n8n Webhook URL (3 мин)
3. ✅ Запустить `./quick_setup.sh` или отредактировать `.env`
4. ✅ Запустить `python bot/main.py`
5. ✅ Готово! 🚀

---

**Всё остальное уже настроено! Дайте мне эти два токена или настройте сами!** 🎉
