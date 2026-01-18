#!/usr/bin/env python3
"""
Автономный агент для парсинга аренды квартир
Работает независимо, парсит каждые 4 часа, отправляет в Telegram автоматически
"""
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import schedule

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rental_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Импорты проекта
from database.models import init_db, get_unsent_listings, mark_as_sent, RentalListing
from parsers.cian_parser import CianParser
from parsers.yandex_parser import YandexParser
from parsers.avito_parser import AvitoParser
from telegram_sender import TelegramSender
from auto_dial import AutoDialer


class RentalParserAgent:
    """
    Автономный агент для парсинга и рассылки объявлений
    """

    def __init__(
        self,
        city: str = 'москва',
        db_path: str = 'rental_parser.db',
        telegram_bot_token: Optional[str] = None,
        telegram_chat_ids: Optional[List[str]] = None,
        auto_dial_enabled: bool = True,
        parse_interval_hours: int = 4,
        max_pages_per_platform: int = 5
    ):
        """
        Инициализация агента

        Args:
            city: Город для парсинга
            db_path: Путь к базе данных
            telegram_bot_token: Токен Telegram бота (из env если не указан)
            telegram_chat_ids: Список chat_id для отправки (из env если не указан)
            auto_dial_enabled: Включить автонабор
            parse_interval_hours: Интервал парсинга в часах
            max_pages_per_platform: Максимум страниц на платформу
        """
        self.city = city
        self.db_path = db_path
        self.parse_interval = parse_interval_hours
        self.max_pages = max_pages_per_platform
        self.auto_dial_enabled = auto_dial_enabled

        # Инициализация БД
        logger.info(f"Initializing database: {db_path}")
        self.db = init_db(db_path)

        # Инициализация парсеров
        logger.info(f"Initializing parsers for city: {city}")
        self.parsers = {
            'cian': CianParser(city=city),
            'yandex': YandexParser(city=city),
            'avito': AvitoParser(city=city)
        }

        # Инициализация Telegram отправителя
        bot_token = telegram_bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        chat_ids = telegram_chat_ids or os.getenv('TELEGRAM_CHAT_IDS', '').split(',')

        if not bot_token or not chat_ids or not chat_ids[0]:
            logger.warning("Telegram credentials not configured! Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_IDS")
            self.telegram_sender = None
        else:
            logger.info(f"Initializing Telegram sender for {len(chat_ids)} chats")
            self.telegram_sender = TelegramSender(bot_token, chat_ids)

        # Инициализация авто-дозвона
        if auto_dial_enabled:
            logger.info("Auto-dial is enabled")
            self.auto_dialer = AutoDialer()
        else:
            self.auto_dialer = None

        logger.info("=" * 60)
        logger.info("Rental Parser Agent initialized successfully!")
        logger.info(f"City: {city}")
        logger.info(f"Parse interval: {parse_interval_hours} hours")
        logger.info(f"Max pages per platform: {max_pages}")
        logger.info(f"Auto-dial: {'enabled' if auto_dial_enabled else 'disabled'}")
        logger.info(f"Telegram: {'configured' if self.telegram_sender else 'NOT configured'}")
        logger.info("=" * 60)

    def parse_platform(self, platform_name: str) -> int:
        """
        Парсинг одной платформы

        Returns:
            Количество новых объявлений
        """
        logger.info(f"Starting parsing: {platform_name}")

        try:
            parser = self.parsers[platform_name]
            listings = parser.parse(max_pages=self.max_pages)

            if not listings:
                logger.warning(f"{platform_name}: No listings found")
                return 0

            # Сохранение в БД
            new_count = 0
            for listing in listings:
                try:
                    # Проверка дубликата по listing_id
                    existing = self.db.query(RentalListing).filter(
                        RentalListing.listing_id == listing.get('listing_id')
                    ).first()

                    if not existing:
                        # Создание нового объявления
                        new_listing = RentalListing(
                            platform=platform_name,
                            listing_id=listing.get('listing_id'),
                            url=listing.get('url'),
                            title=listing.get('title'),
                            price=listing.get('price'),
                            phone=listing.get('phone'),
                            address=listing.get('address'),
                            rooms=listing.get('rooms'),
                            area=listing.get('area'),
                            sent_to_manager=False,
                            created_at=datetime.now()
                        )
                        self.db.add(new_listing)
                        new_count += 1

                except Exception as e:
                    logger.error(f"Error saving listing: {e}")
                    continue

            self.db.commit()
            logger.info(f"{platform_name}: Found {len(listings)} listings, {new_count} new")
            return new_count

        except Exception as e:
            logger.error(f"Error parsing {platform_name}: {e}", exc_info=True)
            return 0

    def parse_all_platforms(self) -> dict:
        """
        Парсинг всех платформ

        Returns:
            Статистика по каждой платформе
        """
        logger.info("=" * 60)
        logger.info("STARTING FULL PARSING CYCLE")
        logger.info("=" * 60)

        stats = {}
        total_new = 0

        for platform_name in ['cian', 'yandex', 'avito']:
            new_count = self.parse_platform(platform_name)
            stats[platform_name] = new_count
            total_new += new_count

        logger.info("=" * 60)
        logger.info(f"PARSING COMPLETED: {total_new} new listings total")
        logger.info(f"Stats: {stats}")
        logger.info("=" * 60)

        return stats

    def send_unsent_listings(self, limit: int = 20) -> int:
        """
        Отправка неотправленных объявлений в Telegram

        Args:
            limit: Максимум объявлений за раз

        Returns:
            Количество отправленных объявлений
        """
        if not self.telegram_sender:
            logger.warning("Telegram sender not configured, skipping sending")
            return 0

        logger.info(f"Fetching up to {limit} unsent listings...")

        listings = get_unsent_listings(self.db, limit=limit)

        if not listings:
            logger.info("No unsent listings found")
            return 0

        logger.info(f"Found {len(listings)} unsent listings, sending to Telegram...")

        sent_count = 0
        for listing in listings:
            try:
                # Формирование сообщения
                message = self._format_listing(listing)

                # Отправка в Telegram
                success = self.telegram_sender.send_listing(message, listing.phone)

                if success:
                    # Пометка как отправленного
                    mark_as_sent(self.db, listing.id, 'agent')
                    sent_count += 1
                    logger.info(f"Sent listing {listing.id} ({listing.platform})")

                    # Автонабор если включен и есть телефон
                    if self.auto_dial_enabled and self.auto_dialer and listing.phone:
                        try:
                            self.auto_dialer.dial(listing.phone, listing.url)
                            logger.info(f"Auto-dialed: {listing.phone}")
                        except Exception as e:
                            logger.error(f"Auto-dial error: {e}")

                    # Задержка между отправками
                    time.sleep(3)
                else:
                    logger.error(f"Failed to send listing {listing.id}")

            except Exception as e:
                logger.error(f"Error sending listing {listing.id}: {e}", exc_info=True)
                continue

        logger.info(f"Successfully sent {sent_count}/{len(listings)} listings")
        return sent_count

    def _format_listing(self, listing) -> str:
        """Форматирование объявления для Telegram"""
        platform_emoji = {
            'cian': '🔵',
            'yandex': '🔴',
            'avito': '🟢'
        }
        platform_name = {
            'cian': 'Cian',
            'yandex': 'Yandex',
            'avito': 'Avito'
        }

        emoji = platform_emoji.get(listing.platform, '⚪')
        name = platform_name.get(listing.platform, listing.platform)

        # Комнаты
        if listing.rooms == 0:
            rooms = 'Студия'
        elif listing.rooms:
            rooms = f'{listing.rooms}-комн'
        else:
            rooms = ''

        # Цена
        if listing.price:
            price = f"{int(listing.price):,} ₽".replace(',', ' ')
        else:
            price = 'Не указана'

        # Сборка сообщения
        lines = [
            f"{emoji} *{name}*",
            "",
            f"*{listing.title or 'Без названия'}*",
            "",
            f"💰 {price}"
        ]

        # Площадь и комнаты
        if rooms or listing.area:
            parts = []
            if rooms:
                parts.append(f"🏠 {rooms}")
            if listing.area:
                parts.append(f"{listing.area} м²")
            lines.append(', '.join(parts))

        # Адрес
        if listing.address:
            lines.append(f"📍 {listing.address}")

        # Телефон
        if listing.phone:
            lines.append(f"📞 `{listing.phone}`")

        # Ссылка
        lines.append("")
        lines.append(f"🔗 [Открыть объявление]({listing.url})")

        return '\n'.join(lines)

    def run_cycle(self):
        """Один цикл работы: парсинг + отправка"""
        logger.info("\n" + "=" * 60)
        logger.info(f"CYCLE STARTED: {datetime.now()}")
        logger.info("=" * 60)

        try:
            # Парсинг
            stats = self.parse_all_platforms()

            # Отправка
            sent = self.send_unsent_listings(limit=20)

            logger.info("=" * 60)
            logger.info(f"CYCLE COMPLETED: Parsed {sum(stats.values())} new, sent {sent}")
            logger.info("=" * 60 + "\n")

        except Exception as e:
            logger.error(f"Error in cycle: {e}", exc_info=True)

    def start(self):
        """Запуск агента с расписанием"""
        logger.info("\n" + "=" * 60)
        logger.info("RENTAL PARSER AGENT STARTED")
        logger.info("=" * 60)
        logger.info(f"Schedule: Every {self.parse_interval} hours")
        logger.info(f"Next run: {datetime.now() + timedelta(hours=self.parse_interval)}")
        logger.info("=" * 60 + "\n")

        # Первый запуск сразу
        logger.info("Running initial cycle...")
        self.run_cycle()

        # Настройка расписания
        schedule.every(self.parse_interval).hours.do(self.run_cycle)

        # Бесконечный цикл
        logger.info("Entering scheduled loop...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Проверка каждую минуту
            except KeyboardInterrupt:
                logger.info("\n" + "=" * 60)
                logger.info("AGENT STOPPED BY USER")
                logger.info("=" * 60)
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(60)


def main():
    """Точка входа"""
    # Конфигурация из environment variables или значения по умолчанию
    agent = RentalParserAgent(
        city=os.getenv('CITY', 'москва'),
        db_path=os.getenv('DB_PATH', 'rental_parser.db'),
        parse_interval_hours=int(os.getenv('PARSE_INTERVAL_HOURS', '4')),
        max_pages_per_platform=int(os.getenv('MAX_PAGES', '5')),
        auto_dial_enabled=os.getenv('AUTO_DIAL_ENABLED', 'true').lower() == 'true'
    )

    agent.start()


if __name__ == '__main__':
    main()
