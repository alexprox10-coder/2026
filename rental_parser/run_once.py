#!/usr/bin/env python3
"""
Простой скрипт для разового запуска парсинга и отправки
Можно запускать из n8n, cron, или вручную
"""
import os
import sys
import json
import logging
import time
from datetime import datetime
from typing import Dict, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем путь для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import init_db, get_unsent_listings, mark_as_sent, RentalListing
from parsers.cian_parser import CianParser
from parsers.yandex_parser import YandexParser
from parsers.avito_parser import AvitoParser
from telegram_sender import TelegramSender
from auto_dial import AutoDialer


def parse_all_platforms(city: str = 'москва', max_pages: int = 5) -> Dict:
    """
    Парсинг всех платформ

    Returns:
        dict: Статистика парсинга
    """
    logger.info("=" * 60)
    logger.info("STARTING PARSING")
    logger.info("=" * 60)

    db = init_db('rental_parser.db')

    parsers = {
        'cian': CianParser(city=city),
        'yandex': YandexParser(city=city),
        'avito': AvitoParser(city=city)
    }

    stats = {}

    for platform_name, parser in parsers.items():
        logger.info(f"Parsing {platform_name}...")

        try:
            listings = parser.parse(max_pages=max_pages)

            if not listings:
                logger.warning(f"{platform_name}: No listings found")
                stats[platform_name] = {'found': 0, 'new': 0}
                continue

            # Сохранение в БД
            new_count = 0
            for listing in listings:
                try:
                    # Проверка дубликата
                    existing = db.query(RentalListing).filter(
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
                        db.add(new_listing)
                        new_count += 1

                except Exception as e:
                    logger.error(f"Error saving listing: {e}")
                    continue

            db.commit()
            stats[platform_name] = {'found': len(listings), 'new': new_count}
            logger.info(f"{platform_name}: Found {len(listings)}, new {new_count}")

        except Exception as e:
            logger.error(f"Error parsing {platform_name}: {e}")
            stats[platform_name] = {'found': 0, 'new': 0, 'error': str(e)}

    total_new = sum(s.get('new', 0) for s in stats.values())
    logger.info("=" * 60)
    logger.info(f"PARSING COMPLETED: {total_new} new listings")
    logger.info("=" * 60)

    db.close()
    return stats


def send_to_telegram(limit: int = 20) -> Dict:
    """
    Отправка неотправленных объявлений в Telegram

    Returns:
        dict: Статистика отправки
    """
    logger.info("=" * 60)
    logger.info("SENDING TO TELEGRAM")
    logger.info("=" * 60)

    # Проверка конфигурации
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_ids = os.getenv('TELEGRAM_CHAT_IDS', '').split(',')

    if not bot_token or not chat_ids or not chat_ids[0]:
        logger.error("Telegram not configured! Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_IDS")
        return {'sent': 0, 'failed': 0, 'error': 'Telegram not configured'}

    db = init_db('rental_parser.db')
    sender = TelegramSender(bot_token, chat_ids)

    # Инициализация автонабора
    auto_dial_enabled = os.getenv('AUTO_DIAL_ENABLED', 'true').lower() == 'true'
    dialer = None
    if auto_dial_enabled:
        try:
            dialer = AutoDialer()
            logger.info(f"Auto-dial enabled: {dialer.backend.value}")
        except Exception as e:
            logger.warning(f"Auto-dial initialization failed: {e}")

    # Получить неотправленные
    listings = get_unsent_listings(db, limit=limit)

    if not listings:
        logger.info("No unsent listings found")
        db.close()
        return {'sent': 0, 'failed': 0}

    logger.info(f"Found {len(listings)} unsent listings")

    sent_count = 0
    failed_count = 0

    for listing in listings:
        try:
            # Формирование сообщения
            message = format_listing(listing)

            # Отправка
            if sender.send_listing(message, listing.phone):
                # Пометка как отправленного
                mark_as_sent(db, listing.id, 'run_once')
                sent_count += 1
                logger.info(f"Sent listing {listing.id} ({listing.platform})")

                # Автонабор если включен и есть телефон
                if dialer and listing.phone:
                    try:
                        dialer.dial(listing.phone, listing.url, listing.id)
                        logger.info(f"Auto-dialed: {listing.phone}")
                    except Exception as e:
                        logger.error(f"Auto-dial failed for {listing.phone}: {e}")

                # Задержка между отправками
                time.sleep(2)
            else:
                failed_count += 1
                logger.error(f"Failed to send listing {listing.id}")

        except Exception as e:
            logger.error(f"Error sending listing {listing.id}: {e}")
            failed_count += 1

    logger.info("=" * 60)
    logger.info(f"SENDING COMPLETED: {sent_count} sent, {failed_count} failed")
    logger.info("=" * 60)

    db.close()
    return {'sent': sent_count, 'failed': failed_count}


def format_listing(listing) -> str:
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


def main():
    """
    Главная функция - парсинг и отправка
    """
    print("\n" + "=" * 60)
    print("RENTAL PARSER - ONE TIME RUN")
    print("=" * 60 + "\n")

    # Загрузка .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv not installed, using system env vars")

    # Параметры
    city = os.getenv('CITY', 'москва')
    max_pages = int(os.getenv('MAX_PAGES', '5'))
    send_limit = int(os.getenv('SEND_LIMIT', '20'))

    print(f"City: {city}")
    print(f"Max pages: {max_pages}")
    print(f"Send limit: {send_limit}")
    print()

    # Парсинг
    parse_stats = parse_all_platforms(city=city, max_pages=max_pages)

    # Отправка
    send_stats = send_to_telegram(limit=send_limit)

    # Результат
    result = {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'parsing': parse_stats,
        'sending': send_stats,
        'summary': {
            'total_new': sum(s.get('new', 0) for s in parse_stats.values()),
            'total_sent': send_stats.get('sent', 0)
        }
    }

    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 60 + "\n")

    # Возврат JSON для n8n
    return result


if __name__ == '__main__':
    result = main()
    sys.exit(0 if result['success'] else 1)
