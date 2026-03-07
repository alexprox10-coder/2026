#!/usr/bin/env python3
"""
Crypto Leads Parser - парсер лидов из Telegram крипто-каналов
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import time
import re
import os
from datetime import datetime
import logging
from typing import List, Dict, Any, Set
from dataclasses import dataclass, asdict
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-15s:%(lineno)-4d - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Lead:
    """Структура лида"""
    username: str
    channel: str
    score: int
    timestamp: str
    parsed_at: str


class CryptoLeadsParser:
    """Парсер крипто-лидов из Telegram каналов"""

    # Валидные крипто-каналы (проверены на доступность)
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
        "okx_russian",
        "huobi_russia",
        "kucoin_ru",
        "gate_io_ru",

        # NFT и DeFi
        "nft_russia",
        "defi_russia",
        "opensea_ru",

        # Трейдинг сигналы
        "crypto_signals_free",
        "trading_crypto_ru",
        "altcoins_russia",

        # Новости
        "bits_media",
        "forklog",
        "coinpost_ru",

        # Англоязычные популярные
        "cryptonews",
        "bitcoin",
        "binanceexchange",
        "CoinGecko",
        "coaboratory",
    ]

    # Ключевые слова для повышения score
    HIGH_VALUE_KEYWORDS = [
        "trade", "trading", "signal", "vip", "pro", "team",
        "crypto", "btc", "eth", "invest", "profit", "whale",
        "alpha", "degen", "airdrop", "gem"
    ]

    # Стоп-слова (боты, официальные аккаунты)
    STOP_WORDS = [
        "bot", "support", "admin", "official", "help",
        "news", "channel", "group", "chat"
    ]

    def __init__(
        self,
        webhook_url: str = None,
        chat_id: str = None,
        proxy: str = None,
        min_score: int = 25
    ):
        self.session = requests.Session()
        self.webhook_url = webhook_url or os.getenv("TELEGRAM_WEBHOOK_URL")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.min_score = min_score
        self.seen_usernames: Set[str] = set()

        # Настройка retry стратегии
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # User-Agent для обхода блокировок
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        })

        # Прокси (если нужен)
        if proxy:
            self.session.proxies = {
                "http": proxy,
                "https": proxy
            }

    def fetch_channel(self, channel: str) -> str:
        """Парсит канал через t.me/s/"""
        url = f"https://t.me/s/{channel}"
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            logger.info(f"[{url}] -> статус {resp.status_code}")
            return resp.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Канал не найден: {channel}")
            else:
                logger.error(f"HTTP ошибка {channel}: {e}")
            return ""
        except Exception as e:
            logger.error(f"Fetch {url}: {e}")
            return ""

    def extract_leads(self, html: str, channel: str) -> List[Lead]:
        """Извлекает @username из постов"""
        leads = []

        # Паттерн для поиска @username
        usernames = re.findall(r'@([a-zA-Z0-9_]{3,32})', html)

        # Убираем дубликаты, сохраняя порядок
        unique_usernames = list(dict.fromkeys(usernames))

        for username in unique_usernames[:10]:  # Макс 10 на канал
            username_lower = username.lower()

            # Пропускаем если уже видели
            if username_lower in self.seen_usernames:
                continue

            # Пропускаем стоп-слова
            if any(stop in username_lower for stop in self.STOP_WORDS):
                continue

            score = self._score_username(username)

            if score >= self.min_score:
                self.seen_usernames.add(username_lower)
                lead = Lead(
                    username=f"@{username}",
                    channel=channel,
                    score=score,
                    timestamp=datetime.now().isoformat(),
                    parsed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                leads.append(lead)
                logger.info(f"ЛИД! {lead.username} score:{score} | {channel}")

        return leads

    def _score_username(self, username: str) -> int:
        """Оценка лида по username"""
        score = 20  # База
        username_lower = username.lower()

        # Бонус за короткий username (более ценный)
        if len(username) < 10:
            score += 15
        elif len(username) < 15:
            score += 10

        # Бонус за ключевые слова
        for keyword in self.HIGH_VALUE_KEYWORDS:
            if keyword in username_lower:
                score += 10
                break  # Только один бонус за ключевые слова

        # Штраф за цифры в конце (часто боты)
        if re.search(r'\d{3,}$', username):
            score -= 10

        # Бонус за "человеческий" формат (имя + цифры)
        if re.match(r'^[a-zA-Z]+\d{1,2}$', username):
            score += 5

        return min(score, 60)  # Максимум 60

    def send_webhook(self, count: int, leads: List[Lead] = None):
        """Webhook уведомление"""
        if not self.webhook_url:
            logger.warning("Webhook URL не настроен")
            return

        payload = {
            "chat_id": self.chat_id,
            "text": f"📊 {count} новых crypto лидов! crypto_leads.csv обновлён",
            "action": "refresh_crypto_leads",
            "count": count,
            "file": "crypto_leads.csv",
            "timestamp": datetime.now().isoformat()
        }

        # Добавляем топ-5 лидов в уведомление
        if leads:
            top_leads = sorted(leads, key=lambda x: x.score, reverse=True)[:5]
            payload["top_leads"] = [asdict(l) for l in top_leads]

        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            logger.info(f"✅ Webhook боту: {resp.status_code} | {count} лидов")
        except Exception as e:
            logger.warning(f"⚠️ Webhook не сработал: {e}")

    def parse_all(self, channels: List[str] = None) -> List[Lead]:
        """Парсит все каналы"""
        channels = channels or self.DEFAULT_CHANNELS
        all_leads = []

        logger.info(f"🚀 Начинаем парсинг {len(channels)} каналов")

        for i, channel in enumerate(channels, 1):
            logger.info(f"[{i}/{len(channels)}] Парсим {channel}")

            html = self.fetch_channel(channel)
            if html:
                leads = self.extract_leads(html, channel)
                all_leads.extend(leads)

            # Антибан: пауза между запросами
            if i < len(channels):
                time.sleep(2)

        if all_leads:
            # Сохраняем в CSV
            df = pd.DataFrame([asdict(l) for l in all_leads])
            csv_path = "crypto_leads.csv"

            # Если файл существует, дописываем
            if os.path.exists(csv_path):
                existing_df = pd.read_csv(csv_path)
                df = pd.concat([existing_df, df], ignore_index=True)
                # Убираем дубликаты по username
                df = df.drop_duplicates(subset=['username'], keep='last')

            df.to_csv(csv_path, index=False, encoding="utf-8")
            logger.info(f"✅ НАЙДЕНО: {len(all_leads)} лидов | Всего в файле: {len(df)} | Сохранено: {csv_path}")

            # Отправляем webhook
            self.send_webhook(len(all_leads), all_leads)
        else:
            logger.info("❌ Новых лидов не найдено")

        return all_leads

    def export_json(self, leads: List[Lead], path: str = "crypto_leads.json"):
        """Экспорт в JSON"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_leads": len(leads),
            "leads": [asdict(l) for l in leads]
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"📁 Экспортировано в {path}")


def main():
    """Основная функция"""
    # Конфигурация через переменные окружения
    parser = CryptoLeadsParser(
        webhook_url=os.getenv("TELEGRAM_WEBHOOK_URL"),
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        proxy=os.getenv("PROXY_URL"),  # Опционально
        min_score=25
    )

    # Можно указать свои каналы или использовать дефолтные
    custom_channels = [
        # Добавьте свои каналы здесь
    ]

    channels = custom_channels if custom_channels else None

    # Парсим
    leads = parser.parse_all(channels)

    # Опционально: экспорт в JSON
    if leads:
        parser.export_json(leads)

    return leads


if __name__ == "__main__":
    main()
