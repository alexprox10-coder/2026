#!/usr/bin/env python3
"""
Модуль автонабора номеров телефонов
Поддерживает несколько бэкендов: Asterisk, Twilio, webhook
"""
import os
import logging
import requests
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class DialerBackend(Enum):
    """Типы бэкендов для автонабора"""
    WEBHOOK = "webhook"  # HTTP webhook
    ASTERISK = "asterisk"  # Asterisk AMI
    TWILIO = "twilio"  # Twilio API
    MOCK = "mock"  # Для тестирования (не звонит реально)


class AutoDialer:
    """
    Класс для автоматического набора номеров
    """

    def __init__(
        self,
        backend: Optional[str] = None,
        webhook_url: Optional[str] = None,
        asterisk_host: Optional[str] = None,
        asterisk_port: int = 5038,
        asterisk_user: Optional[str] = None,
        asterisk_password: Optional[str] = None,
        twilio_account_sid: Optional[str] = None,
        twilio_auth_token: Optional[str] = None,
        twilio_from_number: Optional[str] = None
    ):
        """
        Инициализация автонабора

        Args:
            backend: Тип бэкенда (webhook/asterisk/twilio/mock)
            webhook_url: URL для webhook вызовов
            asterisk_*: Параметры для Asterisk
            twilio_*: Параметры для Twilio
        """
        # Определение бэкенда
        backend_str = backend or os.getenv('DIALER_BACKEND', 'mock')
        try:
            self.backend = DialerBackend(backend_str.lower())
        except ValueError:
            logger.warning(f"Unknown backend '{backend_str}', using MOCK")
            self.backend = DialerBackend.MOCK

        # Webhook конфигурация
        self.webhook_url = webhook_url or os.getenv('DIALER_WEBHOOK_URL')

        # Asterisk конфигурация
        self.asterisk_host = asterisk_host or os.getenv('ASTERISK_HOST')
        self.asterisk_port = asterisk_port
        self.asterisk_user = asterisk_user or os.getenv('ASTERISK_USER')
        self.asterisk_password = asterisk_password or os.getenv('ASTERISK_PASSWORD')

        # Twilio конфигурация
        self.twilio_account_sid = twilio_account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = twilio_auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_from_number = twilio_from_number or os.getenv('TWILIO_FROM_NUMBER')

        logger.info(f"AutoDialer initialized with backend: {self.backend.value}")

        # Проверка конфигурации
        if self.backend == DialerBackend.WEBHOOK and not self.webhook_url:
            logger.warning("Webhook backend selected but DIALER_WEBHOOK_URL not set")
        elif self.backend == DialerBackend.ASTERISK:
            if not all([self.asterisk_host, self.asterisk_user, self.asterisk_password]):
                logger.warning("Asterisk backend selected but credentials incomplete")
        elif self.backend == DialerBackend.TWILIO:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
                logger.warning("Twilio backend selected but credentials incomplete")

    def dial(self, phone: str, listing_url: Optional[str] = None, listing_id: Optional[int] = None) -> bool:
        """
        Набрать номер телефона

        Args:
            phone: Номер телефона
            listing_url: URL объявления (опционально)
            listing_id: ID объявления (опционально)

        Returns:
            True если звонок инициирован успешно
        """
        try:
            if self.backend == DialerBackend.WEBHOOK:
                return self._dial_webhook(phone, listing_url, listing_id)
            elif self.backend == DialerBackend.ASTERISK:
                return self._dial_asterisk(phone, listing_url, listing_id)
            elif self.backend == DialerBackend.TWILIO:
                return self._dial_twilio(phone, listing_url, listing_id)
            elif self.backend == DialerBackend.MOCK:
                return self._dial_mock(phone, listing_url, listing_id)
            else:
                logger.error(f"Unknown backend: {self.backend}")
                return False

        except Exception as e:
            logger.error(f"Error dialing {phone}: {e}")
            return False

    def _dial_webhook(self, phone: str, listing_url: Optional[str], listing_id: Optional[int]) -> bool:
        """Звонок через webhook"""
        if not self.webhook_url:
            logger.error("Webhook URL not configured")
            return False

        payload = {
            'phone': phone,
            'listing_url': listing_url,
            'listing_id': listing_id
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()

            logger.info(f"Webhook call initiated for {phone}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook call failed for {phone}: {e}")
            return False

    def _dial_asterisk(self, phone: str, listing_url: Optional[str], listing_id: Optional[int]) -> bool:
        """Звонок через Asterisk AMI"""
        if not all([self.asterisk_host, self.asterisk_user, self.asterisk_password]):
            logger.error("Asterisk credentials not configured")
            return False

        try:
            # Примечание: Требуется библиотека asterisk.ami или panoramisk
            # pip install asterisk.ami
            from asterisk.ami import AMIClient

            client = AMIClient(
                address=self.asterisk_host,
                port=self.asterisk_port
            )
            client.login(username=self.asterisk_user, secret=self.asterisk_password)

            # Инициация звонка
            # Параметры зависят от конфигурации Asterisk
            future = client.originate(
                channel=f'SIP/{phone}',  # Или PJSIP/{phone}
                exten='s',  # Extension для обработки
                context='outbound',  # Context из dialplan
                priority=1,
                caller_id=f'Rental Agent <{phone}>',
                variables={
                    'LISTING_URL': listing_url or '',
                    'LISTING_ID': str(listing_id or '')
                }
            )

            client.logoff()
            logger.info(f"Asterisk call initiated for {phone}")
            return True

        except ImportError:
            logger.error("asterisk.ami library not installed. Run: pip install asterisk.ami")
            return False
        except Exception as e:
            logger.error(f"Asterisk call failed for {phone}: {e}")
            return False

    def _dial_twilio(self, phone: str, listing_url: Optional[str], listing_id: Optional[int]) -> bool:
        """Звонок через Twilio"""
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
            logger.error("Twilio credentials not configured")
            return False

        try:
            # Примечание: Требуется библиотека twilio
            # pip install twilio
            from twilio.rest import Client

            client = Client(self.twilio_account_sid, self.twilio_auth_token)

            # URL для TwiML (голосового ответа)
            # Можно настроить свой сервер с TwiML или использовать Twilio Bins
            twiml_url = os.getenv('TWILIO_TWIML_URL', 'http://demo.twilio.com/docs/voice.xml')

            call = client.calls.create(
                to=phone,
                from_=self.twilio_from_number,
                url=twiml_url,
                status_callback=os.getenv('TWILIO_STATUS_CALLBACK_URL'),
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST'
            )

            logger.info(f"Twilio call initiated for {phone}, SID: {call.sid}")
            return True

        except ImportError:
            logger.error("twilio library not installed. Run: pip install twilio")
            return False
        except Exception as e:
            logger.error(f"Twilio call failed for {phone}: {e}")
            return False

    def _dial_mock(self, phone: str, listing_url: Optional[str], listing_id: Optional[int]) -> bool:
        """Mock режим для тестирования (не звонит реально)"""
        logger.info(f"[MOCK] Would dial {phone} for listing {listing_id or 'N/A'}")
        if listing_url:
            logger.info(f"[MOCK] Listing URL: {listing_url}")
        return True


# Пример использования
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Тестирование в mock режиме
    dialer = AutoDialer(backend='mock')
    dialer.dial('+79991234567', 'https://cian.ru/rent/123456', 1)

    # Пример с webhook
    # dialer = AutoDialer(
    #     backend='webhook',
    #     webhook_url='https://your-server.com/api/dial'
    # )
    # dialer.dial('+79991234567')

    # Пример с Twilio
    # dialer = AutoDialer(
    #     backend='twilio',
    #     twilio_account_sid='ACxxxxx',
    #     twilio_auth_token='your_token',
    #     twilio_from_number='+15551234567'
    # )
    # dialer.dial('+79991234567')
