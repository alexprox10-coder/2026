#!/usr/bin/env python3
"""
Telegram бот управления агентом прогрева

Кнопки:
- Прогреть лиды (5/10/20)
- Статистика
- Активные диалоги
- Стоп

Требования:
pip install aiogram python-dotenv
"""

import os
import asyncio
import logging
from datetime import datetime

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from lead_warmup_agent import WarmupAgent

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация
BOT_TOKEN = os.getenv('WARMUP_BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', 0))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Глобальный агент
agent: WarmupAgent = None
agent_task = None


def is_admin(user_id: int) -> bool:
    """Проверка админа"""
    return user_id == ADMIN_CHAT_ID


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥 Прогреть 5", callback_data="warmup_5"),
            InlineKeyboardButton(text="🔥 Прогреть 10", callback_data="warmup_10"),
        ],
        [
            InlineKeyboardButton(text="🔥 Прогреть 20", callback_data="warmup_20"),
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
            InlineKeyboardButton(text="💬 Диалоги", callback_data="dialogs"),
        ],
        [
            InlineKeyboardButton(text="🔄 Обновить лиды", callback_data="refresh"),
            InlineKeyboardButton(text="⏹ Стоп", callback_data="stop"),
        ]
    ])


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён")
        return

    await message.answer(
        "🤖 <b>Агент прогрева лидов</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help"""
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "📋 <b>Команды:</b>\n\n"
        "/start - Главное меню\n"
        "/stats - Статистика\n"
        "/warmup N - Прогреть N лидов\n"
        "/stop - Остановить агента\n\n"
        "<b>Как работает:</b>\n"
        "1. Агент берёт лиды из Google Sheets\n"
        "2. Пишет им по username через Telethon\n"
        "3. AI ведёт диалог, квалифицирует\n"
        "4. Результат: qualified / refused\n\n"
        "⚠️ Лимит: 20 сообщений в день",
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("warmup_"))
async def warmup_callback(callback: CallbackQuery):
    """Обработка кнопки прогрева"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещён")
        return

    global agent, agent_task

    count = int(callback.data.split("_")[1])

    await callback.message.edit_text(
        f"⏳ Запускаю прогрев {count} лидов...\n"
        "Это может занять несколько минут.",
        reply_markup=None
    )

    try:
        # Инициализируем агента если нужно
        if agent is None:
            agent = WarmupAgent()
            if not await agent.start():
                await callback.message.edit_text(
                    "❌ Ошибка запуска агента!\n"
                    "Проверь настройки Google Sheets и Telegram API",
                    reply_markup=get_main_keyboard()
                )
                return

        # Запускаем прогрев
        results = await agent.warmup_leads(limit=count)

        # Формируем отчёт
        status_emoji = "✅" if results['status'] == 'ok' else "⚠️"
        report = (
            f"{status_emoji} <b>Прогрев завершён</b>\n\n"
            f"📤 Отправлено: {results.get('sent', 0)}\n"
            f"❌ Ошибок: {results.get('failed', 0)}\n"
        )

        if results.get('details'):
            report += "\n<b>Детали:</b>\n"
            for d in results['details'][:10]:
                icon = "✅" if d['success'] else "❌"
                report += f"{icon} {d['username']}\n"

        if results['status'] == 'limit_reached':
            report += "\n⚠️ Достигнут дневной лимит!"
        elif results['status'] == 'no_leads':
            report += "\n📭 Нет новых лидов для прогрева"

        await callback.message.edit_text(
            report,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )

        # Запускаем прослушку ответов в фоне
        if agent_task is None or agent_task.done():
            agent_task = asyncio.create_task(listen_responses())

    except Exception as e:
        logger.error(f"Ошибка прогрева: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка: {e}",
            reply_markup=get_main_keyboard()
        )


@router.callback_query(F.data == "stats")
async def stats_callback(callback: CallbackQuery):
    """Статистика"""
    if not is_admin(callback.from_user.id):
        return

    global agent

    if agent is None:
        await callback.message.edit_text(
            "📊 <b>Статистика</b>\n\n"
            "Агент не запущен.\n"
            "Нажмите 'Прогреть' для запуска.",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        return

    stats = agent.get_stats()

    await callback.message.edit_text(
        f"📊 <b>Статистика</b>\n\n"
        f"📤 Отправлено сегодня: {stats['messages_sent_today']}/{stats['daily_limit']}\n"
        f"💬 Активных диалогов: {stats['active_conversations']}\n"
        f"📅 Сброс счётчика: {stats['last_reset']}\n",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "dialogs")
async def dialogs_callback(callback: CallbackQuery):
    """Активные диалоги"""
    if not is_admin(callback.from_user.id):
        return

    global agent

    if agent is None or not agent.conversations:
        await callback.message.edit_text(
            "💬 <b>Активные диалоги</b>\n\n"
            "Нет активных диалогов",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        return

    text = "💬 <b>Активные диалоги</b>\n\n"

    for chat_id, ctx in list(agent.conversations.items())[:10]:
        username = ctx['lead'].get('username', 'unknown')
        messages = len(ctx['history'])
        collected = sum(1 for v in ctx['collected_data'].values() if v)

        text += f"• {username}\n"
        text += f"  Сообщений: {messages}, Собрано полей: {collected}\n"

    await callback.message.edit_text(
        text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "refresh")
async def refresh_callback(callback: CallbackQuery):
    """Обновить список лидов"""
    if not is_admin(callback.from_user.id):
        return

    global agent

    if agent is None:
        agent = WarmupAgent()
        await agent.start()

    leads = agent.sheets.get_new_leads(limit=100)

    await callback.message.edit_text(
        f"🔄 <b>Доступные лиды</b>\n\n"
        f"Найдено: {len(leads)} лидов с username\n"
        f"(статус new или пустой, не реклама)\n\n"
        f"Нажмите 'Прогреть' для запуска",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "stop")
async def stop_callback(callback: CallbackQuery):
    """Остановка агента"""
    if not is_admin(callback.from_user.id):
        return

    global agent, agent_task

    if agent:
        await agent.stop()
        agent = None

    if agent_task and not agent_task.done():
        agent_task.cancel()
        agent_task = None

    await callback.message.edit_text(
        "⏹ <b>Агент остановлен</b>\n\n"
        "Для возобновления нажмите 'Прогреть'",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


async def listen_responses():
    """Слушаем ответы от лидов"""
    global agent
    if agent and agent.client:
        try:
            await agent.client.run_until_disconnected()
        except asyncio.CancelledError:
            pass


async def notify_admin(text: str):
    """Отправить уведомление админу"""
    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="HTML")
        except:
            pass


async def on_startup():
    """Действия при запуске"""
    logger.info("Бот запущен")
    await notify_admin("🤖 Бот прогрева запущен")


async def on_shutdown():
    """Действия при остановке"""
    global agent
    if agent:
        await agent.stop()
    logger.info("Бот остановлен")


async def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        print("❌ Установите WARMUP_BOT_TOKEN в .env")
        return

    if not ADMIN_CHAT_ID:
        print("❌ Установите ADMIN_CHAT_ID в .env")
        return

    dp.include_router(router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    print("🤖 Бот прогрева запущен...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
