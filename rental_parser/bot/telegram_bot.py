"""
Telegram bot for managers to receive rental listings
"""
import os
import logging
from datetime import datetime
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import init_db, RentalListing, Manager, get_unsent_listings, mark_as_sent


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TelegramBot')


class RentalBot:
    """Telegram bot for rental property notifications"""

    def __init__(self, token: str, db_path: str = "rental_parser.db"):
        """
        Initialize bot

        Args:
            token: Telegram bot token
            db_path: Path to database
        """
        self.token = token
        self.db_session = init_db(db_path)
        self.application = Application.builder().token(token).build()

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register command and callback handlers"""
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("get", self.cmd_get_listings))
        self.application.add_handler(CommandHandler("stats", self.cmd_stats))
        self.application.add_handler(CommandHandler("settings", self.cmd_settings))

        # Callback handlers
        self.application.add_handler(CallbackQueryHandler(self.callback_handler))

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        telegram_id = str(user.id)

        # Check if manager exists
        manager = self.db_session.query(Manager).filter(
            Manager.telegram_id == telegram_id
        ).first()

        if not manager:
            # Create new manager
            manager = Manager(
                telegram_id=telegram_id,
                name=user.full_name
            )
            self.db_session.add(manager)
            self.db_session.commit()

            welcome_text = (
                f"👋 Добро пожаловать, {user.first_name}!\n\n"
                f"Я бот для получения свежих объявлений об аренде квартир.\n\n"
                f"Используйте /help для списка команд."
            )
        else:
            welcome_text = f"С возвращением, {user.first_name}!"

        await update.message.reply_text(welcome_text)

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🏠 *Команды бота:*

/get [N] - Получить N новых объявлений (по умолчанию 5)
/stats - Статистика по базе данных
/settings - Настройки фильтров

📱 *Функции:*
• Автоматическая отправка свежих объявлений
• Фильтрация по городу, цене, количеству комнат
• Автодозвон по номеру телефона
• Без дубликатов - каждое объявление только один раз

💡 *Пример:*
/get 10 - получить 10 новых объявлений
        """

        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def cmd_get_listings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /get command to fetch new listings"""
        user = update.effective_user
        telegram_id = str(user.id)

        # Get limit from arguments
        try:
            limit = int(context.args[0]) if context.args else 5
            limit = min(limit, 20)  # Max 20 at once
        except (ValueError, IndexError):
            limit = 5

        await update.message.reply_text(f"🔍 Ищу {limit} новых объявлений...")

        # Get unsent listings
        listings = get_unsent_listings(self.db_session, limit=limit)

        if not listings:
            await update.message.reply_text("😔 Новых объявлений пока нет. Попробуйте позже.")
            return

        # Send each listing
        for i, listing in enumerate(listings, 1):
            try:
                message = self._format_listing(listing, i, len(listings))
                keyboard = self._create_listing_keyboard(listing)

                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=keyboard,
                    disable_web_page_preview=False
                )

                # Mark as sent
                mark_as_sent(self.db_session, listing.id, telegram_id)

                # Auto-dial if phone available
                if listing.phone:
                    await self._auto_dial(update, listing.phone)

            except Exception as e:
                logger.error(f"Error sending listing {listing.id}: {e}")

        await update.message.reply_text(f"✅ Отправлено {len(listings)} объявлений")

    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        total = self.db_session.query(RentalListing).count()
        unsent = self.db_session.query(RentalListing).filter(
            RentalListing.sent_to_manager == False
        ).count()

        stats_by_platform = {}
        for platform in ['cian', 'yandex', 'avito']:
            count = self.db_session.query(RentalListing).filter(
                RentalListing.platform == platform
            ).count()
            stats_by_platform[platform] = count

        stats_text = f"""
📊 *Статистика базы данных:*

Всего объявлений: {total}
Не отправлено: {unsent}

*По площадкам:*
🔵 Cian: {stats_by_platform['cian']}
🔴 Yandex: {stats_by_platform['yandex']}
🟢 Avito: {stats_by_platform['avito']}
        """

        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def cmd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        user = update.effective_user
        telegram_id = str(user.id)

        manager = self.db_session.query(Manager).filter(
            Manager.telegram_id == telegram_id
        ).first()

        if not manager:
            await update.message.reply_text("❌ Сначала используйте /start")
            return

        settings_text = f"""
⚙️ *Ваши настройки:*

Город: {manager.city or 'Не задан'}
Макс. цена: {manager.max_price or 'Не задана'}₽
Мин. комнат: {manager.min_rooms or 'Не задано'}

_Настройки в разработке..._
        """

        await update.message.reply_text(settings_text, parse_mode='Markdown')

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline buttons"""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data.startswith('call_'):
            # Extract phone from callback data
            phone = data.replace('call_', '')
            await self._auto_dial(update, phone)
            await query.edit_message_reply_markup(reply_markup=None)

        elif data.startswith('skip_'):
            await query.edit_message_text("⏭️ Пропущено")

    def _format_listing(self, listing: RentalListing, index: int, total: int) -> str:
        """Format listing message"""
        platform_emoji = {
            'cian': '🔵',
            'yandex': '🔴',
            'avito': '🟢'
        }

        emoji = platform_emoji.get(listing.platform, '⚪')

        message = f"{emoji} *Объявление {index}/{total}*\n\n"
        message += f"*{listing.title}*\n\n"

        if listing.price:
            message += f"💰 Цена: {listing.price:,.0f} ₽/мес\n"

        if listing.rooms is not None:
            rooms_text = "Студия" if listing.rooms == 0 else f"{listing.rooms}-комн"
            message += f"🏠 {rooms_text}"

        if listing.area:
            message += f", {listing.area} м²"

        if listing.floor and listing.total_floors:
            message += f", {listing.floor}/{listing.total_floors} этаж"

        message += "\n"

        if listing.address:
            message += f"📍 {listing.address}\n"

        if listing.phone:
            message += f"📞 Телефон: `{listing.phone}`\n"

        message += f"\n🔗 [Открыть объявление]({listing.url})\n"
        message += f"\n_Площадка: {listing.platform.capitalize()}_"

        return message

    def _create_listing_keyboard(self, listing: RentalListing) -> Optional[InlineKeyboardMarkup]:
        """Create inline keyboard for listing"""
        keyboard = []

        if listing.phone:
            keyboard.append([
                InlineKeyboardButton(
                    f"📞 Позвонить {listing.phone}",
                    callback_data=f"call_{listing.phone}"
                )
            ])

        keyboard.append([
            InlineKeyboardButton("⏭️ Пропустить", callback_data=f"skip_{listing.id}")
        ])

        return InlineKeyboardMarkup(keyboard) if keyboard else None

    async def _auto_dial(self, update: Update, phone: str):
        """
        Trigger auto-dial functionality

        Note: Actual auto-dial requires integration with telephony service
        like Asterisk, Twilio, or mobile device API
        """
        # Placeholder for auto-dial integration
        # In production, this would:
        # 1. Send request to telephony API
        # 2. Initiate call to manager
        # 3. When answered, call the listing phone

        message = (
            f"📞 *Автодозвон активирован*\n\n"
            f"Номер: `{phone}`\n\n"
            f"_⚠️ Функция автодозвона требует интеграции с телефонией_"
        )

        if update.callback_query:
            await update.callback_query.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, parse_mode='Markdown')

    def run(self):
        """Start the bot"""
        logger.info("Starting Telegram bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    def close(self):
        """Close database connection"""
        self.db_session.close()


def main():
    """Entry point"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return

    db_path = os.getenv('DB_PATH', 'rental_parser.db')

    bot = RentalBot(token, db_path)

    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        bot.close()


if __name__ == '__main__':
    main()
