# 🚀 Руководство по Развёртыванию

## Локальное развёртывание

### Быстрая установка
См. [QUICKSTART.md](QUICKSTART.md)

## Развёртывание на сервере

### Вариант 1: VPS/Dedicated Server

#### 1. Подготовка сервера (Ubuntu/Debian)

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install python3 python3-pip python3-venv git -y

# Клонирование репозитория
cd /opt
sudo git clone <your-repo-url> lead_agent
cd lead_agent
sudo chown -R $USER:$USER /opt/lead_agent
```

#### 2. Настройка окружения

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка .env
cp .env.example .env
nano .env  # Заполните ключи
```

#### 3. Настройка как системного сервиса

Создайте файл `/etc/systemd/system/lead-agent.service`:

```ini
[Unit]
Description=Lead Collection Agent
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/lead_agent
Environment="PATH=/opt/lead_agent/venv/bin"
ExecStart=/opt/lead_agent/venv/bin/python /opt/lead_agent/agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация сервиса:

```bash
sudo systemctl daemon-reload
sudo systemctl enable lead-agent
sudo systemctl start lead-agent

# Проверка статуса
sudo systemctl status lead-agent

# Просмотр логов
sudo journalctl -u lead-agent -f
```

### Вариант 2: Docker

#### Создание Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создание директорий
RUN mkdir -p logs config

CMD ["python", "agent.py"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  lead-agent:
    build: .
    container_name: lead_agent
    env_file:
      - .env
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped
```

#### Запуск

```bash
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Вариант 3: Cloud Functions (Serverless)

#### Google Cloud Functions

1. Подготовьте `main.py`:

```python
from agent import LeadCollectionAgent

agent = LeadCollectionAgent()

def process_request(request):
    """HTTP Cloud Function для обработки запросов"""
    request_json = request.get_json(silent=True)

    if not request_json or 'message' not in request_json:
        return {'error': 'Message required'}, 400

    try:
        response = agent.process_message(request_json['message'])
        return {'success': True, 'response': response}, 200
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
```

2. Деплой:

```bash
gcloud functions deploy lead-agent \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point process_request \
  --set-env-vars ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
```

## Интеграция с n8n

### Вариант 1: Execute Command Node

1. Импортируйте `n8n_webhook_example.json` в n8n
2. Настройте Execute Command Node с путём к агенту
3. Активируйте workflow

### Вариант 2: HTTP Request

Если агент работает как API:

```json
{
  "method": "POST",
  "url": "http://your-server:8000/process",
  "body": {
    "message": "{{ $json.message }}"
  }
}
```

## Мониторинг и обслуживание

### Логирование

Логи сохраняются в `logs/agent.log`:

```bash
# Просмотр последних логов
tail -f logs/agent.log

# Поиск ошибок
grep ERROR logs/agent.log

# Ротация логов (logrotate)
sudo nano /etc/logrotate.d/lead-agent
```

Конфигурация logrotate:

```
/opt/lead_agent/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Мониторинг производительности

#### Использование Prometheus + Grafana

1. Добавьте метрики в агент
2. Настройте Prometheus для сбора метрик
3. Создайте дашборд в Grafana

#### Простой мониторинг через cron

```bash
# Добавьте в crontab
*/5 * * * * /opt/lead_agent/scripts/health_check.sh
```

`scripts/health_check.sh`:

```bash
#!/bin/bash
if ! systemctl is-active --quiet lead-agent; then
    echo "Agent is down, restarting..."
    systemctl restart lead-agent
    # Отправка уведомления
fi
```

## Резервное копирование

### Google Sheets

Google Sheets автоматически сохраняет версии. Дополнительно:

```bash
# Экспорт данных
python -c "from modules.google_sheets import GoogleSheetsManager; \
gs = GoogleSheetsManager(); \
# Код экспорта"
```

### Конфигурация

```bash
# Регулярное резервное копирование
0 2 * * * tar -czf /backup/lead_agent_$(date +\%Y\%m\%d).tar.gz \
  /opt/lead_agent/config /opt/lead_agent/.env
```

## Масштабирование

### Горизонтальное масштабирование

Для обработки большого объёма запросов:

1. Используйте очередь сообщений (RabbitMQ, Redis)
2. Запустите несколько экземпляров агента
3. Распределите нагрузку через Load Balancer

### Оптимизация производительности

- Используйте кэширование для частых запросов
- Включите пул соединений для Google Sheets
- Оптимизируйте парсинг (асинхронность, батчинг)

## Безопасность

### Рекомендации

1. **Не коммитьте секреты в Git**
   - Используйте `.env` файлы
   - Добавьте `.env` в `.gitignore`

2. **Ограничьте доступ к API ключам**
   - Используйте environment variables
   - Секреты в CI/CD (GitHub Secrets, GitLab CI/CD Variables)

3. **Настройте файрвол**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

4. **Регулярно обновляйте зависимости**
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

5. **Используйте HTTPS для webhook endpoints**

## Обновление

```bash
cd /opt/lead_agent
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart lead-agent
```

## Откат версии

```bash
cd /opt/lead_agent
git log --oneline  # Найдите нужный коммит
git checkout <commit-hash>
sudo systemctl restart lead-agent
```

## Troubleshooting

### Агент не запускается

1. Проверьте логи: `journalctl -u lead-agent -n 50`
2. Проверьте .env файл
3. Убедитесь что виртуальное окружение активно
4. Проверьте права доступа к файлам

### Ошибки Google Sheets

1. Проверьте `google_credentials.json`
2. Убедитесь что service account имеет доступ
3. Проверьте квоты API

### Медленная работа

1. Проверьте логи на таймауты
2. Увеличьте таймауты в настройках
3. Оптимизируйте запросы к API
4. Рассмотрите кэширование

## Поддержка

При возникновении проблем:

1. Проверьте [README.md](README.md)
2. Изучите [QUICKSTART.md](QUICKSTART.md)
3. Просмотрите логи в `logs/agent.log`
4. Запустите `python test_connection.py`
