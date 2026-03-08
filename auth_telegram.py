#!/usr/bin/env python3
"""Скрипт авторизации в Telegram"""
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')

async def main():
    client = TelegramClient('telegram_session', API_ID, API_HASH)
    await client.start(phone=PHONE)

    me = await client.get_me()
    print(f"Авторизация успешна! Привет, {me.first_name}")
    print(f"Username: @{me.username}")
    print(f"ID: {me.id}")

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
