from aiogram import types
from aiogram import F
from keyboards import get_main_keyboard, get_response_keyboard
from clients import client_openai, gemini_model
import asyncio

async def query_ai(ai_type: str, query: str) -> str:
    try:
        if ai_type == "chatgpt" and client_openai:
            resp = await asyncio.to_thread(
                client_openai.chat.completions.create,
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": query}],
                max_tokens=1000
            )
            return resp.choices[0].message.content.strip()

        elif ai_type == "gemini" and gemini_model:
            resp = await asyncio.to_thread(gemini_model.generate_content, query)
            return resp.text.strip()

        else:
            return "AI недоступний (ключ відсутній або помилка)."
    except Exception as e:
        return f"Помилка: {str(e)}"

async def start(message: types.Message, state: FSMContext):
    await message.answer("Обери AI:", reply_markup=get_main_keyboard())
    await state.clear()

async def handle(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_ai = data.get("current_ai")
    if not current_ai:
        await message.answer("Спочатку обери AI!", reply_markup=get_main_keyboard())
        return

    thinking_msg = await message.answer("Думаю...")
    response = await query_ai(current_ai, message.text)

    ai_name = "ChatGPT" if current_ai == "chatgpt" else "Gemini"
    await thinking_msg.edit_text(
        f"**{ai_name}**\n\n{response}",
        reply_markup=get_response_keyboard(),
        parse_mode="Markdown"
    )

async def select_ai(cb: types.CallbackQuery, state: FSMContext):
    ai = cb.data.split("_")[1]
    await state.update_data(current_ai=ai)
    ai_name = "ChatGPT" if ai == "chatgpt" else "Gemini"
    await cb.message.edit_text(f"**{ai_name}** вибрано!\nНапиши запит:", parse_mode="Markdown")
    await cb.answer()

async def back(cb: types.CallbackQuery):
    await cb.message.edit_text("Обери AI:", reply_markup=get_main_keyboard())
    await cb.answer()

async def redirect(cb: types.CallbackQuery):
    await cb.message.edit_text("Обери інший AI:", reply_markup=get_main_keyboard())
    await cb.answer()

async def copy(cb: types.CallbackQuery):
    text = cb.message.text or ""
    await cb.message.answer(f"```markdown:disable-run
    await cb.answer("Скопійовано!")
