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

# Загружаем переменные из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv не установлен. Установите: pip install python-dotenv")

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
    "api_id": int(os.environ.get("TELEGRAM_API_ID", "0")),
    "api_hash": os.environ.get("TELEGRAM_API_HASH", ""),
    "phone": os.environ.get("TELEGRAM_PHONE", ""),

    # Proxy настройки
    "proxy_host": os.environ.get("PROXY_HOST", None),
    "proxy_port": int(os.environ.get("PROXY_PORT", 0)) if os.environ.get("PROXY_PORT") else None,
    "proxy_type": os.environ.get("PROXY_TYPE", "socks5"),

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
    "realty_buyers": {
        "keywords": [
            # Прямые запросы на покупку
            "ищу квартиру", "куплю квартиру", "куплю дом", "хочу купить квартиру",
            "ищу недвижимость", "подыскиваю квартиру", "нужна квартира", "нужен дом",
            # По комнатности
            "ищу однушку", "ищу двушку", "ищу трешку", "ищу студию",
            "ищу 1-комнатную", "ищу 2-комнатную", "ищу 3-комнатную",
            "куплю однокомнатную", "куплю двухкомнатную", "куплю трехкомнатную",
            # Бюджет и ипотека
            "бюджет на квартиру", "ипотека одобрена", "одобрили ипотеку",
            "первоначальный взнос", "готов купить за", "в пределах млн",
            # Район и локация
            "посоветуйте район", "какой район лучше", "где лучше купить",
            "рассматриваю районы", "в каком районе", "подскажите новостройку",
            # Тип недвижимости
            "посоветуйте новостройку", "вторичка или новостройка", "от застройщика",
            "ищу таунхаус", "ищу коттедж", "ищу участок под строительство",
            # Срочность
            "срочно ищу квартиру", "нужна квартира срочно", "переезжаем",
            "срок выхода на сделку", "готовы выйти на сделку"
        ],
        "weight": 1.0,
        "description": "Покупатели недвижимости - горячие лиды для риелтора"
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
        # Настройка прокси если указан
        proxy = None
        if CONFIG.get("proxy_host") and CONFIG.get("proxy_port"):
            import socks
            proxy_type = socks.SOCKS5 if CONFIG.get("proxy_type", "socks5").lower() == "socks5" else socks.SOCKS4
            proxy = (proxy_type, CONFIG["proxy_host"], CONFIG["proxy_port"])
            print(f"🔌 Используется прокси: {CONFIG['proxy_host']}:{CONFIG['proxy_port']}")

        self.client = TelegramClient(
            'parser_session_api',
            self.api_id,
            self.api_hash,
            proxy=proxy
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

        # Контакты - главный критерий
        if data.get('phones'):
            score += 35
        if data.get('usernames'):
            score += 20
        if data.get('emails'):
            score += 25

        # Длина текста
        text_len = len(data.get('text', ''))
        if text_len > 100:
            score += 5
        if text_len > 300:
            score += 5

        # Просмотры
        if data.get('views', 0) > 1000:
            score += 5
        if data.get('views', 0) > 10000:
            score += 5

        # Ниша определена (не general/custom)
        niche = data.get('niche', '')
        if niche and niche not in ['general', 'custom']:
            score += 10

        # Количество совпавших ключевых слов
        keywords_count = data.get('keywords_count', 0)
        if keywords_count >= 2:
            score += 5
        if keywords_count >= 3:
            score += 5

        # Штраф за рекламу
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

    async def parse_channel(self, channel_username, keywords_config, messages_limit=100, days_back=7, parse_all=False):
        """
        Парсинг одного канала

        Args:
            channel_username: username канала
            keywords_config: конфиг ключевых слов для фильтрации
            messages_limit: лимит сообщений
            days_back: дней назад
            parse_all: если True - парсим ВСЕ посты без фильтрации по ключевым словам,
                      но всё равно определяем нишу автоматически
        """
        try:
            print(f"[PARSER] Getting entity for: {channel_username}")
            print(f"[PARSER] Mode: {'PARSE ALL' if parse_all else 'FILTER BY KEYWORDS'}")
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

                # Определяем нишу и ключевые слова
                if parse_all:
                    # Режим "все посты" - автоопределение ниши по NICHE_KEYWORDS
                    niche, keyword, all_matches = self.detect_niche_auto(text)
                    # Если ниша не определена - ставим "general"
                    if not niche:
                        niche = "general"
                        keyword = ""
                        all_matches = {}
                else:
                    # Режим фильтрации - сначала проверяем пользовательские ключевые слова
                    niche, keyword, all_matches = self.detect_niche(text, keywords_config)
                    if not niche:
                        continue  # Пропускаем если нет совпадений

                    # Дополнительно определяем автонишу для обогащения данных
                    auto_niche, auto_keyword, auto_matches = self.detect_niche_auto(text)
                    if auto_niche and auto_niche != "custom":
                        # Добавляем автоопределённые ниши к результату
                        for n, kws in auto_matches.items():
                            if n not in all_matches:
                                all_matches[n] = kws
                        # Если основная ниша "custom", заменяем на автоопределённую
                        if niche == "custom":
                            niche = auto_niche

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

                # Получаем описание ниши
                niche_info = NICHE_KEYWORDS.get(niche, {})
                niche_description = niche_info.get("description", "Общее")
                if niche == "general":
                    niche_description = "Общее"
                elif niche == "custom":
                    niche_description = "Пользовательский фильтр"

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
                    "niche_ru": niche_description,  # Описание ниши на русском
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

    async def parse(self, channels, keywords, messages_limit=100, days_back=7, parse_all=False):
        """
        Основной метод парсинга

        Args:
            channels: список каналов
            keywords: конфиг ключевых слов
            messages_limit: лимит сообщений на канал
            days_back: дней назад
            parse_all: если True - парсим все посты без фильтрации
        """
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
                    days_back,
                    parse_all
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


def run_parser_async(channels, keywords, messages_limit, days_back, parse_all=False):
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
            parser.parse(channels, keywords, messages_limit, days_back, parse_all)
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
        "parse_all": false,
        "async": false
    }

    parse_all: если true - парсит ВСЕ посты с автоопределением ниши (без фильтрации по keywords)
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
    parse_all = data.get("parse_all", False)
    is_async = data.get("async", False)

    if not channels:
        return jsonify({"success": False, "error": "Укажите каналы для парсинга"}), 400

    if is_async:
        # Асинхронный режим - запускаем в фоне
        thread = Thread(
            target=run_parser_async,
            args=(channels, keywords, messages_limit, days_back, parse_all)
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
        run_parser_async(channels, keywords, messages_limit, days_back, parse_all)
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


@app.route('/export', methods=['GET'])
def export_excel():
    """
    Экспорт результатов в Excel файл.

    GET параметры:
    - format: xlsx (по умолчанию) или csv
    - dedupe: true/false - дедупликация по text_hash (по умолчанию true)
    - min_score: минимальный lead_score (по умолчанию 0)
    - has_contacts: true/false - только с контактами
    """
    from flask import send_file
    from io import BytesIO

    if not parser_status["last_results"]:
        return jsonify({"success": False, "error": "Нет результатов для экспорта"}), 404

    results = parser_status["last_results"].get("results", [])

    if not results:
        return jsonify({"success": False, "error": "Нет лидов для экспорта"}), 404

    # Получаем параметры
    export_format = request.args.get("format", "xlsx")
    dedupe = request.args.get("dedupe", "true").lower() == "true"
    min_score = int(request.args.get("min_score", 0))
    has_contacts = request.args.get("has_contacts", "false").lower() == "true"

    # Фильтрация
    filtered = []
    seen_hashes = set()

    for r in results:
        # Дедупликация
        if dedupe:
            text_hash = r.get("text_hash", "")
            if text_hash in seen_hashes:
                continue
            seen_hashes.add(text_hash)

        # Фильтр по скору
        if r.get("lead_score", 0) < min_score:
            continue

        # Фильтр по контактам
        if has_contacts:
            if not (r.get("phones") or r.get("emails") or r.get("usernames")):
                continue

        filtered.append(r)

    # Подготовка данных для экспорта
    export_data = []
    for lead in filtered:
        export_data.append({
            "Дата": lead.get("date", ""),
            "Время": lead.get("timestamp", ""),
            "Канал": lead.get("channel_title", ""),
            "Подписчики": lead.get("subscribers", 0),
            "Текст": lead.get("text", ""),
            "Телефон": lead.get("phones", ""),
            "Username": lead.get("usernames", ""),
            "Email": lead.get("emails", ""),
            "Ссылки": lead.get("links", ""),
            "Post URL": lead.get("post_url", ""),
            "Ниша": lead.get("niche_ru", "") or lead.get("niche", ""),
            "Ключевое слово": lead.get("keyword_matched", ""),
            "Все ключевые": lead.get("keywords_all", ""),
            "Скоринг": lead.get("lead_score", 0),
            "Просмотры": lead.get("views", 0),
            "Репосты": lead.get("forwards", 0),
            "Реклама": "Да" if lead.get("is_ad") else "Нет"
        })

    df = pd.DataFrame(export_data)

    # Генерация файла
    output = BytesIO()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if export_format == "csv":
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'leads_{timestamp}.csv'
        )
    else:
        # Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Все лиды', index=False)

            # Отдельный лист для горячих лидов (с контактами)
            hot_leads = df[
                (df['Телефон'].str.len() > 0) |
                (df['Email'].str.len() > 0) |
                (df['Username'].str.len() > 0)
            ]
            if not hot_leads.empty:
                hot_leads.to_excel(writer, sheet_name='Горячие лиды', index=False)

            # Лист со статистикой
            stats_data = {
                "Метрика": [
                    "Всего лидов",
                    "Уникальных лидов",
                    "С телефоном",
                    "С email",
                    "С username",
                    "Горячих лидов (с контактами)",
                    "Средний скоринг"
                ],
                "Значение": [
                    len(results),
                    len(filtered),
                    len(df[df['Телефон'].str.len() > 0]),
                    len(df[df['Email'].str.len() > 0]),
                    len(df[df['Username'].str.len() > 0]),
                    len(hot_leads),
                    round(df['Скоринг'].mean(), 1) if not df.empty else 0
                ]
            }
            pd.DataFrame(stats_data).to_excel(writer, sheet_name='Статистика', index=False)

        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'leads_{timestamp}.xlsx'
        )


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
    parse_all = False  # Режим парсинга всех постов

    if isinstance(keywords_input, str):
        keywords_list = [k.strip() for k in keywords_input.split(",") if k.strip()]
        if keywords_list:
            keywords = {"custom": keywords_list}
        else:
            # Если ключевые слова пустые - парсим ВСЕ посты с автоопределением ниши
            keywords = {}
            parse_all = True
    else:
        keywords = keywords_input
        if not keywords:
            parse_all = True

    # Явный параметр parse_all из запроса (переопределяет автоопределение)
    if data.get("parse_all"):
        parse_all = True

    print(f"[N8N WEBHOOK] Parsed keywords: {keywords}")
    print(f"[N8N WEBHOOK] Parse all mode: {parse_all}")

    messages_limit = int(data.get("messages_limit", 100))
    days_back = int(data.get("days_back", 7))

    print(f"[N8N WEBHOOK] messages_limit={messages_limit}, days_back={days_back}")

    if not channels:
        return jsonify({"success": False, "error": "Укажите каналы"}), 400

    # Запускаем парсинг синхронно
    run_parser_async(channels, keywords, messages_limit, days_back, parse_all)

    result = parser_status["last_results"]

    if not result or not result.get("success"):
        return jsonify(result or {"success": False, "error": "Ошибка парсинга"}), 500

    # Параметр дедупликации (по умолчанию включен)
    dedupe = data.get("dedupe", True)
    if isinstance(dedupe, str):
        dedupe = dedupe.lower() == "true"

    # Форматируем для n8n (плоская структура для таблицы)
    all_leads = result.get("results", [])

    # Дедупликация по text_hash
    if dedupe:
        seen_hashes = set()
        leads = []
        for lead in all_leads:
            text_hash = lead.get("text_hash", "")
            if text_hash and text_hash in seen_hashes:
                continue
            seen_hashes.add(text_hash)
            leads.append(lead)
        duplicates_removed = len(all_leads) - len(leads)
    else:
        leads = all_leads
        duplicates_removed = 0

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
            "Ниша": lead.get("niche_ru", "") or lead.get("niche", ""),  # Используем русское название
            "Ниша_код": lead.get("niche", ""),  # Код ниши для фильтрации
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
        "total_before_dedupe": len(all_leads),
        "duplicates_removed": duplicates_removed,
        "channels_requested": result.get("channels_requested", 0),
        "channels_processed": result.get("channels_processed", 0),
        "channel_errors": result.get("channel_errors", []),
        "debug": {
            "channels_input": channels,
            "keywords_input": keywords,
            "messages_limit": messages_limit,
            "days_back": days_back,
            "parse_all": parse_all,
            "dedupe": dedupe
        },
        "table_data": table_data,
        "raw_data": leads,
        "export_url": f"/export?dedupe={str(dedupe).lower()}"
    })


if __name__ == "__main__":
    # Проверка конфигурации
    if CONFIG["api_id"] == 0 or not CONFIG["api_hash"]:
        print("❌ ОШИБКА: Не настроены Telegram API credentials!")
        print("   Создайте файл .env с переменными:")
        print("   TELEGRAM_API_ID=ваш_api_id")
        print("   TELEGRAM_API_HASH=ваш_api_hash")
        print("   TELEGRAM_PHONE=+7xxxxxxxxxx")
        print("\n   Или установите переменные окружения.")
        exit(1)

    print("""
╔═══════════════════════════════════════════════════════════╗
║     🔥 TELEGRAM PARSER PRO - API MODE 🔥                  ║
║                                                           ║
║  API для интеграции с n8n + Excel экспорт                 ║
║                                                           ║
║  Endpoints:                                               ║
║  POST /parse          - запуск парсинга                   ║
║  POST /webhook/n8n    - webhook для n8n (+ дедупликация)  ║
║  GET  /status         - статус парсера                    ║
║  GET  /results        - последние результаты              ║
║  GET  /results/leads  - только лиды с контактами          ║
║  GET  /results/filter - фильтрация по keyword_matched     ║
║  GET  /niches         - список ниш с ключевыми словами    ║
║  GET  /export         - 📥 СКАЧАТЬ EXCEL/CSV              ║
║                                                           ║
║  Новые фичи:                                              ║
║  ✅ parse_all - парсинг ВСЕХ постов с автониш ой          ║
║  ✅ dedupe - дедупликация по text_hash                    ║
║  ✅ Excel с 3 листами (все/горячие/статистика)            ║
╚═══════════════════════════════════════════════════════════╝
    """)

    print(f"🚀 Запуск API на http://{CONFIG['host']}:{CONFIG['port']}")
    app.run(host=CONFIG['host'], port=CONFIG['port'], debug=False)
