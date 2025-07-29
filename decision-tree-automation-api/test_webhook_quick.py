#!/usr/bin/env python3
"""
Teste rápido do webhook após correção do erro de datetime
"""

import requests
import json

def test_webhook_quick():
    """Teste rápido do webhook"""
    print("🚀 TESTE RÁPIDO DO WEBHOOK")
    print("=" * 40)
    
    base_url = "https://decision-tree-automation-1.onrender.com"
    
    # 1. Testar se o servidor está respondendo
    print("1️⃣ Testando resposta do servidor...")
    try:
        response = requests.get(f'{base_url}/health', timeout=10)
        if response.status_code == 200:
            print("✅ Servidor respondendo")
        else:
            print(f"❌ Servidor com problema: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return
    
    # 2. Testar debug do webhook
    print("\n2️⃣ Testando debug do webhook...")
    try:
        response = requests.get(f'{base_url}/webhook-debug', timeout=10)
        if response.status_code == 200:
            data = response.json()
            webhook_status = data.get('webhook_status', {})
            print(f"✅ Debug funcionando")
            print(f"   - Webhook configurado: {webhook_status.get('is_configured', False)}")
            print(f"   - URL atual: {webhook_status.get('current_url', 'N/A')}")
            print(f"   - Updates pendentes: {webhook_status.get('pending_updates', 0)}")
        else:
            print(f"❌ Erro no debug: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar debug: {e}")
    
    # 3. Testar listagem de alertas
    print("\n3️⃣ Testando listagem de alertas...")
    try:
        response = requests.get(f'{base_url}/alertas', timeout=10)
        if response.status_code == 200:
            data = response.json()
            pendentes = len(data.get('pendentes', []))
            escaladas = len(data.get('escaladas', []))
            print(f"✅ Listagem funcionando")
            print(f"   - Pendentes: {pendentes}")
            print(f"   - Escaladas: {escaladas}")
            
            if pendentes > 0:
                print(f"   - Há alertas pendentes para testar o webhook")
            else:
                print(f"   - Nenhum alerta pendente - crie um para testar")
        else:
            print(f"❌ Erro na listagem: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar listagem: {e}")
    
    # 4. Testar criação de alerta automático
    print("\n4️⃣ Testando criação de alerta automático...")
    try:
        response = requests.post(f'{base_url}/auto-alert/create-now', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Alerta criado: ID {data.get('alert_id')}")
            print(f"   - Agora você pode testar o webhook enviando uma mensagem")
        else:
            print(f"❌ Erro ao criar alerta: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar criação: {e}")
    
    print("\n" + "=" * 40)
    print("🏁 TESTE CONCLUÍDO")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Envie uma mensagem para o bot no Telegram (ex: '15:30')")
    print("2. Verifique se o alerta foi atualizado")
    print("3. Confirme que aparece na categoria 'Escaladas'")

if __name__ == "__main__":
    test_webhook_quick() 