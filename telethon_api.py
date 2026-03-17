#!/usr/bin/env python3
"""
Мини HTTP-сервер для отправки сообщений через Telethon userbot.
n8n вызывает этот сервер через HTTP Request ноду.

Запуск: python3 telethon_api.py
Порт: 5000

Эндпоинты:
  GET  /health          — проверка работоспособности
  POST /search_channels — поиск Telegram-каналов по ключевым словам
  POST /parse           — парсинг постов из списка каналов (для WF2)
  POST /send            — отправить сообщение по username
  POST /send_message    — то же самое (алиас для WF3, поле message вместо text)
"""

import os
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from threading import Thread
from flask import Flask, request, jsonify
from telethon import TelegramClient
from telethon.errors import (
    UserNotMutualContactError,
    UserPrivacyRestrictedError,
    FloodWaitError,
    PeerIdInvalidError
)
from telethon.tl.functions.contacts import SearchRequest
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app   = Flask(__name__)
loop  = asyncio.new_event_loop()
client: TelegramClient = None


def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


async def init_client():
    global client
    client = TelegramClient(
        'telegram_session',
        int(os.getenv('TELEGRAM_API_ID')),
        os.getenv('TELEGRAM_API_HASH')
    )
    await client.start(phone=os.getenv('TELEGRAM_PHONE'))
    logger.info("Telethon клиент запущен")


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'connected': client is not None and client.is_connected()})


@app.route('/search_channels', methods=['POST'])
def search_channels():
    """
    Тело запроса (JSON):
      { "keywords": ["аренда", "москва"], "limit": 10, "min_subscribers": 100 }

    Ответ:
      { "channels": [ { "username": "...", "title": "...", "subscribers": 123, "description": "..." } ] }
    """
    data = request.get_json(force=True)
    keywords = data.get('keywords', [])
    limit = int(data.get('limit', 10))
    min_subscribers = int(data.get('min_subscribers', 100))

    if not keywords:
        return jsonify({'channels': []})

    query = ' '.join(keywords[:5])

    async def _search():
        try:
            result = await client(SearchRequest(q=query, limit=min(limit * 3, 50)))
            channels = []
            for chat in result.chats:
                try:
                    if not hasattr(chat, 'broadcast') or not chat.broadcast:
                        continue
                    subs = getattr(chat, 'participants_count', 0) or 0
                    if subs < min_subscribers:
                        continue
                    username = getattr(chat, 'username', None)
                    if not username:
                        continue
                    channels.append({
                        'username': username,
                        'title': chat.title or username,
                        'subscribers': subs,
                        'description': getattr(chat, 'about', '') or ''
                    })
                    if len(channels) >= limit:
                        break
                except Exception:
                    continue
            return {'channels': channels}
        except Exception as e:
            logger.error(f"Ошибка поиска каналов: {e}")
            return {'channels': [], 'error': str(e)}

    future = asyncio.run_coroutine_threadsafe(_search(), loop)
    result = future.result(timeout=60)
    return jsonify(result)


@app.route('/parse', methods=['POST'])
def parse_channels():
    """
    Тело запроса (JSON):
      {
        "channels": ["username1", "username2"],
        "days_back": 7,
        "keywords": ["аренда", "снять"],
        "limit_per_channel": 50
      }

    Ответ:
      {
        "posts": [
          {
            "channel": "username1",
            "post_id": 123,
            "text": "текст поста",
            "date": "2026-03-10T12:00:00",
            "views": 500,
            "url": "https://t.me/username1/123"
          }
        ],
        "total": 12
      }
    """
    data = request.get_json(force=True)
    channels = data.get('channels', [])
    days_back = int(data.get('days_back', 7))
    keywords = [k.lower() for k in data.get('keywords', [])]
    limit_per_channel = int(data.get('limit_per_channel', 50))

    if not channels:
        return jsonify({'posts': [], 'total': 0})

    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    async def _parse():
        all_posts = []
        for username in channels:
            try:
                username = username.strip().lstrip('@').lstrip('https://t.me/').split('/')[0]
                entity = await client.get_entity(username)
                async for msg in client.iter_messages(entity, limit=limit_per_channel):
                    if msg.date < cutoff:
                        break
                    if not msg.text:
                        continue
                    text_lower = msg.text.lower()
                    if keywords and not any(kw in text_lower for kw in keywords):
                        continue
                    all_posts.append({
                        'channel': username,
                        'post_id': msg.id,
                        'text': msg.text,
                        'date': msg.date.isoformat(),
                        'views': getattr(msg, 'views', 0) or 0,
                        'url': f'https://t.me/{username}/{msg.id}'
                    })
            except Exception as e:
                logger.warning(f"Ошибка парсинга канала @{username}: {e}")
                continue
        return {'posts': all_posts, 'total': len(all_posts)}

    future = asyncio.run_coroutine_threadsafe(_parse(), loop)
    result = future.result(timeout=120)
    return jsonify(result)


@app.route('/send', methods=['POST'])
@app.route('/send_message', methods=['POST'])
def send_message():
    """
    Тело запроса (JSON):
      { "username": "someuser", "text": "Привет..." }
      или (WF3):
      { "username": "someuser", "message": "Привет...", "post_url": "https://t.me/..." }

    Ответ:
      { "success": true, "chat_id": 123456789 }
      { "success": false, "error": "privacy" | "not_found" | "flood:N" | "error text" }
    """
    data     = request.get_json(force=True)
    username = data.get('username', '').strip().lstrip('@')
    # WF3 передаёт поле "message", WF1/WF2 — "text"
    text     = (data.get('text') or data.get('message') or '').strip()

    if not username or not text:
        return jsonify({'success': False, 'error': 'username and text required'}), 400

    async def _send():
        try:
            entity = await client.get_entity(username)
            await client.send_message(entity, text)
            return {'success': True, 'chat_id': entity.id}
        except (UserNotMutualContactError, UserPrivacyRestrictedError):
            return {'success': False, 'error': 'privacy'}
        except PeerIdInvalidError:
            return {'success': False, 'error': 'not_found'}
        except FloodWaitError as e:
            return {'success': False, 'error': f'flood:{e.seconds}'}
        except Exception as e:
            logger.error(f"Ошибка отправки @{username}: {e}")
            return {'success': False, 'error': str(e)}

    future = asyncio.run_coroutine_threadsafe(_send(), loop)
    result = future.result(timeout=30)
    return jsonify(result)


if __name__ == '__main__':
    # Запускаем event loop в фоновом потоке
    t = Thread(target=start_background_loop, args=(loop,), daemon=True)
    t.start()

    # Инициализируем Telethon (первый раз попросит код из Telegram)
    future = asyncio.run_coroutine_threadsafe(init_client(), loop)
    future.result(timeout=120)

    logger.info("API сервер запущен на http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
