"""Модуль для работы с Google Sheets"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from config.settings import GOOGLE_SHEETS_ID, GOOGLE_CREDENTIALS_FILE, SHEET_NAMES, TIMEZONE
import pytz

logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """Менеджер для работы с Google Sheets"""

    def __init__(self):
        """Инициализация подключения к Google Sheets"""
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = None
        self.spreadsheet = None
        self._connect()

    def _connect(self):
        """Подключение к Google Sheets"""
        try:
            creds = Credentials.from_service_account_file(
                GOOGLE_CREDENTIALS_FILE,
                scopes=self.scopes
            )
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(GOOGLE_SHEETS_ID)
            logger.info(f"Успешно подключено к таблице {GOOGLE_SHEETS_ID}")
        except Exception as e:
            logger.error(f"Ошибка подключения к Google Sheets: {e}")
            raise

    def get_worksheet(self, sheet_name: str):
        """Получить лист по имени"""
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            logger.warning(f"Лист {sheet_name} не найден, создаём новый")
            return self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)

    def add_queries(self, queries: List[Dict[str, Any]]) -> bool:
        """
        Добавить запросы в лист ЗАПРОСЫ

        Args:
            queries: Список запросов с полями: тема, город, запрос, статус

        Returns:
            True если успешно
        """
        try:
            worksheet = self.get_worksheet(SHEET_NAMES['queries'])

            # Проверяем есть ли заголовки
            if worksheet.row_count == 0 or not worksheet.row_values(1):
                headers = ['ID', 'Дата создания', 'Тема', 'Город', 'Запрос', 'Статус', 'Дата обработки']
                worksheet.append_row(headers)

            # Получаем текущее количество строк
            all_values = worksheet.get_all_values()
            next_id = len(all_values)  # ID начинается с 1 (заголовок) + новые строки

            # Подготавливаем данные для добавления
            tz = pytz.timezone(TIMEZONE)
            now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

            rows = []
            for query in queries:
                row = [
                    next_id,
                    now,
                    query.get('тема', ''),
                    query.get('город', ''),
                    query.get('запрос', ''),
                    query.get('статус', 0),
                    ''  # Дата обработки пока пустая
                ]
                rows.append(row)
                next_id += 1

            # Добавляем все строки разом
            worksheet.append_rows(rows)
            logger.info(f"Добавлено {len(rows)} запросов в Google Sheets")
            return True

        except Exception as e:
            logger.error(f"Ошибка при добавлении запросов: {e}")
            return False

    def get_queries_with_status(self, status: int = 0) -> List[Dict[str, Any]]:
        """
        Получить запросы с определённым статусом

        Args:
            status: Статус запросов (0 = не обработан, 1 = обработан)

        Returns:
            Список словарей с данными запросов
        """
        try:
            worksheet = self.get_worksheet(SHEET_NAMES['queries'])
            all_records = worksheet.get_all_records()

            # Фильтруем по статусу
            filtered = [r for r in all_records if int(r.get('Статус', -1)) == status]
            logger.info(f"Найдено {len(filtered)} запросов со статусом {status}")
            return filtered

        except Exception as e:
            logger.error(f"Ошибка при получении запросов: {e}")
            return []

    def add_sites(self, sites: List[Dict[str, Any]]) -> bool:
        """
        Добавить сайты компаний в лист САЙТЫ

        Args:
            sites: Список сайтов с данными компаний

        Returns:
            True если успешно
        """
        try:
            worksheet = self.get_worksheet(SHEET_NAMES['sites'])

            # Проверяем заголовки
            if worksheet.row_count == 0 or not worksheet.row_values(1):
                headers = ['ID', 'Дата добавления', 'Название компании', 'Сайт', 'Телефон',
                          'Адрес', 'Город', 'Категория', 'Статус сбора данных', 'ID запроса']
                worksheet.append_row(headers)

            all_values = worksheet.get_all_values()
            next_id = len(all_values)

            tz = pytz.timezone(TIMEZONE)
            now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

            rows = []
            for site in sites:
                row = [
                    next_id,
                    now,
                    site.get('название', ''),
                    site.get('сайт', ''),
                    site.get('телефон', ''),
                    site.get('адрес', ''),
                    site.get('город', ''),
                    site.get('категория', ''),
                    site.get('статус', 0),
                    site.get('id_запроса', '')
                ]
                rows.append(row)
                next_id += 1

            worksheet.append_rows(rows)
            logger.info(f"Добавлено {len(rows)} сайтов в Google Sheets")
            return True

        except Exception as e:
            logger.error(f"Ошибка при добавлении сайтов: {e}")
            return False

    def get_sites_with_status(self, status: int = 0) -> List[Dict[str, Any]]:
        """Получить сайты с определённым статусом сбора данных"""
        try:
            worksheet = self.get_worksheet(SHEET_NAMES['sites'])
            all_records = worksheet.get_all_records()

            filtered = [r for r in all_records if int(r.get('Статус сбора данных', -1)) == status]
            logger.info(f"Найдено {len(filtered)} сайтов со статусом {status}")
            return filtered

        except Exception as e:
            logger.error(f"Ошибка при получении сайтов: {e}")
            return []

    def add_companies(self, companies: List[Dict[str, Any]]) -> bool:
        """
        Добавить информацию о компаниях в лист КОМПАНИИ

        Args:
            companies: Список компаний с собранными данными

        Returns:
            True если успешно
        """
        try:
            worksheet = self.get_worksheet(SHEET_NAMES['companies'])

            if worksheet.row_count == 0 or not worksheet.row_values(1):
                headers = ['ID', 'Дата сбора', 'Название компании', 'Сайт', 'Email',
                          'Телефон', 'Адрес', 'Описание', 'Услуги', 'Контактное лицо',
                          'Соц. сети', 'ID сайта']
                worksheet.append_row(headers)

            all_values = worksheet.get_all_values()
            next_id = len(all_values)

            tz = pytz.timezone(TIMEZONE)
            now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

            rows = []
            for company in companies:
                row = [
                    next_id,
                    now,
                    company.get('название', ''),
                    company.get('сайт', ''),
                    company.get('email', ''),
                    company.get('телефон', ''),
                    company.get('адрес', ''),
                    company.get('описание', ''),
                    company.get('услуги', ''),
                    company.get('контактное_лицо', ''),
                    company.get('соцсети', ''),
                    company.get('id_сайта', '')
                ]
                rows.append(row)
                next_id += 1

            worksheet.append_rows(rows)
            logger.info(f"Добавлено {len(rows)} компаний в Google Sheets")
            return True

        except Exception as e:
            logger.error(f"Ошибка при добавлении компаний: {e}")
            return False

    def add_letters(self, letters: List[Dict[str, Any]]) -> bool:
        """
        Добавить черновики писем в лист ПИСЬМА

        Args:
            letters: Список писем с данными

        Returns:
            True если успешно
        """
        try:
            worksheet = self.get_worksheet(SHEET_NAMES['letters'])

            if worksheet.row_count == 0 or not worksheet.row_values(1):
                headers = ['ID', 'Дата создания', 'Название компании', 'Email',
                          'Тема письма', 'Текст письма', 'Статус отправки', 'ID компании']
                worksheet.append_row(headers)

            all_values = worksheet.get_all_values()
            next_id = len(all_values)

            tz = pytz.timezone(TIMEZONE)
            now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

            rows = []
            for letter in letters:
                row = [
                    next_id,
                    now,
                    letter.get('название', ''),
                    letter.get('email', ''),
                    letter.get('тема', ''),
                    letter.get('текст', ''),
                    letter.get('статус', 0),
                    letter.get('id_компании', '')
                ]
                rows.append(row)
                next_id += 1

            worksheet.append_rows(rows)
            logger.info(f"Добавлено {len(rows)} писем в Google Sheets")
            return True

        except Exception as e:
            logger.error(f"Ошибка при добавлении писем: {e}")
            return False

    def update_query_status(self, query_id: int, status: int = 1):
        """Обновить статус запроса"""
        try:
            worksheet = self.get_worksheet(SHEET_NAMES['queries'])
            cell = worksheet.find(str(query_id))
            if cell:
                tz = pytz.timezone(TIMEZONE)
                now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
                worksheet.update_cell(cell.row, 6, status)  # Колонка Статус
                worksheet.update_cell(cell.row, 7, now)     # Колонка Дата обработки
                logger.info(f"Обновлён статус запроса {query_id} на {status}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса запроса: {e}")

    def update_site_status(self, site_id: int, status: int = 1):
        """Обновить статус сбора данных по сайту"""
        try:
            worksheet = self.get_worksheet(SHEET_NAMES['sites'])
            cell = worksheet.find(str(site_id))
            if cell:
                worksheet.update_cell(cell.row, 9, status)  # Колонка Статус сбора данных
                logger.info(f"Обновлён статус сайта {site_id} на {status}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса сайта: {e}")
