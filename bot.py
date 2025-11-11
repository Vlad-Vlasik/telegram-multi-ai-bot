import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv
import os

from handlers import router

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)


async def set_commands():
    commands = [
        BotCommand(command="start", description="Почати роботу"),
        BotCommand(command="help", description="Отримати допомогу"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await set_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())