import os
from dotenv import load_dotenv
# config.py - Configurações do sistema

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_IDS = [int(cid) for cid in os.getenv('CHAT_IDS', '').split(',') if cid.strip()]

# URL base da API do Telegram
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

# Configuração do banco de dados - SQLite em memória (dados zerados a cada deploy)
DATABASE_URL = "sqlite:///:memory:"

# Configuração alternativa para desenvolvimento local (arquivo temporário)
if os.getenv('ENVIRONMENT') == 'development':
    DATABASE_URL = "sqlite:///temp_database.db"