#!/usr/bin/env python3
"""
TELEGRAM CHANNEL FINDER BOT

Автоматический поиск каналов под нишу клиента
Команда: /найди недвижимость Москва

Функции:
- Парсинг TGStat и Telega.in
- Проверка живых ссылок через Telethon
- Скоринг и ранжирование каналов
- Топ-20 результатов с детальной статистикой
"""

import asyncio
import re
import json
import os
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import quote, urljoin
import aiohttp
from bs4 import BeautifulSoup

# Telegram libraries
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode

try:
    from telethon import TelegramClient
    from telethon.tl.functions.channels import GetFullChannelRequest
    from telethon.errors import ChannelPrivateError, UsernameNotOccupiedError, FloodWaitError
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    print("Telethon не установлен. Валидация каналов будет ограничена.")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('channel_finder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============== КОНФИГУРАЦИЯ ==============
CONFIG = {
    # Telegram Bot Token (получить у @BotFather)
    "bot_token": os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN"),

    # Telegram API для Telethon (получить на https://my.telegram.org)
    "api_id": os.environ.get("TELEGRAM_API_ID", ""),
    "api_hash": os.environ.get("TELEGRAM_API_HASH", ""),
    "phone": os.environ.get("TELEGRAM_PHONE", ""),

    # Proxy настройки (опционально)
    "proxy_host": os.environ.get("PROXY_HOST", None),
    "proxy_port": int(os.environ.get("PROXY_PORT", 0)) if os.environ.get("PROXY_PORT") else None,

    # Настройки поиска
    "max_channels": 50,  # Максимум каналов для проверки
    "top_results": 20,   # Топ результатов для отправки
    "cache_ttl": 3600,   # Кэш в секундах (1 час)

    # User-Agent для парсинга
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ============== КАТЕГОРИИ НИШ ==============
NICHE_CATEGORIES = {
    "недвижимость": {
        "keywords": ["недвижимость", "квартира", "аренда", "риэлтор", "новостройка", "ипотека"],
        "tgstat_category": "realty",
        "telega_category": "nedvizhimost"
    },
    "крипта": {
        "keywords": ["крипто", "bitcoin", "трейдинг", "криптовалюта", "биткоин", "блокчейн"],
        "tgstat_category": "crypto",
        "telega_category": "kriptovalyuty"
    },
    "бизнес": {
        "keywords": ["бизнес", "стартап", "предприниматель", "инвестиции", "маркетинг"],
        "tgstat_category": "business",
        "telega_category": "biznes"
    },
    "работа": {
        "keywords": ["вакансия", "работа", "удаленка", "фриланс", "карьера", "hr"],
        "tgstat_category": "job",
        "telega_category": "vakansii"
    },
    "авто": {
        "keywords": ["авто", "машина", "автомобиль", "тюнинг", "запчасти"],
        "tgstat_category": "auto",
        "telega_category": "avto"
    },
    "it": {
        "keywords": ["программирование", "разработка", "it", "код", "python", "javascript"],
        "tgstat_category": "tech",
        "telega_category": "it"
    },
    "красота": {
        "keywords": ["красота", "косметика", "маникюр", "салон", "визаж"],
        "tgstat_category": "beauty",
        "telega_category": "krasota"
    },
    "здоровье": {
        "keywords": ["здоровье", "медицина", "фитнес", "спорт", "питание", "диета"],
        "tgstat_category": "health",
        "telega_category": "zdorove"
    },
    "образование": {
        "keywords": ["обучение", "курсы", "образование", "школа", "репетитор"],
        "tgstat_category": "education",
        "telega_category": "obrazovanie"
    },
    "новости": {
        "keywords": ["новости", "события", "политика", "экономика"],
        "tgstat_category": "news",
        "telega_category": "novosti"
    }
}

# ============== ГОРОДА ==============
CITIES = {
    "москва": {"tgstat": "moscow", "telega": "moskva", "region": "RU"},
    "спб": {"tgstat": "spb", "telega": "sankt-peterburg", "region": "RU"},
    "санкт-петербург": {"tgstat": "spb", "telega": "sankt-peterburg", "region": "RU"},
    "питер": {"tgstat": "spb", "telega": "sankt-peterburg", "region": "RU"},
    "казань": {"tgstat": "kazan", "telega": "kazan", "region": "RU"},
    "екатеринбург": {"tgstat": "ekaterinburg", "telega": "ekaterinburg", "region": "RU"},
    "новосибирск": {"tgstat": "novosibirsk", "telega": "novosibirsk", "region": "RU"},
    "краснодар": {"tgstat": "krasnodar", "telega": "krasnodar", "region": "RU"},
    "сочи": {"tgstat": "sochi", "telega": "sochi", "region": "RU"},
    "киев": {"tgstat": "kiev", "telega": "kiev", "region": "UA"},
    "минск": {"tgstat": "minsk", "telega": "minsk", "region": "BY"},
    "алматы": {"tgstat": "almaty", "telega": "almaty", "region": "KZ"},
    "ташкент": {"tgstat": "tashkent", "telega": "tashkent", "region": "UZ"},
    "дубай": {"tgstat": "dubai", "telega": "dubai", "region": "AE"},
}


@dataclass
class ChannelInfo:
    """Информация о канале"""
    username: str
    title: str
    subscribers: int
    avg_views: int = 0
    er: float = 0.0  # Engagement Rate
    posts_per_day: float = 0.0
    description: str = ""
    category: str = ""
    link: str = ""
    source: str = ""  # tgstat, telega, manual
    is_verified: bool = False
    is_alive: bool = True
    last_post_date: str = ""
    price_estimate: str = ""
    score: int = 0

    def calculate_score(self) -> int:
        """Расчет скора канала (0-100)"""
        score = 0

        # Подписчики (до 30 баллов)
        if self.subscribers >= 100000:
            score += 30
        elif self.subscribers >= 50000:
            score += 25
        elif self.subscribers >= 10000:
            score += 20
        elif self.subscribers >= 5000:
            score += 15
        elif self.subscribers >= 1000:
            score += 10
        else:
            score += 5

        # ER - Engagement Rate (до 25 баллов)
        if self.er >= 50:
            score += 25
        elif self.er >= 30:
            score += 20
        elif self.er >= 15:
            score += 15
        elif self.er >= 5:
            score += 10
        elif self.er > 0:
            score += 5

        # Средние просмотры (до 20 баллов)
        if self.avg_views >= 10000:
            score += 20
        elif self.avg_views >= 5000:
            score += 15
        elif self.avg_views >= 1000:
            score += 10
        elif self.avg_views >= 500:
            score += 5

        # Активность постов (до 15 баллов)
        if self.posts_per_day >= 3:
            score += 15
        elif self.posts_per_day >= 1:
            score += 10
        elif self.posts_per_day >= 0.5:
            score += 5

        # Живой канал (10 баллов)
        if self.is_alive:
            score += 10

        self.score = min(100, score)
        return self.score


class ChannelCache:
    """Кэш результатов поиска"""

    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Tuple[datetime, List[ChannelInfo]]] = {}
        self.ttl = ttl

    def get_key(self, niche: str, city: str) -> str:
        return hashlib.md5(f"{niche}:{city}".lower().encode()).hexdigest()

    def get(self, niche: str, city: str) -> Optional[List[ChannelInfo]]:
        key = self.get_key(niche, city)
        if key in self.cache:
            timestamp, data = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                logger.info(f"Cache hit for {niche} {city}")
                return data
            else:
                del self.cache[key]
        return None

    def set(self, niche: str, city: str, data: List[ChannelInfo]):
        key = self.get_key(niche, city)
        self.cache[key] = (datetime.now(), data)
        logger.info(f"Cached {len(data)} channels for {niche} {city}")


class TGStatParser:
    """Парсер TGStat.ru"""

    BASE_URL = "https://tgstat.ru"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if not self.session or self.session.closed:
            headers = {
                "User-Agent": CONFIG["user_agent"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def search_channels(self, niche: str, city: str = "", limit: int = 50) -> List[ChannelInfo]:
        """Поиск каналов на TGStat"""
        channels = []

        try:
            session = await self.get_session()

            # Определяем категорию
            niche_config = NICHE_CATEGORIES.get(niche.lower(), {})
            category = niche_config.get("tgstat_category", "")

            # Определяем город
            city_config = CITIES.get(city.lower(), {})
            city_param = city_config.get("tgstat", "")

            # Формируем поисковый запрос
            search_query = quote(f"{niche} {city}".strip())

            # URL для поиска
            search_url = f"{self.BASE_URL}/channels/search?q={search_query}"
            if category:
                search_url = f"{self.BASE_URL}/channels/category/{category}"
                if city_param:
                    search_url += f"?city={city_param}"

            logger.info(f"TGStat search URL: {search_url}")

            async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    logger.warning(f"TGStat returned status {response.status}")
                    return channels

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Парсим карточки каналов
                channel_cards = soup.select('.channel-card, .peer-item, [data-channel]')

                for card in channel_cards[:limit]:
                    try:
                        channel = self._parse_channel_card(card)
                        if channel:
                            channel.source = "tgstat"
                            channels.append(channel)
                    except Exception as e:
                        logger.debug(f"Error parsing card: {e}")
                        continue

        except asyncio.TimeoutError:
            logger.warning("TGStat request timeout")
        except Exception as e:
            logger.error(f"TGStat error: {e}")

        return channels

    def _parse_channel_card(self, card) -> Optional[ChannelInfo]:
        """Парсинг карточки канала"""
        try:
            # Ищем username
            link_elem = card.select_one('a[href*="/channel/"]') or card.select_one('a[href*="t.me/"]')
            if not link_elem:
                return None

            href = link_elem.get('href', '')
            username = ""

            if '/channel/@' in href:
                username = href.split('/channel/@')[-1].split('/')[0].split('?')[0]
            elif 't.me/' in href:
                username = href.split('t.me/')[-1].split('/')[0].split('?')[0]
            elif '/channel/' in href:
                username = href.split('/channel/')[-1].split('/')[0].split('?')[0]

            if not username or username.startswith('+'):
                return None

            # Название
            title_elem = card.select_one('.channel-title, .peer-title, h3, h4, .title')
            title = title_elem.get_text(strip=True) if title_elem else username

            # Подписчики
            subs_elem = card.select_one('.channel-subs, .subscribers, [data-subscribers]')
            subscribers = 0
            if subs_elem:
                subs_text = subs_elem.get_text(strip=True)
                subscribers = self._parse_number(subs_text)

            # Средние просмотры
            views_elem = card.select_one('.channel-views, .avg-views, [data-views]')
            avg_views = 0
            if views_elem:
                views_text = views_elem.get_text(strip=True)
                avg_views = self._parse_number(views_text)

            # ER
            er_elem = card.select_one('.channel-er, .er, [data-er]')
            er = 0.0
            if er_elem:
                er_text = er_elem.get_text(strip=True)
                er = self._parse_float(er_text)

            # Описание
            desc_elem = card.select_one('.channel-desc, .description, p')
            description = desc_elem.get_text(strip=True)[:200] if desc_elem else ""

            return ChannelInfo(
                username=username,
                title=title,
                subscribers=subscribers,
                avg_views=avg_views,
                er=er,
                description=description,
                link=f"https://t.me/{username}"
            )

        except Exception as e:
            logger.debug(f"Parse error: {e}")
            return None

    def _parse_number(self, text: str) -> int:
        """Парсинг числа (1.5K, 10M, etc)"""
        text = text.upper().replace(' ', '').replace(',', '.')
        multiplier = 1

        if 'K' in text or 'К' in text:
            multiplier = 1000
            text = text.replace('K', '').replace('К', '')
        elif 'M' in text or 'М' in text:
            multiplier = 1000000
            text = text.replace('M', '').replace('М', '')

        try:
            return int(float(re.sub(r'[^\d.]', '', text) or 0) * multiplier)
        except:
            return 0

    def _parse_float(self, text: str) -> float:
        """Парсинг float из текста"""
        try:
            return float(re.sub(r'[^\d.,]', '', text).replace(',', '.') or 0)
        except:
            return 0.0


class TelegaInParser:
    """Парсер Telega.in"""

    BASE_URL = "https://telega.in"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if not self.session or self.session.closed:
            headers = {
                "User-Agent": CONFIG["user_agent"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def search_channels(self, niche: str, city: str = "", limit: int = 50) -> List[ChannelInfo]:
        """Поиск каналов на Telega.in"""
        channels = []

        try:
            session = await self.get_session()

            # Определяем категорию
            niche_config = NICHE_CATEGORIES.get(niche.lower(), {})
            category = niche_config.get("telega_category", "")

            # Формируем URL
            if category:
                search_url = f"{self.BASE_URL}/catalog/{category}"
            else:
                search_query = quote(f"{niche} {city}".strip())
                search_url = f"{self.BASE_URL}/search?q={search_query}"

            logger.info(f"Telega.in search URL: {search_url}")

            async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    logger.warning(f"Telega.in returned status {response.status}")
                    return channels

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Парсим карточки каналов
                channel_cards = soup.select('.catalog-item, .channel-card, .search-result-item')

                for card in channel_cards[:limit]:
                    try:
                        channel = self._parse_channel_card(card)
                        if channel:
                            channel.source = "telega"
                            channels.append(channel)
                    except Exception as e:
                        logger.debug(f"Error parsing Telega card: {e}")
                        continue

        except asyncio.TimeoutError:
            logger.warning("Telega.in request timeout")
        except Exception as e:
            logger.error(f"Telega.in error: {e}")

        return channels

    def _parse_channel_card(self, card) -> Optional[ChannelInfo]:
        """Парсинг карточки канала"""
        try:
            # Ищем ссылку на канал
            link_elem = card.select_one('a[href*="t.me/"]') or card.select_one('a[href*="/channel/"]')
            if not link_elem:
                return None

            href = link_elem.get('href', '')
            username = ""

            if 't.me/' in href:
                username = href.split('t.me/')[-1].split('/')[0].split('?')[0]
            elif '/channel/' in href:
                username = href.split('/channel/')[-1].split('/')[0].split('?')[0]

            if not username or username.startswith('+'):
                return None

            # Название
            title_elem = card.select_one('.channel-name, .title, h3, h4')
            title = title_elem.get_text(strip=True) if title_elem else username

            # Подписчики
            subs_elem = card.select_one('.subscribers, .subs, .channel-subs')
            subscribers = 0
            if subs_elem:
                subs_text = subs_elem.get_text(strip=True)
                subscribers = self._parse_number(subs_text)

            # Цена
            price_elem = card.select_one('.price, .channel-price')
            price = ""
            if price_elem:
                price = price_elem.get_text(strip=True)

            # Описание
            desc_elem = card.select_one('.description, .channel-desc, p')
            description = desc_elem.get_text(strip=True)[:200] if desc_elem else ""

            return ChannelInfo(
                username=username,
                title=title,
                subscribers=subscribers,
                description=description,
                price_estimate=price,
                link=f"https://t.me/{username}"
            )

        except Exception as e:
            logger.debug(f"Parse error: {e}")
            return None

    def _parse_number(self, text: str) -> int:
        """Парсинг числа"""
        text = text.upper().replace(' ', '').replace(',', '.')
        multiplier = 1

        if 'K' in text or 'К' in text or 'ТЫС' in text:
            multiplier = 1000
            text = re.sub(r'[KКТЫС.]', '', text)
        elif 'M' in text or 'М' in text or 'МЛН' in text:
            multiplier = 1000000
            text = re.sub(r'[MММЛН.]', '', text)

        try:
            return int(float(re.sub(r'[^\d.]', '', text) or 0) * multiplier)
        except:
            return 0


class ChannelValidator:
    """Валидатор каналов через Telethon"""

    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.is_connected = False

    async def connect(self):
        """Подключение к Telegram API"""
        if not TELETHON_AVAILABLE:
            logger.warning("Telethon not available, skipping validation")
            return False

        if not CONFIG.get("api_id") or not CONFIG.get("api_hash"):
            logger.warning("Telegram API credentials not configured")
            return False

        try:
            self.client = TelegramClient(
                'channel_finder_session',
                int(CONFIG["api_id"]),
                CONFIG["api_hash"]
            )
            await self.client.start(phone=CONFIG.get("phone"))
            self.is_connected = True
            logger.info("Telethon connected successfully")
            return True
        except Exception as e:
            logger.error(f"Telethon connection error: {e}")
            return False

    async def disconnect(self):
        """Отключение"""
        if self.client:
            await self.client.disconnect()
            self.is_connected = False

    async def validate_channel(self, username: str) -> Dict:
        """Проверка канала и получение актуальной статистики"""
        result = {
            "is_alive": False,
            "subscribers": 0,
            "title": "",
            "description": "",
            "last_post": None,
            "error": None
        }

        if not self.is_connected or not self.client:
            result["error"] = "Not connected"
            return result

        try:
            # Получаем информацию о канале
            entity = await self.client.get_entity(username)
            full = await self.client(GetFullChannelRequest(entity))

            result["is_alive"] = True
            result["subscribers"] = full.full_chat.participants_count
            result["title"] = entity.title
            result["description"] = full.full_chat.about or ""

            # Получаем последний пост
            async for message in self.client.iter_messages(entity, limit=1):
                if message.date:
                    result["last_post"] = message.date.strftime("%Y-%m-%d")

        except (ChannelPrivateError, UsernameNotOccupiedError):
            result["error"] = "Channel not found or private"
        except FloodWaitError as e:
            result["error"] = f"Rate limit: wait {e.seconds}s"
            logger.warning(f"FloodWait for {username}: {e.seconds}s")
        except Exception as e:
            result["error"] = str(e)

        return result


class ChannelFinderBot:
    """Основной класс бота"""

    def __init__(self):
        self.tgstat = TGStatParser()
        self.telega = TelegaInParser()
        self.validator = ChannelValidator()
        self.cache = ChannelCache(CONFIG["cache_ttl"])
        self.app: Optional[Application] = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик /start"""
        welcome_message = """
<b>Channel Finder Bot</b>

Автоматический поиск Telegram-каналов под вашу нишу.

<b>Как использовать:</b>
/найди [ниша] [город] - поиск каналов

<b>Примеры:</b>
<code>/найди недвижимость Москва</code>
<code>/найди крипта</code>
<code>/найди работа СПб</code>
<code>/найди бизнес Казань</code>

<b>Доступные ниши:</b>
недвижимость, крипта, бизнес, работа, авто, it, красота, здоровье, образование, новости

<b>Доступные города:</b>
Москва, СПб, Казань, Екатеринбург, Новосибирск, Краснодар, Сочи, Киев, Минск, Алматы, Дубай

<b>Другие команды:</b>
/help - справка
/stats - статистика бота
"""
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик /help"""
        help_text = """
<b>Справка по боту</b>

<b>Команда поиска:</b>
/найди [ниша] [город]
или
/find [niche] [city]

Бот ищет каналы на TGStat и Telega.in, проверяет их актуальность и выдает топ-20 лучших каналов.

<b>Что показывается:</b>
- Название и ссылка на канал
- Количество подписчиков
- Средние просмотры и ER
- Скоринг качества (0-100)
- Статус канала (живой/мертвый)

<b>Критерии скоринга:</b>
- Подписчики (до 30 баллов)
- Engagement Rate (до 25 баллов)
- Средние просмотры (до 20 баллов)
- Активность постов (до 15 баллов)
- Живой канал (+10 баллов)

Результаты кэшируются на 1 час.
"""
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

    async def find_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик /найди и /find"""
        args = context.args

        if not args:
            await update.message.reply_text(
                "Укажите нишу для поиска.\n"
                "Пример: <code>/найди недвижимость Москва</code>",
                parse_mode=ParseMode.HTML
            )
            return

        # Парсим аргументы
        query = ' '.join(args).lower()
        niche = ""
        city = ""

        # Определяем нишу
        for n in NICHE_CATEGORIES:
            if n in query:
                niche = n
                query = query.replace(n, '').strip()
                break

        if not niche:
            # Пробуем использовать первое слово как нишу
            niche = args[0].lower()
            query = ' '.join(args[1:]) if len(args) > 1 else ""

        # Определяем город
        for c in CITIES:
            if c in query:
                city = c
                break

        # Отправляем сообщение о начале поиска
        status_msg = await update.message.reply_text(
            f"Ищу каналы по запросу: <b>{niche}</b>" + (f" в городе <b>{city}</b>" if city else "") + "\n\n"
            "Парсинг TGStat...",
            parse_mode=ParseMode.HTML
        )

        try:
            # Проверяем кэш
            cached = self.cache.get(niche, city)
            if cached:
                await status_msg.edit_text(
                    f"Найдено в кэше: {len(cached)} каналов\n"
                    "Формирую результат...",
                    parse_mode=ParseMode.HTML
                )
                channels = cached
            else:
                # Парсим TGStat
                tgstat_channels = await self.tgstat.search_channels(niche, city, CONFIG["max_channels"])
                await status_msg.edit_text(
                    f"TGStat: {len(tgstat_channels)} каналов\n"
                    "Парсинг Telega.in...",
                    parse_mode=ParseMode.HTML
                )

                # Парсим Telega.in
                telega_channels = await self.telega.search_channels(niche, city, CONFIG["max_channels"])
                await status_msg.edit_text(
                    f"TGStat: {len(tgstat_channels)} каналов\n"
                    f"Telega.in: {len(telega_channels)} каналов\n"
                    "Объединение и валидация...",
                    parse_mode=ParseMode.HTML
                )

                # Объединяем и дедуплицируем
                channels = self._merge_channels(tgstat_channels, telega_channels)

                # Валидация через Telethon (если доступно)
                if self.validator.is_connected:
                    await status_msg.edit_text(
                        f"Найдено: {len(channels)} уникальных каналов\n"
                        "Проверка живых ссылок...",
                        parse_mode=ParseMode.HTML
                    )
                    channels = await self._validate_channels(channels)

                # Сохраняем в кэш
                self.cache.set(niche, city, channels)

            # Рассчитываем скоры и сортируем
            for ch in channels:
                ch.calculate_score()
            channels.sort(key=lambda x: x.score, reverse=True)

            # Берем топ
            top_channels = channels[:CONFIG["top_results"]]

            # Удаляем статусное сообщение
            await status_msg.delete()

            # Отправляем результаты
            await self._send_results(update, niche, city, top_channels, len(channels))

        except Exception as e:
            logger.error(f"Search error: {e}")
            await status_msg.edit_text(
                f"Ошибка при поиске: {str(e)}\n"
                "Попробуйте позже.",
                parse_mode=ParseMode.HTML
            )

    def _merge_channels(self, list1: List[ChannelInfo], list2: List[ChannelInfo]) -> List[ChannelInfo]:
        """Объединение и дедупликация каналов"""
        seen = {}

        for ch in list1 + list2:
            username = ch.username.lower().strip('@')
            if username in seen:
                # Обновляем данные если новые лучше
                existing = seen[username]
                if ch.subscribers > existing.subscribers:
                    existing.subscribers = ch.subscribers
                if ch.avg_views > existing.avg_views:
                    existing.avg_views = ch.avg_views
                if ch.er > existing.er:
                    existing.er = ch.er
                if not existing.description and ch.description:
                    existing.description = ch.description
            else:
                seen[username] = ch

        return list(seen.values())

    async def _validate_channels(self, channels: List[ChannelInfo]) -> List[ChannelInfo]:
        """Валидация каналов через Telethon"""
        validated = []

        for ch in channels:
            try:
                result = await self.validator.validate_channel(ch.username)

                if result["is_alive"]:
                    ch.is_alive = True
                    ch.subscribers = result["subscribers"] or ch.subscribers
                    ch.title = result["title"] or ch.title
                    ch.last_post_date = result["last_post"] or ""
                    validated.append(ch)
                else:
                    ch.is_alive = False
                    # Включаем мертвые каналы с пометкой
                    validated.append(ch)

                await asyncio.sleep(0.5)  # Антифлуд

            except Exception as e:
                logger.debug(f"Validation error for {ch.username}: {e}")
                ch.is_alive = True  # Считаем живым если не смогли проверить
                validated.append(ch)

        return validated

    async def _send_results(self, update: Update, niche: str, city: str, channels: List[ChannelInfo], total: int):
        """Отправка результатов"""
        if not channels:
            await update.message.reply_text(
                f"По запросу <b>{niche}</b>" + (f" {city}" if city else "") + " каналы не найдены.\n"
                "Попробуйте другую нишу или уберите город.",
                parse_mode=ParseMode.HTML
            )
            return

        # Заголовок
        header = (
            f"<b>Топ-{len(channels)} каналов по запросу:</b>\n"
            f"<b>{niche.title()}</b>" + (f" | {city.title()}" if city else "") + "\n"
            f"<i>Найдено: {total} каналов</i>\n"
            f"{'─' * 30}\n\n"
        )

        # Формируем список
        messages = [header]
        current_msg = header

        for i, ch in enumerate(channels, 1):
            # Эмодзи для статуса
            status = "" if ch.is_alive else ""
            score_emoji = "" if ch.score >= 70 else "" if ch.score >= 40 else ""

            # Форматирование подписчиков
            subs_str = self._format_number(ch.subscribers)
            views_str = self._format_number(ch.avg_views) if ch.avg_views else "-"
            er_str = f"{ch.er:.1f}%" if ch.er else "-"

            channel_text = (
                f"{i}. {status} <b>{ch.title[:30]}</b>\n"
                f"   @{ch.username}\n"
                f"   {subs_str} подп. | {views_str} просм. | ER: {er_str}\n"
                f"   {score_emoji} Скор: {ch.score}/100"
            )

            if ch.price_estimate:
                channel_text += f" | {ch.price_estimate}"
            if ch.last_post_date:
                channel_text += f"\n   Последний пост: {ch.last_post_date}"

            channel_text += "\n\n"

            # Проверяем длину сообщения
            if len(current_msg) + len(channel_text) > 4000:
                messages.append(current_msg)
                current_msg = channel_text
            else:
                current_msg += channel_text

        if current_msg and current_msg != header:
            messages.append(current_msg)

        # Отправляем сообщения
        for msg in messages:
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            await asyncio.sleep(0.3)

        # Кнопки действий
        keyboard = [
            [
                InlineKeyboardButton("Обновить", callback_data=f"refresh:{niche}:{city}"),
                InlineKeyboardButton("Экспорт CSV", callback_data=f"export:{niche}:{city}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "<i>Результаты кэшируются на 1 час</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

    def _format_number(self, num: int) -> str:
        """Форматирование числа"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        return str(num)

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback кнопок"""
        query = update.callback_query
        await query.answer()

        data = query.data.split(':')
        action = data[0]

        if action == "refresh":
            niche = data[1] if len(data) > 1 else ""
            city = data[2] if len(data) > 2 else ""

            # Очищаем кэш
            key = self.cache.get_key(niche, city)
            if key in self.cache.cache:
                del self.cache.cache[key]

            await query.edit_message_text("Кэш очищен. Используйте /найди для нового поиска.")

        elif action == "export":
            niche = data[1] if len(data) > 1 else ""
            city = data[2] if len(data) > 2 else ""

            cached = self.cache.get(niche, city)
            if cached:
                # Генерируем CSV
                csv_content = "username,title,subscribers,avg_views,er,score,link\n"
                for ch in cached:
                    csv_content += f"@{ch.username},{ch.title},{ch.subscribers},{ch.avg_views},{ch.er},{ch.score},{ch.link}\n"

                # Отправляем как файл
                from io import BytesIO
                csv_bytes = BytesIO(csv_content.encode('utf-8'))
                csv_bytes.name = f"channels_{niche}_{city or 'all'}.csv"

                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=csv_bytes,
                    caption=f"Каналы по запросу: {niche} {city or ''}"
                )
            else:
                await query.edit_message_text("Данные не найдены. Выполните поиск заново.")

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статистика бота"""
        cache_count = len(self.cache.cache)
        telethon_status = "Подключен" if self.validator.is_connected else "Не подключен"

        stats_text = f"""
<b>Статистика бота</b>

Кэшированных запросов: {cache_count}
Telethon: {telethon_status}
Время кэша: {CONFIG['cache_ttl']} сек.
"""
        await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)

    async def text_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text.lower().strip()

        # Приветствия
        greetings = ['привет', 'здравствуй', 'hi', 'hello', 'хай', 'прив', 'здарова', 'добрый день', 'доброе утро', 'добрый вечер']
        if any(g in text for g in greetings):
            await update.message.reply_text(
                "Привет! 👋\n\n"
                "Я помогу найти Telegram-каналы под вашу нишу.\n\n"
                "Используйте команду:\n"
                "<code>/найди недвижимость Москва</code>\n\n"
                "Или введите /help для справки.",
                parse_mode=ParseMode.HTML
            )
            return

        # Попытка распознать запрос на поиск
        for niche in NICHE_CATEGORIES:
            if niche in text:
                # Определяем город
                city = ""
                for c in CITIES:
                    if c in text:
                        city = c
                        break

                context.args = [niche]
                if city:
                    context.args.append(city)

                await self.find_command(update, context)
                return

        # Неизвестное сообщение
        await update.message.reply_text(
            "Не понял запрос. 🤔\n\n"
            "Попробуйте:\n"
            "<code>/найди недвижимость Москва</code>\n"
            "<code>/найди крипта</code>\n"
            "<code>/найди работа СПб</code>\n\n"
            "Или /help для списка команд.",
            parse_mode=ParseMode.HTML
        )

    async def run(self):
        """Запуск бота"""
        # Создаем приложение
        self.app = Application.builder().token(CONFIG["bot_token"]).build()

        # Регистрируем обработчики
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("найди", self.find_command))
        self.app.add_handler(CommandHandler("find", self.find_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
        self.app.add_handler(CallbackQueryHandler(self.callback_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_message_handler))

        # Подключаем Telethon для валидации
        if TELETHON_AVAILABLE and CONFIG.get("api_id"):
            await self.validator.connect()

        logger.info("Bot started!")

        # Запускаем polling
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(drop_pending_updates=True)

        # Ждем остановки
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Очистка ресурсов"""
        await self.tgstat.close()
        await self.telega.close()
        await self.validator.disconnect()
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()


def main():
    """Точка входа"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║         TELEGRAM CHANNEL FINDER BOT                       ║
║                                                           ║
║  Автоматический поиск каналов под нишу клиента            ║
║                                                           ║
║  Команды:                                                 ║
║  /найди [ниша] [город] - поиск каналов                    ║
║  /help - справка                                          ║
║  /stats - статистика                                      ║
║                                                           ║
║  Источники: TGStat, Telega.in                             ║
║  Валидация: Telethon API                                  ║
╚═══════════════════════════════════════════════════════════╝
    """)

    if CONFIG["bot_token"] == "YOUR_BOT_TOKEN":
        print("ОШИБКА: Укажите BOT_TOKEN в переменных окружения!")
        print("export BOT_TOKEN='ваш_токен_от_BotFather'")
        return

    bot = ChannelFinderBot()
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
