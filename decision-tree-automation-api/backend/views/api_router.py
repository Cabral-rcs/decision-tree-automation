# api_router.py - Define as rotas da API (View)
from fastapi import APIRouter, Request
from backend.controllers import telegram_webhook
from backend.models.responses_model import add_response, get_responses
import logging
import requests
from backend.config import TELEGRAM_API_URL
from datetime import datetime

api_router = APIRouter()
logger = logging.getLogger(__name__)

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
    logger.info("🔔 WEBHOOK ENDPOINT CHAMADO")
    print("🔔 WEBHOOK ENDPOINT CHAMADO")
    return await telegram_webhook.telegram_webhook(request)

# Rota para configurar webhook do Telegram
@api_router.post('/telegram-set-webhook')
async def set_telegram_webhook():
    """Configura o webhook do Telegram para receber mensagens"""
    try:
        # URL do webhook (ajuste conforme necessário)
        webhook_url = "https://decision-tree-automation-1.onrender.com/telegram-webhook"
        
        payload = {
            'url': webhook_url,
            'allowed_updates': ['message']
        }
        
        response = requests.post(f'{TELEGRAM_API_URL}/setWebhook', json=payload)
        
        if response.ok:
            result = response.json()
            logger.info(f"Webhook configurado com sucesso: {result}")
            return {
                "success": True,
                "message": "Webhook configurado com sucesso",
                "webhook_url": webhook_url,
                "result": result
            }
        else:
            logger.error(f"Erro ao configurar webhook: {response.status_code} - {response.text}")
            return {
                "success": False,
                "message": f"Erro ao configurar webhook: {response.status_code}",
                "error": response.text
            }
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao configurar webhook: {str(e)}"
        }

# Rota para verificar status do webhook
@api_router.get('/telegram-webhook-info')
async def get_webhook_info():
    """Verifica o status do webhook do Telegram"""
    try:
        response = requests.get(f'{TELEGRAM_API_URL}/getWebhookInfo')
        
        if response.ok:
            result = response.json()
            logger.info(f"Informações do webhook: {result}")
            return {
                "success": True,
                "webhook_info": result
            }
        else:
            logger.error(f"Erro ao obter informações do webhook: {response.status_code}")
            return {
                "success": False,
                "message": f"Erro ao obter informações do webhook: {response.status_code}"
            }
    except Exception as e:
        logger.error(f"Erro ao obter informações do webhook: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao obter informações do webhook: {str(e)}"
        } 

# Rota para testar webhook (simulação)
@api_router.post('/telegram-test-webhook')
async def test_telegram_webhook():
    """Testa o processamento do webhook com dados simulados"""
    try:
        # Dados simulados de uma mensagem do Telegram
        test_data = {
            "message": {
                "message_id": 123,
                "from": {
                    "id": 6435800936,  # ID do Rafael Cabral
                    "first_name": "Rafael",
                    "last_name": "Cabral",
                    "is_bot": False
                },
                "chat": {
                    "id": 6435800936,
                    "first_name": "Rafael",
                    "last_name": "Cabral",
                    "type": "private"
                },
                "date": int(datetime.now().timestamp()),
                "text": "15:30"  # Resposta simulada
            }
        }
        
        # Simula o processamento do webhook
        from backend.controllers.telegram_webhook import telegram_webhook
        from fastapi import Request
        import json
        
        # Cria um request simulado
        class MockRequest:
            async def json(self):
                return test_data
        
        mock_request = MockRequest()
        result = await telegram_webhook(mock_request)
        
        logger.info(f"Teste do webhook concluído: {result}")
        return {
            "success": True,
            "message": "Teste do webhook executado",
            "test_data": test_data,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Erro no teste do webhook: {str(e)}")
        return {
            "success": False,
            "message": f"Erro no teste do webhook: {str(e)}"
        } 

# Rota para enviar mensagem de teste para o Telegram
@api_router.post('/telegram-send-test')
async def send_test_message():
    """Envia uma mensagem de teste para o Telegram"""
    try:
        from backend.config import CHAT_IDS
        
        test_message = "🧪 TESTE: Esta é uma mensagem de teste do sistema.\n\nSe você recebeu esta mensagem, responda com um horário no formato HH:MM (ex: 15:30) para testar o webhook."
        
        results = []
        for chat_id in CHAT_IDS:
            payload = {
                'chat_id': chat_id,
                'text': test_message
            }
            
            response = requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload, timeout=10)
            
            if response.ok:
                result = response.json()
                results.append({
                    "chat_id": chat_id,
                    "success": True,
                    "message_id": result.get('result', {}).get('message_id'),
                    "result": result
                })
                logger.info(f"Mensagem de teste enviada para {chat_id}")
            else:
                results.append({
                    "chat_id": chat_id,
                    "success": False,
                    "error": f"{response.status_code} - {response.text}"
                })
                logger.error(f"Erro ao enviar mensagem de teste para {chat_id}: {response.status_code}")
        
        return {
            "success": True,
            "message": "Mensagem de teste enviada",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem de teste: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao enviar mensagem de teste: {str(e)}"
        } 