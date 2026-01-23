# 🚀 Быстрая установка Telegram-бота для парсера недвижимости

## ✅ Что исправлено в этой версии:

1. ✅ **Inline-клавиатура работает правильно** (кнопки отображаются)
2. ✅ **Команда /start обрабатывается корректно**
3. ✅ **Убрана проблемная нода "Check Back"**
4. ✅ **Исправлены все URL** (используется `https://alex024.app.n8n.cloud`)
5. ✅ **Правильный формат кнопок** с callback_data

---

## 📥 Шаг 1: Импорт workflow

1. Скачайте файл: **telegram_realtor_bot_fixed.json**
2. В n8n откройте меню (≡) → **Import from File**
3. Выберите скачанный файл
4. Нажмите **Import**

---

## 🤖 Шаг 2: Создание Telegram бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду: `/newbot`
3. Введите имя бота: `Realtor Parser Bot`
4. Введите username: `realtor_parser_bot` (или любой свободный)
5. **Скопируйте токен** (формат: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

## 🔑 Шаг 3: Создание credentials в n8n

### 3.1 Telegram API Credentials

1. В n8n откройте **Credentials** (🔑 в левом меню)
2. Нажмите **Add Credential** → найдите **Telegram API**
3. Заполните:
   - **Name:** `Telegram Bot API`
   - **Access Token:** [вставьте токен от BotFather]
4. Нажмите **Save**
5. **ВАЖНО:** Скопируйте **ID** этого credential (например: `1`, `2`, `abc123`)

### 3.2 n8n API Credentials

1. В n8n откройте **Settings** (⚙️) → **API**
2. Нажмите **Create an API Key**
3. Введите название: `Telegram Bot API Key`
4. **Скопируйте созданный ключ** (формат: `n8n_api_xxxxxxxxxxxxx`)

5. Вернитесь в **Credentials** → **Add Credential** → **n8n API**
6. Заполните:
   - **Name:** `n8n API`
   - **API Key:** [вставьте скопированный ключ]
   - **Base URL:** `https://alex024.app.n8n.cloud`
7. Нажмите **Save**
8. **ВАЖНО:** Скопируйте **ID** этого credential

---

## 🔧 Шаг 4: Замена Credential IDs в workflow

### Найдите и замените во ВСЕХ нодах:

**Для Telegram нод (18 нод):**
- Найдите: `"id": "REPLACE_WITH_YOUR_TELEGRAM_CREDENTIALS_ID"`
- Замените на: `"id": "1"` (или ваш ID Telegram credentials)

**Ноды с Telegram:**
1. Telegram Trigger
2. Unauthorized
3. Send Welcome
4. Avito Success
5. CIAN Success
6. Both Success
7. Schedule Enabled
8. Schedule Disabled
9. Help Message
10. Feedback Prompt
11. Schedule Settings
12. Interval Updated
13. Feedback Received
14. Forward to Admin

**Для n8n API нод (6 нод):**
- Найдите: `"id": "REPLACE_WITH_YOUR_N8N_API_CREDENTIALS_ID"`
- Замените на: `"id": "2"` (или ваш ID n8n API credentials)

**Ноды с n8n API:**
1. Run Avito Parser
2. Run CIAN Parser
3. Run Both Parsers
4. Enable Schedule
5. Disable Schedule
6. Update Schedule

### Как это сделать быстро:

**Метод 1: В редакторе кода**
1. Откройте workflow в n8n
2. Нажмите **三** (меню) → **Download**
3. Откройте скачанный JSON в текстовом редакторе
4. Используйте **Найти и заменить** (Ctrl+H):
   - Найти: `REPLACE_WITH_YOUR_TELEGRAM_CREDENTIALS_ID`
   - Заменить на: `1` (ваш ID)
5. Повторите для `REPLACE_WITH_YOUR_N8N_API_CREDENTIALS_ID`
6. Сохраните файл
7. В n8n: **Import from File** (импортируйте заново)

**Метод 2: Вручную в каждой ноде**
1. Откройте каждую ноду
2. В секции **Credentials** выберите нужный credential из списка
3. Сохраните ноду

---

## 🌐 Шаг 5: Проверка URL

Убедитесь, что во всех HTTP Request нодах используется правильный URL:

**Ваш n8n:** `https://alex024.app.n8n.cloud`

Если ваш n8n на другом домене, замените URL в нодах:
- Run Avito Parser → URL: `https://ВАШ_ДОМЕН/api/v1/workflows/iXAfySHKjPj3DPcm/run`
- Run CIAN Parser → URL: `https://ВАШ_ДОМЕН/api/v1/workflows/iXAfySHKjPj3DPcm/run`
- Run Both Parsers → URL: `https://ВАШ_ДОМЕН/api/v1/workflows/iXAfySHKjPj3DPcm/run`
- Enable Schedule → URL: `https://ВАШ_ДОМЕН/api/v1/workflows/iXAfySHKjPj3DPcm`
- Disable Schedule → URL: `https://ВАШ_ДОМЕН/api/v1/workflows/iXAfySHKjPj3DPcm`
- Update Schedule → URL: `https://ВАШ_ДОМЕН/api/v1/workflows/iXAfySHKjPj3DPcm`

---

## 🎯 Шаг 6: Проверка ID главного workflow

Убедитесь, что ID вашего главного workflow парсера правильный:

Текущий ID в боте: `iXAfySHKjPj3DPcm`

Если ваш workflow имеет другой ID:
1. Откройте главный workflow парсера
2. Посмотрите в URL: `/workflow/{ID}`
3. Замените `iXAfySHKjPj3DPcm` на ваш ID во всех HTTP Request нодах

---

## ✅ Шаг 7: Активация workflow

1. Нажмите **Save** (Ctrl+S / Cmd+S)
2. Переключите **Active** в правом верхнем углу на ВКЛ (зелёный)
3. Убедитесь, что появилась надпись **"Workflow is active"**

---

## 🧪 Шаг 8: Тестирование

1. Откройте вашего бота в Telegram
2. Отправьте команду: `/start`
3. **Должно появиться:**
   - Приветственное сообщение
   - **6 кнопок** в inline-клавиатуре:
     - 🟢 Парсить только Avito
     - 🔵 Парсить только ЦИАН
     - 🟣 Парсить оба источника
     - ⏰ Настроить авто-парсинг
     - ▶️ Включить / ⏸️ Выключить
     - ❓ Помощь / 💬 Отзыв

4. Попробуйте нажать на кнопки

---

## ❌ Если кнопки НЕ появились:

### Проверьте ноду "Send Welcome":

1. Откройте ноду **Send Welcome**
2. Прокрутите вниз до **Additional Fields**
3. Проверьте, что:
   - ✅ **Parse Mode** = `Markdown`
   - ✅ **Reply Markup** = `Inline Keyboard`
   - ✅ **Inline Keyboard** содержит 6 строк (Rows)
   - ✅ Каждая кнопка имеет **Text** и **Callback Data**

### Пример правильной настройки кнопки:

**Row 1:**
- Button Text: `🟢 Парсить только Avito`
- Additional Fields → Callback Data: `parse_avito`

---

## 🔍 Проверка работы HTTP запросов:

После нажатия кнопки "Парсить только Avito":

1. В n8n откройте **Executions** (слева)
2. Найдите последнее выполнение бота
3. Нажмите на него → просмотрите ноды
4. Проверьте ноду **Run Avito Parser**:
   - Должен быть статус ✅ Success
   - В OUTPUT должен быть ответ от API n8n

**Если ошибка:**
- Проверьте n8n API Credentials
- Проверьте, что API Key правильный
- Проверьте Base URL

---

## 📝 Чек-лист установки:

- [ ] Импортирован файл `telegram_realtor_bot_fixed.json`
- [ ] Создан бот в @BotFather, получен токен
- [ ] Создан Telegram API credential в n8n
- [ ] Создан n8n API Key в Settings → API
- [ ] Создан n8n API credential в n8n
- [ ] Заменены все `REPLACE_WITH_YOUR_TELEGRAM_CREDENTIALS_ID`
- [ ] Заменены все `REPLACE_WITH_YOUR_N8N_API_CREDENTIALS_ID`
- [ ] Проверены URL в HTTP Request нодах
- [ ] Проверен ID главного workflow (`iXAfySHKjPj3DPcm`)
- [ ] Workflow активирован (Active = ON)
- [ ] Протестирована команда /start
- [ ] Появились кнопки в боте
- [ ] Протестированы кнопки парсинга

---

## 🆘 Если что-то не работает:

### Проблема: Бот не отвечает на /start

**Решение:**
1. Проверьте, что workflow активен (зелёный индикатор)
2. Откройте **Executions** → посмотрите ошибки
3. Проверьте Telegram credentials

### Проблема: Кнопки не появляются

**Решение:**
1. Откройте ноду "Send Welcome"
2. Проверьте настройки Inline Keyboard
3. Убедитесь, что Reply Markup = "Inline Keyboard"

### Проблема: Ошибка "access denied" при нажатии кнопок

**Решение:**
1. Проверьте, что ваш User ID = `7984101063`
2. Если другой ID, замените в ноде "Check User ID"

### Проблема: HTTP Request возвращает ошибку

**Решение:**
1. Проверьте n8n API credentials
2. Проверьте Base URL
3. Проверьте, что API Key правильный
4. Проверьте ID главного workflow

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте **Executions** в n8n для просмотра ошибок
2. Проверьте все пункты чек-листа выше
3. Убедитесь, что все credentials настроены правильно

---

**Версия:** 1.1 (исправленная)
**Дата:** 23 января 2026
**Автор:** Claude AI

**Изменения в v1.1:**
- ✅ Исправлена inline-клавиатура
- ✅ Исправлена обработка /start
- ✅ Убрана проблемная нода Check Back
- ✅ Обновлены URL для alex024.app.n8n.cloud
- ✅ Исправлен формат кнопок (additionalFields → callbackData)
