#!/bin/bash
# Запуск Telegram Parser с прокси

# Остановить старый процесс
pkill -f telegram_parser_api.py 2>/dev/null
sleep 1

# Загрузить переменные
source /etc/telegram-parser.env
export TELEGRAM_API_ID TELEGRAM_API_HASH TELEGRAM_PHONE PROXY_HOST PROXY_PORT PROXY_TYPE

# Запустить парсер
nohup python3 /root/telegram_parser_api.py > /var/log/telegram-parser-api.log 2>&1 &

echo "✅ Парсер запущен (PID: $!)"
sleep 2
curl -s http://localhost:5000/health && echo ""
