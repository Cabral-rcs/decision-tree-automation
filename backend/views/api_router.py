# api_router.py - Define as rotas da API (View)
from fastapi import APIRouter
from backend.controllers import responses_controller, telegram_webhook

api_router = APIRouter()

# Rota para receber respostas do Telegram
api_router.post('/respostas')(responses_controller.receive_response)

# Rota para listar respostas para o frontend
api_router.get('/respostas')(responses_controller.list_responses)

# Rota para receber webhooks do Telegram (exemplo)
api_router.post('/webhook/telegram')(telegram_webhook.telegram_webhook) 