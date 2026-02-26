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

# ============== АВТООПРЕДЕЛЕНИЕ НИШ ПО КЛЮЧЕВЫМ СЛОВАМ ==============
NICHE_KEYWORDS = {
    "leads": {
        "keywords": [
            "ищу", "куплю", "нужен", "требуется", "закажу", "где найти", "посоветуйте",
            "подскажите", "кто может", "кто знает", "помогите найти", "срочно нужен",
            "ищем", "нужна помощь", "кто делает", "кто продаёт", "где купить",
            "могу купить", "готов купить", "хочу заказать", "ищу подрядчика"
        ],
        "weight": 1.0,
        "description": "Горячие лиды - люди которые ищут товар/услугу"
    },
    "discounts": {
        "keywords": [
            "скидка", "акция", "распродажа", "промокод", "халява", "бесплатно",
            "розыгрыш", "-50%", "-70%", "sale", "черная пятница", "киберпонедельник",
            "специальная цена", "только сегодня", "ограниченное предложение",
            "выгодная цена", "дешево", "недорого", "по низкой цене", "со скидкой"
        ],
        "weight": 0.7,
        "description": "Акции и скидки"
    },
    "crypto": {
        "keywords": [
            "сигнал", "памп", "buy", "sell", "entry", "target", "stop loss",
            "btc", "eth", "usdt", "биткоин", "эфир", "крипта", "криптовалюта",
            "токен", "альткоин", "defi", "nft", "binance", "bybit", "трейдинг",
            "лонг", "шорт", "позиция", "маржа", "фьючерс", "спот", "холд"
        ],
        "weight": 0.8,
        "description": "Криптовалюта и трейдинг"
    },
    "jobs": {
        "keywords": [
            "вакансия", "удаленка", "remote", "ищем", "зарплата", "оклад",
            "фриланс", "менеджер", "работа", "требуется сотрудник", "набираем",
            "hr", "резюме", "собеседование", "офис", "график", "полная занятость",
            "частичная занятость", "подработка", "стажировка", "испытательный срок"
        ],
        "weight": 0.9,
        "description": "Вакансии и работа"
    },
    "realty": {
        "keywords": [
            "сдам", "сниму", "продам", "куплю квартиру", "комната", "аренда",
            "м²", "этаж", "квартира", "дом", "недвижимость", "ипотека",
            "новостройка", "вторичка", "риэлтор", "агент", "собственник",
            "без комиссии", "долгосрок", "посуточно", "помещение", "офис аренда"
        ],
        "weight": 0.9,
        "description": "Недвижимость"
    },
    "services": {
        "keywords": [
            "услуги", "делаю", "помогу", "настрою", "создам", "разработка",
            "ремонт", "установка", "консультация", "обучение", "курсы",
            "мастер", "специалист", "эксперт", "под ключ", "быстро и качественно",
            "опыт работы", "портфолио", "отзывы", "гарантия"
        ],
        "weight": 0.6,
        "description": "Услуги"
    },
    "auto": {
        "keywords": [
            "авто", "машина", "автомобиль", "продам авто", "куплю авто",
            "запчасти", "сто", "автосервис", "шиномонтаж", "мойка",
            "детейлинг", "полировка", "тюнинг", "пробег", "двигатель"
        ],
        "weight": 0.8,
        "description": "Авто"
    },
    "education": {
        "keywords": [
            "курс", "обучение", "вебинар", "тренинг", "мастер-класс",
            "онлайн-школа", "репетитор", "подготовка", "экзамен", "егэ", "огэ",
            "сертификат", "диплом", "профессия", "навык", "интенсив"
        ],
        "weight": 0.7,
        "description": "Образование"
    },
    "health": {
        "keywords": [
            "врач", "клиника", "медицина", "здоровье", "лечение", "диагностика",
            "анализы", "консультация врача", "стоматолог", "психолог", "массаж",
            "фитнес", "спорт", "диета", "похудение", "wellness"
        ],
        "weight": 0.7,
        "description": "Здоровье и медицина"
    },
    "it": {
        "keywords": [
            "разработка", "программист", "developer", "frontend", "backend",
            "fullstack", "python", "javascript", "react", "node", "api",
            "сайт", "приложение", "бот", "автоматизация", "парсинг", "скрипт"
        ],
        "weight": 0.8,
        "description": "IT и разработка"
    }
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
        """
        Улучшенное определение ниши по ключевым словам.
        Возвращает: (основная_ниша, первое_ключевое_слово, все_совпадения)
        """
        lower_text = text.lower()
        all_matches = {}  # {niche: [matched_keywords]}
        niche_scores = {}  # {niche: score}

        # Если передан пользовательский конфиг (простой формат)
        if keywords_config and isinstance(list(keywords_config.values())[0], list):
            # Простой формат: {"niche": ["kw1", "kw2"]}
            for niche, keywords in keywords_config.items():
                matched = []
                for keyword in keywords:
                    if keyword.lower() in lower_text:
                        matched.append(keyword)
                if matched:
                    all_matches[niche] = matched
                    niche_scores[niche] = len(matched)
        else:
            # Расширенный формат: используем глобальный NICHE_KEYWORDS
            for niche, config in NICHE_KEYWORDS.items():
                keywords = config.get("keywords", [])
                weight = config.get("weight", 1.0)
                matched = []
                for keyword in keywords:
                    if keyword.lower() in lower_text:
                        matched.append(keyword)
                if matched:
                    all_matches[niche] = matched
                    # Скор = количество совпадений * вес ниши
                    niche_scores[niche] = len(matched) * weight

        if not all_matches:
            return None, None, {}

        # Определяем основную нишу по максимальному скору
        primary_niche = max(niche_scores, key=niche_scores.get)
        first_keyword = all_matches[primary_niche][0]

        return primary_niche, first_keyword, all_matches

    def detect_niche_auto(self, text):
        """
        Автоматическое определение ниши без пользовательского конфига.
        Использует глобальный NICHE_KEYWORDS.
        """
        return self.detect_niche(text, None)

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
            print(f"[PARSER] Getting entity for: {channel_username}")
            channel = await self.client.get_entity(channel_username)
            print(f"[PARSER] Found channel: {channel.title} (id={channel.id})")

            try:
                full = await self.client(GetFullChannelRequest(channel))
                subscribers = full.full_chat.participants_count
            except Exception as e:
                print(f"[PARSER] Could not get subscribers: {e}")
                subscribers = 0

            # Дата для фильтрации сообщений (сообщения новее этой даты)
            min_date = datetime.now() - timedelta(days=days_back)
            print(f"[PARSER] Filtering messages newer than: {min_date}")

            # Получаем последние сообщения БЕЗ offset_date
            # offset_date в Telegram API возвращает сообщения СТАРШЕ указанной даты
            # Поэтому получаем последние сообщения и фильтруем по дате
            messages = await self.client(GetHistoryRequest(
                peer=channel,
                limit=messages_limit,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            print(f"[PARSER] Received {len(messages.messages)} messages from API")

            channel_results = []
            messages_with_text = 0
            messages_in_date_range = 0

            for msg in messages.messages:
                if not msg.message:
                    continue

                messages_with_text += 1

                # Фильтруем по дате - пропускаем сообщения старше min_date
                if msg.date.replace(tzinfo=None) < min_date:
                    continue

                messages_in_date_range += 1
                self.stats['total_messages'] += 1
                text = msg.message

                niche, keyword, all_matches = self.detect_niche(text, keywords_config)
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

                # Подготовка данных о совпадениях
                all_keywords_list = []
                for niche_name, kw_list in all_matches.items():
                    all_keywords_list.extend(kw_list)

                # Количество совпадений для фильтрации
                keywords_count = len(all_keywords_list)
                niches_matched = list(all_matches.keys())

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
                    "keywords_all": ", ".join(all_keywords_list),  # Все совпавшие ключевые слова
                    "keywords_count": keywords_count,  # Количество совпадений для фильтрации
                    "niches_matched": ", ".join(niches_matched),  # Все определённые ниши
                    "niches_count": len(niches_matched),  # Количество ниш
                    "is_ad": self.is_advertisement(text),
                    "post_url": f"https://t.me/{channel.username}/{msg.id}" if channel.username else f"https://t.me/c/{channel.id}/{msg.id}",
                    "message_id": msg.id,
                    "text_hash": hashlib.md5(text.encode()).hexdigest()[:16]
                }

                data['lead_score'] = self.calculate_lead_score(data)
                channel_results.append(data)

            print(f"[PARSER] Channel {channel_username}: {messages_with_text} with text, {messages_in_date_range} in date range, {len(channel_results)} matched keywords")
            return channel_results

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"[PARSER] ERROR for {channel_username}: {e}")
            print(f"[PARSER] Traceback: {error_details}")
            return {"error": str(e), "traceback": error_details}

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
        channel_errors = []
        channels_processed = 0

        await self.start()

        try:
            for channel in channels:
                print(f"[PARSER] Processing channel: {channel}")
                results = await self.parse_channel(
                    channel,
                    keywords,
                    messages_limit,
                    days_back
                )
                if isinstance(results, list):
                    self.results.extend(results)
                    channels_processed += 1
                    print(f"[PARSER] Channel {channel}: found {len(results)} leads")
                elif isinstance(results, dict) and "error" in results:
                    error_msg = f"{channel}: {results['error']}"
                    channel_errors.append(error_msg)
                    print(f"[PARSER] Channel {channel} ERROR: {results['error']}")
                await asyncio.sleep(2)

            self.results.sort(key=lambda x: x.get('lead_score', 0), reverse=True)

            return {
                "success": True,
                "stats": self.stats,
                "results": self.results,
                "results_count": len(self.results),
                "channels_requested": len(channels),
                "channels_processed": channels_processed,
                "channel_errors": channel_errors
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


@app.route('/results/filter', methods=['GET', 'POST'])
def filter_results():
    """
    Фильтрация результатов по keyword_matched и нишам.

    GET параметры или POST JSON:
    - niche: фильтр по нише (leads, crypto, jobs, etc.)
    - keyword: фильтр по конкретному ключевому слову
    - min_keywords: минимальное количество совпавших ключевых слов
    - min_score: минимальный lead_score
    - has_contacts: true/false - только с контактами
    """
    if not parser_status["last_results"]:
        return jsonify({"success": False, "error": "Нет результатов"}), 404

    # Получаем параметры фильтрации
    if request.method == 'POST':
        params = request.get_json() or {}
    else:
        params = request.args.to_dict()

    niche_filter = params.get("niche", "").lower()
    keyword_filter = params.get("keyword", "").lower()
    min_keywords = int(params.get("min_keywords", 0))
    min_score = int(params.get("min_score", 0))
    has_contacts = params.get("has_contacts", "").lower() == "true"

    results = parser_status["last_results"].get("results", [])
    filtered = []

    for r in results:
        # Фильтр по нише
        if niche_filter:
            niches = r.get("niches_matched", "").lower()
            if niche_filter not in niches:
                continue

        # Фильтр по ключевому слову
        if keyword_filter:
            keywords = r.get("keywords_all", "").lower()
            if keyword_filter not in keywords:
                continue

        # Фильтр по минимальному количеству ключевых слов
        if min_keywords > 0:
            if r.get("keywords_count", 0) < min_keywords:
                continue

        # Фильтр по минимальному скору
        if min_score > 0:
            if r.get("lead_score", 0) < min_score:
                continue

        # Фильтр только с контактами
        if has_contacts:
            if not (r.get("phones") or r.get("emails") or r.get("usernames")):
                continue

        filtered.append(r)

    return jsonify({
        "success": True,
        "total_results": len(results),
        "filtered_count": len(filtered),
        "filters_applied": {
            "niche": niche_filter or None,
            "keyword": keyword_filter or None,
            "min_keywords": min_keywords,
            "min_score": min_score,
            "has_contacts": has_contacts
        },
        "results": filtered
    })


@app.route('/niches', methods=['GET'])
def get_niches():
    """Получить список доступных ниш с ключевыми словами"""
    niches_info = {}
    for niche, config in NICHE_KEYWORDS.items():
        niches_info[niche] = {
            "description": config.get("description", ""),
            "weight": config.get("weight", 1.0),
            "keywords_count": len(config.get("keywords", [])),
            "keywords_sample": config.get("keywords", [])[:10]  # Первые 10 для примера
        }
    return jsonify({
        "success": True,
        "niches_count": len(NICHE_KEYWORDS),
        "niches": niches_info
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
    channels_raw = data.get("channels") or data.get("channel", "")
    # Если channels - строка, разбиваем по запятой
    if isinstance(channels_raw, str):
        channels = [c.strip() for c in channels_raw.split(",") if c.strip()]
    else:
        channels = [c.strip() for c in channels_raw if c.strip()]

    print(f"[N8N WEBHOOK] Parsed channels: {channels}")

    # Ключевые слова могут быть строкой или списком
    keywords_input = data.get("keywords", "")
    if isinstance(keywords_input, str):
        keywords_list = [k.strip() for k in keywords_input.split(",") if k.strip()]
        keywords = {"custom": keywords_list}
    else:
        keywords = keywords_input

    print(f"[N8N WEBHOOK] Parsed keywords: {keywords}")

    messages_limit = int(data.get("messages_limit", 100))
    days_back = int(data.get("days_back", 7))

    print(f"[N8N WEBHOOK] messages_limit={messages_limit}, days_back={days_back}")

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
            "Ключевое_слово": lead.get("keyword_matched", ""),
            "Все_ключевые": lead.get("keywords_all", ""),
            "Кол_во_ключевых": lead.get("keywords_count", 0),
            "Все_ниши": lead.get("niches_matched", ""),
            "Скоринг": lead.get("lead_score", 0),
            "Просмотры": lead.get("views", 0)
        })

    return jsonify({
        "success": True,
        "stats": result.get("stats", {}),
        "total_leads": len(leads),
        "channels_requested": result.get("channels_requested", 0),
        "channels_processed": result.get("channels_processed", 0),
        "channel_errors": result.get("channel_errors", []),
        "debug": {
            "channels_input": channels,
            "keywords_input": keywords,
            "messages_limit": messages_limit,
            "days_back": days_back
        },
        "table_data": table_data,
        "raw_data": leads
    })


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════╗
║     🔥 TELEGRAM PARSER PRO - API MODE 🔥              ║
║                                                       ║
║  API для интеграции с n8n                             ║
║                                                       ║
║  Endpoints:                                           ║
║  POST /parse          - запуск парсинга               ║
║  POST /webhook/n8n    - webhook для n8n               ║
║  GET  /status         - статус парсера                ║
║  GET  /results        - последние результаты          ║
║  GET  /results/leads  - только лиды с контактами      ║
║  GET  /results/filter - фильтрация по keyword_matched ║
║  GET  /niches         - список ниш с ключевыми словами║
╚═══════════════════════════════════════════════════════╝
    """)

    print(f"🚀 Запуск API на http://{CONFIG['host']}:{CONFIG['port']}")
    app.run(host=CONFIG['host'], port=CONFIG['port'], debug=False)
