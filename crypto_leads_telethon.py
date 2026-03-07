#!/usr/bin/env python3
"""
Crypto Leads Parser на Telethon
Парсит крипто-каналы через Telegram API для извлечения лидов

Установка:
pip install telethon pandas openpyxl aiohttp python-dotenv

Получить api_id и api_hash: https://my.telegram.org/apps
"""

import asyncio
import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, asdict

try:
    from telethon import TelegramClient
    from telethon.tl.functions.channels import GetFullChannelRequest
    from telethon.tl.functions.messages import GetHistoryRequest
    from telethon.tl.types import Channel, Chat
    from telethon.errors import ChannelPrivateError, UsernameNotOccupiedError
    import pandas as pd
    import aiohttp
except ImportError:
    print("Установите зависимости: pip install telethon pandas openpyxl aiohttp")
    exit(1)

from dotenv import load_dotenv
load_dotenv()

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class CryptoLead:
    """Структура крипто-лида"""
    username: str
    source_channel: str
    channel_subscribers: int
    message_text: str
    message_views: int
    message_date: str
    post_url: str
    score: int
    lead_type: str  # trader, investor, whale, signal_seeker
    contacts: Dict
    parsed_at: str


class CryptoLeadsTelethon:
    """Парсер крипто-лидов через Telethon API"""

    # Крипто-каналы для парсинга
    DEFAULT_CHANNELS = [
        # Русскоязычные крипто-каналы
        "CryptoVestnik",
        "CryptoStonks",
        "cryptonews_ru",
        "bitcoin_ru",
        "crypto_mining_ru",
        "tradersclub_ru",
        "binance_russian",
        "bybit_russian_official",

        # NFT и DeFi
        "nft_russia",
        "defi_russia",

        # Трейдинг
        "crypto_signals_free",
        "trading_crypto_ru",
        "altcoins_russia",

        # Новости
        "bits_media",
        "forklog",
        "coinpost_ru",

        # Англоязычные
        "cryptonews",
        "bitcoin",
        "binanceexchange",
        "CoinGecko",
    ]

    # Ключевые слова для определения типа лида
    LEAD_KEYWORDS = {
        "trader": ["trade", "trading", "сигнал", "signal", "buy", "sell", "long", "short", "entry"],
        "investor": ["invest", "hodl", "hold", "portfolio", "allocation", "dca"],
        "whale": ["whale", "кит", "large", "million", "btc whale", "eth whale"],
        "signal_seeker": ["vip", "premium", "сигналы", "signals", "group", "канал"],
        "airdrop_hunter": ["airdrop", "drop", "claim", "free", "раздача", "халява"],
        "nft_collector": ["nft", "opensea", "mint", "collection", "pfp"],
        "defi_user": ["defi", "swap", "liquidity", "farm", "yield", "staking"]
    }

    # Стоп-слова
    STOP_WORDS = ["bot", "support", "admin", "official", "news", "channel", "helper", "service"]

    def __init__(
        self,
        api_id: str = None,
        api_hash: str = None,
        phone: str = None,
        session_name: str = "crypto_leads_session",
        webhook_url: str = None,
        chat_id: str = None,
        messages_limit: int = 50,
        days_back: int = 3,
        min_score: int = 30
    ):
        self.api_id = api_id or os.getenv("TELEGRAM_API_ID")
        self.api_hash = api_hash or os.getenv("TELEGRAM_API_HASH")
        self.phone = phone or os.getenv("TELEGRAM_PHONE")
        self.session_name = session_name

        self.webhook_url = webhook_url or os.getenv("TELEGRAM_WEBHOOK_URL")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

        self.messages_limit = messages_limit
        self.days_back = days_back
        self.min_score = min_score

        self.client: Optional[TelegramClient] = None
        self.seen_usernames: Set[str] = set()
        self.leads: List[CryptoLead] = []

        self.stats = {
            "channels_parsed": 0,
            "messages_scanned": 0,
            "leads_found": 0,
            "phones_extracted": 0,
            "emails_extracted": 0
        }

    async def start(self):
        """Запуск Telegram клиента"""
        if not all([self.api_id, self.api_hash]):
            raise ValueError("API_ID и API_HASH обязательны! Получите на https://my.telegram.org")

        self.client = TelegramClient(
            self.session_name,
            int(self.api_id),
            self.api_hash
        )

        await self.client.start(phone=self.phone)
        me = await self.client.get_me()
        logger.info(f"Подключено как: {me.first_name} (@{me.username})")

    async def stop(self):
        """Остановка клиента"""
        if self.client:
            await self.client.disconnect()
            logger.info("Отключено от Telegram")

    def extract_contacts(self, text: str) -> Dict:
        """Извлечение контактов из текста"""
        contacts = {
            "phones": [],
            "usernames": [],
            "emails": [],
            "wallets": []
        }

        # Телефоны
        phone_patterns = [
            r'(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
            r'\+\d{1,3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            contacts["phones"].extend(phones)

        if contacts["phones"]:
            self.stats["phones_extracted"] += len(contacts["phones"])

        # Telegram usernames
        usernames = re.findall(r'@([a-zA-Z][a-zA-Z0-9_]{4,31})', text)
        contacts["usernames"] = list(set(['@' + u for u in usernames]))

        # Email
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        contacts["emails"] = list(set(emails))

        if contacts["emails"]:
            self.stats["emails_extracted"] += len(contacts["emails"])

        # Крипто-кошельки
        # ETH/BSC/Polygon адреса
        eth_wallets = re.findall(r'0x[a-fA-F0-9]{40}', text)
        # BTC адреса
        btc_wallets = re.findall(r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-HJ-NP-Z0-9]{39,59}', text)
        contacts["wallets"] = list(set(eth_wallets + btc_wallets))

        return contacts

    def detect_lead_type(self, text: str, username: str) -> str:
        """Определение типа лида"""
        lower_text = (text + " " + username).lower()

        for lead_type, keywords in self.LEAD_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in lower_text:
                    return lead_type

        return "general"

    def score_lead(self, username: str, text: str, views: int, subscribers: int, contacts: Dict) -> int:
        """Скоринг лида"""
        score = 20  # База
        username_lower = username.lower()

        # Длина username
        if len(username) < 10:
            score += 15
        elif len(username) < 15:
            score += 10

        # Ключевые слова в username
        crypto_keywords = ["crypto", "btc", "eth", "trade", "invest", "whale", "defi", "nft"]
        for kw in crypto_keywords:
            if kw in username_lower:
                score += 10
                break

        # Контакты в сообщении
        if contacts.get("phones"):
            score += 15
        if contacts.get("emails"):
            score += 10
        if contacts.get("wallets"):
            score += 20  # Крипто-кошельки очень ценны

        # Метрики канала
        if subscribers > 100000:
            score += 15
        elif subscribers > 10000:
            score += 10
        elif subscribers > 1000:
            score += 5

        # Просмотры поста
        if views > 10000:
            score += 10
        elif views > 1000:
            score += 5

        # Штрафы
        if re.search(r'\d{4,}$', username):
            score -= 15  # Много цифр в конце = вероятно бот

        return min(max(score, 0), 100)

    def is_valid_lead(self, username: str) -> bool:
        """Проверка валидности username как лида"""
        username_lower = username.lower()

        # Стоп-слова
        if any(stop in username_lower for stop in self.STOP_WORDS):
            return False

        # Уже видели
        if username_lower in self.seen_usernames:
            return False

        # Слишком короткий
        if len(username) < 4:
            return False

        return True

    async def parse_channel(self, channel_username: str) -> List[CryptoLead]:
        """Парсинг одного канала"""
        channel_leads = []

        try:
            channel = await self.client.get_entity(channel_username)

            # Получаем инфо о канале
            subscribers = 0
            try:
                full = await self.client(GetFullChannelRequest(channel))
                subscribers = full.full_chat.participants_count
            except:
                pass

            channel_title = getattr(channel, 'title', channel_username)
            logger.info(f"Парсинг: {channel_title} ({subscribers:,} подписчиков)")

            # Дата начала
            offset_date = datetime.now() - timedelta(days=self.days_back)

            # Получаем сообщения
            messages = await self.client(GetHistoryRequest(
                peer=channel,
                limit=self.messages_limit,
                offset_date=offset_date,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            for msg in messages.messages:
                if not msg.message:
                    continue

                self.stats["messages_scanned"] += 1
                text = msg.message

                # Ищем @username в тексте
                usernames_found = re.findall(r'@([a-zA-Z][a-zA-Z0-9_]{3,31})', text)

                for username in usernames_found:
                    if not self.is_valid_lead(username):
                        continue

                    contacts = self.extract_contacts(text)
                    score = self.score_lead(username, text, msg.views or 0, subscribers, contacts)

                    if score < self.min_score:
                        continue

                    self.seen_usernames.add(username.lower())
                    lead_type = self.detect_lead_type(text, username)

                    # URL поста
                    if hasattr(channel, 'username') and channel.username:
                        post_url = f"https://t.me/{channel.username}/{msg.id}"
                    else:
                        post_url = f"https://t.me/c/{channel.id}/{msg.id}"

                    lead = CryptoLead(
                        username=f"@{username}",
                        source_channel=channel_title,
                        channel_subscribers=subscribers,
                        message_text=text[:500],
                        message_views=msg.views or 0,
                        message_date=msg.date.strftime("%Y-%m-%d %H:%M"),
                        post_url=post_url,
                        score=score,
                        lead_type=lead_type,
                        contacts={
                            "phones": contacts.get("phones", []),
                            "emails": contacts.get("emails", []),
                            "wallets": contacts.get("wallets", [])
                        },
                        parsed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    channel_leads.append(lead)
                    self.stats["leads_found"] += 1
                    logger.info(f"  ЛИД: {lead.username} | score:{score} | type:{lead_type}")

            self.stats["channels_parsed"] += 1
            logger.info(f"  Найдено {len(channel_leads)} лидов")
            return channel_leads

        except ChannelPrivateError:
            logger.warning(f"Канал {channel_username} приватный")
            return []
        except UsernameNotOccupiedError:
            logger.warning(f"Канал {channel_username} не существует")
            return []
        except Exception as e:
            logger.error(f"Ошибка парсинга {channel_username}: {e}")
            return []

    async def parse_all(self, channels: List[str] = None) -> List[CryptoLead]:
        """Парсинг всех каналов"""
        channels = channels or self.DEFAULT_CHANNELS

        logger.info(f"Запуск парсинга {len(channels)} каналов...")

        for i, channel in enumerate(channels, 1):
            logger.info(f"[{i}/{len(channels)}] {channel}")
            leads = await self.parse_channel(channel)
            self.leads.extend(leads)

            # Пауза между каналами
            if i < len(channels):
                await asyncio.sleep(2)

        # Сортируем по score
        self.leads.sort(key=lambda x: x.score, reverse=True)

        logger.info(f"\nИтого:")
        logger.info(f"  Каналов спарсено: {self.stats['channels_parsed']}")
        logger.info(f"  Сообщений просканировано: {self.stats['messages_scanned']}")
        logger.info(f"  Лидов найдено: {self.stats['leads_found']}")
        logger.info(f"  Телефонов: {self.stats['phones_extracted']}")
        logger.info(f"  Email: {self.stats['emails_extracted']}")

        return self.leads

    def save_csv(self, filename: str = "crypto_leads_telethon.csv") -> str:
        """Сохранение в CSV"""
        if not self.leads:
            logger.warning("Нет лидов для сохранения")
            return ""

        # Преобразуем в DataFrame
        data = []
        for lead in self.leads:
            row = asdict(lead)
            # Преобразуем контакты в строки
            row["phones"] = ", ".join(lead.contacts.get("phones", []))
            row["emails"] = ", ".join(lead.contacts.get("emails", []))
            row["wallets"] = ", ".join(lead.contacts.get("wallets", []))
            del row["contacts"]
            data.append(row)

        df = pd.DataFrame(data)

        # Если файл существует, дописываем
        if os.path.exists(filename):
            existing_df = pd.read_csv(filename)
            df = pd.concat([existing_df, df], ignore_index=True)
            df = df.drop_duplicates(subset=['username'], keep='last')

        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Сохранено в {filename} ({len(df)} записей)")
        return filename

    def save_excel(self, filename: str = None) -> str:
        """Сохранение в Excel с несколькими листами"""
        if not self.leads:
            return ""

        if not filename:
            date_str = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"crypto_leads_{date_str}.xlsx"

        data = []
        for lead in self.leads:
            row = asdict(lead)
            row["phones"] = ", ".join(lead.contacts.get("phones", []))
            row["emails"] = ", ".join(lead.contacts.get("emails", []))
            row["wallets"] = ", ".join(lead.contacts.get("wallets", []))
            del row["contacts"]
            data.append(row)

        df = pd.DataFrame(data)

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Все лиды
            df.to_excel(writer, sheet_name='Все лиды', index=False)

            # Горячие лиды (score > 50)
            hot_df = df[df['score'] > 50]
            if not hot_df.empty:
                hot_df.to_excel(writer, sheet_name='Горячие лиды', index=False)

            # По типам
            for lead_type in df['lead_type'].unique():
                type_df = df[df['lead_type'] == lead_type]
                sheet_name = f"Type_{lead_type}"[:31]
                type_df.to_excel(writer, sheet_name=sheet_name, index=False)

        logger.info(f"Excel сохранен: {filename}")
        return filename

    def save_json(self, filename: str = "crypto_leads.json") -> str:
        """Сохранение в JSON"""
        if not self.leads:
            return ""

        data = {
            "exported_at": datetime.now().isoformat(),
            "stats": self.stats,
            "total_leads": len(self.leads),
            "leads": [asdict(lead) for lead in self.leads]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"JSON сохранен: {filename}")
        return filename

    async def send_webhook(self):
        """Отправка результатов в Telegram бота"""
        if not self.webhook_url or not self.chat_id:
            logger.warning("Webhook не настроен")
            return

        if not self.leads:
            return

        # Формируем сообщение
        sorted_leads = sorted(self.leads, key=lambda x: x.score, reverse=True)[:20]

        text = f"<b>Crypto Leads Parser (Telethon)</b>\n\n"
        text += f"Найдено: {len(self.leads)} лидов\n\n"
        text += "<pre>"
        text += f"{'Username':<20} {'Score':>5} {'Type':<12}\n"
        text += "─" * 40 + "\n"

        for lead in sorted_leads[:15]:
            username = lead.username[:18]
            text += f"{username:<20} {lead.score:>5} {lead.lead_type:<12}\n"

        text += "</pre>"

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as resp:
                    logger.info(f"Webhook отправлен: {resp.status}")
        except Exception as e:
            logger.error(f"Webhook ошибка: {e}")


async def main():
    """Основная функция"""
    parser = CryptoLeadsTelethon(
        api_id=os.getenv("TELEGRAM_API_ID"),
        api_hash=os.getenv("TELEGRAM_API_HASH"),
        phone=os.getenv("TELEGRAM_PHONE"),
        webhook_url=os.getenv("TELEGRAM_WEBHOOK_URL"),
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        messages_limit=50,
        days_back=3,
        min_score=25
    )

    try:
        await parser.start()
        await parser.parse_all()

        # Сохраняем результаты
        parser.save_csv()
        parser.save_excel()
        parser.save_json()

        # Отправляем в бота
        await parser.send_webhook()

    finally:
        await parser.stop()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║   Crypto Leads Parser (Telethon)                 ║
║   Парсинг крипто-каналов через Telegram API      ║
╚══════════════════════════════════════════════════╝
    """)
    asyncio.run(main())
