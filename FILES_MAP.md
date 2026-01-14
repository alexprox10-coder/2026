# 🗺️ Карта файлов проекта

## ✅ НОВЫЕ ИСПРАВЛЕННЫЕ WORKFLOWS (используйте их!)

### 1. child_workflow_01_AgentLeadAddQuery_FIXED.json 🆕
**Статус:** 🆕 НОВЫЙ - АВТОМАТИЧЕСКИЙ ПОИСК!
**Назначение:** Автоматический поиск сайтов компаний через Google
**Размер:** ~20 KB
**Что делает:**
- Принимает поисковый запрос (отрасль, город, регион)
- Ищет сайты компаний через Google (SerpAPI)
- Фильтрует нерелевантные сайты (соцсети, доски объявлений)
- Автоматически добавляет найденные сайты в CompanySites со статусом 0
- Возвращает количество найденных сайтов

**Импорт в n8n:**
```bash
Файл: child_workflow_01_AgentLeadAddQuery_FIXED.json
```

**Документация:** [SEARCH_COMPANIES_GUIDE.md](./SEARCH_COMPANIES_GUIDE.md)

---

### 2. child_workflow_02_AgentLeadAddSiteCompany_FIXED.json
**Статус:** 🆕 НОВЫЙ - ИСПОЛЬЗУЙТЕ ЭТОТ!
**Назначение:** Добавление сайтов компаний через webhook API
**Размер:** 13 KB
**Что делает:**
- Принимает POST запросы с URL сайта компании
- Валидирует URL
- Проверяет дубликаты в базе
- Добавляет в Google Sheets со статусом 0 (новый)
- Возвращает JSON ответ

**Импорт в n8n:**
```bash
Файл: child_workflow_02_AgentLeadAddSiteCompany_FIXED.json
```

---

### 3. child_workflow_03_AgentLeadScrapInformationCompany_FIXED_v2.json 🆕
**Статус:** 🆕 НОВЫЙ - ПО ЗАПРОСУ!
**Назначение:** Сбор данных с сайтов компаний **ПО ВАШЕМУ ЗАПРОСУ**
**Размер:** 30 KB
**Что делает:**
- Запускается webhook-запросом `/start-scraping` (НЕ автоматически!)
- Выбирает сайты со статусом 0 (до 20 штук)
- Загружает HTML
- Использует AI (Google Gemini - бесплатно!) для извлечения данных
- Сохраняет в базу CompanyInformation
- Обновляет статус (2=успех, 3=ошибка)

**Импорт в n8n:**
```bash
Файл: child_workflow_03_AgentLeadScrapInformationCompany_FIXED_v2.json
```

---

### 4. child_workflow_04_AgentLeadMailGenerate.json 🆕
**Статус:** 🆕 НОВЫЙ - ГЕНЕРАЦИЯ ПРЕДЛОЖЕНИЙ!
**Назначение:** Создание персональных коммерческих предложений
**Размер:** 25 KB
**Что делает:**
- Запускается webhook-запросом `/generate-proposals`
- Читает компании из CompanyInformation
- Фильтрует только те, у кого есть email
- AI генерирует уникальное предложение для каждой компании
- Сохраняет черновики в EmailDrafts

**Импорт в n8n:**
```bash
Файл: child_workflow_04_AgentLeadMailGenerate.json
```

---

## 🔄 ПОЛНЫЙ ЦИКЛ РАБОТЫ СИСТЕМЫ (ВСЕ ПО ЗАПРОСУ!) 🆕

### Вариант А: Полный автоматический поиск → персональные предложения (РЕКОМЕНДУЕТСЯ) 🆕

```
1. child_workflow_01 (ПО ВАШЕМУ ЗАПРОСУ!)
   └─ Вы: отправляете запрос (отрасль, город)
   └─ Система: ищет сайты в Google
   └─ Результат: сайты добавлены в CompanySites (Status=0)

2. child_workflow_03_v2 (ПО ВАШЕМУ ЗАПРОСУ!)
   └─ Вы: запускаете через webhook /start-scraping
   └─ Система: собирает данные с помощью AI (Google Gemini)
   └─ Результат: контакты в CompanyInformation (Status=2)

3. child_workflow_04 (ПО ВАШЕМУ ЗАПРОСУ!)
   └─ Вы: запускаете через webhook /generate-proposals
   └─ Система: генерирует персональные предложения
   └─ Результат: черновики писем в EmailDrafts

4. Готово! 🎉
   └─ Проверяете черновики → отправляете письма
```

### Вариант Б: Ручное добавление + обработка

```
1. child_workflow_02
   └─ Вы: добавляете URL сайта вручную
   └─ Результат: сайт добавлен в CompanySites (Status=0)

2. child_workflow_03_v2 (ПО ЗАПРОСУ!)
   └─ Вы: запускаете сбор данных
   └─ Результат: контакты в CompanyInformation

3. child_workflow_04 (ПО ЗАПРОСУ!)
   └─ Вы: генерируете предложения
   └─ Результат: черновики в EmailDrafts
```

---

## 📊 СТАРЫЕ ФАЙЛЫ (для справки)

Возможно, в проекте есть старые версии:
- `child_workflow_02_AgentLeadAddSiteCompany.json` - старая версия
- `child_workflow_03_AgentLeadScrapInformationCompany.json` - старая версия

**⚠️ НЕ ИСПОЛЬЗУЙТЕ СТАРЫЕ ВЕРСИИ!** Они могут содержать ошибки.

---

## 📚 ДОКУМЕНТАЦИЯ

| Файл | Описание |
|------|----------|
| **README.md** | 🆕 Обзор проекта и быстрый старт |
| **FILES_MAP.md** | 🆕 ЭТОТ ФАЙЛ - карта всех файлов |
| **ON_DEMAND_WORKFLOW_GUIDE.md** | 🆕 **СИСТЕМА ПО ЗАПРОСУ** - полный цикл работы! |
| **SEARCH_COMPANIES_GUIDE.md** | 🆕 **АВТОПОИСК САЙТОВ** - настройка SerpAPI |
| **COMPANY_SCRAPER_SYSTEM.md** | 🆕 Архитектура системы сбора данных |
| **SETUP_INSTRUCTIONS.md** | 🆕 Пошаговая установка и настройка |
| **GOOGLE_SHEETS_SETUP.md** | 🆕 Создание Google таблиц (шаблоны) |
| **QUICK_FIX_EXISTING_TABLE.md** | 🆕 Адаптация существующей таблицы |
| **WHERE_TO_FIND_FILES.md** | 🆕 Как найти файлы на GitHub |
| **WORKFLOW_FIXES.md** | Исправления для новостного workflow |

---

## 🎯 Что импортировать в n8n:

### Вариант 1: Для системы новостей
```
✅ workflow_fixed.json
```

### Вариант 2: ПОЛНЫЙ ЦИКЛ - поиск → данные → предложения (РЕКОМЕНДУЕТСЯ) 🆕
```
✅ child_workflow_01_AgentLeadAddQuery_FIXED.json                     (автопоиск сайтов)
✅ child_workflow_02_AgentLeadAddSiteCompany_FIXED.json               (ручное добавление)
✅ child_workflow_03_AgentLeadScrapInformationCompany_FIXED_v2.json   (сбор данных ПО ЗАПРОСУ)
✅ child_workflow_04_AgentLeadMailGenerate.json                       (генерация предложений) 🆕
```

### Вариант 3: Только сбор данных (без поиска и предложений)
```
✅ child_workflow_02_AgentLeadAddSiteCompany_FIXED.json               (добавление сайтов)
✅ child_workflow_03_AgentLeadScrapInformationCompany_FIXED_v2.json   (сбор данных)
```

### Вариант 4: Импортировать всё
```
✅ workflow_fixed.json                                                (новости)
✅ child_workflow_01_AgentLeadAddQuery_FIXED.json                     (автопоиск)
✅ child_workflow_02_AgentLeadAddSiteCompany_FIXED.json               (ручное добавление)
✅ child_workflow_03_AgentLeadScrapInformationCompany_FIXED_v2.json   (сбор данных)
✅ child_workflow_04_AgentLeadMailGenerate.json                       (генерация предложений)
```

---

## 🔍 Как найти нужный файл:

### В GitHub:
1. Перейдите на ветку `claude/initial-setup-E7QOi`
2. Найдите файлы с суффиксом `_FIXED`

### В файловой системе:
```bash
/home/user/2026/child_workflow_02_AgentLeadAddSiteCompany_FIXED.json
/home/user/2026/child_workflow_03_AgentLeadScrapInformationCompany_FIXED.json
```

---

## 🚀 Быстрый старт (пошагово):

### Шаг 1: Импорт workflows
1. Откройте n8n
2. Нажмите "Import from File"
3. Выберите:
   - `child_workflow_01_AgentLeadAddQuery_FIXED.json` (поиск)
   - `child_workflow_02_AgentLeadAddSiteCompany_FIXED.json` (ручное добавление)
   - `child_workflow_03_AgentLeadScrapInformationCompany_FIXED_v2.json` (сбор данных)
   - `child_workflow_04_AgentLeadMailGenerate.json` (генерация предложений)

### Шаг 2: Настройка
1. Создайте Google таблицу с 3 листами (см. GOOGLE_SHEETS_SETUP.md):
   - CompanySites
   - CompanyInformation
   - EmailDrafts 🆕
2. Замените `YOUR_GOOGLE_SHEET_ID_HERE` на ваш ID во всех workflows
3. Получите API ключи:
   - Google Gemini API (бесплатно): https://aistudio.google.com/app/apikey
   - SerpAPI (100 запросов/месяц бесплатно): https://serpapi.com
4. Настройте credentials в n8n

### Шаг 3: Активация
1. Активируйте все 4 workflows
2. Запустите первый поиск компаний через webhook

**📖 Подробная инструкция:** См. ON_DEMAND_WORKFLOW_GUIDE.md

---

## ⚙️ Альтернативные имена файлов

Эти файлы - дубликаты (для совместимости):
- `workflow_add_company_site.json` = `child_workflow_02_AgentLeadAddSiteCompany_FIXED.json`
- `workflow_scrap_company_info.json` = `child_workflow_03_AgentLeadScrapInformationCompany_FIXED.json`

**Используйте версии с префиксом `child_workflow_` и суффиксом `_FIXED`!**

---

## 📞 Помощь

Если запутались:
1. ✅ Используйте файлы с `_FIXED` в названии
2. ✅ Читайте SETUP_INSTRUCTIONS.md
3. ✅ Проверяйте, что на ветке `claude/initial-setup-E7QOi`

---

**Последнее обновление:** 2026-01-14
**Версия:** 1.0
