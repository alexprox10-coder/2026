#!/usr/bin/env python3
"""
AI Агент прогрева лидов через Telegram

Логика:
1. Берёт лиды из Google Sheets (таблица парсера)
2. Пишет лидам по username через Telethon
3. Ведёт AI-диалог для квалификации
4. Обновляет статус: new -> warming -> qualified/refused

Требования:
pip install telethon gspread google-auth aiohttp python-dotenv
"""

import os
import json
import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import (
    UserNotMutualContactError,
    UserPrivacyRestrictedError,
    FloodWaitError,
    PeerIdInvalidError
)
import gspread
from google.oauth2.service_account import Credentials
import aiohttp

# Загружаем .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('warmup_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """Работа с Google Sheets"""

    def __init__(self):
        self.sheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self.sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Telegram_Leads_Template')
        self.client = None
        self.sheet = None

    def connect(self):
        """Подключение к Google Sheets"""
        creds_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service_account.json')

        if not Path(creds_file).exists():
            logger.error(f"Файл {creds_file} не найден! Создай Service Account в Google Cloud Console")
            return False

        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
        self.client = gspread.authorize(creds)

        try:
            spreadsheet = self.client.open_by_key(self.sheet_id)
            self.sheet = spreadsheet.worksheet(self.sheet_name)
            logger.info(f"Подключено к таблице: {self.sheet_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к Google Sheets: {e}")
            return False

    def get_new_leads(self, limit: int = 10) -> List[Dict]:
        """Получить новые лиды для прогрева"""
        if not self.sheet:
            return []

        try:
            # Получаем все записи
            records = self.sheet.get_all_records()

            # Фильтруем: есть username, статус new или пустой, не реклама
            leads = []
            for i, row in enumerate(records, start=2):  # +2 потому что 1 строка - заголовки
                username = row.get('usernames', '').strip()
                status = row.get('status', '').strip().lower()
                is_ad = str(row.get('is_ad', '')).lower() in ['true', '1', 'yes']

                # Пропускаем если нет username или уже обработан
                if not username or username == '':
                    continue
                if status and status not in ['new', '']:
                    continue
                if is_ad:
                    continue

                leads.append({
                    'row_number': i,
                    'username': username.split(',')[0].strip(),  # Берём первый username
                    'text': row.get('text', ''),
                    'text_preview': row.get('text_preview', ''),
                    'niche': row.get('niche', ''),
                    'channel': row.get('channel_title', ''),
                    'lead_score': row.get('lead_score', 0),
                    'phones': row.get('phones', ''),
                    'post_url': row.get('post_url', '')
                })

                if len(leads) >= limit:
                    break

            logger.info(f"Найдено {len(leads)} новых лидов для прогрева")
            return leads

        except Exception as e:
            logger.error(f"Ошибка получения лидов: {e}")
            return []

    def update_lead_status(self, row_number: int, status: str, notes: str = ''):
        """Обновить статус лида"""
        if not self.sheet:
            return

        try:
            # Находим колонку status
            headers = self.sheet.row_values(1)

            if 'status' in headers:
                status_col = headers.index('status') + 1
                self.sheet.update_cell(row_number, status_col, status)

            # Обновляем chat_id если есть
            if 'warmup_notes' in headers:
                notes_col = headers.index('warmup_notes') + 1
                self.sheet.update_cell(row_number, notes_col, notes)

            logger.info(f"Обновлён статус строки {row_number}: {status}")

        except Exception as e:
            logger.error(f"Ошибка обновления статуса: {e}")

    def save_qualified_lead(self, lead_data: Dict):
        """Сохранить квалифицированного лида в отдельный лист"""
        try:
            spreadsheet = self.client.open_by_key(self.sheet_id)

            # Пробуем найти лист qualified_leads
            try:
                qualified_sheet = spreadsheet.worksheet('qualified_leads')
            except:
                # Создаём если нет
                qualified_sheet = spreadsheet.add_worksheet(
                    title='qualified_leads',
                    rows=1000,
                    cols=20
                )
                # Добавляем заголовки
                qualified_sheet.append_row([
                    'timestamp', 'username', 'chat_id', 'city', 'property_type',
                    'rooms', 'budget', 'payment_method', 'timeline', 'contact',
                    'source_channel', 'source_text', 'status'
                ])

            # Добавляем лида
            qualified_sheet.append_row([
                datetime.now().isoformat(),
                lead_data.get('username', ''),
                lead_data.get('chat_id', ''),
                lead_data.get('city', ''),
                lead_data.get('property_type', ''),
                lead_data.get('rooms', ''),
                lead_data.get('budget', ''),
                lead_data.get('payment_method', ''),
                lead_data.get('timeline', ''),
                lead_data.get('contact', ''),
                lead_data.get('source_channel', ''),
                lead_data.get('source_text', '')[:200],
                'qualified'
            ])

            logger.info(f"Сохранён квалифицированный лид: {lead_data.get('username')}")

        except Exception as e:
            logger.error(f"Ошибка сохранения квалифицированного лида: {e}")


class AIAssistant:
    """AI помощник для генерации сообщений"""

    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = 'https://openrouter.ai/api/v1/chat/completions'

    async def generate_response(
        self,
        lead_context: Dict,
        conversation_history: List[Dict],
        is_first_message: bool = False
    ) -> Dict:
        """Генерация ответа AI"""

        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY не установлен, используем шаблон")
            return self._get_template_response(lead_context, is_first_message)

        # Формируем системный промпт
        system_prompt = self._build_system_prompt(lead_context)

        messages = [{"role": "system", "content": system_prompt}]

        # Добавляем историю диалога
        for msg in conversation_history[-10:]:  # Последние 10 сообщений
            messages.append(msg)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json',
                        'HTTP-Referer': 'https://warmup-bot.local'
                    },
                    json={
                        'model': 'openai/gpt-4o-mini',
                        'messages': messages,
                        'temperature': 0.7,
                        'max_tokens': 300
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        content = data['choices'][0]['message']['content']
                        return self._parse_ai_response(content)
                    else:
                        logger.error(f"AI API ошибка: {resp.status}")
                        return self._get_template_response(lead_context, is_first_message)

        except Exception as e:
            logger.error(f"Ошибка AI: {e}")
            return self._get_template_response(lead_context, is_first_message)

    def _build_system_prompt(self, lead_context: Dict) -> str:
        """Создание системного промпта"""
        niche = lead_context.get('niche', 'realty')
        original_text = lead_context.get('text', '')[:300]

        return f"""Ты — вежливый помощник по подбору недвижимости в Москве и МО.

КОНТЕКСТ:
- Человек написал в канале: "{original_text}"
- Ниша: {niche}

ТВОЯ ЗАДАЧА:
1. Начни диалог мягко, покажи что видел запрос
2. Уточни потребности: город/район, тип объекта, комнаты, бюджет, срок
3. Когда всё узнаешь — предложи связь с риелтором

ПРАВИЛА:
- Пиши коротко, 1-2 предложения
- Один вопрос за раз
- Будь человечным, не роботом
- Не обсуждай цены и юридические вопросы

ОТВЕЧАЙ JSON:
{{
  "response": "твой текст ответа",
  "extracted": {{
    "city": "город если упомянут",
    "property_type": "тип объекта",
    "rooms": "количество комнат",
    "budget": "бюджет",
    "payment_method": "способ оплаты",
    "timeline": "срок покупки",
    "contact": "контакт если дал"
  }},
  "is_complete": false,
  "is_refused": false
}}"""

    def _parse_ai_response(self, content: str) -> Dict:
        """Парсинг ответа AI"""
        try:
            # Ищем JSON в ответе
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    'response': content,
                    'extracted': {},
                    'is_complete': False,
                    'is_refused': False
                }
        except:
            return {
                'response': content,
                'extracted': {},
                'is_complete': False,
                'is_refused': False
            }

    def _get_template_response(self, lead_context: Dict, is_first: bool) -> Dict:
        """Шаблонный ответ если AI недоступен"""
        if is_first:
            templates = [
                "Здравствуйте! Увидел ваш запрос по недвижимости. Подскажите, какой район рассматриваете?",
                "Добрый день! Заметил что ищете недвижимость. В каком городе/районе хотели бы?",
                "Привет! Могу помочь с подбором недвижимости. Какой тип объекта интересует?"
            ]
            return {
                'response': random.choice(templates),
                'extracted': {},
                'is_complete': False,
                'is_refused': False
            }
        else:
            return {
                'response': "Спасибо за информацию! А какой примерно бюджет рассматриваете?",
                'extracted': {},
                'is_complete': False,
                'is_refused': False
            }


class WarmupAgent:
    """Основной агент прогрева"""

    def __init__(self):
        self.api_id = int(os.getenv('TELEGRAM_API_ID'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')

        self.client: Optional[TelegramClient] = None
        self.sheets = GoogleSheetsManager()
        self.ai = AIAssistant()

        # Хранилище диалогов (chat_id -> context)
        self.conversations: Dict[int, Dict] = {}

        # Настройки
        self.delay_min = int(os.getenv('WARMUP_DELAY_MIN', 60))
        self.delay_max = int(os.getenv('WARMUP_DELAY_MAX', 180))
        self.daily_limit = int(os.getenv('WARMUP_DAILY_LIMIT', 20))

        # Счётчики
        self.messages_sent_today = 0
        self.last_reset = datetime.now().date()

    async def start(self):
        """Запуск агента"""
        logger.info("Запуск агента прогрева...")

        # Подключаемся к Google Sheets
        if not self.sheets.connect():
            logger.error("Не удалось подключиться к Google Sheets")
            return False

        # Подключаемся к Telegram
        self.client = TelegramClient(
            'telegram_session',
            self.api_id,
            self.api_hash
        )

        await self.client.start(phone=self.phone)
        logger.info("Подключено к Telegram")

        # Регистрируем обработчик входящих сообщений
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_incoming(event):
            await self._handle_response(event)

        return True

    async def stop(self):
        """Остановка агента"""
        if self.client:
            await self.client.disconnect()
        logger.info("Агент остановлен")

    def _reset_daily_counter(self):
        """Сброс дневного счётчика"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.messages_sent_today = 0
            self.last_reset = today
            logger.info("Дневной счётчик сброшен")

    async def warmup_leads(self, limit: int = 5) -> Dict:
        """Прогреть партию лидов"""
        self._reset_daily_counter()

        if self.messages_sent_today >= self.daily_limit:
            logger.warning(f"Достигнут дневной лимит: {self.daily_limit}")
            return {'status': 'limit_reached', 'sent': 0}

        # Получаем лидов
        available = self.daily_limit - self.messages_sent_today
        leads = self.sheets.get_new_leads(min(limit, available))

        if not leads:
            logger.info("Нет новых лидов для прогрева")
            return {'status': 'no_leads', 'sent': 0}

        results = {
            'status': 'ok',
            'sent': 0,
            'failed': 0,
            'details': []
        }

        for lead in leads:
            try:
                success = await self._send_first_message(lead)

                if success:
                    results['sent'] += 1
                    self.messages_sent_today += 1
                    self.sheets.update_lead_status(lead['row_number'], 'warming')
                else:
                    results['failed'] += 1
                    self.sheets.update_lead_status(lead['row_number'], 'unreachable')

                results['details'].append({
                    'username': lead['username'],
                    'success': success
                })

                # Пауза между сообщениями
                delay = random.randint(self.delay_min, self.delay_max)
                logger.info(f"Пауза {delay} секунд...")
                await asyncio.sleep(delay)

            except FloodWaitError as e:
                logger.warning(f"FloodWait: ждём {e.seconds} секунд")
                await asyncio.sleep(e.seconds)
                results['failed'] += 1

            except Exception as e:
                logger.error(f"Ошибка отправки {lead['username']}: {e}")
                results['failed'] += 1

        return results

    async def _send_first_message(self, lead: Dict) -> bool:
        """Отправить первое сообщение лиду"""
        username = lead['username']

        # Убираем @ если есть
        if username.startswith('@'):
            username = username[1:]

        try:
            # Получаем entity пользователя
            entity = await self.client.get_entity(username)
            chat_id = entity.id

            # Генерируем первое сообщение
            ai_response = await self.ai.generate_response(
                lead_context=lead,
                conversation_history=[],
                is_first_message=True
            )

            message_text = ai_response.get('response', '')

            if not message_text:
                logger.warning(f"Пустое сообщение для {username}")
                return False

            # Отправляем
            await self.client.send_message(entity, message_text)
            logger.info(f"Отправлено {username}: {message_text[:50]}...")

            # Сохраняем контекст диалога
            self.conversations[chat_id] = {
                'lead': lead,
                'history': [
                    {'role': 'assistant', 'content': message_text}
                ],
                'collected_data': ai_response.get('extracted', {}),
                'started_at': datetime.now().isoformat()
            }

            return True

        except (UserNotMutualContactError, UserPrivacyRestrictedError) as e:
            logger.warning(f"Не могу написать {username}: приватность")
            return False

        except PeerIdInvalidError:
            logger.warning(f"Пользователь не найден: {username}")
            return False

        except Exception as e:
            logger.error(f"Ошибка отправки {username}: {e}")
            return False

    async def _handle_response(self, event):
        """Обработка входящего сообщения от лида"""
        chat_id = event.chat_id
        text = event.text

        # Проверяем, это ответ на наш прогрев?
        if chat_id not in self.conversations:
            return

        logger.info(f"Получен ответ от {chat_id}: {text[:50]}...")

        context = self.conversations[chat_id]

        # Добавляем сообщение в историю
        context['history'].append({'role': 'user', 'content': text})

        # Генерируем ответ
        ai_response = await self.ai.generate_response(
            lead_context=context['lead'],
            conversation_history=context['history'],
            is_first_message=False
        )

        response_text = ai_response.get('response', '')

        # Обновляем собранные данные
        extracted = ai_response.get('extracted', {})
        for key, value in extracted.items():
            if value and value != 'null':
                context['collected_data'][key] = value

        # Отправляем ответ
        if response_text:
            await event.respond(response_text)
            context['history'].append({'role': 'assistant', 'content': response_text})
            logger.info(f"Ответили {chat_id}: {response_text[:50]}...")

        # Проверяем статус
        if ai_response.get('is_complete'):
            logger.info(f"Лид {chat_id} квалифицирован!")
            self.sheets.update_lead_status(
                context['lead']['row_number'],
                'qualified',
                json.dumps(context['collected_data'], ensure_ascii=False)
            )
            self.sheets.save_qualified_lead({
                **context['collected_data'],
                'username': context['lead']['username'],
                'chat_id': str(chat_id),
                'source_channel': context['lead'].get('channel', ''),
                'source_text': context['lead'].get('text', '')
            })
            # Удаляем из активных диалогов
            del self.conversations[chat_id]

        elif ai_response.get('is_refused'):
            logger.info(f"Лид {chat_id} отказался")
            self.sheets.update_lead_status(
                context['lead']['row_number'],
                'refused'
            )
            del self.conversations[chat_id]

    async def run_forever(self):
        """Запуск в режиме ожидания ответов"""
        logger.info("Агент работает в режиме ожидания ответов...")
        await self.client.run_until_disconnected()

    def get_stats(self) -> Dict:
        """Получить статистику"""
        return {
            'messages_sent_today': self.messages_sent_today,
            'daily_limit': self.daily_limit,
            'active_conversations': len(self.conversations),
            'last_reset': self.last_reset.isoformat()
        }


async def main():
    """Пример использования"""
    agent = WarmupAgent()

    try:
        if await agent.start():
            # Прогреваем 5 лидов
            results = await agent.warmup_leads(limit=5)
            print(f"Результаты: {results}")

            # Ждём ответы
            print("Ожидание ответов (Ctrl+C для выхода)...")
            await agent.run_forever()
    except KeyboardInterrupt:
        print("\nОстановка...")
    finally:
        await agent.stop()


if __name__ == '__main__':
    asyncio.run(main())
