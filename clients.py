import os
import logging
import httpx
from openai import OpenAI
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

client_openai = None
gemini_model = None

def init_clients():
    global client_openai, gemini_model

    # ChatGPT
    key = os.getenv('OPENAI_API_KEY')
    if key:
        try:
            client_openai = OpenAI(
                api_key=key,
                http_client=httpx.Client(proxies=None)  # Без проксі
            )
            logging.info("ChatGPT: OK")
        except Exception as e:
            logging.error(f"ChatGPT помилка: {e}")
    else:
        logging.warning("OPENAI_API_KEY відсутній")

    # Gemini
    key = os.getenv('GEMINI_API_KEY')
    if key:
        try:
            genai.configure(api_key=key)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logging.info("Gemini: OK")
        except Exception as e:
            logging.error(f"Gemini помилка: {e}")
    else:
        logging.warning("GEMINI_API_KEY відсутній")
