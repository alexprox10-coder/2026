#!/usr/bin/env python3
"""
🔥 ПРОДАЖНЫЙ Telegram Парсер PRO
Парсит ЛЮБЫЕ публичные каналы/группы

Для Kwork/Freelance - цена 3000-10000₽

Установка:
pip install telethon pandas openpyxl aiohttp

Получить api_id и api_hash:
https://my.telegram.org/apps
"""

import asyncio
import hashlib
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

try:
    from telethon import TelegramClient
    from telethon.tl.functions.channels import GetFullChannelRequest
    from telethon.tl.functions.messages import GetHistoryRequest
    from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
    import pandas as pd
except ImportError:
    print("Установите зависимости: pip install telethon pandas openpyxl")
    exit(1)


# ============== КОНФИГУРАЦИЯ ==============
CONFIG = {
    # Telegram API (получить на https://my.telegram.org)
    "api_id": "ВАШ_API_ID",
    "api_hash": "ВАШ_API_HASH",
    "phone": "+7XXXXXXXXXX",

    # Каналы для парсинга (username или ссылки)
    "channels": [
        "moscowach",      # ЧП Москва
        "mlomonova",      # Пример
        # Добавьте свои каналы
    ],

    # Лимиты
    "messages_per_channel": 100,  # Сообщений с каждого канала
    "days_back": 7,               # За последние N дней

    # Ключевые слова по нишам
    "keywords": {
        "leads": ["ищу", "куплю", "нужен", "требуется", "закажу", "где найти", "посоветуйте"],
        "discounts": ["скидка", "акция", "распродажа", "промокод", "халява", "бесплатно", "розыгрыш", "-50%", "-70%"],
        "crypto": ["сигнал", "памп", "buy", "sell", "entry", "target", "stop loss", "btc", "eth", "usdt"],
        "jobs": ["вакансия", "удаленка", "remote", "ищем", "зарплата", "оклад", "фриланс", "менеджер"],
        "realty": ["сдам", "сниму", "продам", "куплю квартиру", "комната", "аренда", "м²", "этаж"],
        "services": ["услуги", "делаю", "помогу", "настрою", "создам", "разработка"]
    },

    # Выходные файлы
    "output_excel": "telegram_leads_{date}.xlsx",
    "output_json": "telegram_data_{date}.json"
}


class TelegramParserPro:
    def __init__(self, config):
        self.config = config
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
            'parser_session',
            self.config['api_id'],
            self.config['api_hash']
        )
        await self.client.start(phone=self.config['phone'])
        print("✅ Подключено к Telegram")

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

        # Телефоны (разные форматы)
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
        contacts["urls"] = urls[:5]  # Максимум 5

        return contacts

    def detect_niche(self, text):
        """Определение ниши по ключевым словам"""
        lower_text = text.lower()

        for niche, keywords in self.config['keywords'].items():
            for keyword in keywords:
                if keyword.lower() in lower_text:
                    return niche, keyword

        return None, None

    def calculate_lead_score(self, data):
        """Скоринг качества лида"""
        score = 0

        # Контакты (самое важное)
        if data.get('phones'):
            score += 35
        if data.get('usernames'):
            score += 20
        if data.get('emails'):
            score += 25

        # Контент
        text_len = len(data.get('text', ''))
        if text_len > 100:
            score += 5
        if text_len > 300:
            score += 5

        # Метрики
        if data.get('views', 0) > 1000:
            score += 5
        if data.get('views', 0) > 10000:
            score += 5

        # Штрафы
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

    async def parse_channel(self, channel_username):
        """Парсинг одного канала"""
        try:
            channel = await self.client.get_entity(channel_username)

            # Получаем информацию о канале
            try:
                full = await self.client(GetFullChannelRequest(channel))
                subscribers = full.full_chat.participants_count
            except:
                subscribers = 0

            print(f"📢 Парсинг: {channel.title} ({subscribers} подписчиков)")

            # Дата начала
            offset_date = datetime.now() - timedelta(days=self.config['days_back'])

            # Получаем сообщения
            messages = await self.client(GetHistoryRequest(
                peer=channel,
                limit=self.config['messages_per_channel'],
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

                # Определяем нишу
                niche, keyword = self.detect_niche(text)
                if not niche:
                    continue

                self.stats['matched_messages'] += 1

                # Извлекаем контакты
                contacts = self.extract_contacts(text)

                if contacts['phones']:
                    self.stats['phones_found'] += len(contacts['phones'])
                if contacts['usernames']:
                    self.stats['usernames_found'] += len(contacts['usernames'])
                if contacts['emails']:
                    self.stats['emails_found'] += len(contacts['emails'])

                # Формируем данные
                data = {
                    # Время
                    "timestamp": msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "date": msg.date.strftime("%Y-%m-%d"),

                    # Канал
                    "channel_title": channel.title,
                    "channel_username": f"@{channel.username}" if channel.username else "",
                    "channel_id": channel.id,
                    "subscribers": subscribers,

                    # Контент
                    "text": text,
                    "text_preview": text[:200] + "..." if len(text) > 200 else text,
                    "has_media": bool(msg.media),
                    "media_type": self._get_media_type(msg.media),

                    # Метрики
                    "views": msg.views or 0,
                    "forwards": msg.forwards or 0,

                    # Контакты (ЗОЛОТО!)
                    "phones": ", ".join(set(contacts['phones'])),
                    "usernames": ", ".join(set(contacts['usernames'])),
                    "emails": ", ".join(set(contacts['emails'])),
                    "links": ", ".join(contacts['urls']),

                    # Классификация
                    "niche": niche,
                    "keyword_matched": keyword,
                    "is_ad": self.is_advertisement(text),

                    # Ссылка на пост
                    "post_url": f"https://t.me/{channel.username}/{msg.id}" if channel.username else f"https://t.me/c/{channel.id}/{msg.id}",

                    # Технические
                    "message_id": msg.id,
                    "text_hash": hashlib.md5(text.encode()).hexdigest()[:16]
                }

                # Скоринг
                data['lead_score'] = self.calculate_lead_score(data)

                channel_results.append(data)

            print(f"   ✓ Найдено {len(channel_results)} релевантных постов")
            return channel_results

        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return []

    def _get_media_type(self, media):
        """Определение типа медиа"""
        if not media:
            return None
        if isinstance(media, MessageMediaPhoto):
            return "photo"
        if isinstance(media, MessageMediaDocument):
            return "document"
        return "other"

    async def parse_all(self):
        """Парсинг всех каналов"""
        print("\n🚀 Запуск парсинга...\n")

        for channel in self.config['channels']:
            results = await self.parse_channel(channel)
            self.results.extend(results)
            await asyncio.sleep(2)  # Пауза между каналами

        # Сортируем по скорингу
        self.results.sort(key=lambda x: x['lead_score'], reverse=True)

        print(f"\n📊 Статистика:")
        print(f"   Всего сообщений: {self.stats['total_messages']}")
        print(f"   Релевантных: {self.stats['matched_messages']}")
        print(f"   Телефонов найдено: {self.stats['phones_found']}")
        print(f"   Username найдено: {self.stats['usernames_found']}")
        print(f"   Email найдено: {self.stats['emails_found']}")

    def save_excel(self):
        """Сохранение в Excel (для клиента)"""
        if not self.results:
            print("❌ Нет данных для сохранения")
            return

        date_str = datetime.now().strftime("%Y%m%d_%H%M")
        filename = self.config['output_excel'].format(date=date_str)

        df = pd.DataFrame(self.results)

        # Создаем Excel с несколькими листами
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Лист 1: Все лиды
            df.to_excel(writer, sheet_name='Все лиды', index=False)

            # Лист 2: Горячие лиды (с контактами)
            hot_leads = df[
                (df['phones'] != '') |
                (df['emails'] != '') |
                (df['usernames'] != '')
            ].copy()
            if not hot_leads.empty:
                hot_leads.to_excel(writer, sheet_name='Горячие лиды', index=False)

            # Лист 3: По нишам
            for niche in df['niche'].unique():
                niche_df = df[df['niche'] == niche]
                sheet_name = f"Ниша {niche}"[:31]  # Максимум 31 символ
                niche_df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Лист 4: Статистика
            stats_data = {
                "Метрика": [
                    "Всего постов",
                    "Телефонов",
                    "Username",
                    "Email",
                    "Средний скоринг",
                    "Каналов спарсено"
                ],
                "Значение": [
                    len(df),
                    self.stats['phones_found'],
                    self.stats['usernames_found'],
                    self.stats['emails_found'],
                    round(df['lead_score'].mean(), 1),
                    len(self.config['channels'])
                ]
            }
            pd.DataFrame(stats_data).to_excel(writer, sheet_name='Статистика', index=False)

        print(f"\n✅ Сохранено в {filename}")
        return filename

    def save_json(self):
        """Сохранение в JSON"""
        date_str = datetime.now().strftime("%Y%m%d_%H%M")
        filename = self.config['output_json'].format(date=date_str)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "stats": self.stats,
                "results": self.results
            }, f, ensure_ascii=False, indent=2)

        print(f"✅ Сохранено в {filename}")
        return filename


async def main():
    parser = TelegramParserPro(CONFIG)

    try:
        await parser.start()
        await parser.parse_all()
        parser.save_excel()
        parser.save_json()
    finally:
        await parser.stop()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║     🔥 TELEGRAM PARSER PRO - МОНЕТИЗАЦИЯ 🔥      ║
║                                                  ║
║  Парсит любые каналы, извлекает контакты,       ║
║  сортирует по качеству лида                      ║
║                                                  ║
║  Цена на Kwork: 3000-10000₽                      ║
╚══════════════════════════════════════════════════╝
    """)

    asyncio.run(main())
