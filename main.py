import asyncio
import configparser
import datetime
import re
import time

from aiogram import Bot
from telethon import TelegramClient

config = configparser.ConfigParser()
config.read('bot.config')


async def get_recent_message(api_id, api_hash, chats, regex):
    for chat in chats:
        async with TelegramClient('test', api_id, api_hash) as client:
            current_time = int(time.time())
            seconds_from_now_search_messages = int(config.get('Timing', 'SECONDS_FROM_NOW_SEARCH_MESSAGES'))
            seconds_ago = current_time - seconds_from_now_search_messages
            async for message in client.iter_messages(chat, offset_date=seconds_ago, reverse=True):
                if re.search(regex, message.text, re.MULTILINE | re.IGNORECASE):
                    return message.text
    return False


async def broadcast_message(bot, channel_id, text):
    await bot.send_message(channel_id, text)


async def wait_until(bot, wait_seconds):
    regex = config.get('Bot', 'REGEX')
    api_id = config.get('Telethon', 'API_ID')
    api_hash = config.get('Telethon', 'API_HASH')
    source_chats = config.get('Source', 'CHATS').split(',')
    destination_chat = config.get('Destination', 'CHAT')
    while True:
        coro_message = get_recent_message(api_id, api_hash, source_chats, regex)
        message = await coro_message
        if message:
            coro = broadcast_message(bot, destination_chat, message)
            await coro
        print(datetime.datetime.now())
        await asyncio.sleep(wait_seconds)


def main():
    bot_id = config.get('Bot', 'BOT_ID')
    seconds_between_requests = int(config.get('Timing', 'SECONDS_BETWEEN_REQUESTS'))
    bot = Bot(bot_id)
    loop = asyncio.get_event_loop()
    task = loop.create_task(wait_until(bot, seconds_between_requests))

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass


if __name__ == '__main__':
    main()
