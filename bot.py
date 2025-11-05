# bot.py — 100% СТАБІЛЬНА ВЕРСІЯ (Railway, 05.11.2025)
import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не знайдено!")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class AIChoice(StatesGroup):
    waiting_query = State()

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Grok", callback_data="ai_grok")],
        [InlineKeyboardButton(text="ChatGPT", callback_data="ai_chatgpt")],
        [InlineKeyboardButton(text="Gemini", callback_data="ai_gemini")],
        [InlineKeyboardButton(text="Perplexity", callback_data="ai_perplexity")],
    ])

def get_response_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Інший AI", callback_data="redirect_main")],
        [InlineKeyboardButton(text="Копіювати", callback_data="copy_response")],
        [InlineKeyboardButton(text="Меню", callback_data="back_main")]
    ])

# === Клієнти ===
client_openai = client_xai = gemini_model = perplexity_client = None

def init_clients():
    global client_openai, client_xai, gemini_model, perplexity_client

    # OpenAI — БЕЗ ПРОКСІ
    if key := os.getenv('OPENAI_API_KEY'):
        try:
            import openai
            import httpx
            client_openai = openai.OpenAI(
                api_key=key,
                http_client=httpx.Client(proxies=None)  # ВИПРАВЛЕНО!
            )
            logging.info("OpenAI: OK")
        except Exception as e:
            logging.error(f"OpenAI: {e}")
    else:
        logging.warning("OPENAI_API_KEY відсутній")

    # Grok — БЕЗ ПРОКСІ
    if key := os.getenv('XAI_API_KEY'):
        try:
            from openai import OpenAI
            import httpx
            client_xai = OpenAI(
                base_url="https://api.x.ai/v1",
                api_key=key,
                http_client=httpx.Client(proxies=None)  # ВИПРАВЛЕНО!
            )
            logging.info("Grok: OK")
        except Exception as e:
            logging.error(f"Grok: {e}")
    else:
        logging.warning("XAI_API_KEY відсутній")

    # Gemini
    if key := os.getenv('GEMINI_API_KEY'):
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logging.info("Gemini: OK")
        except Exception as e:
            logging.error(f"Gemini: {e}")
    else:
        logging.warning("GEMINI_API_KEY відсутній")

    # Perplexity
    if key := os.getenv('PERPLEXITY_API_KEY'):
        try:
            from perplexity import Perplexity
            import httpx
            perplexity_client = Perplexity(
                api_key=key,
                client=httpx.Client(proxies=None)  # ВИПРАВЛЕНО!
            )
            logging.info("Perplexity: OK")
        except Exception as e:
            logging.error(f"Perplexity: {e}")
    else:
        logging.warning("PERPLEXITY_API_KEY відсутній")

# === Запит ===
async def query_ai(ai_type: str, query: str) -> str:
    try:
        if ai_type == "chatgpt" and client_openai:
            resp = await asyncio.to_thread(
                client_openai.chat.completions.create,
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": query}]
            )
            return resp.choices[0].message.content

        elif ai_type == "grok" and client_xai:
            resp = await asyncio.to_thread(
                client_xai.chat.completions.create,
                model="grok-beta",
                messages=[{"role": "user", "content": query}]
            )
            return resp.choices[0].message.content

        elif ai_type == "gemini" and gemini_model:
            resp = await asyncio.to_thread(gemini_model.generate_content, query)
            return resp.text

        elif ai_type == "perplexity" and perplexity_client:
            resp = await asyncio.to_thread(
                perplexity_client.chat.completions.create,
                model="llama-3.1-sonar-small-128k-online",
                messages=[{"role": "user", "content": query}]
            )
            return resp.choices[0].message.content

        else:
            return f"{ai_type} недоступний"
    except Exception as e:
        return f"Помилка: {e}"

# === Хендлери ===
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer("Обери AI:", reply_markup=get_main_keyboard())
    await state.set_state(AIChoice.waiting_query)

@dp.message(F.text, AIChoice.waiting_query)
async def handle(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ai = data.get("current_ai")
    if not ai:
        await message.answer("Обери AI!")
        return
    thinking = await message.answer("Думаю...")
    resp = await query_ai(ai, message.text)
    await thinking.edit_text(f"**{ai.upper()}**\n\n{resp}", reply_markup=get_response_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("ai_"))
async def select_ai(cb: types.CallbackQuery, state: FSMContext):
    ai = cb.data.split("_")[1]
    await state.update_data(current_ai=ai)
    await cb.message.edit_text(f"**{ai.upper()}** вибрано!\nНапиши:", parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(F.data == "back_main")
async def back(cb: types.CallbackQuery):
    await cb.message.edit_text("Обери AI:", reply_markup=get_main_keyboard())
    await cb.answer()

@dp.callback_query(F.data == "redirect_main")
async def redirect(cb: types.CallbackQuery):
    await cb.message.edit_text("Обери інший AI:", reply_markup=get_main_keyboard())
    await cb.answer()

@dp.callback_query(F.data == "copy_response")
async def copy(cb: types.CallbackQuery):
    text = cb.message.text or ""
    await cb.message.reply(f"```markdown\n{text}\n```", parse_mode="Markdown")
    await cb.answer("Скопійовано!")

# === Запуск ===
async def main():
    init_clients()
    logging.info("Бот запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
