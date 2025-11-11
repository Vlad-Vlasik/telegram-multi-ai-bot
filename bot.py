import asyncio
import logging
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram import F
from config import TELEGRAM_TOKEN
from clients import init_clients
from handlers import (
    start,
    handle,
    select_ai,
    back,
    redirect,
    copy
)

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Диспетчер
dp = Dispatcher()

# Реєстрація хендлерів
dp.message.register(start, CommandStart())
dp.message.register(handle, F.text)
dp.callback_query.register(select_ai, F.data.startswith("ai_"))
dp.callback_query.register(back, F.data == "back_main")
dp.callback_query.register(redirect, F.data == "redirect_main")
dp.callback_query.register(copy, F.data == "copy_response")

async def main():
    init_clients()
    logging.info("Бот запущено!")
    bot = Bot(token=TELEGRAM_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
