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
        """Извлекает @username трейдеров из постов (с контекстом)"""
        leads = []

        # РАСШИРЕННЫЕ паттерны для поиска лидов
        patterns = [
            # === ВЫСОКИЙ ПРИОРИТЕТ (явные контакты) ===
            # "пиши @user", "пишите @user", "dm @user", "в лс @user"
            r'(?:пиши|пишите|дм|dm|write|contact|в\s*лс|напиши)\s*[:\-]?\s*@([a-z][a-z0-9_]{4,31})',
            # "связь @user", "контакт @user", "менеджер @user"
            r'(?:связь|контакт|manager|менеджер|по\s*вопросам|admin)\s*[:\-]?\s*@([a-z][a-z0-9_]{4,31})',
            # "обращайтесь @user", "вопросы @user"
            r'(?:обращайтесь|вопросы|details|info|подробности)\s*[:\-]?\s*@([a-z][a-z0-9_]{4,31})',
            # "@user - менеджер/трейдер/куратор"
            r'@([a-z][a-z0-9_]{4,31})\s*[\-–—:]\s*(?:менеджер|трейдер|куратор|manager|trader|admin)',

            # === СРЕДНИЙ ПРИОРИТЕТ (контекст крипто/трейдинга) ===
            # VIP, сигналы, обучение
            r'(?:vip|вип|сигнал|signal|обучение|курс|консультац)\w*\s*[:\-]?\s*@([a-z][a-z0-9_]{4,31})',
            # "автор @user", "аналитик @user", "эксперт @user"
            r'(?:автор|author|аналитик|analyst|эксперт|expert)\s*[:\-]?\s*@([a-z][a-z0-9_]{4,31})',
            # Подписка, доступ
            r'(?:подписка|доступ|access|premium|приват)\w*\s*[:\-]?\s*@([a-z][a-z0-9_]{4,31})',

            # === БАЗОВЫЙ ПРИОРИТЕТ (любые @username после ключевых слов) ===
            # После "👉", "➡️", "📩", эмодзи
            r'[👉➡️📩📲💬✍️]\s*@([a-z][a-z0-9_]{4,31})',
            # После "Наш", "Мой", "Our"
            r'(?:наш|мой|our|my)\s+@([a-z][a-z0-9_]{4,31})',
            # "@user для" чего-то
            r'@([a-z][a-z0-9_]{4,31})\s+(?:для|for|по)',

            # === УНИВЕРСАЛЬНЫЙ ПАТТЕРН (с фильтрацией) ===
            # Любой @username в тексте (фильтруется позже)
            r'(?<![/\w])@([a-z][a-z0-9_]{4,31})(?![/\w])',
        ]

        all_usernames = []
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            all_usernames.extend(matches)

        # Убираем дубликаты, сохраняя порядок
        unique_usernames = list(dict.fromkeys([u.lower() for u in all_usernames]))

        # Названия каналов для исключения
        channel_names = {ch.lower() for ch in self.DEFAULT_CHANNELS}
        channel_names.add(channel.lower())

        # ТОЧНЫЕ стоп-слова (известные каналы/боты)
        exact_stops = {
            'joinchat', 'share', 'durov', 'telegram', 'tgstat',
            'telemetr', 'tganalytics', 'cryptorank', 'coingecko',
            'binance', 'bybit', 'okx', 'kucoin', 'gate', 'huobi',
            'forklog', 'bits_media', 'coinpost', 'cointelegraph',
            'bitcoin', 'ethereum', 'opensea', 'rarible', 'coinbase',
            'kraken', 'ftx', 'gemini', 'crypto_com', 'mexc'
        }

        # Суффиксы явных каналов/ботов (отсекаем ТОЛЬКО явные)
        bot_suffixes = ('_bot', 'bot', '_support', '_help', '_official')

        for username in unique_usernames[:30]:  # Увеличили до 30
            # Пропускаем если уже видели
            if username in self.seen_usernames:
                continue

            # Пропускаем названия каналов
            if username in channel_names:
                continue

            # Пропускаем ТОЧНЫЕ стоп-слова
            if username in exact_stops:
                continue

            # Пропускаем ботов (суффиксы)
            if username.endswith(bot_suffixes):
                continue

            # Пропускаем слишком короткие (< 4 символов)
            if len(username) < 4:
                continue

            # Пропускаем стоп-слова только если они в НАЧАЛЕ
            if any(username.startswith(stop) for stop in ['news', 'channel', 'chat', 'group']):
                continue

            score = self._score_username(username, html)

            if score >= self.min_score:
                self.seen_usernames.add(username)
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

    def _score_username(self, username: str, html: str = "") -> int:
        """Оценка лида по username и контексту"""
        score = 15  # Базовый score
        username_lower = username.lower()

        # === КОНТЕКСТНЫЙ АНАЛИЗ (самый важный) ===
        if html:
            context_pattern = rf'.{{0,50}}@{re.escape(username)}.{{0,50}}'
            contexts = re.findall(context_pattern, html, re.IGNORECASE)
            context_text = ' '.join(contexts).lower()

            # ВЫСОКИЙ бонус за явный контакт
            contact_words = ['пиши', 'напиши', 'dm', 'contact', 'связь', 'менеджер', 'manager', 'admin']
            if any(w in context_text for w in contact_words):
                score += 25

            # Средний бонус за крипто-контекст
            crypto_words = ['vip', 'signal', 'сигнал', 'обучение', 'курс', 'premium', 'приват', 'консультац']
            if any(w in context_text for w in crypto_words):
                score += 15

            # Бонус за эмодзи (указывают на контакт)
            if any(e in context_text for e in ['👉', '➡', '📩', '📲', '💬', '✍']):
                score += 10

        # === АНАЛИЗ USERNAME ===
        # Бонус за короткий username (более ценный, обычно у реальных людей)
        if len(username) < 10:
            score += 10
        elif len(username) < 15:
            score += 5

        # Бонус за ключевые слова в нике
        for keyword in self.HIGH_VALUE_KEYWORDS:
            if keyword in username_lower:
                score += 5
                break

        # Штраф за явные признаки канала/бота
        if re.search(r'\d{4,}$', username):  # 4+ цифры в конце
            score -= 15
        if username.endswith(('_ru', '_en', '_news', '_channel')):
            score -= 20
        if 'official' in username_lower or 'support' in username_lower:
            score -= 25

        # Бонус за "человеческий" формат
        if re.match(r'^[a-zA-Z]+[_]?[a-zA-Z]*\d{0,3}$', username):
            score += 5

        return max(0, min(score, 70))  # От 0 до 70

    def send_webhook(self, count: int, leads: List[Lead] = None, csv_path: str = None):
        """Webhook уведомление с таблицей лидов и CSV файлом"""
        if not self.webhook_url:
            logger.warning("Webhook URL не настроен")
            return

        # Базовый URL для Telegram API
        base_url = self.webhook_url.rsplit('/sendMessage', 1)[0]

        # Формируем таблицу с лидами
        if leads:
            # Сортируем по score (лучшие вверху)
            sorted_leads = sorted(leads, key=lambda x: x.score, reverse=True)

            # Заголовок
            table_text = f"📊 <b>{count} новых crypto лидов!</b>\n\n"
            table_text += "<pre>"
            table_text += f"{'Username':<20} {'Канал':<18} {'Score':>5}\n"
            table_text += "─" * 45 + "\n"

            # Строки таблицы
            for lead in sorted_leads:
                username = lead.username[:18] if len(lead.username) > 18 else lead.username
                channel = lead.channel[:16] if len(lead.channel) > 16 else lead.channel
                table_text += f"{username:<20} {channel:<18} {lead.score:>5}\n"

            table_text += "</pre>"
        else:
            table_text = f"📊 {count} новых crypto лидов!"

        # Отправляем текстовое сообщение
        payload = {
            "chat_id": self.chat_id,
            "text": table_text,
            "parse_mode": "HTML"
        }

        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            logger.info(f"✅ Webhook боту: {resp.status_code} | {count} лидов")
        except Exception as e:
            logger.warning(f"⚠️ Webhook не сработал: {e}")

        # Отправляем CSV файл
        if csv_path and os.path.exists(csv_path):
            try:
                with open(csv_path, 'rb') as f:
                    files = {'document': (os.path.basename(csv_path), f, 'text/csv')}
                    data = {
                        'chat_id': self.chat_id,
                        'caption': f'📁 Все лиды ({count} новых)'
                    }
                    resp = requests.post(
                        f"{base_url}/sendDocument",
                        data=data,
                        files=files,
                        timeout=30
                    )
                    logger.info(f"✅ CSV файл отправлен: {resp.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось отправить CSV: {e}")

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

            # Отправляем webhook с CSV файлом
            self.send_webhook(len(all_leads), all_leads, csv_path)
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
    # Конфигурация
    parser = CryptoLeadsParser(
        webhook_url="https://api.telegram.org/bot8713339011:AAEVDmnggcktKmYumbXSbxS9XSNGr2dICfw/sendMessage",
        chat_id="7984101063",
        proxy="http://ufbaka:aRuDhAfBut7k@mproxy.site:16496",
        min_score=20  # Снижено для большей чувствительности
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
