import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Налаштування логування
logging.basicConfig(level=logging.INFO)
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class AIChoice(StatesGroup):
    waiting_query = State()

# ========== МЕНЮ ==========
def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Grok", callback_data="ai_grok")],
        [InlineKeyboardButton(text="💬 ChatGPT", callback_data="ai_chatgpt")],
        [InlineKeyboardButton(text="⭐ Gemini", callback_data="ai_gemini")],
        [InlineKeyboardButton(text="🔍 Perplexity", callback_data="ai_perplexity")],
        [InlineKeyboardButton(text="⚙️ Copilot", callback_data="ai_copilot")],
        [InlineKeyboardButton(text="💻 Програмування", callback_data="cat_programming")],
        [InlineKeyboardButton(text="📚 Навчання", callback_data="cat_learning")],
    ])

def get_programming_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Codeium", callback_data="ai_codeium")],
        [InlineKeyboardButton(text="🔧 Codex", callback_data="ai_codex")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
    ])

def get_learning_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Eduaide", callback_data="ai_eduaide")],
        [InlineKeyboardButton(text="🎓 Khanmigo", callback_data="ai_khanmigo")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
    ])

def get_response_keyboard(msg_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Інший AI", callback_data=f"redirect_{msg_id}")],
        [InlineKeyboardButton(text="📋 Копіювати", callback_data=f"copy_{msg_id}")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="back_main")]
    ])

# ========== API КЛІЄНТИ ==========
client_openai = None
gemini_model = None
perplexity_client = None

def init_clients():
    global client_openai, gemini_model, perplexity_client
    
    try:
        import openai
        if os.getenv('OPENAI_API_KEY'):
            client_openai = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    except ImportError:
        logging.warning("OpenAI не встановлено")
    
    try:
        import google.generativeai as genai
        if os.getenv('GEMINI_API_KEY'):
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except ImportError:
        logging.warning("Google Generative AI не встановлено")
    
    try:
        from perplexity import Perplexity  # Офіційний SDK
        if os.getenv('PERPLEXITY_API_KEY'):
            perplexity_client = Perplexity(api_key=os.getenv('PERPLEXITY_API_KEY'))
    except ImportError:
        logging.warning("Perplexity SDK не встановлено — використовуємо requests fallback")

# ========== QUERY TO AI ==========
async def query_ai(ai_type: str, query: str):
    try:
        if ai_type == "grok":
            from openai import OpenAI
            client = OpenAI(base_url="https://api.x.ai/v1", api_key=os.getenv('XAI_API_KEY'))
            resp = client.chat.completions.create(
                model="grok-beta",
                messages=[{"role": "user", "content": query}]
            )
            return resp.choices[0].message.content
        
        elif ai_type == "chatgpt" and client_openai:
            resp = client_openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": query}]
            )
            return resp.choices[0].message.content
        
        elif ai_type == "gemini" and gemini_model:
            resp = gemini_model.generate_content(query)
            return resp.text
        
        elif ai_type == "perplexity":
            if perplexity_client:
                # Офіційний SDK
                response = perplexity_client.chat.completions.create(
                    model="llama-3.1-sonar-small-128k-online",
                    messages=[{"role": "user", "content": query}]
                )
                return response.choices[0].message.content
            else:
                # Fallback через requests (якщо SDK не встановлено)
                import requests
                headers = {
                    "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [{"role": "user", "content": query}]
                }
                resp = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=data)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                else:
                    return "❌ Perplexity недоступний — перевір ключ"
        
        elif ai_type == "copilot":
            return f"🤖 Copilot: Аналіз запиту '{query[:50]}...' (симуляція)"
        
        elif ai_type == "codeium":
            # Симуляція (API Codeium потребує auth)
            return "```python\n# Generated by Codeium\nprint('Hello World!')\ndef hello():\n    return 'Привіт!'\n```"
        
        elif ai_type == "eduaide":
            return f"📚 **Eduaide урок:** {query}\n\n1. Вступ\n2. Практика\n3. Тест"
        
        elif ai_type == "codex":
            # Використовуємо OpenAI для код-генерації
            if client_openai:
                resp = client_openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Напиши код для: {query}"}]
                )
                return f"```python\n{resp.choices[0].message.content}\n```"
            return "```python\n# Codex симуляція\npass\n```"
        
        elif ai_type == "khanmigo":
            return f"🎓 **Khanmigo:** Пояснення {query} з прикладами"
        
        return f"❌ {ai_type} недоступний — перевір API ключ у .env"
        
    except Exception as e:
        logging.error(f"Помилка {ai_type}: {e}")
        return f"❌ Помилка {ai_type}: {str(e)}"

# ========== HANDLERS ==========
@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer("🤖 **Multi AI Bot**\nОбери AI для запиту:", 
                        reply_markup=get_main_keyboard(), parse_mode="Markdown")
    await state.set_state(AIChoice.waiting_query)

@dp.message(F.text, AIChoice.waiting_query)
async def handle_query(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_ai = data.get("current_ai")
    
    if not current_ai:
        await message.answer("⚠️ Спочатку обери AI з меню!")
        return
    
    await message.answer("⏳ Обробляю запит...")
    
    response = await query_ai(current_ai, message.text)
    msg = await message.answer(
        f"**{current_ai.upper()}**\n\n{response}",
        reply_markup=get_response_keyboard(message.message_id),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("ai_"))
async def ai_selected(callback: CallbackQuery, state: FSMContext):
    ai_type = callback.data.split("_")[1]
    await state.update_data(current_ai=ai_type)
    await callback.message.edit_text(
        f"✅ Вибрано **{ai_type}**\n\nНапиши запит:",
        reply_markup=None,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("cat_"))
async def category_selected(callback: CallbackQuery):
    cat = callback.data.split("_")[1]
    if cat == "programming":
        await callback.message.edit_text("💻 **Програмування**", reply_markup=get_programming_keyboard())
    elif cat == "learning":
        await callback.message.edit_text("📚 **Навчання**", reply_markup=get_learning_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.edit_text("🏠 **Головне меню**", reply_markup=get_main_keyboard())
    await callback.answer()

@dp.callback_query(F.data.startswith("copy_"))
async def copy_response(callback: CallbackQuery):
    # Видаляємо старі кнопки для чистоти
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply(f"📋 **Для копіювання:**\n```{callback.message.text}```", parse_mode="Markdown")
    await callback.answer("Скопійовано! (Ctrl+C)")

@dp.callback_query(F.data.startswith("redirect_"))
async def redirect_ai(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🔄 Обери інший AI для перенаправлення:", reply_markup=get_main_keyboard())
    await state.set_data({"context": callback.message.text})  # Зберігаємо контекст
    await callback.answer()

# ========== MAIN ==========
async def main():
    init_clients()
    print("🚀 Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())