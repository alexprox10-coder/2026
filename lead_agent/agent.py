"""
Интеллектуальный ассистент для сбора информации о компаниях
Использует Claude AI для обработки команд пользователя
"""
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List
import anthropic
from anthropic import Anthropic

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

from config.settings import (
    ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS,
    LOG_LEVEL, LOG_FILE, GOOGLE_SHEETS_ID
)
from modules.google_sheets import GoogleSheetsManager
from modules.telegram_bot import TelegramNotifier
from modules.google_maps import GoogleMapsParser
from modules.scraper import WebScraper

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class LeadCollectionAgent:
    """Главный агент для сбора лидов"""

    def __init__(self):
        """Инициализация агента и всех модулей"""
        logger.info("Инициализация агента...")

        # Инициализация Claude AI
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY не настроен в .env файле")

        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

        # Инициализация модулей
        self.sheets = GoogleSheetsManager()
        self.telegram = TelegramNotifier()
        self.maps_parser = GoogleMapsParser()
        self.scraper = WebScraper()

        # Системный промпт агента
        self.system_prompt = self._load_system_prompt()

        # История разговора
        self.conversation_history = []

        logger.info("Агент успешно инициализирован")

    def _load_system_prompt(self) -> str:
        """Загрузить системный промпт агента"""
        return f"""ТЫ – ИНТЕЛЛЕКТУАЛЬНЫЙ АССИСТЕНТ ДЛЯ СБОРА ИНФОРМАЦИИ О КОМПАНИЯХ. ТЫ ОБЛАДАЕШЬ ПОЛНЫМ ДОСТУПОМ К НАБОРУ ИНСТРУМЕНТОВ ДЛЯ ПОИСКА, АНАЛИЗА И ФИКСАЦИИ ДАННЫХ В GOOGLE SHEETS. ТВОЯ ЗАДАЧА – ЧЕТКО ИСПОЛНЯТЬ КОМАНДЫ ПОЛЬЗОВАТЕЛЯ И ОПТИМАЛЬНО ИСПОЛЬЗОВАТЬ ИНСТРУМЕНТЫ.

### ДАННЫЕ ПОЛЬЗОВАТЕЛЯ ###
- **Google Sheets ID**: {GOOGLE_SHEETS_ID}
- **Листы таблицы**: ЗАПРОСЫ, САЙТЫ, КОМПАНИИ, ПИСЬМА
- **Регион работы**: Вся Россия
- **Часовой пояс**: MSK (Московское время)
- **Целевые ниши**: агентства недвижимости, автосервисы, стоматологии, локальный бизнес
- **Инструменты парсинга**: Claude AI (встроенные возможности), Google Maps API
- **Платформа автоматизации**: n8n workflow

### ДОСТУПНЫЕ ИНСТРУМЕНТЫ ###
1. **AgentLeadAddQuery** – СОЗДАЕТ И СОХРАНЯЕТ ЗАПРОСЫ В GOOGLE SHEETS (лист "ЗАПРОСЫ"), ЕСЛИ ПОЛЬЗОВАТЕЛЬ ПРОСИТ СОБРАТЬ ЗАПРОСЫ, ТЫ ДОЛЖЕН ВЫПОЛНИТЬ ЭТОТ ИНСТРУМЕНТ
2. **AgentLeadAddSiteCompany** – СОБИРАЕТ САЙТЫ КОМПАНИЙ ИЗ GOOGLE MAPS ПО СОЗДАННЫМ ЗАПРОСАМ (лист "САЙТЫ")
3. **AgentLeadScrapInformationCompany** – СОБИРАЕТ ДАННЫЕ О КОМПАНИЯХ С ИХ САЙТОВ (лист "КОМПАНИИ")
4. **TelegramMessage** – ОТПРАВЛЯЕТ ТЕХНИЧЕСКОЕ СООБЩЕНИЕ О НАЧАЛЕ РАБОТЫ
5. **QuerySheets** – ВОЗВРАЩАЕТ ЗАПРОСЫ ИЗ GOOGLE SHEETS, КОТОРЫЕ ЕЩЁ НЕ ОБРАБАТЫВАЛИСЬ (статус = 0)
6. **SiteCompanySheets** – ВОЗВРАЩАЕТ САЙТЫ КОМПАНИЙ ИЗ GOOGLE SHEETS, ПО КОТОРЫМ ЕЩЁ НЕ БЫЛО СБОРА ДАННЫХ (статус = 0)
7. **AgentLeadMailGenerate** – СОЗДАЁТ ЧЕРНОВИК ПИСЬМА И СОХРАНЯЕТ ЕГО В GOOGLE SHEETS (лист "ПИСЬМА")

### ЛОГИКА РАБОТЫ ###
1. **ОТПРАВКА ТЕХНИЧЕСКОГО СООБЩЕНИЯ В ПЕРВУЮ ОЧЕРЕДЬ**
   - В первую очередь, перед вызовом инструментов, вызови `TelegramMessage`
   - Сообщи пользователю, что ты начал выполнять задачу, скажи что тебе понадобится некоторое время, предупреди что процессы долгие
   - Сразу переходи к поставленной задаче

2. **ПРОВЕРКА НЕОБРАБОТАННЫХ ЗАПРОСОВ**
   - Если пользователь запрашивает невыполненные запросы, вызови инструмент `QuerySheets`
   - Проанализируй результат и верни часть запросов со статусом 0

3. **СОЗДАНИЕ НОВЫХ ЗАПРОСОВ**
   - Если пользователь просит создать новые запросы (например: "давай соберём стоматологии по Самаре"), вызови `AgentLeadAddQuery`
   - Передай запрос в формате: "Подготовить запросы на тему {{тема}}, город {{город}}"
   - После выполнения инструмента, сообщи пользователю, что запросы успешно созданы
   - Если пользователь просит собрать ещё запросы, вызови `AgentLeadAddQuery`

4. **СБОР САЙТОВ ПО ЗАПРОСАМ**
   - Если пользователь просит собрать сайты, вызови `AgentLeadAddSiteCompany`
   - Просто запусти инструмент и сообщи пользователю, что сбор сайтов начат

5. **СБОР ИНФОРМАЦИИ О КОМПАНИЯХ**
   - Перед вызовом `AgentLeadScrapInformationCompany` вызови инструмент `SiteCompanySheets`, убедись что есть сайты с нулевым статусом получения данных
   - Если пользователь просит собрать данные о компаниях, вызови `AgentLeadScrapInformationCompany`
   - Если пользователь просит собрать информацию о компаниях вызови `AgentLeadScrapInformationCompany`
   - Если пользователь просит собрать информацию с сайтов вызови `AgentLeadScrapInformationCompany`
   - Просто запусти инструмент, но перед запуском, сообщи пользователю, что сбор данных начат

6. **СОЗДАНИЯ ЧЕРНОВИКА ПИСЬМА**
   - Если пользователь просит создать письма для компаний вызови `AgentLeadMailGenerate`
   - Если пользователь просит создать черновик писем по собранным компаниям вызови `AgentLeadMailGenerate`
   - Просто запусти инструмент `AgentLeadMailGenerate` и сообщи пользователю что создание писем начато

### Дополнительные задачи ###
   - Если ты получил ошибку, верни её опиши что произошло, и предложи войти в систему чтобы решить её
   - Если ты получаешь ошибку обязательно напиши в каком инструменте это произошло
   - Если пользователь просто пишет привет, предложи ему схему своей работы, при условии если это просто привет, без доп текста, в иных случаях выполняй поставленную задачу

### ЧТО НЕ ДЕЛАТЬ ###
- **НЕ СПРАШИВАЙ У ПОЛЬЗОВАТЕЛЯ ЛИШНИХ ПОДРОБНОСТЕЙ**, ЕСЛИ ВСЕ ДАННЫЕ УЖЕ ЯСНЫ
- **НЕ ВЫПОЛНЯЙ ДЕЙСТВИЯ, КОТОРЫЕ НЕ ОПИСАНЫ В ИНСТРУКЦИЯХ**
- **НЕ ДУМАЙ, ЧТО ЗАПРОСЫ УЖЕ ЕСТЬ – ВСЕГДА ПРОВЕРЯЙ `QuerySheets`**
- **НЕ ПРОСИ ПОДТВЕРЖДЕНИЯ, ЕСЛИ ПОЛЬЗОВАТЕЛЬ УЖЕ ОТДАЛ КОНКРЕТНУЮ КОМАНДУ**
- **НЕ СМОТРИ НА ПАМЯТЬ ЕСЛИ ПОЛЬЗОВАТЕЛЬ ПРОСИТ СОБРАТЬ ЕЩЁ ЗАПРОСЫ, ВЫПОЛНИ ЗАДАЧУ**

Ты должен использовать инструменты через function calling. Отвечай ЧЕТКО и КРАТКО."""

    def _get_tools_definition(self) -> List[Dict[str, Any]]:
        """Определение доступных инструментов для Claude"""
        return [
            {
                "name": "TelegramMessage",
                "description": "Отправляет техническое сообщение в Telegram о начале работы. Вызывай ПЕРВЫМ перед любыми другими действиями.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Текст сообщения для пользователя"
                        },
                        "message_type": {
                            "type": "string",
                            "enum": ["start", "progress", "success", "error"],
                            "description": "Тип сообщения"
                        }
                    },
                    "required": ["message", "message_type"]
                }
            },
            {
                "name": "QuerySheets",
                "description": "Возвращает список запросов из Google Sheets со статусом = 0 (необработанные)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Максимальное количество запросов для возврата",
                            "default": 10
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "AgentLeadAddQuery",
                "description": "Создаёт и сохраняет поисковые запросы в Google Sheets (лист ЗАПРОСЫ). Генерирует несколько вариантов запросов для поиска компаний по заданной теме и городу.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "request": {
                            "type": "string",
                            "description": "Описание задачи, например: 'Подготовить запросы на тему стоматологии, город Москва'"
                        }
                    },
                    "required": ["request"]
                }
            },
            {
                "name": "SiteCompanySheets",
                "description": "Возвращает список сайтов компаний из Google Sheets со статусом = 0 (данные не собраны)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Максимальное количество сайтов для возврата",
                            "default": 10
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "AgentLeadAddSiteCompany",
                "description": "Собирает сайты компаний из Google Maps по созданным запросам и сохраняет в Google Sheets (лист САЙТЫ)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "max_queries": {
                            "type": "integer",
                            "description": "Максимальное количество запросов для обработки",
                            "default": 5
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "AgentLeadScrapInformationCompany",
                "description": "Собирает детальную информацию о компаниях с их сайтов и сохраняет в Google Sheets (лист КОМПАНИИ)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "max_sites": {
                            "type": "integer",
                            "description": "Максимальное количество сайтов для обработки",
                            "default": 10
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "AgentLeadMailGenerate",
                "description": "Создаёт персонализированные черновики писем для собранных компаний и сохраняет в Google Sheets (лист ПИСЬМА)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "max_companies": {
                            "type": "integer",
                            "description": "Максимальное количество писем для создания",
                            "default": 10
                        }
                    },
                    "required": []
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнить вызов инструмента

        Args:
            tool_name: Название инструмента
            tool_input: Параметры инструмента

        Returns:
            Результат выполнения
        """
        logger.info(f"Выполнение инструмента: {tool_name} с параметрами: {tool_input}")

        try:
            if tool_name == "TelegramMessage":
                return self._tool_telegram_message(tool_input)

            elif tool_name == "QuerySheets":
                return self._tool_query_sheets(tool_input)

            elif tool_name == "AgentLeadAddQuery":
                return self._tool_add_query(tool_input)

            elif tool_name == "SiteCompanySheets":
                return self._tool_site_company_sheets(tool_input)

            elif tool_name == "AgentLeadAddSiteCompany":
                return self._tool_add_site_company(tool_input)

            elif tool_name == "AgentLeadScrapInformationCompany":
                return self._tool_scrap_information(tool_input)

            elif tool_name == "AgentLeadMailGenerate":
                return self._tool_generate_mail(tool_input)

            else:
                return {"error": f"Неизвестный инструмент: {tool_name}"}

        except Exception as e:
            logger.error(f"Ошибка при выполнении инструмента {tool_name}: {e}")
            return {"error": str(e), "tool": tool_name}

    def _tool_telegram_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка сообщения в Telegram"""
        message = params.get("message", "")
        message_type = params.get("message_type", "start")

        if message_type == "start":
            success = self.telegram.send_start_notification(message)
        elif message_type == "progress":
            success = self.telegram.send_progress_notification("Выполнение", message)
        elif message_type == "success":
            success = self.telegram.send_success_notification("Завершено", message)
        elif message_type == "error":
            success = self.telegram.send_error_notification("Ошибка", message)
        else:
            success = self.telegram.send_message(message)

        return {"success": success, "message": "Сообщение отправлено в Telegram"}

    def _tool_query_sheets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Получить необработанные запросы из Google Sheets"""
        limit = params.get("limit", 10)
        queries = self.sheets.get_queries_with_status(status=0)

        return {
            "success": True,
            "count": len(queries),
            "queries": queries[:limit]
        }

    def _tool_add_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Создать и сохранить запросы"""
        request = params.get("request", "")

        # Используем Claude для генерации запросов
        prompt = f"""На основе следующего запроса создай 5-10 вариантов поисковых запросов для Google Maps:

{request}

Верни ТОЛЬКО JSON массив объектов с полями: тема, город, запрос, статус (всегда 0).

Пример:
[
  {{"тема": "стоматология", "город": "Москва", "запрос": "стоматология Москва", "статус": 0}},
  {{"тема": "стоматология", "город": "Москва", "запрос": "зубной врач Москва", "статус": 0}}
]
"""

        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )

            # Парсим ответ
            import json
            response_text = response.content[0].text
            # Извлекаем JSON из ответа
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            json_text = response_text[start_idx:end_idx]

            queries = json.loads(json_text)

            # Сохраняем в Google Sheets
            success = self.sheets.add_queries(queries)

            return {
                "success": success,
                "count": len(queries),
                "message": f"Создано {len(queries)} запросов"
            }

        except Exception as e:
            logger.error(f"Ошибка при создании запросов: {e}")
            return {"success": False, "error": str(e)}

    def _tool_site_company_sheets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Получить сайты компаний со статусом 0"""
        limit = params.get("limit", 10)
        sites = self.sheets.get_sites_with_status(status=0)

        return {
            "success": True,
            "count": len(sites),
            "sites": sites[:limit]
        }

    def _tool_add_site_company(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Собрать сайты компаний из Google Maps (200-300 штук, без дублей)"""
        max_queries = params.get("max_queries", 10)
        target_count = params.get("target_count", 250)  # Целевое количество сайтов

        # Получаем необработанные запросы
        queries = self.sheets.get_queries_with_status(status=0)[:max_queries]

        if not queries:
            return {"success": False, "message": "Нет необработанных запросов"}

        # Получаем существующие сайты для проверки дублей
        try:
            existing_sites_sheet = self.sheets.get_worksheet(self.sheets.spreadsheet.worksheet('САЙТЫ'))
            existing_records = existing_sites_sheet.get_all_records()
            existing_sites = set(record.get('Сайт', '').lower().strip() for record in existing_records if record.get('Сайт'))
        except:
            existing_sites = set()

        all_sites = []
        processed_urls = set()

        for query in queries:
            if len(all_sites) >= target_count:
                break

            query_text = query.get('Запрос', '')
            city = query.get('Город', '')
            category = query.get('Тема', '')
            query_id = query.get('ID', '')

            # Парсим Google Maps с увеличенным лимитом
            places = self.maps_parser.search_places(query_text, city)

            # Подготавливаем данные для сохранения
            for place in places:
                site_url = place.get('сайт', '').lower().strip()

                # Проверяем на дубли
                if not site_url:
                    continue

                if site_url in existing_sites or site_url in processed_urls:
                    logger.debug(f"Пропуск дубликата: {site_url}")
                    continue

                site_data = {
                    'название': place.get('название', ''),
                    'сайт': place.get('сайт', ''),
                    'телефон': place.get('телефон', ''),
                    'адрес': place.get('адрес', ''),
                    'город': city,
                    'категория': category,
                    'статус': 0,
                    'id_запроса': query_id
                }
                all_sites.append(site_data)
                processed_urls.add(site_url)

                if len(all_sites) >= target_count:
                    break

            # Обновляем статус запроса
            self.sheets.update_query_status(query_id, status=1)

        # Сохраняем сайты
        if all_sites:
            success = self.sheets.add_sites(all_sites)
            return {
                "success": success,
                "count": len(all_sites),
                "message": f"✅ Собрано {len(all_sites)} сайтов компаний (без дублей)\n\n📊 Все сайты добавлены в Google Sheets.\n\n❓ Собрать контактные данные с сайтов?"
            }

        return {"success": False, "message": "Сайты не найдены"}

    def _tool_scrap_information(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Собрать информацию о компаниях с их сайтов"""
        max_sites = params.get("max_sites", 50)  # Увеличиваем лимит

        # Получаем сайты со статусом 0
        sites = self.sheets.get_sites_with_status(status=0)[:max_sites]

        if not sites:
            return {"success": False, "message": "Нет сайтов для обработки"}

        companies = []
        errors = 0

        for site in sites:
            site_url = site.get('Сайт', '')
            if not site_url:
                continue

            try:
                # Парсим информацию
                company_info = self.scraper.scrape_company_info(site_url)

                # Дополняем данными из Google Sheets
                company_info['id_сайта'] = site.get('ID', '')

                # Если название не найдено на сайте, берём из таблицы
                if not company_info.get('название'):
                    company_info['название'] = site.get('Название компании', '')

                # Пытаемся найти страницу контактов
                contact_info = self.scraper.scrape_contact_page(site_url)
                if contact_info:
                    if not company_info['email'] and contact_info.get('email'):
                        company_info['email'] = contact_info['email']
                    if not company_info['телефон'] and contact_info.get('телефон'):
                        company_info['телефон'] = contact_info['телефон']

                companies.append(company_info)

                # Обновляем статус сайта
                self.sheets.update_site_status(site.get('ID', ''), status=1)

            except Exception as e:
                logger.error(f"Ошибка при парсинге {site_url}: {e}")
                errors += 1
                continue

        # Сохраняем компании
        if companies:
            success = self.sheets.add_companies(companies)
            return {
                "success": success,
                "count": len(companies),
                "errors": errors,
                "message": f"✅ Собрана информация о {len(companies)} компаниях\n\n📊 Данные сохранены в Google Sheets (лист КОМПАНИИ)\n{f'⚠️ Ошибок при парсинге: {errors}' if errors > 0 else ''}\n\n❓ Создать коммерческие предложения для компаний?"
            }

        return {"success": False, "message": "Не удалось собрать информацию"}

    def _tool_generate_mail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Создать черновики персонализированных КП про автоматизацию бизнеса"""
        max_companies = params.get("max_companies", 30)  # Увеличиваем лимит

        # Получаем компании из Google Sheets
        try:
            worksheet = self.sheets.get_worksheet(self.sheets.spreadsheet.worksheet('КОМПАНИИ'))
            companies = worksheet.get_all_records()[:max_companies]
        except Exception as e:
            logger.error(f"Ошибка получения компаний: {e}")
            return {"success": False, "message": "Ошибка доступа к данным компаний"}

        if not companies:
            return {"success": False, "message": "Нет компаний для создания писем"}

        letters = []
        errors = 0

        for company in companies:
            company_name = company.get('Название компании', '')
            company_site = company.get('Сайт', '')
            email = company.get('Email', '')
            description = company.get('Описание', '')
            services = company.get('Услуги', '')
            phone = company.get('Телефон', '')
            address = company.get('Адрес', '')

            if not email:
                logger.debug(f"Пропуск {company_name}: нет email")
                continue

            # Используем Claude для анализа компании и создания КП
            prompt = f"""Ты - эксперт по автоматизации бизнес-процессов. Проанализируй компанию и создай персонализированное коммерческое предложение.

## ИНФОРМАЦИЯ О КОМПАНИИ:
Название: {company_name}
Сайт: {company_site}
Описание: {description}
Услуги: {services}
Телефон: {phone}
Адрес: {address}

## ТВОЯ ЗАДАЧА:

1. **Проанализируй бизнес компании:**
   - Определи сферу деятельности
   - Выяви типичные боли и проблемы этой ниши
   - Определи процессы, которые можно автоматизировать

2. **Создай персонализированное КП про автоматизацию:**
   - Обращайся напрямую к болям компании
   - Предложи конкретные решения по автоматизации:
     * Автоматизация обработки заявок и лидов
     * CRM и системы учёта клиентов
     * Автоматические уведомления и рассылки
     * Интеграция сервисов (Telegram, WhatsApp, Email, 1C, AmoCRM)
     * Чат-боты для клиентов
     * Аналитика и отчётность
     * AI-ассистенты для бизнеса
   - Укажи выгоды: экономия времени, снижение ошибок, рост продаж
   - Призыв к действию: бесплатная консультация

3. **Формат письма:**
   - Тема: короткая и цепляющая (до 50 символов)
   - Текст: 150-250 слов, структурированный, с конкретными примерами
   - Тон: профессиональный, но дружелюбный
   - Без шаблонных фраз, только ценность

Верни результат СТРОГО в JSON формате:
{{
  "тема": "Тема письма",
  "текст": "Текст коммерческого предложения"
}}"""

            try:
                response = self.client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}]
                )

                import json
                response_text = response.content[0].text

                # Ищем JSON в ответе
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1

                if start_idx == -1 or end_idx == 0:
                    logger.error(f"JSON не найден в ответе для {company_name}")
                    errors += 1
                    continue

                json_text = response_text[start_idx:end_idx]
                letter_data = json.loads(json_text)

                letter = {
                    'название': company_name,
                    'email': email,
                    'тема': letter_data.get('тема', f'Автоматизация для {company_name}'),
                    'текст': letter_data.get('текст', ''),
                    'статус': 0,
                    'id_компании': company.get('ID', '')
                }

                letters.append(letter)
                logger.info(f"Создано КП для {company_name}")

            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON для {company_name}: {e}")
                errors += 1
                continue
            except Exception as e:
                logger.error(f"Ошибка при генерации письма для {company_name}: {e}")
                errors += 1
                continue

        # Сохраняем письма
        if letters:
            success = self.sheets.add_letters(letters)
            return {
                "success": success,
                "count": len(letters),
                "errors": errors,
                "message": f"✅ Создано {len(letters)} персонализированных коммерческих предложений\n\n📧 Все КП сохранены в Google Sheets (лист ПИСЬМА)\n{f'⚠️ Ошибок при генерации: {errors}' if errors > 0 else ''}\n\n🎉 Готово! Письма можно отправлять клиентам."
            }

        return {"success": False, "message": f"Не удалось создать письма. Ошибок: {errors}"}

    def process_message(self, user_message: str) -> str:
        """
        Обработать сообщение пользователя

        Args:
            user_message: Сообщение от пользователя

        Returns:
            Ответ агента
        """
        logger.info(f"Получено сообщение: {user_message}")

        # Добавляем сообщение в историю
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            # Вызываем Claude с инструментами
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                system=self.system_prompt,
                tools=self._get_tools_definition(),
                messages=self.conversation_history
            )

            # Обрабатываем ответ
            assistant_message = ""
            tool_results = []

            while response.stop_reason == "tool_use":
                # Извлекаем вызовы инструментов
                for content_block in response.content:
                    if content_block.type == "text":
                        assistant_message += content_block.text

                    elif content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_use_id = content_block.id

                        # Выполняем инструмент
                        result = self._execute_tool(tool_name, tool_input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": str(result)
                        })

                # Добавляем результаты в историю
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })

                # Продолжаем диалог
                response = self.client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=CLAUDE_MAX_TOKENS,
                    system=self.system_prompt,
                    tools=self._get_tools_definition(),
                    messages=self.conversation_history
                )

                tool_results = []

            # Финальный ответ
            for content_block in response.content:
                if content_block.type == "text":
                    assistant_message += content_block.text

            # Добавляем ответ в историю
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            logger.info(f"Ответ агента: {assistant_message}")
            return assistant_message

        except Exception as e:
            error_msg = f"Ошибка при обработке сообщения: {e}"
            logger.error(error_msg)
            return error_msg

    def run_interactive(self):
        """Запуск агента в интерактивном режиме"""
        print("=" * 60)
        print("🤖 ИНТЕЛЛЕКТУАЛЬНЫЙ АГЕНТ ДЛЯ СБОРА ЛИДОВ")
        print("=" * 60)
        print("\nАгент готов к работе!")
        print("Введите 'выход' или 'exit' для завершения\n")

        while True:
            try:
                user_input = input("👤 Вы: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['выход', 'exit', 'quit']:
                    print("\n👋 До свидания!")
                    break

                response = self.process_message(user_input)
                print(f"\n🤖 Агент: {response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Работа прервана пользователем")
                break
            except Exception as e:
                logger.error(f"Ошибка в интерактивном режиме: {e}")
                print(f"\n❌ Ошибка: {e}\n")


def main():
    """Главная функция запуска агента"""
    try:
        agent = LeadCollectionAgent()
        agent.run_interactive()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
