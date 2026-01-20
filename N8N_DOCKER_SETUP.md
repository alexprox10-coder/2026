# n8n Docker Setup для подключения к API

## Проблема
n8n в Docker не может подключиться к API серверу на localhost:5555

## Решение

### Вариант 1: Docker с host.docker.internal (Рекомендуется)

При запуске n8n через Docker добавьте флаг `--add-host`:

```bash
docker run -d \
  --name n8n \
  --add-host=host.docker.internal:host-gateway \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Или в `docker-compose.yml`:

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    volumes:
      - ~/.n8n:/home/node/.n8n
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### Вариант 2: Network mode host

Запустите n8n с `--network=host`:

```bash
docker run -d \
  --name n8n \
  --network=host \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Важно:** При использовании `--network=host`:
- Не нужен флаг `-p 5678:5678`
- n8n будет доступен напрямую на порту 5678
- В workflow используйте `http://localhost:5555`

### Вариант 3: Bridge network (если n8n и API на одном хосте)

Если оба контейнера в одной Docker сети:

```bash
docker network create rental_network
docker run -d --name api --network rental_network ...
docker run -d --name n8n --network rental_network n8nio/n8n
```

В workflow используйте `http://api:5555`

## Проверка подключения

После настройки Docker перейдите в n8n и протестируйте HTTP Request node:

```
GET http://host.docker.internal:5555/health
```

Должен вернуть:
```json
{
  "status": "ok",
  "message": "API server is running"
}
```

## Текущие URL в workflows

Все workflow файлы уже настроены на `http://host.docker.internal:5555`:
- `rental_parser_full_workflow.json`
- `rental_parser_api_simple.json`
- `rental_parser_api.json`

## API Server

API сервер уже запущен и слушает на `0.0.0.0:5555`:
```bash
ps aux | grep api_server.py
```

Эндпоинты:
- `GET /health` - Проверка состояния
- `GET /status` - Конфигурация
- `GET /get-unsent?limit=50` - Неотправленные объявления
- `POST /parse` - Запуск парсера (ожидание завершения)
- `POST /parse-async` - Запуск парсера (фоновый режим)
