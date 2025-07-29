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
        # URL do webhook - usa a URL atual do Render
        import os
        render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://decision-tree-automation-1.onrender.com')
        webhook_url = f"{render_url}/telegram-webhook"
        
        logger.info(f"🔧 Configurando webhook para URL: {webhook_url}")
        print(f"🔧 Configurando webhook para URL: {webhook_url}")
        
        payload = {
            'url': webhook_url,
            'allowed_updates': ['message'],
            'drop_pending_updates': True  # Remove mensagens antigas
        }
        
        logger.info(f"📤 Payload do webhook: {payload}")
        print(f"📤 Payload do webhook: {payload}")
        
        response = requests.post(f'{TELEGRAM_API_URL}/setWebhook', json=payload, timeout=30)
        
        logger.info(f"📥 Resposta do Telegram: {response.status_code} - {response.text}")
        print(f"📥 Resposta do Telegram: {response.status_code} - {response.text}")
        
        if response.ok:
            result = response.json()
            logger.info(f"✅ Webhook configurado com sucesso: {result}")
            print(f"✅ Webhook configurado com sucesso: {result}")
            return {
                "success": True,
                "message": "Webhook configurado com sucesso",
                "webhook_url": webhook_url,
                "result": result
            }
        else:
            logger.error(f"❌ Erro ao configurar webhook: {response.status_code} - {response.text}")
            print(f"❌ Erro ao configurar webhook: {response.status_code} - {response.text}")
            return {
                "success": False,
                "message": f"Erro ao configurar webhook: {response.status_code}",
                "error": response.text,
                "webhook_url": webhook_url
            }
    except Exception as e:
        logger.error(f"❌ Erro ao configurar webhook: {str(e)}")
        print(f"❌ Erro ao configurar webhook: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao configurar webhook: {str(e)}"
        }

# Rota para verificar status do webhook
@api_router.get('/telegram-webhook-info')
async def get_webhook_info():
    """Verifica o status do webhook do Telegram"""
    try:
        logger.info("🔍 Verificando informações do webhook")
        print("🔍 Verificando informações do webhook")
        
        response = requests.get(f'{TELEGRAM_API_URL}/getWebhookInfo', timeout=30)
        
        logger.info(f"📥 Resposta do Telegram: {response.status_code} - {response.text}")
        print(f"📥 Resposta do Telegram: {response.status_code} - {response.text}")
        
        if response.ok:
            result = response.json()
            logger.info(f"✅ Informações do webhook: {result}")
            print(f"✅ Informações do webhook: {result}")
            
            # Adiciona informações extras
            webhook_status = {
                "success": True,
                "webhook_info": result,
                "is_configured": result.get("ok", False),
                "url": result.get("result", {}).get("url"),
                "has_custom_certificate": result.get("result", {}).get("has_custom_certificate", False),
                "pending_update_count": result.get("result", {}).get("pending_update_count", 0),
                "last_error_date": result.get("result", {}).get("last_error_date"),
                "last_error_message": result.get("result", {}).get("last_error_message"),
                "max_connections": result.get("result", {}).get("max_connections", 40),
                "allowed_updates": result.get("result", {}).get("allowed_updates", [])
            }
            
            return webhook_status
        else:
            logger.error(f"❌ Erro ao obter informações do webhook: {response.status_code} - {response.text}")
            print(f"❌ Erro ao obter informações do webhook: {response.status_code} - {response.text}")
            return {
                "success": False,
                "message": f"Erro ao obter informações do webhook: {response.status_code}",
                "error": response.text
            }
    except Exception as e:
        logger.error(f"❌ Erro ao obter informações do webhook: {str(e)}")
        print(f"❌ Erro ao obter informações do webhook: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao obter informações do webhook: {str(e)}"
        }

# Rota para testar webhook (simulação)
@api_router.post('/telegram-test-webhook')
async def test_telegram_webhook():
    """Testa o processamento do webhook com dados simulados"""
    try:
        logger.info("🧪 INICIANDO TESTE DO WEBHOOK")
        print("🧪 INICIANDO TESTE DO WEBHOOK")
        
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
        
        logger.info(f"📋 Dados de teste: {test_data}")
        print(f"📋 Dados de teste: {test_data}")
        
        # Simula o processamento do webhook
        from backend.controllers.telegram_webhook import telegram_webhook
        from fastapi import Request
        import json
        
        # Cria um request simulado
        class MockRequest:
            def __init__(self, data):
                self.data = data
                self.headers = {"content-type": "application/json"}
            
            async def json(self):
                return self.data
            
            async def body(self):
                return json.dumps(self.data).encode('utf-8')
        
        mock_request = MockRequest(test_data)
        result = await telegram_webhook(mock_request)
        
        logger.info(f"✅ Teste do webhook concluído: {result}")
        print(f"✅ Teste do webhook concluído: {result}")
        
        return {
            "success": True,
            "message": "Teste do webhook executado",
            "test_data": test_data,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no teste do webhook: {str(e)}")
        print(f"❌ Erro no teste do webhook: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        return {
            "success": False,
            "message": f"Erro no teste do webhook: {str(e)}",
            "error": str(e),
            "traceback": traceback.format_exc()
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

# Rota para forçar configuração do webhook
@api_router.post('/telegram-force-setup')
async def force_webhook_setup():
    """Força a configuração do webhook do Telegram"""
    try:
        logger.info("🔧 FORÇANDO CONFIGURAÇÃO DO WEBHOOK")
        print("🔧 FORÇANDO CONFIGURAÇÃO DO WEBHOOK")
        
        import os
        render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://decision-tree-automation-1.onrender.com')
        webhook_url = f"{render_url}/telegram-webhook"
        
        logger.info(f"🔗 URL do webhook: {webhook_url}")
        print(f"🔗 URL do webhook: {webhook_url}")
        
        # Primeiro, remove o webhook atual
        logger.info("🗑️ Removendo webhook atual...")
        print("🗑️ Removendo webhook atual...")
        
        delete_response = requests.post(f'{TELEGRAM_API_URL}/deleteWebhook', timeout=30)
        if delete_response.ok:
            logger.info("✅ Webhook atual removido")
            print("✅ Webhook atual removido")
        else:
            logger.warning(f"⚠️ Erro ao remover webhook: {delete_response.status_code}")
            print(f"⚠️ Erro ao remover webhook: {delete_response.status_code}")
        
        # Aguarda um pouco
        import time
        time.sleep(2)
        
        # Configura o novo webhook
        payload = {
            'url': webhook_url,
            'allowed_updates': ['message'],
            'drop_pending_updates': True
        }
        
        logger.info(f"📤 Configurando novo webhook: {payload}")
        print(f"📤 Configurando novo webhook: {payload}")
        
        response = requests.post(f'{TELEGRAM_API_URL}/setWebhook', json=payload, timeout=30)
        
        logger.info(f"📥 Resposta do Telegram: {response.status_code} - {response.text}")
        print(f"📥 Resposta do Telegram: {response.status_code} - {response.text}")
        
        if response.ok:
            result = response.json()
            logger.info(f"✅ Webhook configurado com sucesso: {result}")
            print(f"✅ Webhook configurado com sucesso: {result}")
            
            # Verifica se foi configurado corretamente
            verify_response = requests.get(f'{TELEGRAM_API_URL}/getWebhookInfo', timeout=30)
            if verify_response.ok:
                verify_result = verify_response.json()
                current_url = verify_result.get('result', {}).get('url')
                is_correct = current_url == webhook_url
                
                return {
                    "success": True,
                    "message": "Webhook configurado com sucesso",
                    "webhook_url": webhook_url,
                    "current_url": current_url,
                    "is_correctly_configured": is_correct,
                    "result": result,
                    "verification": verify_result
                }
            else:
                return {
                    "success": True,
                    "message": "Webhook configurado, mas não foi possível verificar",
                    "webhook_url": webhook_url,
                    "result": result,
                    "verification_error": verify_response.text
                }
        else:
            logger.error(f"❌ Erro ao configurar webhook: {response.status_code} - {response.text}")
            print(f"❌ Erro ao configurar webhook: {response.status_code} - {response.text}")
            return {
                "success": False,
                "message": f"Erro ao configurar webhook: {response.status_code}",
                "error": response.text,
                "webhook_url": webhook_url
            }
    except Exception as e:
        logger.error(f"❌ Erro ao forçar configuração do webhook: {str(e)}")
        print(f"❌ Erro ao forçar configuração do webhook: {str(e)}")
        import traceback
        return {
            "success": False,
            "message": f"Erro ao forçar configuração do webhook: {str(e)}",
            "traceback": traceback.format_exc()
        } 