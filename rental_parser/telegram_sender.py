#!/usr/bin/env python3
"""
Модуль для автоматической отправки объявлений в Telegram
"""
import logging
import time
from typing import List, Optional
import requests

logger = logging.getLogger(__name__)


class TelegramSender:
    """
    Класс для отправки сообщений в Telegram
    """

    def __init__(self, bot_token: str, chat_ids: List[str]):
        """
        Args:
            bot_token: Токен Telegram бота
            chat_ids: Список chat_id для рассылки
        """
        self.bot_token = bot_token
        self.chat_ids = [cid.strip() for cid in chat_ids if cid.strip()]
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

        logger.info(f"TelegramSender initialized for {len(self.chat_ids)} chats")

    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = 'Markdown',
        disable_web_page_preview: bool = True
    ) -> bool:
        """
        Отправка сообщения в один чат

        Returns:
            True если успешно, False если ошибка
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get('ok'):
                return True
            else:
                logger.error(f"Telegram API error: {result.get('description')}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False

    def send_listing(self, message: str, phone: Optional[str] = None) -> bool:
        """
        Отправка объявления во все чаты

        Args:
            message: Текст сообщения
            phone: Номер телефона (опционально)

        Returns:
            True если хотя бы в один чат отправлено успешно
        """
        success = False

        for chat_id in self.chat_ids:
            try:
                if self.send_message(chat_id, message):
                    logger.info(f"Sent to chat {chat_id}")
                    success = True
                    time.sleep(0.5)  # Небольшая задержка между чатами
                else:
                    logger.warning(f"Failed to send to chat {chat_id}")

            except Exception as e:
                logger.error(f"Error sending to chat {chat_id}: {e}")

        return success

    def send_notification(self, text: str) -> bool:
        """
        Отправка уведомления (без форматирования)

        Args:
            text: Текст уведомления

        Returns:
            True если успешно
        """
        success = False

        for chat_id in self.chat_ids:
            try:
                if self.send_message(chat_id, text, parse_mode=None):
                    success = True
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error sending notification to {chat_id}: {e}")

        return success

    def test_connection(self) -> bool:
        """
        Проверка соединения с Telegram

        Returns:
            True если бот работает
        """
        url = f"{self.base_url}/getMe"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get('ok'):
                bot_info = result.get('result', {})
                logger.info(f"Telegram bot connected: @{bot_info.get('username')}")
                return True
            else:
                logger.error(f"Telegram bot test failed: {result.get('description')}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            return False
