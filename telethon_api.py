#!/usr/bin/env python3
"""
Мини HTTP-сервер для отправки сообщений через Telethon userbot.
n8n вызывает этот сервер через HTTP Request ноду.

Запуск: python telethon_api.py
Порт: 5000

Эндпоинты:
  POST /send            — отправить сообщение по username
  GET  /health          — проверка работоспособности
  POST /search_channels — поиск Telegram-каналов по ключевым словам
"""

import os
import asyncio
import logging
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


@app.route('/send', methods=['POST'])
def send_message():
    """
    Тело запроса (JSON):
      { "username": "someuser", "text": "Привет..." }

    Ответ:
      { "success": true, "chat_id": 123456789 }
      { "success": false, "error": "privacy" | "not_found" | "flood:N" | "error text" }
    """
    data     = request.get_json(force=True)
    username = data.get('username', '').strip().lstrip('@')
    text     = data.get('text', '').strip()

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
