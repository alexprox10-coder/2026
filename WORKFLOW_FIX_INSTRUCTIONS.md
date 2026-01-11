# Исправление ошибки "Workflow does not exist" / Fixing "Workflow does not exist" Error

## Описание проблемы / Problem Description

При выполнении команды через Telegram бот выдает ошибку:
```
Workflow does not exist
```

Это происходит потому, что дочерний рабочий процесс (child workflow) `AgentLeadScrapInformationCompany` не импортирован или неправильно настроен в n8n.

When executing commands through the Telegram bot, the following error appears:
```
Workflow does not exist
```

This happens because the child workflow `AgentLeadScrapInformationCompany` is not imported or incorrectly configured in n8n.

---

## Решение / Solution

### Шаг 1: Импорт рабочих процессов / Step 1: Import Workflows

Вам необходимо импортировать следующие файлы в n8n **в указанном порядке**:

You need to import the following files into n8n **in this order**:

#### 1.1 Дочерние рабочие процессы (Child Workflows) - СНАЧАЛА / FIRST:

**ВАЖНО: Импортируйте дочерние процессы ПЕРЕД основным!**
**IMPORTANT: Import child workflows BEFORE the main workflow!**

```bash
# Child Workflow 1 - Сбор запросов агентств
child_workflow_01_AgentLeadAddQuery.json
ID: (будет присвоен автоматически / will be assigned automatically)

# Child Workflow 2 - Добавление сайта компании
child_workflow_02_AgentLeadAddSiteCompany.json
ID: (будет присвоен автоматически / will be assigned automatically)

# Child Workflow 3 - Сбор информации о компании (КРИТИЧЕСКИ ВАЖНЫЙ!)
child_workflow_03_AgentLeadScrapInformationCompany.json
ID: tBIq1jiaRl2lCLxw (ОБЯЗАТЕЛЬНО ЭТОТ ID! / THIS ID IS REQUIRED!)

# Child Workflow 4 - Генерация email
child_workflow_04_AgentLeadMailGenerate.json
ID: (будет присвоен автоматически / will be assigned automatically)
```

#### 1.2 Основной рабочий процесс (Main Workflow) - ПОТОМ / THEN:

```bash
# Main Telegram Bot Workflow
workflow_parsing_kp.json
```

---

### Шаг 2: Критически важно для child_workflow_03 / Step 2: Critical for child_workflow_03

**ВНИМАНИЕ!** Рабочий процесс `child_workflow_03_AgentLeadScrapInformationCompany.json` ДОЛЖЕН иметь ID: `tBIq1jiaRl2lCLxw`

**ATTENTION!** The workflow `child_workflow_03_AgentLeadScrapInformationCompany.json` MUST have ID: `tBIq1jiaRl2lCLxw`

Как проверить ID в n8n:
1. Откройте рабочий процесс в n8n
2. Нажмите на меню (три точки) → Settings
3. В поле "Workflow ID" должно быть: `tBIq1jiaRl2lCLxw`

How to check ID in n8n:
1. Open the workflow in n8n
2. Click on menu (three dots) → Settings
3. In "Workflow ID" field should be: `tBIq1jiaRl2lCLxw`

Если ID отличается, выполните следующее:
If the ID is different, do the following:

```bash
# Удалите workflow и импортируйте заново из файла
# Delete the workflow and re-import from file
# OR
# Измените ID в файле перед импортом на тот, который присвоил n8n
# Change the ID in the file before import to match what n8n assigned
```

---

### Шаг 3: Активация рабочих процессов / Step 3: Activate Workflows

После импорта активируйте все процессы:

After importing, activate all workflows:

1. **child_workflow_03_AgentLeadScrapInformationCompany** - активировать / activate
2. **workflow_parsing_kp** (main workflow) - активировать / activate

---

### Шаг 4: Проверка / Step 4: Verification

Отправьте тестовое сообщение боту в Telegram:

Send a test message to the bot in Telegram:

```
/start
```

Если всё настроено правильно, бот должен ответить без ошибки "Workflow does not exist".

If everything is configured correctly, the bot should respond without the "Workflow does not exist" error.

---

## Структура проекта / Project Structure

```
/home/user/2026/
├── child_workflow_01_AgentLeadAddQuery.json              # Дочерний процесс 1
├── child_workflow_02_AgentLeadAddSiteCompany.json        # Дочерний процесс 2
├── child_workflow_03_AgentLeadScrapInformationCompany.json  # Дочерний процесс 3 (ГЛАВНЫЙ!)
├── child_workflow_04_AgentLeadMailGenerate.json          # Дочерний процесс 4
├── workflow_parsing_kp.json                               # Основной процесс (Main)
├── workflow_agent_leads.json                              # Webhook процесс для API
├── workflow_fixed.json                                    # RSS новости → Telegram
└── .backup_child_workflow_03_*.json                       # Резервные версии (не использовать!)
```

---

## Технические детали / Technical Details

### Почему возникает ошибка / Why the error occurs:

1. **Отсутствие workflow в n8n**: Файл существует в репозитории, но не импортирован в n8n instance
   **Missing workflow in n8n**: File exists in repository but not imported into n8n instance

2. **Неправильный ID**: ID в файле не совпадает с ID в n8n
   **Wrong ID**: ID in file doesn't match ID in n8n

3. **Workflow не активирован**: Process imported but not activated
   **Workflow not activated**: Process imported but not activated

4. **Неправильный порядок импорта**: Main workflow imported before child workflows
   **Wrong import order**: Main workflow imported before child workflows

### Что делает child_workflow_03:

Child workflow 03 является инструментом AI агента, который:
- Собирает информацию о компаниях
- Записывает данные в Excel файл
- Используется основным процессом через "Execute Workflow" node

Child workflow 03 is an AI agent tool that:
- Collects company information
- Writes data to Excel file
- Used by main workflow through "Execute Workflow" node

---

## Дополнительная информация / Additional Information

### Резервные копии / Backups

Файлы с префиксом `.backup_` являются тестовыми версиями и НЕ должны быть импортированы:

Files with `.backup_` prefix are test versions and should NOT be imported:

- `.backup_child_workflow_03_SINGLE_NODE.json` (тест с 1 узлом)
- `.backup_child_workflow_03_MINIMAL.json` (минимальная версия)
- `.backup_child_workflow_03_ULTRA_SIMPLE.json` (упрощенная версия)

Используйте только основной файл:
Use only the main file:
- `child_workflow_03_AgentLeadScrapInformationCompany.json`

---

## Контакты и поддержка / Support

Если проблема не решена:
If the problem persists:

1. Проверьте логи n8n: `docker logs n8n` (если используется Docker)
2. Убедитесь, что все credentials настроены (Anthropic API, Google Sheets, Telegram)
3. Проверьте, что версия n8n >= 1.0.0

Check:
1. n8n logs: `docker logs n8n` (if using Docker)
2. All credentials are configured (Anthropic API, Google Sheets, Telegram)
3. n8n version >= 1.0.0

---

**Версия документа**: 1.0
**Дата**: 2026-01-11
**Статус**: Исправлено / Fixed ✅
