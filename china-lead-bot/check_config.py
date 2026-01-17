#!/usr/bin/env python3
"""
Configuration Checker for ChinaLeadBot
Проверяет что все настройки заполнены правильно
"""

import os
import sys
from dotenv import load_dotenv
import requests

# Load .env
load_dotenv()

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header():
    print(f"\n{BLUE}{BOLD}{'='*60}")
    print(f"  ChinaLeadBot - Configuration Check")
    print(f"{'='*60}{RESET}\n")

def check_env_var(var_name, required=True, check_placeholder=True):
    """Check if environment variable is set correctly"""
    value = os.getenv(var_name)

    if not value:
        if required:
            print(f"{RED}✗{RESET} {var_name}: {RED}НЕ ЗАДАН (ОБЯЗАТЕЛЬНО!){RESET}")
            return False
        else:
            print(f"{YELLOW}○{RESET} {var_name}: Не задан (опционально)")
            return True

    # Check for placeholder values
    placeholder_keywords = ['ЗАМЕНИТЕ', 'your_', 'YOUR_', 'REPLACE', 'example', 'localhost:5678']

    if check_placeholder and any(keyword in value for keyword in placeholder_keywords):
        if required:
            print(f"{RED}✗{RESET} {var_name}: {RED}НЕ ИЗМЕНЁН (используется placeholder){RESET}")
            print(f"  → Текущее значение: {YELLOW}{value[:50]}...{RESET}")
            return False
        else:
            print(f"{YELLOW}○{RESET} {var_name}: Placeholder (опционально)")
            return True

    # Value is set and not a placeholder
    masked_value = value[:20] + '...' if len(value) > 20 else value
    print(f"{GREEN}✓{RESET} {var_name}: {GREEN}Настроен{RESET}")
    print(f"  → {masked_value}")
    return True

def check_telegram_token(token):
    """Validate Telegram Bot Token format"""
    if not token or 'ЗАМЕНИТЕ' in token:
        return False

    # Telegram token format: 123456:ABC-DEF...
    parts = token.split(':')
    if len(parts) != 2:
        print(f"{RED}  ⚠ Неправильный формат токена! Должен быть: 123456:ABC-DEF...{RESET}")
        return False

    if not parts[0].isdigit():
        print(f"{RED}  ⚠ Первая часть токена должна быть числом!{RESET}")
        return False

    print(f"{GREEN}  ✓ Формат токена корректный{RESET}")
    return True

def check_webhook_url(url):
    """Validate and test n8n webhook URL"""
    if not url or 'ЗАМЕНИТЕ' in url:
        return False

    # Check URL format
    if not (url.startswith('http://') or url.startswith('https://')):
        print(f"{RED}  ⚠ URL должен начинаться с http:// или https://{RESET}")
        return False

    print(f"{GREEN}  ✓ Формат URL корректный{RESET}")

    # Try to ping webhook
    print(f"{BLUE}  → Проверяю доступность webhook...{RESET}")
    try:
        response = requests.post(
            url,
            json={'test': True, 'user_id': 0, 'category': 'test'},
            timeout=10
        )

        if response.status_code == 200:
            print(f"{GREEN}  ✓ Webhook доступен и отвечает!{RESET}")
            return True
        else:
            print(f"{YELLOW}  ○ Webhook доступен (код: {response.status_code}){RESET}")
            print(f"{YELLOW}  → Убедитесь что workflow активирован в n8n{RESET}")
            return True

    except requests.exceptions.Timeout:
        print(f"{YELLOW}  ○ Webhook не отвечает (timeout){RESET}")
        print(f"{YELLOW}  → Проверьте что n8n запущен и workflow активен{RESET}")
        return True

    except requests.exceptions.ConnectionError:
        print(f"{RED}  ✗ Не удается подключиться к webhook{RESET}")
        print(f"{RED}  → Проверьте URL и доступность n8n{RESET}")
        return False

    except Exception as e:
        print(f"{YELLOW}  ○ Ошибка при проверке: {e}{RESET}")
        return True

def main():
    print_header()

    all_ok = True

    # Required settings
    print(f"{BOLD}ОБЯЗАТЕЛЬНЫЕ НАСТРОЙКИ:{RESET}\n")

    telegram_ok = check_env_var('TELEGRAM_BOT_TOKEN', required=True)
    if telegram_ok:
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_ok = check_telegram_token(token)
    all_ok = all_ok and telegram_ok

    print()
    webhook_ok = check_env_var('N8N_WEBHOOK_URL', required=True)
    if webhook_ok:
        url = os.getenv('N8N_WEBHOOK_URL')
        webhook_ok = check_webhook_url(url)
    all_ok = all_ok and webhook_ok

    # Optional settings
    print(f"\n{BOLD}ОПЦИОНАЛЬНЫЕ НАСТРОЙКИ:{RESET}\n")

    check_env_var('ANTHROPIC_API_KEY', required=False, check_placeholder=False)
    print(f"  {YELLOW}→ Не обязательно - бот работает через n8n + OpenAI{RESET}")

    print()
    check_env_var('GOOGLE_SHEET_ID', required=False, check_placeholder=False)
    print(f"  {YELLOW}→ Не обязательно - если уже настроено в n8n{RESET}")

    # Python dependencies
    print(f"\n{BOLD}ПРОВЕРКА ЗАВИСИМОСТЕЙ:{RESET}\n")

    try:
        import telegram
        print(f"{GREEN}✓{RESET} python-telegram-bot: {GREEN}Установлен{RESET}")
    except ImportError:
        print(f"{RED}✗{RESET} python-telegram-bot: {RED}НЕ УСТАНОВЛЕН{RESET}")
        print(f"{RED}  → Запустите: pip install -r requirements.txt{RESET}")
        all_ok = False

    try:
        import requests
        print(f"{GREEN}✓{RESET} requests: {GREEN}Установлен{RESET}")
    except ImportError:
        print(f"{RED}✗{RESET} requests: {RED}НЕ УСТАНОВЛЕН{RESET}")
        all_ok = False

    try:
        from dotenv import load_dotenv
        print(f"{GREEN}✓{RESET} python-dotenv: {GREEN}Установлен{RESET}")
    except ImportError:
        print(f"{RED}✗{RESET} python-dotenv: {RED}НЕ УСТАНОВЛЕН{RESET}")
        all_ok = False

    # Final result
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")

    if all_ok:
        print(f"{GREEN}{BOLD}✓ ВСЁ ГОТОВО К ЗАПУСКУ!{RESET}\n")
        print(f"{BOLD}Следующие шаги:{RESET}")
        print(f"  1. Запустите бота: {BLUE}python bot/main.py{RESET}")
        print(f"  2. Найдите бота в Telegram")
        print(f"  3. Отправьте /start")
        print(f"  4. Протестируйте поиск\n")
    else:
        print(f"{RED}{BOLD}✗ ТРЕБУЕТСЯ НАСТРОЙКА!{RESET}\n")
        print(f"{BOLD}Что нужно сделать:{RESET}\n")

        if not telegram_ok:
            print(f"{RED}1. TELEGRAM_BOT_TOKEN:{RESET}")
            print(f"   • Откройте @BotFather в Telegram")
            print(f"   • Отправьте /newbot")
            print(f"   • Следуйте инструкциям")
            print(f"   • Скопируйте токен в .env файл\n")

        if not webhook_ok:
            print(f"{RED}2. N8N_WEBHOOK_URL:{RESET}")
            print(f"   • Откройте n8n")
            print(f"   • Импортируйте workflow v3")
            print(f"   • АКТИВИРУЙТЕ workflow (Active)")
            print(f"   • Кликните 'Webhook Trigger'")
            print(f"   • Скопируйте 'Production URL' в .env\n")

        print(f"После настройки запустите снова: {BLUE}python check_config.py{RESET}\n")

    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")

    sys.exit(0 if all_ok else 1)

if __name__ == '__main__':
    main()
