"""Модуль для отправки уведомлений в Telegram"""
import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Класс для отправки уведомлений в Telegram"""

    def __init__(self):
        """Инициализация Telegram бота"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logger.warning("Telegram credentials не настроены")
            self.bot = None
            return

        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID

    async def send_message_async(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Асинхронная отправка сообщения в Telegram

        Args:
            message: Текст сообщения
            parse_mode: Режим парсинга (HTML, Markdown)

        Returns:
            True если успешно отправлено
        """
        if not self.bot:
            logger.error("Telegram бот не инициализирован")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info("Сообщение успешно отправлено в Telegram")
            return True

        except TelegramError as e:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")
            return False

    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Синхронная обёртка для отправки сообщения

        Args:
            message: Текст сообщения
            parse_mode: Режим парсинга (HTML, Markdown)

        Returns:
            True если успешно отправлено
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Если event loop уже запущен, создаём новый
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(self.send_message_async(message, parse_mode))

        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            return False

    def send_start_notification(self, task: str) -> bool:
        """
        Отправить уведомление о начале работы

        Args:
            task: Описание задачи

        Returns:
            True если успешно
        """
        message = (
            f"🤖 <b>Агент начал работу</b>\n\n"
            f"📋 Задача: {task}\n\n"
            f"⏳ Процесс может занять некоторое время.\n"
            f"Я сообщу когда закончу!"
        )
        return self.send_message(message)

    def send_success_notification(self, task: str, details: str = "") -> bool:
        """
        Отправить уведомление об успешном выполнении

        Args:
            task: Описание задачи
            details: Дополнительные детали

        Returns:
            True если успешно
        """
        message = f"✅ <b>Задача выполнена</b>\n\n📋 {task}\n"
        if details:
            message += f"\n{details}"

        return self.send_message(message)

    def send_error_notification(self, task: str, error: str) -> bool:
        """
        Отправить уведомление об ошибке

        Args:
            task: Описание задачи
            error: Описание ошибки

        Returns:
            True если успешно
        """
        message = (
            f"❌ <b>Ошибка при выполнении задачи</b>\n\n"
            f"📋 Задача: {task}\n"
            f"⚠️ Ошибка: {error}\n\n"
            f"Пожалуйста, войдите в систему для решения проблемы."
        )
        return self.send_message(message)

    def send_progress_notification(self, task: str, progress: str) -> bool:
        """
        Отправить уведомление о прогрессе

        Args:
            task: Описание задачи
            progress: Описание прогресса

        Returns:
            True если успешно
        """
        message = f"⚙️ <b>В процессе</b>\n\n📋 {task}\n📊 {progress}"
        return self.send_message(message)
