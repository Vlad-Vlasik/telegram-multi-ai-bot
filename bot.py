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

# === Налаштування ===
logging.basicConfig(level=logging.INFO)
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN не знайдено! Додай у Railway Variables")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# === Стани ===
class AIChoice(StatesGroup):
    waiting_query = State()

# === Клавіатури ===
def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Grok (xAI)", callback_data="ai_grok")],
        [InlineKeyboardButton(text="ChatGPT", callback_data="ai_chatgpt")],
        [InlineKeyboardButton(text="Gemini", callback_data="ai_gemini")],
        [InlineKeyboardButton(text="Perplexity", callback_data="ai_perplexity")],
        [InlineKeyboardButton(text="Copilot", callback_data="ai_copilot")],
        [InlineKeyboardButton(text="Програмування", callback_data="cat_programming")],
        [InlineKeyboardButton(text="Навчання", callback_data="cat_learning")],
    ])

def get_programming_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Codeium", callback_data="ai_codeium")],
        [InlineKeyboardButton(text="Codex", callback_data="ai_codex")],
        [InlineKeyboardButton(text="Назад", callback_data="back_main")]
    ])

def get_learning_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Eduaide", callback_data="ai_eduaide")],
        [InlineKeyboardButton(text="Khanmigo", callback_data="ai_khanmigo")],
        [InlineKeyboardButton(text="Назад", callback_data="back_main")]
    ])

def get_response_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Інший AI", callback_data="redirect_main")],
        [InlineKeyboardButton(text="Копіювати", callback_data="copy_response")],
        [InlineKeyboardButton(text="Меню", callback_data="back_main")]
    ])

# === Клієнти AI (без proxies!) ===
client_openai = None
client_xai = None
gemini_model = None
perplexity_client = None

def init_clients():
    global client_openai, client_xai, gemini_model, perplexity_client

    # OpenAI — ТІЛЬКИ api_key
    if os.getenv('OPENAI_API_KEY'):
        try:
            import openai
            client_openai = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            logging.info("OpenAI ініціалізовано")
        except Exception as e:
            logging.error(f"OpenAI помилка: {e}")
    else:
        logging.warning("OPENAI_API_KEY відсутній")

    # Grok (xAI)
    if os.getenv('XAI_API_KEY'):
        try:
            from openai import OpenAI
            client_xai = OpenAI(
                base_url="https://api.x.ai/v1",
                api_key=os.getenv('XAI_API_KEY')
            )
            logging.info("Grok (xAI) ініціалізовано")
        except Exception as e:
            logging.error(f"Grok помилка: {e}")
    else:
        logging.warning("XAI_API_KEY відсутній")

    # Gemini
    if os.getenv('GEMINI_API_KEY'):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logging.info("Gemini ініціалізовано")
        except Exception as e:
            logging.error(f"Gemini помилка: {e}")
    else:
        logging.warning("GEMINI_API_KEY відсутній")

    # Perplexity
    if os.getenv('PERPLEXITY_API_KEY'):
        try:
            from perplexity import Perplexity
            perplexity_client = Perplexity(api_key=os.getenv('PERPLEXITY_API_KEY'))
            logging.info("Perplexity ініціалізовано")
        except Exception as e:
            logging.error(f"Perplexity помилка: {e}")
    else:
        logging.warning("PERPLEXITY_API_KEY відсутній")

# === Запит до AI ===
async def query_ai(ai_type: str, query: str) -> str:
    try:
        if ai_type == "chatgpt" and client_openai:
            resp = await asyncio.to_thread(
                client_openai.chat.completions.create,
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": query}],
                max_tokens=1000
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
            # Fallback
            fallbacks = {
                "copilot": "Copilot: Використовуйте Bing AI для коду.",
                "codeium": "```python\n# Codeium: автодоповнення коду\nprint('Hello')\n```",
                "codex": "```js\n// Codex: генерація коду\nconsole.log('Hi');\n```",
                "eduaide": "Eduaide: персональний репетитор.",
                "khanmigo": "Khanmigo: помічник для навчання."
            }
            return fallbacks.get(ai_type, f"{ai_type} тимчасово недоступний.")
    except Exception as e:
        return f"Помилка {ai_type}: {str(e)}"

# === Хендлери ===
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Multi AI Bot\nОбери модель:",
        reply_markup=get_main_keyboard()
    )
    await state.set_state(AIChoice.waiting_query)

@dp.message(F.text, AIChoice.waiting_query)
async def handle_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ai = data.get("current_ai")
    if not ai:
        await message.answer("Спочатку обери AI з меню!")
        return

    thinking = await message.answer("Думаю...")
    response = await query_ai(ai, message.text)
    await thinking.edit_text(
        f"**{ai.upper()}**\n\n{response}",
        reply_markup=get Rie_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("ai_"))
async def select_ai(callback: CallbackQuery, state: FSMContext):
    ai = callback.data.split("_")[1]
    await state.update_data(current_ai=ai)
    await callback.message.edit_text(
        f"Вибрано: **{ai.upper()}**\n\nНапиши запит:",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("cat_"))
async def select_category(callback: CallbackQuery):
    cat = callback.data.split("_")[1]
    keyboards = {
        "programming": get_programming_keyboard,
        "learning": get_learning_keyboard
    }
    text = "Програмування" if cat == "programming" else "Навчання"
    await callback.message.edit_text(f"{text}", reply_markup=keyboards[cat]())
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("Головне меню:", reply_markup=get_main_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "redirect_main")
async def redirect(callback: CallbackQuery):
    await callback.message.edit_text("Обери інший AI:", reply_markup=get_main_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "copy_response")
async def copy_text(callback: CallbackQuery):
    text = callback.message.text or callback.message.caption or ""
    await callback.message.reply(f"```markdown\n{text}\n```", parse_mode="Markdown")
    await callback.answer("Скопійовано!")

# === Запуск ===
async def main():
    init_clients()
    logging.info("Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
