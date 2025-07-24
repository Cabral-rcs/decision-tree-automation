import os
from dotenv import load_dotenv
# config.py - Configurações do sistema

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_IDS = [int(cid) for cid in os.getenv('CHAT_IDS', '').split(',') if cid.strip()]

# URL base da API do Telegram
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'