#!/usr/bin/env python3
"""
🔥 TELEGRAM PARSER PRO - API для n8n
Запускает парсер через HTTP API

Запуск: python3 telegram_parser_api.py
API будет доступен на http://localhost:5000

Endpoints:
- POST /parse - запуск парсинга
- GET /status - статус парсера
- GET /results - получить последние результаты
"""

import asyncio
import hashlib
import re
import json
import os
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask, request, jsonify
from flask_cors import CORS

try:
    from telethon import TelegramClient
    from telethon.tl.functions.channels import GetFullChannelRequest
    from telethon.tl.functions.messages import GetHistoryRequest
    from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
    import pandas as pd
except ImportError:
    print("Установите зависимости: pip install telethon pandas openpyxl flask flask-cors")
    exit(1)

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для n8n

# ============== КОНФИГУРАЦИЯ ==============
CONFIG = {
    # Telegram API (получить на https://my.telegram.org)
    "api_id": os.environ.get("TELEGRAM_API_ID", "ВАШ_API_ID"),
    "api_hash": os.environ.get("TELEGRAM_API_HASH", "ВАШ_API_HASH"),
    "phone": os.environ.get("TELEGRAM_PHONE", "+7XXXXXXXXXX"),

    # API настройки
    "host": "0.0.0.0",
    "port": 5000,

    # Выходные файлы
    "output_dir": "/root/parser_results"
}

# Глобальные переменные для статуса
parser_status = {
    "is_running": False,
    "last_run": None,
    "last_results": None,
    "last_error": None
}


class TelegramParserAPI:
    def __init__(self, api_id, api_hash, phone):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = None
        self.results = []
        self.stats = {
            "total_messages": 0,
            "matched_messages": 0,
            "phones_found": 0,
            "usernames_found": 0,
            "emails_found": 0
        }

    async def start(self):
        """Запуск клиента"""
        self.client = TelegramClient(
            'parser_session_api',
            self.api_id,
            self.api_hash
        )
        await self.client.start(phone=self.phone)
        return True

    async def stop(self):
        """Остановка клиента"""
        if self.client:
            await self.client.disconnect()

    def extract_contacts(self, text):
        """Извлечение контактов из текста"""
        contacts = {
            "phones": [],
            "usernames": [],
            "emails": [],
            "urls": []
        }

        # Телефоны
        phone_patterns = [
            r'(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
            r'(?:\+7|8)\d{10}',
            r'\+\d{1,3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            contacts["phones"].extend(phones)

        # Telegram usernames
        usernames = re.findall(r'@([a-zA-Z][a-zA-Z0-9_]{4,31})', text)
        contacts["usernames"] = ['@' + u for u in usernames]

        # Email
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        contacts["emails"] = emails

        # URLs
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
        contacts["urls"] = urls[:5]

        return contacts

    def detect_niche(self, text, keywords_config):
        """Определение ниши по ключевым словам"""
        lower_text = text.lower()

        for niche, keywords in keywords_config.items():
            for keyword in keywords:
                if keyword.lower() in lower_text:
                    return niche, keyword

        return None, None

    def calculate_lead_score(self, data):
        """Скоринг качества лида"""
        score = 0

        if data.get('phones'):
            score += 35
        if data.get('usernames'):
            score += 20
        if data.get('emails'):
            score += 25

        text_len = len(data.get('text', ''))
        if text_len > 100:
            score += 5
        if text_len > 300:
            score += 5

        if data.get('views', 0) > 1000:
            score += 5
        if data.get('views', 0) > 10000:
            score += 5

        if data.get('is_ad'):
            score -= 20

        return max(0, min(100, score))

    def is_advertisement(self, text):
        """Определение рекламы"""
        ad_markers = [
            'реклама', 'партнер', '#ad', 'sponsor', 'промо',
            'erid:', 'токен:', 'рекл.', 'на правах рекламы'
        ]
        lower_text = text.lower()
        return any(marker in lower_text for marker in ad_markers)

    def _get_media_type(self, media):
        """Определение типа медиа"""
        if not media:
            return None
        if isinstance(media, MessageMediaPhoto):
            return "photo"
        if isinstance(media, MessageMediaDocument):
            return "document"
        return "other"

    async def parse_channel(self, channel_username, keywords_config, messages_limit=100, days_back=7):
        """Парсинг одного канала"""
        try:
            channel = await self.client.get_entity(channel_username)

            try:
                full = await self.client(GetFullChannelRequest(channel))
                subscribers = full.full_chat.participants_count
            except:
                subscribers = 0

            offset_date = datetime.now() - timedelta(days=days_back)

            messages = await self.client(GetHistoryRequest(
                peer=channel,
                limit=messages_limit,
                offset_date=offset_date,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            channel_results = []

            for msg in messages.messages:
                if not msg.message:
                    continue

                self.stats['total_messages'] += 1
                text = msg.message

                niche, keyword = self.detect_niche(text, keywords_config)
                if not niche:
                    continue

                self.stats['matched_messages'] += 1

                contacts = self.extract_contacts(text)

                if contacts['phones']:
                    self.stats['phones_found'] += len(contacts['phones'])
                if contacts['usernames']:
                    self.stats['usernames_found'] += len(contacts['usernames'])
                if contacts['emails']:
                    self.stats['emails_found'] += len(contacts['emails'])

                data = {
                    "timestamp": msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "date": msg.date.strftime("%Y-%m-%d"),
                    "channel_title": channel.title,
                    "channel_username": f"@{channel.username}" if channel.username else "",
                    "channel_id": channel.id,
                    "subscribers": subscribers,
                    "text": text,
                    "text_preview": text[:200] + "..." if len(text) > 200 else text,
                    "has_media": bool(msg.media),
                    "media_type": self._get_media_type(msg.media),
                    "views": msg.views or 0,
                    "forwards": msg.forwards or 0,
                    "phones": ", ".join(set(contacts['phones'])),
                    "usernames": ", ".join(set(contacts['usernames'])),
                    "emails": ", ".join(set(contacts['emails'])),
                    "links": ", ".join(contacts['urls']),
                    "niche": niche,
                    "keyword_matched": keyword,
                    "is_ad": self.is_advertisement(text),
                    "post_url": f"https://t.me/{channel.username}/{msg.id}" if channel.username else f"https://t.me/c/{channel.id}/{msg.id}",
                    "message_id": msg.id,
                    "text_hash": hashlib.md5(text.encode()).hexdigest()[:16]
                }

                data['lead_score'] = self.calculate_lead_score(data)
                channel_results.append(data)

            return channel_results

        except Exception as e:
            return {"error": str(e)}

    async def parse(self, channels, keywords, messages_limit=100, days_back=7):
        """Основной метод парсинга"""
        self.results = []
        self.stats = {
            "total_messages": 0,
            "matched_messages": 0,
            "phones_found": 0,
            "usernames_found": 0,
            "emails_found": 0
        }

        await self.start()

        try:
            for channel in channels:
                results = await self.parse_channel(
                    channel,
                    keywords,
                    messages_limit,
                    days_back
                )
                if isinstance(results, list):
                    self.results.extend(results)
                await asyncio.sleep(2)

            self.results.sort(key=lambda x: x.get('lead_score', 0), reverse=True)

            return {
                "success": True,
                "stats": self.stats,
                "results": self.results,
                "results_count": len(self.results)
            }

        finally:
            await self.stop()


def run_parser_async(channels, keywords, messages_limit, days_back):
    """Запуск парсера в отдельном потоке"""
    global parser_status

    parser_status["is_running"] = True
    parser_status["last_error"] = None

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        parser = TelegramParserAPI(
            CONFIG["api_id"],
            CONFIG["api_hash"],
            CONFIG["phone"]
        )

        result = loop.run_until_complete(
            parser.parse(channels, keywords, messages_limit, days_back)
        )

        parser_status["last_results"] = result
        parser_status["last_run"] = datetime.now().isoformat()

        # Сохраняем в файл
        os.makedirs(CONFIG["output_dir"], exist_ok=True)
        filename = f"{CONFIG['output_dir']}/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        loop.close()

    except Exception as e:
        parser_status["last_error"] = str(e)
        parser_status["last_results"] = {"success": False, "error": str(e)}

    finally:
        parser_status["is_running"] = False


# ============== API ENDPOINTS ==============

@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья API"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route('/status', methods=['GET'])
def status():
    """Статус парсера"""
    return jsonify(parser_status)


@app.route('/parse', methods=['POST'])
def parse():
    """
    Запуск парсинга

    Body JSON:
    {
        "channels": ["channel1", "channel2"],
        "keywords": {
            "leads": ["ищу", "куплю"],
            "jobs": ["вакансия", "работа"]
        },
        "messages_limit": 100,
        "days_back": 7,
        "async": false
    }
    """
    global parser_status

    if parser_status["is_running"]:
        return jsonify({
            "success": False,
            "error": "Парсер уже запущен. Дождитесь завершения."
        }), 429

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "Требуется JSON body"}), 400

    channels = data.get("channels", [])
    keywords = data.get("keywords", {
        "leads": ["ищу", "куплю", "нужен", "требуется"]
    })
    messages_limit = data.get("messages_limit", 100)
    days_back = data.get("days_back", 7)
    is_async = data.get("async", False)

    if not channels:
        return jsonify({"success": False, "error": "Укажите каналы для парсинга"}), 400

    if is_async:
        # Асинхронный режим - запускаем в фоне
        thread = Thread(
            target=run_parser_async,
            args=(channels, keywords, messages_limit, days_back)
        )
        thread.start()

        return jsonify({
            "success": True,
            "message": "Парсинг запущен в фоновом режиме",
            "check_status": "/status",
            "get_results": "/results"
        })

    else:
        # Синхронный режим - ждём результат
        run_parser_async(channels, keywords, messages_limit, days_back)
        return jsonify(parser_status["last_results"])


@app.route('/results', methods=['GET'])
def results():
    """Получить последние результаты"""
    if parser_status["last_results"]:
        return jsonify(parser_status["last_results"])
    return jsonify({"success": False, "error": "Нет результатов. Сначала запустите парсинг."}), 404


@app.route('/results/leads', methods=['GET'])
def leads_only():
    """Получить только лиды с контактами"""
    if not parser_status["last_results"]:
        return jsonify({"success": False, "error": "Нет результатов"}), 404

    results = parser_status["last_results"].get("results", [])

    # Фильтруем только с контактами
    leads = [
        r for r in results
        if r.get("phones") or r.get("emails") or r.get("usernames")
    ]

    return jsonify({
        "success": True,
        "leads_count": len(leads),
        "leads": leads
    })


@app.route('/webhook/n8n', methods=['POST'])
def n8n_webhook():
    """
    Специальный endpoint для n8n
    Принимает данные в формате n8n и возвращает результаты в удобном формате
    """
    global parser_status

    if parser_status["is_running"]:
        return jsonify({
            "success": False,
            "error": "Парсер занят"
        }), 429

    data = request.get_json()

    # Поддержка разных форматов входных данных от n8n
    channels = data.get("channels") or data.get("channel", "").split(",")
    channels = [c.strip() for c in channels if c.strip()]

    # Ключевые слова могут быть строкой или списком
    keywords_input = data.get("keywords", "")
    if isinstance(keywords_input, str):
        keywords_list = [k.strip() for k in keywords_input.split(",") if k.strip()]
        keywords = {"custom": keywords_list}
    else:
        keywords = keywords_input

    messages_limit = int(data.get("messages_limit", 100))
    days_back = int(data.get("days_back", 7))

    if not channels:
        return jsonify({"success": False, "error": "Укажите каналы"}), 400

    # Запускаем парсинг синхронно
    run_parser_async(channels, keywords, messages_limit, days_back)

    result = parser_status["last_results"]

    if not result or not result.get("success"):
        return jsonify(result or {"success": False, "error": "Ошибка парсинга"}), 500

    # Форматируем для n8n (плоская структура для таблицы)
    leads = result.get("results", [])

    # Преобразуем для Google Sheets / таблицы
    table_data = []
    for lead in leads:
        table_data.append({
            "Дата": lead.get("date", ""),
            "Канал": lead.get("channel_title", ""),
            "Текст": lead.get("text_preview", ""),
            "Телефон": lead.get("phones", ""),
            "Username": lead.get("usernames", ""),
            "Email": lead.get("emails", ""),
            "Ссылка": lead.get("post_url", ""),
            "Ниша": lead.get("niche", ""),
            "Скоринг": lead.get("lead_score", 0),
            "Просмотры": lead.get("views", 0)
        })

    return jsonify({
        "success": True,
        "stats": result.get("stats", {}),
        "total_leads": len(leads),
        "table_data": table_data,
        "raw_data": leads
    })


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║     🔥 TELEGRAM PARSER PRO - API MODE 🔥         ║
║                                                  ║
║  API для интеграции с n8n                        ║
║                                                  ║
║  Endpoints:                                      ║
║  POST /parse        - запуск парсинга            ║
║  POST /webhook/n8n  - webhook для n8n            ║
║  GET  /status       - статус парсера             ║
║  GET  /results      - последние результаты       ║
║  GET  /results/leads - только лиды с контактами  ║
╚══════════════════════════════════════════════════╝
    """)

    print(f"🚀 Запуск API на http://{CONFIG['host']}:{CONFIG['port']}")
    app.run(host=CONFIG['host'], port=CONFIG['port'], debug=False)
