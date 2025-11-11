from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ChatGPT", callback_data="ai_chatgpt")],
        [InlineKeyboardButton(text="Gemini", callback_data="ai_gemini")],
    ])

def get_response_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Інший AI", callback_data="redirect_main")],
        [InlineKeyboardButton(text="Копіювати", callback_data="copy_response")],
        [InlineKeyboardButton(text="Меню", callback_data="back_main")],
    ])
