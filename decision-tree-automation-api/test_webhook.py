#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do webhook do Telegram
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_webhook():
    """Testa o funcionamento do webhook"""
    print("🧪 TESTE DO WEBHOOK DO TELEGRAM")
    print("=" * 50)
    
    # Configurações
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    RENDER_URL = os.getenv('RENDER_EXTERNAL_URL', 'https://decision-tree-automation-1.onrender.com')
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN não encontrado")
        return
    
    TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'
    WEBHOOK_URL = f"{RENDER_URL}/telegram-webhook"
    
    print(f"🔗 URL do Render: {RENDER_URL}")
    print(f"🔗 URL do Webhook: {WEBHOOK_URL}")
    print(f"🤖 API do Telegram: {TELEGRAM_API_URL}")
    print()
    
    # 1. Verificar informações do bot
    print("1️⃣ Verificando informações do bot...")
    try:
        response = requests.get(f'{TELEGRAM_API_URL}/getMe', timeout=30)
        if response.ok:
            bot_info = response.json()
            print(f"✅ Bot encontrado: {bot_info['result']['first_name']} (@{bot_info['result']['username']})")
        else:
            print(f"❌ Erro ao verificar bot: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Erro ao verificar bot: {e}")
        return
    
    # 2. Verificar status atual do webhook
    print("\n2️⃣ Verificando status atual do webhook...")
    try:
        response = requests.get(f'{TELEGRAM_API_URL}/getWebhookInfo', timeout=30)
        if response.ok:
            webhook_info = response.json()
            current_url = webhook_info.get('result', {}).get('url')
            print(f"📋 URL atual: {current_url}")
            print(f"📋 Pendentes: {webhook_info.get('result', {}).get('pending_update_count', 0)}")
            print(f"📋 Último erro: {webhook_info.get('result', {}).get('last_error_message', 'Nenhum')}")
        else:
            print(f"❌ Erro ao verificar webhook: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro ao verificar webhook: {e}")
    
    # 3. Configurar webhook
    print("\n3️⃣ Configurando webhook...")
    try:
        payload = {
            'url': WEBHOOK_URL,
            'allowed_updates': ['message'],
            'drop_pending_updates': True
        }
        
        response = requests.post(f'{TELEGRAM_API_URL}/setWebhook', json=payload, timeout=30)
        if response.ok:
            result = response.json()
            print(f"✅ Webhook configurado: {result}")
        else:
            print(f"❌ Erro ao configurar webhook: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro ao configurar webhook: {e}")
    
    # 4. Verificar se o endpoint está acessível
    print("\n4️⃣ Testando endpoint do webhook...")
    try:
        response = requests.get(f'{RENDER_URL}/health', timeout=30)
        if response.ok:
            print(f"✅ Servidor acessível: {response.status_code}")
        else:
            print(f"⚠️ Servidor retornou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar servidor: {e}")
    
    # 5. Testar processamento interno do webhook
    print("\n5️⃣ Testando processamento interno do webhook...")
    try:
        test_data = {
            "message": {
                "message_id": 999,
                "from": {
                    "id": 6435800936,
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
                "date": 1640995200,  # Timestamp fixo
                "text": "15:30"
            }
        }
        
        response = requests.post(f'{RENDER_URL}/telegram-test-webhook', json=test_data, timeout=30)
        if response.ok:
            result = response.json()
            print(f"✅ Teste interno: {result.get('message', 'Sucesso')}")
        else:
            print(f"❌ Erro no teste interno: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro no teste interno: {e}")
    
    # 6. Verificar debug do webhook
    print("\n6️⃣ Verificando debug do webhook...")
    try:
        response = requests.get(f'{RENDER_URL}/webhook-debug', timeout=30)
        if response.ok:
            debug_info = response.json()
            print(f"✅ Debug disponível: {debug_info.get('webhook_status', {}).get('is_configured', False)}")
        else:
            print(f"❌ Erro no debug: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Envie uma mensagem para o bot no Telegram")
    print("2. Verifique os logs do servidor")
    print("3. Acesse /webhook-debug para mais informações")
    print("4. Use /telegram-test-webhook para testar internamente")

if __name__ == "__main__":
    test_webhook() 