from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🤖 Обрати ChatGPT", callback_data="select_chatgpt")
    kb.button(text="🔮 Обрати Gemini", callback_data="select_gemini")
    kb.adjust(1)
    await message.answer(
        "Вітаю! Я мульти-AI бот. Обери, з ким хочеш спілкуватися 👇",
        reply_markup=kb.as_markup()
    )


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("📘 Команди:\n/start — почати\n/help — допомога")