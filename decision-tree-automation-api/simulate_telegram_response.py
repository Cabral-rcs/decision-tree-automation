#!/usr/bin/env python3
"""
Script para simular uma resposta do Telegram
"""

import requests
import json
from datetime import datetime
import pytz

def simulate_telegram_response():
    """Simula uma resposta do Telegram"""
    
    print("📱 SIMULANDO RESPOSTA DO TELEGRAM")
    print("=" * 50)
    
    # Dados simulados de uma resposta do Telegram
    webhook_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 123,
            "from": {
                "id": 6435800936,
                "is_bot": False,
                "first_name": "Rafael",
                "last_name": "Cabral",
                "username": "rafaelcabral"
            },
            "chat": {
                "id": 6435800936,
                "first_name": "Rafael",
                "last_name": "Cabral",
                "username": "rafaelcabral",
                "type": "private"
            },
            "date": int(datetime.now().timestamp()),
            "text": "15:30"  # Resposta simulada
        }
    }
    
    print(f"📤 Enviando webhook simulado...")
    print(f"   User ID: {webhook_data['message']['from']['id']}")
    print(f"   Nome: {webhook_data['message']['from']['first_name']} {webhook_data['message']['from']['last_name']}")
    print(f"   Resposta: {webhook_data['message']['text']}")
    
    try:
        # Envia o webhook para o endpoint local
        response = requests.post(
            "http://localhost:8000/webhook/telegram",
            json=webhook_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Resposta do webhook: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook processado: {result}")
        else:
            print(f"❌ Erro no webhook: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend não está rodando. Inicie com: uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")

def check_alert_status():
    """Verifica o status do alerta após a simulação"""
    
    print("\n🔍 VERIFICANDO STATUS DO ALERTA")
    print("=" * 50)
    
    try:
        # Verifica o endpoint de debug
        response = requests.get("http://localhost:8000/alertas/debug")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Total de alertas: {data.get('total_alertas', 0)}")
            print(f"📊 Pendentes: {data.get('pendentes', 0)}")
            print(f"📊 Com prazo: {data.get('com_prazo', 0)}")
            
            print("📋 Últimos alertas:")
            for alerta in data.get('ultimos_alertas', []):
                print(f"   ID: {alerta['id']}, Problema: {alerta['problema']}, Prazo: {alerta['prazo']}, Respondido: {alerta['respondido_em']}")
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend não está rodando")
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

def main():
    """Função principal"""
    print("🚀 SIMULAÇÃO DE RESPOSTA DO TELEGRAM")
    print("=" * 50)
    
    # Simula a resposta
    simulate_telegram_response()
    
    # Verifica o status
    check_alert_status()
    
    print("\n" + "=" * 50)
    print("🏁 SIMULAÇÃO CONCLUÍDA")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Inicie o backend: uvicorn backend.main:app --reload")
    print("2. Execute este script novamente")
    print("3. Verifique se o alerta foi atualizado")

if __name__ == "__main__":
    main() 