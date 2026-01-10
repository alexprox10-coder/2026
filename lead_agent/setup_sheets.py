#!/usr/bin/env python3
"""
Скрипт для автоматической настройки структуры Google Sheets
Создаёт необходимые листы и заголовки
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from modules.google_sheets import GoogleSheetsManager
from config.settings import SHEET_NAMES
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def setup_sheets():
    """Настроить структуру Google Sheets"""
    try:
        print("🔧 Настройка структуры Google Sheets...")
        print("=" * 60)

        sheets_manager = GoogleSheetsManager()

        # Создаём или проверяем лист ЗАПРОСЫ
        print("\n📋 Настройка листа ЗАПРОСЫ...")
        queries_sheet = sheets_manager.get_worksheet(SHEET_NAMES['queries'])
        if not queries_sheet.row_values(1):
            headers = ['ID', 'Дата создания', 'Тема', 'Город', 'Запрос', 'Статус', 'Дата обработки']
            queries_sheet.append_row(headers)
            # Форматирование заголовков
            queries_sheet.format('A1:G1', {
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                "horizontalAlignment": "CENTER"
            })
            print("✅ Лист ЗАПРОСЫ создан и настроен")
        else:
            print("✅ Лист ЗАПРОСЫ уже существует")

        # Создаём или проверяем лист САЙТЫ
        print("\n🌐 Настройка листа САЙТЫ...")
        sites_sheet = sheets_manager.get_worksheet(SHEET_NAMES['sites'])
        if not sites_sheet.row_values(1):
            headers = ['ID', 'Дата добавления', 'Название компании', 'Сайт', 'Телефон',
                      'Адрес', 'Город', 'Категория', 'Статус сбора данных', 'ID запроса']
            sites_sheet.append_row(headers)
            sites_sheet.format('A1:J1', {
                "backgroundColor": {"red": 0.2, "green": 0.8, "blue": 0.6},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                "horizontalAlignment": "CENTER"
            })
            print("✅ Лист САЙТЫ создан и настроен")
        else:
            print("✅ Лист САЙТЫ уже существует")

        # Создаём или проверяем лист КОМПАНИИ
        print("\n🏢 Настройка листа КОМПАНИИ...")
        companies_sheet = sheets_manager.get_worksheet(SHEET_NAMES['companies'])
        if not companies_sheet.row_values(1):
            headers = ['ID', 'Дата сбора', 'Название компании', 'Сайт', 'Email',
                      'Телефон', 'Адрес', 'Описание', 'Услуги', 'Контактное лицо',
                      'Соц. сети', 'ID сайта']
            companies_sheet.append_row(headers)
            companies_sheet.format('A1:L1', {
                "backgroundColor": {"red": 0.9, "green": 0.5, "blue": 0.2},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                "horizontalAlignment": "CENTER"
            })
            print("✅ Лист КОМПАНИИ создан и настроен")
        else:
            print("✅ Лист КОМПАНИИ уже существует")

        # Создаём или проверяем лист ПИСЬМА
        print("\n✉️ Настройка листа ПИСЬМА...")
        letters_sheet = sheets_manager.get_worksheet(SHEET_NAMES['letters'])
        if not letters_sheet.row_values(1):
            headers = ['ID', 'Дата создания', 'Название компании', 'Email',
                      'Тема письма', 'Текст письма', 'Статус отправки', 'ID компании']
            letters_sheet.append_row(headers)
            letters_sheet.format('A1:H1', {
                "backgroundColor": {"red": 0.7, "green": 0.2, "blue": 0.9},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                "horizontalAlignment": "CENTER"
            })
            print("✅ Лист ПИСЬМА создан и настроен")
        else:
            print("✅ Лист ПИСЬМА уже существует")

        print("\n" + "=" * 60)
        print("✅ Настройка Google Sheets завершена успешно!")
        print("\n📊 Проверьте вашу таблицу:")
        print(f"https://docs.google.com/spreadsheets/d/{sheets_manager.spreadsheet.id}")

    except Exception as e:
        logger.error(f"❌ Ошибка при настройке: {e}")
        print("\n❌ Настройка не удалась. Проверьте:")
        print("1. Правильность google_credentials.json")
        print("2. Доступ service account к таблице")
        print("3. Правильность GOOGLE_SHEETS_ID в .env")
        sys.exit(1)


if __name__ == "__main__":
    setup_sheets()
