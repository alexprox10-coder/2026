# 📊 НАСТРОЙКА GOOGLE SHEETS ДЛЯ CHINALEADBOT

## Полная инструкция создания таблицы для лидов

---

## 🚀 БЫСТРЫЙ СТАРТ (5 минут)

### Вариант 1: Создать таблицу вручную

#### Шаг 1: Создайте новую таблицу

1. Перейдите на https://sheets.google.com
2. Нажмите **"+ Пусто"** (создать новую таблицу)
3. Назовите таблицу: **"ChinaLeadBot - Leads Database"**

#### Шаг 2: Создайте структуру

**Добавьте следующие столбцы в первую строку:**

| A | B | C | D | E | F | G | H | I | J | K | L | M | N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Timestamp | Company | Rating | MOQ | Price | Location | Years | Email | URL | AI_Score | Recommended | Summary | Pros | Risks |

**Форматирование заголовков:**
1. Выделите первую строку
2. **Формат → Текст → Жирный**
3. **Вид → Закрепить → 1 строка**
4. **Формат → Цвет заливки → Светло-серый**

#### Шаг 3: Настройте форматы столбцов

**Столбец A (Timestamp):**
```
Формат → Число → Дата и время
```

**Столбец C (Rating):**
```
Формат → Число → Число (2 знака после запятой)
```

**Столбец J (AI_Score):**
```
Формат → Число → Число (целое)
```

**Столбец K (Recommended):**
```
Формат → Число → Флажок
```

#### Шаг 4: Добавьте пример данных

Вставьте в строку 2 (для примера):

```
2026-01-17 10:00:00	Shenzhen Tech Electronics Co., Ltd.	4.8	100 pieces	$5.50	Guangdong, China	12	sales@shenzhen-tech.com	https://shenzhen-tech.en.alibaba.com	9	TRUE	Надежная компания с высоким рейтингом	высокий рейтинг, большой опыт, verified	высокий MOQ
```

---

### Вариант 2: Импортировать готовый шаблон

#### Шаг 1: Скачайте CSV шаблон

Файл находится по пути:
```
/home/user/2026/china-lead-bot/templates/leads_template.csv
```

#### Шаг 2: Импортируйте в Google Sheets

1. Откройте https://sheets.google.com
2. **Файл → Импортировать**
3. Загрузите `leads_template.csv`
4. Параметры импорта:
   - Разделитель: **Запятая**
   - Кодировка: **UTF-8**
5. Нажмите **"Импортировать данные"**

---

## 🔑 ПОЛУЧЕНИЕ ID ТАБЛИЦЫ

После создания таблицы:

1. **Скопируйте URL** из адресной строки:
   ```
   https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit
                                          ^^^^^^^^^^^^
                                          Это ваш ID
   ```

2. **ID таблицы** - это часть между `/d/` и `/edit`

3. **Сохраните ID** для использования в .env файле

**Пример:**
```
URL: https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit
ID:  1a2b3c4d5e6f7g8h9i0j
```

---

## 🔐 НАСТРОЙКА ДОСТУПА (ВАЖНО!)

### Метод 1: Через Service Account (Рекомендуется для продакшна)

#### Шаг 1: Создайте Google Cloud проект

1. Перейдите на https://console.cloud.google.com
2. **Создать проект** → Назовите "ChinaLeadBot"
3. Выберите созданный проект

#### Шаг 2: Включите Google Sheets API

1. **APIs & Services → Library**
2. Найдите **"Google Sheets API"**
3. Нажмите **Enable**
4. Также включите **"Google Drive API"**

#### Шаг 3: Создайте Service Account

1. **APIs & Services → Credentials**
2. **Create Credentials → Service Account**
3. Заполните:
   - Name: `chinaleadbot-service`
   - Description: `Service account for ChinaLeadBot n8n integration`
4. Нажмите **Create and Continue**
5. Role: выберите **Editor**
6. Нажмите **Done**

#### Шаг 4: Создайте ключ

1. Найдите созданный Service Account в списке
2. Нажмите на него
3. **Keys → Add Key → Create new key**
4. Выберите **JSON**
5. Нажмите **Create**
6. **Сохраните файл** как `google_credentials.json`

#### Шаг 5: Дайте доступ к таблице

1. Откройте скачанный `google_credentials.json`
2. Найдите строку `"client_email"`:
   ```json
   "client_email": "chinaleadbot-service@project.iam.gserviceaccount.com"
   ```
3. **Скопируйте этот email**
4. Откройте вашу Google таблицу
5. Нажмите **"Настройки доступа"** (кнопка Share)
6. Вставьте скопированный email
7. Права: **Редактор**
8. Снимите галочку **"Уведомить пользователей"**
9. Нажмите **"Готово"**

#### Шаг 6: Установите credentials в проект

```bash
# Скопируйте JSON файл в проект
cp ~/Downloads/google_credentials.json /home/user/2026/china-lead-bot/config/

# Обновите .env
echo "GOOGLE_CREDENTIALS_FILE=config/google_credentials.json" >> .env
```

---

### Метод 2: Через OAuth (Проще для тестирования)

#### В n8n:

1. **Credentials → Add Credential**
2. Выберите **"Google Sheets OAuth2 API"**
3. Нажмите **"Connect my account"**
4. Войдите через Google
5. Разрешите доступ
6. **Save**

**Плюсы:**
- ✅ Очень быстро (2 минуты)
- ✅ Не нужен Service Account

**Минусы:**
- ❌ Токен может истечь
- ❌ Не подходит для продакшна

---

## 📋 СТРУКТУРА ТАБЛИЦЫ - ДЕТАЛИ

### Описание столбцов:

| Столбец | Тип | Описание | Пример |
|---------|-----|----------|--------|
| **Timestamp** | DateTime | Время добавления лида | 2026-01-17T10:30:00Z |
| **Company** | Text | Название компании | Shenzhen Tech Electronics Co. |
| **Rating** | Number | Рейтинг 0-5 | 4.8 |
| **MOQ** | Text | Минимальный заказ | 100 pieces |
| **Price** | Text | Цена за единицу | $5.50 |
| **Location** | Text | Локация | Guangdong, China |
| **Years** | Number | Лет в бизнесе | 12 |
| **Email** | Text | Контактный email | sales@company.com |
| **URL** | URL | Ссылка на компанию | https://company.alibaba.com |
| **AI_Score** | Number | AI оценка 1-10 | 9 |
| **Recommended** | Boolean | Рекомендуется? | TRUE/FALSE |
| **Summary** | Text | AI резюме на русском | Надежная компания... |
| **Pros** | Text | Преимущества | высокий рейтинг, опыт |
| **Risks** | Text | Риски | высокий MOQ |

---

## 🎨 ДОПОЛНИТЕЛЬНЫЕ УЛУЧШЕНИЯ (Опционально)

### 1. Условное форматирование

**Для столбца AI_Score:**

1. Выделите столбец J (AI_Score)
2. **Формат → Условное форматирование**
3. Добавьте правила:
   - **Если >= 8:** Зеленый фон
   - **Если 5-7:** Желтый фон
   - **Если < 5:** Красный фон

**Для столбца Recommended:**

1. Выделите столбец K
2. **Формат → Условное форматирование**
3. **Если TRUE:** Зеленый фон

### 2. Фильтры

1. Выделите первую строку (заголовки)
2. **Данные → Создать фильтр**

Теперь можно фильтровать по:
- Рейтингу > 4.5
- AI_Score > 7
- Recommended = TRUE

### 3. Сортировка по умолчанию

1. **Данные → Сортировать диапазон**
2. Сортировать по: **AI_Score**
3. Порядок: **От Я до А** (сначала лучшие)

### 4. Добавьте Dashboard лист

Создайте второй лист "Dashboard" с формулами:

**Ячейка A1:**
```
=QUERY(Leads!A:N, "SELECT COUNT(A) WHERE A IS NOT NULL LABEL COUNT(A) 'Total Leads'")
```

**Ячейка A3:**
```
=AVERAGE(Leads!J:J)
```
Label: "Average AI Score"

**Ячейка A5:**
```
=COUNTIF(Leads!K:K, TRUE)
```
Label: "Recommended Leads"

---

## 🔧 НАСТРОЙКА В N8N

После создания таблицы и получения доступа:

### В workflow узле "💾 Save to Google Sheets":

1. **Document ID**: Вставьте ID вашей таблицы
   ```
   1a2b3c4d5e6f7g8h9i0j
   ```

2. **Sheet Name**: `Leads` (или как назвали лист)

3. **Credentials**: Выберите созданный credential

4. **Columns**: Уже настроены в workflow ✅

5. **Matching Columns**: `Company` (чтобы не дублировать)

---

## 🧪 ТЕСТИРОВАНИЕ

### Тест 1: Ручная вставка

1. Откройте таблицу
2. Добавьте строку вручную
3. Проверьте что форматы применились

### Тест 2: Через n8n

1. Запустите workflow в n8n
2. Выполните тестовый поиск
3. Проверьте что данные появились в таблице

### Тест 3: Проверка прав

1. Попробуйте открыть таблицу в инкогнито
2. Должен быть доступ (если дали права Service Account)

---

## 📊 ГОТОВАЯ ССЫЛКА НА ШАБЛОН

### Скачать CSV шаблон:

```bash
# Файл находится по пути:
/home/user/2026/china-lead-bot/templates/leads_template.csv

# Или скопируйте в текущую директорию:
cp /home/user/2026/china-lead-bot/templates/leads_template.csv ~/
```

### Структура для копирования:

```
Timestamp | Company | Rating | MOQ | Price | Location | Years | Email | URL | AI_Score | Recommended | Summary | Pros | Risks
```

---

## ⚡ БЫСТРЫЙ ЧЕКЛИСТ

```
☐ Создана таблица в Google Sheets
☐ Добавлены все 14 столбцов
☐ Скопирован ID таблицы
☐ Создан Service Account (или OAuth)
☐ Дан доступ к таблице
☐ Credentials добавлены в n8n
☐ ID таблицы добавлен в workflow
☐ Протестирована вставка данных
☐ ID добавлен в .env файл
```

---

## 🆘 TROUBLESHOOTING

### Ошибка: "Insufficient Permission"

**Решение:**
- Проверьте что Service Account email добавлен в настройки доступа таблицы
- Права должны быть "Редактор" (не "Читатель")

### Ошибка: "Sheet not found"

**Решение:**
- Проверьте что имя листа точно "Leads" (с заглавной L)
- Или измените в workflow на ваше название

### Данные не вставляются

**Решение:**
- Проверьте что Google Sheets API включен
- Проверьте credential в n8n (зеленая галочка)
- Проверьте логи n8n на ошибки

---

## 📞 ГОТОВЫЕ КОМАНДЫ

### Создать таблицу одной командой (через gspread):

```python
# install: pip install gspread oauth2client

from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name(
    'config/google_credentials.json', scope)
client = gspread.authorize(creds)

# Создать таблицу
sheet = client.create('ChinaLeadBot - Leads Database')

# Добавить заголовки
worksheet = sheet.get_worksheet(0)
headers = ['Timestamp', 'Company', 'Rating', 'MOQ', 'Price',
           'Location', 'Years', 'Email', 'URL', 'AI_Score',
           'Recommended', 'Summary', 'Pros', 'Risks']
worksheet.append_row(headers)

print(f"Таблица создана! ID: {sheet.id}")
print(f"URL: https://docs.google.com/spreadsheets/d/{sheet.id}")
```

---

**ВСЁ ГОТОВО! Теперь у вас есть таблица для хранения лидов!** 🎉

**Не забудьте добавить ID таблицы в `.env`:**
```bash
GOOGLE_SHEET_ID=ваш_id_таблицы
```
