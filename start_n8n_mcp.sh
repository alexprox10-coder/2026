#!/bin/bash
# Скрипт запуска n8n-mcp с API ключом

# Загружаем переменные из .env
set -a
source "$(dirname "$0")/.env"
set +a

# Экспортируем для n8n-mcp
export N8N_API_URL="${N8N_URL}"
export N8N_API_KEY="${N8N_API_KEY}"

# Запускаем n8n-mcp
npx n8n-mcp "$@"
