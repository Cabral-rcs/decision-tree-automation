# api_router.py - Define as rotas da API (View)
from fastapi import APIRouter, Request
from backend.controllers import telegram_webhook
from backend.models.responses_model import add_response, get_responses

api_router = APIRouter()

# Rota para receber respostas do Telegram
@api_router.post('/respostas')
async def receive_response(request: Request):
    data = await request.json()
    add_response(data)
    return {"ok": True}

# Rota para listar respostas para o frontend
@api_router.get('/respostas')
def list_responses():
    responses = get_responses()
    return [
        {
            "id": response.id,
            "user_id": response.user_id,
            "pergunta": response.pergunta,
            "resposta": response.resposta,
            "timestamp": response.timestamp.isoformat() if response.timestamp else None
        }
        for response in responses
    ]

# Rota para receber webhooks do Telegram
@api_router.post('/telegram-webhook')
async def telegram_webhook_route(request: Request):
    return await telegram_webhook.telegram_webhook(request) 