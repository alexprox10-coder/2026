#!/usr/bin/env python3
"""
ChinaLeadBot - AI Lead Generation Agent
Telegram bot for finding Chinese suppliers for Russian importers
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
import anthropic
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')

# Conversation states
CATEGORY, MOQ, PRICE_RANGE, CONFIRM = range(4)

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# User database (in production use SQLAlchemy/PostgreSQL)
user_db = {}


class UserProfile:
    """User profile with subscription and search preferences"""
    def __init__(self, user_id):
        self.user_id = user_id
        self.subscription = "free"
        self.leads_used = 0
        self.leads_limit = 5
        self.preferences = {}
        self.created_at = datetime.now()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - registration and welcome message"""
    user = update.effective_user
    user_id = user.id

    # Create user profile if new
    if user_id not in user_db:
        user_db[user_id] = UserProfile(user_id)
        logger.info(f"New user registered: {user.username} (ID: {user_id})")

    welcome_message = f"""
🇨🇳🇷🇺 **Добро пожаловать в ChinaLeadBot!**

Привет, {user.first_name}!

Я AI-агент для автоматического поиска китайских поставщиков.

**Что я умею:**
🔍 Поиск поставщиков на Alibaba, 1688.com
🎯 Фильтрация по вашим критериям
💼 Квалификация лидов (проверка рейтинга, отзывов)
📧 Генерация персонализированных запросов
📊 Экспорт результатов в Google Sheets

**Ваш тариф:** {user_db[user_id].subscription.upper()}
**Доступно поисков:** {user_db[user_id].leads_limit - user_db[user_id].leads_used} из {user_db[user_id].leads_limit}

**Основные команды:**
/find - Найти поставщиков
/settings - Настройки поиска
/status - Статус поисков
/subscribe - Управление подпиской
/help - Справка

Начните с команды /find или выберите категорию товара!
"""

    keyboard = [
        [
            InlineKeyboardButton("🔍 Найти поставщиков", callback_data="find"),
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
        ],
        [
            InlineKeyboardButton("💳 Тарифы", callback_data="pricing"),
            InlineKeyboardButton("❓ Помощь", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def find_suppliers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start supplier search conversation"""
    query = update.callback_query
    await query.answer()

    message = """
🔍 **Поиск поставщиков**

Введите категорию товара или описание того, что ищете.

**Примеры:**
- Электроника (смартфоны, наушники)
- Одежда (футболки, джинсы)
- Мебель (столы, стулья)
- Игрушки
- Косметика

Или отправьте конкретный запрос: "Беспроводные наушники TWS с ANC"
"""

    await query.edit_message_text(message, parse_mode='Markdown')
    return CATEGORY


async def process_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process category input and ask for MOQ"""
    user_id = update.effective_user.id
    category = update.message.text

    # Save to context
    context.user_data['category'] = category

    # Use AI to analyze and improve search query
    try:
        ai_response = claude.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Проанализируй запрос пользователя для поиска товаров на Alibaba: "{category}"

Верни ТОЛЬКО JSON:
{{
  "optimized_query": "улучшенный поисковый запрос на английском",
  "category": "категория товара",
  "keywords": ["ключевое слово 1", "ключевое слово 2"],
  "suggestions": ["дополнительный вопрос 1", "дополнительный вопрос 2"]
}}"""
            }]
        )

        ai_analysis = ai_response.content[0].text
        context.user_data['ai_analysis'] = ai_analysis
        logger.info(f"AI analysis: {ai_analysis}")

    except Exception as e:
        logger.error(f"AI analysis error: {e}")

    message = f"""
✅ Категория: **{category}**

Укажите минимальный объем заказа (MOQ):

**Варианты:**
- Любой
- От 100 шт
- От 500 шт
- От 1000 шт
- От 5000 шт

Или введите свое значение: "от 250 шт"
"""

    keyboard = [
        [InlineKeyboardButton("Любой", callback_data="moq_any")],
        [InlineKeyboardButton("От 100 шт", callback_data="moq_100")],
        [InlineKeyboardButton("От 500 шт", callback_data="moq_500")],
        [InlineKeyboardButton("От 1000 шт", callback_data="moq_1000")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    return MOQ


async def process_moq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process MOQ and ask for price range"""
    query = update.callback_query
    await query.answer()

    moq = query.data.replace("moq_", "")
    context.user_data['moq'] = moq

    message = f"""
✅ MOQ: **{moq if moq != 'any' else 'Любой'}**

Укажите ценовой диапазон (за единицу):

**Варианты:**
- Любая цена
- До $1
- $1-$5
- $5-$10
- $10-$50
- Более $50

Или введите свой диапазон: "$2-$7"
"""

    keyboard = [
        [InlineKeyboardButton("Любая", callback_data="price_any")],
        [InlineKeyboardButton("До $1", callback_data="price_0_1")],
        [InlineKeyboardButton("$1-$5", callback_data="price_1_5")],
        [InlineKeyboardButton("$5-$10", callback_data="price_5_10")],
        [InlineKeyboardButton("$10-$50", callback_data="price_10_50")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    return PRICE_RANGE


async def process_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process price range and confirm search"""
    query = update.callback_query
    await query.answer()

    price = query.data.replace("price_", "")
    context.user_data['price_range'] = price

    # Build search summary
    category = context.user_data.get('category', 'N/A')
    moq = context.user_data.get('moq', 'any')

    message = f"""
📋 **Параметры поиска:**

🏷️ Категория: **{category}**
📦 MOQ: **{moq if moq != 'any' else 'Любой'}**
💰 Цена: **{price.replace('_', '-') if price != 'any' else 'Любая'}**

Начинаю поиск? Это займет 1-2 минуты.

**Что я буду делать:**
1. Поиск поставщиков на Alibaba
2. Фильтрация по вашим критериям
3. AI-анализ качества компаний
4. Проверка рейтингов и отзывов
5. Генерация отчета с топ-10 лидов
"""

    keyboard = [
        [
            InlineKeyboardButton("✅ Начать поиск", callback_data="confirm_search"),
            InlineKeyboardButton("❌ Отменить", callback_data="cancel_search")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    return CONFIRM


async def execute_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute search via n8n webhook"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_profile = user_db.get(user_id)

    # Check limits
    if user_profile.leads_used >= user_profile.leads_limit:
        await query.edit_message_text(
            "❌ Вы исчерпали лимит поисков!\n\nОбновите подписку: /subscribe",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

    # Show processing message
    processing_msg = await query.edit_message_text(
        "🔍 **Поиск запущен!**\n\nАнализирую базу поставщиков...\n⏳ Это займет 1-2 минуты.",
        parse_mode='Markdown'
    )

    # Prepare search payload
    search_params = {
        'user_id': user_id,
        'category': context.user_data.get('category'),
        'moq': context.user_data.get('moq'),
        'price_range': context.user_data.get('price_range'),
        'timestamp': datetime.now().isoformat()
    }

    try:
        # Call n8n webhook
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=search_params,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            leads = result.get('leads', [])

            # Update user stats
            user_profile.leads_used += 1

            # Format results
            if leads:
                results_message = f"""
✅ **Поиск завершен!**

Найдено: **{len(leads)} поставщиков**

**ТОП-5 лидов:**

"""
                for i, lead in enumerate(leads[:5], 1):
                    results_message += f"""
{i}. **{lead.get('company_name', 'N/A')}**
   ⭐ Рейтинг: {lead.get('rating', 'N/A')}/5
   📦 MOQ: {lead.get('moq', 'N/A')}
   💰 Цена: ${lead.get('price', 'N/A')}
   🏭 Опыт: {lead.get('years', 'N/A')} лет
   📍 {lead.get('location', 'N/A')}

"""

                results_message += f"\n📊 Полный отчет отправлен в Google Sheets\n"
                results_message += f"📧 Хотите отправить запросы? /outreach"

            else:
                results_message = "❌ По вашим критериям поставщики не найдены. Попробуйте изменить параметры."

            await processing_msg.edit_text(results_message, parse_mode='Markdown')

        else:
            await processing_msg.edit_text(
                f"❌ Ошибка поиска. Попробуйте позже.\nКод: {response.status_code}",
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"Search error: {e}")
        await processing_msg.edit_text(
            "❌ Произошла ошибка при поиске. Наша команда уже работает над решением.",
            parse_mode='Markdown'
        )

    return ConversationHandler.END


async def show_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show subscription pricing"""
    query = update.callback_query
    await query.answer()

    message = """
💳 **Тарифные планы ChinaLeadBot**

**🆓 FREE**
• 5 поисков в месяц
• Базовая фильтрация
• Топ-10 результатов
• Google Sheets экспорт
💰 **БЕСПЛАТНО**

**⭐ BASIC**
• 50 поисков в месяц
• Расширенная фильтрация
• Топ-30 результатов
• AI-анализ компаний
• Email шаблоны
• Приоритетная поддержка
💰 **2,990₽/месяц**

**🚀 PRO**
• 200 поисков в месяц
• Все фильтры
• Безлимитные результаты
• Продвинутый AI-анализ
• Автоматический outreach
• Персональный менеджер
• API доступ
💰 **7,990₽/месяц**

**💎 ENTERPRISE**
• Безлимитные поиски
• Кастомная интеграция
• Dedicated сервер
• White-label решение
• SLA 99.9%
• Персональная настройка
💰 **19,990₽/месяц**

**Дополнительно:**
📌 Квалифицированный лид: 200₽
📌 Теплый лид (с ответом): 500₽
📌 Назначенная встреча: 2,000₽

Оформить подписку: /subscribe
"""

    keyboard = [
        [InlineKeyboardButton("Оформить BASIC", callback_data="buy_basic")],
        [InlineKeyboardButton("Оформить PRO", callback_data="buy_pro")],
        [InlineKeyboardButton("Связаться по ENTERPRISE", callback_data="contact_enterprise")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = """
❓ **Справка ChinaLeadBot**

**Основные команды:**
/start - Начать работу
/find - Найти поставщиков
/settings - Настройки поиска
/status - Статус поисков
/leads - Мои лиды
/subscribe - Управление подпиской
/help - Эта справка

**Как работает поиск:**
1. Укажите категорию товара
2. Выберите MOQ (минимальный заказ)
3. Укажите ценовой диапазон
4. Подтвердите поиск
5. Получите результаты за 1-2 минуты

**Поддержка:**
📧 support@chinaleadbot.ru
💬 @chinaleadbot_support

**Документация:**
🔗 https://docs.chinaleadbot.ru
"""

    await update.message.reply_text(help_text, parse_mode='Markdown')


def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Conversation handler for supplier search
    search_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(find_suppliers, pattern="^find$")],
        states={
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_category)],
            MOQ: [CallbackQueryHandler(process_moq, pattern="^moq_")],
            PRICE_RANGE: [CallbackQueryHandler(process_price, pattern="^price_")],
            CONFIRM: [CallbackQueryHandler(execute_search, pattern="^confirm_search$")],
        },
        fallbacks=[CallbackQueryHandler(start, pattern="^cancel_search$")],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(search_conv_handler)
    application.add_handler(CallbackQueryHandler(show_pricing, pattern="^pricing$"))

    # Start bot
    logger.info("ChinaLeadBot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
