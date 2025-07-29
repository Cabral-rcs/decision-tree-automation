#!/usr/bin/env python3
"""
Script para testar se a rota do webhook está funcionando
"""

import requests
import json
from datetime import datetime

def test_rota_webhook():
    """Testa se a rota do webhook está funcionando"""
    print("🧪 TESTE DA ROTA DO WEBHOOK")
    print("=" * 40)
    
    # Dados de teste
    webhook_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 123,
            "from": {
                "id": 6435800936,
                "is_bot": False,
                "first_name": "Rafael",
                "last_name": "Cabral",
                "username": "rafael_cabral",
                "language_code": "pt"
            },
            "chat": {
                "id": 6435800936,
                "first_name": "Rafael",
                "last_name": "Cabral",
                "username": "rafael_cabral",
                "type": "private"
            },
            "date": int(datetime.now().timestamp()),
            "text": "20:30"
        }
    }
    
    print("📤 Enviando webhook para /telegram-webhook...")
    
    try:
        response = requests.post(
            "http://localhost:8000/telegram-webhook",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook processado com sucesso!")
            print(f"   Status: {result.get('status')}")
            print(f"   Mensagem: {result.get('msg')}")
            return True
        else:
            print("❌ Erro no webhook")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_health():
    """Testa se o servidor está respondendo"""
    print("\n🔍 Verificando se o servidor está rodando...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando")
            return True
        else:
            print("❌ Servidor não está respondendo corretamente")
            return False
    except requests.exceptions.RequestException:
        print("❌ Servidor não está rodando")
        print("💡 Execute: uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DA ROTA DO WEBHOOK")
    print("=" * 50)
    
    if not test_health():
        return
    
    success = test_rota_webhook()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ A rota do webhook está funcionando")
    else:
        print("❌ TESTE FALHOU")
        print("❌ Há problemas com a rota do webhook")

if __name__ == "__main__":
    main() 